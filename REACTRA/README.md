# REACTRA

> **Reaction-Aware Field Testing & Verifiable Evidence**  
> *A measurement-validity and evidence-integrity layer for presumptive colorimetric field testing.*

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![Tests](https://img.shields.io/badge/tests-45%20passed%20(100%25)-brightgreen.svg)]()
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)]()

---

## Non-Negotiable Operational Disclaimers

> **PRESUMPTIVE FIELD-TEST RESULT — Laboratory confirmation is required.**  
> REACTRA is a field screening companion designed to standardize and preserve presumptive colorimetric reactions. Colorimetric tests are presumptive field indicators only. Confirmatory laboratory testing (e.g., GC-MS / HPLC) remains chemically and legally required for judicial certainty.  
> *Notice: All evaluation benchmarks use mathematically generated synthetic imagery with known CIE Lab ground truth. No real narcotics, illegal drugs, or controlled chemical substances were acquired, handled, or tested.*

---

## SIH 2026
- **Problem Statement:** SIH26231 — Digital Companion for Field Drug Testing
- **Theme:** Security & Law Enforcement / Forensic Science
- **Authoritative Entry Point:** `app.py` (`streamlit run app.py`)
- **Windows Launcher:** `run_reactra.bat`

---

## Problem
Presumptive chemical field testing (e.g., Marquis, Scott, Duquenois-Levine reagent kits) is widely deployed by law enforcement officers to detect illicit substances. However, conventional manual field interpretation suffers from severe operational vulnerabilities:
1. **Lighting & Optical Distortion:** Uncontrolled ambient illumination (e.g., sodium-vapour streetlights vs blue LEDs) shifts perceived chemical colours by up to 40 $\Delta E$ units, causing misinterpretation.
2. **Degraded Field Photography:** Blurred, overexposed, or glare-saturated mobile snapshots lead to catastrophic false positives or unverified interpretations.
3. **Absence of Chain of Custody:** Smartphone photos lack cryptographic binding, permitting post-capture tampering, metadata alteration, or evidentiary contestation in court.
4. **Subjective Officer Fatigue:** Manual visual comparison against printed colour charts induces confirmation bias under high-stress field conditions.

---

## Solution
REACTRA does not blindly turn a photograph into a conclusion. It introduces an automated measurement-validity and digital evidence-integrity layer that:
1. **Validates optical conditions** before classification, enforcing a strict pre-classification quality gate that blocks execution on degraded captures.
2. **Normalizes ambient illumination** using affine least-squares regression in perceptual CIE $L^*a^*b^*$ colour space against a standardized reference card.
3. **Produces explainable presumptive interpretations** via nearest-centroid distance scoring with an explicit `INCONCLUSIVE` margin.
4. **Seals physical and digital context** in an Ed25519-signed digital evidence envelope anchored to a local, tamper-evident audit hash chain.

---

## Core Workflow
The field operator experiences a unified, sequential 6-step workflow:
```
PHYSICAL TEST
      ↓
[1. START NEW TEST] ──> Operator Credentials, Reagent Profile, Location Mode
      ↓
[2. CAPTURE] ─────────> Live Device Camera / Verified Image Import
      ↓
[3. CHECK] ───────────> Image Quality Gate (Blur, Exposure, Glare, Card Detection)
      │
      ├──> IF FAILED: RECAPTURE_REQUIRED / REVIEW ──> STOP (Classification Blocked)
      │
      └──> IF PASSED: CIE Lab Calibration ──> Nearest-Centroid Classifier
      ↓
[4. RESULT] ──────────> Presumptive Outcome + Visual Explanation Layer
      ↓
[5. EVIDENCE] ────────> Field Test Reliability Passport + Ed25519 Signature + Audit Chain
      ↓
[6. COMPLETE] ────────> Historical Archive / Portable JSON & HTML Export / Lab Referral
```

---

## Architecture
REACTRA follows a clean, modular, layered architecture with strict separation of concerns:
- **UI Layer (`app.py`, `src/rectra/ui/`):** Streamlit interface utilizing service functions only. Zero SQL statements, zero cryptography, zero raw OpenCV in application views.
- **Session Layer (`src/rectra/core/session_manager.py`):** Explicit 10-stage lifecycle state machine with automatic SQLite persistence and recovery upon browser reload.
- **Vision Layer (`src/rectra/vision/`):** ArUco marker + contour perspective card detector, CIE Lab least-squares calibrator, and multi-metric quality gate.
- **Classification Layer (`src/rectra/classification/`):** Lightweight nearest-centroid distance scoring in perceptual CIE Lab space.
- **Evidence Layer (`src/rectra/evidence/`):** Deterministic canonical JSON serialization (`json-sort-keys-compact-utf8-v1`), Ed25519 digital signatures, and backward-linking hash chaining.
- **Persistence Layer (`src/rectra/database/`):** Local SQLite database (`test_sessions`, `evidence_records`, `assay_profiles`, `audit_chain`).

---

## MVP
The current submission-ready MVP provides:
- Fully functional 6-step sequential field operator workflow.
- Pre-classification validity gate enforcing strict blur, exposure, glare, and card completeness checks.
- CIE Lab colour calibration across 6 canonical swatches with measured residual $\Delta E$.
- Nearest-centroid presumptive classifier supporting `POSITIVE`, `NEGATIVE`, and `INCONCLUSIVE`.
- Complete Field Test Reliability Passport segregating capture, measurement, classification, and evidence dimensions.
- Real Ed25519 asymmetric signing and verification.
- Local backward-linking audit hash chain detecting record modification or deletion.
- Searchable SQLite history archive with detailed session inspection.
- Standardized laboratory referral packet generation for inconclusive or failed tests.
- Standalone Windows batch launcher (`run_reactra.bat`).
- 300 DPI vector-embedded printable reference card generator (`scripts/generate_printable_cards.py`).

---

## Technical Components

### Measurement Validity Gate
Evaluates physical and optical usability before interpretation:
- **Blur Detection:** Laplacian variance check ($\ge 80.0$).
- **Exposure Bounds:** Mean grayscale intensity within $[50, 220]$.
- **Specular Glare:** Saturation clipping fraction ($\le 5.0\%$). Severe glare ($> 20\%$) enforces `RECAPTURE_REQUIRED`.
- **Card Localization:** 4-point geometric quadrilateral confidence and aspect ratio verification.
- **Test ROI Integrity:** Pixel sufficiency ($\ge 500$ valid reaction pixels) and bounding containment.

### Reliability Passport
An integrated four-quadrant attestation document:
1. **Capture:** Capture mode (`LIVE_CAMERA` vs `IMPORTED_IMAGE`), UTC timestamp, Operator ID, Geolocation source (`GPS_DEVICE`, `MANUAL_DEMO`, `UNAVAILABLE`).
2. **Measurement:** Card detection status, Profile version, Calibration status, Residual $\Delta E$, Quality gate status.
3. **Classification:** Presumptive result, Prototype proxy score, Centroid distances, Model and Algorithm versions.
4. **Evidence:** Image SHA-256 digest, Record canonical digest, Ed25519 signature status, Audit chain link continuity.

### Evidence Integrity
- **Ed25519 Signatures:** RFC 8032 Edwards-curve digital signatures generated using local private keys stored in ignored runtime storage.
- **Tamper-Evident Local Hash Chain:** Incorporates `previous_record_hash` into canonical digest:
  $$\text{Digest}_i = \text{SHA-256}(\text{CanonicalJSON}(\text{Record}_i \parallel \text{Digest}_{i-1}))$$
- **Cryptographic Envelopes:** Portable `.json` and self-contained `.html` evidence summaries for courtroom and archival verification.

---

## Synthetic Data
To ensure safety and scientific transparency, all testing is conducted using controlled synthetic datasets:
- Generated via `scripts/generate_demo_data.py`.
- 17 controlled benchmark scenarios across positive, negative, ambiguous, blurred, and overexposed states.
- Known CIE Lab ground truth coordinates with synthetic noise, illumination temperature shifts, and specular artifacts.
- No real chemical hazards or illicit substances.

---

