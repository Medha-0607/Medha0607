# 11 — Innovation Roadmap & Future Phases

## Phase 0: MVP Proof-of-Concept (Current Release)
- **Status:** Complete & Fully Validated.
- **Capabilities:**
  - 4-corner fiducial reference card and perspective warp.
  - CIE Lab affine illumination calibration.
  - Laplacian blur, luminance exposure, and specular glare quality gates.
  - Nearest Centroid presumptive classifier with inconclusive boundary checks.
  - Field Test Reliability Passport (4 structured audit sections).
  - Canonical JSON serialization (`json-sort-keys-compact-utf8-v1`) and SHA-256 digests.
  - Ed25519 digital signature signing and verification.
  - SQLite backward-linking tamper-evident audit hash chain.
  - Automated Lab Referral Packet generator (JSON and styled HTML).
  - Explicit, honest manual `DEMO LOCATION` coordinate tagging.

---

## Phase 1: Operational Field Hardening
- **Target:** Law enforcement field trial prototype.
- **Key Enhancements:**
  - **Native Hardware Geolocation:** Hardware GPS integration via secure OS location services (replacing manual DEMO LOCATION).
  - **Secure Enclave / TPM Key Management:** Storing Ed25519 private keys in Android KeyStore / iOS Secure Enclave / Windows TPM 2.0.
  - **Multi-Reagent Profile Library:** JSON assay profiles for standard kits (Marquis, Scott, Duquenois-Levine, Cobalt Thiocyanate).
  - **Camera White-Balance Locking:** Direct camera sensor controls via Camera2 API to lock exposure time, ISO, and manual focus before capture.

---

## Phase 2: Reaction Kinetics & Advanced Optical Processing
- **Target:** Specialized forensic companion terminal.
- **Key Enhancements:**
  - **Kinetic Video Analysis ($\Delta E(t)$):** Multi-frame video ingestion tracking rate of colour development over 30 seconds. Reagent degradation alters reaction speed; temporal analysis distinguishes fresh reactions from oxidized contaminants.
  - **Polarized Lighting Shield:** Low-cost cross-polarizing physical film over lens and flash to physically eliminate specular reflections from liquid ampoules.
  - **Adulterant Spectrum Decomposition:** Mixture separation model estimating target compound presence in the presence of dominant cutting agents.

---

## Phase 3: National Forensic Laboratory Integration
- **Target:** Nationwide evidentiary integration.
- **Key Enhancements:**
  - **Central Laboratory Ingestion Gateway:** Automated intake of `RECTRA_REFERRAL_*.json` packets into LIMS (Laboratory Information Management Systems).
  - **Confirmatory Cross-Validation:** Direct pairing of presumptive field test records with subsequent GC-MS / HPLC confirmatory results to continuously calibrate assay profiles.
  - **Mutual TLS Federated Sync:** Offline-first field devices securely sync local audit chains with central jurisdictional evidence repositories when docking at the station.
