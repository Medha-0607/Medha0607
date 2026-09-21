"""Generate Ed25519 development keypair for RECTRA evidence signing.

Windows-compatible with icacls file permissions restriction.
Idempotent: skips generation if keys already exist.
"""

from __future__ import annotations

import logging
import os
import platform
import subprocess
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from rectra.config import PRIVATE_KEY_PATH, PUBLIC_KEY_PATH, RECTRA_KEY_DIR
from rectra.core.logging_config import configure_logging

logger = logging.getLogger(__name__)


def generate_keys(force: bool = False) -> tuple[Path, Path]:
    """Generate Ed25519 keypair and save to runtime/keys directory."""
    RECTRA_KEY_DIR.mkdir(parents=True, exist_ok=True)

    if not force and PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists():
        logger.info("Keys already exist at %s. Skipping generation.", RECTRA_KEY_DIR)
        return PRIVATE_KEY_PATH, PUBLIC_KEY_PATH

    logger.info("Generating new Ed25519 development keypair...")
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Write private key
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_pem)

    # Write public key
    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(public_pem)

    # Restrict permissions
    _restrict_permissions(PRIVATE_KEY_PATH)

    logger.info("Development keypair successfully saved to %s", RECTRA_KEY_DIR)
    return PRIVATE_KEY_PATH, PUBLIC_KEY_PATH


def _restrict_permissions(key_path: Path) -> None:
    """Restrict file permissions to current user only."""
    if platform.system() == "Windows":
        try:
            username = os.getenv("USERNAME", "")
            if username:
                # Remove inherited permissions and grant Read/Write to current user only
                cmd = f'icacls "{key_path}" /inheritance:r /grant:r "{username}:(R,W)"'
                subprocess.run(
                    cmd,
                    shell=True,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.info("Restricted permissions on %s via Windows icacls.", key_path.name)
            else:
                logger.warning("Could not determine Windows USERNAME to restrict permissions.")
        except Exception as exc:
            logger.warning(
                "Could not restrict Windows permissions on %s via icacls: %s. "
                "Ensure runtime/ is not accessible by unauthorized users.",
                key_path,
                exc,
            )
    else:
        try:
            os.chmod(key_path, 0o600)
            logger.info("Restricted POSIX permissions on %s to 0600.", key_path.name)
        except Exception as exc:
            logger.warning("Failed to chmod 0600 on %s: %s", key_path, exc)


if __name__ == "__main__":
    configure_logging()
    generate_keys()
