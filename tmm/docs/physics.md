# Light through a stack of thin films

> The physics behind [`tmm/`](../README.md), derived from the problem rather than
> from the formula. Read this if you want to know *why* the equations in
> `tmm/physics.py` are those and not others.

This document follows one cycle, and the cycle is the point:

```
phenomenon → question → order of magnitude → assumptions → minimal model
   → equations → scale analysis → closed forms → simulation → validation
   → limits of the model → next question
```

The middle is what a degree teaches. The two ends — framing the question and
knowing where the model stops — are what actually separates people who solve
new problems from people who apply formulas. So the two ends get the space
here.

**Contents**

1. [The phenomenon](#1-the-phenomenon)
2. [What multilayers are for](#2-what-multilayers-are-for)
3. [Before you calculate](#3-before-you-calculate)
4. [Why the naive answer fails](#4-why-the-naive-answer-fails)
5. [The minimal model](#5-the-minimal-model)
6. [The equations](#6-the-equations)
7. [Composing the stack: three ways, one physics](#7-composing-the-stack-three-ways-one-physics)
8. [Scale analysis: reading the answer off the phase](#8-scale-analysis-reading-the-answer-off-the-phase)
9. [Closed forms worth memorising](#9-closed-forms-worth-memorising)
10. [What the simulation showed](#10-what-the-simulation-showed)
11. [Where the model stops being true](#11-where-the-model-stops-being-true)
12. [The essentials](#12-the-essentials)
13. [Open questions](#13-open-questions)
14. [References](#14-references)

---

## 1. The phenomenon

A soap bubble is colourless liquid and it is violently coloured. A puddle with
a drop of oil on it is coloured. A beetle's shell is coloured and has no
pigment in it at all. Your glasses have a purple sheen; the front element of a
camera lens has a green one. A laser mirror looks like a piece of glass and
returns 99.999% of what hits it.

All of these are the same object: **a few layers of transparent material,
each a fraction of a wavelength thick, stacked on top of each other.**

None of them has any absorption doing the work. The colour is not a dye. It is
interference — the same phenomenon as two speakers cancelling in a room, run at
$5\times10^{14}$ Hz.

> **The question.**
> A stack of $N$ parallel layers, each with refractive index $n_k$ and
> thickness $d_k$. A plane wave arrives from outside at angle $\theta_0$ with
> vacuum wavelength $\lambda$.
> **What fraction of the incident power comes back, and what fraction gets
> through?**

Call those $R$ and $T$. That is the entire forward problem, and it is what
`tmm/` computes.

Reverse it — choose the $n_k$ and $d_k$ so that $R(\lambda,\theta)$ is the
curve you want — and you have the inverse problem, which is an entire
industry. The forward problem has to be exact and cheap first, because the
inverse one calls it a few million times.

---

## 2. What multilayers are for

Worth going through before any equations, because the applications tell you
which regime of the equations matters.

### 2.1 Removing a reflection (anti-reflection coatings)

Bare glass reflects about 4% per surface. That sounds negligible until you
count surfaces: a six-element camera lens has twelve, and $0.9574^{12} = 0.59$
— **41% of the light is gone**, and most of it is not gone, it is bouncing
around inside the barrel producing flare and washing out contrast.

Bare silicon is worse. At $n \approx 3.9$ the front surface of a solar cell
reflects $\left(\frac{1-3.9}{1+3.9}\right)^2 = 0.35$ before the semiconductor
gets a chance — 35% of the light. One quarter-wave layer of silicon nitride
takes that to 0.02% at the design wavelength. That single layer is worth more
than most of the process optimisation downstream of it.

The history is a good lesson in noticing things. Rayleigh (1886) observed that
*tarnished* glass transmitted more light than fresh glass — the opposite of
what anyone would guess. Taylor patented deliberate chemical tarnishing in
1904 but never made it reproducible. Smakula at Zeiss patented evaporated
coatings in 1935, and the modern coating industry starts there.

### 2.2 Making a perfect reflection (Bragg mirrors / DBRs)

Stack quarter-wave pairs of a high and a low index and every partial
reflection comes back in phase. Reflectance approaches 1 exponentially in the
number of periods, with no metal and therefore no absorption loss.

- **Semiconductor lasers.** A VCSEL has gain of a fraction of a percent per
  pass, so its cavity mirrors must exceed 99.9%. Nothing metallic does that.
  20–40 periods of AlAs/GaAs do.
- **EUV lithography.** At 13.5 nm every material absorbs and nothing refracts
  usefully — there are no lenses. The whole optical train is Mo/Si multilayer
  mirrors, ~50 bilayers, ~70% reflectance each. Every mirror in the chain
  costs you 30%, which is why there are as few as physically possible.
- **Gravitational-wave detectors.** LIGO's test masses are multilayer coatings
  where the *loss* budget is parts per million, and where coating thermal
  noise is a limiting noise source for the instrument.

### 2.3 Choosing which colours pass (filters)

Dichroic beamsplitters, notch filters, fluorescence-microscopy filter cubes,
low-emissivity window coatings, heat mirrors, laser-line filters. Same
mathematics, aimed at a target curve rather than at a single number.

### 2.4 Colour without pigment (structural colour)

Morpho butterfly wings, beetle elytra, peacock feathers, fish scales, the
inside of a shell. Biology discovered dielectric stacks long before Zeiss.
The signature is angle dependence: a pigment does not change hue when you
tilt it and a multilayer always does, because $\delta \propto \cos\theta$.

### 2.5 Measuring things (ellipsometry)

Run the model *backwards* against measured $(\Psi, \Delta)$ and you recover
the thickness and index of a film to sub-nanometre precision. Ellipsometry is
one of the most-used metrology techniques in semiconductor fabs, and the
forward model inside it is exactly the one in this document.

### Papers worth reading

| Reference | Why |
|---|---|
| [Abelès, *Ann. Phys.* **12**, 596 (1950)](https://www.annphys.org/articles/anphys/abs/1950/05/anphys19501205p596/anphys19501205p596.html) | The $2\times2$ characteristic-matrix formulation. The origin of "TMM" |
| [Rouard, *Ann. Phys.* **11**, 291 (1937)](https://www.annphys.org/articles/anphys/abs/1937/07/anphys19371107p291/anphys19371107p291.html) | The recursion, thirteen years earlier. Same physics, different bookkeeping |
| [Yeh, Yariv & Hong, *JOSA* **67**, 423 (1977)](https://opg.optica.org/abstract.cfm?URI=josa-67-4-423) | Bloch theory of periodic stacks. Where the stopband formula comes from |
| [Li, *JOSA A* **13**, 1024 (1996)](https://opg.optica.org/josaa/abstract.cfm?uri=josaa-13-5-1024) | Why the matrix product is numerically unstable and the recursion is not |
| [Katsidis & Siapkas, *Appl. Opt.* **41**, 3978 (2002)](https://opg.optica.org/ao/abstract.cfm?uri=ao-41-19-3978) | Coherent, partially coherent and incoherent layers in one framework |
| [Byrnes, *Multilayer optical calculations*, arXiv:1603.02720](https://arxiv.org/abs/1603.02720) | The careful modern write-up: branch cuts, absorbing ambients, why $T \neq \lvert t\rvert^2$ |
| [Fink et al., *Science* **282**, 1679 (1998)](https://www.science.org/doi/10.1126/science.282.5394.1679) | A 1D stack that reflects at *every* angle — the omnidirectional mirror |
| [Tikhonravov, Trubetskov & DeBell, *Appl. Opt.* **35**, 5493 (1996)](https://opg.optica.org/ao/abstract.cfm?uri=ao-35-28-5493) | Needle optimisation: the inverse problem done properly |

Books: Born & Wolf §1.6 for the derivation, Macleod's *Thin-Film Optical
Filters* for design practice, Yeh's *Optical Waves in Layered Media* for the
periodic-media theory.

---

## 3. Before you calculate

The rule from the book: **write a number down before you read the next
section.** The learning is in the gap between your number and the real one,
and the gap does not exist if you did not commit.

> 1. A quarter-wave anti-reflection layer for green light on glass. **How
>    thick, in nanometres?** How many atoms is that?
> 2. You need a mirror with $R \gt 0.999$ built from layers of $n_H = 2.3$ and
>    $n_L = 1.45$. **How many pairs?** Ten? Fifty? Five hundred?
> 3. A Bragg mirror designed for 550 nm reflects a band, not a line. **How
>    wide is that band?** And does stacking more periods make it wider?

Answers in [§8](#8-scale-analysis-reading-the-answer-off-the-phase) and
[§9](#9-closed-forms-worth-memorising). Two of the three are one line of
arithmetic. If you can do them on a napkin you do not need the code to sanity
check itself — you already know the answer to within a few percent, and the
code's job becomes confirming a prediction rather than producing a surprise.

---

## 4. Why the naive answer fails

The tempting first model: light hits interface 1, some fraction $R_1$ bounces
back; the rest hits interface 2, some fraction bounces back; add them up.

$$R_{\text{naive}} \stackrel{?}{=} R_{01} + T_{01}R_{12}T_{10} + \dots$$

This is wrong, and it is wrong in a way worth understanding because the same
error shows up everywhere in wave physics.

**Powers do not add. Amplitudes add.** The partial waves that come back out
of the stack are coherent with each other — they have a definite relative
phase, set by the extra optical path each one travelled. What arrives at the
detector is

$$r_{\text{total}} = \sum_m r_m e^{i\phi_m},
\qquad R = \left|\sum_m r_m e^{i\phi_m}\right|^2
\thickspace \neq\thickspace \sum_m |r_m|^2$$

The cross terms *are* the phenomenon. Drop them and the soap bubble is grey.

Two consequences that make it more than a technicality:

- **$R$ can be larger than the sum of the parts** (Bragg mirror: 20 interfaces
  each reflecting 8% give 99.99%, not 20×8%), **or smaller** (AR coating: two
  interfaces each reflecting ~2% give 0.0%).
- **A model that adds powers can never produce either.** It is not a worse
  approximation; it is a different physical situation — the incoherent one,
  which is what you actually get if the layer is thicker than the source's
  coherence length ([§11](#11-where-the-model-stops-being-true)).

So the problem is: sum an infinite number of coherent partial waves. That
sounds bad. It collapses to two lines of algebra, and that collapse is the
nice part of the derivation.

---

## 5. The minimal model

Every assumption below buys a specific simplification, and every one of them
fails somewhere real. Listing them is not ceremony — the list *is* the
domain of validity, and it is the thing the tests can never tell you.

| Assumption | What it buys | Where it breaks |
|---|---|---|
| Monochromatic plane wave, $e^{-i\omega t}$ | One $\lambda$, one $\theta$, no wave packets | Focused beams, ultrashort pulses, Goos–Hänchen shift |
| Layers infinite and flat in $x,y$ | Translational invariance ⇒ $k_x$ conserved ⇒ Snell | Roughness, gratings, finite apertures, scattering |
| Piecewise-homogeneous, isotropic $n_k$ | A scalar index per layer | Birefringence, graded index, liquid crystals |
| Non-magnetic, $\mu = 1$ | Impedance is $1/n$, not $\sqrt{\mu/\varepsilon}$ | Metamaterials, magnetic media, RF |
| Linear, local response | Superposition; $n$ independent of intensity | Nonlinear optics, spatial dispersion |
| Passive media, $\operatorname{Im} n \ge 0$ | The forward-decaying branch is well defined | Gain media, lasers — **refused** by `check_domain` |
| Transparent ambient, $\operatorname{Im} n_0 = 0$ | Incident power is well defined | Immersion in an absorbing liquid — **refused** |
| Fully coherent throughout | Amplitudes add everywhere | Thick substrates, broadband sources ([§11](#11-where-the-model-stops-being-true)) |
| $n$ constant, not $n(\lambda)$ | One index per material | Any real spectrum over a wide range |

That is the model. Notice what it does **not** assume: it does not assume the
layers are thin, or lossless, or that the angle is small, or that there are
few of them. Absorption and total internal reflection come out for free, as
long as the algebra is done in the complex plane and the branch is chosen
physically. That is the whole trick of the next section.

---

## 6. The equations

### 6.1 From Maxwell to two scalar problems

In a source-free, linear, isotropic, non-magnetic region every field component
$\psi$ obeys the Helmholtz equation

$$\nabla^2\psi + k_0^2 n^2 \psi = 0, \qquad k_0 = \frac{2\pi}{\lambda}$$

with $\lambda$ the **vacuum** wavelength. Two structural facts collapse this
into something a computer can do in twenty lines.

**Fact 1 — the structure only depends on $z$.** It is invariant under
translation in $x$ and $y$. So we can look for solutions of the form
$\psi(x,z) = \psi(z)\thinspace e^{ik_x x}$, with the plane of incidence taken as $xz$.
At any interface the boundary condition must hold for *all* $x$, and two
functions of $x$ agree everywhere only if their $x$-dependence is identical.
Therefore:

$$\boxed{\thickspace k_x \text{ is the same in every layer}\thickspace }$$

This is Snell's law. Not "a law about rays bending" — a **conservation law
enforced by a symmetry**, exactly like momentum conservation from translational
invariance. Writing $k_x = k_0 n_k \sin\theta_k$ gives back the familiar
$n_0\sin\theta_0 = n_k\sin\theta_k$, but the conserved-quantity form is the one
that survives when $n$ is complex and $\theta$ stops being an angle.

**Fact 2 — the vector problem splits in two.** With the plane of incidence
fixed, Maxwell's equations decouple into two independent scalar problems:

| | Transverse field | Also called | Physical picture |
|---|---|---|---|
| **s** | $E = E_y\hat y$ | TE, $\sigma$ | $E$ perpendicular to the plane of incidence |
| **p** | $H = H_y\hat y$ | TM, $\pi$ | $E$ in the plane of incidence |

Every polarisation state is a superposition of these two, so solving both
solves everything. This is why the code carries a `pol` argument through
every function instead of a $4\times4$ matrix: the physics already
block-diagonalised the problem for us.

### 6.2 The longitudinal wavevector, and why $\arcsin$ is a trap

Inside layer $k$, $k_x^2 + k_{z,k}^2 = k_0^2 n_k^2$, so

$$k_{z,k} = k_0\sqrt{n_k^2 - \left(n_0\sin\theta_0\right)^2}
\thickspace \equiv\thickspace k_0\thinspace n_k\cos\theta_k,
\qquad
\cos\theta_k = \sqrt{1 - \left(\frac{n_0\sin\theta_0}{n_k}\right)^2}$$

This is [`physics.layer_cosines()`](../physics.py). Two things about it.

**Never compute $\theta_k = \arcsin(\cdot)$ and then take its cosine.** The
textbook route throws away precisely the two interesting regimes:

- past the critical angle the argument exceeds 1 and `arcsin` returns `nan`;
- for complex $n_k$ the angle is not a real number at all and the concept of
  "the angle in the absorbing layer" stops being useful.

Work with $\cos\theta_k$ as a complex number from the start and both cases are
just... arithmetic. Total internal reflection becomes a purely imaginary
$\cos\theta$; absorption becomes a complex one. Nothing special-cased.

**The square root has two branches, and choosing between them is physics, not
numerics.** $\sqrt{\cdot}$ returns $\pm$; the wave $e^{ik_z z}$ either decays
or grows as it goes forward. The physical requirement is that a passive medium
attenuate:

$$\operatorname{Im}\negthinspace \left(n_k\cos\theta_k\right) \ge 0
\qquad\text{and, when that is zero,}\qquad
\operatorname{Re}\negthinspace \left(n_k\cos\theta_k\right) \gt 0$$

The first condition says *decay forward, never amplify*. The second picks the
propagating wave that carries energy in $+z$ for the lossless case, where the
first condition alone does not decide. In the code:

```python
q = n * cos_theta
wrong_branch = (q.imag < 0) | ((q.imag == 0) & (q.real < 0))
return np.where(wrong_branch, -cos_theta, cos_theta)
```

This is the clearest example in the whole entry of a rule that *looks*
numerical and is actually a statement about nature — which is why it lives in
`physics.py` and not in a solver. Get it wrong and energy conservation still
holds perfectly; you will just be simulating a medium that amplifies light.

### 6.3 Fresnel: continuity of tangential fields

At an interface with no free charge or current, the tangential components of
$\mathbf{E}$ and $\mathbf{H}$ are continuous. That is the only input. Write
$c_k \equiv \cos\theta_k$ and take a unit-amplitude wave in medium $i$ hitting
medium $j$.

**s-polarisation.** $E_y$ is tangential, so $1 + r = t$. The tangential
magnetic component is $H_x = -\dfrac{k_z}{\omega\mu_0}E_y$, so continuity of
$H_x$ gives $n_ic_i(1-r) = n_jc_jt$. Two equations, two unknowns:

$$r^s_{ij} = \frac{n_ic_i - n_jc_j}{n_ic_i + n_jc_j},
\qquad
t^s_{ij} = \frac{2n_ic_i}{n_ic_i + n_jc_j}$$

**p-polarisation.** Now $H_y$ is the tangential one and
$E_x = \dfrac{k_z}{\omega\varepsilon_0 n^2}H_y$, so the same two steps with
$n \to 1/n$ in the right place give

$$r^p_{ij} = \frac{n_jc_i - n_ic_j}{n_jc_i + n_ic_j},
\qquad
t^p_{ij} = \frac{2n_ic_i}{n_jc_i + n_ic_j}$$

This is [`physics.fresnel()`](../physics.py), verbatim.

> **A convention warning that costs people days.** For p-polarisation, $t^p$
> above is the ratio of the *magnitudes* of the electric fields, not of their
> $x$-components. Different books make different choices here, which is why
> the transmittance formula in §6.5 looks different in different books. It is
> also why, in this convention, $r^p = -r^s$ at normal incidence: a sign
> convention artefact, not physics. $R^s = R^p$ at $\theta = 0$, as it must be
> — at normal incidence there is no plane of incidence to be polarised
> relative to.

**Brewster falls out immediately.** $r^p = 0$ when $n_jc_i = n_ic_j$.
Combined with Snell that gives

$$\tan\theta_B = \frac{n_j}{n_i}$$

and at that angle $\theta_i + \theta_j = 90°$. The physical reading: the
reflected wave is radiated by dipoles driven in medium $j$, which oscillate
along $\mathbf{E}_j$; at Brewster that direction *is* the direction the
reflected ray would have to go, and a dipole does not radiate along its own
axis. Nothing analogous exists for s, whose dipoles are always perpendicular
to the plane. This is the claim [`experiments/brewster.py`](../experiments/brewster.py)
tests numerically.

### 6.4 Phase across a layer

Crossing a layer of thickness $d_k$ once multiplies the amplitude by
$e^{i k_{z,k} d_k}$, so define

$$\delta_k = \frac{2\pi}{\lambda}\thinspace n_k \cos\theta_k\thinspace d_k$$

[`physics.accumulated_phase()`](../physics.py). Real part = phase
advance; imaginary part = attenuation, since
$e^{i\delta} = e^{i\operatorname{Re}\delta}e^{-\operatorname{Im}\delta}$. For a
passive medium on the correct branch $\operatorname{Im}\delta \ge 0$, so
$|e^{i\delta}| \le 1$ **always**. Remember that inequality: it is the entire
reason one of the two solvers cannot overflow ([§7.4](#74-same-physics-different-numerics)).

**That is the whole domain.** Snell, Fresnel, phase. Three ideas, ~40 lines of
Python. Everything after this is bookkeeping — and the point of the repo's
[architecture](../../docs/architecture.md) is that bookkeeping is exactly the part you are
allowed to swap.

### 6.5 Power: why $T \neq |t|^2$

$R = |r|^2$ is safe: the reflected wave travels in the same medium as the
incident one, so the ratio of powers is the ratio of $|E|^2$. Transmission is
not, because the transmitted wave lives in a *different* medium and travels at
a different angle. What is conserved is the component of the time-averaged
Poynting vector **normal to the interface**:

$$S_z = \tfrac12\operatorname{Re}\left(\mathbf{E}\times\mathbf{H}^{\ast}\right)_z$$

Doing that integral for each polarisation, with the field conventions of §6.3:

$$S_z^{\thinspace s} \propto \operatorname{Re}(n\cos\theta)\thinspace |E|^2,
\qquad
S_z^{\thinspace p} \propto \operatorname{Re}(n\cos^{\ast}\negthinspace \theta)\thinspace |E|^2$$

Hence [`physics.normal_flux()`](../physics.py) and

$$T^s = |t|^2\thinspace \frac{\operatorname{Re}(n_fc_f)}{\operatorname{Re}(n_0c_0)},
\qquad
T^p = |t|^2\thinspace \frac{\operatorname{Re}(n_fc_f^{\ast})}{\operatorname{Re}(n_0c_0^{\ast})},
\qquad
A = 1 - R - T$$

The conjugate in the p case is not a typo and it is not cosmetic — it is the
difference between $\mathbf{E}$ and $\mathbf{H}$ being the transverse field,
and it only matters when $\cos\theta$ is complex, i.e. exactly when a layer
absorbs or you are past the critical angle. Which is exactly when you are
least likely to notice you got it wrong.

For transparent media at normal incidence it degenerates to the familiar
$T = |t|^2 n_f/n_0$, and past the critical angle
$\operatorname{Re}(n_fc_f) = 0$ gives $T = 0$ exactly, with no special case in
the code.

> **Where this bites.** If the *ambient* absorbs, "incident power" has no
> unique meaning — the incoming wave is already decaying, so its intensity
> depends on where you measure it. Unguarded, this entry used to return
> $R = 5.83$, $T = -4.82$ and not complain. That is why `check_domain()`
> raises instead of approximating. See Byrnes §5 for the full argument.

---

## 7. Composing the stack: three ways, one physics

### 7.1 One film: sum the infinite series (Airy)

Ambient 0, film 1 of phase $\delta$, substrate 2. Enumerate the partial waves
that come back out:

$$r = r_{01} + t_{01}r_{12}t_{10}e^{2i\delta}
      + t_{01}r_{12}r_{10}r_{12}t_{10}e^{4i\delta} + \cdots
    = r_{01} + t_{01}t_{10}r_{12}e^{2i\delta}\sum_{m\ge0}\left(r_{10}r_{12}e^{2i\delta}\right)^m$$

A geometric series. Sum it, then use the **Stokes relations**, which follow
directly from the Fresnel formulas above:

$$r_{10} = -r_{01},\qquad t_{01}t_{10} = 1 - r_{01}^2$$

and the whole thing collapses:

$$\boxed{\thickspace r = \frac{r_{01} + r_{12}e^{2i\delta}}{1 + r_{01}r_{12}e^{2i\delta}}\thickspace }$$

Infinitely many bounces, one fraction. This is Airy's formula, and it is the
single most useful closed form in the subject — every test in
`test_physics.py` that checks a single film against "the analytic answer"
checks against this.

Note the denominator. It is a resonance: when $r_{01}r_{12}e^{2i\delta} \to -1$
the response blows up. That is a Fabry–Pérot cavity, and it is the same
denominator that will appear in the recursion.

### 7.2 Many films: fold one at a time (Rouard)

The trick is that Airy's formula does not care that "medium 2" is a
half-space. Replace $r_{12}$ by the effective reflection coefficient of
*everything below the film* and you can recurse. Start at the substrate and
walk up:

$$r_k = \frac{\rho_k + r_{k+1}e^{2i\delta_{k+1}}}{1 + \rho_k r_{k+1}e^{2i\delta_{k+1}}},
\qquad
t_k = \frac{\tau_k\thinspace t_{k+1}\thinspace e^{i\delta_{k+1}}}{1 + \rho_k r_{k+1}e^{2i\delta_{k+1}}}$$

where $\rho_k,\tau_k$ are the bare Fresnel coefficients of interface
$k \to k+1$, and $\delta_{k+1}$ is the phase across the layer just below.
This is [`methods/recursion.py`](../methods/recursion.py), and it is Rouard's
1937 method.

### 7.3 Many films: multiply matrices (Abelès)

Alternatively, track the pair of amplitudes $(A_k, B_k)$ — forward-going and
backward-going — in each layer, and note that both interfaces and propagation
act on that pair **linearly**. Converting the scattering description into a
transfer description (using the same Stokes relations) gives

$$I_{ij} = \frac{1}{t_{ij}}\begin{pmatrix}1 & r_{ij}\cr r_{ij} & 1\end{pmatrix},
\qquad
P_k = \begin{pmatrix}e^{-i\delta_k} & 0\cr 0 & e^{i\delta_k}\end{pmatrix}$$

and the stack is just their product:

$$M = I_{01}P_1I_{12}P_2\cdots I_{N-1,N}$$

Impose no backward wave in the substrate, $(A_0,B_0)^\top = M(A_N,0)^\top$
with $A_0 = 1$, and read off

$$t = \frac{1}{M_{00}}, \qquad r = \frac{M_{10}}{M_{00}}$$

[`methods/transfer_matrix.py`](../methods/transfer_matrix.py). Writing
$I$ in terms of the Fresnel coefficients rather than the textbook
$D_iP D_i^{-1}$ form removes a `linalg.inv` per layer — the 2024 original
called it twice per layer for no reason.

### 7.4 Same physics, different numerics

The two solvers agree to $10^{-13}$, which the suite asserts. They are *not*
equally good.

$P_k$ contains $e^{+i\delta_k}$, whose modulus is $e^{+\operatorname{Im}\delta_k}$
— it **grows** exponentially in an absorbing layer. The final ratio
$r = M_{10}/M_{00}$ cancels that growth analytically, so the answer stays
right... until $M_{00}$ exceeds the float range and the cancellation becomes
`inf/inf`. Measured in this entry: about 20 µm of metal in a single layer, and
then $r$ goes `NaN` with no warning.

The recursion cannot do this. Every factor it touches is $e^{i\delta}$ with
$|e^{i\delta}| \le 1$ for a passive layer (§6.4), so the recursion can only
ever shrink. It underflows gracefully to zero where the matrix product
explodes.

This is the same instability that makes the transfer-matrix formulation
unusable for thick gratings, and the reason RCWA implementations use
scattering matrices instead — see Li (1996), which is the standard reference
on exactly this failure.

**And this is the payoff of the [architecture](../../docs/architecture.md).** Two
methods, one `physics.py`: the physics is identical to $10^{-13}$ and only
the numerical ceiling differs. Being able to say that sentence with confidence
is the whole reason the equations live in a file that imports nothing.

---

## 8. Scale analysis: reading the answer off the phase

Before running anything, look at $\delta = \frac{2\pi}{\lambda}n d\cos\theta$
and ask what values matter. Almost every classical design is a statement about
$\delta$.

### 8.1 The quarter wave, $\delta = \pi/2$

$$n\thinspace d\cos\theta = \frac{\lambda}{4}
\quad\Longrightarrow\quad
d = \frac{\lambda}{4n\cos\theta}$$

Round trip inside the layer is $2\delta = \pi$. Combined with the sign flip
that reflection off a higher index gives you, consecutive partial reflections
come back **in phase** — constructive, a mirror — or **out of phase** —
destructive, an AR coating — depending on the ordering of the indices.

*Answer to question 1:* MgF₂ ($n=1.38$) at 550 nm needs
$d = 550/(4\times1.38) = 99.6$ nm. About **330 atomic layers**. That number is
the reason AR coatings had to wait for vacuum deposition: you cannot polish
your way to a hundred nanometres.

### 8.2 The half wave, $\delta = \pi$ — the absentee layer

Then $P_k = \operatorname{diag}(e^{-i\pi}, e^{i\pi}) = -I$, which flips the
sign of the whole matrix product. So $r = M_{10}/M_{00}$ is **completely
unchanged**, and $t$ picks up a phase $\pi$ with $|t|$ unchanged.

A half-wave layer is invisible in power at its design wavelength, whatever its
index. It is not invisible at any other wavelength, which is what makes it
useful — it is how you add a spectral feature without disturbing the design
point. It is also a sharp test of whether your phase convention is right, and
it is in `test_physics.py` for exactly that reason.

### 8.3 Admittance: a quarter wave inverts

For a quarter-wave layer at normal incidence the characteristic matrix maps
the input admittance $Y$ of everything below it to

$$Y \longmapsto \frac{n^2}{Y}$$

Everything about quarter-wave design follows from iterating that one map.

**Single-layer AR.** One layer on a substrate: $Y = n_1^2/n_s$. Zero
reflection needs $Y = n_0$, so

$$\boxed{\thinspace n_1 = \sqrt{n_0 n_s}\thinspace }$$

For glass, $\sqrt{1.52} = 1.23$. No durable material has an index that low —
MgF₂ at 1.38 is the practical floor, giving 1.3% instead of 0%, which is why
real AR coatings use several layers instead of one. That gap between
$\sqrt{n_0n_s}$ and what chemistry offers is the entire reason multilayer AR
design exists as a field.

**Bragg stack.** $(HL)^N$ on a substrate: apply the map $2N$ times.

$$Y = n_s\left(\frac{n_H}{n_L}\right)^{2N},
\qquad
R = \left(\frac{n_0 - Y}{n_0 + Y}\right)^2$$

For $Y \gg n_0$ this linearises beautifully:

$$1 - R \thickspace \simeq\thickspace \frac{4n_0}{n_s}\left(\frac{n_L}{n_H}\right)^{2N}$$

**Every added period multiplies the leakage by $(n_L/n_H)^2$.** With
$n_H/n_L = 2.3/1.45$ that factor is 0.40 — each pair cuts what gets through
by 2.5×.

*Answer to question 2:* $R \gt 0.999$ needs $Y \gt 4n_0/10^{-3} = 4000$, so
$(1.586)^{2N} \gt 2632$, so $N \gt 8.5$: **nine pairs.** Not fifty, not five
hundred. Exponentials are why mirror design is easy and why it took
`experiments/bragg_mirror.py` only 16 periods to reach six nines.

### 8.4 Stopband width — the one that does *not* improve

The band edges of an infinite periodic stack are where the Bloch phase of one
period goes complex, $\left|\tfrac12\operatorname{Tr}M_{\text{period}}\right| = 1$.
For a quarter-wave period that gives

$$\frac{\Delta\lambda}{\lambda_0} = \frac{4}{\pi}\arcsin\negthinspace \left(\frac{n_H-n_L}{n_H+n_L}\right)$$

*Answer to question 3:* with 2.3/1.45 that is **0.291**, i.e. 160 nm wide at
550 nm. And note what is *not* in the formula: $N$. **More periods buy depth,
never width.** Width is set by index contrast alone. Everybody's first
instinct here is wrong, which is why it is worth measuring rather than
asserting — and why `bragg_mirror.py` prints the measured width next to the
analytic one.

To widen a stopband you need contrast, or several stacks at staggered design
wavelengths (a "chirped" mirror). To reach *every* angle and both
polarisations simultaneously you need a condition on contrast that most
material pairs fail — that is the result in Fink et al. (1998).

### 8.5 Angle: why coatings shift blue when you tilt them

$\delta \propto \cos\theta_k$, so tilting *reduces* the phase, and the design
wavelength moves down:

$$\lambda_{\text{design}}(\theta) \approx \lambda_0\sqrt{1 - \left(\frac{n_0\sin\theta_0}{n_{\text{eff}}}\right)^2}$$

Every dielectric filter blueshifts with angle. Your glasses look more purple
edge-on; a dichroic mirror in a microscope has to be specified at 45°, not at
normal incidence. This is also the fingerprint that distinguishes structural
colour from pigment in nature and in a lab.

### 8.6 The critical angle

For $n_0 \gt n_1$ and $\sin\theta_0 \gt n_1/n_0$, $\cos\theta_1$ becomes purely
imaginary. On the physical branch $n_1c_1 = i\thinspace |n_1c_1|$, so with $n_0c_0$
real,

$$r = \frac{n_0c_0 - i|n_1c_1|}{n_0c_0 + i|n_1c_1|}
\quad\Longrightarrow\quad
|r| = 1 \text{ exactly},\qquad T = 0 \text{ exactly}$$

Total internal reflection with no special-casing, no `nan`, and a nonzero
evanescent field in medium 1 that carries no net power across the boundary.
The only thing that made this work was choosing the branch correctly in §6.2.

---

## 9. Closed forms worth memorising

These are what you check code against. Cross-checking two solvers proves they
agree; checking against a closed form proves they are *right*. Every row here
is a test in [`../tests/`](../tests/).

| Situation | Result |
|---|---|
| Normal incidence, one interface | $R = \left(\dfrac{n_0-n_1}{n_0+n_1}\right)^2$ |
| Air/glass, normal | $R = 0.04$ |
| Brewster angle | $R^p = 0$ at $\theta_B = \arctan(n_j/n_i)$ |
| Critical angle and beyond | $R = 1$, $T = 0$, exactly |
| One film, any $\delta$ | $r = \dfrac{r_{01}+r_{12}e^{2i\delta}}{1+r_{01}r_{12}e^{2i\delta}}$ (Airy) |
| Quarter-wave single layer | $R = \left(\dfrac{n_0n_s-n_1^2}{n_0n_s+n_1^2}\right)^2$ |
| Ideal single-layer AR | $n_1 = \sqrt{n_0n_s}$ |
| Half-wave layer | absentee: $R$ unchanged at $\lambda_0$ |
| Quarter-wave stack $(HL)^N$ | $Y = n_s(n_H/n_L)^{2N}$, $R = \left(\dfrac{n_0-Y}{n_0+Y}\right)^2$ |
| Stack leakage, large $N$ | $1-R \simeq \dfrac{4n_0}{n_s}\left(\dfrac{n_L}{n_H}\right)^{2N}$ |
| Stopband width | $\dfrac{\Delta\lambda}{\lambda_0} = \dfrac{4}{\pi}\arcsin\dfrac{n_H-n_L}{n_H+n_L}$ |
| Any lossless stack | $R + T = 1$, every angle, both polarisations |
| Reversed symmetric stack | $R$ unchanged |

**A warning about the second-to-last row.** $R + T = 1$ is the test everybody
writes first and it is nearly worthless on its own. In this entry it held to
six decimals on three physically *wrong* results — an absorbing ambient
returning $R = 5.83$, a gain medium returning $A = -0.29$. A conservation law
constrains your bookkeeping, not your physics. Closed forms outrank it, and
cross-method agreement ranks below both.

---

## 10. What the simulation showed

The book's rule: **predict before you run.** Both experiments in the entry are
built as predictions with a number attached, not as plots to admire.

**[`bragg_mirror.py`](../experiments/bragg_mirror.py)** — prediction: peak
reflectance follows the admittance transform exactly, and the stopband width
does not move with $N$.

```
 periods     R peak   analytic   stopband
       2   0.658887   0.658887     0.0909
       4   0.936438   0.936438     0.1101
       8   0.998363   0.998363     0.2319
      16   0.999999   0.999999     0.2927

analytic stopband (infinite stack): 0.2911
```

Six decimals on the peak. The width converges to 0.2911 from below — the
measured value uses a crude 99%-of-peak threshold, which only becomes
meaningful once the band is genuinely flat, hence the drift at low $N$. The
napkin estimate of §8.3 also lands: for $N=8$ it predicts a leakage of
$1.639\times10^{-3}$ against a measured $1.637\times10^{-3}$, and stays within
0.2% all the way to $N=16$.

**[`brewster.py`](../experiments/brewster.py)** — prediction: the minimum
of $R^p$ sits at $\arctan(n_2/n_1)$ and is a true zero.

```
       interface      found   arctan(n2/n1)    Rp at min
    air -> glass    56.651d         56.659d    7.677e-09
  air -> silicon    75.557d         75.548d    1.090e-07
    glass -> air    33.339d         33.341d    2.352e-09
```

A true zero, limited by the angular grid rather than by the physics.

The complete verification table lives in [the entry README](../README.md)
§4.

---

## 11. Where the model stops being true

The section that matters most, and the one that is usually missing.

### 11.1 Coherence — the assumption that fails first

Everything above adds amplitudes, which requires the partial waves to have a
stable relative phase. They only do if the round-trip path is shorter than the
source's **coherence length**:

$$L_c \approx \frac{\lambda^2}{\Delta\lambda}$$

| Source | $\Delta\lambda$ | $L_c$ at 550 nm |
|---|---|---|
| Sunlight / white light | ~300 nm | ~1 µm |
| LED | ~30 nm | ~10 µm |
| HeNe laser | ~0.002 nm | ~15 cm |

This is why the field is called *thin*-film optics. A 100 nm layer is coherent
for any source. **A 1 mm glass substrate is not** — in daylight, its two faces
do not interfere, and the correct treatment adds *powers* there while adding
amplitudes inside the coating. That is the mixed coherent/incoherent problem,
and Katsidis & Siapkas (2002) is the reference for it. This entry does not
implement it, and any real coating on a real substrate needs it.

### 11.2 The rest of the list

| Limit | What actually happens | This entry |
|---|---|---|
| Absorbing ambient | Incident power undefined; gave $R=5.83$, $T=-4.82$ | `ValueError` |
| Gain medium, $\operatorname{Im}n\lt 0$ | Forward-decay branch rule breaks; gave $A=-0.29$ | `ValueError` |
| ~20 µm of metal, one layer | $M_{00}$ overflows, $r \to$ `NaN` | use `method="recursion"` |
| Dispersion $n(\lambda)$ | Every spectrum is subtly wrong | not modelled — $n$ is constant |
| Interface roughness | Scattering out of the specular direction; $R+T\lt 1$ with no absorption | not modelled |
| Birefringence / anisotropy | s and p stop decoupling; needs $4\times4$ | not modelled |
| Focused or short-pulse beams | Angular/spectral spread, Goos–Hänchen shift | not modelled |
| Nonlinearity | $n(I)$; superposition fails | not modelled |
| Layers thinner than ~2 nm | Bulk $n$ stops meaning anything | outside the model's premises |

Two of those rows exist because someone **probed** the edges, not because
anyone reasoned their way there. The suite was green and both holes were wide
open. Which is the general lesson and the reason this section exists at all:

> A test suite proves the cases you thought of. The limits of a model are
> found by attacking it, not by re-reading it.

---

## 12. The essentials

- A multilayer is **interference, not absorption**. Amplitudes add; powers do
  not. Every phenomenon in this document is a cross term.
- **Snell is a conservation law** — $k_x$ conserved because the structure is
  invariant in $x$. Written that way it survives complex indices and total
  internal reflection; written as $\arcsin$ it does not.
- **Fresnel is just continuity** of the tangential fields. Two lines of
  algebra per polarisation, and Brewster falls out of $r^p = 0$.
- The whole domain is **three equations**: Snell, Fresnel, phase. Everything
  else is bookkeeping — and bookkeeping is the part you are allowed to swap.
- **The branch cut is physics.** Choosing $\operatorname{Im}(n\cos\theta)\ge0$
  is the statement that passive media attenuate. Get it wrong and energy
  conservation still passes.
- **$T \neq |t|^2$.** Transmittance carries the ratio of normal energy flux,
  and the two polarisations project differently — with a conjugate that only
  matters exactly when you would not notice it missing.
- **The infinite sum of bounces is a geometric series** and collapses to
  Airy's formula. Recursion and matrix product are two ways of iterating that
  one result.
- **Quarter wave inverts admittance.** AR coatings, Bragg mirrors and the
  $\sqrt{n_0n_s}$ rule are all that single map applied a different number of
  times.
- **More periods buy depth, never width.** Stopband width depends on contrast
  alone.
- **$R+T=1$ is a weak test.** It held on three wrong answers. Closed forms
  first, cross-method agreement last.
- **Coherence is the assumption that fails first** in any real device, and it
  fails at the substrate, not in the coating.

---

## 13. Open questions

Things this document deliberately does not answer, roughly in order of how
much they would teach:

- **Mixed coherent/incoherent stacks.** The physically correct treatment of a
  coating on a 1 mm substrate under a broadband source. This is the single
  biggest gap between this entry and a usable tool.
- **The field profile inside the stack.** $R$ and $T$ say nothing about *where*
  the light is absorbed. For a solar cell or an OLED that spatial distribution
  is the whole design target, and it comes from keeping $(A_k,B_k)$ rather
  than discarding them.
- **The inverse problem.** Given a target $R(\lambda)$, find the layers. Needle
  optimisation (Tikhonravov 1996) is the classical answer; ML surrogates are
  the current fashion. Worth knowing that the forward model is called millions
  of times, so §7.4's numerical stability stops being academic.
- **Why an omnidirectional reflector needs a contrast condition.** Fink et al.
  (1998) — a genuinely non-obvious result that follows from the same Bloch
  analysis as §8.4.
- **What happens when the period stops being periodic.** Chirped mirrors,
  rugate filters, quasi-periodic and disordered stacks — where the Bloch
  argument no longer applies and the matrix product is all you have.

---

## 14. References

**Foundational**

- **Abelès, F.** *Recherches sur la propagation des ondes électromagnétiques
  sinusoïdales dans les milieux stratifiés. Application aux couches minces.*
  Annales de Physique **12**, 596–640 (1950).
  [link](https://www.annphys.org/articles/anphys/abs/1950/05/anphys19501205p596/anphys19501205p596.html)
  — the characteristic-matrix method.
- **Rouard, P.** *Études des propriétés optiques des lames métalliques très
  minces.* Annales de Physique **11**, 291–384 (1937).
  [link](https://www.annphys.org/articles/anphys/abs/1937/07/anphys19371107p291/anphys19371107p291.html)
  — the recursion, thirteen years before the matrices.
- **Born, M. & Wolf, E.** *Principles of Optics*, §1.6. The canonical
  derivation of stratified-media optics.

**Periodic stacks**

- **Yeh, P., Yariv, A. & Hong, C.-S.** *Electromagnetic propagation in periodic
  stratified media. I. General theory.* JOSA **67**, 423–438 (1977).
  [link](https://opg.optica.org/abstract.cfm?URI=josa-67-4-423)
  — Bloch waves, band edges, where §8.4 comes from.
- **Fink, Y. et al.** *A dielectric omnidirectional reflector.* Science **282**,
  1679–1682 (1998).
  [link](https://www.science.org/doi/10.1126/science.282.5394.1679)
- **Joannopoulos, J. D. et al.** *Photonic Crystals: Molding the Flow of Light*,
  2nd ed. (2008). A quarter-wave stack is a 1D photonic crystal; ch. 4.

**Numerics — the part most texts skip**

- **Li, L.** *Formulation and comparison of two recursive matrix algorithms for
  modeling layered diffraction gratings.* JOSA A **13**, 1024–1035 (1996).
  [link](https://opg.optica.org/josaa/abstract.cfm?uri=josaa-13-5-1024)
  — why transfer matrices blow up and scattering matrices do not. §7.4 in one
  paper.
- **Byrnes, S. J.** *Multilayer optical calculations.* arXiv:1603.02720.
  [link](https://arxiv.org/abs/1603.02720)
  — branch cuts, absorbing ambients, the p-polarisation conjugate, incoherent
  layers. The companion to the `tmm` Python package, and the clearest modern
  treatment of the traps.
- **Katsidis, C. C. & Siapkas, D. I.** *General transfer-matrix method for
  optical multilayer systems with coherent, partially coherent, and incoherent
  interference.* Applied Optics **41**, 3978–3987 (2002).
  [link](https://opg.optica.org/ao/abstract.cfm?uri=ao-41-19-3978)

**Design and practice**

- **Macleod, H. A.** *Thin-Film Optical Filters*, 4th ed. (2010). The
  practitioner's book — admittance diagrams, real materials, manufacturing
  tolerance.
- **Yeh, P.** *Optical Waves in Layered Media* (1988).
- **Tikhonravov, A. V., Trubetskov, M. K. & DeBell, G. W.** *Application of the
  needle optimization technique to the design of optical coatings.* Applied
  Optics **35**, 5493–5508 (1996).
  [link](https://opg.optica.org/ao/abstract.cfm?uri=ao-35-28-5493)

**Structural colour**

- **Vukusic, P. & Sambles, J. R.** *Photonic structures in biology.* Nature
  **424**, 852–855 (2003).
- **Kinoshita, S., Yoshioka, S. & Miyazaki, J.** *Physics of structural colors.*
  Reports on Progress in Physics **71**, 076401 (2008).

---

*Code: [`../physics.py`](../physics.py) and [`../methods/`](../methods/) ·
Entry: [`../README.md`](../README.md) · Repo-wide architecture:
[`docs/architecture.md`](../../docs/architecture.md)*
