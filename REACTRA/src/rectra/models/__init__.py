"""Domain models for RECTRA test sessions, measurement, evidence, and referral."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from rectra.core.constants import (
    CaptureMode,
    GpsStatus,
    OutcomeClass,
    QualityStatus,
)


@dataclass
class TestSessionModel:
    """Represents a complete field test session."""

    __test__ = False

    test_id: str
    operator_id: str
    capture_mode: str | CaptureMode
    timestamp_utc: str
    latitude: float | None
    longitude: float | None
    gps_status: str | GpsStatus
    profile_id: str
    profile_version: str
    result: str | OutcomeClass | None = None
    quality_gate_status: str | QualityStatus | None = None
    session_state: str = "DRAFT"
    session_data: str | None = None
    created_at: str | None = None


@dataclass
class EvidenceRecordModel:
    """Represents the cryptographic evidence preserved in the database."""

    test_id: str
    record_json: str
    record_digest: str
    signature: str
    public_key_fingerprint: str
    image_sha256: str
    previous_record_hash: str | None = None
    chain_valid: int = 1


@dataclass
class ReferralPacketModel:
    """Represents a laboratory referral packet."""

    test_id: str
    reason: str
    timestamp_utc: str
    operator_id: str
    profile_id: str
    profile_version: str
    quality_gate_status: str
    presumptive_result: str
    image_sha256: str
    record_digest: str
    details: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "EvidenceRecordModel",
    "ReferralPacketModel",
    "TestSessionModel",
]