## Demo
Launch the interactive demo to evaluate all core execution paths:
1. Run `streamlit run app.py` or double-click `run_reactra.bat`.
2. Select **Field Operator Mode** to experience the 6-step testing workflow.
3. In Step 1, select `DEMO-ASSAY-001`, enter Operator ID, and choose Import Image.
4. In Step 2, select **Case 1: Positive Reaction** and click **Run Measurement & Quality Check**.
5. Step 3 verifies measurement readiness (`READY FOR ANALYSIS`).
6. Step 4 displays the presumptive outcome with visual overlays and nearest-centroid margins.
7. Step 5 displays the Reliability Passport and seals the evidence in the local chain.
8. Step 6 allows downloading the evidence envelope, HTML report, or referral packet.
9. Switch to **Validation & QA Mode** in the sidebar to execute all 7 automated validation scenarios and the tamper-detection lab.

---

## Installation

### Prerequisites
- Python 3.11.x
- Git

### Setup
```powershell
# Clone repository
git clone https://github.com/Medha-0607/Medha0607.git reactra
cd reactra

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Generate runtime cryptographic keys and initialize database
python scripts/generate_demo_keys.py
python scripts/init_database.py
python scripts/generate_demo_data.py
```

---

## Run
```powershell
# Launch Streamlit Field Companion
streamlit run app.py

# Or run Windows batch launcher
.\run_reactra.bat
```

---

## Tests
```powershell
# Run full automated test suite (45 tests)
python -m pytest -v

# Run linter
ruff check src/ app.py scripts/ tests/

# Run 7 deterministic demo scenarios
python scripts/run_demo.py

# Verify audit hash chain integrity
python scripts/verify_chain.py
```

---

## Limitations
1. **Synthetic Demonstration Profiles:** The primary profile (`DEMO-ASSAY-001`) utilizes controlled synthetic colour centroids. Secondary profiles (`MARQUIS-001`, `SCOTT-001`) are staged and explicitly require physical laboratory calibration.
2. **Presumptive Field Nature:** Colorimetric chemical tests cannot separate cut adulterants or provide quantitative purity analysis. Confirmatory GC-MS / HPLC testing remains mandatory.
3. **Platform Camera Variations:** Browser camera access depends on user permissions and device driver white-balance presets.
4. **No Direct eSakshya Integration:** The system exports portable, standardized evidence envelopes but does not claim unauthorized live integration with government backends.

---

## Prior Art
- **DetectaChem MobileDetect:** Commercial mobile presumptive test system utilizing barcode/QR alignment. REACTRA differentiates through an open, versioned assay profile library, transparent pre-classification quality gating, and local tamper-evident hash chaining.
- **Academic Smartphone Colorimetry:** Multiple publications establish smartphone RGB/Lab colorimetry. REACTRA integrates optical validity gating, least-squares CIE Lab illumination normalization, and asymmetric Ed25519 signing into a unified field companion.
- **Time-Resolved Kinetic Spot Testing (Kineticolor):** Research demonstrates reaction rate $\Delta E(t)$ analysis. REACTRA acknowledges this prior art and plans future kinetic temporal concordance in Phase 2.

---

## Differentiation
1. **Strict Measurement Validity Gate:** Rejects blurred, glare-saturated, or occluded captures before interpretation.
2. **Field Test Reliability Passport:** Transparently reports capture, measurement, classification, and evidence integrity without misleading aggregate percentages.
3. **Tamper-Evident Local Evidence Chain:** Mathematical proof of sequential audit integrity without cloud or blockchain dependencies.
4. **Offline-First Security:** Zero network requirements; all signing, hashing, and analysis execute locally.

---

## Roadmap
- **Phase 1 (Completed MVP):** 6-step operator workflow, quality gate, CIE Lab calibration, nearest-centroid classification, Ed25519 signing, local hash chain, lab referral packets.
- **Phase 2 (Research & Validation):** Real-world multi-reagent spectrometric centroid calibration (Marquis, Scott, Duquenois-Levine).
- **Phase 3 (Temporal Reaction Intelligence):** Video $\Delta E(t)$ kinetic curve analysis and endpoint concordance cross-checking.
- **Phase 4 (Interoperability):** Structured digital evidence export adapters for approved criminal justice management systems.

---

## Team Development Notes
- Repository maintained under strict type hints, Ruff linting (line length 100), and test-first integration.
- No private keys, local databases, or runtime evidence records are committed to version control.
