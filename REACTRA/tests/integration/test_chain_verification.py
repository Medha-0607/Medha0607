"""Integration tests for SQLite audit chain verification and integrity checks."""

from __future__ import annotations

import json
import sqlite3

from rectra.database.repository import save_evidence_record
from rectra.evidence.canonical import build_canonical_record_dict
from rectra.evidence.chain import verify_chain
from rectra.evidence.hashing import compute_record_digest
from rectra.evidence.signing import get_public_key_fingerprint, sign_digest
from rectra.models import EvidenceRecordModel


def _add_chained_record(test_id: str, prev_hash: str | None, conn: sqlite3.Connection) -> str:
    rec = build_canonical_record_dict(
        test_id=test_id,
        operator_id="OP-CHAIN-INT",
        capture_mode="LIVE_CAMERA",
        timestamp_utc="2026-09-20T12:00:00Z",
        latitude=28.6139,
        longitude=77.2090,
        gps_status="MANUAL_DEMO",
        profile_id="DEMO-ASSAY-001",
        profile_version="1.0",
        reference_card_version="1.0",
        algorithm_version="1.0",
        model_version="1.0",
        result="POSITIVE",
        classification_score=0.95,
        measurement_quality="HIGH",
        quality_gate_status="VALID",
        image_sha256="b" * 64,
        previous_record_hash=prev_hash,
    )
    digest = compute_record_digest(rec)
    sig = sign_digest(digest)
    fp = get_public_key_fingerprint()

    ev = EvidenceRecordModel(
        test_id=test_id,
        record_json=json.dumps(rec),
        record_digest=digest,
        signature=sig,
        public_key_fingerprint=fp,
        image_sha256="b" * 64,
        previous_record_hash=prev_hash,
    )
    save_evidence_record(ev, conn=conn)
    return digest


def test_chain_verification_intact_sequence(memory_db) -> None:
    """A multi-entry chain with valid forward and backward hashes must verify intact."""
    prev = None
    for i in range(5):
        prev = _add_chained_record(f"test-chain-{i}", prev, memory_db)

    res = verify_chain(conn=memory_db)
    assert res.valid is True
    assert res.total_records == 5


def test_chain_verification_deleted_record(memory_db) -> None:
    """Deleting an intermediate record creates a hash gap that verify_chain must detect."""
    prev = None
    for i in range(4):
        prev = _add_chained_record(f"test-del-{i}", prev, memory_db)

    # Delete record #2
    memory_db.execute("DELETE FROM evidence_records WHERE test_id = 'test-del-2'")
    memory_db.commit()

    res = verify_chain(conn=memory_db)
    assert res.valid is False
    assert "Audit chain broken" in res.reason or "does not match" in res.reason


def test_chain_verification_modified_hash(memory_db) -> None:
    """Modifying a digest stored in the database breaks signature and canonical integrity."""
    d1 = _add_chained_record("t1", None, memory_db)
    _add_chained_record("t2", d1, memory_db)

    # Tamper with t1's record_digest in place
    memory_db.execute(
        "UPDATE evidence_records SET record_digest = ? WHERE test_id = 't1'",
        ("9" * 64,),
    )
    memory_db.commit()

    res = verify_chain(conn=memory_db)
    assert res.valid is False
    assert "Integrity check failed" in res.reason or "tampered" in res.reason
