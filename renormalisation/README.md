# Renormalisation

Zoom out. If the system looks like itself with a different parameter, you have
a map, and the critical point is where that map stands still. On percolation
the whole calculation is one polynomial — and for a block of two it is
$2p^2 - p^4$, whose fixed point is the golden ratio. 293 lines of core.

| | |
|---|---|
| **Level** | L1 derive · L2 implement · L3 experiment |
| **Domain** | [`flow.py`](flow.py) — 178 lines, no block-size sweep in it |
| **Methods** | [`enumeration.py`](methods/enumeration.py) 25 · [`sampling.py`](methods/sampling.py) 38 |
| **Tests** | 63, split into domain, contract, and where the methods diverge |
| **Acts on** | [`forest-fire/`](../forest-fire/), which is where the threshold comes from |

## Layout

```
flow.py               the domain: the block rule, the map, its fixed points
methods/
  enumeration.py      count every configuration — exact, and stops at b = 4
  sampling.py         count a sample at fixed occupancy — error bars, no ceiling
solve.py              the plain scheme, and the cell-to-cell one
experiments/
  convergence.py      does a bigger block give a better answer? (half of one)
                      figures go to experiments/out/ until a derivation uses them
tests/
  test_flow.py            domain laws, no scheme chosen
  test_methods.py         the contract, run against both
  test_methods_differ.py  where they legitimately disagree
```

Same dependency rule as everywhere in this repo: **`methods/` imports `flow`,
`flow` imports nobody.** See [`docs/architecture.md`](../docs/architecture.md).

## 1. What problem does it solve

[`forest-fire/`](../forest-fire/) has a threshold: below a tree density of
$p_c = 0.5927460$ a fire cannot cross the lattice, above it a fire can. The
number is measured, and two questions are left over.

**Why is it that number?** And, much more strangely, **why do systems with
nothing in common share the same critical exponents?** A magnet, a liquid at
its critical point and a percolating lattice have different constituents,
different interactions and different physics, and their exponents agree.

The answer to both is one idea: coarse-grain, and see what survives.

## 2. The equations

Group the lattice into blocks of $b \times b$ sites and ask when a block counts
as occupied at the coarse scale. Connection is what has to survive — a block
full of disconnected sites does not conduct — so the criterion is spanning.

Then the coarse density is a polynomial in the fine one:

$$R(p) = \sum_k N_k\thinspace p^k (1-p)^{b^2 - k}$$

with $N_k$ the number of spanning configurations having $k$ sites occupied.
That is the entire renormalisation group for this problem: **one polynomial.**

For $b = 2$ with a top-to-bottom rule it is small enough to do on paper —
$R(p) = 2p^2 - p^4$ — and $R(p^{\ast}) = p^{\ast}$ factors as
$(p-1)(p^2 + p - 1) = 0$, giving

$$p^{\ast} = \frac{\sqrt5 - 1}{2} = 0.618034$$

the golden ratio, 4.3% from the true threshold.

**The fixed point is unstable**, and that is the point. Below it, repeated
coarse-graining drives the density to zero and the system looks empty at large
scales; above it, to one. Only exactly on it does the system look the same at
every scale, which is what scale invariance at a critical point means.

The exponent comes from the slope. One step multiplies the distance from the
fixed point by $\lambda = dR/dp$ while dividing lengths by $b$, so if
$\xi \sim |p - p^{\ast}|^{-\nu}$ then

$$\nu = \frac{\ln b}{\ln \lambda}$$

**An exponent out of a derivative.** Nothing about the microscopic lattice
survives into it — that is universality, and this is the mechanism behind it.

## 3. What I implemented

```
flow.P_C, flow.NU         the two numbers to be checked against
flow.spans()              when a coarse block counts as occupied — three rules
flow.block_polynomial()   the spanning counts, by exhaustive enumeration
flow.recursion()          the counts turned into the map R(p)
flow.fixed_point()        where R(p) = p, other than 0 and 1
flow.slope(), exponent()  dR/dp, and nu = ln(b)/ln(lambda)
methods.enumeration       exact, 2^(b*b) work
methods.sampling          at fixed occupancy, with a binomial coefficient
solve.scheme()            block to site
solve.cell_to_cell()      block to block, which is the one that works
```

## 4. What I verified

63 tests, in three groups. Note what is *not* in the contract: getting the
right answer. A renormalisation scheme is a **choice**, and different choices
land in different places — which is the entry rather than a defect.

