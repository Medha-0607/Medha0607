"""CIE Lab least-squares colour calibration for RECTRA.

Maps observed reference patch colours to canonical profile colours using an affine
least-squares transformation to correct for ambient lighting and camera sensors.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from rectra.core.exceptions import CalibrationError
from rectra.core.types import CalibrationResult

logger = logging.getLogger(__name__)


def delta_e76(lab1: tuple[float, float, float], lab2: tuple[float, float, float]) -> float:
    """Calculate Euclidean distance (CIE ΔE 1976) between two Lab colours."""
    return float(
        np.sqrt((lab1[0] - lab2[0]) ** 2 + (lab1[1] - lab2[1]) ** 2 + (lab1[2] - lab2[2]) ** 2)
    )


def calibrate_colours(
    observed_patches: dict[str, tuple[float, float, float]],
    profile: dict[str, Any],
    raw_test_colour_lab: tuple[float, float, float],
) -> CalibrationResult:
    """Compute affine colour transformation and return corrected test colour and residuals."""
    canonical_dict = profile["canonical_reference_patches"]
    calib_cfg = profile.get("calibration", {})
    max_residual = calib_cfg.get("max_residual_delta_e", 8.0)
    min_patches = calib_cfg.get("min_patches_required", 3)

    # Align matching patches
    common_names = [name for name in observed_patches if name in canonical_dict]
    if len(common_names) < min_patches:
        raise CalibrationError(
            f"Insufficient matching patches for calibration: found {len(common_names)}, "
            f"minimum {min_patches} required."
        )

    # Build design matrices: Obs * M ≈ Can
    # Obs shape: [N, 4] with bias term (L, a, b, 1.0)
    # Can shape: [N, 3] (L, a, b)
    obs_rows = []
    can_rows = []
    canonical_patch_colours: dict[str, tuple[float, float, float]] = {}

    for name in common_names:
        obs_l, obs_a, obs_b = observed_patches[name]
        obs_rows.append([obs_l, obs_a, obs_b, 1.0])

        can_data = canonical_dict[name]
        can_tuple = (float(can_data["L"]), float(can_data["a"]), float(can_data["b"]))
        canonical_patch_colours[name] = can_tuple
        can_rows.append([can_tuple[0], can_tuple[1], can_tuple[2]])

    A = np.array(obs_rows, dtype=np.float64)
    B = np.array(can_rows, dtype=np.float64)

    # Solve least squares: A @ M ≈ B -> M has shape [4, 3]
    try:
        M, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)
    except Exception as exc:
        raise CalibrationError(f"Least-squares solver failed: {exc}") from exc

    # Apply transformation to observed patches to calculate residual ΔE
    mapped_patches = A @ M
    patch_errors = []
    for i, name in enumerate(common_names):
        mapped_lab = (
            float(mapped_patches[i, 0]),
            float(mapped_patches[i, 1]),
            float(mapped_patches[i, 2]),
        )
        err = delta_e76(mapped_lab, canonical_patch_colours[name])
        patch_errors.append(err)

    mean_residual_delta_e = float(np.mean(patch_errors)) if patch_errors else 999.0
    calib_valid = bool(mean_residual_delta_e <= max_residual)

    # Apply transformation to raw test colour
    raw_vec = np.array(
        [raw_test_colour_lab[0], raw_test_colour_lab[1], raw_test_colour_lab[2], 1.0],
        dtype=np.float64,
    )
    corrected_vec = raw_vec @ M
    corrected_lab = (
        round(float(np.clip(corrected_vec[0], 0.0, 100.0)), 2),
        round(float(np.clip(corrected_vec[1], -128.0, 127.0)), 2),
        round(float(np.clip(corrected_vec[2], -128.0, 127.0)), 2),
    )

    logger.info(
        "Colour calibration: residual ΔE=%.2f (threshold=%.2f, valid=%s)",
        mean_residual_delta_e,
        max_residual,
        calib_valid,
    )

    return CalibrationResult(
        observed_patch_colours=observed_patches,
        canonical_patch_colours=canonical_patch_colours,
        calibration_matrix=M.tolist(),
        corrected_test_colour_lab=corrected_lab,
        residual_delta_e=round(mean_residual_delta_e, 2),
        calibration_valid=calib_valid,
        method="least_squares_lab",
    )
