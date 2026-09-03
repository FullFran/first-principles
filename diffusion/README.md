# Diffusion

Destroy a distribution with noise until nothing is left, learn the slope of
the log-density along the way, and walk back up it. The reverse process needs
one thing the forward process throws away — the score — and the honest
question is how you would ever know a learned one is right. So the target
here is a Gaussian mixture, the one family whose noised score stays exactly
computable. 505 lines of core.

| | |
|---|---|
| **Level** | L1 derive · L2 implement · L3 experiment |
| **Domain** | [`process.py`](process.py) — 233 lines, no sampler in it |
| **Methods** | [`ancestral.py`](methods/ancestral.py) 34 · [`probability_flow.py`](methods/probability_flow.py) 44 |
| **Tests** | 96, split into domain, contract, and where the methods diverge |
| **Follows** | [`sampling/`](../sampling/), which is the same walk with the energy given rather than learned |

## Layout

```
docs/process.md       the derivation, from the phenomenon down
docs/figures/         the figures it argues from
process.py            the domain: noising, and the exact score it implies
methods/
  ancestral.py        sample the reverse transition
  probability_flow.py integrate the flow with the same marginals
solve.py              the schedule, the loop, and the verdict
experiments/
  collapse.py         what noising destroys, and what the score still knows
  step_budget.py      where the two methods separate, and where they stop
  trajectories.py     the flow is the quantile transport map
tests/
  test_process.py     the score, three independent ways
  test_methods.py     the contract: the samples are draws from the target
  test_methods_differ.py  the one term that separates them
```

## 1. What problem does it solve

You have samples from a distribution and no formula for it. There is no
density for photographs, and no energy anyone wrote down. That is the exact
mirror of [`sampling/`](../sampling/), where the energy is given and the
normaliser is unobtainable — here the samples are given and the density is.

Both are solved by the same object. Sampling needs ratios of probabilities;
diffusion needs the gradient of a log probability. Neither can see a
normalising constant, because a constant cancels in a ratio and vanishes
under a derivative.

The trick is to make the hard distribution reachable from an easy one. Add
Gaussian noise until what is left is a standard normal, which you can sample
trivially, and then run the process backwards. Reversing it needs

$$\nabla_x \log q_t(x),$$

the score of the *noised* density at each point along the way. Learn that,
and you can walk noise back into data.

Which is where the question this entry exists for arrives: if the score is a
network's output, what is it being compared against?

## 2. The equations

The forward process, in the form that matters — not one step, but the jump
from the data to any time at once:

$$x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1 - \bar\alpha_t}\, \varepsilon,
\qquad \varepsilon \sim \mathcal{N}(0, I)$$

One scalar $\bar\alpha_t \in (0, 1]$ carries all of time: the fraction of the
signal still present. Nothing below needs $t$ itself.

**The mixture stays a mixture.** A Gaussian convolved with a Gaussian is a
Gaussian, so if $p_0 = \sum_k w_k \mathcal{N}(\mu_k, \Sigma_k)$ then

$$q_t = \sum_k w_k \mathcal{N}\!\left(\sqrt{\bar\alpha}\,\mu_k,\;
S_k\right), \qquad S_k = \bar\alpha \Sigma_k + (1 - \bar\alpha) I.$$

Means shrink toward the origin, covariances inflate toward the identity, and
the weights never move — noise does not change which component a sample came
from, only how well you can tell.

**The score, in closed form.** Differentiating the log of that sum:

$$\nabla \log q_t(x) = -\sum_k r_k(x)\, S_k^{-1}\left(x - \sqrt{\bar\alpha}\,
\mu_k\right), \qquad r_k(x) = \operatorname{softmax}_k\big[\log w_k + \log
\mathcal{N}(x; \sqrt{\bar\alpha}\mu_k, S_k)\big].$$

A responsibility-weighted average of where each component would pull. As
$\bar\alpha \to 0$ the responsibilities flatten, every pull agrees, and the
score collapses to $-x$: at the end of the forward process there is nothing
left to reverse, which is precisely why the reverse process may start from
pure noise.

**Tweedie's formula**, which is not about mixtures at all:

$$\mathbb{E}[x_0 \mid x_t] = \frac{x_t + (1 - \bar\alpha)\nabla \log
q_t(x_t)}{\sqrt{\bar\alpha}}, \qquad \nabla \log q_t(x_t) = -\frac{\mathbb{E}
[\varepsilon \mid x_t]}{\sqrt{1 - \bar\alpha}}.$$

It holds for any $p_0$ under Gaussian noising. That is the reason a network
trained to predict the noise in a corrupted image is a score estimator
without anyone deciding it should be, and the reason denoising and generation
turned out to be one subject.

## 3. What I implemented

Two ways back, differing in one term.

**Ancestral** samples the reverse transition. The exact $q(x_{t-1} \mid x_t)$
is not Gaussian — it is a Gaussian mixed over everything $x_0$ could have
been — but for a small enough step it is close to one:

$$x_{t-1} = \frac{x_t + (1 - \alpha_t)\,\nabla \log q_t}{\sqrt{\alpha_t}} +
\sigma_t z, \qquad \alpha_t = \frac{\bar\alpha_t}{\bar\alpha_{t-1}}.$$

