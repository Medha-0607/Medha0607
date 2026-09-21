"""Unit tests for the measurement quality gate."""

from __future__ import annotations

import numpy as np

from rectra.core.constants import QualityStatus
from rectra.core.types import CalibrationResult, CardDetectionResult
from rectra.vision.quality_gate import evaluate_quality_gate
from rectra.vision.roi_detector import RoiExtractionResult


def test_quality_gate_all_pass(assay_profile) -> None:
    """Sharp, well-exposed image with valid card and ROI must be QualityStatus.VALID."""
    rng = np.random.RandomState(42)
    img = rng.randint(60, 200, (400, 400, 3), dtype=np.uint8)

    card_res = CardDetectionResult(detected=True, geometry_quality=0.95, reference_patch_count=6)
    calib_res = CalibrationResult(
        observed_patch_colours={},
        canonical_patch_colours={},
        calibration_matrix=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        corrected_test_colour_lab=(40.0, 20.0, 10.0),
        residual_delta_e=2.5,
        calibration_valid=True,
    )
    roi_res = RoiExtractionResult(
        is_valid=True,
        roi_bgr=np.full((50, 50, 3), 100, dtype=np.uint8),
        mean_lab=(40.0, 0.0, 0.0),
        std_lab=(1.0, 1.0, 1.0),
        pixel_count=2500,
    )

    res = evaluate_quality_gate(
        image_bgr=img,
        card_result=card_res,
        calibration_result=calib_res,
        roi_result=roi_res,
        profile=assay_profile,
    )

    assert res.status == QualityStatus.VALID
    assert len(res.reasons) == 0


def test_quality_gate_blur_rejection(assay_profile) -> None:
    """A flat blurred image must fail blur check and result in RECAPTURE."""
    flat_img = np.full((300, 300, 3), 128, dtype=np.uint8)

    card_res = CardDetectionResult(detected=True)
    calib_res = CalibrationResult(
        observed_patch_colours={},
        canonical_patch_colours={},
        calibration_matrix=[],
        corrected_test_colour_lab=(0.0, 0.0, 0.0),
        residual_delta_e=1.0,
        calibration_valid=True,
    )
    roi_res = RoiExtractionResult(
        is_valid=True,
        roi_bgr=np.zeros((10, 10, 3), dtype=np.uint8),
        mean_lab=(0.0, 0.0, 0.0),
        std_lab=(0.0, 0.0, 0.0),
        pixel_count=100,
    )

    res = evaluate_quality_gate(
        image_bgr=flat_img,
        card_result=card_res,
        calibration_result=calib_res,
        roi_result=roi_res,
        profile=assay_profile,
    )

    assert res.status == QualityStatus.RECAPTURE
    assert any("Blur detected" in r for r in res.reasons)


def test_quality_gate_glare_review(assay_profile) -> None:
    """Specular glare exceeding threshold must trigger REVIEW."""
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    img[::10, ::10] = 180
    img[1::2, 1::2] = 120
    # Add 15% pure saturated white glare (threshold is 5%)
    img[:60, :] = 255

    card_res = CardDetectionResult(detected=True)
    calib_res = CalibrationResult(
        observed_patch_colours={},
        canonical_patch_colours={},
        calibration_matrix=[],
        corrected_test_colour_lab=(0.0, 0.0, 0.0),
        residual_delta_e=1.0,
        calibration_valid=True,
    )
    roi_res = RoiExtractionResult(
        is_valid=True,
        roi_bgr=np.zeros((10, 10, 3), dtype=np.uint8),
        mean_lab=(0.0, 0.0, 0.0),
        std_lab=(0.0, 0.0, 0.0),
        pixel_count=100,
    )

    res = evaluate_quality_gate(
        image_bgr=img,
        card_result=card_res,
        calibration_result=calib_res,
        roi_result=roi_res,
        profile=assay_profile,
    )

    assert res.status == QualityStatus.REVIEW
    assert any("glare" in r.lower() for r in res.reasons)
