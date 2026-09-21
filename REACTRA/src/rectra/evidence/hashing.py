"""Cryptographic SHA-256 hashing utilities for images and evidence records."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from rectra.evidence.canonical import canonicalize_record


def sha256_bytes(data: bytes) -> str:
    """Compute the lowercase hexadecimal SHA-256 digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Compute SHA-256 digest of a file reading in chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_record_digest(record: dict[str, Any]) -> str:
    """Compute SHA-256 digest of a canonical record.

    Excludes variable cryptographic envelope fields ('record_digest', 'signature',
    'public_key_fingerprint') to produce the authoritative preimage digest.
    """
    excluded_fields = {"record_digest", "signature", "public_key_fingerprint"}
    clean_record = {k: v for k, v in record.items() if k not in excluded_fields}
    canonical_bytes = canonicalize_record(clean_record)
    return sha256_bytes(canonical_bytes)
