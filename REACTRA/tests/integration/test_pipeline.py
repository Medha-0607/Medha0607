"""Integration tests for the end-to-end vision, calibration, and classification pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest

from rectra.core.constants import OutcomeClass, QualityStatus
from rectra.demo.scenarios import run_pipeline_on_image
from rectra.vision.capture import load_image_to_bgr


@pytest.mark.parametrize(
    ("image_rel_path", "expected_result", "expected_gate"),
    [
        ("data/demo/positive/DEMO-POS-001.png", OutcomeClass.POSITIVE, QualityStatus.VALID),
        ("data/demo/negative/DEMO-NEG-001.png", OutcomeClass.NEGATIVE, QualityStatus.VALID),
        ("data/demo/inconclusive/DEMO-INC-001.png", OutcomeClass.INCONCLUSIVE, QualityStatus.VALID),
    ],
)
def test_pipeline_standard_samples(
    image_rel_path: str,
    expected_result: OutcomeClass,
    expected_gate: QualityStatus,
    assay_profile,
) -> None:
    """Standard synthetic images must process through pipeline with expected outcomes."""
    img_path = Path(image_rel_path)
    if not img_path.exists():
        pytest.skip(f"Test image {image_rel_path} not found.")

    img_bgr = load_image_to_bgr(img_path)
    pipeline_res = run_pipeline_on_image(img_bgr, assay_profile)

    assert pipeline_res["card_detection"].detected is True
    assert pipeline_res["calibration"].calibration_valid is True
    assert pipeline_res["quality_gate"].status == expected_gate
    assert pipeline_res["classification"].result == expected_result


def test_pipeline_blurred_image(assay_profile) -> None:
    """Blurred edge-case image must trigger RECAPTURE REQUIRED on the quality gate."""
    img_path = Path("data/demo/edge_cases/DEMO-EDGE-BLURRED.png")
    if not img_path.exists():
        pytest.skip("Blurred sample not found.")

    img_bgr = load_image_to_bgr(img_path)
    pipeline_res = run_pipeline_on_image(img_bgr, assay_profile)

    assert pipeline_res["quality_gate"].status == QualityStatus.RECAPTURE
    assert any("Blur" in f for f in pipeline_res["quality_gate"].reasons)


def test_pipeline_glare_image(assay_profile) -> None:
    """Overexposed glare edge-case image must fail glare validity threshold."""
    img_path = Path("data/demo/edge_cases/DEMO-EDGE-OVEREXPOSED.png")
    if not img_path.exists():
        pytest.skip("Glare sample not found.")

    img_bgr = load_image_to_bgr(img_path)
    pipeline_res = run_pipeline_on_image(img_bgr, assay_profile)

    assert pipeline_res["quality_gate"].status in (QualityStatus.RECAPTURE, QualityStatus.REVIEW)
    reasons = [r.lower() for r in pipeline_res["quality_gate"].reasons]
    assert any("glare" in r or "exposure" in r for r in reasons)


def test_pipeline_critical_gate_blocks_classification(assay_profile) -> None:
    """CRITICAL SAFETY RULE: Bad image must fail quality gate and block classifier execution."""
    blurred_path = Path("data/demo/edge_cases/DEMO-EDGE-BLURRED.png")
    if not blurred_path.exists():
        pytest.skip("Blurred test image not found.")

    img_bgr = load_image_to_bgr(blurred_path)
    pipeline_res = run_pipeline_on_image(img_bgr, assay_profile)

    # 1. Quality gate must fail with RECAPTURE
    assert pipeline_res["quality_gate"].status == QualityStatus.RECAPTURE

    # 2. Classifier must NEVER be called; result must be None
    assert pipeline_res["classification"] is None

