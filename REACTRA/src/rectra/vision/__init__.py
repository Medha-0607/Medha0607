"""Vision pipeline for image capture, card detection, calibration, and quality gating."""

from rectra.vision.calibration import calibrate_colours, delta_e76
from rectra.vision.capture import create_capture_metadata, load_image_to_bgr
from rectra.vision.card_detector import (
    CANONICAL_HEIGHT,
    CANONICAL_WIDTH,
    bgr_to_lab,
    detect_card,
)
from rectra.vision.color_features import ColorFeatures, extract_color_features
from rectra.vision.quality_gate import evaluate_quality_gate
from rectra.vision.roi_detector import RoiExtractionResult, extract_test_roi

__all__ = [
    "CANONICAL_HEIGHT",
    "CANONICAL_WIDTH",
    "ColorFeatures",
    "RoiExtractionResult",
    "bgr_to_lab",
    "calibrate_colours",
    "create_capture_metadata",
    "delta_e76",
    "detect_card",
    "evaluate_quality_gate",
    "extract_color_features",
    "extract_test_roi",
    "load_image_to_bgr",
]
