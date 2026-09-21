"""Authoritative database repository for RECTRA test sessions, evidence, and audit logs."""

from __future__ import annotations

import datetime
import logging
import sqlite3
from typing import Any

from rectra.config import RECTRA_DB_PATH
from rectra.database.connection import get_connection
from rectra.models import EvidenceRecordModel, TestSessionModel

logger = logging.getLogger(__name__)


def save_test_session(session: TestSessionModel, conn: sqlite3.Connection | None = None) -> None:
    """Insert or update a test session in the database."""
    should_close = False
    if conn is None:
        conn = get_connection(RECTRA_DB_PATH)
        should_close = True

    cm_str = (
        session.capture_mode.value
        if hasattr(session.capture_mode, "value")
        else str(session.capture_mode)
    )
    gps_str = (
        session.gps_status.value
        if hasattr(session.gps_status, "value")
        else str(session.gps_status)
    )
    res_str = None
    if session.result is not None:
        res_str = session.result.value if hasattr(session.result, "value") else str(session.result)
    q_str = None
    if session.quality_gate_status is not None:
        q_str = (
            session.quality_gate_status.value
            if hasattr(session.quality_gate_status, "value")
            else str(session.quality_gate_status)
        )
    created = session.created_at or datetime.datetime.now(datetime.timezone.utc).isoformat()

    sess_state = (
        session.session_state.value
        if hasattr(session.session_state, "value")
        else str(session.session_state or "DRAFT")
    )
    sess_data = session.session_data

    try:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO test_sessions (
                    test_id, operator_id, capture_mode, timestamp_utc,
                    latitude, longitude, gps_status, profile_id, profile_version,
                    result, quality_gate_status, session_state, session_data, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.test_id,
                    session.operator_id,
                    cm_str,
                    session.timestamp_utc,
                    session.latitude,
                    session.longitude,
                    gps_str,
                    session.profile_id,
                    session.profile_version,
                    res_str,
                    q_str,
                    sess_state,
                    sess_data,
                    created,
                ),
            )
        logger.info("Saved test session %s for operator %s", session.test_id, session.operator_id)
    finally:
        if should_close:
            conn.close()


def save_evidence_record(
    record: EvidenceRecordModel,
    conn: sqlite3.Connection | None = None,
) -> None:
    """Insert or update an evidence record in the database."""
    should_close = False
    if conn is None:
        conn = get_connection(RECTRA_DB_PATH)
        should_close = True

    try:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO evidence_records (
                    test_id, record_json, record_digest, signature,
                    public_key_fingerprint, image_sha256, previous_record_hash, chain_valid
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.test_id,
                    record.record_json,
                    record.record_digest,
                    record.signature,
                    record.public_key_fingerprint,
                    record.image_sha256,
                    record.previous_record_hash,
                    record.chain_valid,
                ),
            )
        logger.info("Saved cryptographic evidence record for test %s", record.test_id)
    finally:
        if should_close:
            conn.close()


def get_test_session(
    test_id: str,
    conn: sqlite3.Connection | None = None,
) -> TestSessionModel | None:
    """Retrieve a single test session by UUID."""
    should_close = False
    if conn is None:
        conn = get_connection(RECTRA_DB_PATH)
        should_close = True

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_sessions WHERE test_id = ?", (test_id,))
        row = cursor.fetchone()
        if not row:
            return None

        # Check if row has session_state and session_data
        col_names = [d[0] for d in cursor.description]
        session_state = row["session_state"] if "session_state" in col_names else "DRAFT"
        session_data = row["session_data"] if "session_data" in col_names else None

        return TestSessionModel(
            test_id=row["test_id"],
            operator_id=row["operator_id"],
            capture_mode=row["capture_mode"],
            timestamp_utc=row["timestamp_utc"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            gps_status=row["gps_status"],
            profile_id=row["profile_id"],
            profile_version=row["profile_version"],
            result=row["result"],
            quality_gate_status=row["quality_gate_status"],
            session_state=session_state,
            session_data=session_data,
            created_at=row["created_at"],
        )
    finally:
        if should_close:
            conn.close()


def get_latest_incomplete_session(
    conn: sqlite3.Connection | None = None,
) -> TestSessionModel | None:
    """Retrieve the latest incomplete test session (for crash/reload recovery)."""
    should_close = False
    if conn is None:
        conn = get_connection(RECTRA_DB_PATH)
        should_close = True

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM test_sessions
            WHERE session_state NOT IN ('COMPLETED', 'EVIDENCE_SEALED')
            ORDER BY created_at DESC LIMIT 1
            """
        )
        row = cursor.fetchone()
        if not row:
            return None

        col_names = [d[0] for d in cursor.description]
        session_state = row["session_state"] if "session_state" in col_names else "DRAFT"
        session_data = row["session_data"] if "session_data" in col_names else None

        return TestSessionModel(
            test_id=row["test_id"],
            operator_id=row["operator_id"],
            capture_mode=row["capture_mode"],
            timestamp_utc=row["timestamp_utc"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            gps_status=row["gps_status"],
            profile_id=row["profile_id"],
            profile_version=row["profile_version"],
            result=row["result"],
            quality_gate_status=row["quality_gate_status"],
            session_state=session_state,
            session_data=session_data,
            created_at=row["created_at"],
        )
    finally:
        if should_close:
            conn.close()


def get_evidence_record(
    test_id: str,
    conn: sqlite3.Connection | None = None,
) -> EvidenceRecordModel | None:
    """Retrieve the cryptographic evidence record by test_id."""
    should_close = False
    if conn is None:
        conn = get_connection(RECTRA_DB_PATH)
        should_close = True

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence_records WHERE test_id = ?", (test_id,))
        row = cursor.fetchone()
        if not row:
            return None

        return EvidenceRecordModel(
            test_id=row["test_id"],
            record_json=row["record_json"],
            record_digest=row["record_digest"],
            signature=row["signature"],
            public_key_fingerprint=row["public_key_fingerprint"],
            image_sha256=row["image_sha256"],
            previous_record_hash=row["previous_record_hash"],
            chain_valid=row["chain_valid"],
        )
    finally:
        if should_close:
            conn.close()


def search_test_history(
    test_id_query: str | None = None,
    operator_query: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    result_filter: str | None = None,
    quality_filter: str | None = None,
    limit: int = 100,
    conn: sqlite3.Connection | None = None,
) -> list[dict[str, Any]]:
    """Search and filter the test log across test sessions and evidence records."""
    should_close = False
    if conn is None:
        conn = get_connection(RECTRA_DB_PATH)
        should_close = True

    try:
        query = """
            SELECT s.test_id, s.operator_id, s.capture_mode, s.timestamp_utc,
                   s.latitude, s.longitude, s.gps_status, s.profile_id, s.profile_version,
                   s.result, s.quality_gate_status, s.created_at,
                   e.record_digest, e.signature, e.image_sha256, e.previous_record_hash
            FROM test_sessions s
            LEFT JOIN evidence_records e ON s.test_id = e.test_id
            WHERE 1=1
        """
        params: list[Any] = []

        if test_id_query and test_id_query.strip():
            query += " AND s.test_id LIKE ?"
            params.append(f"%{test_id_query.strip()}%")

        if operator_query and operator_query.strip():
            query += " AND s.operator_id LIKE ?"
            params.append(f"%{operator_query.strip()}%")

        if date_from:
            query += " AND s.timestamp_utc >= ?"
            params.append(date_from)

        if date_to:
            query += " AND s.timestamp_utc <= ?"
            params.append(date_to)

        if result_filter and result_filter != "ALL":
            query += " AND s.result = ?"
            params.append(result_filter)

        if quality_filter and quality_filter != "ALL":
            query += " AND s.quality_gate_status = ?"
            params.append(quality_filter)

        query += " ORDER BY s.rowid DESC LIMIT ?"
        params.append(limit)

        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for r in rows:
            results.append(
                {
                    "test_id": r["test_id"],
                    "operator_id": r["operator_id"],
                    "capture_mode": r["capture_mode"],
                    "timestamp_utc": r["timestamp_utc"],
                    "latitude": r["latitude"],
                    "longitude": r["longitude"],
                    "gps_status": r["gps_status"],
                    "profile_id": r["profile_id"],
                    "profile_version": r["profile_version"],
                    "result": r["result"],
                    "quality_gate_status": r["quality_gate_status"],
                    "record_digest": r["record_digest"],
                    "image_sha256": r["image_sha256"],
                    "previous_record_hash": r["previous_record_hash"],
                }
            )
        return results

    finally:
        if should_close:
            conn.close()


def append_audit_chain_entry(
    test_id: str,
    record_digest: str,
    previous_record_hash: str | None,
    verification_status: str,
    conn: sqlite3.Connection | None = None,
) -> None:
    """Record an audit chain verification entry."""
    should_close = False
    if conn is None:
        conn = get_connection(RECTRA_DB_PATH)
        should_close = True

    try:
        with conn:
            conn.execute(
                """
                INSERT INTO audit_chain (
                    test_id, record_digest, previous_record_hash, verified_at, verification_status
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    test_id,
                    record_digest,
                    previous_record_hash,
                    datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    verification_status,
                ),
            )
    finally:
        if should_close:
            conn.close()
