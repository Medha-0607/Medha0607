"""Generate deterministic synthetic colorimetric test images and ground truth metadata.

Applies controlled optical variations (lighting shift, noise, blur, perspective, glare)
to synthetic reference card captures for POSITIVE, NEGATIVE, INCONCLUSIVE, and edge cases.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import cv2
import numpy as np

from rectra.config import DATA_DIR, DEFAULT_PROFILE_PATH, REFERENCE_CARD_PATH
from rectra.core.logging_config import configure_logging

try:
    from scripts.generate_reference_card import generate_card, lab_to_bgr
except ImportError:
    from generate_reference_card import generate_card, lab_to_bgr

logger = logging.getLogger(__name__)


def add_reaction_spot(
    base_card: np.ndarray,
    target_lab: dict[str, float],
    rng: np.random.Generator,
    variation_lab: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> np.ndarray:
    """Draw a circular reagent reaction spot inside the TEST ZONE."""
    card = base_card.copy()
    cx = 250 + 250 + int(rng.integers(-15, 15))
    cy = 320 + 130 + int(rng.integers(-15, 15))
    radius = int(rng.integers(55, 75))

    target_l = np.clip(target_lab["L"] + variation_lab[0], 0, 100)
    target_a = np.clip(target_lab["a"] + variation_lab[1], -128, 127)
    target_b = np.clip(target_lab["b"] + variation_lab[2], -128, 127)

    spot_bgr = lab_to_bgr(target_l, target_a, target_b)

    mask = np.zeros(card.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (cx, cy), radius, 255, -1)
    mask = cv2.GaussianBlur(mask, (21, 21), 0)

    spot_img = np.full_like(card, spot_bgr, dtype=np.uint8)
    alpha = (mask.astype(float) / 255.0)[:, :, np.newaxis]
    card = (alpha * spot_img + (1.0 - alpha) * card).astype(np.uint8)
    return card


def apply_optical_variations(
    img: np.ndarray,
    rng: np.random.Generator,
    brightness_shift: float = 0.0,
    noise_sigma: float = 0.0,
    blur_ksize: int = 0,
    rotation_deg: float = 0.0,
    add_glare: bool = False,
    overexpose: bool = False,
) -> np.ndarray:
    """Apply realistic environmental and camera variations to the card image."""
    result = img.astype(np.float32)

    if overexpose:
        result = np.clip(result + 120.0, 0, 255)
    elif brightness_shift != 0.0:
        result = np.clip(result + brightness_shift, 0, 255)

    if noise_sigma > 0:
        noise = rng.normal(0, noise_sigma, result.shape).astype(np.float32)
        result = np.clip(result + noise, 0, 255)

    result = result.astype(np.uint8)

    if blur_ksize > 1:
        if blur_ksize % 2 == 0:
            blur_ksize += 1
        result = cv2.GaussianBlur(result, (blur_ksize, blur_ksize), 0)

    if add_glare:
        gx = int(rng.integers(200, 700))
        gy = int(rng.integers(200, 500))
        cv2.circle(result, (gx, gy), 60, (255, 255, 255), -1)

    if abs(rotation_deg) > 0.1:
        h, w = result.shape[:2]
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, rotation_deg, 0.98)
        result = cv2.warpAffine(result, rot_mat, (w, h), borderValue=(220, 220, 220))

    return result


def generate_dataset(
    output_dir: Path | None = None,
    seed: int = 42,
    samples_per_class: int = 5,
) -> Path:
    """Generate deterministic synthetic demo dataset with ground truth metadata."""
    base_dir = output_dir or DATA_DIR / "demo"
    base_dir.mkdir(parents=True, exist_ok=True)

    if not REFERENCE_CARD_PATH.exists():
        generate_card(REFERENCE_CARD_PATH)

    base_card = cv2.imread(str(REFERENCE_CARD_PATH))
    if base_card is None:
        raise RuntimeError(f"Could not load reference card at {REFERENCE_CARD_PATH}")

    with open(DEFAULT_PROFILE_PATH, "r", encoding="utf-8") as f:
        profile = json.load(f)

    centroids = profile["class_centroids_lab"]
    rng = np.random.default_rng(seed)

    ground_truth: dict[str, object] = {
        "data_note": "Synthetic demonstration data. Not real drug test imagery.",
        "dataset_version": "synthetic-v1",
        "random_seed": seed,
        "profile_id": profile["profile_id"],
        "samples": [],
    }

    classes = ["POSITIVE", "NEGATIVE", "INCONCLUSIVE"]

    for cls in classes:
        cls_dir = base_dir / cls.lower()
        cls_dir.mkdir(parents=True, exist_ok=True)
        centroid = centroids[cls]

        for i in range(1, samples_per_class + 1):
            sample_id = f"DEMO-{cls[:3]}-{i:03d}"
            img_filename = f"{sample_id}.png"
            img_path = cls_dir / img_filename

            b_shift = float(rng.uniform(-15, 15))
            n_sigma = float(rng.uniform(1.0, 4.0))
            rot = float(rng.uniform(-2.5, 2.5))
            var_l = float(rng.uniform(-2.0, 2.0))
            var_a = float(rng.uniform(-2.0, 2.0))
            var_b = float(rng.uniform(-2.0, 2.0))

            spotted = add_reaction_spot(
                base_card, centroid, rng, variation_lab=(var_l, var_a, var_b)
            )

            final_img = apply_optical_variations(
                spotted,
                rng,
                brightness_shift=b_shift,
                noise_sigma=n_sigma,
                blur_ksize=0,
                rotation_deg=rot,
            )

            cv2.imwrite(str(img_path), final_img)

            rel_path = f"data/demo/{cls.lower()}/{img_filename}"
            samples_list: list[dict[str, object]] = ground_truth["samples"]  # type: ignore[assignment]
            samples_list.append(
                {
                    "sample_id": sample_id,
                    "class": cls,
                    "seed": seed,
                    "generation_params": {
                        "brightness_shift": round(b_shift, 2),
                        "noise_sigma": round(n_sigma, 2),
                        "rotation_deg": round(rot, 2),
                    },
                    "image_path": rel_path,
                    "scenario_type": "standard",
                }
            )

    # Edge cases
    edge_dir = base_dir / "edge_cases"
    edge_dir.mkdir(parents=True, exist_ok=True)

    spotted_pos = add_reaction_spot(base_card, centroids["POSITIVE"], rng)
    blurred_img = apply_optical_variations(spotted_pos, rng, blur_ksize=25)
    blurred_path = edge_dir / "DEMO-EDGE-BLURRED.png"
    cv2.imwrite(str(blurred_path), blurred_img)

    samples_list = ground_truth["samples"]  # type: ignore[assignment]
    samples_list.append(
        {
            "sample_id": "DEMO-EDGE-BLURRED",
            "class": "POSITIVE",
            "seed": seed,
            "generation_params": {"blur_ksize": 25},
            "image_path": "data/demo/edge_cases/DEMO-EDGE-BLURRED.png",
            "scenario_type": "blurred_quality_fail",
        }
    )

    overexposed_img = apply_optical_variations(spotted_pos, rng, overexpose=True, add_glare=True)
    overexp_path = edge_dir / "DEMO-EDGE-OVEREXPOSED.png"
    cv2.imwrite(str(overexp_path), overexposed_img)

    samples_list.append(
        {
            "sample_id": "DEMO-EDGE-OVEREXPOSED",
            "class": "POSITIVE",
            "seed": seed,
            "generation_params": {"overexpose": True, "add_glare": True},
            "image_path": "data/demo/edge_cases/DEMO-EDGE-OVEREXPOSED.png",
            "scenario_type": "overexposed_glare_fail",
        }
    )

    gt_path = base_dir / "ground_truth.json"
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)

    total_samples = len(samples_list)
    logger.info("Generated %d synthetic samples at %s", total_samples, base_dir)
    logger.info("Ground truth metadata written to %s", gt_path)
    return gt_path


if __name__ == "__main__":
    configure_logging()
    parser = argparse.ArgumentParser(description="Generate synthetic RECTRA demo dataset")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory path")
    args = parser.parse_args()

    out = Path(args.output_dir) if args.output_dir else None
    generate_dataset(output_dir=out, seed=args.seed)
