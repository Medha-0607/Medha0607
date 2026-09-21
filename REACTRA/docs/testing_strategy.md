# REACTRA — Automated Testing & Verification Strategy

**Problem Statement:** SIH26231 — Digital Companion for Field Drug Testing  
**Framework:** Pytest 9.1+ | Test Coverage: Unit, Integration, Cryptographic, and Safety

---

## 1. Test Architecture

The test suite is structured into two main tiers:
- `tests/unit/`: Testing isolated mathematical, vision, and cryptographic functions.
- `tests/integration/`: Testing multi-stage pipeline flows, quality-gate blocking rules, tamper detection, and hash-chain breaks.

---

## 2. Test Execution Commands

```powershell
# Run entire test suite (45 tests)
python -m pytest -v

# Run only unit tests
python -m pytest tests/unit/ -v

# Run only integration tests
python -m pytest tests/integration/ -v

# Verify code style and linting
ruff check src/ app.py scripts/ tests/

# Execute 7 deterministic demo scenarios
python scripts/run_demo.py

# Verify local SQLite audit chain integrity
python scripts/verify_chain.py
```

---

## 3. Test Coverage Summary

### Unit Tests
1. **Calibration (`test_calibration.py`):** Identical mapping $\Delta E = 0$, known distance verification, affine transformation recovery.
2. **Canonical Serialization (`test_canonical.py`):** Key sorting, deterministic JSON formatting, nested float preservation.
3. **Audit Chain (`test_chain.py`):** Empty chain validity, genesis link, multi-link continuity, broken hash detection.
4. **Classifier (`test_classifier.py`):** Centroid match for positive and negative, inconclusive margin thresholding.
5. **Database Repository (`test_database.py`):** Session saving, evidence persistence, query filter combinations.
6. **Profile Loader (`test_profile_loader.py`):** Profile enumeration, uncalibrated profile validation, rejection of missing centroids on calibrated profiles.
7. **Quality Gate (`test_quality_gate.py`):** Blur rejection, exposure thresholds, glare classification.
8. **Referral Packet (`test_referral.py`):** Trigger conditions (inconclusive, recapture), structured packet generation.
9. **Session Manager (`test_session_manager.py`):** State machine transitions, SQLite draft persistence and recovery.
10. **Digital Signing (`test_signing.py`):** Ed25519 signature validity, tampered digest rejection, key fingerprint formatting.

### Integration Tests
1. **End-to-End Pipeline (`test_pipeline.py`):** Standard positive, negative, inconclusive benchmark execution.
2. **Critical Quality Gate Rule (`test_pipeline.py`):** Proves degraded capture (blur/glare) fails quality gate and strictly blocks classifier execution (`classification is None`).
3. **Tamper Detection (`test_tamper_detection.py`):** Verifies detection of altered presumptive result, operator ID, classification score, and signature bytes.
4. **Chain Verification (`test_chain_verification.py`):** Verifies detection of deleted intermediate records and modified link hashes.
