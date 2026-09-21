"""Generate a print-ready A4 PDF containing the RECTRA reference card with scale rulers.

Renders physical cutting marks, millimeter calibration bar, and printing instructions
at 300 DPI for high-precision physical deployment.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from rectra.config import ASSETS_DIR, REFERENCE_CARD_PATH
from rectra.core.logging_config import configure_logging

logger = logging.getLogger(__name__)

PDF_OUTPUT_PATH = ASSETS_DIR / "reference_cards" / "RECTRA_PRINTABLE_REFERENCE_CARD.pdf"


def generate_printable_card_pdf(output_path: Path | None = None) -> Path:
    """Generate a print-ready 300 DPI A4 PDF with reference card and calibration rulers."""
    dest = output_path or PDF_OUTPUT_PATH
    dest.parent.mkdir(parents=True, exist_ok=True)

    # 1. Ensure the base reference card exists
    if not REFERENCE_CARD_PATH.exists():
        from scripts.generate_reference_card import generate_card

        generate_card(REFERENCE_CARD_PATH)

    card_img = Image.open(REFERENCE_CARD_PATH).convert("RGB")

    # A4 dimensions at 300 DPI: 2480 x 3508 pixels
    a4_w, a4_h = 2480, 3508
    page = Image.new("RGB", (a4_w, a4_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(page)

    # Header title
    try:
        font_large = ImageFont.truetype("arial.ttf", 44)
        font_med = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text(
        (160, 160),
        "RECTRA — Physical Field Reference Card (Printable Sheet)",
        fill=(10, 30, 60),
        font=font_large,
    )
    draw.text(
        (160, 220),
        "Calibrated Field-Test Intelligence & Presumptive Evidence System (SIH26231)",
        fill=(80, 90, 100),
        font=font_med,
    )
    draw.line([(160, 270), (a4_w - 160, 270)], fill=(200, 200, 200), width=3)

    # Place the reference card scaled to 2x for crisp 300 DPI printing (2000 x 1400)
    card_print_w = 2000
    card_print_h = int(card_img.height * (card_print_w / card_img.width))
    card_resized = card_img.resize((card_print_w, card_print_h), Image.Resampling.LANCZOS)

    card_x = (a4_w - card_print_w) // 2
    card_y = 360
    page.paste(card_resized, (card_x, card_y))

    # Draw corner cut marks around card
    cut_len = 50
    cut_color = (120, 120, 120)

    # Top-Left cut marks
    draw.line([(card_x - 15, card_y), (card_x - 15 - cut_len, card_y)], fill=cut_color, width=2)
    draw.line([(card_x, card_y - 15), (card_x, card_y - 15 - cut_len)], fill=cut_color, width=2)

    # Top-Right cut marks
    rx = card_x + card_print_w
    draw.line([(rx + 15, card_y), (rx + 15 + cut_len, card_y)], fill=cut_color, width=2)
    draw.line([(rx, card_y - 15), (rx, card_y - 15 - cut_len)], fill=cut_color, width=2)

    # Bottom-Left cut marks
    by = card_y + card_print_h
    draw.line([(card_x - 15, by), (card_x - 15 - cut_len, by)], fill=cut_color, width=2)
    draw.line([(card_x, by + 15), (card_x, by + 15 + cut_len)], fill=cut_color, width=2)

    # Bottom-Right cut marks
    draw.line([(rx + 15, by), (rx + 15 + cut_len, by)], fill=cut_color, width=2)
    draw.line([(rx, by + 15), (rx, by + 15 + cut_len)], fill=cut_color, width=2)

    # Physical scale validation bar: 100mm at 300 DPI is approx 1181 pixels (11.811 px/mm)
    # 50mm bar = 591 pixels
    ruler_y = by + 90
    bar_50mm_px = int(50.0 * 300.0 / 25.4)  # 590.55 -> 591 px
    ruler_x = (a4_w - bar_50mm_px) // 2

    draw.rectangle(
        [(ruler_x, ruler_y), (ruler_x + bar_50mm_px, ruler_y + 24)],
        fill=(20, 20, 20),
    )
    draw.text(
        (ruler_x, ruler_y - 35),
        "PHYSICAL SCALE VERIFICATION BAR: EXACTLY 50.0 MILLIMETERS",
        fill=(40, 40, 40),
        font=font_small,
    )
    draw.text(
        (ruler_x, ruler_y + 35),
        "0 mm",
        fill=(60, 60, 60),
        font=font_small,
    )
    draw.text(
        (ruler_x + bar_50mm_px - 60, ruler_y + 35),
        "50 mm",
        fill=(60, 60, 60),
        font=font_small,
    )

    # Printing instructions box
    box_y = ruler_y + 110
    box_w = a4_w - 320
    draw.rounded_rectangle(
        [(160, box_y), (160 + box_w, box_y + 400)],
        radius=16,
        fill=(248, 250, 252),
        outline=(210, 220, 230),
        width=2,
    )

    instructions = [
        "IMPORTANT FIELD PRINTING & USAGE INSTRUCTIONS:",
        "1. Print Scale: Print this sheet at 100% / Actual Size. Do NOT scale to fit.",
        "2. Scale Check: Measure the black bar above with a physical ruler. Must equal 50 mm.",
        "3. Paper Stock: Print on heavy, non-reflective matte card stock or matte photo paper.",
        "4. ANTI-GLARE NOTICE: DO NOT laminate with glossy plastic. Glossy lamination produces",
        "   severe specular reflections that trigger RECAPTURE REQUIRED on the quality gate.",
        "5. Reagent Placement: Position the reaction ampoule strictly within the central",
        "   'TEST REACTION ZONE' without obscuring corner black fiducials or color patches.",
    ]

    curr_y = box_y + 30
    for idx, line in enumerate(instructions):
        color = (180, 20, 20) if idx == 0 else (40, 50, 60)
        curr_font = font_med if idx == 0 else font_small
        draw.text((190, curr_y), line, fill=color, font=curr_font)
        curr_y += 48

    # Save as high-resolution PDF
    page.save(str(dest), "PDF", resolution=300.0)
    logger.info("Generated print-ready PDF reference card at %s", dest)
    return dest


if __name__ == "__main__":
    configure_logging()
    out = generate_printable_card_pdf()
    print(f"Generated printable PDF at: {out}")
