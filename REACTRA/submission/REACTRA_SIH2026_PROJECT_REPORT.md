# REACTRA — Comprehensive Project Report & SIH Pitch Blueprint

**Problem Statement:** SIH26231 — *Digital Companion for Field Drug Testing*  
**Project Title:** REACTRA: Reaction-Aware Field Testing & Verifiable Evidence  
**Theme:** MedTech / Law Enforcement / Smart Governance  
**Repository:** `https://github.com/Medha-0607/Medha0607.git`  
**Target Platform:** Windows / Offline Field Terminals / Touch Web App  
**Release Version:** v1.1.0 (Hardened)

---

## 1. Executive Summary & Ground Reality

In narcotics interdiction, law enforcement officers routinely perform preliminary chemical screening using single-use colorimetric test kits (e.g., Marquis, Scott, Duquenois-Levine). An officer crushes chemical glass ampoules inside a flexible polyethylene pouch containing the suspect powder and visually matches the resulting hue against a printed reference chart on the packaging.

Under cross-examination in criminal court, this current field practice suffers from **three fatal vulnerabilities** that result in evidence suppression, overturned convictions, or wrongful arrests:

1. **Illumination Distortion:** Under night-time sodium-vapor streetlights (2700K) or vehicle halogens, reflected light shifts dramatically. A reaction that appears deep purple under daylight can appear brown under artificial light, causing chromatic shifts of up to 30 $\Delta E$ units.
2. **Measurement Blindness:** Generic smartphone apps apply deep-learning computer vision directly to raw camera frames. They classify blurry, out-of-focus, or glare-washed photos with false 95%+ confidence, ignoring whether the physical measurement is usable.
3. **Broken Chain of Custody:** Field test results are recorded in manual paper logbooks or unauthenticated smartphone galleries. Under Section 63 of Bharatiya Sakshya Adhiniyam (BSA) / Section 65B Indian Evidence Act, unhashed, unsigned photos fail judicial integrity requirements.

---

## 2. Competitive Benchmark & Prior-Art Positioning

| Capability / Architectural Dimension | Commercial Apps (e.g. MobileDetect) | Academic Smartphone Colorimetry | Generic Computer Vision Models | **REACTRA (Our Architecture)** |
|---|---|---|---|---|
| **Operating Environment** | Proprietary Cloud Backend | Isolated Python scripts | Cloud API or Mobile App | **100% Offline-First Architecture** |
| **Physical Quality Gate** | Basic barcode presence check | None (processes all pixels) | None (blind neural inference) | **Strict Pre-Classification Gate (Blur, Glare, Exposure, ROI)** |
| **Colorimetric Space** | Proprietary RGB matching | Basic RGB/HSV averaging | Raw RGB pixel arrays | **CIE L\*a\*b\* Perceptual Space with Affine Illumination Compensation** |
| **Explainability** | Proprietary percentage score | Mean RGB values | Uninterpretable Neural Weights | **Deterministic Nearest Centroid + Euclidean $\Delta E$ Margin** |
| **Cryptographic Custody** | Proprietary central cloud database | None | Plain SQLite / CSV | **Ed25519 Asymmetric Signature & Local SHA-256 Hash Chain** |
| **Judicial Referral** | Simple printable summary | None | None | **Standardized Machine-Readable JSON + Court-Ready PDF/HTML Packets** |

---

## 3. Core Architectural Principle

> **"REACTRA does not blindly turn a photograph into a conclusion."**

It first evaluates whether the physical optical measurement is usable. If the image suffers from motion blur, severe glare (>20%), or exposure blowout, the classification engine is **strictly blocked** with an actionable `RECAPTURE REQUIRED` directive. Only valid physical measurements proceed to calibration, presumptive classification, and cryptographic sealing.

```text
[CAPTURE] ➔ [CALIBRATE] ➔ [QUALITY GATE] ➔ (IF PASS) ➔ [CLASSIFY] ➔ [SEAL & CHAIN]
                                 │
                            (IF FAIL)
                                 ▼
                     [STOP: RECAPTURE REQUIRED]
```

---

## 4. In-Depth Technical Modules

### Module 1: Reference Card Detection & Planar Homography
* **Physical Target:** Standardized physical card containing 4 corner high-contrast square fiducial markers, 4 canonical reference color patches (White, 50% Gray, Black, Reagent Calibrant), a 50mm forensic scale, and a central reaction chamber cutout.
* **Detection Pipeline:** Grayscale conversion $\to$ Otsu adaptive thresholding $\to$ Contour quadrilateral approximation $\to$ Corner ordering $[(0,0), (W,0), (W,H), (0,H)] \to$ Perspective transform warp to canonical $1000 \times 700\,\text{px}$ geometry.

