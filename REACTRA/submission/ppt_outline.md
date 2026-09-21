# RECTRA — Pitch Deck & Presentation Outline (SIH 2026)

## Slide 1: Title & Identity
- **Title:** RECTRA: Calibrated Field-Test Intelligence & Presumptive Evidence System
- **Sub-Title:** Digital Companion for Field Drug Testing (SIH26231)
- **Key Message:** Turning subjective chemical screening into scientifically calibrated, cryptographically verifiable presumptive evidence.
- **Visual:** RECTRA logo, reference card rendering, terminal mockups.

---

## Slide 2: The Ground Reality & Problem Statement
- **Current Practice:** Officers crush chemical ampoules in plastic pouches and visually compare colours to packaging swatches under streetlamps.
- **Three Fatal Flaws:**
  1. *Illumination Distortion:* Ambient lighting alters colour perception by up to 30 $\Delta E$ units.
  2. *Measurement Blindness:* Blurry, glary, or degraded photos produce false interpretations.
  3. *Unverified Paper Trails:* Test logs lack tamper-evidence or mathematical chain of custody.
- **The Legal Risk:** Overstating presumptive screening as forensic certainty leads to wrongful arrests or court dismissals.

---

## Slide 3: Core Product Principle & Philosophy
- **Non-Negotiable Principle:** RECTRA does not blindly turn a photograph into a conclusion.
- **The 5-Step Pipeline:**
  $$\text{CAPTURE} \longrightarrow \text{CALIBRATE} \longrightarrow \text{VALIDATE} \longrightarrow \text{CLASSIFY} \longrightarrow \text{PRESERVE}$$
- **Safety First:** Prominent disclaimers on every interface: *"PRESUMPTIVE FIELD-TEST RESULT — Laboratory confirmation is required."*

---

## Slide 4: Computer Vision & Physical Illumination Calibration
- **Geometric Normalization:**
  - 4 corner black square fiducials detect card boundaries.
  - Perspective warp to canonical $1000 \times 700$ geometry.
- **CIE Lab Least-Squares Calibration:**
  - 6 canonical colour patches (White, Gray, Black, Red, Green, Blue).
  - Solves affine matrix $\mathbf{M} \in \mathbb{R}^{4 \times 3}$ in perceptual CIE Lab space.
  - Dynamic residual calculation ($\Delta E < 8.00$).

---

## Slide 5: The Measurement Validity Gate
- **Physical Quality Checks Before Classification:**
  - *Blur (Focus):* Laplacian variance $\ge 80.0$.
  - *Exposure:* Mean luminance $50 - 220$.
  - *Specular Glare:* Saturated reflection fraction $\le 5\%$.
  - *Card & ROI Integrity:* Patch visibility and minimum pixel count.
- **Actionable Defenses:** Fails degraded photos with `RECAPTURE REQUIRED`, refusing to guess on bad data.

---

## Slide 6: Explainable Presumptive Classification
- **Nearest Centroid in CIE Lab Space:**
  - Calculates Euclidean distance to nominal class centroids.
  - Enforces `inconclusive_delta_e_margin`: if difference is $< 12.00$, outputs `INCONCLUSIVE`.
  - Zero deep learning black-boxes; completely explainable in court.
- **Automated Laboratory Escalation:**
  - Inconclusive or reviewed tests immediately generate machine-readable (`.json`) and human-readable (`.html`) Lab Referral Packets.

---

## Slide 7: Cryptographic Integrity & Evidence Chain
- **Tamper-Evident Evidence Envelopes:**
  - Canonical JSON serialization (`json-sort-keys-compact-utf8-v1`).
  - SHA-256 preimage digest.
  - Ed25519 digital signature generated with local hardware key.
- **Local Backward-Linking Audit Chain:**
  - Sequential hash chain ($H_i = \text{SHA256}(R_i \parallel H_{i-1})$).
  - Gap detection and immediate tamper discovery.
  - Standalone verification: verify envelopes without cloud access.

---

## Slide 8: Live System Demonstration & Validation
- **7 Deterministic Demo Scenarios:**
  - Good Positive, Good Negative, Ambiguous Reagent, Motion Blur, Overexposed Glare, Tampered Record, Deleted Chain Record.
  - **100% Pass Rate (7 / 7 scenarios).**
- **Test Suite Metrics:**
  - 37 automated tests (24 unit, 13 integration), 100% passing in 1.4s.
  - Macro F1: 1.0000 on synthetic benchmark.
  - 0 lint errors (`ruff`).

---

## Slide 9: Innovation Roadmap & Production Viability
- **Phase 0 (Current):** Standalone calibrated MVP with manual DEMO LOCATION and SQLite chain.
- **Phase 1 (Hardening):** Hardware GPS, TPM/Secure Enclave key storage, multi-kit profile library.
- **Phase 2 (Kinetics):** Kinetic video analysis $\Delta E(t)$ to detect expired/slow reagent reactions.
- **Phase 3 (LIMS):** Central laboratory synchronization and confirmatory cross-validation.

---

## Slide 10: Conclusion & Impact
- **Forensic Defensibility:** Transparent, mathematically provable presumptive screening.
- **Zero Cloud / Zero Blockchain:** Completely operable offline in basements, rural borders, and remote checkpoints.
- **Integrity You Can Prove in Court:** Sealed digital records that withstand judicial scrutiny.
