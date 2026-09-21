"""Unit tests for the tamper-evident backward-linking hash chain."""

from __future__ import annotations

import json
import sqlite3

from rectra.database.repository import save_evidence_record
from rectra.evidence.canonical import build_canonical_record_dict
from rectra.evidence.chain import get_latest_record_hash, verify_chain
from rectra.evidence.hashing import compute_record_digest
from rectra.evidence.signing import get_public_key_fingerprint, sign_digest
from rectra.models import EvidenceRecordModel


def _add_chained_record(test_id: str, prev_hash: str | None, conn: sqlite3.Connection) -> str:
    """Helper to construct, sign, and persist a valid EvidenceRecordModel."""
    rec = build_canonical_record_dict(
        test_id=test_id,
        operator_id="OP-CHAIN-01",
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
        image_sha256="a" * 64,
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
        image_sha256="a" * 64,
        previous_record_hash=prev_hash,
    )
    save_evidence_record(ev, conn=conn)
    return digest


def test_chain_empty_is_valid(memory_db) -> None:
    """An empty audit chain is trivially valid with zero records."""
    res = verify_chain(conn=memory_db)
    assert res.valid is True
    assert res.total_records == 0


def test_chain_single_genesis_record(memory_db) -> None:
    """A single genesis record must have previous_record_hash=None and verify successfully."""
    digest = _add_chained_record("test-uuid-001", None, memory_db)

    res = verify_chain(conn=memory_db)
    assert res.valid is True
    assert res.total_records == 1
    assert get_latest_record_hash(conn=memory_db) == digest


def test_chain_multi_link_continuity(memory_db) -> None:
    """A 3-link chain must verify unbroken continuity."""
    d1 = _add_chained_record("uuid-1", None, memory_db)
    d2 = _add_chained_record("uuid-2", d1, memory_db)
    _add_chained_record("uuid-3", d2, memory_db)

    res = verify_chain(conn=memory_db)
    assert res.valid is True
    assert res.total_records == 3


def test_chain_broken_link_fails(memory_db) -> None:
    """If an intermediate record links to an incorrect hash, verify_chain must detect it."""
    _add_chained_record("uuid-1", None, memory_db)
    # Broken link: links to "f"*64 instead of d1
    _add_chained_record("uuid-2", "f" * 64, memory_db)

    res = verify_chain(conn=memory_db)
    assert res.valid is False
    assert "Audit chain broken" in res.reason or "does not match" in res.reason
