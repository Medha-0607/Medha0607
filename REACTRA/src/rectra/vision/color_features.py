"""Feature extraction for calibrated colorimetric test reaction regions."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from rectra.vision.calibration import delta_e76

logger = logging.getLogger(__name__)


@dataclass
class ColorFeatures:
    """Interpretable colorimetric features extracted from corrected test ROI."""

    mean_lab: tuple[float, float, float]
    median_lab: tuple[float, float, float]
    mean_hsv: tuple[float, float, float]
    std_lab: tuple[float, float, float]
    delta_e_to_centroids: dict[str, float]
    l_percentiles: tuple[float, float, float]  # (10th, 50th, 90th)


def extract_color_features(
    roi_bgr: np.ndarray,
    corrected_lab: tuple[float, float, float],
    profile: dict[str, Any],
) -> ColorFeatures:
    """Extract interpretable statistical colour features and class centroid distances."""
    if roi_bgr is None or roi_bgr.size == 0:
        return ColorFeatures(
            mean_lab=corrected_lab,
            median_lab=corrected_lab,
            mean_hsv=(0.0, 0.0, 0.0),
            std_lab=(0.0, 0.0, 0.0),
            delta_e_to_centroids={},
            l_percentiles=(0.0, 0.0, 0.0),
        )

    # Convert ROI to Lab and HSV
    roi_lab = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    # Scale OpenCV Lab to CIE standard
    l_channel = roi_lab[:, :, 0] * 100.0 / 255.0
    a_channel = roi_lab[:, :, 1] - 128.0
    b_channel = roi_lab[:, :, 2] - 128.0

    median_l = float(np.median(l_channel))
    median_a = float(np.median(a_channel))
    median_b = float(np.median(b_channel))

    std_l = float(np.std(l_channel))
    std_a = float(np.std(a_channel))
    std_b = float(np.std(b_channel))

    # HSV
    roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    mean_h = float(np.mean(roi_hsv[:, :, 0]))
    mean_s = float(np.mean(roi_hsv[:, :, 1]))
    mean_v = float(np.mean(roi_hsv[:, :, 2]))

    # Percentiles of L
    p10 = float(np.percentile(l_channel, 10))
    p50 = float(np.percentile(l_channel, 50))
    p90 = float(np.percentile(l_channel, 90))

    # Distances to configured class centroids from profile
    centroids = profile.get("class_centroids_lab", {})
    delta_e_distances: dict[str, float] = {}

    for cls_name, cent in centroids.items():
        cent_tuple = (float(cent["L"]), float(cent["a"]), float(cent["b"]))
        dist = delta_e76(corrected_lab, cent_tuple)
        delta_e_distances[cls_name] = round(dist, 2)

    return ColorFeatures(
        mean_lab=(
            round(corrected_lab[0], 2),
            round(corrected_lab[1], 2),
            round(corrected_lab[2], 2),
        ),
        median_lab=(round(median_l, 2), round(median_a, 2), round(median_b, 2)),
        mean_hsv=(round(mean_h, 2), round(mean_s, 2), round(mean_v, 2)),
        std_lab=(round(std_l, 2), round(std_a, 2), round(std_b, 2)),
        delta_e_to_centroids=delta_e_distances,
        l_percentiles=(round(p10, 2), round(p50, 2), round(p90, 2)),
    )
