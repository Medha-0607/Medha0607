# 02 — RECTRA System Architecture

## 1. High-Level Architectural Diagram

```
+-----------------------------------------------------------------------------------+
|                                 RECTRA SYSTEM                                     |
+-----------------------------------------------------------------------------------+
                                          |
  [ FIELD IMAGE + OPERATOR METADATA ]     | (Capture Module)
                                          v
+-----------------------------------------------------------------------------------+
| 1. CARD LOCALIZATION & PERSPECTIVE WARP (card_detector.py)                        |
|    - QR code decode (assay profile & version identification)                      |
|    - 4 corner black square contour detection                                      |
|    - Perspective transform to canonical 1000x700 pixel geometry                  |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 2. ILLUMINATION CALIBRATION (calibration.py)                                      |
|    - Sample 6 canonical colour reference patches                                  |
|    - Least-squares affine mapping in perceptual CIE Lab space                     |
|    - Calculate residual calibration error ΔE76 (threshold < 8.00)                 |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| 3. MEASUREMENT VALIDITY GATE (quality_gate.py)                                    |
|    - Blur: Laplacian variance >= 80.0                                             |
|    - Exposure: Mean brightness 50 - 220                                           |
|    - Glare: Saturated specular pixel fraction <= 5%                               |
|    - Calibration valid & Test ROI bounding verified                              |
+-----------------------------------------------------------------------------------+
                                          |
                         +----------------+----------------+
                         | (VALID / REVIEW)                | (RECAPTURE)
                         v                                 v
+------------------------------------+  +-------------------------------------------+
| 4. CLASSIFIER (predictor.py)       |  | BLOCK INTERPRETATION                      |
|    - Nearest Centroid in Lab space |  | Quality Gate Failure: Operator prompted   |
|    - Check inconclusive margin     |  | to retake capture under better lighting   |
|    - Class scores & ΔE distances   |  +-------------------------------------------+
+------------------------------------+
                   |
                   v
+-----------------------------------------------------------------------------------+
| 5. EVIDENCE PRESERVATION & CHAIN-OF-CUSTODY (evidence/)                          |
|    - Image SHA-256 digest                                                         |
|    - Canonical JSON serialization (json-sort-keys-compact-utf8-v1)                |
|    - Ed25519 digital signature                                                    |
|    - Backward-linking audit hash chain                                            |
|    - SQLite local persistence & Exportable Evidence Envelope                      |
+-----------------------------------------------------------------------------------+
                   |
                   v
+-----------------------------------------------------------------------------------+
| 6. LAB REFERRAL & REPORTING (referral/ & ui/)                                     |
|    - Automated trigger on REVIEW, RECAPTURE, or INCONCLUSIVE                      |
|    - Machine-readable JSON + Human-readable HTML packet                           |
|    - Reliability Passport with 4 structured audit sections                        |
+-----------------------------------------------------------------------------------+
```

---

## 2. Component Structure & Boundaries

RECTRA strictly enforces the **UI-Service Separation Rule**:
- **`rectra.ui` (`pages.py`, `components.py`):** Pure presentation. Zero SQL queries, zero OpenCV/CV code, zero cryptography.
- **`rectra.vision` (`capture.py`, `card_detector.py`, `calibration.py`, `quality_gate.py`, `roi_detector.py`):** Authoritative image processing and measurement validation.
- **`rectra.classification` (`predictor.py`, `evaluation.py`):** Nearest Centroid classifier with inconclusive thresholding and benchmark scoring.
- **`rectra.evidence` (`canonical.py`, `hashing.py`, `signing.py`, `chain.py`, `verifier.py`, `envelope.py`):** Cryptographic preservation and verification.
- **`rectra.database` (`connection.py`, `schema.py`, `repository.py`):** Local SQLite storage, indexed query filters, and atomic audit logging.
- **`rectra.referral` (`lab_packet.py`):** Automated laboratory packet synthesis.

---

## 3. Technology Stack & Zero Cloud Policy

- **Language:** Python 3.11
- **Computer Vision:** `opencv-python-headless`, `numpy`, `pillow`
- **QR Decoding:** OpenCV `QRCodeDetector` (pure software, no binary C dependencies)
- **Cryptography:** `cryptography` (Ed25519, SHA-256)
- **Database:** Standard library `sqlite3`
- **User Interface:** `streamlit`
- **Zero Cloud / Zero Network:** Entire pipeline runs locally on device without internet connectivity, remote APIs, cloud servers, or distributed blockchains.
