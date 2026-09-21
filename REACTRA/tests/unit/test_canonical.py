"""Unit tests for canonical evidence record serialization."""

from __future__ import annotations

from rectra.evidence.canonical import (
    build_canonical_record_dict,
    canonicalize_record,
)


def test_canonicalize_record_key_sorting() -> None:
    """Keys must be strictly alphabetically sorted regardless of dict insertion order."""
    dict_a = {"z": 1, "a": 2, "m": 3}
    dict_b = {"a": 2, "m": 3, "z": 1}

    bytes_a = canonicalize_record(dict_a)
    bytes_b = canonicalize_record(dict_b)

    assert bytes_a == bytes_b
    assert bytes_a == b'{"a":2,"m":3,"z":1}'


def test_canonicalize_record_nested_structures() -> None:
    """Nested dictionaries and lists must also have their keys deterministically sorted."""
    nested_1 = {"outer": {"b": 2, "a": 1}, "list": [{"y": 2, "x": 1}]}
    nested_2 = {"list": [{"x": 1, "y": 2}], "outer": {"a": 1, "b": 2}}

    assert canonicalize_record(nested_1) == canonicalize_record(nested_2)
    assert canonicalize_record(nested_1) == b'{"list":[{"x":1,"y":2}],"outer":{"a":1,"b":2}}'


def test_build_canonical_record_dict_structure() -> None:
    """Canonical record dict builder must populate all required fields."""
    rec = build_canonical_record_dict(
        test_id="test-canon-01",
        operator_id="OP-01",
        capture_mode="LIVE_CAMERA",
        timestamp_utc="2026-09-20T12:00:00Z",
        latitude=28.6139,
        longitude=77.2090,
        gps_status="MANUAL_DEMO",
        profile_id="DEMO-ASSAY-001",
        profile_version="1.0",
        reference_card_version="1.0",
        algorithm_version="1.0",
        model_version="1.0",
        result="POSITIVE",
        classification_score=0.98765,
        measurement_quality="HIGH",
        quality_gate_status="VALID",
        image_sha256="a" * 64,
        previous_record_hash=None,
    )

    assert rec["test_id"] == "test-canon-01"
    assert rec["classification_score"] == 0.9877
    assert rec["evidence_format_version"] == "1.0"
