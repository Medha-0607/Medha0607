# REACTRA — Current State Architecture & Quality Audit

**Document Date:** September 21, 2026  
**Problem Statement:** SIH26231 — Digital Companion for Field Drug Testing  
**Project Identity:** REACTRA (Reaction-Aware Field Testing & Verifiable Evidence)  
**Inspection Target:** RECTRA/REACTRA Local Codebase  

---

## 1. Executive Summary

This audit represents the mandatory initial inspection of the existing codebase prior to executing the master rebuild and hardening refactor. The codebase contains a solid, mathematically sound, and tested foundation in core computer vision, asymmetric cryptography, and database persistence (37 passing automated tests). However, critical usability, workflow state consistency, quality-gate gating, and branding flaws must be resolved to achieve full compliance with SIH 2026 standards.

---

## 2. Git & Environment Inspection

- **Git Root:** `C:/Users/deena` (parent workspace root contains staged deletions of previous project; `REACTRA` is located at `c:\Users\deena\REACTRA`).
- **Active Branch:** `main`
- **Remote Origin:** `https://github.com/Medha-0607/Medha0607.git`
- **Python Environment:** Python 3.11.9 on Windows 11 (`win32`).
- **Runtime Dependencies:** Streamlit, OpenCV (`opencv-python-headless`), NumPy, Pandas, scikit-learn, Pillow, Cryptography (Ed25519), QRCode.
- **Test Status:** 37/37 pytest tests passing; 0 ruff lint errors.
- **Runtime Service:** Streamlit server running on `http://localhost:8501`.

---

## 3. Detailed Component Audit

### 3.1 What Currently Works
- **Cryptographic Evidence Engine (`src/rectra/evidence/`):**
  - Real Ed25519 signing and verification with zero cloud dependency.
  - Deterministic JCS-compliant canonical JSON formatting (`json-sort-keys-compact-utf8-v1`).
  - Public key fingerprinting (`SHA256:<hex>`).
- **Tamper-Evident Local Evidence Chain (`src/rectra/evidence/chain.py`):**
  - Cryptographic hash chaining incorporating `previous_record_hash`.
  - `verify_chain()` rigorously detects modified records, deleted records, and ordering corruptions.
- **Evidence Envelope Packaging (`src/rectra/evidence/envelope.py`):**
  - Portable, self-contained JSON evidence envelope containing test payload, signature, and verification headers.
- **SQLite Database Architecture (`src/rectra/database/`):**
  - Clean repository pattern isolating SQL from UI.
  - Normalized tables: `test_sessions`, `evidence_records`, `assay_profiles`, `audit_chain`.
- **Vision Pipeline (`src/rectra/vision/`):**
  - Reference card detection using ArUco + geometric contour quadrilateral fallback with 4-point perspective warp.
  - Least-squares affine CIE Lab colour calibration across 6 reference swatches with measured residual $\Delta E_{76}$.
  - Test ROI extraction and pixel sufficiency checks.
- **Classifier (`src/rectra/classification/`):**
  - Nearest-centroid in CIE Lab space with explicit `INCONCLUSIVE` margin thresholding.
- **Referral Generation (`src/rectra/referral/`):**
  - Automated generation of structured lab referral packets for inconclusive, review, or failed tests.

### 3.2 What Partially Works
- **Session Lifecycle & Navigation:**
  - Tests run through the pipeline, but active state is stored in an ephemeral `st.session_state["active_test"]`. When the user navigates across sidebar stages or refreshes the page, the state can be lost, showing: *"No active test session."*
- **Quality Gate Integration:**
  - Blur, underexposure, card absence, and ROI loss trigger `RECAPTURE`; however, overexposure and glare currently trigger `REVIEW`, and `run_pipeline_on_image` was still invoking the classifier for `REVIEW` states instead of strictly halting.
- **Demonstration Scenarios (`src/rectra/demo/scenarios.py`):**
  - Scenarios 1-3, 6, 7 pass correctly.
  - Scenarios 4 and 5 had flawed or contradictory test oracles (e.g. Expected `"NONE (Quality Gate Failure)"` vs Actual `"POSITIVE"`, yet passing).

### 3.3 What is UI-Only or Misleading
- **Device & Location Placeholders:**
  - Device info displayed `"Handheld Field Terminal (Prototype)"` without querying real user-agent/browser environment.
  - Manual demo coordinates were displayed with fixed defaults (19.0760, 72.8777) instead of explicitly stating `GPS: UNAVAILABLE` when device geolocation is absent.
