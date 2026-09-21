# AGENTS.md — REACTRA Development & Maintenance Rules

## Project Identity
- **Name:** REACTRA
- **Title:** Reaction-Aware Field Testing & Verifiable Evidence
- **Problem Statement:** SIH26231 — Digital Companion for Field Drug Testing
- **Target Python Version:** 3.11
- **Authoritative Entry Point:** `app.py` (`streamlit run app.py`)
- **Windows Launcher:** `run_reactra.bat`

---

## Core Product Principle
REACTRA does not blindly turn a photograph into a conclusion.
It first checks whether the physical measurement is usable (blur, exposure, glare, card geometry, ROI completeness), then produces a calibrated presumptive interpretation, preserves it in a versioned, Ed25519-signed digital evidence record, and maintains a local tamper-evident hash chain for subsequent judicial integrity verification.

---

## Architecture Rules
1. **UI Layer (`app.py`, `src/rectra/ui/`):**
   - UI code calls service and repository functions only.
   - Zero SQL statements in UI code.
   - Zero cryptographic algorithms or signing in UI code.
   - Zero raw OpenCV image processing in `app.py`.
2. **Authority & Single Implementation:**
   - One authoritative implementation per capability.
   - Never create duplicate trees: `backend_v2/`, `app2.py`, `frontend_new/`, `test_new/`.
   - All thresholds must derive from assay profiles (`profiles/`) — never scatter magic numbers across source files.
   - Always use `pathlib.Path` for all filesystem operations — never string concatenation.
3. **Session Lifecycle Machine:**
   - All test sessions follow the legal state machine:
     `DRAFT` ➔ `CAPTURED` ➔ `ANALYZING` ➔ `VALIDATION_FAILED` / `READY_FOR_CLASSIFICATION` ➔ `CLASSIFIED` ➔ `EVIDENCE_SEALED` ➔ `COMPLETED`.
   - Incomplete sessions must remain recoverable from SQLite upon browser reload.
   - Never silently lose the active test.

---

## Measurement Validity & Safety Rules
1. **Pre-Classification Gate:**
   - Image quality evaluation MUST genuinely precede classification:
     `CAPTURE ➔ QUALITY GATE ➔ (IF FAILED: STOP) ➔ CALIBRATION ➔ CLASSIFICATION ➔ PRESERVE`.
   - The classifier must NEVER run after a hard quality-gate failure (e.g. blur or severe glare).
2. **Mandatory Disclaimers:**
   - Every result view and evidence report must prominently display:
     `"PRESUMPTIVE FIELD-TEST RESULT — Laboratory confirmation is required."`
   - Evaluation notes must state:
     `"Controlled prototype evaluation uses synthetic demonstration data and is not validated for real-world forensic deployment."`
3. **Honest Geolocation and Device Reporting:**
   - Real browser GPS only when permission granted.
   - When unavailable, display `GPS: UNAVAILABLE`.
   - Manual demo entry is strictly labelled: `MANUAL DEMO LOCATION`.
   - Device information: `Not reported by browser` unless real metadata is detected. Never fabricate.
4. **No Real Drugs or Chemical Claims in Demo Data:**
   - Demonstration kits use synthetic colour values.
   - Multi-reagent profiles (`MARQUIS-001`, `SCOTT-001`) remain staged with `class_centroids_lab: null` and require physical calibration.
5. **No Private Keys in Git:**
   - Private keys, SQLite runtime databases, and local test evidence files are stored in `runtime/` and must remain strictly `.gitignore`d.

---

## Coding & Linting Standards
- **Ruff:** Target line length is 100 characters. Zero lint or formatting warnings.
- **Type Hints:** Type hints on all public functions.
- **Logging:** Use `logging.getLogger(__name__)` in all modules — no bare `print()`.
- **Testing:** Pytest for automated unit and integration tests. Deterministic random seeds for synthetic data.

---

## Session Handoff Checklist
Before completing any engineering session:
1. Run: `python -m pytest -v` (all tests must pass).
2. Run: `ruff check src/ app.py scripts/ tests/` (must pass with 0 errors).
3. Run: `python scripts/run_demo.py` (all 7 deterministic scenarios must pass).
4. Run: `python scripts/verify_chain.py` (audit hash chain must verify as intact).
5. Verify Streamlit smoke test on `http://localhost:8501`.
6. Update `CHANGELOG.md` with completed changes.
7. Inspect `git status` — confirm no private keys, databases, or untracked cache files are staged.
