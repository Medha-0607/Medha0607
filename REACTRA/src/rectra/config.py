"""Configuration management for RECTRA using pathlib.Path and python-dotenv."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Base project directory
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# Environment & logging
RECTRA_ENV: str = os.getenv("RECTRA_ENV", "development")
RECTRA_LOG_LEVEL: str = os.getenv("RECTRA_LOG_LEVEL", "INFO")

# Runtime & database paths
RUNTIME_DIR: Path = BASE_DIR / "runtime"
RECTRA_DB_PATH: Path = BASE_DIR / Path(os.getenv("RECTRA_DB_PATH", "runtime/rectra.db"))
RECTRA_KEY_DIR: Path = BASE_DIR / Path(os.getenv("RECTRA_KEY_DIR", "runtime/keys"))
PRIVATE_KEY_PATH: Path = RECTRA_KEY_DIR / "rectra_demo.key"
PUBLIC_KEY_PATH: Path = RECTRA_KEY_DIR / "rectra_demo.pub"

# Assay profiles
PROFILES_DIR: Path = BASE_DIR / "profiles"
RECTRA_PROFILE_ID: str = os.getenv("RECTRA_PROFILE_ID", "DEMO-ASSAY-001")
RECTRA_PROFILE_VERSION: str = os.getenv("RECTRA_PROFILE_VERSION", "1.0")
DEFAULT_PROFILE_PATH: Path = PROFILES_DIR / RECTRA_PROFILE_ID / f"v{RECTRA_PROFILE_VERSION}.json"

# Assets and Data paths
ASSETS_DIR: Path = BASE_DIR / "assets"
DATA_DIR: Path = BASE_DIR / "data"
REFERENCE_CARD_PATH: Path = ASSETS_DIR / "reference_cards" / "RECTRA_DEMO_REFERENCE_CARD.png"


def get_profile_path(profile_id: str, version: str) -> Path:
    """Resolve the filesystem path for a specific assay profile version."""
    return PROFILES_DIR / profile_id / f"v{version}.json"
