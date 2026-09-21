"""Unit tests for the laboratory referral packet generator."""

from __future__ import annotations

from pathlib import Path

from rectra.core.constants import (
    DISCLAIMER_LAB_REQUIRED,
    DISCLAIMER_PRESUMPTIVE,
    CaptureMode,
    GpsStatus,
    OutcomeClass,
    QualityStatus,
    SignatureStatus,
)
from rectra.core.types import CaptureMetadata, ClassificationResult, QualityGateResult
from rectra.referral.lab_packet import generate_lab_packet, should_refer_to_lab


def test_should_refer_to_lab_conditions() -> None:
    """Referral must trigger on REVIEW, RECAPTURE, or INCONCLUSIVE outcomes."""
    assert should_refer_to_lab(QualityStatus.VALID.value, OutcomeClass.POSITIVE.value) is False
    assert should_refer_to_lab(QualityStatus.VALID.value, OutcomeClass.NEGATIVE.value) is False

    assert should_refer_to_lab(QualityStatus.VALID.value, OutcomeClass.INCONCLUSIVE.value) is True
    assert should_refer_to_lab(QualityStatus.REVIEW.value, OutcomeClass.POSITIVE.value) is True
    assert should_refer_to_lab(QualityStatus.RECAPTURE.value, OutcomeClass.NEGATIVE.value) is True


def test_generate_lab_packet(tmp_path: Path) -> None:
    """Packet generator must write valid JSON and HTML with non-negotiable safety disclaimers."""
    meta = CaptureMetadata(
        capture_mode=CaptureMode.LIVE_CAMERA,
        timestamp_utc="2026-09-20T14:30:00Z",
        operator_id="DET-REF-1",
        latitude=28.6139,
        longitude=77.2090,
        gps_status=GpsStatus.MANUAL_DEMO,
        profile_id="DEMO-ASSAY-001",
        profile_version="1.0",
    )

    q_gate = QualityGateResult(
        status=QualityStatus.REVIEW,
        blur={"pass": True},
        exposure={"pass": True},
        glare={"pass": True},
        calibration={"pass": True},
        roi={"pass": True},
        reasons=["Ambiguous test reaction"],
    )

    classification = ClassificationResult(
        result=OutcomeClass.INCONCLUSIVE,
        class_scores={"POSITIVE": 0.48, "NEGATIVE": 0.52},
        classification_score=0.52,
        model_version="1.0",
        algorithm_version="1.0",
    )

    json_p, html_p = generate_lab_packet(
        test_id="test-ref-001",
        metadata=meta,
        quality_gate=q_gate,
        classification=classification,
        image_sha256="e" * 64,
        record_digest="d" * 64,
        signature_status=SignatureStatus.VALID.value,
        output_dir=tmp_path,
    )

    assert json_p.exists()
    assert html_p.exists()

    html_content = html_p.read_text(encoding="utf-8")
    assert DISCLAIMER_PRESUMPTIVE in html_content
    assert DISCLAIMER_LAB_REQUIRED in html_content
    assert "DET-REF-1" in html_content
