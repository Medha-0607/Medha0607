"""Reference card detection, QR code decoding, and perspective normalization.

Identifies the 4 corner square fiducials and/or rectangular card boundary,
decodes the embedded profile QR code, warps the card to canonical coordinates (1000x700),
and extracts the 6 reference colour patches.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import cv2
import numpy as np

from rectra.core.types import CardDetectionResult
from rectra.profiles.loader import load_profile

logger = logging.getLogger(__name__)

CANONICAL_WIDTH = 1000
CANONICAL_HEIGHT = 700

# Canonical patch coordinates on 1000x700 card: (x, y, w, h)
CANONICAL_PATCH_BOXES = {
    "white": (100, 130, 70, 70),
    "black": (240, 130, 70, 70),
    "red": (380, 130, 70, 70),
    "green": (520, 130, 70, 70),
    "blue": (660, 130, 70, 70),
    "grey": (800, 130, 70, 70),
}


def bgr_to_lab(bgr_pixel: tuple[float, float, float] | np.ndarray) -> tuple[float, float, float]:
    """Convert an 8-bit BGR color to CIE Lab (L: 0..100, a: -128..127, b: -128..127)."""
    if isinstance(bgr_pixel, tuple):
        arr = np.uint8([[[int(bgr_pixel[0]), int(bgr_pixel[1]), int(bgr_pixel[2])]]])
    else:
        arr = np.uint8([[bgr_pixel]])

    lab = cv2.cvtColor(arr, cv2.COLOR_BGR2LAB)
    cv_l, cv_a, cv_b = lab[0, 0]
    # Convert OpenCV scaling to standard CIE Lab
    L = float(cv_l) * 100.0 / 255.0
    a = float(cv_a) - 128.0
    b = float(cv_b) - 128.0
    return (round(L, 2), round(a, 2), round(b, 2))


def order_quad_points(pts: np.ndarray) -> np.ndarray:
    """Order 4 points in sequence: Top-Left, Top-Right, Bottom-Right, Bottom-Left."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Top-Left
    rect[2] = pts[np.argmax(s)]  # Bottom-Right

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Top-Right
    rect[3] = pts[np.argmax(diff)]  # Bottom-Left
    return rect


def find_corner_fiducials(gray: np.ndarray) -> np.ndarray | None:
    """Find 4 corner black square fiducials."""
    # Threshold for dark squares
    _, thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    fiducials = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 300 or area > 35000:
            continue
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = float(w) / float(h)
        if 0.7 <= aspect_ratio <= 1.3:
            # Check solidity / square approximation
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            if 4 <= len(approx) <= 6:
                fiducials.append(np.array([x + w / 2.0, y + h / 2.0], dtype=np.float32))

    if len(fiducials) == 4:
        return np.array(fiducials, dtype=np.float32)

    return None


