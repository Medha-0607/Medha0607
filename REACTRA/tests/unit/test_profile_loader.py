"""Unit tests for assay profile discovery, loading, and validation."""

from __future__ import annotations

import pytest

from rectra.core.exceptions import ProfileError
from rectra.profiles.loader import list_available_profiles, load_profile, validate_profile


def test_list_available_profiles_discovers_profiles() -> None:
    """list_available_profiles must discover all installed assay profiles."""
    profiles = list_available_profiles()
    ids = [p["profile_id"] for p in profiles]

    assert "DEMO-ASSAY-001" in ids
    assert "MARQUIS-001" in ids
    assert "SCOTT-001" in ids


def test_demo_profile_calibrated() -> None:
    """DEMO-ASSAY-001 must be calibrated with non-null centroid dictionary."""
    prof = load_profile("DEMO-ASSAY-001", "1.0")
    assert prof["profile_id"] == "DEMO-ASSAY-001"
    assert prof.get("is_calibrated", True) is True
    assert isinstance(prof["class_centroids_lab"], dict)
    assert "POSITIVE" in prof["class_centroids_lab"]
    assert "NEGATIVE" in prof["class_centroids_lab"]


def test_staged_marquis_profile_uncalibrated() -> None:
    """MARQUIS-001 must be staged with null centroids and documentation note."""
    prof = load_profile("MARQUIS-001", "1.0")
    assert prof["profile_id"] == "MARQUIS-001"
    assert prof.get("is_calibrated") is False
    expected_note = "Real-world colorimetric calibration required before use. Not validated."
    assert expected_note in prof["documentation_note"]


def test_staged_scott_profile_uncalibrated() -> None:
    """SCOTT-001 must be staged with null centroids and documentation note."""
    prof = load_profile("SCOTT-001", "1.0")
    assert prof["profile_id"] == "SCOTT-001"
    assert prof.get("is_calibrated") is False
    assert prof["class_centroids_lab"] is None
    assert "documentation_note" in prof
    expected_note = "Real-world colorimetric calibration required before use. Not validated."
    assert expected_note in prof["documentation_note"]



def test_validate_profile_rejects_missing_centroids_when_calibrated() -> None:
    """A profile claiming calibration without a centroid dictionary must be rejected."""
    malformed = {
        "profile_id": "FAKE-001",
        "profile_version": "1.0",
        "outcome_classes": ["POSITIVE", "NEGATIVE", "INCONCLUSIVE"],
        "canonical_reference_patches": {},
        "class_centroids_lab": None,  # null centroids while calibrated!
        "is_calibrated": True,
        "calibration": {},
        "quality_thresholds": {},
        "classifier": {},
        "algorithm_version": "reactra-algo-v0.1",
        "model_version": "reactra-model-v0.1",
    }
    with pytest.raises(ProfileError, match="must define a valid 'class_centroids_lab' dictionary"):
        validate_profile(malformed)
