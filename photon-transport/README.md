# Photon transport

Photons from a source, a slab that absorbs some of them, a detector that counts
the rest. Two estimators for the same number: one simulates what each photon
does, the other integrates it. They agree, and one of them needs 200 000× fewer
photons. 282 lines of core.

| | |
|---|---|
| **Level** | L1 derive · L2 implement · L3 experiment |
| **Domain** | [`physics.py`](physics.py) — 136 lines, no sampling loop in it |
| **Methods** | [`analog.py`](methods/analog.py) 25 · [`weighted.py`](methods/weighted.py) 32 |
| **Tests** | 56, split into domain, contract, and where the methods diverge |
| **Migrated from** | [`Physics-simulations/Iter_rad_material`](https://github.com/FullFran/Physics-simulations) (2024) |

## Layout

```
physics.py            the domain: emission, free paths, geometry, Beer-Lambert
methods/
  analog.py           sample a free path; the photon gets through or it does not
  weighted.py         never absorb — carry the survival probability
solve.py              run photons, return a value with an error bar
experiments/
  beer_lambert.py     recover the law the estimators were never told
  variance.py         the same answer, and one keeps almost no randomness
  radiograph.py       what that difference looks like as an image
tests/
  test_physics.py         domain laws, no estimator involved
  test_methods.py         the contract, run against both estimators
  test_methods_differ.py  where they legitimately disagree
```

Same dependency rule as everywhere in this repo: **`methods/` imports
`physics`, `physics` imports nobody.** See
[`docs/architecture.md`](../docs/architecture.md).

## 1. What problem does it solve

A source emits photons into a cone. Some distance away sits a slab of material
that absorbs them, and behind that a detector. **What fraction arrives?**

That is a radiograph, and it is also shielding design, dosimetry, and every
"how much of this gets through that" question in radiation physics. The
analytic answer exists for this geometry, which is exactly what makes it worth
building: you can check the simulation against something.

## 2. The equations

Three ideas and the model is complete.

**Emission into a cone.** The solid angle element is
$d\Omega = \sin\theta\thinspace d\theta\thinspace d\phi$, so the flat variable
is the cosine, not the angle:

$$p(\theta)\thinspace d\theta = \sin\theta\thinspace d\theta
\quad\Longleftrightarrow\quad
p(\cos\theta)\thinspace d(\cos\theta) = d(\cos\theta)$$

**The free path.** A photon's chance of surviving a distance $s$ falls
exponentially, so the distance to its next interaction is drawn by inverting
that:

$$p(s) = \mu\thinspace e^{-\mu s}
\qquad\Longrightarrow\qquad
s = -\frac{\ln U}{\mu}, \quad U \sim \mathcal{U}(0,1]$$

**The geometry.** A photon at angle $\theta$ crosses a slab of thickness $L$
along a path of length $L/\cos\theta$. That single factor is the whole angular
dependence, and together the three give the closed form:

$$\boxed{\enspace T = \exp\negthinspace\left(-\frac{\mu L}{\cos\theta}\right)\enspace}$$

Beer–Lambert. Averaged over the cone it becomes an exponential integral with no
elementary form, evaluated by quadrature in
[`cone_transmittance()`](physics.py) to a precision far beyond any Monte Carlo
run — which is what makes it a reference rather than a second opinion.

Note that $\mu$ and $L$ never appear apart. **There is one length scale, the
mean free path $1/\mu$**, and every result is a function of the optical depth
$\mu L$ alone.

## 3. What I implemented

```
physics.sample_direction()    uniform over solid angle, not over the angle
physics.sample_free_path()    inverse transform of the exponential
physics.slab_path()           L / cos(theta)
physics.transmittance()       Beer-Lambert
physics.cone_transmittance()  the same, averaged over the cone by quadrature
physics.check_medium/cone()   passive media, and cones that stay under 90 degrees
methods.analog                sample a free path; count survivors
methods.weighted              never absorb; carry exp(-mu * path)
solve.transmitted()           mean, standard error, photon count, method
```

## 4. What I verified

56 tests, in three groups. Note what is *not* in the contract: variance.
Demanding a common variance would assert something false, and demanding none
would exclude the honest estimator.

| Property | Scope |
|---|---|
| **Beer–Lambert at normal incidence, over several μ and L** | domain |
| μ and L only ever appear as their product | domain |
| A tilted photon crosses exactly 1/cos θ more material | domain |
| A collimated cone reduces to Beer–Lambert exactly | domain |
| Opening the cone can only lower transmission | domain |
| The cone average is bracketed by its axial and most tilted rays | domain |
| **Directions are uniform over solid angle, not over the angle** | domain |
| Free paths are exponential — checked on the survival function, not the mean | domain |
| A free path is never infinite | domain |
| Gain media, negative thickness, 90° cones and grazing rays are rejected | domain |
| **Both estimators land within 4σ of the closed form, over 5 geometries** | contract |
| Transparent and zero-thickness slabs transmit exactly 1 | contract |
| Contributions are probabilities, in [0, 1] | contract |
| The error falls as 1/√N | contract |
| A run is reproducible from its seed | contract |
| **Analog reports one bit per photon; weighted a continuum** | differ |
| **Analog variance is binomial T(1−T) and ignores the cone** | differ |
| **Narrowing the cone widens the gap without bound** | differ |
| **A collimated beam makes the weighted estimator exact** | differ |
| **Weighted matches the analog error bar on under 2% of the photons** | differ |

The row that pays for the entry is the first contract one. Cross-checking two
estimators proves they agree; checking against Beer–Lambert proves they are
right. Both were checked against the closed form *before* they were checked
against each other.

### The experiments

**[`beer_lambert.py`](experiments/beer_lambert.py)** — prediction: a straight
line on a log axis for a collimated beam, bending away as the cone opens.
Neither estimator is told the law.

```
--- 45 degree cone ---
   thickness    analytic                 analog               weighted
        1.00    0.308413      0.306910+-0.00146      0.308490+-0.00011
        3.00    0.030532      0.031040+-0.00055      0.030548+-0.00003
        5.00    0.003171      0.003350+-0.00018      0.003169+-0.00001
```

A methodological note worth more than the plot. The first version used one seed
for every point in the sweep, which reuses the same free paths, pulls every
point the same way, and turns honest 1σ scatter into what reads as a systematic
bias — the analog column sat above theory at *every* thickness. The error bars
were correct throughout; only the eye was fooled. The seed now varies per point.

**[`variance.py`](experiments/variance.py)** — prediction: the gap grows
without bound as the cone narrows, and the analog variance does not move at
all.

```
   cone          T   binomial T(1-T)    analog var    weighted var        ratio
    45d   0.308413          0.213294      0.213201       1.298e-03    1.643e+02
    15d   0.361540          0.230829      0.230730       1.355e-05    1.703e+04
     5d   0.367179          0.232358      0.232242       1.639e-07    1.417e+06
     1d   0.367851          0.232537      0.232422       2.617e-10    8.882e+08

to match the analog error bar of 0.000730 at 400000 photons,
  a 45-degree cone needs    2435 weighted photons (   164x fewer)
  a 15-degree cone needs      24 weighted photons ( 16666x fewer)
  a  5-degree cone needs       2 weighted photons (200000x fewer)
```

The analog variance is $T(1-T)$ to four decimals at every cone angle — it is a
coin flip and nothing about the geometry reaches it. The weighted variance
falls as roughly $\alpha^4$, because the only randomness left is the spread of
path lengths across the cone, and that spread scales as
$1-\cos\alpha \sim \alpha^2$.

**[`radiograph.py`](experiments/radiograph.py)** — the same argument, as a
picture. A sphere with two denser inclusions, 120 photons per pixel, both
estimators.

```
   estimator   RMS error vs exact   worst pixel
      analog             0.027925      0.170133
    weighted             0.000000      0.000000
```

Identical photon budget, and one image is grainy while the other is exact. That
is also why dose matters in a real X-ray: the noise is the counting statistics
of photons the patient absorbed, and the only analog way to halve it is to
quadruple the exposure.

## 5. What I deliberately left out

- **Scattering.** Every photon here travels in a straight line until it is
  absorbed. Compton scattering dominates at diagnostic energies and turns the
  path into a random walk, which is what makes real transport hard — and what
  removes the weighted estimator's shortcut.
- **Energy.** Monochromatic throughout. Real μ depends strongly on energy, and
  beam hardening — the spectrum shifting as the soft part is absorbed first —
  is a first-order effect in radiography.
- **The interaction channels.** Photoelectric, Rayleigh, Compton and pair
  production are one attenuation coefficient here. The 2024 version had stubs
  for all four; see below.
- **Reconstruction.** This projects. Getting the object back from projections
  is tomography, and it is a different entry.
- **Detector physics.** Perfect counting, no efficiency, no blur, no pixel
  cross-talk.
- **Ray tracing in the graphics sense.** No reflection, refraction or shading.
  It was never that.

## Where this stops being right

| Boundary | What happens |
|---|---|
| Scattering | Straight-line paths are wrong, and the weighted estimator loses its analytic path |
| Broad spectra | One μ cannot represent beam hardening; transmission is not exponential in L |
| Cone approaching 90° | The slab path diverges; rejected rather than approximated |
| Very thick slabs | The analog estimator returns almost all zeros and its relative error blows up |
| A zero-variance estimator | "Within 3σ" becomes meaningless — see below |
| Deep optical depth with weighting | Weights underflow to zero long before the analog count would |

**The σ trap is worth its own line**, because it bit during development. The
weighted estimator on a collimated beam gives every photon the same
contribution, so its standard error is float noise rather than a spread.
Dividing by it turned a difference of 0.2 ulp into **447 σ**. The better the
estimator, the more brittle a "within three sigma" check becomes, and
`Estimate.sigma_from` now floors the denominator at what the arithmetic can
resolve.

## Provenance: the 2024 version

Original: `Iter_rad_material/rayosnew.py` and `unfoton.py`, plus a notebook.
The physics in it was right — cosine sampling, the exponential free path, and a
slab path computed as the 3D distance between entry and exit points, which is
$L/\cos\theta$ the long way round. What the rewrite changed:

| | 2024 | now |
|---|---|---|
| Uncertainty | `len(passed)/Nphoto`, and nothing else | mean ± standard error, always |
| Ground truth | none; the simulation was never checked against a law | every estimator pinned to Beer–Lambert first |
| Estimator | analog only | two, behind a contract, with the variance gap measured |
| Reproducibility | bare `np.random`, unseeded | an explicit `rng`, seeded per run |
| `log(rand())` | `rand()` can return 0.0, giving an infinite path | draws on (0, 1] so the singularity is unreachable |
| Cone angle | `maxtheta` defaulted and never passed through, so it could not be changed | a parameter everywhere |
| Loop | Python loop over photons, recomputing coordinates twice per photon | vectorised over the whole batch |
| Unfinished work | `fotoelectrico`, `comtom` and `pares` are `pass`; `raileight` resamples the same cone and is not Rayleigh | scattering declared out of scope instead |
| Tests | none | 56 |

The first two rows are the ones that matter. **A Monte Carlo result without an
error bar is not a measurement** — there is no way to tell whether a
disagreement with theory is a bug or the sample size. And a simulation that is
never checked against a closed form is only ever checked against your
expectations, which is the one thing it was supposed to test.

## Run it

```bash
uv run pytest photon-transport                            # 56 tests
uv run python photon-transport/experiments/beer_lambert.py
uv run python photon-transport/experiments/variance.py
uv run python photon-transport/experiments/radiograph.py
```

## What this sets up

The Monte Carlo half of the repo. [`hopfield/`](../hopfield/) samples a
landscape at zero temperature and [`mlp/`](../mlp/) descends one; this one
estimates an integral by throwing darts at it, and pays the $1/\sqrt{N}$ that
comes with it. Add scattering and it becomes a random walk, which is the same
mathematics as diffusion — and the next thing worth building.
