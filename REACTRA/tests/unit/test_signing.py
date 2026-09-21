"""Unit tests for Ed25519 digital signature generation and verification."""

from __future__ import annotations

import hashlib

from rectra.evidence.signing import (
    get_public_key_fingerprint,
    sign_digest,
    verify_signature,
)


def test_sign_and_verify_valid_digest() -> None:
    """A valid Ed25519 signature on a 64-character hex digest must verify successfully."""
    digest = hashlib.sha256(b"canonical_test_payload").hexdigest()

    sig_hex = sign_digest(digest)
    assert len(sig_hex) == 128  # 64 bytes in hex

    is_valid = verify_signature(digest, sig_hex)
    assert is_valid is True


def test_verify_tampered_digest_fails() -> None:
    """Verifying an altered digest against the original signature must fail."""
    digest = hashlib.sha256(b"original_payload").hexdigest()
    tampered_digest = hashlib.sha256(b"tampered_payload").hexdigest()

    sig_hex = sign_digest(digest)

    is_valid = verify_signature(tampered_digest, sig_hex)
    assert is_valid is False


def test_public_key_fingerprint_format() -> None:
    """Fingerprint must be exactly 16 lowercase hexadecimal characters."""
    fp = get_public_key_fingerprint()

    assert len(fp) == 16
    assert all(c in "0123456789abcdef" for c in fp)
