# Transfer Matrix Method

Reflection and transmission of light through a stack of thin films, computed
from Snell's law and the Fresnel equations alone. About 120 lines of core.

| | |
|---|---|
| **Level** | L1 derive · L2 implement · L3 experiment |
| **Core** | [`core.py`](core.py) — 125 lines, 86 without comments |
| **Migrated from** | [`Physics-simulations/Cristal_multicapa`](https://github.com/FullFran/Physics-simulations) (2024, master's course) |

## 1. What problem does it solve

Light hits a stack of parallel layers with different refractive indices. At
every interface part reflects and part transmits, and those partial waves
interfere. TMM answers: **given the stack, what fraction of the incident power
comes back and what fraction gets through, at each wavelength and angle?**

Reverse the question and you get materials design — pick the layers so the
stack reflects exactly what you want. That is a Bragg mirror, an
anti-reflection coating, a dielectric filter.

## 2. The equations

Only three ideas, and the whole implementation is their product.

**Snell**, written so it survives absorption and total internal reflection.
The transverse wavevector $n\sin\theta$ is conserved, so

$$\cos\theta_k = \sqrt{1 - \left(\frac{n_0\sin\theta_0}{n_k}\right)^2}$$

evaluated in the complex plane. The `arcsin` form found in every textbook
throws away exactly the two interesting cases.

**Fresnel**, from the continuity of the tangential fields at one interface:

$$r^s_{ij} = \frac{n_i c_i - n_j c_j}{n_i c_i + n_j c_j}
\qquad
r^p_{ij} = \frac{n_j c_i - n_i c_j}{n_j c_i + n_i c_j}
\qquad c_k \equiv \cos\theta_k$$

**Phase**, accumulated crossing a layer of thickness $d_k$:

$$\delta_k = \frac{2\pi}{\lambda} n_k c_k d_k$$

Assemble. Each interface and each layer becomes a $2\times2$ matrix acting on
the pair (forward, backward) amplitude:

$$I_{ij} = \frac{1}{t_{ij}}\begin{pmatrix}1 & r_{ij}\\ r_{ij} & 1\end{pmatrix}
\qquad
P_k = \begin{pmatrix}e^{-i\delta_k} & 0\\ 0 & e^{i\delta_k}\end{pmatrix}$$

$$M = I_{01}\,P_1\,I_{12}\,P_2\cdots I_{N-2,N-1}
\qquad
r = \frac{M_{10}}{M_{00}} \qquad t = \frac{1}{M_{00}}$$

The last step is the one worth slowing down on. $R = |r|^2$, but
**$T \neq |t|^2$** — transmittance carries the ratio of normal energy flux
between substrate and ambient, and that projection differs per polarisation:

$$T^s = |t|^2\,\frac{\mathrm{Re}(n_f c_f)}{\mathrm{Re}(n_0 c_0)}
\qquad
T^p = |t|^2\,\frac{\mathrm{Re}(n_f c_f^{*})}{\mathrm{Re}(n_0 c_0^{*})}$$

## 3. What I implemented

```
layer_cosines()        complex Snell with forward-decaying branch selection
fresnel()              amplitude r, t at one interface, both polarisations
amplitudes()           the matrix product -> stack r, t
RT()                   power reflectance and transmittance
```

No matrix inversion anywhere — writing the interface matrix in terms of the
Fresnel coefficients removes the `linalg.inv` that the 2024 version called
twice per layer.

## 4. What I verified

45 property tests. Each encodes something the physics guarantees.

| Property | Why it bites |
|---|---|
| Single interface reproduces closed-form Fresnel | The most basic case in optics |
| Air/glass → R = 0.04 at normal incidence | The number everyone knows by heart |
| Lossless stack: R + T = 1 at every angle, both polarisations | Energy bookkeeping |
| Absorbing film: 0 < A < 1 | Complex index handled, not faked |
| Past the critical angle: R = 1 exactly, no NaN | The branch cut is right |
| Brewster: Rp = 0 at arctan(n₂/n₁) | Polarisation physics, not just algebra |
| Half-wave layer is absentee | Phase convention is right |
| (HL)ᴺ matches the quarter-wave admittance transform | Multi-layer interference is right |
| Reversing a symmetric stack preserves R | Catches index-alignment bugs |

Two experiments push past pass/fail into prediction:

**[`experiments/bragg_mirror.py`](experiments/bragg_mirror.py)** — peak
reflectance matches the analytic admittance to six decimals, and the stopband
width converges to the contrast-only prediction:

```
 periods     R peak   analytic   stopband
       2   0.658887   0.658887     0.0909
       4   0.936438   0.936438     0.1101
       8   0.998363   0.998363     0.2319
      16   0.999999   0.999999     0.2927

analytic stopband (infinite stack): 0.2911
```

More periods buy **depth, never width** — the width is set by the index
contrast alone. (The measured width uses a crude 99%-of-peak threshold, which
only becomes meaningful once the band is flat, hence the drift at low N.)

**[`experiments/brewster.py`](experiments/brewster.py)** — the numerical
minimum of Rp lands on arctan(n₂/n₁) to grid resolution, and it is a real
zero (~1e-8, limited by the angular grid):

```
       interface      found   arctan(n2/n1)    Rp at min
    air -> glass    56.651d         56.659d    7.677e-09
  air -> silicon    75.557d         75.548d    1.090e-07
    glass -> air    33.339d         33.341d    2.352e-09
```

## 5. What I deliberately left out

- **Incoherent / thick layers.** Everything here is fully coherent.
- **Anisotropy and magnetic media.** Scalar n, μ = 1.
- **Field profiles inside the stack.** Only the exterior r and t.
- **Dispersion.** n is a constant, not n(λ).
- **Vectorisation over wavelength.** One λ per call, on purpose — the
  matrix product stays readable. A spectrum is a loop in the experiment.
- **Inverse design.** The 2024 original had a genetic optimiser and a Keras
  surrogate bolted on. That is a different problem and does not belong in an
  implementation meant to be read.

## Provenance: what the 2024 version got wrong

Worth recording, because the failures are more instructive than the code.

| Probe | 2024 original | Correct |
|---|---|---|
| Air → glass, single interface | R = 0.000000 | 0.04 |
| Absorbing film, 30° | A = **−0.247579** | 0 < A < 1 |
| Glass → air, 60° (past critical) | R = **nan** | 1.0 |

The root cause of the first is one line: the exit medium was hardcoded to
`n[0]`, so the substrate index was silently discarded. The other two come
from `np.arcsin`, which cannot represent a complex angle.

**The lesson that made this migration worth doing:** the original satisfied
R + T = 1 to six decimals in every one of those broken cases. Energy
conservation is necessary and nowhere near sufficient. A test suite that only
checks conservation would have signed off on all three defects.

## Run it

```bash
uv run pytest tmm                            # 45 tests
uv run python tmm/experiments/bragg_mirror.py
uv run python tmm/experiments/brewster.py
```
