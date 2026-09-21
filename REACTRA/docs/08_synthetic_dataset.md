# 08 — Synthetic Dataset & Benchmark Specification

## 1. Ethical & Scientific Policy

RECTRA operates under a strict **Zero Illegal Substances / Synthetic Benchmark Policy**:
- No real narcotics, illegal drugs, or controlled chemical substances were acquired, handled, or tested.
- All evaluation imagery is programmatically generated using mathematically defined CIE Lab nominal colour values, perspective transforms, Gaussian blurs, and specular glare overlays.
- Synthetic ground truth enables **100% reproducible, objective validation** without human labeling ambiguity or chemical hazards.

---

## 2. Dataset Structure & Generation Parameters

Generated via `scripts/generate_demo_data.py` (Random Seed: 42):

```
data/demo/
├── ground_truth.json
├── positive/
│   ├── DEMO-POS-001.png ... DEMO-POS-005.png
├── negative/
│   ├── DEMO-NEG-001.png ... DEMO-NEG-005.png
├── inconclusive/
│   ├── DEMO-INC-001.png ... DEMO-INC-005.png
└── edge_cases/
    ├── DEMO-EDGE-BLURRED.png
    └── DEMO-EDGE-OVEREXPOSED.png
```

### Class Distribution

1. **POSITIVE (5 samples):**
   - Target Reagent Nominal Lab: $L=43.5, a=43.0, b=20.0$ (Deep reddish-violet presumptive indication).
   - Variations: Subtle illumination shifts, slight rotation, minor perspective keystone.
2. **NEGATIVE (5 samples):**
   - Target Reagent Nominal Lab: $L=78.0, a=-10.0, b=45.0$ (Unreacted pale yellow reagent).
   - Variations: Illumination shifts, sensor noise.
3. **INCONCLUSIVE (5 samples):**
   - Target Reagent Nominal Lab: $L=60.7, a=16.5, b=32.5$ (Ambiguous transitional brown midpoint colour).
   - Distance difference $| \Delta E_{\text{pos}} - \Delta E_{\text{neg}} | < 12.00$ margin.
4. **Edge Cases (2 samples):**
   - Motion Blur: Strong Gaussian kernel ($k=25$), reducing Laplacian variance to $< 30.0$.
   - Overexposure / Glare: Saturated specular highlight ($R, G, B \ge 254$) covering $> 10\%$ of image area.

---

## 3. Ground Truth Tracking

Every sample in `data/demo/ground_truth.json` records:
- `filename` and `relative_path`
- `ground_truth_class` (`POSITIVE`, `NEGATIVE`, `INCONCLUSIVE`)
- `nominal_lab` coordinates
- `expected_gate_status` (`VALID`, `REVIEW`, `RECAPTURE`)
- `description` of perturbations applied
