"""Unit tests for CIE Lab calibration module."""

from __future__ import annotations

import pytest

from rectra.vision.calibration import (
    calibrate_colours,
    delta_e76,
)


def test_delta_e76_identical_values() -> None:
    """Identical CIE Lab colours must have zero delta E."""
    lab = (50.0, 10.0, -20.0)
    de = delta_e76(lab, lab)
    assert pytest.approx(de, abs=1e-6) == 0.0


def test_delta_e76_known_difference() -> None:
    """Delta E76 is Euclidean distance in Lab space."""
    lab1 = (0.0, 0.0, 0.0)
    lab2 = (3.0, 4.0, 0.0)
    # sqrt(3^2 + 4^2) = 5.0
    de = delta_e76(lab1, lab2)
    assert pytest.approx(de, abs=1e-5) == 5.0


def test_calibrate_colours_exact_nominal(assay_profile) -> None:
    """Calibrating matching nominal patches against profile must yield near-zero residual."""
    canonical_dict = assay_profile["canonical_reference_patches"]
    observed = {
        name: (float(val["L"]), float(val["a"]), float(val["b"]))
        for name, val in canonical_dict.items()
    }
    raw_test_colour = (45.0, 40.0, 20.0)

    result = calibrate_colours(observed, assay_profile, raw_test_colour)

    assert result.calibration_valid is True
    assert result.residual_delta_e < assay_profile["calibration"]["max_residual_delta_e"]
    assert pytest.approx(result.corrected_test_colour_lab[0], abs=1e-1) == raw_test_colour[0]
