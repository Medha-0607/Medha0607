"""SQLite connection manager for RECTRA."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from rectra.config import RECTRA_DB_PATH


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Obtain a SQLite database connection with row factory enabled."""
    target_path = Path(db_path) if db_path is not None else RECTRA_DB_PATH
    if target_path != Path(":memory:"):
        target_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