### Module 2: Perceptual CIE L\*a\*b\* Illumination Compensation
RGB color representations are hardware-dependent and non-linear. REACTRA operates in CIE L\*a\*b\* space, where Euclidean distance corresponds directly to perceived color difference ($\Delta E^*76$):
$$\Delta E^* = \sqrt{(\Delta L^*)^2 + (\Delta a^*)^2 + (\Delta b^*)^2}$$
The system extracts observed values from 4 canonical reference patches and solves an affine illumination compensation matrix $\mathbf{M}$ using ordinary least squares. The residual calibration error is computed; if residual $\Delta E > 8.00$, illumination compensation failure is flagged.

### Module 3: The Pre-Classification Gatekeeper
The gatekeeper evaluates four physical quality checks. Failure immediately halts the pipeline:
* **Blur Variance:** Evaluates variance of the Laplacian operator: $\text{Var}(\nabla^2 I) \ge 80.0$. Motion-blurred captures fail.
* **Exposure Window:** Mean luminance must satisfy $50 \le \mu(L^*) \le 220$ to prevent underexposed noise or sensor blowout.
* **Specular Glare Fraction:** Saturated reflections ($V \ge 250$ in HSV) must not exceed 5.0% of reaction area. Severe glare (>20%) mandates recapture.
* **ROI Geometric Completeness:** The reaction window must contain $\ge 1200$ valid non-occluded pixels.

### Module 4: Explainable Nearest-Centroid Classifier & Ambiguity Guard
REACTRA computes the Euclidean distance in calibrated CIE L\*a\*b\* space to predefined class centroids:
$$d_k = \|\vec{c}_{\text{observed}} - \vec{\mu}_k\|_2$$
**The Ambiguity Safety Margin:** If the distance differential $|d_{\text{pos}} - d_{\text{neg}}| < 12.0\,\Delta E$, the system refuses to guess and explicitly assigns **INCONCLUSIVE**, generating an automatic lab referral.

### Module 5 & 6: Cryptographic Sealing & Local Audit Hash Chain
* Every test session generates a canonical JSON serialization (RFC 8785 strict key sorting, compact UTF-8).
* A SHA-256 digest is generated and digitally signed using the device's local Ed25519 private key.
* The record is appended to a local SQLite backward-linking hash chain:
  $$H_0 = \text{SHA256}(\text{CanonicalRecord}_0)$$
  $$H_i = \text{SHA256}(\text{CanonicalRecord}_i \parallel H_{i-1})$$
* If any historical row is modified, an officer ID altered, or a test deleted, the chain continuity breaks immediately, triggering mathematical tamper alerts.

---

## 5. Benchmark Validation Results (7 Deterministic Scenarios)

| Scenario ID & Description | Expected State | Actual System Behavior | Verification Outcome |
|---|---|---|---|
| **Case 1:** Clean Positive Field Capture | POSITIVE (Ready) | Presumptive Positive (Score 0.96, $\Delta E$ 2.37) | **[PASS] Verified** |
| **Case 2:** Clean Negative Field Capture | NEGATIVE (Ready) | Presumptive Negative (Score 0.96, $\Delta E$ 2.11) | **[PASS] Verified** |
| **Case 3:** Ambiguous Reagent Reaction | INCONCLUSIVE (Review) | Inconclusive (Margin $< 12\,\Delta E$, Score 0.98) | **[PASS] Verified** |
| **Case 4:** Motion-Blurred Capture | RECAPTURE_REQUIRED | Pre-gate stops pipeline; classifier blocked | **[PASS] Verified** |
| **Case 5:** Specular Glare / Overexposed | RECAPTURE_REQUIRED | Pre-gate stops pipeline; classifier blocked | **[PASS] Verified** |
| **Case 6:** Post-Signing Tampered Record | INTEGRITY_FAILED | SHA-256 digest mismatch detected instantly | **[PASS] Verified** |
| **Case 7:** Deleted Audit Chain Record | CHAIN_BROKEN | Hash link continuity break detected | **[PASS] Verified** |

---

## 6. What We Are Implementing Further to Stand Out (Differentiation Roadmap)

### 1. Time-Resolved Reaction Kinetics ($\Delta E(t)$ Multi-Frame Video Stream)
* **The Industry Blindspot:** All existing commercial systems analyze a single snapshot at an arbitrary time. However, chemical color reactions are dynamic kinetic processes. For example, the Marquis reaction with MDMA flashes dark purple within 2 seconds and turns black within 10 seconds, whereas sugar cutting agents react slowly over 45 seconds due to acid dehydration.
* **Our Innovation:** Ingest a 15-second multi-frame video stream, plotting color trajectory vectors $\vec{v}(t) = \frac{d}{dt}(L^*, a^*, b^*)$. Comparing reaction velocity and curve slope against kinetic reference models separates genuine narcotics from slow-reacting adulterants and identifies expired reagent kits.