def detect_card(
    image_bgr: np.ndarray,
    profile: dict[str, Any] | None = None,
) -> CardDetectionResult:
    """Detect reference card, decode QR metadata, and warp to canonical perspective."""
    if image_bgr is None or image_bgr.size == 0:
        return CardDetectionResult(
            detected=False,
            rejection_reason="RECAPTURE REQUIRED — Image is empty or invalid.",
        )

    active_profile = profile or load_profile()
    expected_profile_id = active_profile["profile_id"]
    min_patches_required = active_profile["calibration"].get("min_patches_required", 3)

    h, w = image_bgr.shape[:2]
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Attempt QR code detection and decoding
    qr_detector = cv2.QRCodeDetector()
    decoded_text, qr_points, _ = qr_detector.detectAndDecode(gray)

    decoded_profile_id = None
    decoded_version = None

    if decoded_text:
        try:
            qr_data = json.loads(decoded_text)
            decoded_profile_id = qr_data.get("profile_id")
            decoded_version = qr_data.get("profile_version")
            logger.info("Decoded QR metadata: %s v%s", decoded_profile_id, decoded_version)
        except Exception:
            logger.debug("QR payload was not valid JSON: %s", decoded_text)

    # 2. Locate card geometry
    warped: np.ndarray | None = None
    geometry_quality = 0.0
    detected_corners: list[list[float]] = []

    # Strategy A: 4 black corner square fiducials
    fiducial_centers = find_corner_fiducials(gray)
    if fiducial_centers is not None:
        ordered_pts = order_quad_points(fiducial_centers)
        detected_corners = ordered_pts.tolist()

        dst_pts = np.array(
            [
                [50.0, 50.0],
                [float(CANONICAL_WIDTH - 50), 50.0],
                [float(CANONICAL_WIDTH - 50), float(CANONICAL_HEIGHT - 50)],
                [50.0, float(CANONICAL_HEIGHT - 50)],
            ],
            dtype=np.float32,
        )

        transform_matrix = cv2.getPerspectiveTransform(ordered_pts, dst_pts)
        warped = cv2.warpPerspective(
            image_bgr, transform_matrix, (CANONICAL_WIDTH, CANONICAL_HEIGHT)
        )
        geometry_quality = 0.95
        logger.info("Card detected via 4 corner square fiducials.")

    # Strategy B: Card boundary rectangular contour
    if warped is None:
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_card_contour = None
        max_card_area = (w * h) * 0.25  # Card must cover at least 25% of the frame

        for c in contours:
            area = cv2.contourArea(c)
            if area > max_card_area:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.03 * peri, True)
                if len(approx) == 4 and cv2.isContourConvex(approx):
                    best_card_contour = approx
                    max_card_area = area

        if best_card_contour is not None:
            pts = best_card_contour.reshape(4, 2).astype(np.float32)
            ordered_pts = order_quad_points(pts)
            detected_corners = ordered_pts.tolist()

            dst_pts = np.array(
                [
                    [0.0, 0.0],
                    [float(CANONICAL_WIDTH), 0.0],
                    [float(CANONICAL_WIDTH), float(CANONICAL_HEIGHT)],
                    [0.0, float(CANONICAL_HEIGHT)],
                ],
                dtype=np.float32,
            )

            transform_matrix = cv2.getPerspectiveTransform(ordered_pts, dst_pts)
            warped = cv2.warpPerspective(
                image_bgr, transform_matrix, (CANONICAL_WIDTH, CANONICAL_HEIGHT)
            )
            geometry_quality = 0.85
            logger.info("Card detected via outer boundary contour.")

    # Strategy C: Full-frame card image (direct capture of the card)
    if warped is None:
        aspect_ratio = float(w) / float(h)
        expected_ratio = float(CANONICAL_WIDTH) / float(CANONICAL_HEIGHT)
        if abs(aspect_ratio - expected_ratio) < 0.35 and w >= 600 and h >= 400:
            warped = cv2.resize(image_bgr, (CANONICAL_WIDTH, CANONICAL_HEIGHT))
            geometry_quality = 0.80
            detected_corners = [[0, 0], [w, 0], [w, h], [0, h]]
            logger.info("Card detected as full-frame image.")

    if warped is None:
        return CardDetectionResult(
            detected=False,
            geometry_quality=0.0,
            confidence=0.0,
            rejection_reason="RECAPTURE REQUIRED — Reference card not detected.",
        )

    # 3. Verify reference patches within canonical warped image
    valid_patches_count = 0
    canonical_patches = active_profile["canonical_reference_patches"]

    for name, box in CANONICAL_PATCH_BOXES.items():
        if name not in canonical_patches:
            continue
        bx, by, bw, bh = box
        # Sample center 40x40 of the patch to avoid borders
        margin = 15
        patch_roi = warped[by + margin : by + bh - margin, bx + margin : bx + bw - margin]
        if patch_roi.size > 0:
            spatial_std = float(np.std(patch_roi, axis=(0, 1)).mean())
            # A valid patch region is spatially uniform (not occluded by noise/text)
            if spatial_std < 25.0:
                valid_patches_count += 1

    if valid_patches_count < min_patches_required:
        return CardDetectionResult(
            detected=False,
            geometry_quality=geometry_quality,
            reference_patch_count=valid_patches_count,
            confidence=0.2,
            rejection_reason=(
                f"RECAPTURE REQUIRED — Insufficient visible reference patches "
                f"({valid_patches_count}/{len(CANONICAL_PATCH_BOXES)} found, "
                f"min {min_patches_required} required)."
            ),
        )

    # Calculate overall confidence
    confidence = round(geometry_quality * (valid_patches_count / len(CANONICAL_PATCH_BOXES)), 2)

    return CardDetectionResult(
        detected=True,
        profile_id=decoded_profile_id or expected_profile_id,
        profile_version=decoded_version or active_profile["profile_version"],
        geometry_quality=round(geometry_quality, 2),
        reference_patch_count=valid_patches_count,
        confidence=confidence,
        corners=detected_corners,
        warped_image=warped,
    )
