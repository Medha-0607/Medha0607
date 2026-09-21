# RECTRA — Step-by-Step Evaluator Demo Flow

This document provides an exact, reproducible sequence of actions for demonstrating RECTRA during an interactive evaluation session.

---

## Pre-Demo Checklist (1 Minute Before Start)
1. Open terminal in project root: `c:\Users\deena\REACTRA`.
2. Verify virtual environment is active: `python --version` (should be Python 3.11).
3. Ensure test suite is passing: `python -m pytest` (37 passed).
4. Launch Streamlit app: `streamlit run app.py` (opens `http://localhost:8501`).

---

## Interactive Demonstration Steps

### Step 1: Landing Page & Architectural Overview
- **Action:** Point evaluators to the Home page.
- **Narrative:** Highlight the 5-step pipeline (`Capture → Calibrate → Validate → Classify → Preserve`). Point out the non-negotiable safety warning at the top of the screen.

### Step 2: Ingestion & Metadata Tagging (New Test Page)
- **Action:** In sidebar, select **NEW TEST**.
- **Input:**
  - Operator ID: `DET-SHARMA-402`
  - DEMO LOCATION: `28.6139, 77.2090` (New Delhi)
  - Image Source: File Upload ➔ Select `data/demo/positive/DEMO-POS-001.png`.
- **Click:** "Run Calibration & Analysis Pipeline".

### Step 3: Diagnostics & Physical Quality Gate (Analysis Page)
- **Action:** App automatically transitions to **ANALYSIS**.
- **Show Evaluators:**
  - *Reference Card Localization:* 4 corner square fiducials localized, perspective warped to canonical 1000x700 image.
  - *Illumination Calibration:* 6 canonical patches identified, affine matrix computed, mean residual $\Delta E = 1.15$ (well below 8.00 threshold).
  - *Quality Gate Breakdown:* Focus (variance 450+), Exposure (mean ~130), Glare (<1% saturated pixels), ROI (valid).

### Step 4: Result Interpretation & Explainability (Result Page)
- **Action:** In sidebar, select **RESULT**.
- **Show Evaluators:**
  - Mandatory disclaimer: `"PRESUMPTIVE FIELD-TEST RESULT — Laboratory confirmation is required."`
  - Presumptive Result Badge: `PRESUMPTIVE POSITIVE` (Confidence: 96%).
  - Explainable Class Distance Chart: Distance to Positive $\Delta E = 1.20$, Distance to Negative $\Delta E = 32.40$.
- **Click:** "Preserve Evidence Record & Append to Local Chain".
- **Show Reliability Passport:** 4 complete audit sections rendered with overall status `READY`.

### Step 5: Handling Corrupted Data (Blur & Glare)
- **Action:** Go to sidebar ➔ **DEMO / VALIDATION** ➔ Tab 1.
- **Run Scenario #4 (Motion Blur):**
  - Result: `RECAPTURE REQUIRED`. Show that classifier is blocked — RECTRA refuses to produce false positives on degraded data.
- **Run Scenario #5 (Glare):**
  - Result: `RECAPTURE / REVIEW`. Show that saturated specular reflections over 5% trigger safety review.

### Step 6: Handling Ambiguous Reagents (Inconclusive & Referral)
- **Action:** Run Scenario #3 (Ambiguous Reagent).
- **Show Evaluators:**
  - Result: `INCONCLUSIVE (REVIEW)` because distance difference is below margin threshold ($< 12.00$).
  - Navigate to **REFERRAL** page:
  - Show generated `RECTRA_REFERRAL_*.json` and formatted `.html` report.
  - Show rendered HTML report preview with safety disclaimers and laboratory submission section.

### Step 7: Cryptographic Tamper Detection & Audit Chain
- **Action:** Navigate to **EVIDENCE** page.
- **Tab 1 (Active Envelope):** Download `RECTRA_EVIDENCE_*.json`.
- **Action:** Open downloaded file in text editor, modify `"result": "POSITIVE"` to `"result": "NEGATIVE"`, and save.
- **Tab 2 (Verify Envelope):** Upload the modified file.
- **System Response:** Instant red alert: `❌ INTEGRITY VERIFICATION FAILED: Record content does not match canonical digest. One or more fields have been altered.`
- **Tab 3 (Audit Chain):** Click "Run Chain Verification".
- **System Response:** `✅ CHAIN INTACT: Tamper-evident local evidence chain is intact (5 records verified).`

### Step 8: Searchable Test Log (Test History Page)
- **Action:** Navigate to **TEST HISTORY**.
- **Filter:** Type operator query `SHARMA` or filter by result `POSITIVE`.
- **Click:** "View Passport" on any record to view its full 4-section modal breakdown.
