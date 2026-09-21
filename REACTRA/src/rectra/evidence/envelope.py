"""Portable signed evidence envelope export and verification."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from rectra.core.constants import ENVELOPE_FORMAT
from rectra.evidence.verifier import verify_evidence_record


def create_evidence_envelope(record_dict: dict[str, Any]) -> dict[str, Any]:
    """Package a signed evidence record into a portable, verifiable evidence envelope.

    Notice: Never includes private signing keys.
    """
    exported_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return {
        "envelope_format": ENVELOPE_FORMAT,
        "exported_at": exported_at,
        "evidence_record": record_dict,
        "image_sha256": record_dict.get("image_sha256", ""),
        "signature": record_dict.get("signature", ""),
        "public_key_fingerprint": record_dict.get("public_key_fingerprint", ""),
        "profile_id": record_dict.get("profile_id", ""),
        "profile_version": record_dict.get("profile_version", ""),
        "integrity_note": (
            "Verify by recomputing canonical digest (json-sort-keys-compact-utf8-v1) "
            "and verifying Ed25519 signature."
        ),
    }


def verify_envelope(
    envelope: dict[str, Any],
    public_key_path: Path | None = None,
) -> tuple[bool, str]:
    """Verify an exported evidence envelope by inspecting its embedded evidence_record."""
    rec = envelope.get("evidence_record")
    if not isinstance(rec, dict):
        return False, "INTEGRITY VERIFICATION FAILED: Missing 'evidence_record' in envelope."

    return verify_evidence_record(rec, public_key_path=public_key_path)
