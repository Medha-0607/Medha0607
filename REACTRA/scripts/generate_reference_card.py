"""Generate the RECTRA synthetic reference card with corner square fiducials.

Embeds 4 solid black corner squares for OpenCV contour detection, an embedded QR code
encoding assay profile metadata, 6 canonical colour reference patches, and a designated
test reaction zone.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import cv2
import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont

from rectra.config import DEFAULT_PROFILE_PATH, REFERENCE_CARD_PATH
from rectra.core.logging_config import configure_logging

logger = logging.getLogger(__name__)


def lab_to_bgr(L: float, a: float, b: float) -> tuple[int, int, int]:
    """Convert a single CIE Lab coordinate into 8-bit BGR values."""
    cv_l = np.clip(L * 255.0 / 100.0, 0, 255)
    cv_a = np.clip(a + 128.0, 0, 255)
    cv_b = np.clip(b + 128.0, 0, 255)
    lab_pixel = np.uint8([[[cv_l, cv_a, cv_b]]])
    bgr_pixel = cv2.cvtColor(lab_pixel, cv2.COLOR_LAB2BGR)
    b, g, r = bgr_pixel[0, 0]
    return int(b), int(g), int(r)


def generate_card(output_path: Path | None = None) -> Path:
    """Generate reference card image and write to disk."""
    dest = output_path or REFERENCE_CARD_PATH
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Load canonical profile
    with open(DEFAULT_PROFILE_PATH, "r", encoding="utf-8") as f:
        profile_data = json.load(f)

    profile_id = profile_data["profile_id"]
    profile_version = profile_data["profile_version"]
    card_version = profile_data.get("reference_card_version", "1.0")
    patches = profile_data["canonical_reference_patches"]

    # Dimensions
    width, height = 1000, 700
    card = np.ones((height, width, 3), dtype=np.uint8) * 215  # Off-white matte paper background

    # Outer border
    cv2.rectangle(card, (10, 10), (width - 10, height - 10), (170, 170, 170), 2)

    # 1. Four corner black square fiducials (50x50 px, 25px margin)
    fiducial_size = 50
    margin = 25
    corners = [
        (margin, margin),
        (width - margin - fiducial_size, margin),
        (margin, height - margin - fiducial_size),
        (width - margin - fiducial_size, height - margin - fiducial_size),
    ]
    for x, y in corners:
        cv2.rectangle(card, (x, y), (x + fiducial_size, y + fiducial_size), (0, 0, 0), -1)

    # Convert to PIL for typography
    pil_img = Image.fromarray(cv2.cvtColor(card, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

    # 2. Header & Title
    draw.text((100, 35), "RECTRA CALIBRATION REFERENCE CARD", fill=(20, 20, 20), font=font_large)
    info_text = f"Profile: {profile_id} | Version: {profile_version} | Card: v{card_version}"
    draw.text((100, 60), info_text, fill=(80, 80, 80), font=font_small)
    sub_text = "Place card flat under ambient lighting. Ensure full card is visible."
    draw.text((100, 75), sub_text, fill=(110, 110, 110), font=font_small)

    card = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # 3. QR Code with profile metadata
    qr_payload = json.dumps(
        {
            "profile_id": profile_id,
            "profile_version": profile_version,
            "reference_card_version": card_version,
        }
    )
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(qr_payload)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_cv = cv2.cvtColor(np.array(qr_img), cv2.COLOR_RGB2BGR)
    qr_h, qr_w = qr_cv.shape[:2]
    card[30 : 30 + qr_h, 760 : 760 + qr_w] = qr_cv
    cv2.putText(card, "PROFILE QR", (760, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (80, 80, 80), 1)

    # 4. Canonical 6 Colour Patches (White, Black, Red, Green, Blue, Grey)
    patch_size = 70
    patch_start_x = 100
    patch_start_y = 130
    patch_names = ["white", "black", "red", "green", "blue", "grey"]

    for idx, name in enumerate(patch_names):
        lab = patches[name]
        bgr = lab_to_bgr(lab["L"], lab["a"], lab["b"])
        px = patch_start_x + idx * 140
        py = patch_start_y

        cv2.rectangle(card, (px, py), (px + patch_size, py + patch_size), bgr, -1)
        cv2.rectangle(card, (px, py), (px + patch_size, py + patch_size), (120, 120, 120), 1)
        cv2.putText(
            card,
            name.upper(),
            (px, py + patch_size + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (40, 40, 40),
            1,
        )
        cv2.putText(
            card,
            f"L:{lab['L']:.0f}",
            (px, py + patch_size + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (100, 100, 100),
            1,
        )

    # 5. Designated Reaction / Test Zone
    rx, ry, rw, rh = 250, 320, 500, 260
    cv2.rectangle(card, (rx, ry), (rx + rw, ry + rh), (235, 235, 235), -1)
    cv2.rectangle(card, (rx, ry), (rx + rw, ry + rh), (0, 102, 204), 2)
    cv2.line(
        card,
        (rx + rw // 2 - 20, ry + rh // 2),
        (rx + rw // 2 + 20, ry + rh // 2),
        (200, 200, 200),
        1,
    )
    cv2.line(
        card,
        (rx + rw // 2, ry + rh // 2 - 20),
        (rx + rw // 2, ry + rh // 2 + 20),
        (200, 200, 200),
        1,
    )
    cv2.putText(
        card, "TEST ZONE", (rx + 15, ry + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 102, 204), 2
    )
    cv2.putText(
        card,
        "Place chemical test reaction capsule/well here",
        (rx + 15, ry + 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (100, 100, 100),
        1,
    )

    # Footer notice
    footer_text = (
        "RECTRA SIH26231 SYNTHETIC PROTOTYPE REFERENCE CARD — NOT AN OFFICIAL FORENSIC ARTIFACT"
    )
    cv2.putText(card, footer_text, (100, 640), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (120, 120, 120), 1)

    cv2.imwrite(str(dest), card)
    logger.info("Reference card successfully generated at %s", dest)
    return dest


if __name__ == "__main__":
    configure_logging()
    generate_card()
