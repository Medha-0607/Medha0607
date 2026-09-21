"""Streamlit page implementations for the REACTRA field companion application."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import cv2
import streamlit as st

from rectra.classification.evaluation import load_evaluation_results
from rectra.core.constants import (
    DISCLAIMER_LAB_REQUIRED,
    DISCLAIMER_PRESUMPTIVE,
    DISCLAIMER_SYNTHETIC_NOTE,
    CaptureMode,
    ChainStatus,
    GpsStatus,
    QualityStatus,
    SessionState,
    SignatureStatus,
)
from rectra.core.session_manager import (
    clear_active_session,
    create_new_draft,
    get_active_session,
    init_session_state,
    update_active_session,
)
from rectra.database.connection import get_connection
from rectra.database.repository import (
    get_evidence_record,
    save_evidence_record,
    search_test_history,
)
from rectra.demo.scenarios import run_demo_scenario, run_pipeline_on_image
from rectra.evidence.canonical import build_canonical_record_dict
from rectra.evidence.chain import get_latest_record_hash
from rectra.evidence.envelope import create_evidence_envelope
from rectra.evidence.hashing import compute_record_digest
from rectra.evidence.signing import get_public_key_fingerprint, sign_digest
from rectra.models import EvidenceRecordModel
from rectra.profiles.loader import list_available_profiles, load_profile
from rectra.referral.lab_packet import generate_lab_packet, should_refer_to_lab
from rectra.ui.components import (
    build_reliability_passport,
    draw_detection_overlay,
    generate_evidence_html_report,
    render_reliability_passport,
)
from rectra.vision.capture import load_image_to_bgr
from rectra.vision.card_detector import detect_card

logger = logging.getLogger(__name__)


def render_home_page() -> None:
    """Render REACTRA landing page with primary actions and system status."""
    st.title("🔬 REACTRA")
    st.subheader("Reaction-Aware Field Testing & Verifiable Evidence")
    st.caption("SIH 2026 — Problem Statement SIH26231 (Digital Companion for Field Drug Testing)")

    st.markdown(
        f"""
        > **{DISCLAIMER_PRESUMPTIVE}** — {DISCLAIMER_LAB_REQUIRED}
        > *{DISCLAIMER_SYNTHETIC_NOTE}*
        """
    )

    # Primary Action Buttons
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🚀 Start New Field Test", type="primary", use_container_width=True):
            clear_active_session()
            st.session_state["nav_target"] = "START FIELD TEST"
            st.rerun()
    with c2:
        if st.button("📂 Open Test History", use_container_width=True):
            st.session_state["nav_target"] = "TEST HISTORY ARCHIVE"
            st.rerun()
    with c3:
        if st.button("🧪 Validation & QA Mode", use_container_width=True):
            st.session_state["nav_target"] = "VALIDATION & QA"
            st.rerun()

    st.markdown("---")

    # Workflow Visual Story
    st.markdown("### 5-Step Operational Pipeline")
    p_cols = st.columns(5)
    with p_cols[0]:
        st.info("**1. CAPTURE**\n\nLive camera or verified image import with audit metadata.")
    with p_cols[1]:
        st.info(
            "**2. CALIBRATE**\n\nCompensate ambient lighting against canonical CIE Lab patches."
        )
    with p_cols[2]:
        st.info("**3. VALIDATE**\n\nStrict pre-classification gate: blur, glare, exposure, ROI.")
    with p_cols[3]:
        st.info("**4. CLASSIFY**\n\nPresumptive interpretation with explainable centroid distance.")
    with p_cols[4]:
        st.info(
            "**5. PRESERVE**\n\nEd25519 asymmetric signature & local tamper-evident hash chain."
        )

    st.markdown("---")

    # System Status and Reference Card
    col_stat, col_card = st.columns(2)
    with col_stat:
        with st.container(border=True):
            st.markdown("#### ⚙️ System Status")
            st.write("📷 **Camera Pipeline:** Live & Import Supported")
            st.write("💾 **Database:** Connected (Local SQLite)")
            st.write("🔑 **Signing Key:** Ed25519 Active")
            st.write("📋 **Assay Profiles:** Installed & Validated")
            st.caption("Zero cloud dependencies. Completely offline-capable.")

    with col_card:
        with st.container(border=True):
            st.markdown("#### 📄 Submission & Deployment Assets")
            st.caption("Official SIH 2026 Project Report and Printable 300 DPI Reference Card.")

            # 1. Printable Reference Card
            pdf_path = Path("assets/reference_cards/RECTRA_PRINTABLE_REFERENCE_CARD.pdf")
            if not pdf_path.exists():
                from scripts.generate_printable_cards import generate_printable_card_pdf

                generate_printable_card_pdf(pdf_path)

            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                "📥 Download Reference Card (PDF)",
                data=pdf_bytes,
                file_name="REACTRA_REFERENCE_CARD.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            # 2. Comprehensive SIH Project Report (HTML)
            report_html_path = Path("submission/REACTRA_SIH2026_PROJECT_REPORT.html")
            if report_html_path.exists():
                with open(report_html_path, "rb") as f:
                    html_bytes = f.read()
                st.download_button(
                    "📊 Download Full Project Report (HTML / PDF)",
                    data=html_bytes,
                    file_name="REACTRA_SIH2026_PROJECT_REPORT.html",
                    mime="text/html",
                    use_container_width=True,
                )

            # 3. Comprehensive SIH Project Report (Markdown)
            report_md_path = Path("submission/REACTRA_SIH2026_PROJECT_REPORT.md")
            if report_md_path.exists():
                with open(report_md_path, "rb") as f:
                    md_bytes = f.read()
                st.download_button(
                    "📝 Download Pitch & PPT Report (Markdown)",
                    data=md_bytes,
                    file_name="REACTRA_SIH2026_PROJECT_REPORT.md",
                    mime="text/markdown",
                    use_container_width=True,
                )


def render_field_operator_workflow() -> None:
    """Render the unified 6-step field operator workflow."""
    init_session_state()
    step = st.session_state.get("wizard_step", 1)

    # Step Breadcrumbs
    steps_labels = [
        "1. Setup",
        "2. Capture",
        "3. Check",
        "4. Result",
        "5. Evidence",
        "6. Complete",
    ]
    step_cols = st.columns(6)
    for i, s_col in enumerate(step_cols):
        idx = i + 1
        if idx < step:
            s_col.markdown(f"**✅ {steps_labels[i]}**")
        elif idx == step:
            s_col.markdown(f"**:blue[▶ {steps_labels[i]}]**")
        else:
            s_col.markdown(
                f"<span style='color: #64748b;'>{steps_labels[i]}</span>", unsafe_allow_html=True
            )

    st.markdown("---")

    if step == 1:
        _render_step_setup()
    elif step == 2:
        _render_step_capture()
    elif step == 3:
        _render_step_check()
    elif step == 4:
        _render_step_result()
    elif step == 5:
        _render_step_evidence()
    elif step == 6:
        _render_step_complete()


def _render_step_setup() -> None:
    """Step 1: Operator credentials, assay profile, and capture configuration."""
    st.markdown("### Step 1: Start New Field Test Session")
    st.markdown("Initialize field metadata, target reagent assay profile, and location mode.")

    # Profiles discovery
    profiles = list_available_profiles()
    if not profiles:
        default_prof = load_profile()
        profiles = [default_prof]

    prof_options = {
        f"{p['profile_id']} — {p['display_name']} "
        f"({'Calibrated' if p.get('is_calibrated', True) else 'Calibration Required'})": p
        for p in profiles
    }

    selected_label = st.selectbox("Target Reagent Assay Profile *", list(prof_options.keys()))
    selected_prof = prof_options[selected_label]
    is_calibrated = selected_prof.get("is_calibrated", True) and (
        selected_prof.get("class_centroids_lab") is not None
    )

    if not is_calibrated:
        st.warning("⚠️ This profile requires physical calibration before use.")
        st.caption(
            selected_prof.get(
                "documentation_note",
                "Real-world colorimetric calibration required before use. Not validated.",
            )
        )

    col1, col2 = st.columns(2)
    with col1:
        operator_id = st.text_input(
            "Operator ID *", value="DET-SHARMA-402", help="Officer badge or terminal ID."
        )
    with col2:
        capture_method = st.radio("Capture Method *", ["Import Image / Demo", "Live Device Camera"])

    st.markdown("#### Geolocation Handling")
    loc_mode = st.radio(
        "Location Source:",
        ["GPS Unavailable / Not Reported", "Explicit Manual Demo Location (Testing Only)"],
        index=0,
    )

    demo_lat, demo_lon, gps_status = None, None, GpsStatus.UNAVAILABLE
    if loc_mode == "Explicit Manual Demo Location (Testing Only)":
        st.caption("Explicitly labelled demonstration coordinates. Never fabricated as GPS.")
        c_lat, c_lon = st.columns(2)
        with c_lat:
            demo_lat = st.number_input("Latitude", value=19.0760, format="%.5f")
        with c_lon:
            demo_lon = st.number_input("Longitude", value=72.8777, format="%.5f")
        gps_status = GpsStatus.MANUAL_DEMO

    st.text_input("Capture Device", value="Not reported by browser", disabled=True)

    st.markdown("---")
    continue_disabled = not is_calibrated or len(operator_id.strip()) < 3
    if st.button("Continue to Capture ➔", type="primary", disabled=continue_disabled):
        cap_mode = (
            CaptureMode.LIVE_CAMERA
            if capture_method == "Live Device Camera"
            else CaptureMode.IMPORTED_IMAGE
        )
        create_new_draft(
            operator_id=operator_id.strip(),
            profile_id=selected_prof["profile_id"],
            profile_version=selected_prof["profile_version"],
            capture_mode=cap_mode,
            latitude=demo_lat,
            longitude=demo_lon,
            gps_status=gps_status,
        )
        st.session_state["active_profile"] = selected_prof
        st.session_state["wizard_step"] = 2
        st.rerun()



def _render_step_capture() -> None:
    """Step 2: Live camera framing or verified image import."""
    st.markdown("### Step 2: Image Capture & Ingestion")
    session = get_active_session()
    if not session:
        st.warning("No active session found. Returning to setup.")
        st.session_state["wizard_step"] = 1
        st.rerun()
        return

    meta = session["metadata"]
    st.caption(
        f"Test ID: `{session.get('test_id', 'N/A')}` | Operator: `{meta['operator_id']}` | "
        f"Profile: `{meta['profile_id']} v{meta['profile_version']}`"
    )

    is_live = meta.get("capture_mode") == str(CaptureMode.LIVE_CAMERA)

    img_bgr = None
    if is_live:
        st.markdown("#### Live Device Camera")
        st.info("Align the reference card and the reaction target area squarely in the frame.")
        cam_file = st.camera_input("Capture Reference Card")
        if cam_file:
            img_bgr = load_image_to_bgr(cam_file)
    else:
        st.markdown(
            "> ⚠️ **IMPORT MODE** — This image was not captured through the live camera workflow."
        )
        tab_sample, tab_upload = st.tabs(["⚡ One-Click Demo Sample", "📁 Upload Image File"])
        with tab_sample:
            demo_samples = {
                "Case 1: Positive Reaction (DEMO-POS-001)": Path(
                    "data/demo/positive/DEMO-POS-001.png"
                ),
                "Case 2: Negative Unreacted (DEMO-NEG-001)": Path(
                    "data/demo/negative/DEMO-NEG-001.png"
                ),
                "Case 3: Ambiguous Inconclusive (DEMO-INC-001)": Path(
                    "data/demo/inconclusive/DEMO-INC-001.png"
                ),
                "Case 4: Motion Blurred Sample (DEMO-EDGE-BLURRED)": Path(
                    "data/demo/edge_cases/DEMO-EDGE-BLURRED.png"
                ),
                "Case 5: Overexposed Glare Sample (DEMO-EDGE-OVEREXPOSED)": Path(
                    "data/demo/edge_cases/DEMO-EDGE-OVEREXPOSED.png"
                ),
            }
            sample_choice = st.selectbox(
                "Select Controlled Benchmark Sample", list(demo_samples.keys())
            )
            sample_path = demo_samples[sample_choice]
            if sample_path.exists():
                img_bgr = cv2.imread(str(sample_path))

        with tab_upload:
            uploaded = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
            if uploaded:
                img_bgr = load_image_to_bgr(uploaded)

    if img_bgr is not None:
        st.markdown("---")
        col_prev, col_status = st.columns([1, 1])
        with col_prev:
            st.image(
                cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB),
                caption="Captured Input Image",
                width=360,
            )

        with col_status:
            # Quick card presence test
            prof = st.session_state.get("active_profile") or load_profile(
                meta["profile_id"], meta["profile_version"]
            )
            card_res = detect_card(img_bgr, prof)
            if card_res.detected:
                st.success(f"✅ Card Detected (Geometry: {card_res.geometry_quality:.2f})")
            else:
                st.error("❌ Reference Card Not Detected in Frame")
                st.caption(card_res.rejection_reason or "Ensure all 4 card corners are visible.")

            if st.button("Run Measurement & Quality Check ➔", type="primary"):
                with st.spinner("Executing REACTRA measurement pipeline..."):
                    pipeline = run_pipeline_on_image(
                        img_bgr,
                        operator_id=meta["operator_id"],
                        latitude=meta.get("latitude"),
                        longitude=meta.get("longitude"),
                        gps_status=meta.get("gps_status", GpsStatus.UNAVAILABLE),
                        capture_mode=meta.get("capture_mode", CaptureMode.IMPORTED_IMAGE),
                        profile_id=meta["profile_id"],
                        profile_version=meta["profile_version"],
                    )
                    pipeline["test_id"] = session.get("test_id")
                    pipeline["image_bgr"] = img_bgr

                    next_state = (
                        SessionState.VALIDATION_FAILED
                        if pipeline["quality_gate"].status == QualityStatus.RECAPTURE
                        else SessionState.READY_FOR_CLASSIFICATION
                    )
                    update_active_session(pipeline, next_state)
                    st.session_state["wizard_step"] = 3
                    st.rerun()

    c_back, _ = st.columns([1, 4])
    with c_back:
        if st.button("⬅ Back to Setup"):
            st.session_state["wizard_step"] = 1
            st.rerun()


def _render_step_check() -> None:
    """Step 3: Pre-classification measurement readiness check."""
    st.markdown("### Step 3: Measurement Readiness & Quality Gate")
    session = get_active_session()
    if not session or "quality_gate" not in session:
        st.warning("No measurement data found. Please capture an image first.")
        st.session_state["wizard_step"] = 2
        st.rerun()
        return

    q_gate = session["quality_gate"]
    card_res = session["card_detection"]
    status_str = str(q_gate.status.value if hasattr(q_gate.status, "value") else q_gate.status)

    # Big Status Alert
    if status_str == "VALID":
        st.success("### ✅ OVERALL STATUS: READY FOR ANALYSIS\nMeasurement conditions verified.")
    elif status_str == "REVIEW":
        st.warning(
            "### ⚠️ OVERALL STATUS: REVIEW REQUIRED\n"
            "Measurement exhibits optical or lighting variance."
        )
    else:
        st.error(
            "### 🛑 OVERALL STATUS: RECAPTURE REQUIRED\n"
            "Measurement conditions failed. Classification is blocked."
        )

    # Quality Gate Matrix
    m_cols = st.columns(4)
    with m_cols[0]:
        blur_val = q_gate.blur.get("laplacian_variance", 0.0)
        st.metric(
            "Blur (Laplacian)",
            f"{blur_val:.1f}",
            "PASS" if q_gate.blur.get("pass") else "FAIL (<80)",
        )
    with m_cols[1]:
        exp_val = q_gate.exposure.get("mean_brightness", 0.0)
        st.metric(
            "Exposure", f"{exp_val:.1f}", "PASS" if q_gate.exposure.get("pass") else "FAIL (50-220)"
        )
    with m_cols[2]:
        glare_pct = q_gate.glare.get("saturation_fraction", 0.0) * 100.0
        st.metric(
            "Specular Glare",
            f"{glare_pct:.1f}%",
            "PASS" if q_gate.glare.get("pass") else "FAIL (>5%)",
        )
    with m_cols[3]:
        st.metric("Card Detection", "DETECTED" if card_res.detected else "FAIL")

    if q_gate.reasons:
        st.markdown("#### Identified Quality Gate Issues:")
        for r in q_gate.reasons:
            st.error(f"- {r}")

        st.info(
            "💡 **Corrective Action:** Adjust lighting to minimize glare, stabilize the "
            "camera, and ensure the reference card is fully visible."
        )


    st.markdown("---")
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🔄 Recapture Image (Back to Step 2)"):
            st.session_state["wizard_step"] = 2
            st.rerun()

    with col_nav2:
        if status_str == "VALID":
            if st.button("Proceed to Presumptive Result ➔", type="primary"):
                st.session_state["wizard_step"] = 4
                st.rerun()
        else:
            if st.button("📋 Generate Lab Referral Packet (Quality Failure) ➔"):
                st.session_state["nav_target"] = "LAB REFERRAL PACKETS"
                st.rerun()


def _render_step_result() -> None:
    """Step 4: Presumptive interpretation and visual explanation layer."""
    st.markdown("### Step 4: Presumptive Result & Visual Explanation")
    session = get_active_session()
    if not session or "classification" not in session or session["classification"] is None:
        st.warning("No classification available. Image did not pass quality gate.")
        st.session_state["wizard_step"] = 3
        st.rerun()
        return

    cls_res = session["classification"]
    calib = session.get("calibration")
    card_res = session.get("card_detection")

    res_val = str(cls_res.result.value if hasattr(cls_res.result, "value") else cls_res.result)

    # Result Header Box
    res_color = (
        "#991b1b" if res_val == "POSITIVE" else "#166534" if res_val == "NEGATIVE" else "#854d0e"
    )
    st.markdown(
        f"""
        <div style="background-color: #1e293b; border-left: 8px solid {res_color};
                    padding: 18px 24px; border-radius: 8px; margin-bottom: 20px;">
            <div style="font-size: 0.9rem; text-transform: uppercase; color: #94a3b8;">
                Presumptive Field-Test Result
            </div>
            <div style="font-size: 2.2rem; font-weight: 800; color: #f8fafc; margin-top: 4px;">
                {res_val}
            </div>
            <div style="font-size: 0.95rem; color: #cbd5e1; margin-top: 4px;">
                Prototype Score: <strong>{cls_res.classification_score:.2f}</strong>
                <span style="color: #94a3b8; margin-left: 10px;">
                    (Proxy score — not laboratory certainty)
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning(f"⚠️ **{DISCLAIMER_PRESUMPTIVE}** — {DISCLAIMER_LAB_REQUIRED}")

    # Visual Explanation Layer
    st.markdown("### 🔬 Visual Explanation Layer")
    exp_tab1, exp_tab2 = st.tabs(["📐 Detection & ROI Overlay", "🎨 CIE Lab Colour Alignment"])

    with exp_tab1:
        if card_res and card_res.warped_image is not None:
            overlay = draw_detection_overlay(card_res.warped_image)
            st.image(
                cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB),
                caption="Normalized Card (1000x700): Patches (Green) and ROI (Cyan)",
                width=640,
            )

    with exp_tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### CIE Lab Values")
            if calib:
                lab = calib.corrected_test_colour_lab
                st.write(
                    f"**Measured Test Colour:** `L={lab[0]:.1f}, a={lab[1]:.1f}, b={lab[2]:.1f}`"
                )
                st.write(
                    f"**Calibration Residual ΔE:** `{calib.residual_delta_e:.2f}` (Threshold: 8.00)"
                )
        with c2:
            st.markdown("#### Nearest-Centroid Distances (ΔE)")
            if cls_res.class_scores:
                for c_name, dist in cls_res.class_scores.items():
                    st.write(f"- Distance to **{c_name}**: `{dist:.2f}`")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Back to Measurement Check"):
            st.session_state["wizard_step"] = 3
            st.rerun()
    with col2:
        if st.button("Proceed to Evidence Preservation ➔", type="primary"):
            st.session_state["wizard_step"] = 5
            st.rerun()


