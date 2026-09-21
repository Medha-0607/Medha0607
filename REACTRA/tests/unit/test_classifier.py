"""Unit tests for the Nearest Centroid presumptive classifier."""

from __future__ import annotations

from rectra.classification.predictor import classify_reaction
from rectra.core.constants import OutcomeClass


def test_classifier_exact_positive(assay_profile) -> None:
    """Exact positive nominal Lab centroid must return POSITIVE outcome."""
    pos_data = assay_profile["class_centroids_lab"]["POSITIVE"]
    pos_centroid = (float(pos_data["L"]), float(pos_data["a"]), float(pos_data["b"]))

    result = classify_reaction(pos_centroid, assay_profile)

    assert result.result == OutcomeClass.POSITIVE
    assert result.classification_score > 0.90


def test_classifier_exact_negative(assay_profile) -> None:
    """Exact negative nominal Lab centroid must return NEGATIVE outcome."""
    neg_data = assay_profile["class_centroids_lab"]["NEGATIVE"]
    neg_centroid = (float(neg_data["L"]), float(neg_data["a"]), float(neg_data["b"]))

    result = classify_reaction(neg_centroid, assay_profile)

    assert result.result == OutcomeClass.NEGATIVE
    assert result.classification_score > 0.90


def test_classifier_ambiguous_inconclusive(assay_profile) -> None:
    """A midpoint colour with distance difference under margin must return INCONCLUSIVE."""
    pos_data = assay_profile["class_centroids_lab"]["POSITIVE"]
    neg_data = assay_profile["class_centroids_lab"]["NEGATIVE"]

    midpoint = (
        (float(pos_data["L"]) + float(neg_data["L"])) / 2.0,
        (float(pos_data["a"]) + float(neg_data["a"])) / 2.0,
        (float(pos_data["b"]) + float(neg_data["b"])) / 2.0,
    )

    result = classify_reaction(midpoint, assay_profile)

    assert result.result == OutcomeClass.INCONCLUSIVE
