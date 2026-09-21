from __future__ import annotations

from typing import Any

import streamlit as st

from rectra.core.constants import (
    DISCLAIMER_LAB_REQUIRED,
    DISCLAIMER_PRESUMPTIVE,
    ChainStatus,
    PassportStatus,
    SignatureStatus,
)
from rectra.core.types import (
    CalibrationResult,
    CaptureMetadata,
    ClassificationResult,
    QualityGateResult,
    ReliabilityPassport,
)


def build_reliability_passport(
    metadata: CaptureMetadata,
    quality_gate: QualityGateResult,
    calibration: CalibrationResult | None,
    classification: ClassificationResult | None,
    image_sha256: str = "N/A",
    record_digest: str = "N/A",
    signature_status: str | SignatureStatus = SignatureStatus.NOT_SIGNED,
    chain_status: str | ChainStatus = ChainStatus.NOT_CHAINED,
) -> ReliabilityPassport:
    """Construct a structured ReliabilityPassport from operational pipeline outputs."""
    if quality_gate.status == "RECAPTURE":
        overall = PassportStatus.RECAPTURE
    elif quality_gate.status == "REVIEW":
        overall = PassportStatus.REVIEW
    elif classification is not None and str(classification.result) == "INCONCLUSIVE":
        overall = PassportStatus.REVIEW
    elif quality_gate.status == "VALID":
        overall = PassportStatus.READY
    else:
        overall = PassportStatus.REVIEW

    cm_val = (
        metadata.capture_mode.value
        if hasattr(metadata.capture_mode, "value")
        else str(metadata.capture_mode)
    )
    gps_val = (
        metadata.gps_status.value
        if hasattr(metadata.gps_status, "value")
        else str(metadata.gps_status)
    )
    q_status_val = (
        quality_gate.status.value
        if hasattr(quality_gate.status, "value")
        else str(quality_gate.status)
    )
    res_val = "N/A"
    if classification is not None:
        res_val = (
            classification.result.value
            if hasattr(classification.result, "value")
            else str(classification.result)
        )

    return ReliabilityPassport(
        capture_mode=cm_val,
        timestamp_utc=metadata.timestamp_utc,
        operator_id=metadata.operator_id,
        gps_status=gps_val,
        latitude=metadata.latitude,
        longitude=metadata.longitude,
        card_detected=quality_gate.card_pass if hasattr(quality_gate, "card_pass") else True,
        card_profile=f"{metadata.profile_id} v{metadata.profile_version}",
        calibration_valid=calibration.calibration_valid if calibration else False,
        calibration_residual_delta_e=calibration.residual_delta_e if calibration else 999.0,
        image_quality=q_status_val,
        roi_quality="Valid" if quality_gate.roi.get("pass") else "Invalid",
        presumptive_result=res_val,
        class_scores=classification.class_scores if classification else {},
        classification_score=classification.classification_score if classification else 0.0,
        model_version=classification.model_version if classification else "N/A",
        algorithm_version=classification.algorithm_version if classification else "N/A",
        image_sha256=image_sha256,
        record_digest=record_digest,
        signature_status=signature_status,
        chain_status=chain_status,
        overall_status=overall,
    )