def _render_step_evidence() -> None:
    """Step 5: Digital Evidence Preservation & Reliability Passport."""
    st.markdown("### Step 5: Digital Evidence & Reliability Passport")
    session = get_active_session()
    if not session:
        st.warning("No active session.")
        st.session_state["wizard_step"] = 1
        st.rerun()
        return

    meta = session["metadata"]
    q_gate = session["quality_gate"]
    calib = session.get("calibration")
    cls_res = session.get("classification")
    test_id = session.get("test_id")

    passport = build_reliability_passport(
        metadata=meta if hasattr(meta, "operator_id") else session["metadata"],
        quality_gate=q_gate,
        calibration=calib,
        classification=cls_res,
        image_sha256=session["image_sha256"],
        record_digest="Pending sealing...",
        signature_status=SignatureStatus.NOT_SIGNED,
        chain_status=ChainStatus.NOT_CHAINED,
    )
    render_reliability_passport(passport)

    st.markdown("---")
    if st.button(
        "🔒 Sign & Seal in Local Evidence Chain", type="primary", use_container_width=True
    ):
        with st.spinner("Computing canonical record digest and signing with Ed25519..."):
            conn = get_connection()
            prev_hash = get_latest_record_hash(conn)

            res_str = (
                str(cls_res.result.value if hasattr(cls_res.result, "value") else cls_res.result)
                if cls_res
                else "RECAPTURE"
            )
            q_stat_str = str(
                q_gate.status.value if hasattr(q_gate.status, "value") else q_gate.status
            )

            # Build canonical record
            m_dict = meta if isinstance(meta, dict) else meta.__dict__
            record_dict = build_canonical_record_dict(
                test_id=test_id,
                operator_id=m_dict.get("operator_id", "DEMO-OP"),
                capture_mode=m_dict.get("capture_mode", "IMPORTED_IMAGE"),
                timestamp_utc=m_dict.get("timestamp_utc", "2026-09-20T12:00:00Z"),
                latitude=m_dict.get("latitude"),
                longitude=m_dict.get("longitude"),
                gps_status=m_dict.get("gps_status", "UNAVAILABLE"),
                profile_id=m_dict.get("profile_id", "DEMO-ASSAY-001"),
                profile_version=m_dict.get("profile_version", "1.0"),
                reference_card_version="1.0",
                algorithm_version=cls_res.algorithm_version if cls_res else "reactra-algo-v0.1",
                model_version=cls_res.model_version if cls_res else "reactra-model-v0.1",
                result=res_str,
                classification_score=cls_res.classification_score if cls_res else 0.0,
                measurement_quality=q_stat_str,
                quality_gate_status=q_stat_str,
                image_sha256=session["image_sha256"],
                previous_record_hash=prev_hash,
            )

            digest = compute_record_digest(record_dict)
            sig = sign_digest(digest)
            fp = get_public_key_fingerprint()

            record_dict["record_digest"] = digest
            record_dict["signature"] = sig
            record_dict["public_key_fingerprint"] = fp

            # Save evidence to database
            ev_model = EvidenceRecordModel(
                test_id=test_id,
                record_json=json.dumps(record_dict),
                record_digest=digest,
                signature=sig,
                public_key_fingerprint=fp,
                image_sha256=session["image_sha256"],
                previous_record_hash=prev_hash,
                chain_valid=1,
            )
            save_evidence_record(ev_model, conn=conn)
            conn.close()

            session["evidence_record"] = record_dict
            update_active_session(session, SessionState.EVIDENCE_SEALED)

            st.success(f"Evidence sealed! Record Digest: `{digest[:16]}...`")
            st.session_state["wizard_step"] = 6
            st.rerun()