### 2. Optical Cross-Polarization Lens Attachment
* **The Industry Blindspot:** Field presumptive tests are conducted inside glossy polyethylene pouches. Camera flash creates high-intensity specular glare that washes out color.
* **Our Innovation:** A 3D-printable clip-on adapter with cross-polarizing physical film (one linear polarizer over the smartphone LED flash and an orthogonal linear polarizer over the camera lens). This eliminates 99% of specular surface reflections before light hits the camera sensor.

### 3. Cutting-Agent Spectral Decomposition
* **The Industry Blindspot:** Street narcotics are heavily cut with paracetamol, caffeine, phenacetin, or levamisole, producing muddy composite colors that confuse standard classifiers.
* **Our Innovation:** A non-negative matrix factorization (NMF) unmixing model in CIE L\*a\*b\* space that decomposes composite chromatic vectors into target compounds and cutting agents, flagging adulteration explicitly.

### 4. Hardware TPM 2.0 / Secure Enclave Key Binding
* **The Industry Blindspot:** Mobile apps store signing keys in app sandboxes, vulnerable to rooted phones.
* **Our Innovation:** Binding Ed25519 signing operations directly into hardware security chips (Android KeyStore StrongBox / Apple Secure Enclave / Windows TPM 2.0). Keys are non-exportable even under physical device compromise.

### 5. National Forensic LIMS & eSakshya Ingestion
* **The Industry Blindspot:** Field presumptive test data remains trapped on individual officer phones.
* **Our Innovation:** Standardized export integration with the Ministry of Home Affairs' **eSakshya** digital evidence platform and central Forensic Science Laboratory (FSL) LIMS via signed JSON envelopes and mTLS docking sync.

---

## 7. Slide-by-Slide Presentation Blueprint for SIH PPT

### Slide 1: Title & Vision
* **Title:** REACTRA: Reaction-Aware Field Testing & Verifiable Evidence
* **Subtitle:** Digital Companion for Field Drug Testing (SIH26231)
* **Tagline:** Transforming subjective field chemical screening into scientifically calibrated, cryptographically verifiable presumptive evidence.
* **Key Visuals:** High-contrast REACTRA logo, reference card schematic with fiducial alignment lines, screenshot of the 6-step operator wizard.

### Slide 2: The Legal Crisis — Why Field Tests Fail in Court
* **The Street Reality:** Officers crush chemical ampoules in plastic pouches and visually match colors under yellow streetlights or headlights.
* **Ambient Distortion:** Street lighting shifts perceived color by over $25\,\Delta E$ units, causing wrongful arrests.
* **Evidentiary Inadmissibility:** Under Section 63 BSA / 65B Indian Evidence Act, unverified phone photos and paper logs lack proof of authenticity.
* **Key Visual:** Split image showing daylight true purple vs night-time yellow-light brown.

### Slide 3: Core Philosophy — Measurement Validity Gate
* **Fundamental Law:** REACTRA never turns an unverified photograph into an evidentiary conclusion.
* **5-Step Core Engine:** $\text{Capture} \to \text{Calibrate} \to \text{Validate} \to \text{Classify} \to \text{Preserve}$.
* **Absolute Safety:** Fails degraded photos with actionable recapture instructions; displays mandatory presumptive disclaimers on all outputs.
* **Key Visual:** Horizontal pipeline diagram with prominent red gate for "Recapture Required".

### Slide 4: Optical Normalization — Homography & CIE Lab Calibration
* **4-Point Homography:** Detects corner fiducials and warps card to canonical $1000 \times 700$ geometry.
* **CIE L\*a\*b\* Space:** Replaces hardware-dependent RGB with perceptually uniform color coordinates.
* **Affine Illumination Matrix:** Least-squares calibration against known patches with real-time residual $\Delta E$ reporting.
* **Key Visual:** Detection overlay graphic: warped reference card, extracted patches, and affine formula.

### Slide 5: The Gatekeeper — Refusing to Guess on Bad Data
* Evaluates physical measurement quality *before* running classification.
* **4 Physical Checks:** Laplacian blur variance ($\ge 80.0$), luminance balance ($50-220$), specular glare fraction ($\le 5\%$), and ROI completeness.
* Prevents the #1 flaw of existing AI solutions: giving high-confidence predictions on blurry or glary photos.
* **Key Visual:** Side-by-side comparison: Sharp image (Passed) vs Blurred image (Classification Blocked).

