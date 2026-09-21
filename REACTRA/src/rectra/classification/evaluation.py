"""Evaluation metrics computation for the RECTRA colorimetric classifier."""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from rectra.config import BASE_DIR, DATA_DIR, RUNTIME_DIR
from rectra.core.constants import OutcomeClass
from rectra.profiles.loader import load_profile

logger = logging.getLogger(__name__)

EVALUATION_RESULTS_PATH: Path = RUNTIME_DIR / "evaluation_results.json"


def evaluate_dataset(
    ground_truth_path: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Run classifier evaluation across ground truth samples and compute metrics."""
    from rectra.classification.predictor import classify_reaction
    from rectra.vision.calibration import calibrate_colours
    from rectra.vision.card_detector import detect_card
    from rectra.vision.roi_detector import extract_test_roi

    gt_file = ground_truth_path or DATA_DIR / "demo" / "ground_truth.json"
    dest = output_path or EVALUATION_RESULTS_PATH
    dest.parent.mkdir(parents=True, exist_ok=True)

    if not gt_file.exists():
        raise FileNotFoundError(f"Ground truth dataset not found at {gt_file}")

    with open(gt_file, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    profile = load_profile()
    classes = [
        OutcomeClass.POSITIVE.value,
        OutcomeClass.NEGATIVE.value,
        OutcomeClass.INCONCLUSIVE.value,
    ]
    class_to_idx = {cls: idx for idx, cls in enumerate(classes)}

    y_true: list[str] = []
    y_pred: list[str] = []

    samples = gt_data.get("samples", [])
    for sample in samples:
        # Only evaluate standard samples (skip intentional optical error edge cases)
        if sample.get("scenario_type") != "standard":
            continue

        rel_path = sample["image_path"]
        img_full_path = BASE_DIR / Path(rel_path)
        if not img_full_path.exists():
            continue

        img = cv2.imread(str(img_full_path))
        if img is None:
            continue

        card_res = detect_card(img, profile)
        if not card_res.detected or card_res.warped_image is None:
            continue

        roi_res = extract_test_roi(card_res.warped_image, profile)
        if not roi_res.is_valid:
            continue

        # Extract reference patches from warped card
        from rectra.vision.card_detector import CANONICAL_PATCH_BOXES, bgr_to_lab

        observed: dict[str, tuple[float, float, float]] = {}
        for name, box in CANONICAL_PATCH_BOXES.items():
            bx, by, bw, bh = box
            patch_crop = card_res.warped_image[by + 15 : by + bh - 15, bx + 15 : bx + bw - 15]
            mb = float(np.mean(patch_crop[:, :, 0]))
            mg = float(np.mean(patch_crop[:, :, 1]))
            mr = float(np.mean(patch_crop[:, :, 2]))
            observed[name] = bgr_to_lab((mb, mg, mr))

        calib_res = calibrate_colours(observed, profile, roi_res.mean_lab)
        class_res = classify_reaction(calib_res.corrected_test_colour_lab, profile)

        y_true.append(sample["class"])
        res_str = (
            class_res.result.value if hasattr(class_res.result, "value") else str(class_res.result)
        )
        y_pred.append(res_str)

    # Compute 3x3 confusion matrix: rows=true, cols=predicted
    cm = np.zeros((3, 3), dtype=int)
    for t, p in zip(y_true, y_pred, strict=False):
        if t in class_to_idx and p in class_to_idx:
            cm[class_to_idx[t], class_to_idx[p]] += 1

    # Per-class precision, recall, f1
    precision: dict[str, float] = {}
    recall: dict[str, float] = {}
    f1_scores: dict[str, float] = {}

    for cls, idx in class_to_idx.items():
        tp = cm[idx, idx]
        fp = np.sum(cm[:, idx]) - tp
        fn = np.sum(cm[idx, :]) - tp

        prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        precision[cls] = round(prec, 4)
        recall[cls] = round(rec, 4)
        f1_scores[cls] = round(f1, 4)

    macro_f1 = round(float(np.mean(list(f1_scores.values()))), 4)

    evaluation_report = {
        "dataset_version": gt_data.get("dataset_version", "synthetic-v1"),
        "seed": gt_data.get("random_seed", 42),
        "total_evaluated_samples": len(y_true),
        "model_version": profile.get("model_version", "rectra-model-v0.1"),
        "algorithm_version": profile.get("algorithm_version", "rectra-algo-v0.1"),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "classes": classes,
        "confusion_matrix": cm.tolist(),
        "precision": precision,
        "recall": recall,
        "f1": f1_scores,
        "macro_f1": macro_f1,
    }

    with open(dest, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, indent=2)

    logger.info("Evaluation complete: macro F1=%.4f saved to %s", macro_f1, dest)
    return evaluation_report


def load_evaluation_results() -> dict[str, Any] | None:
    """Load cached evaluation metrics, or return None if evaluation has not run yet."""
    if not EVALUATION_RESULTS_PATH.exists():
        return None
    try:
        with open(EVALUATION_RESULTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Failed to load evaluation results: %s", exc)
        return None
