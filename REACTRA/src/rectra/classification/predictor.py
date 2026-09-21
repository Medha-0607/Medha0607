"""Nearest Centroid presumptive classifier with inconclusive margin boundary check."""

from __future__ import annotations

import logging
from typing import Any

from rectra.core.constants import OutcomeClass
from rectra.core.types import ClassificationResult
from rectra.vision.calibration import delta_e76

logger = logging.getLogger(__name__)


def classify_reaction(
    corrected_lab: tuple[float, float, float],
    profile: dict[str, Any],
) -> ClassificationResult:
    """Classify calibrated test colour using Nearest Centroid in CIE Lab space.

    Enforces the inconclusive_delta_e_margin threshold: if the top two candidate
    classes have centroid distances closer than this margin, returns INCONCLUSIVE.
    """
    centroids = profile.get("class_centroids_lab", {})
    classifier_cfg = profile.get("classifier", {})
    inconclusive_margin = float(classifier_cfg.get("inconclusive_delta_e_margin", 12.0))
    algo_version = profile.get("algorithm_version", "rectra-algo-v0.1")
    model_version = profile.get("model_version", "rectra-model-v0.1")

    # Compute ΔE76 to each configured class centroid
    distances: dict[str, float] = {}
    for cls_name, cent in centroids.items():
        cent_tuple = (float(cent["L"]), float(cent["a"]), float(cent["b"]))
        dist = delta_e76(corrected_lab, cent_tuple)
        distances[cls_name] = round(dist, 2)

    # Sort classes by distance ascending
    sorted_classes = sorted(distances.items(), key=lambda item: item[1])

    if not sorted_classes:
        return ClassificationResult(
            result=OutcomeClass.INCONCLUSIVE,
            class_scores={},
            classification_score=0.0,
            model_version=model_version,
            algorithm_version=algo_version,
            note="Prototype classification score — not laboratory certainty.",
        )

    best_class, best_dist = sorted_classes[0]

    # Check inconclusive boundary
    if len(sorted_classes) > 1:
        second_class, second_dist = sorted_classes[1]
        dist_difference = second_dist - best_dist

        if dist_difference < inconclusive_margin:
            logger.info(
                "Classification boundary ambiguous: Δ(%s, %s)=%.2f < margin %.2f -> INCONCLUSIVE",
                best_class,
                second_class,
                dist_difference,
                inconclusive_margin,
            )
            conf = round(max(0.0, 1.0 - (dist_difference / inconclusive_margin)), 2)
            return ClassificationResult(
                result=OutcomeClass.INCONCLUSIVE,
                class_scores=distances,
                classification_score=conf,
                model_version=model_version,
                algorithm_version=algo_version,
                note="Prototype classification score — not laboratory certainty.",
            )

    # Normalized confidence score proxy based on distance to centroid
    conf_score = round(max(0.0, min(1.0, 1.0 - (best_dist / 60.0))), 2)

    logger.info(
        "Presumptive classification: %s (dist=%.2f, score=%.2f)",
        best_class,
        best_dist,
        conf_score,
    )

    return ClassificationResult(
        result=OutcomeClass(best_class),
        class_scores=distances,
        classification_score=conf_score,
        model_version=model_version,
        algorithm_version=algo_version,
        note="Prototype classification score — not laboratory certainty.",
    )
