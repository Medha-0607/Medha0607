"""Stand-alone evidence record and envelope verification."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from rectra.config import PUBLIC_KEY_PATH
from rectra.evidence.hashing import compute_record_digest
from rectra.evidence.signing import verify_signature

logger = logging.getLogger(__name__)


def verify_evidence_record(
    record_dict: dict[str, Any],
    public_key_path: Path | None = None,
) -> tuple[bool, str]:
    """Verify the cryptographic authenticity and integrity of an individual evidence record.

    Checks:
    1. Mandatory fields exist.
    2. Computed canonical SHA-256 digest matches the stored record_digest.
    3. Ed25519 digital signature verifies against the stored digest and public key.
    """
    pub_key = public_key_path or PUBLIC_KEY_PATH

    stored_digest = record_dict.get("record_digest")
    if not stored_digest:
        return False, "INTEGRITY VERIFICATION FAILED: Missing 'record_digest' in record."

    stored_signature = record_dict.get("signature")
    if not stored_signature:
        return False, "INTEGRITY VERIFICATION FAILED: Missing 'signature' in record."

    # 1. Recompute canonical digest
    recomputed_digest = compute_record_digest(record_dict)
    if recomputed_digest != stored_digest:
        logger.warning(
            "Evidence digest mismatch: recomputed %s != stored %s",
            recomputed_digest,
            stored_digest,
        )
        return (
            False,
            (
                "INTEGRITY VERIFICATION FAILED: Record content does not match canonical digest. "
                "One or more fields have been altered."
            ),
        )

    # 2. Verify digital signature
    sig_valid = verify_signature(stored_digest, stored_signature, pub_key)
    if not sig_valid:
        logger.warning("Digital signature mismatch for digest %s", stored_digest)
        return (
            False,
            "INTEGRITY VERIFICATION FAILED: Ed25519 signature is invalid for the record digest.",
        )

    return True, "RECORD VERIFIED: Canonical digest and Ed25519 digital signature are intact."
