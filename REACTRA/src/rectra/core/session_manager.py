"""Session lifecycle manager for REACTRA field testing workflows.

Maintains active test sessions across Streamlit navigation and provides
deterministic recovery from SQLite persistence upon browser refresh/reload.
"""

from __future__ import annotations

import datetime
import json
import logging
import uuid
from typing import Any

import streamlit as st

from rectra.core.constants import CaptureMode, GpsStatus, SessionState
from rectra.database.repository import (
    get_latest_incomplete_session,
    get_test_session,
    save_test_session,
)
from rectra.models import TestSessionModel

logger = logging.getLogger(__name__)

# Valid state machine transitions
LEGAL_TRANSITIONS: dict[SessionState, set[SessionState]] = {
    SessionState.DRAFT: {SessionState.CAPTURED},
    SessionState.CAPTURED: {SessionState.ANALYZING, SessionState.VALIDATION_FAILED},
    SessionState.ANALYZING: {
        SessionState.VALIDATION_FAILED,
        SessionState.READY_FOR_CLASSIFICATION,
        SessionState.REVIEW_REQUIRED,
    },
    SessionState.VALIDATION_FAILED: {SessionState.REFERRAL_REQUIRED, SessionState.CAPTURED},
    SessionState.READY_FOR_CLASSIFICATION: {SessionState.CLASSIFIED, SessionState.REVIEW_REQUIRED},
    SessionState.CLASSIFIED: {SessionState.EVIDENCE_SEALED, SessionState.REFERRAL_REQUIRED},
    SessionState.REVIEW_REQUIRED: {SessionState.CLASSIFIED, SessionState.REFERRAL_REQUIRED},
    SessionState.REFERRAL_REQUIRED: {SessionState.EVIDENCE_SEALED, SessionState.COMPLETED},
    SessionState.EVIDENCE_SEALED: {SessionState.COMPLETED},
    SessionState.COMPLETED: set(),
}


def init_session_state() -> None:
    """Initialize Streamlit session keys if not already present."""
    if "active_test_id" not in st.session_state:
        st.session_state["active_test_id"] = None
    if "active_session_data" not in st.session_state:
        st.session_state["active_session_data"] = None
    if "active_session_state" not in st.session_state:
        st.session_state["active_session_state"] = None
    if "wizard_step" not in st.session_state:
        st.session_state["wizard_step"] = 1


def create_new_draft(
    operator_id: str,
    profile_id: str,
    profile_version: str,
    capture_mode: CaptureMode | str = CaptureMode.IMPORTED_IMAGE,
    latitude: float | None = None,
    longitude: float | None = None,
    gps_status: GpsStatus | str = GpsStatus.UNAVAILABLE,
) -> str:
    """Create a new field test session in DRAFT state and persist to SQLite."""
    test_id = str(uuid.uuid4())
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

    session_model = TestSessionModel(
        test_id=test_id,
        operator_id=operator_id.strip(),
        capture_mode=capture_mode,
        timestamp_utc=now_utc,
        latitude=latitude,
        longitude=longitude,
        gps_status=gps_status,
        profile_id=profile_id,
        profile_version=profile_version,
        session_state=SessionState.DRAFT,
        session_data=json.dumps({"created_at": now_utc, "step": 1}),
        created_at=now_utc,
    )
    save_test_session(session_model)

    st.session_state["active_test_id"] = test_id
    st.session_state["active_session_data"] = {
        "metadata": {
            "test_id": test_id,
            "operator_id": operator_id,
            "timestamp_utc": now_utc,
            "latitude": latitude,
            "longitude": longitude,
            "gps_status": str(gps_status),
            "profile_id": profile_id,
            "profile_version": profile_version,
            "capture_mode": str(capture_mode),
        }
    }
    st.session_state["active_session_state"] = SessionState.DRAFT
    st.session_state["wizard_step"] = 2
    logger.info("Created new draft test session %s for operator %s", test_id, operator_id)
    return test_id


def get_active_session() -> dict[str, Any] | None:
    """Retrieve active session data, restoring from SQLite if refreshed."""
    # First check memory
    if st.session_state.get("active_session_data") and st.session_state.get("active_test_id"):
        return st.session_state["active_session_data"]

    # Try recovering from DB if active_test_id is set
    active_id = st.session_state.get("active_test_id")
    if active_id:
        db_session = get_test_session(active_id)
        if db_session:
            _restore_from_db_model(db_session)
            return st.session_state["active_session_data"]

    # Try recovering latest incomplete session from DB
    latest = get_latest_incomplete_session()
    if latest:
        _restore_from_db_model(latest)
        return st.session_state["active_session_data"]

    return None


