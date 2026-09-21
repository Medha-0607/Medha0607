"""Ed25519 digital signature generation and verification for RECTRA evidence."""

from __future__ import annotations

import logging
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from rectra.config import PRIVATE_KEY_PATH, PUBLIC_KEY_PATH
from rectra.core.exceptions import SignatureError
from rectra.evidence.hashing import sha256_bytes

logger = logging.getLogger(__name__)


def load_private_key(key_path: Path | None = None) -> ed25519.Ed25519PrivateKey:
    """Load Ed25519 private key from PEM file."""
    path = key_path or PRIVATE_KEY_PATH
    if not path.exists():
        raise SignatureError(f"Signing private key not found at {path}")

    try:
        with open(path, "rb") as f:
            key_data = f.read()
        return serialization.load_pem_private_key(key_data, password=None)  # type: ignore[return-value]
    except Exception as exc:
        raise SignatureError(f"Failed to load private key from {path}: {exc}") from exc


def load_public_key(key_path: Path | None = None) -> ed25519.Ed25519PublicKey:
    """Load Ed25519 public key from PEM file."""
    path = key_path or PUBLIC_KEY_PATH
    if not path.exists():
        raise SignatureError(f"Signing public key not found at {path}")

    try:
        with open(path, "rb") as f:
            key_data = f.read()
        return serialization.load_pem_public_key(key_data)  # type: ignore[return-value]
    except Exception as exc:
        raise SignatureError(f"Failed to load public key from {path}: {exc}") from exc


def get_public_key_fingerprint(public_key_path: Path | None = None) -> str:
    """Return the first 16 hex characters of the SHA-256 digest of the public key bytes."""
    path = public_key_path or PUBLIC_KEY_PATH
    with open(path, "rb") as f:
        key_bytes = f.read()
    return sha256_bytes(key_bytes)[:16]


def sign_digest(record_digest: str, private_key_path: Path | None = None) -> str:
    """Sign a canonical record digest with Ed25519 and return hexadecimal signature."""
    private_key = load_private_key(private_key_path)
    # Sign the UTF-8 bytes of the hexadecimal digest
    signature = private_key.sign(record_digest.encode("utf-8"))
    return signature.hex()


def verify_signature(
    record_digest: str,
    signature_hex: str,
    public_key_path: Path | None = None,
) -> bool:
    """Verify an Ed25519 digital signature against a record digest.

    Returns True if valid, False if invalid or corrupted.
    """
    try:
        public_key = load_public_key(public_key_path)
        sig_bytes = bytes.fromhex(signature_hex)
        public_key.verify(sig_bytes, record_digest.encode("utf-8"))
        return True
    except (InvalidSignature, ValueError, TypeError) as exc:
        logger.warning("Digital signature verification failed: %s", exc)
        return False