| Property | Scope |
|---|---|
| **The 2×2 vertical map is exactly $2p^2 - p^4$** | domain |
| **Its fixed point is exactly the golden ratio** | domain |
| $R(0) = 0$ and $R(1) = 1$ — the two trivial fixed points | domain |
| The map is increasing: more trees cannot conduct less | domain |
| **The fixed point is unstable, for every rule and block** | domain |
| The flow runs away from it in both directions | domain |
| Connection is what counts, not how many sites | domain |
| A stable fixed point has no exponent | domain |
| The empty and full blocks are counted exactly | contract |
| A block cannot span with fewer sites than a side | contract |
| There is an unstable fixed point, and an exponent | contract |
| **Cell-to-cell beats the plain scheme** | contract |
| **The two counting methods agree wherever both can run** | differ |
| **Enumeration refuses a block it cannot finish** | differ |
| **Sampling keeps going where enumeration stops** | differ |
| **The plain scheme is stuck with the vertical rule** | differ |
| **`either` and `both` bracket the true threshold** | differ |

### The experiment

**[`convergence.py`](experiments/convergence.py)** — prediction, written down
first: enlarging the block improves the answer, and the plain scheme converges
on $p_c$ and $\nu = 4/3$.

**Half right, and the wrong half is the interesting one.**

```
1. THE PLAIN SCHEME
       rule   b         p*    error        nu    error
   vertical   2   0.618034     4.3%    1.6353    22.6%
   vertical   3   0.619260     4.5%    1.6245    21.8%
   vertical   4   0.619355     4.5%    1.6067    20.5%

     either   2   0.381966    35.6%    1.6353    22.6%
     either   3   0.472628    20.3%    1.5113    13.3%
     either   4   0.509355    14.1%    1.4853    11.4%
```

With the vertical rule **the block size does nothing** — 0.618, 0.619, 0.619.
It does not converge slowly, it sits still. Asking for a top-to-bottom path
only is a biased criterion, and a bigger block does not cure a bias.

With `either` it does improve, and the striking thing is that `either` and
`both` **bracket the true value from opposite sides**: at $b = 4$ they give
0.509 and 0.708, closing in on 0.5927 from below and above. Two schemes that
disagree are worth more than one that happens to be close.

```
2. CELL TO CELL:  R_small(p) = R_large(p)  instead of  R(p) = p
       rule   blocks         p*    error        nu    error
     either      2,3   0.559599     5.6%    1.2791     4.1%
     either      3,4   0.591046     0.3%    1.3758     3.2%
     either      2,4   0.574132     3.1%    1.3161     1.3%
```

**0.591046 against a true 0.5927460 — three parts in a thousand**, out of
blocks of at most sixteen sites, and the exponent to 1.3%. Comparing two
*blocks* rather than a block against a *site* cancels most of what the block
rule gets wrong, because both sides of the comparison are then the same kind of
object.

The plain scheme was comparing a block with a single site and calling them the
same thing. They are not, and no amount of enlarging the block makes them so.

## 5. What I deliberately left out

- **Momentum-space renormalisation.** Wilson's actual method, the epsilon
  expansion, and everything the 1982 Nobel was for. Real-space on percolation
  is the version you can do by hand, and it is a cousin rather than the thing.
- **The Ising model.** Block-spin renormalisation on Ising is the canonical
  worked example and needs a coupling constant rather than a probability, so
  the map is two-dimensional and the flow has directions.
- **Relevant and irrelevant operators.** With one parameter there is one
  eigenvalue and no room for the classification that explains universality
  properly.
- **Every other exponent.** $\beta$, $\gamma$, $\eta$ and the scaling
  relations between them. $\nu$ is the one the flow gives directly.
- **Larger blocks.** The sampler reaches $b = 6$ and beyond; the entry stops
  at 4 because that is where enumeration can still check it.

## Where this stops being right

| Boundary | What happens |
|---|---|
| **The plain scheme with a biased rule** | Does not converge at all — 0.618, 0.619, 0.619 |
| A block mapped to a site | Compares two different objects; cell-to-cell exists because of it |
| Enumeration past $b = 4$ | 2^25 configurations; refuses rather than hanging |
| Sampling | Error bars on every coefficient, and no exact answer |
| One parameter | Real flows are multi-dimensional; this cannot see an irrelevant direction |
| The exponent | Harder than the threshold, and the number that actually tests the scheme |

**The exponent row is the honest one.** A fixed point can land near $p_c$ for
uninteresting reasons — it is one number in the unit interval. $\nu$ comes from
the *derivative* at that point and is much harder to get by accident, which is
why the table above reports both and why the plain scheme looks far worse in
the second column than the first.

## Run it

```bash
uv run pytest renormalisation                                # 63 tests, ~40 s
uv run python renormalisation/experiments/convergence.py     # ~60 s
```

## What this sets up

Diffusion, and not by analogy. A diffusion model's forward process destroys
structure a little at a time, and its reverse process rebuilds it — which is a
flow in the space of distributions with a fixed point at pure noise. The
vocabulary here is the vocabulary there: coarse-graining, a flow, what survives
it and what does not.

The one piece still missing for that entry is learning a score instead of
deriving it, and [`mlp/`](../mlp/) already knows how to learn a function from
its gradients.
