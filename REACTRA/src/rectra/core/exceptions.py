"""Custom exception hierarchy for RECTRA."""

from __future__ import annotations


class RectraError(Exception):
    """Base exception for all RECTRA domain errors."""


class ProfileError(RectraError):
    """Raised when an assay profile is missing, malformed, or unsupported."""


class CaptureError(RectraError):
    """Raised when camera or image capture fails."""


class CardDetectionError(RectraError):
    """Raised when the reference card cannot be detected or located."""


class CalibrationError(RectraError):
    """Raised when colour calibration fails or has insufficient reference patches."""


class QualityGateError(RectraError):
    """Raised when an image fails the quality gate and cannot be interpreted."""


class ClassificationError(RectraError):
    """Raised when presumptive classification encounters an error."""


class EvidenceError(RectraError):
    """Raised when evidence canonicalization, hashing, or packaging fails."""


class SignatureError(EvidenceError):
    """Raised when digital signing or signature verification fails."""


class ChainIntegrityError(EvidenceError):
    """Raised when hash chain continuity or verification fails."""


class DatabaseError(RectraError):
    """Raised when a database operation encounters a failure."""