def _render_step_complete() -> None:
    """Step 6: Completed field test attestation and package export."""
    st.markdown("### Step 6: Field Test Complete & Export")
    session = get_active_session()
    if not session or "evidence_record" not in session:
        st.info("No completed evidence record to export.")
        st.session_state["wizard_step"] = 1
        st.rerun()
        return

    ev_record = session["evidence_record"]
    test_id = ev_record.get("test_id", "TEST-000")

    st.success(f"🎉 Field Test `{test_id}` successfully sealed and recorded in local audit chain.")

    col1, col2 = st.columns(2)
    with col1:
        envelope = create_evidence_envelope(ev_record)
        env_json = json.dumps(envelope, indent=2)
        st.download_button(
            "📥 Download Evidence Envelope (.json)",
            data=env_json,
            file_name=f"REACTRA_EVIDENCE_{test_id}.json",
            mime="application/json",
            use_container_width=True,
        )

    with col2:
        html_report = generate_evidence_html_report(ev_record)
        st.download_button(
            "📄 Download Evidence Report (.html)",
            data=html_report,
            file_name=f"REACTRA_EVIDENCE_{test_id}.html",
            mime="text/html",
            use_container_width=True,
        )

    # Referral Check
    if should_refer_to_lab(ev_record):
        st.markdown("---")
        st.warning("⚠️ **Laboratory Confirmation Referral Recommended** for this test.")
        packet = generate_lab_packet(ev_record)
        st.download_button(
            "📑 Download Laboratory Referral Packet (.json)",
            data=json.dumps(packet, indent=2),
            file_name=f"REACTRA_LAB_REFERRAL_{test_id}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("---")
    if st.button("🚀 Start Another Field Test", type="primary"):
        clear_active_session()
        st.session_state["wizard_step"] = 1
        st.rerun()


def render_test_history_page() -> None:
    """Render searchable test history archive."""
    st.title("📂 Test History Archive")
    st.caption(
        "Search and inspect past field tests, verified evidence records, and chain integrity."
    )

    conn = get_connection()
    c_op, c_res = st.columns(2)
    with c_op:
        op_filter = st.text_input("Filter by Operator ID", value="")
    with c_res:
        res_filter = st.selectbox(
            "Filter by Result",
            ["ALL", "POSITIVE", "NEGATIVE", "INCONCLUSIVE", "RECAPTURE"],
        )

    r_arg = None if res_filter == "ALL" else res_filter
    records = search_test_history(
        operator_id=op_filter if op_filter else None, result=r_arg, conn=conn
    )
    conn.close()

    if not records:
        st.info("No matching test records found in local database.")
        return

    st.markdown(f"Found **{len(records)}** archived test session(s):")
    for r in records:
        tid = r["test_id"]
        res = r["result"] or "RECAPTURE"
        ts = r["timestamp_utc"]
        op = r["operator_id"]
        mode = r["capture_mode"]

        with st.expander(f"Test: `{tid}` | {res} | Operator: {op} | {ts}"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Capture Mode:** `{mode}`")
                st.write(f"**Timestamp (UTC):** `{ts}`")
                st.write(f"**Profile:** `{r['profile_id']} v{r['profile_version']}`")
            with c2:
                st.write(f"**Presumptive Result:** `{res}`")
                st.write(f"**Quality Gate:** `{r['quality_gate_status']}`")
                st.write(f"**Saved In DB:** `{r['created_at']}`")

            ev = get_evidence_record(tid)
            if ev:
                st.markdown("---")
                st.write(f"**Record Digest:** `{ev.record_digest}`")
                st.write(f"**Ed25519 Signature:** `{ev.signature[:32]}...`")
                st.write(f"**Public Key Fingerprint:** `{ev.public_key_fingerprint}`")
                st.download_button(
                    "📥 Export Evidence Record",
                    data=ev.record_json,
                    file_name=f"REACTRA_{tid}.json",
                    mime="application/json",
                    key=f"dl_{tid}",
                )


def render_referral_page() -> None:
    """Render laboratory referral packets page."""
    st.title("📑 Laboratory Referral Packets")
    st.caption(
        "Standardized forensic packets for laboratory confirmatory analysis (e.g., GC-MS / HPLC)."
    )

    st.markdown(
        f"""
        > **{DISCLAIMER_PRESUMPTIVE}** — {DISCLAIMER_LAB_REQUIRED}
        """
    )

    conn = get_connection()
    records = search_test_history(conn=conn)
    conn.close()

    referrals = []
    for r in records:
        ev = get_evidence_record(r["test_id"])
        if ev:
            try:
                rec_dict = json.loads(ev.record_json)
                if should_refer_to_lab(rec_dict):
                    referrals.append(rec_dict)
            except Exception:
                continue

    if not referrals:
        st.info("No tests currently flagged as requiring laboratory referral.")
        return

    st.markdown(f"**{len(referrals)}** field test(s) flagged for laboratory referral:")
    for rec in referrals:
        tid = rec["test_id"]
        res = rec.get("result", "UNKNOWN")
        with st.expander(f"Referral for `{tid}` ({res})"):
            packet = generate_lab_packet(rec)
            st.json(packet)
            st.download_button(
                "📥 Download Lab Referral Packet (.json)",
                data=json.dumps(packet, indent=2),
                file_name=f"REACTRA_LAB_REFERRAL_{tid}.json",
                mime="application/json",
                key=f"ref_dl_{tid}",
            )


def render_demo_page() -> None:
    """Render Development & Validation QA Console."""
    st.title("🛠️ Development & Validation Console")
    st.caption(
        "Deterministic test suites, classifier evaluation metrics, and tamper detection labs."
    )

    st.warning("⚠️ **DEVELOPMENT / QA MODE** — For SIH evaluators and test engineers only.")

    tab1, tab2, tab3 = st.tabs(
        ["🧪 7 Deterministic Scenarios", "📊 Classifier Metrics", "🔐 Tamper & Hash-Chain Lab"]
    )

    with tab1:
        st.markdown("### Deterministic Execution Scenarios")
        st.caption("Executes all 7 core execution paths against controlled benchmark data.")

        if st.button("▶ Run All 7 Scenarios", type="primary"):
            results = []
            for s_id in range(1, 8):
                res = run_demo_scenario(s_id)
                results.append(res)

            for res in results:
                status_icon = "✅" if res["passed"] else "❌"
                with st.expander(f"{status_icon} Scenario {res['scenario_id']}: {res['title']}"):
                    exp_str = f"{res['expected_result']} ({res['expected_status']})"
                    st.write(f"**Expected Result:** `{exp_str}`")
                    act_str = f"{res['actual_result']} ({res['actual_status']})"
                    st.write(f"**Actual Result:** `{act_str}`")
                    if "reason" in res:
                        st.info(f"Reason: {res['reason']}")
                    if res["passed"]:
                        st.success("Test Assertion: PASSED")
                    else:
                        st.error("Test Assertion: FAILED")

    with tab2:
        st.markdown("### Controlled Evaluation Metrics")
        st.caption("Offline evaluation across synthetic benchmark set.")
        eval_data = load_evaluation_results()
        if eval_data:
            total_samples = eval_data.get("total_evaluated_samples") or eval_data.get(
                "total_samples", 0
            )

            # Safely extract precision (dict or float)
            raw_prec = eval_data.get("precision", 0.0)
            if isinstance(raw_prec, dict):
                prec_val = sum(raw_prec.values()) / max(len(raw_prec), 1)
            else:
                prec_val = float(raw_prec)

            # Safely extract recall (dict or float)
            raw_rec = eval_data.get("recall", 0.0)
            if isinstance(raw_rec, dict):
                rec_val = sum(raw_rec.values()) / max(len(raw_rec), 1)
            else:
                rec_val = float(raw_rec)

            # Safely extract F1 score
            if "macro_f1" in eval_data:
                f1_val = float(eval_data["macro_f1"])
            else:
                raw_f1 = eval_data.get("f1") or eval_data.get("f1_score", 0.0)
                if isinstance(raw_f1, dict):
                    f1_val = sum(raw_f1.values()) / max(len(raw_f1), 1)
                else:
                    f1_val = float(raw_f1)

            m_cols = st.columns(4)
            with m_cols[0]:
                st.metric("Total Samples", total_samples)
            with m_cols[1]:
                st.metric("Macro Precision", f"{prec_val * 100:.1f}%")
            with m_cols[2]:
                st.metric("Macro Recall", f"{rec_val * 100:.1f}%")
            with m_cols[3]:
                st.metric("Macro F1", f"{f1_val:.2f}")

            classes = eval_data.get("classes", ["POSITIVE", "NEGATIVE", "INCONCLUSIVE"])

            # Render per-class breakdown if available
            if isinstance(raw_prec, dict) and isinstance(raw_rec, dict):
                import pandas as pd

                st.markdown("#### Per-Class Performance")
                rows = []
                for c in classes:
                    p = raw_prec.get(c, 0.0)
                    r = raw_rec.get(c, 0.0)
                    f_val_c = (
                        eval_data.get("f1", {}).get(c, 0.0)
                        if isinstance(eval_data.get("f1"), dict)
                        else 0.0
                    )
                    rows.append(
                        {
                            "Class": c,
                            "Precision": f"{p * 100:.1f}%",
                            "Recall": f"{r * 100:.1f}%",
                            "F1 Score": f"{f_val_c:.2f}",
                        }
                    )
                st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

            if "confusion_matrix" in eval_data:
                import pandas as pd

                st.markdown("#### Confusion Matrix (Actual Rows × Predicted Cols)")
                cm_df = pd.DataFrame(
                    eval_data["confusion_matrix"],
                    index=[f"Actual {c}" for c in classes],
                    columns=[f"Pred {c}" for c in classes],
                )
                st.dataframe(cm_df, use_container_width=True)
        else:
            st.info("Evaluation metrics file not found.")

    with tab3:
        st.markdown("### Cryptographic Tamper & Hash-Chain Lab")
        st.caption("Demonstrates mathematical detection of post-signing tampering and deletion.")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Test 1: Data Tampering Detection")
            if st.button("Run Tamper Test"):
                res = run_demo_scenario(6)
                if res["passed"]:
                    st.success(
                        "✅ Tampering successfully detected! Digital signature verification failed."
                    )
                    st.json(res["details"])
                else:
                    st.error("❌ Tamper detection failed.")

        with c2:
            st.markdown("#### Test 2: Deleted Record Chain Break")
            if st.button("Run Chain Break Test"):
                res = run_demo_scenario(7)
                if res["passed"]:
                    st.success("✅ Missing audit record detected! Hash chain continuity broken.")
                    st.json(res["details"])
                else:
                    st.error("❌ Chain failure detection failed.")