- **Validation Oracle Labeling:**
  - The validation console displayed `"NONE"` as an expected outcome string instead of explicit typed statuses (`RECAPTURE_REQUIRED`, `REVIEW`, etc.).

### 3.4 What is Broken
- **Classifier Gating Violation:**
  - In `run_pipeline_on_image`, calibration and ROI detection were executed prior to evaluating image validity, and classification was not blocked on hard quality failures. The pipeline rule must be: `CAPTURE -> QUALITY GATE -> IF FAIL: STOP -> CALIBRATE -> CLASSIFY`.
- **Active Session Loss:**
  - Inability to recover active test sessions across navigation or browser reloads.
- **Branding & Naming:**
  - Legacy name `RECTRA` is used throughout codebase, UI, configs, and documentation instead of official `REACTRA`.

### 3.5 What Can Be Reused Without Modification
- Cryptographic signing, hashing, and verification primitives.
- Card detection and perspective transformation algorithms.
- CIE Lab calibration matrix calculation.
- Database schema and repository query functions.
- PDF and PNG reference card generation scripts.

### 3.6 What Must Be Rewritten / Redesigned
1. **Primary Operator UX:**
   - Transition from a disjointed developer console sidebar (`NEW TEST`, `ANALYSIS`, `RESULT`, `EVIDENCE`) to a unified, sequential 6-step operator workflow (`NEW TEST` -> `CAPTURE` -> `CHECK` -> `RESULT` -> `EVIDENCE` -> `COMPLETE`).
   - Move validation, developer tools, and tamper demos into a distinct `VALIDATION / QA MODE`.
2. **Session Manager & Lifecycle:**
   - Explicit lifecycle state machine (`DRAFT`, `CAPTURED`, `ANALYZING`, `VALIDATION_FAILED`, `READY_FOR_CLASSIFICATION`, `CLASSIFIED`, `EVIDENCE_SEALED`, `REVIEW_REQUIRED`, `REFERRAL_REQUIRED`, `COMPLETED`).
   - Persistent session recovery from SQLite.
3. **Quality Gate & Pipeline Sequence:**
   - Enforce pre-classification gate: hard failure immediately blocks classification.
   - Refactor test oracles in `scenarios.py` to use typed statuses without `NONE`.
4. **Project-Wide Renaming:**
   - Complete migration from `RECTRA` to `REACTRA` across UI, configs, tests, documentation, and package metadata.

### 3.7 What Must Be Deferred
- **Temporal Reaction Analysis (Video $\Delta E(t)$):** Deferred to P2 research roadmap (documented with clean theoretical interface).
- **Physical Chemistry Centroids for Marquis & Scott:** Remain staged with `null` centroids and mandatory calibration warnings until real physical spectrometry data is gathered.
- **Cloud/Blockchain Adapters:** Anti-patterns not permitted under offline-first requirement.

---

## 4. Architectural Target State

```
PHYSICAL TEST
      ↓
[1. START NEW TEST] ──> Enter Operator ID, Profile, Capture Mode
      ↓
[2. CAPTURE] ─────────> Live Device Camera / Verified Image Import
      ↓
[3. CHECK] ───────────> Image Quality Gate (Blur, Glare, Exposure, Card)
      │
      ├──> IF FAILED: RECAPTURE_REQUIRED / REVIEW ──> STOP (Classification Blocked)
      │
      └──> IF PASSED: CIE Lab Calibration ──> Nearest-Centroid Classifier
      ↓
[4. RESULT] ──────────> Presumptive Classification + Visual Explanation Layer
      ↓
[5. EVIDENCE] ────────> Reliability Passport + Ed25519 Signature + Hash Chain Seal
      ↓
[6. COMPLETE] ────────> History Archive / Export Package / Lab Referral
```

---

## 5. Next Steps

Proceed immediately with Phase 1 through Phase 10 implementation:
1. Phase 1: Audit completion (this document).
2. Phase 2: Session state & lifecycle machine.
3. Phase 3: Quality gate correctness & validation oracle.
4. Phase 4: Capture/calibration/classification pipeline re-sequencing.
5. Phase 5: Evidence/signature/hash-chain hardening.
6. Phase 6: Redesigned field-operator UX & visual explanation layer.
7. Phase 7: Comprehensive automated testing & security test suite.
8. Phase 8: Complete documentation suite update.
9. Phase 9: Git staging and commit.
10. Phase 10: Remote GitHub push.
