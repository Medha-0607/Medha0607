"""Logging configuration for RECTRA."""

from __future__ import annotations

import logging
import os


def configure_logging() -> None:
    """Configure standardized application logging based on RECTRA_LOG_LEVEL."""
    level = os.getenv("RECTRA_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )
