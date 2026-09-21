from __future__ import annotations

import sqlite3

from rectra.core.constants import SessionState
from rectra.core.session_manager import LEGAL_TRANSITIONS
from rectra.database.repository import (
    get_latest_incomplete_session,
    get_test_session,
    save_test_session,
)
from rectra.models import TestSessionModel


def test_session_state_lifecycle_transitions() -> None:
    """State machine transitions must follow legal lifecycle graph."""
    assert SessionState.CAPTURED in LEGAL_TRANSITIONS[SessionState.DRAFT]
    assert SessionState.CLASSIFIED not in LEGAL_TRANSITIONS[SessionState.DRAFT]
    assert SessionState.ANALYZING in LEGAL_TRANSITIONS[SessionState.CAPTURED]
    assert SessionState.READY_FOR_CLASSIFICATION in LEGAL_TRANSITIONS[SessionState.ANALYZING]
    assert SessionState.EVIDENCE_SEALED in LEGAL_TRANSITIONS[SessionState.CLASSIFIED]
    assert SessionState.COMPLETED in LEGAL_TRANSITIONS[SessionState.EVIDENCE_SEALED]


def test_session_persistence_and_recovery() -> None:
    """Incomplete sessions must be recoverable from SQLite upon refresh."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    from rectra.database.schema import create_tables

    create_tables(conn)

    session = TestSessionModel(
        test_id="RECOVERY-TEST-001",
        operator_id="OFFICER-TEST",
        capture_mode="IMPORTED_IMAGE",
        timestamp_utc="2026-09-21T10:00:00Z",
        latitude=None,
        longitude=None,
        gps_status="UNAVAILABLE",
        profile_id="DEMO-ASSAY-001",
        profile_version="1.0",
        result=None,
        quality_gate_status="VALID",
        session_state=SessionState.DRAFT,
        session_data='{"step": 1, "note": "draft session"}',
    )
    save_test_session(session, conn=conn)

    # Fetch by test_id
    retrieved = get_test_session("RECOVERY-TEST-001", conn=conn)
    assert retrieved is not None
    assert retrieved.test_id == "RECOVERY-TEST-001"
    assert retrieved.session_state == SessionState.DRAFT
    assert retrieved.session_data is not None
    assert "draft session" in retrieved.session_data

    # Fetch latest incomplete session
    latest = get_latest_incomplete_session(conn=conn)
    assert latest is not None
    assert latest.test_id == "RECOVERY-TEST-001"

    conn.close()
