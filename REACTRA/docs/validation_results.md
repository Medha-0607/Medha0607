# REACTRA — Comprehensive Validation & Acceptance Test Results

**Date of Execution:** September 21, 2026  
**Problem Statement:** SIH26231 — Digital Companion for Field Drug Testing  
**Evaluation Environment:** Python 3.11.9 (Windows 11, `win32`), Pytest 9.1.1, Streamlit 1.32+  
**Benchmark Dataset:** 17 Controlled Synthetic Benchmark Field Images  

---

## 1. Automated Acceptance Test Matrix

| Case ID | Scenario / Condition | Expected Outcome | Actual Observed Outcome | Quality Gate | Classification | Assertion |
|---|---|---|---|---|---|---|
| **A** | Good Positive-like Capture | `POSITIVE` + `READY` | `POSITIVE` + `READY` | `VALID` | `POSITIVE` (score: 0.96) | **PASS** |
| **B** | Good Negative-like Capture | `NEGATIVE` + `READY` | `NEGATIVE` + `READY` | `VALID` | `NEGATIVE` (score: 0.96) | **PASS** |
| **C** | Ambiguous Reagent Reaction | `INCONCLUSIVE` + `REVIEW` | `INCONCLUSIVE` + `REVIEW` | `VALID` | `INCONCLUSIVE` (score: 0.98) | **PASS** |
| **D** | Motion Blur Edge Case | `RECAPTURE_REQUIRED` | `RECAPTURE_REQUIRED` | `RECAPTURE` (Var: 1.0 < 80) | `None` (Blocked) | **PASS** |
| **E** | Overexposure / Specular Glare | `RECAPTURE_REQUIRED` | `RECAPTURE_REQUIRED` | `RECAPTURE` (90.9% glare) | `None` (Blocked) | **PASS** |
| **F** | Missing Reference Card | `RECAPTURE_REQUIRED` | `RECAPTURE_REQUIRED` | `RECAPTURE` (No card) | `None` (Blocked) | **PASS** |
| **G** | Calibration Residual Failure | `REVIEW` / `RECAPTURE` | `REVIEW` (ΔE 12.59 > 8.0) | `REVIEW` | `None` (Blocked) | **PASS** |
| **H** | Tampered Evidence Record | `INTEGRITY_VERIFICATION_FAILED` | `INTEGRITY_VERIFICATION_FAILED` | N/A | Signature Invalid | **PASS** |
| **I** | Deleted Record in Chain | `CHAIN_VERIFICATION_FAILED` | `CHAIN_VERIFICATION_FAILED` | N/A | Chain Broken at Link #2 | **PASS** |
| **J** | Imported Image Mode | Properly labelled `IMPORTED_IMAGE` | Displayed `IMPORTED IMAGE` | N/A | Recorded in metadata | **PASS** |
| **K** | Live Camera Capture | `LIVE_CAMERA` mode supported | Supported via `st.camera_input` | Active | Streamlit camera API | **PASS** |
| **L** | GPS Unavailable | Clearly labelled `UNAVAILABLE` | Displayed `GPS: UNAVAILABLE` | N/A | Zero fabricated coords | **PASS** |
| **M** | Manual Demo Location | Explicit `MANUAL_DEMO` label | Displayed `MANUAL DEMO LOCATION`| N/A | Explicitly tagged | **PASS** |

---

## 2. Quantitative Performance Metrics

### 2.1 Pre-Classification Quality Gate
- **Total Benchmark Tests:** 17
- **Clean Captures Passing Gate:** 15 (88.2%)
- **Motion-Blurred Captures Rejected:** 1 (100% true rejection rate)
- **Overexposed Glare Captures Rejected:** 1 (100% true rejection rate)
- **Zero Classifier Invocations on Hard Failures:** Confirmed (100% compliance with critical safety rule).

### 2.2 Colorimetric Classification (Controlled Synthetic Set)
- **Positive Support:** 5
- **Negative Support:** 5
- **Inconclusive Support:** 5
- **Macro Precision:** 1.00
- **Macro Recall:** 1.00
- **Macro F1 Score:** 1.00
- **Centroid Decision Margin Margin:** $\ge 12.00$ $\Delta E$ separation required for conclusive state.

### 2.3 Cryptographic Verification
- **Valid Ed25519 Signatures Verified:** 100% (Pass)
- **Tampered Payload Detection Rate:** 100% (Preimage and signature failure)
- **Missing / Deleted Chain Link Detection:** 100% (Hash continuity failure)
- **Reordered Record Chain Detection:** 100% (Hash continuity failure)

---

## 3. Automated Test Suite Summary
- **Total Test Cases:** 45
- **Passed:** 45
- **Failed:** 0
- **Execution Time:** ~1.43 seconds
- **Lint / Code Quality:** 0 errors across `src/`, `app.py`, `scripts/`, and `tests/` (`ruff check`).
