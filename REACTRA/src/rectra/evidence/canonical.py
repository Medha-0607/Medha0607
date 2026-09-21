"""Deterministic canonical serialization for RECTRA evidence records."""

from __future__ import annotations

import json
from typing import Any

from rectra.core.constants import CANONICAL_ALGORITHM, EVIDENCE_FORMAT_VERSION


def canonicalize_record(record: dict[str, Any]) -> bytes:
    """Serialize a dictionary using canonical JSON format (json-sort-keys-compact-utf8-v1).

    Ensures consistent hash generation regardless of key insertion order or formatting.
    """
    return json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def build_canonical_record_dict(
    test_id: str,
    operator_id: str,
    capture_mode: str,
    timestamp_utc: str,
    latitude: float | None,
    longitude: float | None,
    gps_status: str,
    profile_id: str,
    profile_version: str,
    reference_card_version: str,
    algorithm_version: str,
    model_version: str,
    result: str,
    classification_score: float,
    measurement_quality: str,
    quality_gate_status: str,
    image_sha256: str,
    previous_record_hash: str | None = None,
) -> dict[str, Any]:
    """Construct the standardized dictionary representing the canonical record before signing."""
    return {
        "evidence_format_version": EVIDENCE_FORMAT_VERSION,
        "test_id": test_id,
        "operator_id": operator_id,
        "capture_mode": capture_mode,
        "timestamp_utc": timestamp_utc,
        "latitude": latitude,
        "longitude": longitude,
        "gps_status": gps_status,
        "profile_id": profile_id,
        "profile_version": profile_version,
        "reference_card_version": reference_card_version,
        "algorithm_version": algorithm_version,
        "model_version": model_version,
        "result": result,
        "classification_score": round(classification_score, 4),
        "measurement_quality": measurement_quality,
        "quality_gate_status": quality_gate_status,
        "image_sha256": image_sha256,
        "canonical_algorithm": CANONICAL_ALGORITHM,
        "previous_record_hash": previous_record_hash,
    }
