# REACTRA — Field Operator Workflow Specification

**Problem Statement:** SIH26231 — Digital Companion for Field Drug Testing  
**Project:** REACTRA (Reaction-Aware Field Testing & Verifiable Evidence)  

---

## 1. Overview

The primary field user experience of REACTRA is designed for law enforcement officers, forensic field technicians, and checkpoint screeners operating in high-stress, variable-lighting environments. The interface eliminates cluttered developer toggles in favor of a sequential, 6-step guided wizard.

---

## 2. The 6-Step Field Operator Workflow

```
[1. SETUP] ➔ [2. CAPTURE] ➔ [3. CHECK] ➔ [4. RESULT] ➔ [5. EVIDENCE] ➔ [6. COMPLETE]
```

### Step 1: Start New Field Test (Setup)
- **Operator Credentials:** Officer enters a verified Operator/Terminal ID (minimum 3 characters).
- **Assay Reagent Profile:** Officer selects the chemical test kit in use (e.g. `DEMO-ASSAY-001`, `MARQUIS-001`, or `SCOTT-001`).
  - *Safety Guard:* If an uncalibrated profile is chosen, the system displays `"⚠️ This profile requires physical calibration before use"` and disables execution.
- **Capture Method:** Officer declares whether imagery is acquired via `LIVE CAMERA` or `IMPORT IMAGE`.
- **Geolocation Mode:** Clearly labelled as `GPS_DEVICE` (if browser geolocation is available) or `UNAVAILABLE` / `MANUAL_DEMO`. Coordinates are never fabricated.

### Step 2: Image Capture & Ingestion
- **Live Device Camera:** Displays framing guide indicating reference card perimeter and center reaction target.
- **Image Import:** File uploader alongside One-Click Benchmark Sample Selector for immediate verification.
- **Import Badge:** Displays prominent warning: `⚠️ IMPORT MODE: This image was not captured through the live camera workflow.`
- **Instant Card Check:** Performs rapid quadrilateral detection, verifying card visibility before proceeding.

### Step 3: Measurement Check (Readiness Gate)
*Crucial Safety Invariant:* The classifier NEVER runs before measurement readiness is verified.
- **Evaluates:**
  - High-frequency blur variance (Laplacian $\ge 80.0$).
  - Exposure luminance bounds ($50 \le \bar{Y} \le 220$).
  - Specular glare saturation fraction ($\le 5.0\%$).
  - 4-point reference card geometric confidence.
  - Test reaction ROI pixel sufficiency ($\ge 500$ pixels).
- **Outcomes:**
  - `READY FOR ANALYSIS`: Advances to interpretation.
  - `RECAPTURE REQUIRED`: Hard optical failure. Classification is strictly blocked. Provides actionable guidance (e.g., *"Adjust lighting to reduce specular glare and hold camera steady"*).
  - `REVIEW REQUIRED`: Ambiguous optical variance.

### Step 4: Presumptive Result & Visual Explanation
- Displays presumptive classification: `POSITIVE`, `NEGATIVE`, or `INCONCLUSIVE`.
- **Mandatory Disclaimers:**
  - `PRESUMPTIVE FIELD-TEST RESULT — Laboratory confirmation is required.`
- **Visual Explanation Layer:**
  - Overlaid image showing normalized card borders, 6 reference patch locations (green), and reaction target ROI (cyan).
  - CIE Lab colour comparison table (measured test colour vs nominal centroids).
  - Nearest-centroid distance scoring with decision separation margin.

### Step 5: Digital Evidence & Reliability Passport
- Renders the 4-quadrant **Field Test Reliability Passport**:
  - `CAPTURE`: Mode, UTC timestamp, Operator ID, Geolocation status.
  - `MEASUREMENT`: Card detection, Profile ID/version, Calibration status, Residual $\Delta E$, Quality gate status.
  - `CLASSIFICATION`: Presumptive result, Proxy score, Model/Algorithm versions.
  - `EVIDENCE`: Image SHA-256 digest, Record digest, Ed25519 signature status, Hash-chain link.
- **Preservation Action:** `[🔒 Sign & Seal in Local Evidence Chain]` computes canonical JSON digest, signs with Ed25519, and links to previous record hash.

### Step 6: Complete & Export
- Confirms evidence sealing and local audit chain commitment.
- Export options:
  - Download Evidence Envelope (`.json`).
  - Download Evidence Report (`.html`).
  - Download Lab Referral Packet (`.json`) for inconclusive, review, or failed tests.
- Action: `[Start Another Field Test]` resets state machine to Step 1.
