# 01 — Problem Understanding: Field Drug Testing & Presumptive Evidence

## 1. Context & Operational Background

Field drug testing kits (colorimetric reagent ampoules such as Marquis, Scott, Duquenois-Levine, and Cobalt Thiocyanate) are widely used by law enforcement, border security, customs, and correctional agencies for immediate screening of suspected illicit substances.

In traditional field operations:
1. An officer places a milligram-scale sample into a transparent chemical pouch.
2. Glass ampoules containing concentrated acids and reagents are mechanically crushed.
3. A chemical reaction produces a subjective colour shift over 10 to 60 seconds.
4. The officer visually compares the liquid colour to an ink-printed reference chart on the packaging.
5. The officer writes a handwritten incident report recording the presumptive result.

---

## 2. Core Operational Failure Modes

Field colorimetric assays are subject to systemic environmental, human, and evidential vulnerabilities:

### A. Subjective Human Interpretation
- **Colour Perception Variance:** Mild colour blindness or eye fatigue under nighttime conditions leads to conflicting interpretations between different officers.
- **Lighting Bias:** Ambient lighting drastically shifts observed RGB colours. Yellow incandescent streetlamps, blue LED flashlights, or cloudy daylight completely alter the chromatic appearance of a liquid reagent.

### B. Degraded Chemical / Physical Conditions
- **Expired Reagents:** Outdated chemical ampoules produce sluggish, weak, or aberrant colour changes.
- **Reaction Kinetic Timing:** Premature reading (at 5 seconds) or reading after oxidation/evaporation (at 10 minutes) yields false results.
- **Sample Adulterants:** Cutting agents (e.g. sugars, starches, caffeine, analgesics) produce competing background tints that mask target reactions.

### C. Legal & Evidentiary Vulnerabilities
- **Presumptive vs Confirmatory Confusion:** Field kits are legally **presumptive screening tools only**. They cannot substitute for confirmatory laboratory testing (GC-MS / HPLC). Misrepresenting a field screening as definitive chemical identification risks wrongful arrest or immediate evidentiary challenge.
- **Unverified Paper Trails:** Standard paper forms lack cryptographic integrity, tamper-evidence, or verifiable chain-of-custody. Photographs taken on personal smartphones are vulnerable to metadata stripping, filter artifacts, or intentional alteration.

---

## 3. SIH 2026 Problem Statement (SIH26231) Scope

Problem statement **SIH26231** calls for a "Digital Companion for Field Drug Testing" to standardise, assist, and preserve presumptive testing procedures.

RECTRA resolves this challenge not by attempting black-box deep learning or making unscientific claims of chemical certainty, but by applying rigorous **measurement verification, illumination calibration, explainable classification, and cryptographic chain-of-custody preservation**.

---

## 4. Key Guiding Principles

1. **Measurement Usability First:** RECTRA never blindly turns a photograph into a conclusion. It first verifies focus, exposure, specular glare, card fiducials, and calibration accuracy. If the capture is physically degraded, it flags `RECAPTURE REQUIRED`.
2. **Defensible, Explainable Scoring:** Uses Nearest Centroid classification in perceptual CIE Lab space with explicit `INCONCLUSIVE` boundary margins.
3. **Cryptographic Preservation:** Generates canonical Ed25519 digital signatures and an append-only backward-linking audit hash chain.
4. **Honest Forensic Posture:** Prominently displays `PRESUMPTIVE FIELD-TEST RESULT — Laboratory confirmation is required` on every report.
