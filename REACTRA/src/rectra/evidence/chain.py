"""Tamper-evident local evidence chain management and integrity verification."""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path

from rectra.config import PUBLIC_KEY_PATH, RECTRA_DB_PATH
from rectra.core.types import ChainVerificationResult
from rectra.database.connection import get_connection
from rectra.evidence.hashing import compute_record_digest
from rectra.evidence.signing import verify_signature

logger = logging.getLogger(__name__)


def get_latest_record_hash(conn: sqlite3.Connection) -> str | None:
    """Retrieve the record_digest of the most recent evidence record in the chain."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT record_digest
        FROM evidence_records
        ORDER BY rowid DESC
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    return str(row["record_digest"]) if row else None


def verify_chain(
    db_path: Path | str | None = None,
    public_key_path: Path | None = None,
    conn: sqlite3.Connection | None = None,
) -> ChainVerificationResult:
    """Verify the integrity of the entire tamper-evident local evidence chain.

    Checks:
    1. Recomputed canonical digest matches stored record_digest.
    2. Digital signature is cryptographically valid.
    3. Chain continuity: previous_record_hash matches previous record digest.
    """
    target_db = db_path or RECTRA_DB_PATH
    pub_key = public_key_path or PUBLIC_KEY_PATH
    should_close = False
    if conn is None:
        conn = get_connection(target_db)
        should_close = True

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT e.test_id, e.record_json, e.record_digest, e.signature,
                   e.previous_record_hash, e.rowid
            FROM evidence_records e
            ORDER BY e.rowid ASC
            """
        )
        records = cursor.fetchall()

        total = len(records)
        if total == 0:
            return ChainVerificationResult(
                valid=True,
                total_records=0,
                reason="Chain is empty (no records recorded yet).",
            )

        prev_expected_hash: str | None = None

        for idx, row in enumerate(records):
            test_id = str(row["test_id"])
            raw_json = str(row["record_json"])
            stored_digest = str(row["record_digest"])
            signature = str(row["signature"])
            stored_prev_hash = row["previous_record_hash"]

            # 1. Parse and verify canonical digest
            try:
                record_dict = json.loads(raw_json)
            except Exception as exc:
                return ChainVerificationResult(
                    valid=False,
                    total_records=total,
                    broken_at_test_id=test_id,
                    reason=f"Record {test_id} has invalid JSON content: {exc}",
                )

            recomputed_digest = compute_record_digest(record_dict)
            if recomputed_digest != stored_digest:
                logger.error(
                    "Digest mismatch at test %s: computed %s != stored %s",
                    test_id,
                    recomputed_digest,
                    stored_digest,
                )
                return ChainVerificationResult(
                    valid=False,
                    total_records=total,
                    broken_at_test_id=test_id,
                    reason=(
                        f"Integrity check failed at record {test_id}: "
                        f"canonical content has been tampered with or modified."
                    ),
                )

            # 2. Verify digital signature
            sig_valid = verify_signature(stored_digest, signature, pub_key)
            if not sig_valid:
                logger.error("Signature invalid for test %s", test_id)
                return ChainVerificationResult(
                    valid=False,
                    total_records=total,
                    broken_at_test_id=test_id,
                    reason=(
                        f"Cryptographic signature check failed at record {test_id}: "
                        f"Ed25519 signature does not match public key."
                    ),
                )

            # 3. Verify backward chain link
            if idx == 0:
                if stored_prev_hash is not None:
                    return ChainVerificationResult(
                        valid=False,
                        total_records=total,
                        broken_at_test_id=test_id,
                        reason=(
                            f"Genesis record {test_id} has unexpected previous hash: "
                            f"{stored_prev_hash}"
                        ),
                    )
            else:
                if stored_prev_hash != prev_expected_hash:
                    logger.error(
                        "Chain broken at test %s: expected prev %s != stored %s",
                        test_id,
                        prev_expected_hash,
                        stored_prev_hash,
                    )
                    return ChainVerificationResult(
                        valid=False,
                        total_records=total,
                        broken_at_test_id=test_id,
                        reason=(
                            f"Audit chain broken at record {test_id}: previous_record_hash "
                            f"does not match previous link in chain."
                        ),
                    )

            prev_expected_hash = stored_digest

        logger.info("Audit chain verified successfully (%d records intact).", total)
        return ChainVerificationResult(
            valid=True,
            total_records=total,
            reason=f"Tamper-evident local evidence chain is intact ({total} records verified).",
        )

    finally:
        if should_close:
            conn.close()
