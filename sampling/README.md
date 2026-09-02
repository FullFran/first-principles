# Sampling an energy landscape

You can evaluate an energy anywhere and you can never normalise it. Two chains
live with that in different ways: one compares heights and rejects, the other
follows the gradient and never rejects. One is exact and one is biased by a
known amount. 356 lines of core.

| | |
|---|---|
| **Level** | L1 derive · L2 implement · L3 experiment |
| **Domain** | [`distribution.py`](distribution.py) — 152 lines, no chain in it |
| **Methods** | [`metropolis.py`](methods/metropolis.py) 33 · [`langevin.py`](methods/langevin.py) 35 |
| **Tests** | 56, split into domain, contract, and where the methods diverge |
| **Related work of mine** | [`GPU-accelerated-Ising-Model`](https://github.com/FullFran/GPU-accelerated-Ising-Model) — Metropolis–Hastings on the 3D Ising model, at a scale this entry deliberately is not |

## Layout

```
docs/distribution.md  the derivation, from the phenomenon down
docs/figures/         the figures it argues from — tracked, unlike out/
distribution.py       the domain: energies, gradients, the density, closed forms
methods/
  metropolis.py       propose and accept on a ratio — exact, and a random walk
  langevin.py         follow the gradient and add noise — biased by O(dt)
solve.py              run a chain, report what it is worth after correlation
experiments/
  gaussian.py         the bias, against its own closed form
  double_well.py      where a chain lies to you and nothing says so
  annealing.py        the same code optimises at T→0 and samples at fixed T
tests/
  test_distribution.py    domain laws, no chain involved
  test_methods.py         the contract, run against both samplers
  test_methods_differ.py  where they legitimately disagree
```

Same dependency rule as everywhere in this repo: **`methods/` imports
`distribution`, `distribution` imports nobody.** See
[`docs/architecture.md`](../docs/architecture.md).

## 1. What problem does it solve

You have an energy $E(x)$ and you want samples from the density it defines:

$$p(x) = \frac{e^{-E(x)/T}}{Z}, \qquad Z = \int e^{-E(x)/T}\thinspace dx$$

You can compute $E$ anywhere. **You cannot compute $Z$** — it is an integral
over the whole space, and in any interesting number of dimensions it is
unobtainable. So you can compute *ratios* of probabilities and never a
probability.

Every method here is a way of living with exactly that.

## 2. The equations

Derived from the problem downwards — what Markov chains are, where they came
from (an argument about free will), detailed balance, ergodicity and where it
all stops — in [`docs/distribution.md`](docs/distribution.md).

**Metropolis.** Propose $y$, accept it with

$$\min\negthinspace\left(1,\ \frac{p(y)}{p(x)}\right)
= \min\negthinspace\left(1,\ e^{-\left(E(y)-E(x)\right)/T}\right)$$

$Z$ cancels because it is in the numerator and the denominator. Rejecting is
what enforces detailed balance,

$$p(x)\thinspace q(x \to y)\thinspace A(x \to y)
= p(y)\thinspace q(y \to x)\thinspace A(y \to x)$$

so the stationary distribution is the target **exactly, at any step size**.

**Langevin.** Follow the gradient and add noise:

$$x \leftarrow x - \nabla E(x)\thinspace \Delta t
\thinspace + \thinspace \sqrt{2T\Delta t}\thinspace \xi$$

$Z$ vanishes here too, for a different reason. The drift is the gradient of
the log density, and $\log p = -E/T - \log Z$, so

$$\nabla \log p = -\frac{\nabla E}{T}$$

because the gradient of a constant is zero.

> **Both methods work for the same reason.** $Z$ is a constant, and neither a
> ratio nor the gradient of a logarithm can see a constant. One exploits the
> first fact and one the second.

That gradient of a log density has a name — the **score** — and it is what a
diffusion model learns instead of deriving it from an energy anyone wrote
down. It is learnable *because* it never needs $Z$.

Two limits worth holding on to: set $T = 0$ and Langevin is the gradient
descent of [`mlp/`](../mlp/); set $E = 0$ and it is Brownian motion, with
$\langle x^2\rangle = 2Tt$, whose continuum limit is the diffusion equation.

## 3. What I implemented

```
distribution.Target           an energy and its gradient; everything else derives
distribution.GAUSSIAN         E = x²/2, every moment known
distribution.DOUBLE_WELL      two minima and a barrier, populations computable
distribution.FREE             no energy at all — Brownian motion
distribution.exact_moment()   ⟨xⁿ⟩ by quadrature, the reference
distribution.exact_probability()  P(a < x < b) by quadrature
methods.metropolis            propose, compare, accept or reject
methods.langevin              gradient step plus noise, never rejects
solve.chain()                 run it, and report the correlation-corrected error
solve.autocorrelation_time()  how many steps before the chain forgets
```

## 4. What I verified

56 tests, in three groups. Note what is *not* in the contract: that the chain
samples the target. Metropolis does and unadjusted Langevin does not, and
demanding it of both would assert something false.

| Property | Scope |
|---|---|
| The Gaussian's second moment is exactly the temperature | domain |
| **Only energy differences matter** — shift E by 137 and nothing changes | domain |
| Every gradient matches a finite-difference derivative | domain |
| The double well's leftover population follows exp(−ΔE/T) | domain |
| The quadrature support is wide enough not to truncate | domain |
| T ≤ 0 is rejected — it is a delta, not a distribution | domain |
| A symmetric target gives a zero mean, for both | contract |
| The chain visits the low-energy region and actually moves | contract |
| A colder chain stays closer to the minimum | contract |
| **Correlated samples are worth less than independent ones** | contract |
| Independent draws are worth their face value — the control | contract |
| **Metropolis is unbiased at any step size** | differ |
| **Langevin is biased by exactly 1/(1−Δt/2)** | differ |
| More samples fix Metropolis and do not fix Langevin | differ |
| Only Metropolis rejects, and that is where the bias comes from | differ |
| **Only Langevin ever asks for the gradient** | differ |
| A barrier traps either of them, and neither says so | differ |

The second differ row is the one that pays for the entry. On $E = x^2/2$ the
Langevin update is an AR(1), $x' = (1-\Delta t)x + \sqrt{2\Delta t}\thinspace\xi$,
whose stationary variance is $1/(1-\Delta t/2)$. **The wrong answer has a
closed form**, and reproducing your own error exactly is a far sharper test
than being approximately right.

### The experiments

**[`gaussian.py`](experiments/gaussian.py)** — prediction: Metropolis lands on
1 at any step size, Langevin lands on a curve you can draw in advance.

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

Both held, and a third thing appeared that was not predicted. **Read the
Langevin error bars downward as the bias shrinks: 0.0040, 0.0056, 0.0076,
0.0106, 0.0163.** They *grow*. A smaller step is less biased and more
correlated, so the effective sample size collapses and the error widens to
cover the bias. At Δt = 0.02 the chain is "consistent with 1" at 0.1σ only
because it has become four times less certain about everything.

**You cannot fix the bias by shrinking the step.** You trade it for
correlation, and the error bar politely hides the swap.

Both methods have a step-size tradeoff and they are different tradeoffs.
Metropolis trades acceptance against exploration — at 0.905 acceptance the
steps are so small that τ is 30, at 0.374 acceptance τ is 5 — and *the answer
never moves*. Langevin trades bias against correlation, and the answer moves.

**[`double_well.py`](experiments/double_well.py)** — prediction: at high
temperature both recover the populations, at low temperature a chain can get
stuck.

```
     T  barrier/T  exact P(x>0)             metropolis               langevin
  1.00        1.2        0.6216     0.6219 ( 25428 x)     0.5757 (  2395 x)
  0.20        5.8        0.9449     0.9406 (  1030 x)     0.9998 (    16 x)
  0.10       11.7        0.9972     0.9972 (    18 x)     0.0000 (     0 x)
  0.05       23.3        1.0000     1.0000 (     0 x)     0.0000 (     0 x)
```

The bracketed count is barrier crossings. At T = 0.10 **Langevin reports 0.0000
where the truth is 0.9972** — it started in the left well, its steps were too
small to climb out, and it never left. Converged-looking, monotone, with a
shrinking error bar, and the exact opposite of the answer.

And look at the last row, which is the sharper one. **Metropolis got it right
with zero crossings.** It crossed during burn-in and then sat still. A right
answer from a chain that never sampled the distribution is not a right answer
— it is the same failure that happened to land on the correct side. The
diagnostic caught what the number could not.

**[`annealing.py`](experiments/annealing.py)** — the same code, three
temperature schedules.

```
              schedule   final x    final E  best E seen   ended in
    frozen  (T = 0.02)   -0.9985    0.29957      0.29415  LEFT well
     hot     (T = 2.0)   -0.4131    0.81173     -0.30543  LEFT well
 cooled  (2.0 -> 0.02)   +1.0202   -0.30440     -0.30543      right
```

Frozen never had the energy to cross, so it optimised whichever well it
started in — and never even *saw* the global minimum. Hot found it and would
not settle: it is sampling, not optimising. Only cooling did both.

This is chapter 10 of the book measured: optimising and sampling are the same
operation at two temperatures.

**A correction the setup forced.** The first version used a proposal width of
0.5 and predicted the frozen chain would stay put. It did not — it ended in
the right well. With the wells at ±1, a width of 0.5 proposes a jump straight
from one minimum to the other, the move is downhill, and it is accepted
whatever the temperature. **The barrier only traps you if your moves are
local.** Annealing is a cure for local moves; a proposal wide enough to clear
the barrier in one step means there was no problem — and no hope of that
working in any real number of dimensions.

## 5. What I deliberately left out

- **MALA.** Metropolis-adjusting the Langevin proposal removes the bias
  entirely and keeps the gradient. It is the obvious fix, it is two lines, and
  leaving it out is what makes the bias measurable here.
- **Hamiltonian Monte Carlo.** The answer to the random-walk problem: use
  momentum so the chain travels instead of diffusing.
- **Gibbs sampling.** Which is what the Ising model in my other repo uses.
- **Hidden units and learning an energy.** A visible Boltzmann machine is this
  entry's `DOUBLE_WELL` with more dimensions. *Training* one needs contrastive
  divergence and the intractable Z, and that is a separate entry.
- **Convergence diagnostics beyond one chain.** No $\hat R$, no multiple
  chains, no comparison of within- and between-chain variance — which is the
  standard way to catch exactly the double-well failure above.
- **Anything in high dimension.** All targets here are one-dimensional, which
  is where the closed forms live and where the random-walk problem is invisible.

## Where this stops being right

| Boundary | What happens |
|---|---|
| Unadjusted Langevin, any Δt | Samples a distribution *near* the target, never the target |
| Shrinking Δt to fix that | Trades bias for correlation; the error bar widens to hide it |
| A barrier much taller than T | Either chain can sit in one mode forever and report it confidently |
| A right answer with zero crossings | Not evidence of anything — check the diagnostic, not the number |
| Proposal wider than the barrier | The barrier stops mattering, and so does annealing |
| High dimension | Metropolis acceptance collapses; a random walk needs ~d² steps to cross |
| One chain only | Nothing here can detect a mode it never visited |

The last row is the honest summary of the entry's limits. **A single chain
cannot tell you about a part of the distribution it never reached**, and no
amount of running it longer changes that.

## Run it

```bash
uv run pytest sampling                              # 56 tests, ~22 s
uv run python sampling/experiments/gaussian.py      # ~30 s
uv run python sampling/experiments/double_well.py   # ~40 s
uv run python sampling/experiments/annealing.py
```

The slowest suite in the repo, and for a reason that is not a defect: a chain
is sequential by definition, so there is nothing to vectorise. Every other
entry batches its work; this one cannot.

## What this sets up

Diffusion. A diffusion model is Langevin with the score $\nabla \log p$
*learned* instead of derived, plus a noise schedule — which is
[`annealing.py`](experiments/annealing.py) run in the other direction. The
pieces are now all here: [`mlp/`](../mlp/) learns a function from its
gradients, [`hopfield/`](../hopfield/) has an energy landscape written by hand,
and this has the sampler that turns one into the other.
