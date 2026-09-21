# 03 — MVP Scope & Acceptance Tracking

## 1. Product Scope

RECTRA is a calibrated field-test intelligence and evidence preservation companion for presumptive colorimetric drug testing kits.

### In Scope (MVP / Phase 1)
- End-to-end vertical pipeline:
  `CAPTURE → CALIBRATE → VALIDATE → CLASSIFY → PRESERVE → VERIFY → SEARCH / REFER`
- Explicit measurement validity gate (blur, exposure, glare, calibration residual, ROI integrity).
- CIE Lab colour calibration against a synthetic reference card with corner square fiducials.
- Nearest Centroid presumptive classifier with inconclusive $\Delta E$ margin.
- Field Test Reliability Passport with 4 structured sections.
- Canonical JSON serialization (`json-sort-keys-compact-utf8-v1`) and SHA-256 digest calculation.
- Ed25519 digital signature of evidence records and tamper detection.
- Local backward-linking hash chain across the test log.
- Local SQLite database with filtered search (ID, operator, date range, result, quality status).
- Automatic Lab Referral Packet generation (machine-readable JSON + human-readable HTML).
- 7 deterministic demo scenarios.
- Local Streamlit application.

### Deferred Features (P1 / P2)
- **Device GPS Geolocation Bridge:** Deferred to P1 to avoid brittle browser/OS dependencies during field demos. Primary MVP capture uses explicit, honest `DEMO LOCATION` manual entry.
- **Temporal Reaction Intelligence (Kinetic $\Delta E(t)$):** Deferred to Phase 4 (requires P0 stability).
- **Multiple Test Kit Profiles:** Architecture supports JSON profiles, but MVP ships with `DEMO-ASSAY-001 v1.0`.
- **Advanced Glare Inpainting:** Complex specular highlight restoration deferred to P2.

### Explicitly Excluded / Non-Goals
- No cloud infrastructure, Kubernetes, Docker, Firebase, PostgreSQL, Redis, Kafka.
- No blockchain, LLM APIs, vector databases, or deep neural networks.
- No claim of chemical confirmation, legal admissibility, forensic certification, or laboratory equivalence.
- No real illicit drug substances or chemical claims in demonstration data.

---

## 2. Acceptance Criteria Tracking Matrix

| # | Criterion | Status |
|---|---|---|
| 1 | Streamlit app launches locally | PASSED |
| 2 | Clean repository structure exists | PASSED |
| 3 | README exists and is accurate | PASSED |
| 4 | Dependencies install without error | PASSED |
| 5 | Synthetic data generator works | PASSED |
| 6 | Reference card generated | PASSED |
| 7 | Camera input works | PASSED |
| 8 | Image upload fallback works | PASSED |
| 9 | Operator ID required and validated | PASSED |
| 10 | Timestamp recorded (ISO 8601 UTC) | PASSED |
| 11 | GPS works OR explicit demo-location fallback labelled correctly | PASSED |
| 12 | Reference card detected | PASSED |
| 13 | Profile identified from card | PASSED |
| 14 | Calibration works | PASSED |
| 15 | Calibration residual ΔE calculated | PASSED |
| 16 | Image quality gate works | PASSED |
| 17 | Invalid capture can be rejected (RECAPTURE) | PASSED |
| 18 | Test ROI identified | PASSED |
| 19 | Classification works | PASSED |
| 20 | INCONCLUSIVE result is possible | PASSED |
| 21 | Reliability Passport displayed with all 4 sections | PASSED |
| 22 | Image SHA-256 generated | PASSED |
| 23 | Canonical evidence record generated | PASSED |
| 24 | Ed25519 signature generated | PASSED |
| 25 | Signature verification passes on valid record | PASSED |
| 26 | Hash chain generated | PASSED |
| 27 | Hash chain verification passes | PASSED |
| 28 | Tampering causes verification failure | PASSED |
| 29 | SQLite stores record | PASSED |
| 30 | History search works (by ID, operator, date, result) | PASSED |
| 31 | Evidence record can be reopened from history | PASSED |
| 32 | Lab referral packet generated (JSON + HTML) | PASSED |
| 33 | All unit tests pass | PASSED |
| 34 | All integration tests pass | PASSED |
| 35 | All 7 demo scenarios produce expected outputs | PASSED |
| 36 | No fake metrics anywhere | PASSED |
| 37 | No private key committed to Git | PASSED |
| 38 | No unsupported scientific claims | PASSED |
| 39 | README installation instructions work end-to-end | PASSED |
| 40 | PPT outline created | PASSED |
| 41 | Video script created | PASSED |
| 42 | Demo flow document created | PASSED |
| 43 | Git status is clean (only intended untracked files) | PASSED |
