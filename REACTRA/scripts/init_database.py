"""Initialize the RECTRA SQLite database schema and seed the active assay profile."""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path

from rectra.config import DEFAULT_PROFILE_PATH, RECTRA_DB_PATH
from rectra.core.logging_config import configure_logging
from rectra.database.connection import get_connection
from rectra.database.schema import create_tables

logger = logging.getLogger(__name__)


def init_db(db_path: Path | None = None, reset: bool = False) -> None:
    """Initialize database tables and register the default assay profile."""
    path = db_path or RECTRA_DB_PATH
    if reset and path.exists():
        logger.info("Reset requested: removing existing database at %s", path)
        path.unlink()

    logger.info("Initializing database at %s", path)
    conn = get_connection(path)

    try:
        create_tables(conn)
        logger.info("Database tables verified/created.")

        # Seed default profile if present
        if DEFAULT_PROFILE_PATH.exists():
            with open(DEFAULT_PROFILE_PATH, "r", encoding="utf-8") as f:
                profile_data = json.load(f)

            profile_id = profile_data["profile_id"]
            profile_version = profile_data["profile_version"]
            loaded_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

            with conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO assay_profiles
                    (profile_id, profile_version, profile_json, loaded_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (profile_id, profile_version, json.dumps(profile_data), loaded_at),
                )
            logger.info("Registered assay profile %s v%s in database.", profile_id, profile_version)
        else:
            logger.warning("Default profile not found at %s. Skipping seed.", DEFAULT_PROFILE_PATH)

    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    configure_logging()
    should_reset = "--reset" in sys.argv
    init_db(reset=should_reset)
