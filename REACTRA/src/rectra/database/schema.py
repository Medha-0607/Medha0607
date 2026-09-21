"""SQLite database schema definitions and table creation for RECTRA."""

from __future__ import annotations

import sqlite3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS test_sessions (
    test_id TEXT PRIMARY KEY,
    operator_id TEXT NOT NULL,
    capture_mode TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    gps_status TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    profile_version TEXT NOT NULL,
    result TEXT,
    quality_gate_status TEXT,
    session_state TEXT NOT NULL DEFAULT 'DRAFT',
    session_data TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS evidence_records (
    test_id TEXT PRIMARY KEY,
    record_json TEXT NOT NULL,
    record_digest TEXT NOT NULL,
    signature TEXT NOT NULL,
    public_key_fingerprint TEXT NOT NULL,
    image_sha256 TEXT NOT NULL,
    previous_record_hash TEXT,
    chain_valid INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (test_id) REFERENCES test_sessions(test_id)
);

CREATE TABLE IF NOT EXISTS assay_profiles (
    profile_id TEXT NOT NULL,
    profile_version TEXT NOT NULL,
    profile_json TEXT NOT NULL,
    loaded_at TEXT NOT NULL,
    PRIMARY KEY (profile_id, profile_version)
);

CREATE TABLE IF NOT EXISTS audit_chain (
    chain_entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id TEXT NOT NULL,
    record_digest TEXT NOT NULL,
    previous_record_hash TEXT,
    verified_at TEXT NOT NULL,
    verification_status TEXT NOT NULL
);
"""


def create_tables(conn: sqlite3.Connection) -> None:
    """Execute DDL statements to create all required REACTRA database tables."""
    with conn:
        conn.executescript(SCHEMA_SQL)
        # Migration for existing databases
        for col, col_type in [
            ("session_state", "TEXT NOT NULL DEFAULT 'DRAFT'"),
            ("session_data", "TEXT"),
        ]:
            try:
                conn.execute(f"ALTER TABLE test_sessions ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass
