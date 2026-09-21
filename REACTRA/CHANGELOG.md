# CHANGELOG — REACTRA

All notable changes to the REACTRA project will be documented in this file.
Format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.0] - 2026-09-21: SIH 2026 Master Rebuild & Hardening Release

### Added
- **Official Name Consistency:** Systematic migration across codebase, UI, configurations, scripts, and documentation to official name **REACTRA** (Reaction-Aware Field Testing & Verifiable Evidence).
- **Session Lifecycle & Persistent Recovery (`src/rectra/core/session_manager.py`):**
  - 10-state session lifecycle state machine (`DRAFT`, `CAPTURED`, `ANALYZING`, `VALIDATION_FAILED`, `READY_FOR_CLASSIFICATION`, `CLASSIFIED`, `EVIDENCE_SEALED`, `REVIEW_REQUIRED`, `REFERRAL_REQUIRED`, `COMPLETED`).
  - Active session survival across UI navigation and deterministic draft recovery from SQLite upon browser reload.
- **Strict Pre-Classification Quality Gate Enforcement:**
  - Pipeline re-sequenced to enforce `CAPTURE ➔ QUALITY GATE ➔ (IF FAILED: STOP) ➔ CALIBRATION ➔ CLASSIFICATION`.
  - Classifier is strictly blocked from executing on degraded captures (e.g. motion blur, severe glare, underexposure, or missing card).
- **Explicit Typed Statuses for Validation Oracles (`OracleStatus`):**
  - Replaced ambiguous `"NONE"` expected outputs with typed statuses: `VALID`, `REVIEW`, `RECAPTURE_REQUIRED`, `INCONCLUSIVE`, `POSITIVE`, `NEGATIVE`, `INTEGRITY_VERIFICATION_FAILED`, `CHAIN_VERIFICATION_FAILED`.
  - All 7 deterministic demonstration scenarios verified with strict type matching.
- **Redesigned 6-Step Field Operator Workflow (`src/rectra/ui/pages.py`):**
  - Replaced developer sidebar stages with a unified sequential wizard: `1. Setup ➔ 2. Capture ➔ 3. Check ➔ 4. Result ➔ 5. Evidence ➔ 6. Complete`.
  - Clean mode segregation: **Field Operator Mode** vs **Validation & QA Mode**.
- **Visual Explanation Layer:**
  - Visual overlays showing normalized reference card bounding box, 6 reference patch locations (green), and reaction ROI target zone (cyan).
  - CIE Lab colour comparison table and nearest-centroid decision distance margin breakdown.
- **Self-Contained HTML Evidence Report Generator (`generate_evidence_html_report`):**
  - Exportable, human-readable HTML digital evidence certificate alongside standard `.json` envelopes.
- **Staged Multi-Reagent Profiles (`MARQUIS-001`, `SCOTT-001`):**
  - Added JSON profile library entries with `class_centroids_lab: null`, `is_calibrated: false`, and mandatory calibration requirement notices.
  - Interactive profile switcher in UI with automatic execution disable guard and warning banners.
- **Windows Launcher & High-Res PDF Reference Card:**
  - Double-clickable `run_reactra.bat` batch launcher for Windows.
  - 300 DPI vector-embedded printable A4/PVC reference card generator with 50mm physical calibration ruler (`scripts/generate_printable_cards.py`).
- **Comprehensive Test Expansion:**
  - Test suite expanded to 45 automated unit and integration tests (100% pass rate in ~1.4 seconds).
  - Added critical safety integration test proving degraded captures block classifier execution.
  - Added session lifecycle transition and draft recovery tests.

## [1.0.0] - Milestone 12: Complete Documentation & Final Delivery


### Added
- Complete suite of 13 architectural, legal, and operational documentation specifications in `docs/`:
  - `01_problem_understanding.md`: Operational realities, environmental failure modes, and SIH26231 mapping.
  - `02_system_architecture.md`: End-to-end dataflow, component boundaries, and zero-cloud invariants.
  - `03_mvp_scope.md`: All 43 acceptance criteria marked 100% PASSED with tracking matrices.
  - `04_field_test_reliability_passport.md`: 4-section diagnostic audit architecture specification.
  - `05_evidence_record_specification.md`: Canonical serialization format (`json-sort-keys-compact-utf8-v1`).
  - `06_cryptographic_verification.md`: Ed25519 signing, preimage invariance, and backward hash chaining.
  - `07_calibration_methodology.md`: CIE Lab space, least-squares affine transformation, and $\Delta E_{76}$ residuals.
  - `08_synthetic_dataset.md`: Reproducible synthetic benchmark generation and zero real drug policy.
  - `09_security_threat_model.md`: Forensic threat vectors, tamper defenses, and trust boundaries.
  - `10_evaluation_report.md`: Real quantitative performance (Macro F1 = 1.0 on synthetic data).
  - `11_innovation_roadmap.md`: P1 hardware GPS/TPM, P2 kinetic analysis $\Delta E(t)$, and P3 LIMS federation.
  - `12_demo_script.md`: 5-7 minute live presentation guide for evaluators.
  - `13_judge_questions.md`: Thorough, scientifically authoritative answers to all 15 judge questions.
- Submission presentation assets in `submission/`:
  - `submission/ppt_outline.md`: 10-slide high-impact pitch deck outline.
  - `submission/video_script.md`: Timed 3-5 minute demonstration video walkthrough script.
  - `submission/demo_flow.md`: Step-by-step evaluator click guide.
  - `submission/metrics_template.md`: Real automated test and classifier performance metrics.
- Authoritative root `README.md` with pipeline diagrams, quickstart instructions, and documentation index.
- Full verification passed: 37/37 automated tests passing, 0 lint errors, 7/7 demo scenarios validated.

## [0.11.0] - Milestone 11: Comprehensive Test Suite & Metrics Population

### Added
- Complete automated pytest suite (37 tests across unit and integration categories, 100% pass rate in ~1.4 seconds).
- Shared testing fixtures (`tests/conftest.py`) providing in-memory SQLite instances, default profile loaders, and synthetic test cards.
- Unit tests (`tests/unit/`):
  - Calibration: Identity mapping, Euclidean $\Delta E_{76}$, and affine colour correction.
  - Quality Gate: High-frequency blur variance, luminance boundaries, and specular glare fraction.
  - Classifier: Nominal centroid matches and ambiguous inconclusive margin boundaries.
  - Canonical Serialization: Key sorting, compact JSON, and deterministic float formatting.
  - Digital Signing: Ed25519 signature generation, verification, and fingerprinting.
  - Audit Chain: Genesis link verification, multi-entry continuity, and broken link detection.
  - SQLite Database: Session and evidence model persistence, plus multi-filter log queries.
  - Lab Referral: Automated referral threshold checks and HTML report generation.
- Integration tests (`tests/integration/`):
  - End-to-end pipeline on positive, negative, inconclusive, blurred, and overexposed synthetic samples.
  - Cryptographic tamper detection testing outcome, operator, score, and signature alterations.
  - SQLite audit chain verification testing gap detection on deleted records and hash modifications.
- Official metrics document (`submission/metrics_template.md`) populated with real, verified evaluation figures (Macro F1 = 1.0 on synthetic data, 7/7 demo scenarios passed).
- Zero fake metrics policy strictly adhered to.

## [0.10.0] - Milestone 10: Demo Scenarios & Complete UI Pages

### Added
- 7 deterministic demo scenario runners (`src/rectra/demo/scenarios.py`) covering positive, negative, inconclusive, blurred, overexposed, tampered record, and broken chain cases.
- Standalone CLI demo runner (`scripts/run_demo.py`) executing all 7 demo scenarios with terminal status reports.
- Comprehensive multi-page Streamlit interface (`src/rectra/ui/pages.py`) and entrypoint (`app.py`) featuring:
  - Home: Problem overview, pipeline diagram, and quick-action links.
  - New Test: Form with operator ID, DEMO LOCATION coordinates, image capture/upload, and validation.
  - Analysis: Visual card localization, perspective normalization display, calibration diagnostics, and quality gate breakdown metrics.
  - Result: Prominent safety banners, presumptive classification badge, explainable class distance chart, and one-click evidence preservation.
  - Evidence: Canonical preimage viewer, Ed25519 signature details, envelope JSON export/upload verification, and local audit chain validator.
  - Test History: Multi-field search log with modal viewing of the complete 4-section Reliability Passport.
  - Referral: Automatic lab referral packet exporter (JSON & styled HTML) with live in-app preview.
  - Demo / Validation: 7 one-click demo triggers, real confusion matrix and F1 metrics viewer, and prototype scope disclosures.
- Strict UI-service boundary enforced: zero SQL, CV, or cryptographic operations in UI components.


### Added
- Laboratory referral generator (`src/rectra/referral/lab_packet.py`) producing machine-readable `RECTRA_REFERRAL_{TEST_ID}.json` and formatted `RECTRA_REFERRAL_{TEST_ID}.html` reports.
- Automated referral threshold evaluation triggered by ambiguous presumptive classifications (`INCONCLUSIVE`) or compromised measurements (`REVIEW`/`RECAPTURE`).

## [0.8.0] - Milestone 8: SQLite Database Repository & Searchable Test Log

### Added
- Authoritative database repository (`src/rectra/database/repository.py`) supporting CRUD operations for `test_sessions`, `evidence_records`, and `audit_chain`.
- Multi-criteria searchable test log with filters for Test UUID, Operator ID, Date Range, Presumptive Result, and Quality Gate Status.

