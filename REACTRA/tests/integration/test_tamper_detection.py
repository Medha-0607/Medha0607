"""Integration tests for cryptographic evidence tamper detection."""

from __future__ import annotations

import copy

import pytest

from rectra.core.constants import CaptureMode, GpsStatus, OutcomeClass, QualityStatus
from rectra.evidence.canonical import build_canonical_record_dict
from rectra.evidence.envelope import create_evidence_envelope, verify_envelope
from rectra.evidence.hashing import compute_record_digest
from rectra.evidence.signing import get_public_key_fingerprint, sign_digest
from rectra.models import TestSessionModel


@pytest.fixture
def sample_valid_envelope():
    """Generates a valid signed evidence envelope for tamper testing."""
    fingerprint = get_public_key_fingerprint()

    session = TestSessionModel(
        test_id="session-tamper-test",
        timestamp_utc="2026-09-20T15:00:00Z",
        operator_id="DET-TAMPER-01",
        capture_mode=CaptureMode.LIVE_CAMERA,
        profile_id="DEMO-ASSAY-001",
        profile_version="1.0",
        latitude=28.6139,
        longitude=77.2090,
        gps_status=GpsStatus.MANUAL_DEMO,
        quality_gate_status=QualityStatus.VALID,
        result=OutcomeClass.POSITIVE,
    )

    canonical_dict = build_canonical_record_dict(
        test_id=session.test_id,
        operator_id=session.operator_id,
        capture_mode="LIVE_CAMERA",
        timestamp_utc=session.timestamp_utc,
        latitude=session.latitude,
        longitude=session.longitude,
        gps_status="MANUAL_DEMO",
        profile_id="DEMO-ASSAY-001",
        profile_version="1.0",
        reference_card_version="1.0",
        algorithm_version="1.0",
        model_version="1.0",
        result="POSITIVE",
        classification_score=0.965,
        measurement_quality="HIGH",
        quality_gate_status="VALID",
        image_sha256="7" * 64,
        previous_record_hash=None,
    )

    digest = compute_record_digest(canonical_dict)
    signature = sign_digest(digest)

    rec_dict = dict(canonical_dict)
    rec_dict["record_digest"] = digest
    rec_dict["signature"] = signature
    rec_dict["public_key_fingerprint"] = fingerprint

    return create_evidence_envelope(rec_dict)


def test_tamper_detection_unmodified(sample_valid_envelope) -> None:
    """An untouched envelope must verify with status True."""
    is_valid, reason = verify_envelope(sample_valid_envelope)
    assert is_valid is True
    assert "RECORD VERIFIED" in reason


def test_tamper_detection_altered_result(sample_valid_envelope) -> None:
    """Modifying presumptive result from POSITIVE to NEGATIVE must break verification."""
    tampered = copy.deepcopy(sample_valid_envelope)
    tampered["evidence_record"]["result"] = "NEGATIVE"

    is_valid, reason = verify_envelope(tampered)
    assert is_valid is False
    assert "Digest mismatch" in reason or "altered" in reason


def test_tamper_detection_altered_operator(sample_valid_envelope) -> None:
    """Modifying the operator ID in the canonical record must be detected."""
    tampered = copy.deepcopy(sample_valid_envelope)
    tampered["evidence_record"]["operator_id"] = "DET-ATTACKER-99"

    is_valid, reason = verify_envelope(tampered)
    assert is_valid is False
    assert "Digest mismatch" in reason or "altered" in reason


def test_tamper_detection_altered_score(sample_valid_envelope) -> None:
    """Modifying a numeric score must trigger digest mismatch."""
    tampered = copy.deepcopy(sample_valid_envelope)
    tampered["evidence_record"]["classification_score"] = 0.9999

    is_valid, reason = verify_envelope(tampered)
    assert is_valid is False
    assert "Digest mismatch" in reason or "altered" in reason


def test_tamper_detection_altered_signature(sample_valid_envelope) -> None:
    """Modifying one character of the signature must fail signature verification."""
    tampered = copy.deepcopy(sample_valid_envelope)
    curr_sig = tampered["evidence_record"]["signature"]
    flipped_char = "0" if curr_sig[0] != "0" else "1"
    tampered["evidence_record"]["signature"] = flipped_char + curr_sig[1:]

    is_valid, reason = verify_envelope(tampered)
    assert is_valid is False
    assert "signature is invalid" in reason.lower()
