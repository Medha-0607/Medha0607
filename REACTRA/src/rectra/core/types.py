"""Common domain types and dataclasses for RECTRA."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from rectra.core.constants import (
    CaptureMode,
    ChainStatus,
    GpsStatus,
    OutcomeClass,
    PassportStatus,
    QualityStatus,
    SignatureStatus,
)


@dataclass
class CaptureMetadata:
    """Metadata captured alongside the physical image."""

    capture_mode: Literal["LIVE_CAMERA", "IMPORTED_IMAGE"] | CaptureMode
    timestamp_utc: str
    operator_id: str
    latitude: float | None
    longitude: float | None
    gps_status: Literal["GPS_DEVICE", "MANUAL_DEMO", "UNAVAILABLE"] | GpsStatus
    profile_id: str
    profile_version: str


@dataclass
class CardDetectionResult:
    """Result of searching and localizing the reference card."""

    detected: bool
    profile_id: str | None = None
    profile_version: str | None = None
    geometry_quality: float = 0.0
    reference_patch_count: int = 0
    confidence: float = 0.0
    rejection_reason: str | None = None
    corners: list[list[float]] = field(default_factory=list)
    warped_image: Any = None


@dataclass
class CalibrationResult:
    """Result of CIE Lab least-squares colour calibration."""

    observed_patch_colours: dict[str, tuple[float, float, float]]
    canonical_patch_colours: dict[str, tuple[float, float, float]]
    calibration_matrix: list[list[float]]
    corrected_test_colour_lab: tuple[float, float, float]
    residual_delta_e: float
    calibration_valid: bool
    method: str = "least_squares_lab"


@dataclass
class QualityGateResult:
    """Pre-classification measurement quality gate evaluation."""

    status: Literal["VALID", "REVIEW", "RECAPTURE"] | QualityStatus
    blur: dict[str, Any]
    exposure: dict[str, Any]
    glare: dict[str, Any]
    calibration: dict[str, Any]
    roi: dict[str, Any]
    reasons: list[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    """Presumptive classification output."""

    result: Literal["POSITIVE", "NEGATIVE", "INCONCLUSIVE"] | OutcomeClass
    class_scores: dict[str, float]
    classification_score: float
    model_version: str
    algorithm_version: str
    note: str = "Prototype classification score — not laboratory certainty."


@dataclass
class ChainVerificationResult:
    """Result of cryptographic audit chain verification."""

    valid: bool
    total_records: int
    broken_at_test_id: str | None = None
    reason: str | None = None


@dataclass
class ReliabilityPassport:
    """Field Test Reliability Passport structuring quality and evidence attestation."""

    # Capture Section
    capture_mode: str
    timestamp_utc: str
    operator_id: str
    gps_status: str
    latitude: float | None
    longitude: float | None

    # Measurement Section
    card_detected: bool
    card_profile: str
    calibration_valid: bool
    calibration_residual_delta_e: float
    image_quality: str
    roi_quality: str

    # Classification Section
    presumptive_result: str
    class_scores: dict[str, float]
    classification_score: float
    model_version: str
    algorithm_version: str

    # Evidence Section
    image_sha256: str
    record_digest: str
    signature_status: str | SignatureStatus
    chain_status: str | ChainStatus

    # Overall
    overall_status: str | PassportStatus