def _restore_from_db_model(db_session: TestSessionModel) -> None:
    """Populate Streamlit state from a persistent TestSessionModel."""
    st.session_state["active_test_id"] = db_session.test_id
    st.session_state["active_session_state"] = db_session.session_state

    parsed_data = {}
    if db_session.session_data:
        try:
            parsed_data = json.loads(db_session.session_data)
        except Exception:
            parsed_data = {}

    if "metadata" not in parsed_data:
        parsed_data["metadata"] = {
            "test_id": db_session.test_id,
            "operator_id": db_session.operator_id,
            "timestamp_utc": db_session.timestamp_utc,
            "latitude": db_session.latitude,
            "longitude": db_session.longitude,
            "gps_status": str(db_session.gps_status),
            "profile_id": db_session.profile_id,
            "profile_version": db_session.profile_version,
            "capture_mode": str(db_session.capture_mode),
        }

    parsed_data["test_id"] = db_session.test_id
    st.session_state["active_session_data"] = parsed_data


def update_active_session(
    pipeline_dict: dict[str, Any],
    new_state: SessionState,
) -> None:
    """Update active session data and transition lifecycle state in SQLite."""
    test_id = st.session_state.get("active_test_id") or pipeline_dict.get("test_id")
    if not test_id:
        test_id = str(uuid.uuid4())
        st.session_state["active_test_id"] = test_id

    st.session_state["active_session_data"] = pipeline_dict
    st.session_state["active_session_state"] = new_state

    # Persist serialized data to SQLite
    meta = pipeline_dict.get("metadata")
    q_gate = pipeline_dict.get("quality_gate")
    cls_res = pipeline_dict.get("classification")

    q_stat = (
        str(q_gate.status.value if hasattr(q_gate.status, "value") else q_gate.status)
        if q_gate
        else None
    )
    res_str = (
        str(cls_res.result.value if hasattr(cls_res.result, "value") else cls_res.result)
        if cls_res
        else None
    )

    # Safe JSON serialization for session_data
    serializable = {}
    for k, v in pipeline_dict.items():
        if k in ("image_bgr", "warped_image"):
            continue  # Do not store raw matrices in JSON
        if hasattr(v, "__dict__"):
            serializable[k] = str(v)
        else:
            try:
                json.dumps(v)
                serializable[k] = v
            except (TypeError, ValueError):
                serializable[k] = str(v)

    session_model = TestSessionModel(
        test_id=test_id,
        operator_id=meta.operator_id
        if hasattr(meta, "operator_id")
        else meta.get("operator_id", "DEMO-OP"),
        capture_mode=meta.capture_mode
        if hasattr(meta, "capture_mode")
        else meta.get("capture_mode", CaptureMode.IMPORTED_IMAGE),
        timestamp_utc=meta.timestamp_utc
        if hasattr(meta, "timestamp_utc")
        else meta.get("timestamp_utc", datetime.datetime.now(datetime.timezone.utc).isoformat()),
        latitude=meta.latitude if hasattr(meta, "latitude") else meta.get("latitude"),
        longitude=meta.longitude if hasattr(meta, "longitude") else meta.get("longitude"),
        gps_status=meta.gps_status
        if hasattr(meta, "gps_status")
        else meta.get("gps_status", GpsStatus.UNAVAILABLE),
        profile_id=meta.profile_id
        if hasattr(meta, "profile_id")
        else meta.get("profile_id", "DEMO-ASSAY-001"),
        profile_version=meta.profile_version
        if hasattr(meta, "profile_version")
        else meta.get("profile_version", "1.0"),
        result=res_str,
        quality_gate_status=q_stat,
        session_state=new_state,
        session_data=json.dumps(serializable),
    )
    save_test_session(session_model)
    logger.info("Updated active session %s to state %s", test_id, new_state)


def clear_active_session() -> None:
    """Reset active session state in memory."""
    st.session_state["active_test_id"] = None
    st.session_state["active_session_data"] = None
    st.session_state["active_session_state"] = None
    st.session_state["wizard_step"] = 1
