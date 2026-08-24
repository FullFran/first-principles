# Transfer Matrix Method

Reflection and transmission of light through a stack of thin films, computed
from Snell's law and the Fresnel equations alone. 259 lines of core across two
solvers that must agree with each other.

| | |
|---|---|
| **Level** | L1 derive · L2 implement · L3 experiment |
| **Domain** | [`physics.py`](physics.py) — 119 lines, no algorithm in it |
| **Methods** | [`transfer_matrix.py`](methods/transfer_matrix.py) 44 · [`recursion.py`](methods/recursion.py) 38 |
| **Tests** | 217, of which the contract suite runs against every method |
| **Migrated from** | [`Physics-simulations/Cristal_multicapa`](https://github.com/FullFran/Physics-simulations) (2024, master's course) |

## Layout

```
docs/physics.md       the derivation, from the phenomenon down
physics.py            the domain: Snell, Fresnel, phase, flux, invariants
methods/
  transfer_matrix.py  one way to solve the stack
  recursion.py        another way (Rouard), numerically better behaved
solve.py              orchestration: validate, dispatch, convert to power
tests/
  test_physics.py     domain laws, no solver involved
  test_methods.py     the contract, parametrised over every method
  test_methods_agree.py   the methods cross-checked against each other
```

One dependency rule: **`methods/` imports `physics`, `physics` imports
nobody.** A method receives quantities the domain already computed and returns
amplitudes; it never touches Snell, flux or power.

The split is not filing. It exists because *the physics is the invariant and
the algorithm is a choice* — and the way to prove you understand which is
which is to swap the algorithm and watch every physical law survive. That is
what `test_methods.py` does, and it is the only thing making the folder
boundary real. Without it the directories would be decoration.

## 1. What problem does it solve

Light hits a stack of parallel layers with different refractive indices. At
every interface part reflects and part transmits, and those partial waves
interfere. TMM answers: **given the stack, what fraction of the incident power
comes back and what fraction gets through, at each wavelength and angle?**

Reverse the question and you get materials design — pick the layers so the
stack reflects exactly what you want. That is a Bragg mirror, an
anti-reflection coating, a dielectric filter.

## 2. The equations

Only three ideas. Everything else is bookkeeping. Derived from the problem
downwards — what multilayers are for, the order-of-magnitude estimates, the
branch cut, the scale analysis and where it all stops — in
[`docs/physics.md`](docs/physics.md).

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

That is the whole domain. The two methods are two ways of composing it.

**Transfer matrix** — make each interface and each layer a $2\times2$ matrix
and multiply:

$$I_{ij} = \frac{1}{t_{ij}}\begin{pmatrix}1 & r_{ij}\cr r_{ij} & 1\end{pmatrix}
\qquad
P_k = \begin{pmatrix}e^{-i\delta_k} & 0\cr 0 & e^{i\delta_k}\end{pmatrix}
\qquad
r = \frac{M_{10}}{M_{00}},\enspace t = \frac{1}{M_{00}}$$

**Recursion** — fold one layer at a time, starting at the substrate:

$$r_k = \frac{\rho + r_{k+1}e^{2i\delta}}{1 + \rho\thinspace r_{k+1}e^{2i\delta}}
\qquad
t_k = \frac{\tau\thinspace t_{k+1}e^{i\delta}}{1 + \rho\thinspace r_{k+1}e^{2i\delta}}$$

Same physics, different arithmetic. They agree to $10^{-13}$, and that
agreement is asserted in the suite.

Last step, worth slowing down on. $R = |r|^2$, but **$T \neq |t|^2$** —
transmittance carries the ratio of normal energy flux between substrate and
ambient, and that projection differs per polarisation:

$$T^s = |t|^2\thinspace \frac{\mathrm{Re}(n_f c_f)}{\mathrm{Re}(n_0 c_0)}
\qquad
T^p = |t|^2\thinspace \frac{\mathrm{Re}(n_f c_f^{\ast})}{\mathrm{Re}(n_0 c_0^{\ast})}$$

## 3. What I implemented

```
physics.layer_cosines()       complex Snell with forward-decaying branch
physics.fresnel()             amplitude r, t at one interface
physics.accumulated_phase()   delta across a layer
physics.normal_flux()         the projection that makes T != |t|^2
physics.check_domain()        the invariants, enforced not assumed
methods.transfer_matrix       the matrix product
methods.recursion             Rouard's recursion
solve.amplitudes() / .RT()    dispatch and convert
```

No matrix inversion anywhere — writing the interface matrix in terms of the
Fresnel coefficients removes the `linalg.inv` the 2024 version called twice
per layer.

## 4. What I verified

217 tests. Each encodes something the physics guarantees, and the contract
ones run once per method.

| Property | Why it bites |
|---|---|
| Single interface reproduces closed-form Fresnel | The most basic case in optics |
| Air/glass → R = 0.04 at normal incidence | The number everyone knows by heart |
| Lossless stack: R + T = 1 at every angle, both polarisations | Energy bookkeeping |
| Absorbing film matches the Airy closed form to 1e-13 | Complex index handled, not faked |
| Absorbing film: 0 < A < 1 | The weak version of the row above, kept as a cheap net |
| Absorbing ambient and gain media raise | The two cases that used to fail silently |
| Past the critical angle: R = 1 exactly, no NaN | The branch cut is right |
| Brewster: Rp = 0 at arctan(n₂/n₁) | Polarisation physics, not just algebra |
| Half-wave layer is absentee | Phase convention is right |
| (HL)ᴺ matches the quarter-wave admittance transform | Multi-layer interference is right |
| Reversing a symmetric stack preserves R | Catches index-alignment bugs |
| **Every method agrees with every other to 1e-13** | Two independent algorithms, one answer |

Two experiments push past pass/fail into prediction.

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
  composition stays readable. A spectrum is a loop in the experiment.
- **Inverse design.** The 2024 original had a genetic optimiser and a Keras
  surrogate bolted on. That is a different problem and does not belong in an
  implementation meant to be read.
- **Gain media and absorbing ambients.** Not approximated — refused.

## Where this stops being right

Verified inside a domain, not in general. The boundaries, measured rather
than assumed:

| Boundary | What happens | Handling |
|---|---|---|
| Ambient with Im(n) > 0 | incident power is undefined; unguarded it returned R = 5.83, T = −4.82 | `ValueError` |
| Gain medium, Im(n) < 0 | the forward-decaying branch rule stops holding; unguarded it returned T = 1.27, A = −0.29 | `ValueError` |
| ~20 µm of metal in one layer | `transfer-matrix` overflows `M₀₀` and r goes NaN | use `method="recursion"`, which cannot grow |
| Anything in the omissions list above | not modelled | out of scope by design |

Both `ValueError`s exist because probing found them, not because I reasoned my
way there. That is worth recording: the suite was green and the two holes were
wide open. **A test suite proves the cases you thought of.**

The third row is the one that pays for the architecture. Two methods, one
domain: the physics is identical to 1e-13 and only the numerical ceiling
differs, which is exactly the distinction the folder split claims to make.

## Run it

```bash
uv run pytest tmm                            # 217 tests
uv run python tmm/experiments/bragg_mirror.py
uv run python tmm/experiments/brewster.py
```

```python
from solve import RT
RT("s", [1.0, 2.3, 1.45, 1.52], [0, 60, 95, 0], 550.0)
RT("s", n, d, 550.0, method="recursion")     # same physics, different arithmetic
```
