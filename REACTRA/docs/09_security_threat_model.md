# 09 — Security & Forensic Threat Model

## 1. Threat Landscape & Adversarial Vectors

In field law enforcement and evidentiary proceedings, digital evidence companions are targeted by distinct adversarial actors:
- **Corrupt / Malicious Operator:** Seeks to frame a suspect by flipping an inconclusive test to POSITIVE, or protect an associate by flipping a positive test to NEGATIVE.
- **Accused / Defense Counsel:** Seeks to challenge the chain-of-custody, arguing an image was photoshopped, captured on a different day, or altered in storage.
- **Third-Party Intruder / Ransomware:** Seeks to modify, delete, or inject fake records into local storage.

---

## 2. Threat Analysis & Mitigations

| Threat Vector | Attack Mechanism | RECTRA Mitigation |
|---|---|---|
| **Post-Hoc Result Tampering** | Attacker edits SQLite database or JSON file to change `result: POSITIVE` to `result: NEGATIVE`. | **Canonical Hash Digest & Ed25519 Signature:** Altering any character changes the canonical SHA-256 digest. Signature verification immediately fails. |
| **Score / Metric Inflation** | Attacker alters `classification_score` or `residual_delta_e` to pretend a test was higher quality. | **Preimage Inclusion:** All numerical diagnostic metrics are included in the signed canonical preimage. Altering a float fails digest verification. |
| **Image Swapping / Replacement** | Attacker substitutes a different photograph into the capture folder. | **Raw Image SHA-256 Digest:** The raw image byte hash is embedded inside the signed canonical record. Any modified image produces an SHA-256 mismatch. |
| **Selective Record Deletion** | Attacker deletes an incriminating test record from the database. | **Backward-Linking Hash Chain:** Subsequent records contain `previous_record_hash`. Deleting an entry breaks the chain continuity, flagging `CHAIN COMPROMISED: Discontinuity detected`. |
| **Audit Chain Forking** | Attacker creates a competing sequence of records from an earlier point. | **Timestamp Monotonicity & Key Fingerprinting:** Audit logs record timestamps, rowids, and public key fingerprints. Verified against terminal public key records. |
| **Private Key Extraction** | Attacker accesses local machine and copies signing keys. | **Key Isolation:** Private keys are stored in `runtime/keys/` restricted via Windows `icacls` (or POSIX `0600`) to the current user. Never exported in envelopes. P1 roadmap specifies hardware secure enclave / HSM / TPM storage. |

---

## 3. Assumptions & Trust Boundary

- **Trusted Execution Boundary:** The local RECTRA runtime process and device OS kernel are assumed uncompromised during active signature generation.
- **Untrusted Storage Boundary:** Stored SQLite databases, exported JSON envelopes, and filesystem images are treated as completely untrusted. They are verified cryptographically before display or referral.