def render_reliability_passport(passport: ReliabilityPassport) -> None:
    """Render the structured Field Test Reliability Passport in Streamlit."""
    status_str = (
        passport.overall_status.value
        if hasattr(passport.overall_status, "value")
        else str(passport.overall_status)
    )

    if status_str == "READY":
        status_color = "#10b981"
        status_desc = "READY — Usable measurement. Presumptive field interpretation produced."
    elif status_str == "REVIEW":
        status_color = "#f59e0b"
        status_desc = "REVIEW REQUIRED — Measurement ambiguous or optical variance detected."
    else:
        status_color = "#ef4444"
        status_desc = "RECAPTURE REQUIRED — Measurement failed validity gate. Do not interpret."

    banner_html = f"""
    <div style="background-color: #0f172a; border-left: 6px solid {status_color};
                padding: 16px 20px; border-radius: 6px; margin-bottom: 20px;">
        <div style="font-size: 0.85rem; text-transform: uppercase; color: #94a3b8;">
            Field Test Reliability Passport
        </div>
        <div style="font-size: 1.5rem; font-weight: 800; color: {status_color}; margin-top: 4px;">
            OVERALL STATUS: {status_str}
        </div>
        <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 4px;">
            {status_desc}
        </div>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)
    st.warning(f"⚠️ **{DISCLAIMER_PRESUMPTIVE}** — {DISCLAIMER_LAB_REQUIRED}")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("### 📷 1. Capture")
            st.write(f"**Capture Mode:** `{passport.capture_mode}`")
            st.write(f"**Timestamp (UTC):** `{passport.timestamp_utc}`")
            st.write(f"**Operator ID:** `{passport.operator_id}`")
            if passport.latitude is not None and passport.longitude is not None:
                coord_str = f"{passport.latitude:.4f}, {passport.longitude:.4f}"
                st.write(f"**GPS ({passport.gps_status}):** `{coord_str}`")
            else:
                st.write(f"**GPS Status:** `{passport.gps_status}`")

        with st.container(border=True):
            st.markdown("### 🔬 2. Measurement")
            st.write(f"**Card Detected:** {'✅ Yes' if passport.card_detected else '❌ No'}")
            st.write(f"**Card Profile:** `{passport.card_profile}`")
            c_val = "✅ Valid" if passport.calibration_valid else "❌ Invalid"
            st.write(f"**Calibration:** {c_val}")
            st.write(f"**Residual ΔE:** `{passport.calibration_residual_delta_e:.2f}`")
            st.write(f"**Image Quality Gate:** `{passport.image_quality}`")
            st.write(f"**ROI Quality:** `{passport.roi_quality}`")

    with col2:
        with st.container(border=True):
            st.markdown("### 📊 3. Classification")
            st.markdown(f"**Presumptive Result:** `{passport.presumptive_result}`")
            st.write(f"**Prototype Score:** `{passport.classification_score:.2f}`")
            st.caption("*(Prototype confidence proxy — not laboratory certainty)*")
            if passport.class_scores:
                st.write("**Centroid Distances (ΔE):**")
                for cls, score in passport.class_scores.items():
                    st.write(f"- {cls}: `{score:.2f}`")
            st.write(f"**Model:** `{passport.model_version}`")
            st.write(f"**Algorithm:** `{passport.algorithm_version}`")

        with st.container(border=True):
            st.markdown("### 🔒 4. Evidence Integrity")
            img_h = (
                passport.image_sha256[:16] + "..."
                if len(passport.image_sha256) > 16
                else passport.image_sha256
            )
            rec_d = (
                passport.record_digest[:16] + "..."
                if len(passport.record_digest) > 16
                else passport.record_digest
            )
            st.write(f"**Image SHA-256:** `{img_h}`")
            st.write(f"**Record Digest:** `{rec_d}`")
            st.write(f"**Digital Signature:** `{passport.signature_status}`")
            st.write(f"**Audit Chain:** `{passport.chain_status}`")


def draw_detection_overlay(
    warped_card: Any,
    roi_coords: tuple[int, int, int, int] | None = None,
) -> Any:
    """Draw bounding boxes for reference card patches and reaction zone ROI on warped card."""
    import cv2

    from rectra.vision.card_detector import CANONICAL_PATCH_BOXES

    overlay = warped_card.copy()

    # Draw 6 canonical reference patch boxes (green)
    for name, box in CANONICAL_PATCH_BOXES.items():
        bx, by, bw, bh = box
        cv2.rectangle(overlay, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
        cv2.putText(
            overlay,
            name.upper(),
            (bx + 4, by + 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )

    # Draw test reaction zone ROI box (cyan/blue)
    rx, ry, rw, rh = roi_coords if roi_coords else (400, 200, 200, 200)
    cv2.rectangle(overlay, (rx, ry), (rx + rw, ry + rh), (255, 128, 0), 3)
    cv2.putText(
        overlay,
        "TEST REACTION ROI",
        (rx + 5, ry - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 128, 0),
        2,
        cv2.LINE_AA,
    )
    return overlay


def generate_evidence_html_report(
    evidence_dict: dict, test_session_dict: dict | None = None
) -> str:
    """Generate a self-contained, human-readable HTML digital evidence summary report."""
    test_id = evidence_dict.get("test_id", "UNKNOWN")
    digest = evidence_dict.get("record_digest", "N/A")
    sig = evidence_dict.get("signature", "N/A")
    fp = evidence_dict.get("public_key_fingerprint", "N/A")
    img_h = evidence_dict.get("image_sha256", "N/A")
    result = evidence_dict.get("result", "UNKNOWN")
    score = evidence_dict.get("classification_score", 0.0)
    operator = evidence_dict.get("operator_id", "N/A")
    ts = evidence_dict.get("timestamp_utc", "N/A")
    prev_h = evidence_dict.get("previous_record_hash", "GENESIS")

    badge_cls = (
        "badge-pos"
        if result == "POSITIVE"
        else "badge-neg"
        if result == "NEGATIVE"
        else "badge-inc"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>REACTRA Digital Evidence Record — {test_id}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: #0f172a; color: #f8fafc; margin: 0; padding: 30px; }}
  .card {{ background: #1e293b; border-radius: 10px; padding: 25px; margin-bottom: 20px;
           border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }}
  .header {{ border-left: 6px solid #3b82f6; padding-left: 15px; margin-bottom: 25px; }}
  h1 {{ margin: 0; font-size: 24px; color: #f8fafc; }}
  .subtitle {{ color: #94a3b8; font-size: 14px; margin-top: 5px; }}
  .badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px;
            font-weight: 700; font-size: 14px; }}
  .badge-pos {{ background: #991b1b; color: #fef2f2; }}
  .badge-neg {{ background: #166534; color: #f0fdf4; }}
  .badge-inc {{ background: #854d0e; color: #fefce8; }}
  .hash {{ font-family: monospace; background: #020617; padding: 6px 10px;
          border-radius: 4px; color: #38bdf8; word-break: break-all; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
  .label {{ font-size: 12px; text-transform: uppercase; color: #94a3b8; margin-bottom: 3px; }}
  .val {{ font-size: 15px; font-weight: 600; color: #f1f5f9; }}
  .disclaimer {{ background: #451a03; border-left: 4px solid #f59e0b; padding: 12px;
                border-radius: 4px; color: #fef3c7; font-size: 13px; margin-top: 20px; }}
</style>
</head>
<body>
  <div class="header">
    <h1>🔬 REACTRA Digital Evidence Record</h1>
    <div class="subtitle">Reaction-Aware Field Testing & Verifiable Evidence | SIH26231</div>
  </div>

  <div class="card">
    <div class="label">Presumptive Classification</div>
    <div style="margin: 10px 0;">
      <span class="badge {badge_cls}">
        {result}
      </span>
      <span style="margin-left: 15px; font-size: 16px; color: #94a3b8;">
        Prototype Score: <strong>{score:.2f}</strong>
      </span>
    </div>
    <div class="disclaimer">
      <strong>PRESUMPTIVE FIELD-TEST RESULT</strong> — Laboratory confirmation is required.<br>

      This digital evidence record seals the physical and optical measurement context.
    </div>
  </div>

  <div class="card">
    <div class="grid">
      <div><div class="label">Test UUID</div><div class="val">{test_id}</div></div>
      <div><div class="label">Operator ID</div><div class="val">{operator}</div></div>
      <div><div class="label">Timestamp (UTC)</div><div class="val">{ts}</div></div>
      <div><div class="label">Signing Algorithm</div><div class="val">Ed25519 (RFC 8032)</div></div>
    </div>
  </div>

  <div class="card">
    <div class="label">Image SHA-256 Digest</div>
    <div class="hash">{img_h}</div>
    <div style="height: 12px;"></div>
    <div class="label">Canonical Evidence Record Digest</div>
    <div class="hash">{digest}</div>
    <div style="height: 12px;"></div>
    <div class="label">Ed25519 Digital Signature</div>
    <div class="hash">{sig}</div>
    <div style="height: 12px;"></div>
    <div class="label">Public Key Fingerprint</div>
    <div class="hash">{fp}</div>
    <div style="height: 12px;"></div>
    <div class="label">Previous Record Hash (Audit Chain)</div>
    <div class="hash">{prev_h}</div>
  </div>
</body>
</html>
"""
    return html
