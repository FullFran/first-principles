# Walking noise backwards

> The theory behind [`diffusion/`](../README.md), derived from the problem
> rather than from the formula. Read this if you want to know *why* the
> equations in `diffusion/process.py` and `diffusion/methods/` are those and
> not others.

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
7. [Two ways back](#7-two-ways-back)
8. [Scale analysis: when do the modes merge](#8-scale-analysis-when-do-the-modes-merge)
9. [Closed forms worth memorising](#9-closed-forms-worth-memorising)
10. [What the simulation showed](#10-what-the-simulation-showed)
11. [Where the model stops being true](#11-where-the-model-stops-being-true)
12. [The essentials](#12-the-essentials)
13. [Open questions](#13-open-questions)
14. [References](#14-references)

---

## 1. The phenomenon

Take a photograph. Add a little Gaussian noise. Add a little more. Keep
going, and after enough steps the photograph is gone — what is left is
indistinguishable from static, and no amount of staring recovers the cat.

Nothing about that is surprising. Destroying information is easy, and it is
the direction everything in physics runs.

Here is the surprising part. **The destruction is reversible — not for a
single image, but for the distribution.** There is a second process, running
backwards in time, whose statistics at every instant match the forward one.
Run it from pure static and it produces a photograph. Not the photograph you
started with; *a* photograph, drawn from the same distribution the originals
came from.

And the only thing that second process needs to know, at each point along the
way, is a single vector field: the direction in which the noisy density
increases fastest.

$$\nabla_x \log q_t(x)$$

That is the whole subject. Everything else — the schedules, the U-Nets, the
guidance scales, the thing that draws you an astronaut on a horse — is
engineering on top of one theorem about reversing a diffusion.

The question this document answers is why that vector field is enough, and
what you would compare a learned one against.

## 2. What this is for

### 2.1 Generative modelling

The obvious use, and the one that made the subject famous. Every image
generator in wide use — Stable Diffusion, Imagen, DALL·E 2 onwards, Midjourney
— is this process with a neural network in place of the exact score.

### 2.2 Inverse problems, which turn out to be the same problem

Denoising, inpainting, deblurring, super-resolution, MRI reconstruction. All
of them ask: given a corrupted observation, what was the clean signal? Section
6.4 shows that answering that question *is* estimating a score, by an identity
nobody designed for the purpose. The generative models were built out of
denoisers, and it took thirty years to notice that a denoiser was already
half a generative model.

### 2.3 Statistical physics, which is where it came from

The forward process is Brownian motion. The reverse process is a
time-reversed diffusion, and time-reversal in a dissipative system is the
question non-equilibrium thermodynamics exists to ask. The 2015 paper that
started the field says so in its title, and its argument is explicitly the
one Jarzynski used for free-energy differences: a process too fast to be
quasi-static can still be analysed, if you keep track of the whole ensemble
of paths rather than one of them.

### 2.4 The mirror of `sampling/`

[`sampling/`](../../sampling/) has an energy you can evaluate anywhere and a
normaliser you cannot compute. This has samples you can draw and a density
you cannot evaluate anywhere at all. The two problems are exact mirrors, and
both are solved by the same trick: work with an object that cannot see a
normalising constant. A ratio cannot. Neither can the gradient of a logarithm.

### 2.5 History

::: **A theorem for electrical circuits, unused for thirty years** ·
*Verification: A — Anderson, Stochastic Processes and their Applications 12(3),
1982, 313–326.*

Brian Anderson was a control theorist at the University of Newcastle in
Australia, working on filtering and stochastic realisation. In 1982 he
published a paper establishing that a process defined by a forward-time
diffusion equation has an associated reverse-time model, and that the reverse
drift differs from the forward one by a term involving the gradient of the log
density.

That is the theorem the entire field runs on. It is the reason any of this
works.

The applications Anderson lists are **stochastic realisation, signal
processing, and electric circuit theory**. There is no hint of generative
modelling, because in 1982 there was nothing to generate: no dataset, no
compute, and no reason to want a sampler for the distribution of photographs.
The result sat in a control-theory journal for three decades, complete and
correct and unused for the thing it would eventually make possible.

There is a lesson in that which is not about diffusion models. The
mathematics was never the bottleneck.

::: **A formula that arrived in a letter** ·
*Verification: A — Robbins, Proc. Third Berkeley Symposium, 1956, crediting
personal correspondence with Maurice Tweedie; revived by Efron, JASA 106(496),
2011.*

In the 1950s Herbert Robbins was building empirical Bayes: the idea that if
you are estimating many parameters at once, the data can tell you the prior.
In his 1956 Berkeley Symposium paper he reports a formula for the posterior
mean of a parameter given a noisy observation, and credits it to **private
correspondence with Maurice Tweedie**, a British statistician who had derived
it around 1947 and, as far as the record goes, never published it under his
own name.

The formula says: to get from a noisy observation to the best estimate of the
clean signal, add a correction that is *exactly proportional to the score of
the noisy marginal*.

$$\mathbb{E}[x_0 \mid x_t] = \frac{x_t + (1-\bar\alpha)\,\nabla \log q_t(x_t)}
{\sqrt{\bar\alpha}}$$

Read it right to left and it says a score gives you a denoiser. Read it left
to right and it says **a denoiser gives you a score** — that a network trained
only to clean up corrupted images has, without anyone intending it, learned
the gradient field of the data distribution.

That is the bridge between the two halves of this subject, and it came from a
letter in 1947, published by someone else in 1956, and largely forgotten until
Efron revived it in 2011.

::: **Two groups, two directions, one equation** ·
*Verification: A for the papers and dates; B for the claim that the two lines
of work were independent — it is the standard account and consistent with the
citation record, but I have not seen either group state it in those words.*

By 2019 there were two separate research programmes that did not know they
were the same one.

**From thermodynamics.** Jascha Sohl-Dickstein and colleagues published *Deep
Unsupervised Learning using Nonequilibrium Thermodynamics* in 2015. It has
the whole architecture: destroy the data with a diffusion, learn the reverse,
sample by running it backwards. Then Jonathan Ho, Ajay Jain and Pieter Abbeel
turned it into DDPM in 2020, and the images were suddenly competitive.

**From score matching.** Aapo Hyvärinen had introduced score matching in 2005
— fit a density by matching gradients, so the normaliser never appears — but
it required the trace of a Hessian and was intractable at scale. In 2011
Pascal Vincent proved that a denoising autoencoder's training objective is
score matching in disguise, **removing the second derivatives entirely**. Yang
Song and Stefano Ermon built noise-conditioned score networks on that in 2019.

In 2021 Song and coauthors showed the two were discretisations of the same
Itô SDE, and derived the deterministic ODE that shares its marginals. Two
communities had spent years walking toward each other from opposite ends of a
result Anderson had proved in 1982.

::: **Why 2015 did not look like 2022** ·
*Verification: C — widely repeated, and I have not verified it against
citation counts. Treat it as a plausible story, not a fact.*

The usual telling is that the 2015 paper was largely ignored for five years
until DDPM made it work. It is repeated everywhere and it is consistent with
what happened next, but I have not checked it against the citation record and
neither should you take it from me. What is documented is the gap in dates and
the jump in sample quality.

#### Papers worth reading

- **Anderson (1982)**, *Reverse-time diffusion equation models*. The theorem.
  Short, and written for control theorists.
- **Robbins (1956)**, *An empirical Bayes approach to statistics*. Where
  Tweedie's formula first appears in print.
- **Hyvärinen (2005)**, *Estimation of non-normalized statistical models by
  score matching*. Why you can fit a density you cannot normalise.
- **Vincent (2011)**, *A connection between score matching and denoising
  autoencoders*. The paper that made it tractable.
- **Sohl-Dickstein et al. (2015)**, *Deep unsupervised learning using
  nonequilibrium thermodynamics*. The architecture, five years early.
- **Ho, Jain, Abbeel (2020)**, *Denoising diffusion probabilistic models*.
  The one that worked.
- **Song et al. (2021)**, *Score-based generative modeling through stochastic
  differential equations*. The unification, and the probability-flow ODE.

## 3. Before you calculate

Three things are worth being clear about before any equation, because getting
them wrong makes the rest incomprehensible.

**The reverse process does not recover your image.** It produces *a* sample
from the distribution. Running it from the noise that a particular photograph
happened to decay into will not give you that photograph back. Nothing here
is an inverse in the ordinary sense.

**Time appears only through one scalar.** The forward process is usually
written as a chain of small steps, but every step composes, so the state at
time $t$ is a single Gaussian around the data. Everything in
`process.py` takes $\bar\alpha$ and never $t$: there is no second parameter
hiding.

**The score is a property of the noisy density, not of the data.** There is
no useful score of the data distribution itself — for data on a manifold it
does not exist. Adding noise is not only a way to destroy the data; it is
what makes the gradient defined in the first place.

## 4. Why the naive answer fails

Suppose you want to sample a distribution given only samples of it. The
obvious approaches all die, and they die for reasons worth knowing.

**Fit a density and sample it.** To sample a density you generally need its
normaliser, and in any interesting dimension that integral is unobtainable.
This is exactly the wall [`sampling/`](../../sampling/) is built around.

**Run a Markov chain.** Now you do not need the normaliser — ratios cancel it.
But a chain has to *travel*, and between two modes separated by a region of
low probability it travels exponentially slowly. That is the barrier problem,
measured in `sampling/`, and real data is nothing but modes.

**Learn the score directly and run Langevin dynamics on it.** Closer, and this
is what score matching proposes. It fails for two compounding reasons. Where
there is no data there is no signal, so the learned score is garbage in
exactly the regions a chain must cross. And on a manifold the score is not
defined at all.

The fix that makes everything work is small and strange: **do not learn one
score, learn a family of them, indexed by how much noise you added.** At high
noise the density is broad, the score is defined everywhere, and it is easy
to learn. At low noise it is sharp and hard, but by then you are already in
the right region. The noise level is a continuation parameter, and the whole
sampler is a homotopy from a problem you can solve to the one you cannot.

## 5. The minimal model

To ask whether a learned score is any good you need a case where the true
score is known. That is the entire design constraint, and it has exactly one
family of solutions.

A Gaussian convolved with a Gaussian is a Gaussian. So if the data is a
**mixture of Gaussians**, the noised data is a mixture of Gaussians too, with
parameters you can write down, at every noise level, forever. It is the only
non-trivial family that stays closed under the forward process.

A mixture is not interesting data. That is the point. It is the case with an
answer key, and the entry exists to build the key, not to admire the samples.

## 6. The equations

### 6.1 The forward process

Add Gaussian noise in small steps, and compose them. The composition is
another Gaussian, so the state at any time is

$$x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1-\bar\alpha_t}\,\varepsilon,
\qquad \varepsilon \sim \mathcal{N}(0, I).$$

One scalar $\bar\alpha_t \in (0,1]$ carries all of time: the fraction of the
signal still present. At 1 you have the data. At 0 you have a standard normal
and the data is gone.

### 6.2 The mixture stays a mixture

If $p_0 = \sum_k w_k \mathcal{N}(\mu_k, \Sigma_k)$ then

$$q_t = \sum_k w_k\, \mathcal{N}\!\left(\sqrt{\bar\alpha}\,\mu_k,\; S_k\right),
\qquad S_k = \bar\alpha\,\Sigma_k + (1-\bar\alpha) I.$$

Means shrink toward the origin by $\sqrt{\bar\alpha}$; covariances interpolate
toward the identity. The weights never move — noise does not change which
component a sample came from, only how well you can tell.

### 6.3 The score, in closed form

Differentiate the logarithm of that sum and the normaliser drops out:

$$\nabla \log q_t(x) = -\sum_k r_k(x)\; S_k^{-1}\left(x - \sqrt{\bar\alpha}\,
\mu_k\right),$$

$$r_k(x) = \operatorname{softmax}_k \big[\log w_k + \log \mathcal{N}(x;
\sqrt{\bar\alpha}\mu_k, S_k)\big].$$

A responsibility-weighted average of where each component would pull. Two
limits are worth checking by hand, because both are load-bearing:

- $\bar\alpha \to 1$: the responsibilities become a hard assignment and the
  score points straight at the component the point belongs to.
- $\bar\alpha \to 0$: every component's noised density is the same standard
  normal, the responsibilities flatten to $w_k$, all the pulls agree, and the
  score collapses to $-x$. **There is nothing left to reverse, which is
  exactly why the reverse process may start from pure noise.**

### 6.4 Tweedie, and why a denoiser is a score model

Rearranged, the same object answers a different question:

$$\mathbb{E}[x_0 \mid x_t] = \frac{x_t + (1-\bar\alpha)\,\nabla \log q_t(x_t)}
{\sqrt{\bar\alpha}}, \qquad
\nabla \log q_t(x_t) = -\frac{\mathbb{E}[\varepsilon \mid x_t]}
{\sqrt{1-\bar\alpha}}.$$

This holds for **any** $p_0$, not just a mixture. It is the 1947 formula from
section 2.5, and it is the reason a network trained to predict the noise in a
corrupted image is a score estimator whether or not anyone meant it to be.

### 6.5 The reverse-time process

Anderson's theorem: a forward diffusion has a reverse-time partner whose
drift is the forward drift *minus* a term in the score. Discretised on the
$\bar\alpha$ grid, and with the score substituted for the noise prediction,
the reverse step is

$$x_{t-1} = \frac{x_t + (1-\alpha_t)\,\nabla \log q_t}{\sqrt{\alpha_t}}
+ \sigma_t z, \qquad \alpha_t = \frac{\bar\alpha_t}{\bar\alpha_{t-1}}.$$

The coefficient is $1-\alpha_t$, the **per-step** quantity — not $1-\bar\alpha_t$,
the cumulative one. Getting that wrong is not a small error: see section 10.

### 6.6 The probability-flow ODE

Every diffusion has a deterministic partner with the same marginal density at
every time. Not the same paths — the same distribution at each instant, which
is all a sampler is ever asked for. Its discretisation is

$$x_{t-1} = \sqrt{\bar\alpha_{t-1}}\,\hat x_0 + \sqrt{1-\bar\alpha_{t-1}}\,
\hat\varepsilon, \qquad
\hat x_0 = \frac{x_t + (1-\bar\alpha_t)\nabla \log q_t}{\sqrt{\bar\alpha_t}},
\quad \hat\varepsilon = -\sqrt{1-\bar\alpha_t}\,\nabla \log q_t.$$

Read the second line as: *estimate the noise, then re-add exactly as much as
the next time step should have.*

## 7. Two ways back

They differ in one term — the $\sigma_t z$ — and everything else follows.

| | ancestral | probability flow |
|---|---|---|
| draws from the generator | at every step | once, at the start |
| the map from noise to data | not a function | a function |
| paths | cross constantly | cannot cross |
| a mode not near the start | reachable | unreachable |
| a discretisation error | partly washed out | integrated |

The bottom two rows are the same fact read twice, which is the honest way to
present a trade-off: the noise that lets a run change its mind is the noise
that stops it being reproducible.

## 8. Scale analysis: when do the modes merge

The forward process does not blur the modes together gradually. There is a
threshold, and it is worth being able to predict it before running anything.

Two components separated by a distance $d$ have noised means separated by
$\sqrt{\bar\alpha}\,d$ — shrinking. Their noised widths are
$\sqrt{\bar\alpha \sigma^2 + (1-\bar\alpha)}$ — growing toward 1. So the
resolvability

$$R(\bar\alpha) = \frac{\sqrt{\bar\alpha}\, d}
{2\sqrt{\bar\alpha \sigma^2 + (1-\bar\alpha)}}$$

falls monotonically, and $R = 1$ is where two bumps become one. For the
bimodal target ($d = 4$, $\sigma^2 = 0.3$) that is at $\bar\alpha \approx 0.2$.

![Top: the exact density as the signal fraction falls, two wells merging into
one blob. Bottom: the score field at the same four times, with two attractors
at the start and a single radial field at the end.](figures/collapse.png)

Measured:

```
  abar  mode gap / width  resolvable
  1.00              3.65  yes
  0.70              2.34  yes
  0.30              1.23  yes
  0.05              0.46  no
```

The consequence is a scheduling one. **All of the interesting decisions happen
in a narrow band of $\bar\alpha$**, and a sampler that spends its steps
uniformly in $t$ spends most of them where the density is already Gaussian and
nothing is left to decide. That is what a cosine schedule is for, and why the
original linear schedule needed a thousand steps to be worth using.

Note which quantity sets the threshold: the noised width is dominated by the
*smallest* eigenvalue of the data covariance, not the average. In an
anisotropic dataset different directions lose their structure at different
times.

## 9. Closed forms worth memorising

| Quantity | Form |
|---|---|
| Noised mixture | $\sum_k w_k \mathcal{N}(\sqrt{\bar\alpha}\mu_k,\; \bar\alpha\Sigma_k + (1-\bar\alpha)I)$ |
| Score, $\bar\alpha \to 0$ | $-x$ |
| Denoiser ↔ score | $\nabla \log q_t = -\mathbb{E}[\varepsilon|x_t]/\sqrt{1-\bar\alpha}$ |
| Reverse mean | $(x_t + (1-\alpha_t)\nabla\log q_t)/\sqrt{\alpha_t}$ |
| Reverse variance | $\frac{1-\bar\alpha_{t-1}}{1-\bar\alpha_t}(1-\alpha_t)$ |
| Modes merge at | $R(\bar\alpha) = 1$, $R = \sqrt{\bar\alpha}d \,/\, 2\sqrt{\bar\alpha\sigma^2 + 1 - \bar\alpha}$ |
| Flow map, 1-D | $x \mapsto F^{-1}(\Phi(x))$ |

## 10. What the simulation showed

**The score is right.** Three independent checks, none of which shares a line
with the formula under test: central differences of the log density (worst
$1.7\times10^{-9}$), an unrelated Tweedie derivation by Gaussian conditioning
($2.1\times10^{-14}$), and the $\varepsilon$ identity (machine precision).

**A wrong coefficient is invisible in the mathematics and obvious in the
samples.** The first version of `ancestral.step` used $1-\bar\alpha_t$ where
$1-\alpha_t$ belongs. Both methods consume the same score, so the domain was
exonerated immediately: probability flow sat inside the noise floor while
ancestral sat at $\text{MMD}^2 = 4\times10^{-1}$. Two methods over one domain
is what turns "something is wrong" into "the bug is in this file".

**The deterministic sampler is the quantile transport map.** Not merely
deterministic — in one dimension it is *the* monotone map carrying the noise
onto the target, so a start at the $u$-th quantile of the noise lands at the
$u$-th quantile of the target.

![Top: twelve paths from the same twelve starts, tangled for ancestral and
non-crossing for the flow. Bottom left: endpoint against start, with the flow
lying on the exact quantile curve and ancestral flat. Bottom right: the error
against the exact map, first order in the step
count.](figures/trajectories.png)

That single fact explains three things no other property does. The paths
cannot cross, because a monotone map has no room to. The endpoints are not at
the modes, because quantiles go to quantiles. And which mode a run reaches is
decided entirely by its first draw.

Its mirror image is what ancestral does. Over a range of starting points five
units wide, its endpoint moves by **0.024**: the sample comes from the noise
injected along the way, not from where the walk began.

The map is exact only in the limit, and the approach is clean first order:

```
  steps   worst error   halving
     50      5.50e-02        --
    100      2.80e-02      2.0x
    200      1.43e-02      2.0x
    400      7.30e-03      2.0x
    800      3.80e-03      1.9x
   1600      2.04e-03      1.9x
```

**A threshold has to be measured.** The discrepancy is an unbiased MMD²
against exact draws, and the floor — how far two sets of *exact* draws
disagree — was first estimated from a single pair. The contract test then
passed at 100 steps, failed at 200 and passed again at 400 on the same
target. A noisy measurement against a noisy threshold is a coin flip wearing
a lab coat. It is now taken over five pairs, at the top.

**And a claim about step budgets survives only in a window.** The received
wisdom is that the deterministic sampler needs far fewer steps. It holds at
five to eight steps — 0.6–0.9× in MMD² on the anisotropic targets — which is
worth knowing, because the usual argument is made with a learned score and a
perceptual metric and neither survives into this setting automatically. Past
about twelve steps both methods are inside the floor. An earlier version of
the experiment kept ranking them there and reported ancestral ahead by 5.6×,
which was two numbers indistinguishable from zero being divided by each other.

## 11. Where the model stops being true

**A mixture is not data.** Real data lies near a low-dimensional manifold, its
score does not exist at zero noise, and no closed form is coming. Everything
here is the instrument, not the specimen.

**Two dimensions hide the whole problem.** The reason score matching needed
Vincent's trick is a Hessian trace that is fine in 2-D and impossible in
$10^5$.

**The score is exact, so nothing here measures learning.** Every failure mode
of a real diffusion model — a score that is wrong where data is thin, a
network that smooths across modes, a schedule mismatched to what the network
learned — is invisible by construction.

**The discretisation is fixed-grid.** The continuous-time SDE and its
probability-flow ODE are the general statement; DDPM and DDIM are one
discretisation of them, and higher-order integrators do better than the first
order measured in section 10.

**$\bar\alpha$ is refused below $10^{-8}$**, and the schedules stop at
$10^{-4}$. At zero exactly the softmax is over identical logits, and returning
$-x$ would be reporting a limit as if it had been computed.

## 12. The essentials

If you keep five things from this document:

1. **Destroying a distribution is easy and reversible in law.** Not
   trajectory by trajectory — in distribution, which is all a sampler needs.
2. **The reverse process needs one object: $\nabla \log q_t$.** It is a
   gradient of a logarithm, so the normaliser is gone before you start.
3. **A denoiser is a score model.** Tweedie's formula, from a 1947 letter,
   says the correction from noisy to clean is proportional to the score.
4. **Noise is a continuation parameter, not just damage.** It makes the score
   defined everywhere and turns an impossible problem into a homotopy from an
   easy one.
5. **The modes merge at a threshold, not gradually**, and the threshold is set
   by the smallest eigenvalue of the data covariance.

## 13. Open questions

- **What does a learned score cost?** Everything here is the answer key; the
  entry that uses it does not exist yet. `solve.sample` takes a `score_fn`
  precisely so that entry changes no line under `methods/`.
- **Where does the learned score go wrong first?** The honest guess is: in the
  narrow band of $\bar\alpha$ identified in section 8, because that is where
  the density has structure and the training signal is thinnest per unit of
  consequence. Untested.
- **Does the transport-map result survive in higher dimensions?** In 1-D the
  flow is the monotone quantile map. In 2-D and above there is no canonical
  monotone map, and what the ODE converges to is a specific one — which?
- **Is the few-step advantage of the deterministic sampler a property of the
  score or of the metric?** Measured here with an exact score and MMD; the
  literature measures it with a learned score and FID.

## 14. References

- Anderson, B. D. O. (1982). *Reverse-time diffusion equation models*.
  Stochastic Processes and their Applications 12(3), 313–326.
- Efron, B. (2011). *Tweedie's formula and selection bias*. JASA 106(496).
- Ho, J., Jain, A., Abbeel, P. (2020). *Denoising diffusion probabilistic
  models*. NeurIPS.
- Hyvärinen, A. (2005). *Estimation of non-normalized statistical models by
  score matching*. JMLR 6, 695–709.
- Nichol, A., Dhariwal, P. (2021). *Improved denoising diffusion probabilistic
  models*. The cosine schedule used in `solve.py`.
- Robbins, H. (1956). *An empirical Bayes approach to statistics*. Proc. Third
  Berkeley Symposium.
- Sohl-Dickstein, J., Weiss, E., Maheswaranathan, N., Ganguli, S. (2015).
  *Deep unsupervised learning using nonequilibrium thermodynamics*. ICML.
- Song, J., Meng, C., Ermon, S. (2020). *Denoising diffusion implicit models*.
- Song, Y., Ermon, S. (2019). *Generative modeling by estimating gradients of
  the data distribution*. NeurIPS.
- Song, Y., et al. (2021). *Score-based generative modeling through stochastic
  differential equations*. ICLR.
- Vincent, P. (2011). *A connection between score matching and denoising
  autoencoders*. Neural Computation 23(7), 1661–1674.
