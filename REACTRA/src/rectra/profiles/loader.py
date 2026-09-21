"""Assay profile loader and validator for RECTRA."""

from __future__ import annotations

import json
from typing import Any

from rectra.config import DEFAULT_PROFILE_PATH, get_profile_path
from rectra.core.exceptions import ProfileError


def load_profile(profile_id: str | None = None, version: str | None = None) -> dict[str, Any]:
    """Load an assay profile by ID and version, or the default profile."""
    if profile_id and version:
        profile_path = get_profile_path(profile_id, version)
    else:
        profile_path = DEFAULT_PROFILE_PATH

    if not profile_path.exists():
        raise ProfileError(
            f"Assay profile not found at {profile_path}. "
            f"Verify profile files in profiles/ or check configuration."
        )

    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        raise ProfileError(f"Failed to parse assay profile at {profile_path}: {exc}") from exc

    validate_profile(data)
    return data


def validate_profile(data: dict[str, Any]) -> None:
    """Validate that required fields exist in the assay profile."""
    required_keys = [
        "profile_id",
        "profile_version",
        "outcome_classes",
        "canonical_reference_patches",
        "class_centroids_lab",
        "calibration",
        "quality_thresholds",
        "classifier",
        "algorithm_version",
        "model_version",
    ]
    for key in required_keys:
        if key not in data:
            raise ProfileError(f"Malformed assay profile: missing required field '{key}'")

    is_calibrated = data.get("is_calibrated", True)
    if is_calibrated:
        if not isinstance(data.get("class_centroids_lab"), dict):
            raise ProfileError(
                f"Calibrated profile '{data.get('profile_id')}' must define "
                f"a valid 'class_centroids_lab' dictionary."
            )
    else:
        if "documentation_note" not in data or not data["documentation_note"]:
            raise ProfileError(
                f"Staged uncalibrated profile '{data.get('profile_id')}' must define "
                f"a non-empty 'documentation_note'."
            )


def list_available_profiles() -> list[dict[str, Any]]:
    """Enumerate all available assay profiles in the profiles directory."""
    from rectra.config import PROFILES_DIR

    profiles: list[dict[str, Any]] = []
    if not PROFILES_DIR.exists():
        return profiles

    for profile_dir in sorted(PROFILES_DIR.iterdir()):
        if profile_dir.is_dir():
            for json_file in sorted(profile_dir.glob("*.json")):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    validate_profile(data)
                    profiles.append(data)
                except Exception:
                    continue
    return profiles