## [0.7.0] - Milestone 7: Evidence Preservation, Cryptography & Hash Chain

### Added
- Deterministic canonical serialization (`src/rectra/evidence/canonical.py`) using `json-sort-keys-compact-utf8-v1`.
- Cryptographic SHA-256 digest computation (`src/rectra/evidence/hashing.py`) for images and canonical record preimages.
- Ed25519 digital signature signing and verification (`src/rectra/evidence/signing.py`) with public key fingerprinting.
- Tamper-evident local evidence chain (`src/rectra/evidence/chain.py`) tracking `previous_record_hash` and detecting alterations or broken links.
- Standalone evidence verification (`src/rectra/evidence/verifier.py`) and portable evidence envelope export (`src/rectra/evidence/envelope.py`).
- CLI chain verification utility (`scripts/verify_chain.py`).

## [0.6.0] - Milestone 6: Field Test Reliability Passport

### Added
- Domain models (`src/rectra/models/`) defining `TestSessionModel`, `EvidenceRecordModel`, and `ReferralPacketModel`.
- Field Test Reliability Passport builder and UI component (`src/rectra/ui/components.py`) rendering the 4 structured audit sections (Capture, Measurement, Classification, Evidence) and the overall operational status badge.

## [0.5.0] - Milestone 5: Classifier & Evaluation Framework

### Added
- Nearest Centroid classifier (`src/rectra/classification/predictor.py`) enforcing `inconclusive_delta_e_margin` threshold and normalized confidence scoring.
- Evaluation engine (`src/rectra/classification/evaluation.py`) computing real confusion matrix, precision, recall, and macro F1 against ground truth.
- Zero fake metrics safeguard: dynamically loads cached evaluation or cleanly displays "Evaluation not yet run" guidance.

## [0.4.0] - Milestone 4: Calibration, Test ROI Detection, Quality Gate & Colour Features

### Added
- CIE Lab colour calibration module (`src/rectra/vision/calibration.py`) performing least-squares affine transformation and residual $\Delta E_{76}$ calculation.
- Test reaction ROI extractor (`src/rectra/vision/roi_detector.py`) with bounding region validation and pixel count verification.
- Pre-classification measurement validity gate (`src/rectra/vision/quality_gate.py`) evaluating Laplacian variance blur, exposure luminance bounds, specular glare saturation, card detection, and calibration error.
- Interpretable colour features extraction (`src/rectra/vision/color_features.py`) with statistical Lab/HSV properties, L channel percentiles, and class centroid distance scoring.

## [0.3.0] - Milestone 3: Capture & Reference Card Detection

### Added
- Image capture pipeline (`src/rectra/vision/capture.py`) supporting live camera and image uploads with operator validation and explicit manual DEMO LOCATION GPS tagging.
- Card detector (`src/rectra/vision/card_detector.py`) with QR code decoding, 4 corner black square fiducial detection, perspective transformation to canonical 1000x700 coordinates, and spatial reference patch extraction.

## [0.2.0] - Milestone 2: Profiles, Reference Card & Synthetic Data Generator

### Added
- Reference card generator (`scripts/generate_reference_card.py`) generating `assets/reference_cards/RECTRA_DEMO_REFERENCE_CARD.png` with 4 corner black square fiducials, profile QR code, 6 canonical colour patches, and reaction test zone.
- Synthetic dataset generator (`scripts/generate_demo_data.py`) with reproducible random seeds, generating positive, negative, inconclusive, blurred, and overexposed images.
- Ground truth metadata file `data/demo/ground_truth.json` tracked in repository.
- `data/README.md` documenting synthetic data policies and reproducibility instructions.

## [0.1.0] - Milestone 1: Repository Foundation, Windows Rules & App Skeleton

### Added
- Project root configuration: `AGENTS.md`, `pyproject.toml`, `.gitignore`, `.env.example`.
- Dependencies specification: `requirements.txt` and `requirements-dev.txt` (removed unused `streamlit-js-eval`, relying on explicit manual `DEMO LOCATION`).
- Documentation: `docs/03_mvp_scope.md` with complete acceptance criteria tracking matrix (§49).
- Core package structure under `src/rectra/` (`config.py`, `core/constants.py`, `core/exceptions.py`, `core/logging_config.py`, `core/types.py`).
- Windows security helper in `scripts/generate_demo_keys.py` with `icacls` permission restrictions.
- Database schema and connection module in `src/rectra/database/` and `scripts/init_database.py`.
- Demo assay profile `profiles/DEMO-ASSAY-001/v1.0.json`.
- Minimal runnable `app.py` shell with first-run checks (keys, DB, profile) and sidebar navigation skeleton.
