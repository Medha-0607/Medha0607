"""Measurement validity gate enforcing pre-classification physical and optical checks.

Evaluates blur (Laplacian variance), exposure (mean luminance), glare (pixel saturation),
reference card detection status, calibration residual error, and ROI integrity.
"""

from __future__ import annotations

import logging
from typing import Any

import cv2
import numpy as np

from rectra.core.constants import QualityStatus
from rectra.core.types import CalibrationResult, CardDetectionResult, QualityGateResult
from rectra.vision.roi_detector import RoiExtractionResult

logger = logging.getLogger(__name__)


def evaluate_quality_gate(
    image_bgr: np.ndarray,
    card_result: CardDetectionResult,
    calibration_result: CalibrationResult | None,
    roi_result: RoiExtractionResult | None,
    profile: dict[str, Any],
) -> QualityGateResult:
    """Perform pre-classification quality checks against profile thresholds."""
    q_thresh = profile.get("quality_thresholds", {})
    min_blur = q_thresh.get("min_blur_laplacian_variance", 80.0)
    min_bright = q_thresh.get("min_brightness", 50)
    max_bright = q_thresh.get("max_brightness", 220)
    max_glare = q_thresh.get("max_glare_saturation_fraction", 0.05)
    max_calib_delta_e = q_thresh.get("max_calibration_residual_delta_e", 8.0)

    reasons: list[str] = []
    is_recapture = False
    is_review = False

    # 1. Blur Check (Laplacian Variance)
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    blur_pass = laplacian_var >= min_blur
    blur_data = {
        "laplacian_variance": round(laplacian_var, 2),
        "threshold": min_blur,
        "pass": blur_pass,
    }
    if not blur_pass:
        reasons.append(
            f"Blur detected (Laplacian variance {laplacian_var:.1f} < threshold {min_blur:.1f})"
        )
        is_recapture = True

    # 2. Exposure Check (Mean Gray Value)
    mean_brightness = float(np.mean(gray))
    exposure_pass = min_bright <= mean_brightness <= max_bright
    exposure_data = {
        "mean_brightness": round(mean_brightness, 2),
        "min_threshold": min_bright,
        "max_threshold": max_bright,
        "pass": exposure_pass,
    }
    if not exposure_pass:
        if mean_brightness < min_bright:
            reasons.append(f"Underexposure (brightness {mean_brightness:.1f} < {min_bright})")
            is_recapture = True
        else:
            reasons.append(f"Overexposure (brightness {mean_brightness:.1f} > {max_bright})")
            is_recapture = True

    # 3. Glare Check (Fraction of Saturated Specular Pixels)
    saturated = (
        (image_bgr[:, :, 0] >= 254) & (image_bgr[:, :, 1] >= 254) & (image_bgr[:, :, 2] >= 254)
    )
    glare_fraction = float(np.sum(saturated) / (image_bgr.shape[0] * image_bgr.shape[1]))
    glare_pass = glare_fraction <= max_glare
    glare_data = {
        "saturation_fraction": round(glare_fraction, 4),
        "threshold": max_glare,
        "pass": glare_pass,
    }
    if not glare_pass:
        reasons.append(
            f"Excessive specular glare ({glare_fraction * 100:.1f}% saturated pixels > "
            f"{max_glare * 100:.1f}%)"
        )
        if glare_fraction > 0.20:
            is_recapture = True
        else:
            is_review = True


    # 4. Card Detection Check
    card_pass = card_result.detected
    if not card_pass:
        reasons.append(card_result.rejection_reason or "Reference card not detected")
        is_recapture = True

    # 5. Calibration Check
    calib_data: dict[str, Any] = {}
    if calibration_result is not None:
        calib_pass = (
            calibration_result.calibration_valid
            and calibration_result.residual_delta_e <= max_calib_delta_e
        )
        calib_data = {
            "residual_delta_e": calibration_result.residual_delta_e,
            "threshold": max_calib_delta_e,
            "pass": calib_pass,
        }
        if not calib_pass:
            reasons.append(
                f"Calibration residual Delta E {calibration_result.residual_delta_e:.2f} > "
                f"threshold {max_calib_delta_e:.2f}"
            )
            is_review = True

    else:
        calib_data = {"pass": False, "note": "Calibration not performed"}
        reasons.append("Calibration not performed or failed")
        is_recapture = True

    # 6. ROI Check
    roi_data: dict[str, Any] = {}
    if roi_result is not None:
        roi_pass = roi_result.is_valid
        roi_data = {
            "pixel_count": roi_result.pixel_count,
            "pass": roi_pass,
        }
        if not roi_pass:
            reasons.append(roi_result.rejection_reason or "Test ROI invalid or occluded")
            is_recapture = True
    else:
        roi_data = {"pass": False, "note": "ROI extraction failed"}
        reasons.append("Test ROI extraction failed")
        is_recapture = True

    # Determine overall gate status
    if is_recapture:
        overall_status = QualityStatus.RECAPTURE
    elif is_review:
        overall_status = QualityStatus.REVIEW
    else:
        overall_status = QualityStatus.VALID

    logger.info("Quality gate evaluated: status=%s, reasons=%s", overall_status, reasons)

    return QualityGateResult(
        status=overall_status,
        blur=blur_data,
        exposure=exposure_data,
        glare=glare_data,
        calibration=calib_data,
        roi=roi_data,
        reasons=reasons,
    )
