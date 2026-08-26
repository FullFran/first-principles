# Chains that forget where they started

> The theory behind [`sampling/`](../README.md), derived from the problem
> rather than from the formula. Read this if you want to know *why* the
> equations in `sampling/distribution.py` and `sampling/methods/` are those
> and not others.

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
7. [Two chains, one density](#7-two-chains-one-density)
8. [Scale analysis: how long until it forgets](#8-scale-analysis-how-long-until-it-forgets)
9. [Closed forms worth memorising](#9-closed-forms-worth-memorising)
10. [What the simulation showed](#10-what-the-simulation-showed)
11. [Where the model stops being true](#11-where-the-model-stops-being-true)
12. [The essentials](#12-the-essentials)
13. [Open questions](#13-open-questions)
14. [References](#14-references)

---

## 1. The phenomenon

Here is a fact that ought to be strange and is not treated as one. **You can
describe how likely something is without being able to say how likely it is.**

Write down an energy for a configuration — a protein folded a certain way, a
magnet with its spins pointing somewhere, a set of parameters fitting some
data — and you have said everything about the relative likelihood of every
configuration. Which of two is more probable, and by exactly what factor, is
now decided. What you have not got, and cannot get, is a single probability,
because that requires knowing the total over everything else.

For a system with $N$ binary components that total is a sum over $2^N$ terms.
At $N = 300$ it exceeds the number of atoms in the observable universe.

> **The question.**
> An energy $E(x)$, evaluable anywhere. The density it defines,
> $p(x) = e^{-E(x)/T}/Z$, with $Z$ unobtainable.
> **How do you draw samples from $p$?**

Not "how do you approximate $Z$" — that is a different and mostly hopeless
problem. Samples are enough for everything anyone actually wants: averages,
uncertainties, the shape of the distribution, the most probable
configurations. And samples turn out to be reachable when the probability
itself is not.

---

## 2. What this is for

### 2.1 Statistical physics, which is where it came from

A magnet is $10^{23}$ spins with an energy, and every question about it is an
average over the Boltzmann distribution. The partition function is exactly the
$Z$ above and it is exactly as unobtainable. Sampling is not a numerical
convenience here; it is the only route to the answer for any model that is not
exactly solvable, which is nearly all of them.

My own [`GPU-accelerated-Ising-Model`](https://github.com/FullFran/GPU-accelerated-Ising-Model)
is this document applied to the 3D Ising model at a scale this entry
deliberately is not.

### 2.2 Bayesian inference

The posterior is
$p(\theta \mid D) \propto p(D \mid \theta)\thinspace p(\theta)$,
and that $\propto$ is hiding an integral over parameter space that nobody can
do. Every modern Bayesian computation is a chain, and Metropolis is
the ancestor of all of them.

### 2.3 Optimisation, which is the same thing cold

Lower the temperature while the chain runs and it stops exploring and starts
converging on the lowest energy it can find. That is simulated annealing
(Kirkpatrick, Gelatt & Vecchi, 1983), and the only thing that changed is that
$T$ became a function of time. [§10.3](#103-the-same-code-optimising) measures
it.

### 2.4 Complex systems, and the word for what goes wrong

This is where the entry stops being a numerical methods exercise.

A chain that cannot cross a barrier in the time you have is not a broken
chain. It is a **glass**. Ergodicity — the assumption that a long enough
trajectory visits states in proportion to their probability — is a statement
about infinite time, and every real system and every real chain has finite
time. When the two disagree, the system has a stationary distribution it
cannot reach, and that is the definition of ergodicity breaking.

It is not an exotic case. It is window glass, which is a liquid that failed to
find its crystal. It is a spin glass, which is [`hopfield/`](../../hopfield/README.md)
with random couplings. It is why protein folding is hard and why simulated
annealing has to be slow. **The double-well experiment in
[§10.2](#102-where-a-chain-lies-to-you) is that phenomenon in one dimension**,
small enough to have an exact answer to be wrong about.

The related quantity is **critical slowing down**: near a phase transition the
correlation length diverges, and with it the time a chain needs to produce one
independent sample. The diagnostic that detects it is the autocorrelation time
in [`solve.py`](../solve.py) — the same number, doing the same job, in a
one-dimensional toy.

### 2.5 History

::: **Markov, Nekrasov, and an argument about free will** ·
*Verification: A — Basharin, Langville & Stewart (2004); Hayes (2013).*

Pavel Nekrasov was a mathematician at Moscow University, a former seminarian,
and part of a school that took the law of large numbers as evidence for
theology. His argument ran: the law of large numbers requires independent
trials; social statistics — crime rates, marriage rates — obey the law of
large numbers; therefore human acts are independent; therefore they are free.

Andrey Markov, in St Petersburg, was an atheist, a republican, and by all
accounts spectacularly disagreeable. He thought the argument was rubbish, and
rather than say so he **built a counterexample**: a sequence of variables that
are explicitly *dependent* — each one's distribution fixed by the one before —
and that obeys the law of large numbers anyway.

That counterexample is the Markov chain. It exists because someone wanted to
win an argument about free will.

Markov then had to demonstrate it on something real, and what he chose was
**the first 20,000 letters of Pushkin's *Eugene Onegin***, classified by hand
into vowels and consonants, counted in pairs. He measured the probability that
a vowel follows a vowel and found it was not the probability that a vowel
appears — dependence, in a text, obeying the law of large numbers. He
published it in 1913.

There is no computer anywhere in this story. There is a man with a hostile
temperament, a novel in verse, and twenty thousand pencil marks.

::: **Who wrote the Metropolis algorithm** ·
*Verification: A — Gubernatis,* Physics of Plasmas **12**, 057303 (2005),
*from an interview with Marshall Rosenbluth shortly before his death.*

The 1953 paper is *Equation of State Calculations by Fast Computing Machines*,
six pages, five authors in alphabetical order: Nicholas Metropolis, Arianna W.
Rosenbluth, Marshall N. Rosenbluth, Augusta H. Teller and Edward Teller.

Marshall Rosenbluth's account of who did what:

- **Metropolis** supplied machine time and the MANIAC infrastructure. He did
  not participate in developing the algorithm.
- **Edward Teller** made one important early suggestion: sample in
  configuration space rather than momentum space, since the kinetic part
  integrates analytically.
- **Augusta Teller** began some of the programming.
- **Marshall and Arianna Rosenbluth** developed the algorithm and wrote the
  program. Arianna Rosenbluth, a Harvard physics PhD, programmed the MANIAC
  entirely.

Rosenbluth summarised it by saying Metropolis had nothing to do with the
development beyond providing computer time.

The algorithm is universally called Metropolis. Alphabetical order put his
name first on a paper he did not contribute the idea to, and the name of the
person who actually programmed it is not attached to anything.

### Papers worth reading

| Reference | Why |
|---|---|
| [Metropolis et al., *J. Chem. Phys.* **21**, 1087 (1953)](https://doi.org/10.1063/1.1699114) | Six pages. The algorithm, and see the history above |
| [Hastings, *Biometrika* **57**, 97 (1970)](https://doi.org/10.1093/biomet/57.1.97) | The generalisation to asymmetric proposals |
| [Gubernatis, *Phys. Plasmas* **12**, 057303 (2005)](https://doi.org/10.1063/1.1887186) | Who actually did it |
| [Basharin, Langville & Stewart, *Lin. Alg. Appl.* **386**, 3 (2004)](https://doi.org/10.1016/j.laa.2003.12.041) | Markov, Nekrasov and *Eugene Onegin* |
| [Roberts & Tweedie, *Bernoulli* **2**, 341 (1996)](https://doi.org/10.2307/3318418) | Why unadjusted Langevin is biased, and MALA |
| [Roberts & Rosenthal, *Stat. Sci.* **16**, 351 (2001)](https://doi.org/10.1214/ss/1015346320) | The optimal acceptance rate, and why it is 0.234 |
| [Neal, *Handbook of MCMC*, ch. 5 (2011)](https://arxiv.org/abs/1206.1901) | Hamiltonian Monte Carlo: the fix for random walks |
| [Song & Ermon, *NeurIPS* (2019)](https://arxiv.org/abs/1907.05600) | Langevin with a *learned* score. The road out of this entry |

---

## 3. Before you calculate

The rule from the book: **write a number down before you read the next
section.** The learning is in the gap between your number and the real one,
and the gap does not exist if you did not commit.

> 1. You want samples from $p \propto e^{-E}$ in 100 dimensions. The obvious
>    method is to draw uniformly and keep points in proportion to $p$.
>    **What fraction of draws survive?**
> 2. A chain runs for a million steps. **How many independent samples is that
>    worth?** A million? And what would you have to measure to know?
> 3. A barrier twice as high as the temperature costs some number of steps to
>    cross. **Make it four times as high — how much slower?** Twice? Four
>    times?

Answers in [§4](#4-why-the-naive-answer-fails) and
[§8](#8-scale-analysis-how-long-until-it-forgets). The first is the reason
Markov chains exist, and the third is the reason glasses do.

---

## 4. Why the naive answer fails

### 4.1 The asymmetry that starts everything

You can evaluate $E(x)$ anywhere. You cannot evaluate

$$Z = \int e^{-E(x)/T}\thinspace dx$$

because it is an integral over the whole space. So you can compute

$$\frac{p(y)}{p(x)} = e^{-\left(E(y)-E(x)\right)/T}$$

for any pair of points — the $Z$ cancels — and you can never compute $p(x)$.

Everything in this document is a way of living with that. And the useful
reframing is not "$Z$ is hard" but: **ratios are enough**, if you can find a
procedure that only ever asks for them.

### 4.2 Rejection sampling, and how badly it dies

The textbook answer: draw $x$ from something easy, accept it with probability
proportional to $p(x)/q(x)$. It is correct, it needs no chain, and it produces
genuinely independent samples.

It is also useless in any interesting number of dimensions, and the reason is
worth doing as arithmetic rather than taking on faith.

Take $p$ a unit Gaussian in $d$ dimensions and $q$ a Gaussian with standard
deviation $\sigma \gt 1$. The best possible acceptance rate is
$\sigma^{-d}$ — the ratio of the normalisations. At $\sigma = 1.1$, hardly a
mismatch at all:

| $d$ | acceptance |
|---|---|
| 1 | 0.91 |
| 10 | 0.39 |
| 100 | $7\times10^{-5}$ |
| 1000 | $10^{-42}$ |

*Answer to question 1: essentially none.* And the failure is not fixable by
choosing $q$ better, because it comes from volume. In high dimension almost
all of the volume of any region is near its boundary, and two distributions
that look similar concentrate on shells that barely overlap.

**So the escape is to give up on independence.** Do not draw a fresh point;
modify the one you have. That is the whole idea of a Markov chain, and what it
costs is that consecutive samples are correlated
([§8](#8-scale-analysis-how-long-until-it-forgets)).

### 4.3 And a naive answer that is subtler

Follow the gradient downhill and add noise. That is Langevin, it is in
[`methods/langevin.py`](../methods/langevin.py), and it is *nearly* right —
right in the continuous-time limit and wrong at any step size you can actually
take.

The failure is quiet: the chain converges, its error bar shrinks, and it
converges to the wrong distribution. [§7.3](#73-the-price-of-never-rejecting)
computes exactly how wrong.

---

## 5. The minimal model

Every assumption below buys a specific simplification, and every one of them
fails somewhere real.

| Assumption | What it buys | Where it breaks |
|---|---|---|
| The target is $e^{-E/T}$ | One scalar function defines everything | Distributions with no density; discrete supports |
| $E$ is cheap to evaluate | Millions of steps are affordable | A likelihood that needs a PDE solve per call |
| $E$ is differentiable | Langevin exists at all | Discrete variables; hard constraints |
| $T \gt 0$ | There is a distribution to sample | At $T = 0$ it is a delta, and the dynamics is descent |
| One chain | Simplicity | Nothing here can detect a mode it never visited |
| A symmetric proposal | The Metropolis ratio has no $q$ in it | Hastings' correction for asymmetric proposals |
| A fixed step size | One number to reason about | Every real sampler adapts it |
| One dimension | The closed forms exist | The random-walk problem is invisible until $d$ is large |
| Time-independent $T$ | The chain has a stationary distribution | Annealing has none, and is not a sampler |

The last row matters more than it looks. **A chain with a schedule is not a
sampler**, because a moving target has no stationary distribution to converge
to. That is why the annealing experiment writes its own loop instead of going
through `solve.chain`.

---

## 6. The equations

### 6.1 What a Markov chain is

A sequence $x_0, x_1, x_2, \dots$ where the distribution of the next state
depends only on the current one:

$$\mathbb{P}\left(x_{t+1} \mid x_t, x_{t-1}, \dots, x_0\right)
= \mathbb{P}\left(x_{t+1} \mid x_t\right) \equiv K(x_t \to x_{t+1})$$

$K$ is the **transition kernel**. That single line is the whole definition,
and it is the one Markov wrote down to beat Nekrasov: the variables are
dependent — each on the one before — and none of the arguments that need
independence apply.

A distribution $\pi$ is **stationary** for $K$ if running one step from $\pi$
leaves you in $\pi$:

$$\int \pi(x)\thinspace K(x \to y)\thinspace dx = \pi(y)$$

The plan is now visible: **construct a $K$ whose stationary distribution is
the $p$ you want, run it, and read off the states.** Two things have to be
arranged — that $p$ is stationary, and that the chain actually gets there.

### 6.2 Detailed balance, which is a sufficient condition

Stationarity is an integral equation and hard to impose directly. There is a
stronger condition that is trivial to impose and implies it:

$$\boxed{\enspace p(x)\thinspace K(x \to y) = p(y)\thinspace K(y \to x)\enspace}$$

**Detailed balance**: the flow of probability from $x$ to $y$ equals the flow
back. Integrate both sides over $x$ and stationarity falls out, since $K$
integrates to one.

It is worth seeing that this is a physical statement and not a trick. It says
the chain is *reversible* — a movie of it run backwards is statistically
indistinguishable — and that is exactly what "equilibrium" means. A system in
equilibrium has no net current anywhere, which is a stronger claim than "its
distribution is not changing".

### 6.3 Metropolis: enforce it by rejecting

Propose $y$ from a symmetric $q(x \to y) = q(y \to x)$, and accept with
probability $A(x \to y)$. Then $K(x \to y) = q(x \to y)A(x \to y)$ for
$y \neq x$, and detailed balance requires

$$\frac{A(x \to y)}{A(y \to x)} = \frac{p(y)}{p(x)}
= e^{-\left(E(y)-E(x)\right)/T}$$

Any $A$ satisfying that ratio works. The choice that accepts as often as
possible — and therefore explores fastest — is

$$\boxed{\enspace A(x \to y)
= \min\negthinspace\left(1,\ e^{-\Delta E/T}\right)\enspace}$$

$Z$ never appears, because only the ratio does. Nine lines of code, 1953, on a
machine with 1024 words of memory.

**Rejection is not wasted work.** It is the mechanism. The chain stays put
exactly often enough to make the flows balance, and that is why the stationary
distribution is the target *exactly*, at any step size, with no small
parameter anywhere.

### 6.4 Langevin: enforce it by taking a limit

The other route. Write down a continuous-time stochastic process whose
stationary density is $p$:

$$dx = -\nabla E(x)\thinspace \frac{dt}{T} \cdot T + \sqrt{2T}\thinspace dW
\quad\text{i.e.}\quad
dx = -\nabla E\thinspace dt + \sqrt{2T}\thinspace dW$$

The Fokker–Planck equation for this process has $e^{-E/T}$ as its stationary
solution — the drift pushes probability downhill and the diffusion pushes it
back out, and $e^{-E/T}$ is where they balance.

Here too $Z$ vanishes, and for a different reason worth seeing:

$$\log p = -\frac{E}{T} - \log Z
\quad\Longrightarrow\quad
\nabla \log p = -\frac{\nabla E}{T}$$

because the gradient of a constant is zero.

> **The two escapes are the same escape.** $Z$ is a constant, and neither a
> ratio nor the gradient of a logarithm can see a constant. Metropolis uses
> the first fact, Langevin the second.

That gradient of a log density has a name — the **score** — and it is the
object a diffusion model learns rather than deriving from an energy anyone
wrote down. It is learnable *precisely because* it never needs $Z$: there is
nothing to normalise, so there is nothing intractable to fit.

### 6.5 Ergodicity, which is the assumption nobody checks

Stationarity says: if you are already in $p$, you stay. It does not say you
ever get there.

For that you need the chain to be **irreducible** — able to reach any region
from any other — and **aperiodic**. Given both, the chain converges to $p$
from any start, and time averages converge to expectations. That is the
ergodic theorem, and it is what licenses the entire method.

It is also stated for infinite time, and every run is finite. A chain that is
irreducible in principle and takes $e^{10}$ steps to cross a barrier is, for
your purposes, not irreducible at all. **The theorem is true and does not
apply.** That gap has a name in physics — ergodicity breaking — and it is
[§10.2](#102-where-a-chain-lies-to-you).

---

## 7. Two chains, one density

### 7.1 What Metropolis buys and costs

**Exact at any step size.** Rejection enforces detailed balance directly, so
there is no discretisation parameter and no bias to shrink.

**And it is a blind random walk.** The proposal knows nothing about the target
— it steps in a random direction and asks afterwards. The step size has to be
small enough to be accepted and large enough to go somewhere, and those two
demands fight. In $d$ dimensions the optimal acceptance rate falls to 0.234
and the number of steps needed to traverse the distribution grows like $d^2$
(Roberts & Rosenthal 2001).

### 7.2 What Langevin buys

**It knows which way is downhill.** The gradient is information about the
target that Metropolis never asks for, and using it turns a random walk into a
directed drift. That is the whole reason gradient-based samplers exist and why
they dominate in high dimension.

### 7.3 The price of never rejecting

Nothing rejects, so nothing enforces detailed balance, and the discretised
chain has a stationary distribution *near* $p$ rather than $p$.

On $E = x^2/2$ at $T=1$ the update is exactly an AR(1) process:

$$x' = (1 - \Delta t)\thinspace x + \sqrt{2\Delta t}\thinspace \xi$$

whose stationary variance solves $\sigma^2 = (1-\Delta t)^2\sigma^2 + 2\Delta t$:

$$\boxed{\enspace \sigma^2 = \frac{2\Delta t}{1 - (1-\Delta t)^2}
= \frac{1}{1 - \Delta t/2}\enspace}$$

The target has variance 1. **The wrong answer has a closed form**, it is too
wide by $\Delta t/2$ to leading order, and no number of samples removes it.

Reproducing your own error exactly is a far sharper test than being
approximately right, and it is the test the entry is built on.

**The fix has a name.** Metropolis-adjust the Langevin proposal — accept it
with the Metropolis ratio, corrected for the proposal's asymmetry — and the
bias vanishes while the gradient information stays. That is MALA, it is about
two lines, and leaving it out is what makes the bias measurable here.

---

## 8. Scale analysis: how long until it forgets

### 8.1 A million samples are not a million samples

Consecutive states of a chain are nearly the same state. The number that says
how nearly is the **integrated autocorrelation time**

$$\tau = 1 + 2\sum_{k=1}^{\infty} \rho(k),
\qquad \rho(k) = \mathrm{corr}\left(f(x_t), f(x_{t+k})\right)$$

and the honest count of independent samples is

$$N_{\text{eff}} = \frac{N}{\tau},
\qquad
\text{error} = \frac{\sigma}{\sqrt{N_{\text{eff}}}}$$

*Answer to question 2: a million divided by $\tau$, and you have to measure
$\tau$ to know.* It depends on the target, the method, the step size and the
observable, and it is routinely in the tens or hundreds. Reporting
$\sigma/\sqrt{N}$ instead is not a small error — it is claiming an accuracy
you do not have by a factor of $\sqrt{\tau}$.

Note the sum has to be truncated. The tail of an empirical autocorrelation is
noise, and summing all of it adds variance without signal; the standard
automatic window is to stop once the lag exceeds a few times the running
estimate, which is what [`autocorrelation_time()`](../solve.py) does.

### 8.2 Barriers cost exponentially

*Answer to question 3.* The time to cross a barrier of height $\Delta$ at
temperature $T$ grows like

$$t_{\text{cross}} \sim e^{\Delta/T}$$

which is Arrhenius' law, and Kramers' 1940 calculation is where the prefactor
comes from. Doubling $\Delta/T$ does not double the time — it *squares* it.

Measured on the double well with a Metropolis chain, steps between crossings:

| $\Delta/T$ | 1.17 | 1.95 | 2.92 | 3.89 | 4.67 | 5.84 |
|---|---|---|---|---|---|---|
| steps per crossing | 11.8 | 17.9 | 33.2 | 64.4 | 118 | 282 |

Exponential, with an effective barrier *lower* than the landscape's — the
fitted slope is around 0.7 rather than 1 — because a proposal of finite width
can start partway up. Which is the same fact that made the annealing
experiment misbehave until the proposal was made local ([§10.3](#103-the-same-code-optimising)).

### 8.3 And that is what a glass is

Extrapolate the table. At $\Delta/T = 20$ the crossing time is $10^6$ steps;
at 40 it is $10^{12}$; at 100 no computer and no laboratory will ever see one.

The chain still *has* a stationary distribution. The ergodic theorem is still
true. And the system will sit in one basin for longer than the age of the
universe, so the distribution it actually samples is the one restricted to
that basin.

That is not a numerical artefact — it is the physics of glasses, of spin
glasses, of protein misfolding, of any system whose landscape is rugged
enough. **[`hopfield/`](../../hopfield/README.md) is a spin glass**, and the
spurious minima it gets trapped in are the same phenomenon at $T = 0$.

The complex-systems reading of the entry is exactly this: a stationary
distribution is a property of the dynamics, and whether you can *see* it is a
property of your patience.

---

## 9. Closed forms worth memorising

| Situation | Result |
|---|---|
| The target | $p \propto e^{-E/T}$, and only ratios of it are computable |
| Detailed balance | $p(x)K(x\to y) = p(y)K(y\to x)$ |
| Metropolis acceptance | $\min(1, e^{-\Delta E/T})$ |
| Langevin update | $x \leftarrow x - \nabla E\thinspace\Delta t + \sqrt{2T\Delta t}\thinspace\xi$ |
| The score | $\nabla\log p = -\nabla E/T$ |
| Gaussian target, $E=x^2/2$ | $\langle x^2\rangle = T$ exactly |
| Unadjusted Langevin on it | $\langle x^2\rangle = 1/(1-\Delta t/2)$ — the exact bias |
| Free Langevin, $E=0$ | $\langle x^2\rangle = 2Tt$ — Brownian motion |
| Effective sample size | $N/\tau$ |
| Rejection acceptance in $d$ dimensions | $\sigma^{-d}$ — hopeless |
| Optimal Metropolis acceptance, large $d$ | $0.234$ |
| Random-walk traversal cost | $\sim d^2$ steps |
| Barrier crossing time | $\sim e^{\Delta/T}$ |
| Two wells, population ratio | $e^{-\Delta E/T}$ times a width ratio |

**A warning about the last row.** It is tempting to test a sampler by checking
that the low-energy state is more populated than the high-energy one. That
passes on a chain that never left one well, on a biased chain, and on a chain
with the wrong temperature. The closed forms with numbers in them outrank it,
and a diagnostic outranks both — see the next section.

---

## 10. What the simulation showed

### 10.1 The wrong answer, on its own curve

Prediction: Metropolis lands on 1 at any step size; Langevin lands on
$1/(1-\Delta t/2)$, a curve you can draw before running anything.

![Left: measured second moment against step size for Langevin, against the
closed-form bias curve and the target. Right: sampled histograms against the
target density on a log axis.](figures/gaussian.png)

```
   step       langevin <x^2>   1/(1-dt/2)  sigma from 1
   0.50      1.334140+-0.0040     1.333333          82.6
   0.20      1.109683+-0.0056     1.111111          19.6
   0.10      1.050395+-0.0076     1.052632           6.6
   0.05      1.021036+-0.0106     1.025641           2.0
   0.02      0.998665+-0.0163     1.010101           0.1

   step     metropolis <x^2>  acceptance     tau  sigma from 1
   0.30      0.973953+-0.0124       0.905    29.7           2.1
   1.00      0.991364+-0.0058       0.705     6.3           1.5
   3.00      1.000194+-0.0053       0.374     5.2           0.0
```

**What to conclude**, and the third thing was not predicted.

Both predictions held. Now read the Langevin error bars downward as the bias
falls: **0.0040, 0.0056, 0.0076, 0.0106, 0.0163.** They *grow*. A smaller step
is less biased and more correlated, the effective sample size collapses, and
the error bar widens until it covers the bias. At $\Delta t = 0.02$ the chain
is "consistent with 1" at $0.1\sigma$ only because it has become four times
less certain about everything.

**You cannot fix the bias by shrinking the step.** You trade it for
correlation, and the error bar politely hides the swap.

Both methods have a step-size tradeoff and they are different tradeoffs.
Metropolis trades acceptance against exploration — at 0.905 acceptance the
steps are so small that $\tau = 30$, at 0.374 acceptance $\tau = 5$ — and *the
answer never moves*. Langevin trades bias against correlation, and the answer
does.

### 10.2 Where a chain lies to you

![Left: the double-well energy. Right: fraction of time in the right well
against temperature, for both samplers and the exact answer.](figures/double_well.png)

```
     T  barrier/T  exact P(x>0)             metropolis               langevin
  1.00        1.2        0.6216     0.6219 ( 25428 x)     0.5757 (  2395 x)
  0.20        5.8        0.9449     0.9406 (  1030 x)     0.9998 (    16 x)
  0.10       11.7        0.9972     0.9972 (    18 x)     0.0000 (     0 x)
  0.05       23.3        1.0000     1.0000 (     0 x)     0.0000 (     0 x)
```

The bracketed count is barrier crossings.

**What to conclude:** at $T = 0.10$ **Langevin reports 0.0000 where the truth
is 0.9972.** It started in the left well, its steps were too small to climb
out, and it never left — converged-looking, monotone, shrinking error bar, and
the exact opposite of the answer.

And the last row is the sharper one. **Metropolis got it right with zero
crossings.** It crossed during burn-in and then sat still. A right answer from
a chain that never sampled the distribution is not a right answer; it is the
same failure that happened to land on the correct side.

**The diagnostic caught both. Neither number could.** That is the practical
content of §6.5: irreducibility is not something you can read off an estimate,
and a chain reports its basin with exactly the same confidence whether or not
that basin is the distribution.

### 10.3 The same code, optimising

![Left: the trajectory of three temperature schedules. Right: the best energy
each has found so far.](figures/annealing.png)

```
              schedule   final x    final E  best E seen   ended in
    frozen  (T = 0.02)   -0.9985    0.29957      0.29415  LEFT well
     hot     (T = 2.0)   -0.4131    0.81173     -0.30543  LEFT well
 cooled  (2.0 -> 0.02)   +1.0202   -0.30440     -0.30543      right
```

**What to conclude:** frozen never had the energy to cross, so it optimised
whichever well it started in and never even *saw* the global minimum. Hot
found it and would not settle — it is sampling, not optimising. Only cooling
did both.

Optimising and sampling are the same operation at two temperatures, which is
the argument of chapter 10 of the book, measured.

**A correction the setup forced.** The first version used a proposal width of
0.5 and predicted the frozen chain would stay put. It did not — it ended in
the right well. With the wells at $\pm 1$, a width of 0.5 proposes a jump
straight from one minimum to the other, the move is downhill, and it is
accepted at any temperature. **The barrier only traps you if your moves are
local.** Annealing is a cure for local moves, and a proposal wide enough to
clear the barrier in one step means there was no problem to solve — and no
chance of that working in any real number of dimensions.

---

## 11. Where the model stops being true

| Limit | What actually happens | This entry |
|---|---|---|
| Unadjusted Langevin, any $\Delta t$ | Samples a distribution near the target, never it | measured; MALA left out |
| Shrinking $\Delta t$ to fix it | Trades bias for correlation; the error bar hides the swap | measured |
| A barrier much taller than $T$ | Either chain sits in one mode and reports it confidently | measured |
| A right answer with zero crossings | Not evidence of anything | the diagnostic, not the number |
| Proposal wider than the barrier | The barrier stops mattering, and so does annealing | found the hard way |
| High dimension | Acceptance collapses; a random walk needs $\sim d^2$ steps | one dimension only |
| One chain | Cannot detect a mode it never visited | no $\hat R$, no multiple chains |
| A time-dependent temperature | No stationary distribution; it is not a sampler | kept out of `solve.chain` |
| An expensive $E$ | Millions of evaluations stop being free | assumed cheap |

**The one-chain row is the honest summary.** Nothing in this entry can tell
you about a part of the distribution it never reached, and running it longer
does not change that — it changes how confident the wrong answer looks. The
standard defence is several chains from dispersed starts and a comparison of
within- and between-chain variance, and it is not here.

---

## 12. The essentials

- **You can know every ratio of probabilities and no probability.** $Z$ is an
  integral over everything, and everything is too big.
- **Ratios are enough**, if the procedure only ever asks for them.
- **Both methods dodge $Z$ for the same reason**: it is a constant, and
  neither a ratio nor the gradient of a logarithm can see a constant.
- **The gradient of the log density is the score**, and it is what a diffusion
  model learns — learnable exactly because it needs no normaliser.
- **Rejection sampling dies of dimension**, at a rate like $\sigma^{-d}$. Give
  up independence, keep the point you have, and you have a Markov chain.
- **Detailed balance is reversibility**, and it is a sufficient condition for
  stationarity that you can impose one move at a time.
- **Rejecting is the mechanism, not waste.** It is what makes Metropolis exact
  at any step size.
- **Never rejecting is exactly why Langevin is biased**, by $1/(1-\Delta t/2)$
  on a Gaussian — a closed form for being wrong.
- **A million samples are $N/\tau$ samples.** Measure $\tau$ or overstate your
  accuracy by $\sqrt{\tau}$.
- **Barriers cost $e^{\Delta/T}$.** Double the ratio and you square the time.
- **Ergodicity is a theorem about infinite time.** When the time you have is
  shorter, the system has a distribution it cannot reach — and that is what a
  glass is.
- **Convergence is not correctness, and a right answer is not evidence.**
  Check the diagnostic.

---

## 13. Open questions

- **How much does MALA actually buy?** Metropolis-adjusting the Langevin
  proposal removes the bias and keeps the gradient. Two lines, and measuring
  where its acceptance rate collapses would say when the gradient stops
  helping.
- **Why is momentum the answer to random walks?** Hamiltonian Monte Carlo
  travels ballistically instead of diffusing, turning $d^2$ into roughly
  $d^{1/4}$ in the cost of an independent sample. The mechanism is a
  symplectic integrator, which is the same object as the Boris pusher.
- **What does high dimension actually do?** Every closed form here lives in one
  dimension, which is exactly where the interesting failure is invisible.
- **How do you detect a mode you never visited?** You cannot, in general —
  which makes it worth knowing precisely what the standard diagnostics can and
  cannot see.
- **What happens when the score is learned rather than derived?** Replace
  $\nabla E$ with a network's output and Langevin becomes score-based
  generative modelling; add a noise schedule run backwards and it is a
  diffusion model. The pieces are in [`mlp/`](../../mlp/README.md) and here.

---

## 14. References

**Foundational**

- **Metropolis, N., Rosenbluth, A. W., Rosenbluth, M. N., Teller, A. H. &
  Teller, E.** *Equation of state calculations by fast computing machines.*
  Journal of Chemical Physics **21**, 1087–1092 (1953).
  [link](https://doi.org/10.1063/1.1699114)
- **Hastings, W. K.** *Monte Carlo sampling methods using Markov chains and
  their applications.* Biometrika **57**, 97–109 (1970).
  [link](https://doi.org/10.1093/biomet/57.1.97)
- **Markov, A. A.** *An example of statistical investigation of the text*
  Eugene Onegin *concerning the connection of samples in chains* (1913).
  Translated in Science in Context **19**, 591–600 (2006).

**The history**

- **Gubernatis, J. E.** *Marshall Rosenbluth and the Metropolis algorithm.*
  Physics of Plasmas **12**, 057303 (2005).
  [link](https://doi.org/10.1063/1.1887186)
- **Basharin, G. P., Langville, A. N. & Naumov, V. A.** *The life and work of
  A. A. Markov.* Linear Algebra and its Applications **386**, 3–26 (2004).
  [link](https://doi.org/10.1016/j.laa.2003.12.041)
- **Hayes, B.** *First links in the Markov chain.* American Scientist **101**,
  92 (2013).

**Theory and practice**

- **Roberts, G. O. & Tweedie, R. L.** *Exponential convergence of Langevin
  distributions and their discrete approximations.* Bernoulli **2**, 341–363
  (1996). [link](https://doi.org/10.2307/3318418) — the bias, and MALA.
- **Roberts, G. O. & Rosenthal, J. S.** *Optimal scaling for various
  Metropolis-Hastings algorithms.* Statistical Science **16**, 351–367 (2001).
  [link](https://doi.org/10.1214/ss/1015346320) — where 0.234 comes from.
- **Neal, R. M.** *MCMC using Hamiltonian dynamics.* Handbook of Markov Chain
  Monte Carlo, ch. 5 (2011). [link](https://arxiv.org/abs/1206.1901)
- **Kirkpatrick, S., Gelatt, C. D. & Vecchi, M. P.** *Optimization by simulated
  annealing.* Science **220**, 671–680 (1983).

**Complex systems**

- **Kramers, H. A.** *Brownian motion in a field of force and the diffusion
  model of chemical reactions.* Physica **7**, 284–304 (1940). The escape rate.
- **Binder, K. & Young, A. P.** *Spin glasses: experimental facts, theoretical
  concepts, and open questions.* Reviews of Modern Physics **58**, 801 (1986).
- **Palmer, R. G.** *Broken ergodicity.* Advances in Physics **31**, 669 (1982).
  The precise version of §8.3.

**Where it goes**

- **Song, Y. & Ermon, S.** *Generative modeling by estimating gradients of the
  data distribution.* NeurIPS (2019). [link](https://arxiv.org/abs/1907.05600)
- **Ho, J., Jain, A. & Abbeel, P.** *Denoising diffusion probabilistic models.*
  NeurIPS (2020). [link](https://arxiv.org/abs/2006.11239)

---

*Code: [`../distribution.py`](../distribution.py) and
[`../methods/`](../methods/) · Entry: [`../README.md`](../README.md) ·
Repo-wide architecture: [`docs/architecture.md`](../../docs/architecture.md)*