**Probability flow** integrates the deterministic partner of that stochastic
equation — a different process with the same marginal density at every time,
which is the only property a sampler is asked for:

$$x_{t-1} = \sqrt{\bar\alpha_{t-1}}\,\hat x_0 + \sqrt{1 - \bar\alpha_{t-1}}\,
\hat\varepsilon.$$

Neither method is handed the target. Both receive a score already evaluated
at the current point, which is the seam the entry is built on: `solve.sample`
takes a `score_fn`, and swapping the exact score for a learned one changes no
line in `methods/`.

## 4. What I verified

| Claim | Where |
|---|---|
| **The score matches central differences of the log density** — 15 combinations of target and $\bar\alpha$, worst $1.7 \times 10^{-9}$ | domain |
| **Tweedie agrees with Gaussian conditioning** — an unrelated derivation of $\mathbb{E}[x_0 \mid x_t]$, sharing no line, worst $2.1\times10^{-14}$ | domain |
| **$\nabla \log q_t = -\mathbb{E}[\varepsilon\mid x_t]/\sqrt{1-\bar\alpha}$** to machine precision | domain |
| **The score forgets the target as the signal dies** — at $\bar\alpha = 10^{-6}$ it is $-x$ | domain |
| **$q_t$ integrates to 1** on a grid | domain |
| **The samples are draws from the target** — unbiased MMD² inside a measured floor, both methods, all three targets | contract |
| **Both modes get visited** — 50/50 on the symmetric target, not 100/0 | contract |
| **A wrong score gives wrong samples** — halve it and the discrepancy rises | contract |
| **The flow is a function of its starting noise** — bit-identical, not to a tolerance | differ |
| **Ancestral keeps drawing after the start** | differ |
| **Neither survives three steps** — an order of magnitude outside the floor | differ |
| **The flow is ahead at five steps** — 0.6–0.9× in MMD², above the floor | differ |

The threshold is measured, not chosen. Two independent sets of *exact* draws
disagree by some amount; that is the floor, estimated over five pairs and
taken at the top, and a sampler is allowed exactly that much.

That detail is not decoration. The first version estimated the floor from a
single pair, and the contract test then passed at 100 steps, failed at 200
and passed again at 400 on the same target — a coin flip wearing a threshold.

### The experiment

**[`step_budget.py`](experiments/step_budget.py)** — where the two methods
separate. The received claim is that the deterministic sampler needs far
fewer steps, and it is usually argued with a learned score and a perceptual
metric. It survives the change to an exact score and a distributional metric,
but only in a window:

```
=== arc (noise floor 8.8e-03) ===
 steps     ancestral     prob-flow    ratio  ahead
     5      3.09e-02      1.70e-02     0.6x  prob-flow
     8      1.12e-02      7.06e-03     0.6x  prob-flow
    12      4.35e-03      3.85e-03       --  both at floor
    50      2.59e-04      1.46e-03       --  both at floor
```

Past about twelve steps there is nothing left to rank. **An earlier version of
this file ranked them anyway** and reported ancestral ahead by up to 5.6× at
fifty steps. Both numbers were indistinguishable from zero, and dividing one
by the other measured which noise was larger. The floor is now printed beside
the table and the ratio is withheld once both fall under it.

## 5. What I deliberately left out

**The learned score.** This is the omission that matters, and it is the point
of the seam rather than an accident of scope. Everything here runs on a score
that is derived, so what the entry establishes is the answer key: a target
whose score is exact, a metric with a measured floor, and a sampler that
takes the score as an argument. Learning it is the next entry, and it can be
graded rather than admired.

**Real data.** A Gaussian mixture is not interesting. It is the case with an
answer, and the whole design follows from wanting one.

**Continuous time.** The SDE and its probability-flow ODE are the general
statement; this is their discretisation on a fixed grid, which is what DDPM
and DDIM are.

**Classifier-free guidance, latent spaces, conditioning, $v$-prediction.**
All of them are modifications of the score, and none changes what is being
verified here.

**Learned variances.** $\sigma_t$ comes from the schedule.

## Where this stops being right

The core is 505 lines, just over the 100–500 band of rule 4. It is stated
rather than rounded down.

$\bar\alpha$ is refused below $10^{-8}$: at zero exactly the mixture has
forgotten which component it came from, and the softmax is over identical
logits. The schedules stop at $10^{-4}$.

The MMD floor is a function of the sample size. Comparing runs at different
`draws` compares two different thresholds, which is why the experiment holds
it fixed.

`bimodal` is too easy to rank methods on: both sit at the floor from about
eight steps, and the comparison there reports noise. The anisotropic targets
are the ones that separate anything.

## Run it

```bash
uv run pytest diffusion
uv run python diffusion/experiments/step_budget.py
```

```python
import solve
run = solve.sample(target="arc", method="probability-flow", steps=50)
run.within_noise          # is it a draw from the target, or only nearly
```

## What this sets up

[`sampling/`](../sampling/) walks an energy somebody wrote down. This walks
one nobody did. The remaining step is to stop deriving the score and learn
it — the gradients for that are [`mlp/`](../mlp/) — at which point every
number in section 4 becomes a grade instead of a check.
