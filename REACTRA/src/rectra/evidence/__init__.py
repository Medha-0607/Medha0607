"""Cryptographic evidence preservation, canonicalization, signing, and chain verification."""

from rectra.evidence.canonical import build_canonical_record_dict, canonicalize_record
from rectra.evidence.chain import get_latest_record_hash, verify_chain
from rectra.evidence.envelope import create_evidence_envelope, verify_envelope
from rectra.evidence.hashing import compute_record_digest, sha256_bytes, sha256_file
from rectra.evidence.signing import (
    get_public_key_fingerprint,
    load_private_key,
    load_public_key,
    sign_digest,
    verify_signature,
)
from rectra.evidence.verifier import verify_evidence_record

__all__ = [
    "build_canonical_record_dict",
    "canonicalize_record",
    "compute_record_digest",
    "create_evidence_envelope",
    "get_latest_record_hash",
    "get_public_key_fingerprint",
    "load_private_key",
    "load_public_key",
    "sha256_bytes",
    "sha256_file",
    "sign_digest",
    "verify_chain",
    "verify_envelope",
    "verify_evidence_record",
    "verify_signature",
]
