"""Shared pytest fixtures for the REACTRA test suite."""

from __future__ import annotations

import sqlite3
from typing import Any, Generator

import numpy as np
import pytest

from rectra.config import DEFAULT_PROFILE_PATH
from rectra.database.schema import create_tables
from rectra.profiles.loader import load_profile


@pytest.fixture
def assay_profile() -> dict[str, Any]:
    """Fixture providing the default assay profile dictionary."""
    return load_profile(DEFAULT_PROFILE_PATH)


@pytest.fixture
def memory_db() -> Generator[sqlite3.Connection, None, None]:
    """Fixture providing a clean, fully initialized in-memory SQLite connection."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_tables(conn)
    yield conn
    conn.close()


@pytest.fixture
def sample_card_image() -> np.ndarray:
    """Fixture providing a synthetic card-like BGR image (1000x700)."""
    img = np.full((700, 1000, 3), 240, dtype=np.uint8)
    size = 70
    # Top-left
    img[20 : 20 + size, 20 : 20 + size] = 0
    # Top-right
    img[20 : 20 + size, 1000 - 20 - size : 1000 - 20] = 0
    # Bottom-right
    img[700 - 20 - size : 700 - 20, 1000 - 20 - size : 1000 - 20] = 0
    # Bottom-left
    img[700 - 20 - size : 700 - 20, 20 : 20 + size] = 0
    return img


@pytest.fixture
def sample_blur_image() -> np.ndarray:
    """Fixture providing a uniform blurry image with near-zero Laplacian variance."""
    return np.full((500, 500, 3), 128, dtype=np.uint8)
