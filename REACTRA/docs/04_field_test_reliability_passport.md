# 04 — Field Test Reliability Passport Specification

## 1. Concept & Purpose

A photograph alone is not reliable legal or operational evidence. Without metadata, calibration data, and validation metrics, an image can be contested or misinterpreted.

The **Field Test Reliability Passport** is a standardized, 4-section diagnostic summary that accompanies every test session. It provides operators, supervisors, and laboratory technicians with immediate transparency into the physical integrity and reliability of the presumptive field test.

---

## 2. The 4 Structured Audit Sections

### Section 1: Capture Metadata
- **Test Session UUID:** Unique identifier generated at ingestion.
- **Timestamp (UTC):** ISO 8601 UTC timestamp.
- **Operator ID:** Identification string of field personnel (minimum 3 characters, audited).
- **Location & GPS Status:** Coordinates labelled explicitly as `GPS_DEVICE`, `MANUAL_DEMO`, or `UNAVAILABLE`.
- **Capture Mode:** `LIVE_CAMERA` or `IMPORTED_IMAGE`.

### Section 2: Measurement Usability & Calibration
- **Card Detection:** Fiducial geometry quality score ($0.0 - 1.0$), reference patch count (6/6).
- **Ambient Calibration:** Least-squares CIE Lab residual error $\Delta E_{76}$ (must be $< 8.00$).
- **Image Validity Gate Breakdown:**
  - *Blur (Focus):* Laplacian variance ($\ge 80.0$).
  - *Exposure:* Mean gray-level luminance ($50 - 220$).
  - *Specular Glare:* Fraction of saturated reflection pixels ($\le 5\%$).
  - *ROI Status:* Bounding integrity and minimum pixel count.

### Section 3: Presumptive Interpretation
- **Target Assay Profile:** Profile ID and Version (e.g. `DEMO-ASSAY-001 v1.0`).
- **Presumptive Classification:** `POSITIVE`, `NEGATIVE`, or `INCONCLUSIVE`.
- **Explainable Class Scores:** Relative distances ($\Delta E$) to class centroids and normalized match confidence.
- **Safety Disclaimers:**
  - `"PRESUMPTIVE FIELD-TEST RESULT"`
  - `"Laboratory confirmation is required."`

### Section 4: Cryptographic Preservation
- **Raw Image SHA-256:** Cryptographic digest of the ingested photo.
- **Canonical Record SHA-256:** Authoritative preimage digest (`json-sort-keys-compact-utf8-v1`).
- **Digital Signature:** Ed25519 signature generated with local hardware key.
- **Public Key Fingerprint:** Truncated SHA-256 fingerprint of the verifying key.
- **Chain Continuity:** Backward-linking hash of the preceding test log entry (`previous_record_hash`).

---

## 3. Overall Reliability Status Badge

The Reliability Passport evaluates all 4 sections to assign a single operational status:

1. **`READY` (Green):** Measurement passed all quality gates, calibration is valid, classification is unambiguous, and evidence is cryptographically signed and chained.
2. **`REVIEW` (Amber):** Borderline measurement (e.g. mild glare, marginal calibration residual) or ambiguous reaction colour (`INCONCLUSIVE`). Triggers automatic lab referral recommendation.
3. **`RECAPTURE` (Red):** Physical measurement failed (motion blur, underexposure, card missing, ROI occluded). Classifier is blocked, and the operator is instructed to capture a new photo.
