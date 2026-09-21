"""Test Region of Interest (ROI) localization and validation on normalized reference card."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

from rectra.vision.card_detector import bgr_to_lab

logger = logging.getLogger(__name__)

# Test zone coordinates on canonical 1000x700 warped card
# TEST ZONE bounding rectangle: rx=250, ry=320, rw=500, rh=260
# Central reaction spot analysis window (centered around cx=500, cy=450)
ROI_X = 470
ROI_Y = 420
ROI_W = 60
ROI_H = 60


@dataclass
class RoiExtractionResult:
    """Extracted reaction region and statistical properties."""

    is_valid: bool
    roi_bgr: np.ndarray | None
    mean_lab: tuple[float, float, float]
    std_lab: tuple[float, float, float]
    pixel_count: int
    rejection_reason: str | None = None


def extract_test_roi(
    warped_card: np.ndarray,
    profile: dict[str, Any],
) -> RoiExtractionResult:
    """Extract and validate the test reaction spot from a canonically warped card."""
    if warped_card is None or warped_card.size == 0:
        return RoiExtractionResult(
            is_valid=False,
            roi_bgr=None,
            mean_lab=(0.0, 0.0, 0.0),
            std_lab=(0.0, 0.0, 0.0),
            pixel_count=0,
            rejection_reason="Warped card image is empty.",
        )

    h, w = warped_card.shape[:2]
    min_pixels = profile.get("quality_thresholds", {}).get("min_roi_pixel_count", 500)

    # Bound check
    x1 = max(0, min(ROI_X, w - 1))
    y1 = max(0, min(ROI_Y, h - 1))
    x2 = max(x1 + 1, min(ROI_X + ROI_W, w))
    y2 = max(y1 + 1, min(ROI_Y + ROI_H, h))

    roi_crop = warped_card[y1:y2, x1:x2]
    pixel_count = roi_crop.shape[0] * roi_crop.shape[1]

    if pixel_count < min_pixels:
        return RoiExtractionResult(
            is_valid=False,
            roi_bgr=roi_crop,
            mean_lab=(0.0, 0.0, 0.0),
            std_lab=(0.0, 0.0, 0.0),
            pixel_count=pixel_count,
            rejection_reason=(
                f"RECAPTURE REQUIRED — Test ROI contains only {pixel_count} pixels "
                f"(minimum {min_pixels} required)."
            ),
        )

    # Compute mean BGR and convert to Lab
    mean_b = float(np.mean(roi_crop[:, :, 0]))
    mean_g = float(np.mean(roi_crop[:, :, 1]))
    mean_r = float(np.mean(roi_crop[:, :, 2]))
    mean_lab = bgr_to_lab((mean_b, mean_g, mean_r))

    # Compute per-channel standard deviation
    std_b = float(np.std(roi_crop[:, :, 0]))
    std_g = float(np.std(roi_crop[:, :, 1]))
    std_r = float(np.std(roi_crop[:, :, 2]))

    # If region is entirely black or completely uniform flat artifact
    if mean_b < 5.0 and mean_g < 5.0 and mean_r < 5.0:
        return RoiExtractionResult(
            is_valid=False,
            roi_bgr=roi_crop,
            mean_lab=mean_lab,
            std_lab=(std_b, std_g, std_r),
            pixel_count=pixel_count,
            rejection_reason="RECAPTURE REQUIRED — Test ROI is fully occluded or unexposed.",
        )

    logger.info("Extracted test ROI: %d pixels, mean Lab=%s", pixel_count, mean_lab)

    return RoiExtractionResult(
        is_valid=True,
        roi_bgr=roi_crop,
        mean_lab=mean_lab,
        std_lab=(round(std_b, 2), round(std_g, 2), round(std_r, 2)),
        pixel_count=pixel_count,
    )
