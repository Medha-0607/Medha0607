"""Deterministic demo scenarios demonstrating all 7 core RECTRA execution paths.

Cases:
1. Good POSITIVE image -> PRESUMPTIVE POSITIVE (READY)
2. Good NEGATIVE image -> PRESUMPTIVE NEGATIVE (READY)
3. Ambiguous image -> INCONCLUSIVE (REVIEW)
4. Blurred image -> RECAPTURE REQUIRED
5. Overexposed image -> RECAPTURE / REVIEW REQUIRED
6. Tampered evidence record -> INTEGRITY VERIFICATION FAILED
7. Deleted/Broken record in chain -> CHAIN VERIFICATION FAILED
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import cv2
import numpy as np

from rectra.classification.predictor import classify_reaction
from rectra.config import DATA_DIR
from rectra.core.constants import (
    CaptureMode,
    GpsStatus,
    OutcomeClass,
    PassportStatus,
    QualityStatus,
)
from rectra.core.types import CaptureMetadata
from rectra.database.connection import get_connection
from rectra.database.repository import (
    save_evidence_record,
    save_test_session,
)
from rectra.evidence.canonical import build_canonical_record_dict
from rectra.evidence.hashing import compute_record_digest, sha256_bytes
from rectra.evidence.signing import get_public_key_fingerprint, sign_digest
from rectra.evidence.verifier import verify_evidence_record
from rectra.models import EvidenceRecordModel, TestSessionModel
from rectra.profiles.loader import load_profile
from rectra.vision.calibration import calibrate_colours
from rectra.vision.card_detector import CANONICAL_PATCH_BOXES, bgr_to_lab, detect_card
from rectra.vision.quality_gate import evaluate_quality_gate
from rectra.vision.roi_detector import extract_test_roi

logger = logging.getLogger(__name__)


def run_pipeline_on_image(
    image_bgr: np.ndarray,
    operator_id: str = "DEMO-OP",
    latitude: float | None = None,
    longitude: float | None = None,
    gps_status: GpsStatus | str = GpsStatus.UNAVAILABLE,
    capture_mode: CaptureMode | str = CaptureMode.IMPORTED_IMAGE,
    profile_id: str | None = None,
    profile_version: str | None = None,
) -> dict[str, Any]:
    """Execute full vertical pipeline on an image with strict pre-classification gating."""
    profile = load_profile(profile_id, profile_version)
    raw_bytes = cv2.imencode(".png", image_bgr)[1].tobytes()
    img_sha = sha256_bytes(raw_bytes)

    meta = CaptureMetadata(
        capture_mode=capture_mode,
        timestamp_utc="2026-09-20T12:00:00Z",
        operator_id=operator_id,
        latitude=latitude,
        longitude=longitude,
        gps_status=gps_status if latitude is not None else GpsStatus.UNAVAILABLE,
        profile_id=profile["profile_id"],
        profile_version=profile["profile_version"],
    )

    card_res = detect_card(image_bgr, profile)
    calib_res = None
    roi_res = None
    class_res = None

    if card_res.detected and card_res.warped_image is not None:
        roi_res = extract_test_roi(card_res.warped_image, profile)

        # Extract reference patches
        observed: dict[str, tuple[float, float, float]] = {}
        for name, box in CANONICAL_PATCH_BOXES.items():
            bx, by, bw, bh = box
            patch_crop = card_res.warped_image[by + 15 : by + bh - 15, bx + 15 : bx + bw - 15]
            mb = float(np.mean(patch_crop[:, :, 0]))
            mg = float(np.mean(patch_crop[:, :, 1]))
            mr = float(np.mean(patch_crop[:, :, 2]))
            observed[name] = bgr_to_lab((mb, mg, mr))

        if roi_res.is_valid:
            calib_res = calibrate_colours(observed, profile, roi_res.mean_lab)

    # 1. EVALUATE QUALITY GATE
    q_gate = evaluate_quality_gate(image_bgr, card_res, calib_res, roi_res, profile)

    # 2. STRICT PRE-CLASSIFICATION GATE:
    # If quality gate status is RECAPTURE or REVIEW, STOP! The classifier must NEVER run!
    if (
        q_gate.status == QualityStatus.VALID
        and calib_res is not None
        and profile.get("is_calibrated", True)
        and profile.get("class_centroids_lab")
    ):
        class_res = classify_reaction(calib_res.corrected_test_colour_lab, profile)

    # Determine overall status
    if q_gate.status == QualityStatus.RECAPTURE:
        overall_status = PassportStatus.RECAPTURE
    elif q_gate.status == QualityStatus.REVIEW or (
        class_res and class_res.result == OutcomeClass.INCONCLUSIVE
    ):
        overall_status = PassportStatus.REVIEW
    else:
        overall_status = PassportStatus.READY

    return {
        "metadata": meta,
        "image_sha256": img_sha,
        "card_detection": card_res,
        "roi": roi_res,
        "calibration": calib_res,
        "quality_gate": q_gate,
        "classification": class_res,
        "overall_status": overall_status,
    }


def run_demo_scenario(scenario_id: int) -> dict[str, Any]:
    """Run one of the 7 deterministic demonstration scenarios."""
    demo_dir = DATA_DIR / "demo"

    if scenario_id == 1:
        # Case 1: Good Positive
        img_path = demo_dir / "positive" / "DEMO-POS-001.png"
        img = cv2.imread(str(img_path))
        pipeline = run_pipeline_on_image(img, operator_id="OP-SCENARIO-1")
        return {
            "scenario_id": 1,
            "title": "Good Positive Field Capture",
            "expected_result": "POSITIVE",
            "actual_result": str(pipeline["classification"].result)
            if pipeline["classification"]
            else "RECAPTURE_REQUIRED",
            "expected_status": "READY",
            "actual_status": str(pipeline["overall_status"]),
            "passed": (
                pipeline["classification"] is not None
                and pipeline["classification"].result == OutcomeClass.POSITIVE
                and pipeline["overall_status"] == PassportStatus.READY
            ),
            "details": pipeline,
        }

    elif scenario_id == 2:
        # Case 2: Good Negative
        img_path = demo_dir / "negative" / "DEMO-NEG-001.png"
        img = cv2.imread(str(img_path))
        pipeline = run_pipeline_on_image(img, operator_id="OP-SCENARIO-2")
        return {
            "scenario_id": 2,
            "title": "Good Negative Field Capture",
            "expected_result": "NEGATIVE",
            "actual_result": str(pipeline["classification"].result)
            if pipeline["classification"]
            else "RECAPTURE_REQUIRED",
            "expected_status": "READY",
            "actual_status": str(pipeline["overall_status"]),
            "passed": (
                pipeline["classification"] is not None
                and pipeline["classification"].result == OutcomeClass.NEGATIVE
                and pipeline["overall_status"] == PassportStatus.READY
            ),
            "details": pipeline,
        }

    elif scenario_id == 3:
        # Case 3: Ambiguous Inconclusive
        img_path = demo_dir / "inconclusive" / "DEMO-INC-001.png"
        img = cv2.imread(str(img_path))
        pipeline = run_pipeline_on_image(img, operator_id="OP-SCENARIO-3")
        return {
            "scenario_id": 3,
            "title": "Ambiguous Reagent Reaction",
            "expected_result": "INCONCLUSIVE",
            "actual_result": str(pipeline["classification"].result)
            if pipeline["classification"]
            else "RECAPTURE_REQUIRED",
            "expected_status": "REVIEW",
            "actual_status": str(pipeline["overall_status"]),
            "passed": (
                pipeline["classification"] is not None
                and pipeline["classification"].result == OutcomeClass.INCONCLUSIVE
                and pipeline["overall_status"] == PassportStatus.REVIEW
            ),
            "details": pipeline,
        }

    elif scenario_id == 4:
        # Case 4: Motion Blurred Capture
        img_path = demo_dir / "edge_cases" / "DEMO-EDGE-BLURRED.png"
        img = cv2.imread(str(img_path))
        pipeline = run_pipeline_on_image(img, operator_id="OP-SCENARIO-4")
        return {
            "scenario_id": 4,
            "title": "Motion-Blurred Field Capture",
            "expected_result": "RECAPTURE_REQUIRED",
            "actual_result": "RECAPTURE_REQUIRED"
            if pipeline["classification"] is None
            else str(pipeline["classification"].result),
            "expected_status": "RECAPTURE_REQUIRED",
            "actual_status": "RECAPTURE_REQUIRED"
            if pipeline["overall_status"] == PassportStatus.RECAPTURE
            else str(pipeline["overall_status"]),
            "passed": (
                pipeline["quality_gate"].status == QualityStatus.RECAPTURE
                and pipeline["classification"] is None
            ),
            "details": pipeline,
            "reason": "Blur score below configured threshold: "
            + "; ".join(pipeline["quality_gate"].reasons),
        }

    elif scenario_id == 5:
        # Case 5: Overexposed Glare Capture
        img_path = demo_dir / "edge_cases" / "DEMO-EDGE-OVEREXPOSED.png"
        img = cv2.imread(str(img_path))
        pipeline = run_pipeline_on_image(img, operator_id="OP-SCENARIO-5")
        return {
            "scenario_id": 5,
            "title": "Overexposed / Specular Glare Capture",
            "expected_result": "RECAPTURE_REQUIRED",
            "actual_result": "RECAPTURE_REQUIRED"
            if pipeline["classification"] is None
            else str(pipeline["classification"].result),
            "expected_status": "RECAPTURE_REQUIRED",
            "actual_status": "RECAPTURE_REQUIRED"
            if pipeline["overall_status"] == PassportStatus.RECAPTURE
            else str(pipeline["overall_status"]),
            "passed": (
                pipeline["quality_gate"].status == QualityStatus.RECAPTURE
                and pipeline["classification"] is None
            ),
            "details": pipeline,
            "reason": "Excessive specular glare / saturation above threshold: "
            + "; ".join(pipeline["quality_gate"].reasons),
        }

    elif scenario_id == 6:
        # Case 6: Tampered Evidence Record
        test_id = str(uuid.uuid4())
        rec = build_canonical_record_dict(
            test_id=test_id,
            operator_id="OFFICER-44",
            capture_mode="LIVE_CAMERA",
            timestamp_utc="2026-09-20T12:00:00Z",
            latitude=13.0827,
            longitude=80.2707,
            gps_status="MANUAL_DEMO",
            profile_id="DEMO-ASSAY-001",
            profile_version="1.0",
            reference_card_version="1.0",
            algorithm_version="reactra-algo-v0.1",
            model_version="reactra-model-v0.1",
            result="POSITIVE",
            classification_score=0.91,
            measurement_quality="VALID",
            quality_gate_status="VALID",
            image_sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        )
        digest = compute_record_digest(rec)
        sig = sign_digest(digest)
        fp = get_public_key_fingerprint()

        rec["record_digest"] = digest
        rec["signature"] = sig
        rec["public_key_fingerprint"] = fp

        # Tamper with one field: modify presumptive result from POSITIVE to NEGATIVE!
        tampered_rec = dict(rec)
        tampered_rec["result"] = "NEGATIVE"

        is_valid, reason = verify_evidence_record(tampered_rec)
        return {
            "scenario_id": 6,
            "title": "Tampered Evidence Record (Result Changed Post-Signing)",
            "expected_result": "INTEGRITY VERIFICATION FAILED",
            "actual_result": "RECORD VERIFIED" if is_valid else "INTEGRITY VERIFICATION FAILED",
            "expected_status": "TAMPER_DETECTED",
            "actual_status": "FAILED" if not is_valid else "PASSED",
            "passed": (is_valid is False),
            "details": {"reason": reason, "tampered_field": "result: POSITIVE -> NEGATIVE"},
        }

    elif scenario_id == 7:
        # Case 7: Broken / Tampered Evidence Chain
        # Create an in-memory database with 3 chained records, then delete record #2
        conn = get_connection(":memory:")
        from rectra.database.schema import create_tables

        create_tables(conn)

        prev_hash = None
        test_ids = []
        for i in range(3):
            tid = f"CHAIN-TEST-{i + 1}"
            test_ids.append(tid)
            sess = TestSessionModel(
                test_id=tid,
                operator_id=f"OP-{i + 1}",
                capture_mode="IMPORTED_IMAGE",
                timestamp_utc=f"2026-09-20T10:0{i}:00Z",
                latitude=None,
                longitude=None,
                gps_status="UNAVAILABLE",
                profile_id="DEMO-ASSAY-001",
                profile_version="1.0",
                result="POSITIVE",
                quality_gate_status="VALID",
            )
            save_test_session(sess, conn=conn)

            rec = build_canonical_record_dict(
                test_id=tid,
                operator_id=f"OP-{i + 1}",
                capture_mode="IMPORTED_IMAGE",
                timestamp_utc=f"2026-09-20T10:0{i}:00Z",
                latitude=None,
                longitude=None,
                gps_status="UNAVAILABLE",
                profile_id="DEMO-ASSAY-001",
                profile_version="1.0",
                reference_card_version="1.0",
                algorithm_version="rectra-algo-v0.1",
                model_version="rectra-model-v0.1",
                result="POSITIVE",
                classification_score=0.9,
                measurement_quality="VALID",
                quality_gate_status="VALID",
                image_sha256=f"hash-{i}",
                previous_record_hash=prev_hash,
            )
            dig = compute_record_digest(rec)
            sig = sign_digest(dig)
            fp = get_public_key_fingerprint()

            rec["record_digest"] = dig
            rec["signature"] = sig
            rec["public_key_fingerprint"] = fp

            ev = EvidenceRecordModel(
                test_id=tid,
                record_json=json.dumps(rec),
                record_digest=dig,
                signature=sig,
                public_key_fingerprint=fp,
                image_sha256=f"hash-{i}",
                previous_record_hash=prev_hash,
            )
            save_evidence_record(ev, conn=conn)
            prev_hash = dig

        # Delete middle record (CHAIN-TEST-2)
        with conn:
            conn.execute("DELETE FROM evidence_records WHERE test_id = 'CHAIN-TEST-2'")

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence_records ORDER BY rowid ASC")
        recs = cursor.fetchall()
        p_hash = None
        chain_broken = False
        broken_id = None
        for idx, r in enumerate(recs):
            if idx == 0 and r["previous_record_hash"] is not None:
                chain_broken = True
                broken_id = r["test_id"]
                break
            elif idx > 0 and r["previous_record_hash"] != p_hash:
                chain_broken = True
                broken_id = r["test_id"]
                break
            p_hash = r["record_digest"]

        conn.close()

        return {
            "scenario_id": 7,
            "title": "Deleted Record in Audit Chain (Chain Continuity Break)",
            "expected_result": "CHAIN VERIFICATION FAILED",
            "actual_result": "CHAIN VERIFICATION FAILED" if chain_broken else "CHAIN INTACT",
            "expected_status": "BROKEN_CHAIN_DETECTED",
            "actual_status": "BROKEN" if chain_broken else "INTACT",
            "passed": chain_broken,
            "details": {"broken_at_test_id": broken_id, "deleted_record": "CHAIN-TEST-2"},
        }

    else:
        raise ValueError(f"Unknown scenario ID: {scenario_id} (valid: 1 to 7)")
