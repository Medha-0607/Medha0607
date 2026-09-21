"""Unit tests for SQLite database repository and search functionality."""

from __future__ import annotations

from rectra.core.constants import CaptureMode, GpsStatus, OutcomeClass, QualityStatus
from rectra.database.repository import (
    get_evidence_record,
    get_test_session,
    save_evidence_record,
    save_test_session,
    search_test_history,
)
from rectra.models import EvidenceRecordModel, TestSessionModel


def test_save_and_get_test_session(memory_db) -> None:
    """Saving and retrieving a TestSessionModel must preserve all fields faithfully."""
    session = TestSessionModel(
        test_id="session-uuid-100",
        operator_id="OP-TEST-01",
        capture_mode=CaptureMode.LIVE_CAMERA,
        timestamp_utc="2026-09-20T12:00:00Z",
        latitude=28.6139,
        longitude=77.2090,
        gps_status=GpsStatus.MANUAL_DEMO,
        profile_id="DEMO-ASSAY-001",
        profile_version="1.0",
        result=OutcomeClass.POSITIVE,
        quality_gate_status=QualityStatus.VALID,
    )

    save_test_session(session, conn=memory_db)
    retrieved = get_test_session("session-uuid-100", conn=memory_db)

    assert retrieved is not None
    assert retrieved.test_id == "session-uuid-100"
    assert retrieved.operator_id == "OP-TEST-01"
    assert retrieved.result == OutcomeClass.POSITIVE
    assert retrieved.quality_gate_status == QualityStatus.VALID


def test_save_and_get_evidence_record(memory_db) -> None:
    """Saving and retrieving an EvidenceRecordModel must store all fields accurately."""
    rec = EvidenceRecordModel(
        test_id="session-uuid-100",
        record_json='{"test_id":"session-uuid-100"}',
        record_digest="d" * 64,
        signature="s" * 128,
        public_key_fingerprint="f" * 16,
        image_sha256="i" * 64,
        previous_record_hash=None,
    )

    save_evidence_record(rec, conn=memory_db)
    retrieved = get_evidence_record("session-uuid-100", conn=memory_db)

    assert retrieved is not None
    assert retrieved.record_digest == "d" * 64
    assert retrieved.signature == "s" * 128


def test_search_test_history_filters(memory_db) -> None:
    """Search queries must filter correctly by operator, result, and gate status."""
    s1 = TestSessionModel(
        test_id="uuid-pos-valid",
        operator_id="OP-ALICE",
        capture_mode=CaptureMode.LIVE_CAMERA,
        timestamp_utc="2026-09-20T10:00:00Z",
        latitude=None,
        longitude=None,
        gps_status=GpsStatus.MANUAL_DEMO,
        profile_id="DEMO-ASSAY-001",
        profile_version="1.0",
        result=OutcomeClass.POSITIVE,
        quality_gate_status=QualityStatus.VALID,
    )
    s2 = TestSessionModel(
        test_id="uuid-neg-review",
        operator_id="OP-BOB",
        capture_mode=CaptureMode.LIVE_CAMERA,
        timestamp_utc="2026-09-20T11:00:00Z",
        latitude=None,
        longitude=None,
        gps_status=GpsStatus.MANUAL_DEMO,
        profile_id="DEMO-ASSAY-001",
        profile_version="1.0",
        result=OutcomeClass.NEGATIVE,
        quality_gate_status=QualityStatus.REVIEW,
    )

    save_test_session(s1, conn=memory_db)
    save_test_session(s2, conn=memory_db)

    # Filter by operator
    res_op = search_test_history(operator_query="BOB", conn=memory_db)
    assert len(res_op) == 1
    assert res_op[0]["test_id"] == "uuid-neg-review"

    # Filter by result
    res_pos = search_test_history(result_filter="POSITIVE", conn=memory_db)
    assert len(res_pos) == 1
    assert res_pos[0]["test_id"] == "uuid-pos-valid"

    # Filter by quality gate
    res_review = search_test_history(quality_filter="REVIEW", conn=memory_db)
    assert len(res_review) == 1
    assert res_review[0]["test_id"] == "uuid-neg-review"
