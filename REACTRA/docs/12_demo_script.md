# 12 — Live Demonstration Script & Flow (SIH 2026 Presentation)

## Presentation Objective
Demonstrate to evaluators that RECTRA is not a superficial "AI photo scanner," but a **calibrated, tamper-evident forensic intelligence companion** built on rigorous measurement validity, explainability, and chain-of-custody preservation.

**Total Duration:** 5 to 7 Minutes

---

## 1. Introduction & Problem Framing (1 Minute)
- "Good morning, respected judges. In field drug testing, officers crush chemical ampoules and look at a color shift under streetlights. This process suffers from three major flaws: ambient lighting shifts the perceived color, blurry photos produce false interpretations, and paper test logs lack cryptographic chain of custody."
- "RECTRA's core product principle is: **RECTRA does not blindly turn a photograph into a conclusion.** It first checks whether the physical measurement is usable, produces a calibrated presumptive interpretation, and preserves it in a signed, tamper-evident evidence envelope."

---

## 2. Standard Positive Field Test Walkthrough (2 Minutes)
1. **Navigate to NEW TEST:**
   - Show Operator ID (`DET-SHARMA-402`) and explicit `DEMO LOCATION` manual coordinates.
   - Ingest `data/demo/positive/DEMO-POS-001.png`.
2. **Review ANALYSIS Page:**
   - Highlight Card Localization: Perspective warped to canonical 1000x700 geometry.
   - Highlight Illumination Calibration: Least-squares residual $\Delta E = 1.15 < 8.00$.
   - Highlight Quality Gate: 4 green indicators (Blur, Exposure, Glare, ROI).
3. **Review RESULT Page:**
   - Point out prominent safety banners: `PRESUMPTIVE FIELD-TEST RESULT — Laboratory confirmation is required.`
   - Show Presumptive Result: `POSITIVE` with normalized match score (0.96) and class distances.
4. **Preserve Evidence:**
   - Click "Preserve Evidence Record & Append to Local Chain".
   - View Reliability Passport: Status `READY` with all 4 structured audit sections.

---

## 3. Physical Measurement Quality Gate Defenses (1.5 Minutes)
1. **Motion Blur Defense (Scenario 4):**
   - Ingest `data/demo/edge_cases/DEMO-EDGE-BLURRED.png`.
   - Show the Quality Gate instantly rejecting the capture: `RECAPTURE REQUIRED (Laplacian variance 21.4 < 80.0)`.
   - Point out that classification is blocked — RECTRA refuses to guess on degraded data.
2. **Ambiguous Reagent Defense (Scenario 3):**
   - Ingest `data/demo/inconclusive/DEMO-INC-001.png`.
   - Show Presumptive Result: `INCONCLUSIVE (REVIEW)`.
   - Show automated Lab Referral Packet generation (JSON and formatted HTML report).

---

## 4. Cryptographic Tamper Detection & Chain Verification (1.5 Minutes)
1. **Envelope Export & Tamper Detection (Scenario 6):**
   - Export an evidence envelope `RECTRA_EVIDENCE_*.json`.
   - Open in text editor, modify `result: "POSITIVE"` to `"NEGATIVE"`.
   - Upload into Evidence Verification tab:
   - System immediately displays: `❌ INTEGRITY VERIFICATION FAILED: Canonical digest mismatch.`
2. **Audit Chain Continuity (Scenario 7):**
   - Click "Run Chain Verification".
   - Demonstrate 5 unbroken records verified.
   - Simulate a deleted record: System immediately displays `❌ CHAIN COMPROMISED: Discontinuity detected`.

---

## 5. Conclusion & Forensic Posture (30 Seconds)
- "RECTRA brings scientific rigor, physical calibration, and cryptographic integrity to field testing without requiring cloud servers, proprietary hardware, or unproven black-box claims."
- Open floor for evaluator questions.
