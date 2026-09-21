# RECTRA — Video Demonstration Script (3–5 Minutes)

---

### [00:00 - 00:45] Scene 1: The Problem
**Visual:** Split screen showing an officer under a yellow streetlight holding a drug testing pouch, next to an uncalibrated smartphone photo with severe glare and motion blur.
**Voiceover:**
"In field law enforcement, presumptive drug testing is essential. Officers crush chemical ampoules and observe a color change. But streetlights distort the color, blurry camera captures cause false interpretations, and paper test logs offer zero cryptographic protection in court.
Most smartphone solutions try to slap a black-box deep learning model on a photo. But deep learning cannot understand lighting physics, and it cannot be audited in a court of law.
Meet **RECTRA**: the Calibrated Field-Test Intelligence and Presumptive Evidence System."

---

### [00:45 - 01:45] Scene 2: Capture, Calibration & Validation
**Visual:** Screen recording of RECTRA UI on NEW TEST page. Ingesting `DEMO-POS-001.png`. Transitioning to ANALYSIS page.
**Voiceover:**
"RECTRA follows one foundational rule: it never turns a photograph into a conclusion without checking the measurement first.
An officer captures the test using the RECTRA reference card.
The system automatically:
First, locates the card's 4 corner fiducials and normalizes perspective.
Second, reads the profile QR code to identify the exact chemical assay.
Third, performs least-squares affine calibration in perceptual CIE Lab space across 6 physical reference patches, removing ambient illumination shifts.
Fourth, enforces the Measurement Quality Gate: checking focus with Laplacian variance, exposure limits, and specular glare.
Because this capture is sharp, well-exposed, and properly calibrated, it passes cleanly."

---

### [01:45 - 02:45] Scene 3: Explainable Classification & Presumptive Safeguards
**Visual:** Screen recording of RESULT page. Highlighting the safety banners, presumptive classification badge, and class distance metrics.
**Voiceover:**
"Next, RECTRA's Nearest Centroid classifier measures the Euclidean distance from the corrected reaction color to nominal class centroids.
The result is **PRESUMPTIVE POSITIVE** with a 96% match score.
Notice the prominent non-negotiable warning on every screen: *PRESUMPTIVE FIELD-TEST RESULT — Laboratory confirmation is required.*
RECTRA never oversteps forensic boundaries.
With one click, the officer preserves the session.
RECTRA generates the **Field Test Reliability Passport** — a 4-section audit record summarizing capture metadata, physical quality gate metrics, presumptive interpretation, and cryptographic signatures."

---

### [02:45 - 03:45] Scene 4: Defending Against Bad Data & Tampering
**Visual:** Running Scenario 4 (Blurred capture) showing instant RECAPTURE rejection. Then running Scenario 6 (Tampered record) showing verification failure.
**Voiceover:**
"What happens when the field conditions are degraded?
If an officer uploads a blurry photo — RECTRA's quality gate instantly catches it: *RECAPTURE REQUIRED — Focus variance too low.* The classifier is blocked. RECTRA refuses to guess on compromised data.
What about an ambiguous reaction? If cutting agents produce an uncertain color, RECTRA outputs *INCONCLUSIVE* and automatically synthesizes a Laboratory Referral Packet in both JSON and styled HTML for immediate lab escalation.
Now watch what happens if someone attempts to tamper with the evidence.
We export an evidence envelope, open it, and alter the result from POSITIVE to NEGATIVE.
When uploaded for verification, RECTRA immediately detects the modification: *INTEGRITY VERIFICATION FAILED.* The Ed25519 digital signature and canonical SHA-256 digest are broken."

---

### [03:45 - 04:30] Scene 5: Verification, Audit Chain & Summary
**Visual:** Navigating to Test History, running the local backward-linking audit chain validator, and showing 37 passing unit/integration tests in terminal.
**Voiceover:**
"All tests are linked in a local backward-linking hash chain stored in SQLite. If an attacker deletes a record or alters a database entry, chain verification detects the gap instantly.
RECTRA is 100% offline. Zero cloud servers. Zero blockchain. Zero deep learning hallucinations.
It has been validated across 7 deterministic scenarios and 37 comprehensive automated tests with 100% passing results.
RECTRA: Bringing scientific calibration, explainable intelligence, and cryptographic chain-of-custody to field drug testing."
*(Fade to black with RECTRA logo and SIH26231 details)*
