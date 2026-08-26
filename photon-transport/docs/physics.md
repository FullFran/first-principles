# Photons through matter

> The physics behind [`photon-transport/`](../README.md), derived from the
> problem rather than from the formula. Read this if you want to know *why*
> the equations in `photon-transport/physics.py` are those and not others.

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
2. [What this is for](#2-what-this-is-for)
3. [Before you calculate](#3-before-you-calculate)
4. [Why the naive answer fails](#4-why-the-naive-answer-fails)
5. [The minimal model](#5-the-minimal-model)
6. [The equations](#6-the-equations)
7. [Two estimators, one integral](#7-two-estimators-one-integral)
8. [Scale analysis: everything is optical depth](#8-scale-analysis-everything-is-optical-depth)
9. [Closed forms worth memorising](#9-closed-forms-worth-memorising)
10. [What the simulation showed](#10-what-the-simulation-showed)
11. [Where the model stops being true](#11-where-the-model-stops-being-true)
12. [The essentials](#12-the-essentials)
13. [Open questions](#13-open-questions)
14. [References](#14-references)

---

## 1. The phenomenon

Put a torch against your palm in a dark room and your hand glows red. Not the
surface — the whole hand, lit from inside, and only red. Hold a hand up to the
sun and you can make out the bones as darker shapes.

Something similar happens in a hospital, with harder light and a detector
instead of an eye, and it produces an image of the inside of a person without
opening them.

All of these are the same situation: **light enters a material, some of it
gets absorbed, and what comes out the other side carries information about
what it went through.**

Notice what is *not* happening. Nothing is being focused. There is no lens,
no image formation, no reflection. The picture is made entirely of what
survived, and every dark region is a place where more of the light did not.

> **The question.**
> A source emits photons into a cone of half-angle $\alpha$. A slab of
> material of thickness $L$ and attenuation coefficient $\mu$ sits in the way,
> and a detector sits behind it.
> **What fraction of the emitted photons arrive?**

That is the entire forward problem, and it is what `photon-transport/`
computes. Reverse it — measure what arrives and work out what the object was
— and you have tomography, which is a different entry.

---

## 2. What this is for

### 2.1 Seeing inside things without opening them

The obvious one, and it is enormous: radiography, CT, mammography, industrial
inspection of welds and castings, airport security, and the non-destructive
examination of paintings and mummies. All of them are the same measurement —
count what got through, per pixel — and all of them are limited by the same
thing, which is [§10.3](#103-a-picture-of-the-difference).

### 2.2 Deciding how much material to stand behind

Shielding design is the same calculation aimed at a different number. How much
concrete around a reactor, how much lead in an apron, how far from the source
you have to stand. The answer is always an exponential, which is what makes it
tractable and also what makes it unforgiving: halving the transmitted dose
costs a fixed thickness, and the tenth-value layer is
[§8](#8-scale-analysis-everything-is-optical-depth).

### 2.3 Dose, which is the thing nobody wants to pay

Every photon that forms a radiographic image is a photon the patient absorbed.
That is not a side effect of the measurement, it *is* the measurement: the
image is made of the ones that were stopped. So image quality and dose are the
same quantity seen twice, and [§10.3](#103-a-picture-of-the-difference) shows
what the exchange rate is.

### 2.4 Light through anything cloudy

The same mathematics runs the optics of fog, milk, biological tissue, planetary
atmospheres, interstellar dust and snow. My own
[`snow-mcrt`](https://github.com/FullFran/snow-mcrt) is this problem with
scattering put back in, which is the step this entry deliberately does not
take ([§11](#11-where-the-model-stops-being-true)).

### 2.5 And it is where Monte Carlo came from

Not "an application of Monte Carlo" — the reason it exists. The method was
invented for neutron transport, which is this problem with the neutrons
allowed to multiply, and the story is [§2.6](#26-history).

### 2.6 History

::: The solitaire · *Verification: A — Ulam tells it himself in* Adventures of
a Mathematician.

In January 1946 Stanisław Ulam was convalescing in Los Angeles from an acute
encephalitis that had nearly killed him and had cost him an emergency
craniotomy. He could not work on anything serious, so he played Canfield
solitaire.

Canfield has a famously bad success rate. Bored, Ulam wondered what the
probability of completing it actually was, tried to attack it with
combinatorics, saw the size of the problem — and realised it would be far more
practical to play a hundred hands and count.

**The interesting part is what he thought of next**, which was the neutron
diffusion problem he had been working on.

That jump is less obvious than it looks in hindsight. In solitaire the
probability is the quantity you want and playing is the natural process, so
simulating is the obvious move. In neutron diffusion the quantity you want is
*deterministic* — the multiplication factor of a mass of fissile material, a
fixed number — and what you have is an integro-differential equation in a
six-dimensional phase space that nobody could solve for realistic geometries.

The jump is seeing that **the equation describes the average behaviour of an
underlying random process**, and that you can therefore estimate it by
following individual sampled trajectories: where a neutron hits, what happens
when it does, where it goes next. Instead of solving the equation for the
average, **generate the average**.

Ulam told von Neumann. In March 1947 von Neumann wrote an eleven-page letter
to Robert Richtmyer that was not a letter of ideas but a complete computing
plan for the ENIAC — the physical problem, the trajectory sampling scheme, the
cross-section treatment, the random number generation. The name came from
Ulam's uncle, who used to borrow money to gamble at Monte Carlo.

::: Beer's law, which is mostly Bouguer's · *Verification: B — the chronology
is well documented, the reason the name stuck is not.*

The exponential in this document is usually called the Beer–Lambert law, and
occasionally Beer–Lambert–Bouguer, which is closer to fair and still in the
wrong order. Pierre Bouguer published the exponential absorption of light in
1729. Lambert restated it in 1760, citing Bouguer. Beer's 1852 contribution
was the dependence on the *concentration* of an absorbing solute, which is a
genuinely different statement and the one chemists needed.

It is a small case of the pattern in every one of these entries: the person
whose name survives is the one whose version was useful to the largest field,
not the one who got there first.

### Papers and books worth reading

| Reference | Why |
|---|---|
| [Metropolis & Ulam, *JASA* **44**, 335 (1949)](https://doi.org/10.1080/01621459.1949.10483310) | The paper that named the method |
| [Eckhardt, *Los Alamos Science* **15**, 131 (1987)](https://library.lanl.gov/cgi-bin/getfile?15-13.pdf) | Ulam, von Neumann and the ENIAC, with the letter |
| **Lux & Koblinger**, *Monte Carlo Particle Transport Methods* (1991) | The estimator zoo. Implicit capture is §5 |
| **Attix**, *Introduction to Radiological Physics and Radiation Dosimetry* | Where the attenuation coefficients come from |
| [Berger et al., NIST XCOM](https://www.nist.gov/pml/xcom-photon-cross-sections-database) | The actual $\mu$ tables, per element, per energy |
| **Chandrasekhar**, *Radiative Transfer* (1950) | The analytic theory this method exists to avoid |

---

## 3. Before you calculate

The rule from the book: **write a number down before you read the next
section.** The learning is in the gap between your number and the real one,
and the gap does not exist if you did not commit.

> 1. A slab that lets half the photons through. **How thick is it**, measured
>    in mean free paths? And how thick is one that lets a tenth through — is
>    it twice that, or something else?
> 2. A radiograph looks grainy and you want half the noise. **How many more
>    photons?** Twice? Four times?
> 3. The source is not a laser, it is a cone. **Does opening the cone let more
>    or less light through the slab?** And why is that not obvious?

Answers in [§8](#8-scale-analysis-everything-is-optical-depth). All three are
one line, and the third one is the only one people get wrong.

---

## 4. Why the naive answer fails

There are two naive answers here and they fail in opposite directions.

### 4.1 "Solve the transport equation"

The right description of this problem is an integro-differential equation for
the photon density over position, direction and energy. Written down, it is
exact and it is a function on a six-dimensional phase space, and for anything
but a slab in a vacuum nobody can solve it.

This is the situation Ulam was in with neutrons, and the escape is the whole
subject: **the equation describes the average of a random process, so generate
the process instead of solving for the average.** No geometry is harder than
any other, because a photon does not know what shape the object is — it only
ever asks how far to the next interaction.

That trade is not free, and what it costs is $1/\sqrt{N}$
([§8.3](#83-the-price-of-throwing-darts)).

### 4.2 "The photons all travel a distance L"

Tempting, and wrong in two separate ways.

**They do not all travel $L$.** A photon at angle $\theta$ crosses
$L/\cos\theta$ of material, so a cone of directions is a spread of path
lengths. That is why the answer to napkin question 3 is *less* — every
off-axis photon sees more material than an axial one, and none sees less, so
opening the cone can only attenuate more.

**And there is no such thing as "the" distance a photon travels before it
interacts.** It is a random variable, drawn from an exponential, and that is
not a modelling convenience — it is what "attenuation coefficient" means. A
photon has no memory of how far it has already come, so its chance of
interacting in the next millimetre is the same wherever it is, and the only
distribution with that property is the exponential
([§6.2](#62-the-free-path-and-why-it-is-exponential)).

Replacing that distribution with its mean gets you the wrong answer, because
$\langle e^{-\mu s}\rangle \neq e^{-\mu\langle s\rangle}$. Exponentials do not
commute with averaging, which is the same reason the naive answer failed in
[`tmm/`](../../tmm/docs/physics.md) and will fail again anywhere a nonlinear
function meets a distribution.

---

## 5. The minimal model

Every assumption below buys a specific simplification, and every one of them
fails somewhere real. Listing them is not ceremony — the list *is* the domain
of validity, and it is the thing the tests can never tell you.

| Assumption | What it buys | Where it breaks |
|---|---|---|
| **No scattering** — absorb or pass | Straight lines; the path length is known before the photon moves | Compton scattering dominates at diagnostic energies |
| Monochromatic | One $\mu$ | Real sources have spectra; beam hardening is first-order |
| A homogeneous slab | $\mu$ is a number, not a field | Any real object |
| Infinite in $x,y$ | No edges to leak round | Small objects, collimators, finite detectors |
| Point source | One cone, one origin | Extended sources blur the image |
| Photons are independent | The answer is a mean over one-photon histories | Always true here, and false for coherent light |
| $\mu \ge 0$ | Transmission is at most 1 | Gain media — **refused** by `check_medium` |
| Cone half-angle $\lt \pi/2$ | The slab path is finite | Grazing rays — **refused** by `check_cone` |
| A perfect detector | Counts are the measurement | Efficiency, blur, cross-talk, dead time |

That is the model. Notice what it does **not** assume: it does not assume the
slab is thin, or the cone narrow, or the attenuation weak. Those all come out
correctly. The one assumption doing real work is the first, and it is doing so
much work that it deserves its own row in
[§11](#11-where-the-model-stops-being-true).

---

## 6. The equations

### 6.1 Emission: the cosine is the flat variable

A cone of half-angle $\alpha$ subtends a solid angle, and the solid angle
element is

$$d\Omega = \sin\theta\thinspace d\theta\thinspace d\phi$$

so the density of directions in $\theta$ carries that $\sin\theta$ and the
density in $\cos\theta$ is flat:

$$p(\theta)\thinspace d\theta = \sin\theta\thinspace d\theta
\quad\Longleftrightarrow\quad
p(\cos\theta)\thinspace d(\cos\theta) = d(\cos\theta)$$

Sample the cosine uniformly on $[\cos\alpha, 1]$ and the weighting is
automatic. Sample $\theta$ uniformly instead — which is the obvious thing to
type — and you crowd photons towards the axis. The fingerprint is the mean
cosine:

$$\text{uniform in }\cos\theta:\ \langle\cos\theta\rangle
= \frac{1+\cos\alpha}{2},
\qquad
\text{uniform in }\theta:\ \langle\cos\theta\rangle = \frac{\sin\alpha}{\alpha}$$

which differ by 5% at $\alpha = 45°$ and never by zero. That is a test, and it
is [`test_physics.py`](../tests/test_physics.py)'s sharpest one, because a
wrong angular distribution produces a *plausible* answer.

### 6.2 The free path, and why it is exponential

A photon in a uniform medium has no memory. Whatever it has already survived,
its probability of interacting in the next $ds$ is $\mu\thinspace ds$ — that
is the definition of the attenuation coefficient. Writing $S(s)$ for the
probability of surviving a distance $s$,

$$S(s + ds) = S(s)\left(1 - \mu\thinspace ds\right)
\quad\Longrightarrow\quad
\frac{dS}{ds} = -\mu S
\quad\Longrightarrow\quad
S(s) = e^{-\mu s}$$

The memorylessness *is* the exponential; they are the same statement. So the
distance to the next interaction has density $p(s) = \mu e^{-\mu s}$, and to
draw from it, invert the survival probability — which is uniform on $(0,1]$:

$$\boxed{\enspace s = -\frac{\ln U}{\mu}\enspace}$$

This is [`sample_free_path()`](../physics.py), and it is the whole of inverse
transform sampling: **if you can invert the cumulative distribution, you can
sample it with one uniform number.** That works here and fails in general, and
the failure is why [`sampling/`](../../sampling/README.md) exists.

> **One line of care.** `rng.random()` returns $[0, 1)$, and $\ln 0$ is
> $-\infty$. Drawing $1 - U$ instead puts the sample on $(0, 1]$, which makes
> the singularity **unreachable** rather than merely improbable. The 2024
> version used `log(rand())` and would have produced an infinite path roughly
> once in $10^{16}$ draws — never in a test run, and eventually in production.

### 6.3 Geometry: one factor, and it is the only one

A photon crossing a slab of thickness $L$ at angle $\theta$ travels

$$\ell = \frac{L}{\cos\theta}$$

through it. That is the entire angular dependence of the problem. The 2024
version computed it as the three-dimensional distance between the entry and
exit points, which is the same number arrived at the long way.

### 6.4 Beer–Lambert

Put the three together. A photon transmits if its free path exceeds its slab
path, and the probability of that is the survival probability evaluated there:

$$\boxed{\enspace T(\theta)
= \mathbb{P}\left(s > \ell\right)
= \exp\negthinspace\left(-\frac{\mu L}{\cos\theta}\right)\enspace}$$

Not an approximation, not a fit — the survival function of §6.2 evaluated at
the geometry of §6.3. Averaged over the cone it becomes

$$T = \frac{1}{1-\cos\alpha}
\int_{\cos\alpha}^{1} e^{-\mu L / c}\thinspace dc$$

which is an exponential integral with no elementary form. It is computed by
quadrature in [`cone_transmittance()`](../physics.py) — on a fixed grid, to a
precision far beyond what any Monte Carlo run reaches, which is what makes it
a **reference** rather than a second opinion.

---

## 7. Two estimators, one integral

Everything so far is the physics. What follows is a choice, and it is the
choice this entry is about.

### 7.1 Analog: simulate what a photon does

Draw a free path. Compare it with the slab path. Count the survivors.

Every random number stands for something that physically happens, and the
answer is a tally. It is the literal translation of the process, it is what
the 2024 version did, and it is what everybody writes first.

**Its cost is that each photon reports one bit.** A photon that was absorbed
tells you only that it was absorbed. The estimate carries the full binomial
noise of a coin flip, variance $T(1-T)$, no matter how narrow the beam or how
well you understand the geometry.

### 7.2 Weighted: integrate the die instead of rolling it

Look at what the free path is *for*. It is drawn, compared once, and thrown
away — it only ever answers one question, and that question has a known answer
in expectation:

$$\mathbb{P}\left(s > \ell\right) = e^{-\mu\ell}$$

So do not sample it. Each photon contributes its exact survival probability,
and the estimator is unbiased because the mean of the indicator *was* that
probability all along.

This is **implicit capture**, and it is what every serious transport code
does. What it buys is the removal of one entire source of randomness: the only
variance left is the spread of path lengths across the cone.

$$\mathrm{Var}_{\text{analog}} = T(1-T),
\qquad
\mathrm{Var}_{\text{weighted}} = \mathrm{Var}_c\negthinspace\left(e^{-\mu L/c}\right)$$

Close the cone and the second one goes to zero with it. The first does not
move at all.

### 7.3 What the contract may and may not demand

[`tests/test_methods.py`](../tests/test_methods.py) is parametrised over every
registered estimator and asserts what both must do: land on Beer–Lambert,
return probabilities, shrink as $1/\sqrt{N}$, be reproducible.

It says nothing about variance, because that is where they differ by eight
orders of magnitude and a shared claim would be false. The same design
decision as [`hopfield/`](../../hopfield/README.md) refusing to demand energy
descent from its synchronous schedule.

---

## 8. Scale analysis: everything is optical depth

### 8.1 There is one variable, and it is dimensionless

$\mu$ and $L$ never appear apart. They appear as their product

$$\tau = \mu L$$

the **optical depth**, and every result in this document is a function of
$\tau$ alone. A centimetre of something twice as absorbing is the same slab as
two centimetres of the original, exactly, and a test pins it.

That is worth more than it sounds. It means there is precisely **one** length
scale in the problem, the mean free path $1/\mu$, and that measuring anything
in those units removes the material from the question.

### 8.2 Half-value and tenth-value layers

*Answer to question 1.* Set $e^{-\tau} = 1/2$:

$$\tau_{1/2} = \ln 2 = 0.693, \qquad \tau_{1/10} = \ln 10 = 2.303$$

So the tenth-value layer is **3.3 times** the half-value layer, not ten times
and not twice. Each factor of two costs the same fixed thickness, which is the
whole content of an exponential and the reason shielding is quoted this way.

### 8.3 The price of throwing darts

*Answer to question 2.* A Monte Carlo estimate has error $\sigma/\sqrt{N}$.
Halving the noise needs **four times** the photons, and one more decimal digit
needs a hundred times.

That is the standing cost of the escape in
[§4.1](#41-solve-the-transport-equation), and it is why the choice of
estimator matters so much: it cannot change the $1/\sqrt{N}$, but it can change
the $\sigma$ on top of it, and [§10.2](#102-the-same-answer-for-a-fraction-of-the-photons)
changes it by eight orders of magnitude.

In a radiograph the exchange rate is not abstract. The noise is the counting
statistics of the photons the patient absorbed, so halving the graininess of
an image means quadrupling the dose.

### 8.4 Opening the cone

*Answer to question 3.* **Less gets through.** Every off-axis photon crosses
$L/\cos\theta \gt L$ of material and none crosses less, so widening the cone
can only attenuate more.

The reason people hesitate is that they are thinking of the detector, where
opening the cone spreads the same photons over more area and each pixel gets
fewer. That is a different question with the same answer, and conflating them
is how you end up dividing by the solid angle twice.

---

## 9. Closed forms worth memorising

These are what you check code against. Cross-checking two estimators proves
they agree; checking against Beer–Lambert proves they are right. Every row
here is a test in [`../tests/`](../tests/).

| Situation | Result |
|---|---|
| Survival over a distance | $S(s) = e^{-\mu s}$ |
| Free path sample | $s = -\ln U/\mu$ |
| Mean free path | $1/\mu$ |
| Slab path at angle $\theta$ | $L/\cos\theta$ |
| Transmission, one direction | $T = e^{-\mu L/\cos\theta}$ |
| Transmission, over a cone | $\frac{1}{1-\cos\alpha}\int_{\cos\alpha}^{1}e^{-\mu L/c}\thinspace dc$ |
| Emission, mean cosine | $(1+\cos\alpha)/2$ |
| Half-value layer | $\tau = \ln 2 = 0.693$ |
| Tenth-value layer | $\tau = \ln 10 = 2.303$, i.e. 3.3 half-values |
| Analog variance | $T(1-T)$, whatever the geometry |
| Weighted variance | the spread of $e^{-\mu L/c}$ over the cone, $\sim\alpha^4$ |
| Monte Carlo error | $\sigma/\sqrt{N}$, for any estimator |
| Two slabs of equal $\mu L$ | identical, exactly |

**A warning about the last row.** "Both estimators agree" is the test people
reach for and it is the weakest one here — they agree because they are
estimating the same integral, and they would agree just as happily on a wrong
integral if the shared physics were wrong. The closed form outranks it, and
the closed form was checked first.

---

## 10. What the simulation showed

The book's rule: **predict before you run.** All three experiments are
predictions with a number attached, not plots to admire.

### 10.1 Beer–Lambert, recovered

Prediction: a straight line on a log axis for a collimated beam, with slope
$-\mu$, bending away as the cone opens. Neither estimator is told the law.

![Transmitted fraction against slab thickness on a log axis, for a collimated
beam and a 45-degree cone, with the closed form drawn through measured points
carrying error bars.](figures/beer_lambert.png)

**What to conclude:** both estimators land on a law that appears nowhere in
either of them. The analog one samples free paths and counts; the weighted one
integrates a survival probability; the exponential is a consequence.

```
--- 45 degree cone ---
   thickness    analytic                 analog               weighted
        1.00    0.308413      0.306910+-0.00146      0.308490+-0.00011
        3.00    0.030532      0.031040+-0.00055      0.030548+-0.00003
        5.00    0.003171      0.003350+-0.00018      0.003169+-0.00001
```

**A methodological note worth more than the plot.** The first version used one
seed for every point in the sweep. That reuses the same free paths, pulls
every point the same way, and turns honest $1\sigma$ scatter into what reads
as a systematic bias — the analog column sat above theory at *every*
thickness. The error bars were correct throughout; only the eye was fooled.
The seed now varies per point.

### 10.2 The same answer for a fraction of the photons

Prediction: the gap between the estimators grows without bound as the cone
narrows, and the analog variance does not move at all.

![Variance per photon against cone half-angle, log-log, for both estimators,
with a reference line of slope four.](figures/variance.png)

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

**What to conclude:** the analog variance is $T(1-T)$ to four decimals at
every cone angle. It is a coin flip, and **nothing the geometry knows can
reach it** — the estimator discards that information by construction. The
weighted variance falls as roughly $\alpha^4$, because the only randomness
left is the spread of path lengths, and that spread goes as
$1-\cos\alpha \sim \alpha^2$.

A five-degree cone needs **two** weighted photons to match four hundred
thousand analog ones.

### 10.3 A picture of the difference

The same argument stops being a number.

![Three detector images of a sphere with two denser inclusions: analog,
weighted, and the exact transmission, at the same photon budget.](figures/radiograph.png)

```
   estimator   RMS error vs exact   worst pixel
      analog             0.027925      0.170133
    weighted             0.000000      0.000000
```

**What to conclude:** identical photon budget, 120 per pixel, and one image is
grainy while the other is exact. The graininess is not a rendering artefact —
it is the binomial noise of §7.1, one bit per photon, made visible.

And this is where §8.3 stops being abstract. In a real radiograph that noise
is the counting statistics of the photons the patient absorbed, so halving it
means quadrupling the dose. The weighted estimator gets the clean image for
free because it is a *simulation*; a real machine has no such option.

---

## 11. Where the model stops being true

The section that matters most, and the one that is usually missing.

### 11.1 Scattering — the assumption that fails first

Everything here has photons travelling in straight lines until they are
absorbed. Real photons at diagnostic energies mostly **scatter**: Compton
scattering changes their direction and takes some of their energy, and they
carry on.

That breaks the entry in two separate places.

**The physics.** A scattered photon still reaches the detector, just from the
wrong direction, carrying no information about the line it appeared to come
along. In real radiography scattered photons are a fog laid over the image,
and removing them — with grids, air gaps, collimation — is a large part of
what the hardware is for.

**And the estimator.** The weighted estimator works because the path through
the medium is known *before the photon moves*. Add scattering and the path
becomes a random walk whose length is not known in advance, so the analytic
integration of §7.2 has nothing to integrate. Implicit capture still exists in
scattering codes, but it has to be earned again per collision rather than
handed over once.

That is the honest summary of the entry's scope: it is the case where the
shortcut is available.

### 11.2 The rest of the list

| Limit | What actually happens | This entry |
|---|---|---|
| Scattering | Straight lines wrong; the weighted shortcut disappears | not modelled |
| Broad spectrum | Soft photons absorbed first, so $\mu$ falls with depth; transmission is not exponential in $L$ | not modelled |
| Very thick slabs | The analog estimator returns almost all zeros and its *relative* error explodes | measured |
| Very thick slabs, weighted | Weights underflow to zero long before the analog count would | not guarded |
| Cone approaching $\pi/2$ | The slab path diverges | `ValueError` |
| Gain media, $\mu \lt 0$ | Transmission above 1 | `ValueError` |
| A zero-variance estimator | "Within 3σ" becomes meaningless — 0.2 ulp read as 447σ | floored |
| Inhomogeneous objects | $\mu$ is a field, not a number | only in the radiograph, by hand |
| Detector physics | Efficiency, blur, dead time, cross-talk | perfect counting |

The σ row is worth its own sentence because it bit during development. The
weighted estimator on a collimated beam gives every photon the *same*
contribution, so its standard error is float noise rather than a spread, and
dividing by it turned a difference of 0.2 ulp into **447 standard errors**.
**The better the estimator, the more brittle a "within three sigma" check
becomes**, which is not a sentence I expected to write.

---

## 12. The essentials

- **The picture is made of what survived.** Nothing is focused, nothing is
  reflected; every dark region is a place more of the light did not get
  through.
- **Memorylessness is the exponential.** A photon's chance of interacting in
  the next millimetre does not depend on how far it has come, and only one
  distribution has that property.
- **Inverting the CDF samples it in one line** — and that works here and
  almost nowhere else, which is why MCMC exists.
- **There is one variable and it is $\mu L$.** One length scale, the mean free
  path, and everything else is a ratio to it.
- **A tenth-value layer is 3.3 half-value layers**, not ten and not two.
- **Monte Carlo escapes the six-dimensional equation by generating the average
  instead of solving for it**, and the standing charge is $1/\sqrt{N}$.
- **An estimator cannot change the $1/\sqrt{N}$ and can change the $\sigma$**
  — here by eight orders of magnitude, by declining to sample something whose
  expectation it already knows.
- **The analog estimator discards what the geometry knows.** One bit per
  photon, variance $T(1-T)$, unimprovable by understanding.
- **Image noise is dose.** Halve the graininess, quadruple the exposure.
- **A Monte Carlo result without an error bar is not a measurement**, and a
  simulation never checked against a closed form is only ever checked against
  your expectations.

---

## 13. Open questions

Things this document deliberately does not answer, roughly in order of how
much they would teach:

- **What does scattering cost?** It removes the weighted estimator's shortcut
  and turns the path into a random walk. That walk is the same mathematics as
  [`sampling/`](../../sampling/README.md)'s Langevin dynamics and, in the
  continuum limit, the diffusion equation. It is the single biggest gap
  between this entry and anything usable.
- **How do you weight without knowing the path?** Implicit capture survives
  scattering, but it has to be re-earned per collision, and the variance
  bookkeeping is what makes real transport codes hard.
- **What is the optimal estimator?** Weighted beats analog here by declining
  to sample one variable. There is a whole family behind that — importance
  sampling, splitting, Russian roulette — and a principled statement of when
  each pays.
- **Where does $\mu$ come from?** Photoelectric absorption, Compton, pair
  production, each with its own dependence on energy and atomic number. This
  entry takes $\mu$ as given, and everything interesting about materials is in
  how it is not.
- **How do you invert this?** Measuring projections and recovering the object
  is tomography, and the fact that it is possible at all is a nineteenth-
  century theorem about the Radon transform.

---

## 14. References

**Monte Carlo, and where it came from**

- **Metropolis, N. & Ulam, S.** *The Monte Carlo method.* Journal of the
  American Statistical Association **44**, 335–341 (1949).
  [link](https://doi.org/10.1080/01621459.1949.10483310)
- **Eckhardt, R.** *Stan Ulam, John von Neumann, and the Monte Carlo method.*
  Los Alamos Science **15**, 131–143 (1987).
  [link](https://library.lanl.gov/cgi-bin/getfile?15-13.pdf) — includes von
  Neumann's 1947 letter to Richtmyer.
- **Ulam, S.** *Adventures of a Mathematician* (1976). The solitaire, in his
  own words.

**Transport and estimators**

- **Lux, I. & Koblinger, L.** *Monte Carlo Particle Transport Methods: Neutron
  and Photon Calculations* (1991). Implicit capture, splitting, Russian
  roulette — the variance-reduction family this entry takes one member of.
- **Chandrasekhar, S.** *Radiative Transfer* (1950). The analytic theory, and
  a good look at what you are avoiding.
- **Spanier, J. & Gelbard, E. M.** *Monte Carlo Principles and Neutron
  Transport Problems* (1969).

**The physics of $\mu$**

- **Attix, F. H.** *Introduction to Radiological Physics and Radiation
  Dosimetry* (1986).
- **Berger, M. J. et al.** *XCOM: Photon Cross Sections Database*, NIST.
  [link](https://www.nist.gov/pml/xcom-photon-cross-sections-database)
- **Bouguer, P.** *Essai d'optique sur la gradation de la lumière* (1729). The
  exponential, first.

---

*Code: [`../physics.py`](../physics.py) and [`../methods/`](../methods/) ·
Entry: [`../README.md`](../README.md) · Repo-wide architecture:
[`docs/architecture.md`](../../docs/architecture.md)*
