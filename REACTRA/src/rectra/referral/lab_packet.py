"""Automated laboratory referral packet generator for ambiguous or compromised field tests.

Produces both a machine-readable JSON packet (RECTRA_REFERRAL_{TEST_ID}.json)
and a professional human-readable HTML referral report (RECTRA_REFERRAL_{TEST_ID}.html).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from rectra.config import RUNTIME_DIR
from rectra.core.constants import (
    DISCLAIMER_LAB_REQUIRED,
    DISCLAIMER_PRESUMPTIVE,
    DISCLAIMER_SYNTHETIC_NOTE,
)
from rectra.core.types import (
    CaptureMetadata,
    ClassificationResult,
    QualityGateResult,
)

logger = logging.getLogger(__name__)


def should_refer_to_lab(
    quality_gate_status: str,
    classification_result: str | None = None,
) -> bool:
    """Determine whether a test meets the automated lab referral threshold."""
    if quality_gate_status in ("REVIEW", "RECAPTURE"):
        return True
    if classification_result == "INCONCLUSIVE":
        return True
    return False


def generate_lab_packet(
    test_id: str,
    metadata: CaptureMetadata,
    quality_gate: QualityGateResult,
    classification: ClassificationResult | None,
    image_sha256: str,
    record_digest: str,
    signature_status: str,
    output_dir: Path | None = None,
) -> tuple[Path, Path]:
    """Generate both JSON and HTML lab referral packets."""
    dest_dir = output_dir or RUNTIME_DIR / "referrals"
    dest_dir.mkdir(parents=True, exist_ok=True)

    json_path = dest_dir / f"RECTRA_REFERRAL_{test_id}.json"
    html_path = dest_dir / f"RECTRA_REFERRAL_{test_id}.html"

    # Determine referral reasons
    reasons = list(quality_gate.reasons)
    res_str = "N/A"
    if classification is not None:
        res_str = (
            classification.result.value
            if hasattr(classification.result, "value")
            else str(classification.result)
        )

    if res_str == "INCONCLUSIVE":
        reasons.append("Presumptive test interpretation is ambiguous (INCONCLUSIVE).")

    q_status_str = (
        quality_gate.status.value
        if hasattr(quality_gate.status, "value")
        else str(quality_gate.status)
    )
    cm_str = (
        metadata.capture_mode.value
        if hasattr(metadata.capture_mode, "value")
        else str(metadata.capture_mode)
    )
    gps_str = (
        metadata.gps_status.value
        if hasattr(metadata.gps_status, "value")
        else str(metadata.gps_status)
    )

    packet_data: dict[str, Any] = {
        "referral_format": "rectra-referral-v1",
        "test_id": test_id,
        "disclaimer_header": f"{DISCLAIMER_PRESUMPTIVE} — {DISCLAIMER_LAB_REQUIRED}",
        "synthetic_notice": DISCLAIMER_SYNTHETIC_NOTE,
        "operator_id": metadata.operator_id,
        "timestamp_utc": metadata.timestamp_utc,
        "capture_mode": cm_str,
        "gps": {
            "status": gps_str,
            "latitude": metadata.latitude,
            "longitude": metadata.longitude,
        },
        "assay_profile": {
            "profile_id": metadata.profile_id,
            "profile_version": metadata.profile_version,
        },
        "measurement_status": {
            "quality_gate_status": q_status_str,
            "quality_metrics": {
                "blur": quality_gate.blur,
                "exposure": quality_gate.exposure,
                "glare": quality_gate.glare,
                "calibration": quality_gate.calibration,
                "roi": quality_gate.roi,
            },
            "referral_reasons": reasons,
        },
        "classification": {
            "presumptive_result": res_str,
            "classification_score": classification.classification_score if classification else 0.0,
            "class_scores": classification.class_scores if classification else {},
            "model_version": classification.model_version if classification else "N/A",
            "algorithm_version": classification.algorithm_version if classification else "N/A",
        },
        "evidence": {
            "image_sha256": image_sha256,
            "record_digest": record_digest,
            "signature_status": signature_status,
        },
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(packet_data, f, indent=2)

    coords_display = (
        f"{metadata.latitude:.5f}, {metadata.longitude:.5f}"
        if metadata.latitude is not None and metadata.longitude is not None
        else "N/A"
    )
    reasons_html = "".join(f"<li>{r}</li>" for r in reasons)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RECTRA Lab Referral — {test_id}</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #f8fafc;
               color: #0f172a; margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 860px; margin: 0 auto; background: #fff; border-radius: 8px;
                      border: 1px solid #e2e8f0; padding: 32px; }}
        .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 24px; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px;
                  font-weight: 700; font-size: 0.85rem; background: #fee2e2; color: #991b1b; }}
        .warning-banner {{ background: #fef3c7; border-left: 4px solid #f59e0b;
                           padding: 12px 16px; margin-bottom: 24px; font-weight: 600;
                           color: #92400e; }}
        .notice-banner {{ background: #f1f5f9; border-left: 4px solid #64748b;
                          padding: 10px 16px; margin-bottom: 24px; font-size: 0.85rem;
                          color: #475569; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
                 margin-bottom: 24px; }}
        .box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;
                padding: 16px; }}
        .box h3 {{ margin-top: 0; font-size: 1rem; color: #1e293b;
                   border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; }}
        ul {{ padding-left: 20px; margin: 8px 0; }}
        code {{ background: #e2e8f0; padding: 2px 6px; border-radius: 4px;
                font-size: 0.85rem; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="float: right;">
                <span class="badge">REFERRAL: {q_status_str}</span>
            </div>
            <h1 style="margin: 0; font-size: 1.5rem; color: #1e293b;">
                🔬 RECTRA Laboratory Referral Packet
            </h1>
            <div style="color: #64748b; font-size: 0.9rem; margin-top: 4px;">
                Test UUID: <code>{test_id}</code>
            </div>
        </div>

        <div class="warning-banner">
            ⚠️ {DISCLAIMER_PRESUMPTIVE} — {DISCLAIMER_LAB_REQUIRED}
        </div>

        <div class="notice-banner">
            ℹ️ {DISCLAIMER_SYNTHETIC_NOTE}
        </div>

        <div class="grid">
            <div class="box">
                <h3>1. Incident & Capture Context</h3>
                <p><strong>Operator ID:</strong> {metadata.operator_id}</p>
                <p><strong>Timestamp (UTC):</strong> {metadata.timestamp_utc}</p>
                <p><strong>Capture Mode:</strong> {cm_str}</p>
                <p><strong>GPS Status:</strong> {gps_str}</p>
                <p><strong>Coordinates:</strong> {coords_display}</p>
                <p><strong>Assay:</strong> {metadata.profile_id} v{metadata.profile_version}</p>
            </div>

            <div class="box">
                <h3>2. Presumptive Test Finding</h3>
                <p><strong>Result:</strong>
                   <span style="font-weight: 700; color: #b91c1c;">{res_str}</span></p>
                <p><strong>Quality Gate Status:</strong> {q_status_str}</p>
                <p><strong>Referral Triggers:</strong></p>
                <ul>{reasons_html}</ul>
            </div>
        </div>

        <div class="box" style="margin-bottom: 24px;">
            <h3>3. Cryptographic Chain-of-Custody Attestation</h3>
            <p><strong>Image SHA-256:</strong> <code>{image_sha256}</code></p>
            <p><strong>Canonical Record Digest:</strong> <code>{record_digest}</code></p>
            <p><strong>Ed25519 Digital Signature:</strong> <code>{signature_status}</code></p>
        </div>

        <div style="text-align: center; color: #94a3b8; font-size: 0.8rem;
                    border-top: 1px solid #e2e8f0; padding-top: 16px;">
            RECTRA Calibrated Field-Test Intelligence & Evidence System | SIH26231 Prototype
        </div>
    </div>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info("Generated lab referral packets: %s and %s", json_path.name, html_path.name)
    return json_path, html_path