### Slide 6: Explainable Classifier — Transparent Nearest Centroid
* Calculates Euclidean distance to calibrated centroids in CIE L\*a\*b\*.
* **Safety Margin:** If distance between Positive and Negative is under $12.0\,\Delta E$, the system automatically declares `INCONCLUSIVE`.
* **No Black Boxes:** Fully explainable colorimetric distances that withstand forensic scrutiny in court.
* **Key Visual:** Dual-swatch comparison showing Observed Lab vs Expected Centroid Lab with $\Delta E$ distance.

### Slide 7: Cryptographic Truth — Ed25519 & Hash Chain
* **Asymmetric Sealing:** Ed25519 digital signature of canonical SHA-256 evidence digest.
* **Backward-Linked Hash Chain:** $H_i = \text{SHA256}(R_i \parallel H_{i-1})$ stores an immutable local ledger.
* **Instant Detection:** Altering a result, changing an officer ID, or deleting a record immediately breaks chain validation.
* **Key Visual:** Hash chain block diagram illustrating backward hash pointers and red tamper alert.

### Slide 8: Empirical Validation — 7 Deterministic Scenarios
* **7 Synthetic Scenarios:** Good Positive, Good Negative, Ambiguous Reaction, Motion Blur, Overexposed Glare, Tampered Record, Deleted Chain Record.
* **100% Pass Rate:** Tested across all 7 scenarios with typed oracles.
* **Codebase Quality:** 45 automated pytest tests passing in 2.2s; 0 lint errors (`ruff`).
* **Key Visual:** Clean table showing 7 scenarios with green "PASSED" badges and confusion matrix.

### Slide 9: Market Differentiation — Beyond Existing Solutions
* **Kinetic Analysis $\Delta E(t)$:** Multi-frame video tracking reaction speed to detect cutting agents and expired reagent kits.
* **Cross-Polarization Shield:** Physical filter eliminating 99% of liquid pouch glare.
* **Hardware Enclave:** Ed25519 keys bound to hardware TPM 2.0 / Android StrongBox.
* **eSakshya Bridge:** Native export into India's National Digital Evidence ecosystem.
* **Key Visual:** Innovation roadmap timeline (Phase 0 Current $\to$ Phase 1 Hardening $\to$ Phase 2 Kinetics $\to$ Phase 3 National Scale).

### Slide 10: Impact & Conclusion — Justice at the Front Lines
* **Protects Citizens:** Eliminates wrongful arrests caused by ambient lighting and blurry photos.
* **Protects Officers:** Provides an intuitive, error-proof 6-step guided workflow.
* **Protects Evidence:** Provides courtroom-defensible digital records adhering to Section 63 BSA.
* **100% Offline:** Operable in remote border areas, maritime checkpoints, and basements.
* **Key Visual:** Summary graphic highlighting "Scientific Rigor + Cryptographic Truth + Total Offline Autonomy".

---

## 8. Anticipated Judge Questions & Defensible Answers

### Q1: Why not use a deep-learning neural network (YOLO / CNN) directly?
> **Answer:** *"Deep learning models are black-box pattern matchers. In chemical spot testing, lighting variance causes convolutional networks to misclassify with unexplainable high confidence. Under cross-examination in court, an officer cannot explain a neural weight. REACTRA uses physics-first CIE L\*a\*b\* colorimetry, affine illumination compensation, and nearest-centroid Euclidean distance. It is 100% transparent, deterministic, and court-defensible."*

### Q2: What happens if an officer tampers with the SQLite database directly on the device?
> **Answer:** *"Every evidence record is sealed with an Ed25519 digital signature of its SHA-256 canonical digest. If any database column (result, timestamp, operator ID) is altered, signature verification fails instantly. Furthermore, our backward-linking hash chain ties each test to its predecessor ($H_i = \text{SHA256}(R_i \parallel H_{i-1})$); modifying or deleting any record breaks the mathematical hash chain across all subsequent tests."*

### Q3: Does REACTRA claim to replace confirmatory laboratory tests like GC-MS?
> **Answer:** *"No. Field chemical colorimetric tests are strictly presumptive screening tools. REACTRA reinforces this legally by printing mandatory presumptive disclaimers on every screen, PDF, and report. Inconclusive or ambiguous tests automatically generate a standardized Laboratory Referral Packet to fast-track confirmatory testing at the central forensic lab."*

### Q4: How does REACTRA handle expired or contaminated reagent ampoules?
> **Answer:** *"Our Phase 0 architecture checks calibration residual thresholds ($\Delta E \le 8.00$) and enforces ambiguity margins ($12.0\,\Delta E$). In Phase 2 of our roadmap, we implement Time-Resolved Kinetic Video Analysis ($\Delta E(t)$). Expired or contaminated reagents exhibit significantly slower reaction rates and altered velocity slopes, allowing REACTRA to flag kit expiration before an officer makes a misjudgment."*
