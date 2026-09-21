# 10 — Model Evaluation & Performance Report

## 1. Executive Summary

RECTRA's presumptive interpretation engine was evaluated against the synthetic benchmark dataset (`data/demo/ground_truth.json`).
- **Total Evaluated Samples:** 15 standard synthetic samples (5 Positive, 5 Negative, 5 Inconclusive) + 2 physical edge cases.
- **Classifier Architecture:** Nearest Centroid in calibrated CIE $L^*a^*b^*$ space with an inconclusive margin $\Delta E = 12.00$.
- **Zero Cloud / Local Execution:** Evaluation executed entirely on a single CPU thread with sub-millisecond inference per sample.

---

## 2. Quantitative Performance Metrics

### Confusion Matrix ($3 \times 3$)

```
                  Predicted POSITIVE  Predicted NEGATIVE  Predicted INCONCLUSIVE
Actual POSITIVE           5                   0                     0
Actual NEGATIVE           0                   5                     0
Actual INCONCLUSIVE       0                   0                     5
```

### Precision, Recall, and F1 Scores

| Target Class | Support | Precision | Recall | F1-Score |
|---|:---:|:---:|:---:|:---:|
| **POSITIVE** | 5 | 1.0000 | 1.0000 | 1.0000 |
| **NEGATIVE** | 5 | 1.0000 | 1.0000 | 1.0000 |
| **INCONCLUSIVE** | 5 | 1.0000 | 1.0000 | 1.0000 |
| **Macro Average** | **15** | **1.0000** | **1.0000** | **1.0000** |

---

## 3. Physical Quality Gate Performance

| Edge Case Test | Defect Type | Expected Gate Status | Measured Gate Status | Quality Gate Failures Detected |
|---|---|:---:|:---:|---|
| `DEMO-EDGE-BLURRED.png` | Motion Blur | `RECAPTURE` | `RECAPTURE` | Laplacian Variance $21.4 < 80.0$ threshold |
| `DEMO-EDGE-OVEREXPOSED.png` | Specular Glare | `RECAPTURE` / `REVIEW` | `RECAPTURE` | Saturated pixel fraction $12.8\% > 5.0\%$ threshold |

Both degraded captures were **successfully blocked from reaching the classifier**, preventing false conclusions.

---

## 4. Methodological Safeguards

1. **No Fake Accuracy Claims:** High metrics reflect performance on a controlled synthetic benchmark with known nominal CIE Lab ground truth. Real-world chemical assays feature continuous spectrums, reagent degradation, and cutting adulterants.
2. **Dynamic Generation:** Metrics are computed by `src/rectra/classification/evaluation.py` and written to `runtime/evaluation_results.json`. The UI loads this dynamic file directly.
