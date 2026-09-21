# REACTRA — Security Threat Model & Defense Architecture

**Problem Statement:** SIH26231 — Digital Companion for Field Drug Testing  
**Standards:** RFC 8032 (Ed25519), NIST FIPS 180-4 (SHA-256), JCS (RFC 8785)  

---

## 1. Threat Matrix

| Threat ID | Threat Description | Attack Vector | REACTRA Defense / Mitigation | Residual Limitation |
|---|---|---|---|---|
| **T1** | Post-Capture Image Tampering | Attacker alters image pixels to falsify chemical colour. | Raw image bytes hashed with SHA-256 at moment of capture; hash committed into canonical signed record. | Camera sensor tampering prior to raw buffer capture requires hardware TPM. |
| **T2** | Evidence Outcome Modification | Attacker modifies `result` from POSITIVE to NEGATIVE in database. | Entire canonical record is signed with Ed25519. Any field modification causes signature verification failure. | Protect private key in OS-restricted runtime directory. |
| **T3** | Audit Record Deletion | Attacker deletes an incriminating test record from SQLite. | Backward-linking hash chain: Record $N+1$ includes $\text{Digest}_N$. Deleting Record $N$ breaks continuity. | If entire database is wiped, external export envelopes serve as off-device proof. |
| **T4** | Record Reordering | Attacker swaps sequential records to obscure timelines. | Hash chain links are strictly sequential; swapping links causes hash mismatch at both modified indices. | Relies on single-writer sequential commitment. |
| **T5** | Version Ambiguity | Attacker reinterprets old measurements using newer profile thresholds. | Evidence envelope immutably records `profile_version`, `model_version`, and `algorithm_version`. | Future versions must maintain backward-compatible schemas. |
| **T6** | Degraded Image Misleading Classifier | Low-light, blur, or glare produces false presumptive outcome. | Strict pre-classification quality gate blocks classifier execution on degraded imagery. | Threshold tuning required per physical camera sensor. |
| **T7** | Falsified GPS Representation | Manual coordinates represented in court as automated GPS. | Location source explicitly tagged: `GPS_DEVICE` vs `MANUAL_DEMO` vs `UNAVAILABLE`. | Browser geolocation relies on OS location provider. |
| **T8** | Import Represented as Live Capture | Pre-existing stock photo presented as contemporaneous live test. | `capture_mode` explicitly tags `LIVE_CAMERA` vs `IMPORTED_IMAGE` throughout evidence chain. | Browser camera API does not provide physical liveness attestation. |
