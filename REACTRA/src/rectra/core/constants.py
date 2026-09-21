"""Constants, enumerations, and standardized disclaimer texts for RECTRA."""

from __future__ import annotations

from enum import StrEnum


class OutcomeClass(StrEnum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    INCONCLUSIVE = "INCONCLUSIVE"


class QualityStatus(StrEnum):
    VALID = "VALID"
    REVIEW = "REVIEW"
    RECAPTURE = "RECAPTURE"


class PassportStatus(StrEnum):
    READY = "READY"
    REVIEW = "REVIEW"
    RECAPTURE = "RECAPTURE"


class CaptureMode(StrEnum):
    LIVE_CAMERA = "LIVE_CAMERA"
    IMPORTED_IMAGE = "IMPORTED_IMAGE"


class GpsStatus(StrEnum):
    GPS_DEVICE = "GPS_DEVICE"
    MANUAL_DEMO = "MANUAL_DEMO"
    UNAVAILABLE = "UNAVAILABLE"


class SignatureStatus(StrEnum):
    VALID = "VALID"
    INVALID = "INVALID"
    NOT_SIGNED = "NOT_SIGNED"


class ChainStatus(StrEnum):
    INTACT = "INTACT"
    BROKEN = "BROKEN"
    NOT_CHAINED = "NOT_CHAINED"


class SessionState(StrEnum):
    """Lifecycle states for a field test session."""

    DRAFT = "DRAFT"
    CAPTURED = "CAPTURED"
    ANALYZING = "ANALYZING"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    READY_FOR_CLASSIFICATION = "READY_FOR_CLASSIFICATION"
    CLASSIFIED = "CLASSIFIED"
    EVIDENCE_SEALED = "EVIDENCE_SEALED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REFERRAL_REQUIRED = "REFERRAL_REQUIRED"
    COMPLETED = "COMPLETED"


class OracleStatus(StrEnum):
    """Explicit typed statuses for validation scenarios and test oracles."""

    VALID = "VALID"
    REVIEW = "REVIEW"
    RECAPTURE_REQUIRED = "RECAPTURE_REQUIRED"
    INCONCLUSIVE = "INCONCLUSIVE"
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    INTEGRITY_VERIFICATION_FAILED = "INTEGRITY_VERIFICATION_FAILED"
    CHAIN_VERIFICATION_FAILED = "CHAIN_VERIFICATION_FAILED"


# Cryptographic & Canonical Formats
CANONICAL_ALGORITHM = "json-sort-keys-compact-utf8-v1"
EVIDENCE_FORMAT_VERSION = "1.0"
ENVELOPE_FORMAT = "reactra-evidence-v1"

# Standard Disclaimers
DISCLAIMER_PRESUMPTIVE = "PRESUMPTIVE FIELD-TEST RESULT"
DISCLAIMER_LAB_REQUIRED = "Laboratory confirmation is required."
DISCLAIMER_SYNTHETIC_NOTE = (
    "This prototype does not replace laboratory confirmatory testing. "
    "Prototype evaluation uses controlled/synthetic demonstration data "
    "and is not validated for real-world forensic deployment."
)
