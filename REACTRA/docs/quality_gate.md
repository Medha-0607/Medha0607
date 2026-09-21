# REACTRA — Measurement Validity Gate Architecture

**Problem Statement:** SIH26231 — Digital Companion for Field Drug Testing  
**Component:** `src/rectra/vision/quality_gate.py`  

---

## 1. Core Mandate

Field colorimetric spot tests are vulnerable to optical corruption. If a degraded image is fed into a classifier, the classifier will compute mathematical distances to colour centroids regardless of physical reliability, producing dangerous false interpretations.

**REACTRA Core Rule:**  
The quality gate MUST genuinely precede classification. If measurement conditions fail, the classifier is strictly blocked from executing.

$$\text{CAPTURE} \longrightarrow \text{QUALITY GATE} \longrightarrow \begin{cases} \text{FAIL} \implies \text{STOP} \ (\text{RECAPTURE REQUIRED}) \\ \text{PASS} \implies \text{CALIBRATE} \longrightarrow \text{CLASSIFY} \end{cases}$$

---

## 2. Quantitative Quality Checks

| Check | Metric | Mathematical Method | Threshold | Action on Failure |
|---|---|---|---|---|
| **Blur** | High-Frequency Variance | Laplacian variance $\sigma^2(\nabla^2 I)$ | $\ge 80.0$ | `RECAPTURE REQUIRED` |
| **Underexposure** | Mean Luminance | $\bar{Y} = \frac{1}{N}\sum Y_i$ | $\ge 50.0$ | `RECAPTURE REQUIRED` |
| **Overexposure** | Mean Luminance | $\bar{Y} = \frac{1}{N}\sum Y_i$ | $\le 220.0$ | `RECAPTURE REQUIRED` |
| **Specular Glare** | Saturated Pixel Ratio | $\frac{\sum [R=255 \land G=255 \land B=255]}{W \times H}$ | $\le 5.0\%$ | Moderate: `REVIEW`<br>Severe ($>20\%$): `RECAPTURE` |
| **Card Presence** | 4-Corner Geometry | ArUco dictionary + contour convex quadrilateral | Confidence $\ge 0.70$ | `RECAPTURE REQUIRED` |
| **Calibration Residual** | Mean Colour Error | Least-squares residual $\Delta E_{76}$ | $\le 8.00$ | `REVIEW REQUIRED` |
| **Reaction ROI** | Pixel Sufficiency | Area of segmented reaction zone | $\ge 500$ px | `RECAPTURE REQUIRED` |

---

## 3. Structured Failure Reporting

When the quality gate flags an issue, it returns structured, actionable feedback rather than a generic error:
- **Exact Metric:** e.g., `Blur detected (Laplacian variance 1.0 < threshold 80.0)`.
- **Operator Guidance:** e.g., `Adjust ambient illumination to avoid specular glare and stabilize camera.`
- **Classification Gating:** `classification` field is set to `None`.
