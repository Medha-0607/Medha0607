# 07 — Illumination Calibration Methodology

## 1. The Physical Colour Challenge

When a field officer captures an image of a chemical reaction spot:
$$\text{Sensor RGB} = \int E(\lambda) \cdot R(\lambda) \cdot S(\lambda) \, d\lambda$$
where $E(\lambda)$ is ambient illumination, $R(\lambda)$ is surface reagent reflectance, and $S(\lambda)$ is camera sensor spectral sensitivity.

A change in ambient light (e.g. tungsten streetlamp $2700\text{K}$ vs overcast daylight $6500\text{K}$) shifts the raw RGB values by up to $30\text{--}40$ CIE $\Delta E$ units. Without physical calibration, computer vision algorithms misclassify the colour.

---

## 2. CIE Lab Colour Space

RECTRA maps all colours to **CIE $L^*a^*b^*$ (1976)**:
- $L^*$: Perceptual lightness ($0 = \text{black}$, $100 = \text{diffuse white}$).
- $a^*$: Red-green opponent axis (negative = green, positive = red).
- $b^*$: Yellow-blue opponent axis (negative = blue, positive = yellow).

Color differences are calculated using Euclidean distance:
$$\Delta E_{76} = \sqrt{(\Delta L^*)^2 + (\Delta a^*)^2 + (\Delta b^*)^2}$$
A $\Delta E_{76} \approx 2.3$ corresponds to the Just Noticeable Difference (JND) for human vision.

---

## 3. Least-Squares Affine Calibration Mapping

The RECTRA reference card includes 6 canonical color patches with known nominal coordinates defined in the assay profile:
- White ($L=95.0, a=0.0, b=0.0$)
- Neutral Gray 50% ($L=50.0, a=0.0, b=0.0$)
- Deep Black ($L=10.0, a=0.0, b=0.0$)
- Reference Red ($L=45.0, a=55.0, b=30.0$)
- Reference Green ($L=50.0, a=-40.0, b=25.0$)
- Reference Blue ($L=35.0, a=10.0, b=-45.0$)

During test analysis:
1. Observed patches $\mathbf{O} \in \mathbb{R}^{N \times 4}$ are sampled with an augmented bias column $[L_{\text{obs}}, a_{\text{obs}}, b_{\text{obs}}, 1.0]$.
2. Canonical target patches $\mathbf{C} \in \mathbb{R}^{N \times 3}$ are retrieved from profile JSON.
3. The affine transformation matrix $\mathbf{M} \in \mathbb{R}^{4 \times 3}$ is solved via ordinary least squares:
   $$\mathbf{M} = (\mathbf{O}^T \mathbf{O})^{-1} \mathbf{O}^T \mathbf{C}$$
4. The raw test reaction spot colour $[L_{\text{raw}}, a_{\text{raw}}, b_{\text{raw}}, 1.0]$ is corrected:
   $$[L_{\text{corr}}, a_{\text{corr}}, b_{\text{corr}}] = [L_{\text{raw}}, a_{\text{raw}}, b_{\text{raw}}, 1.0] \cdot \mathbf{M}$$
5. Calibration residual error is computed across all reference patches:
   $$\overline{\Delta E}_{\text{residual}} = \frac{1}{N} \sum_{i=1}^N \Delta E_{76}(\mathbf{O}_i \mathbf{M}, \mathbf{C}_i)$$
   If $\overline{\Delta E}_{\text{residual}} > 8.00$, the calibration is declared **Invalid**, warning the operator of extreme illumination non-uniformity or card damage.
