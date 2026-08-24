# Hopfield network

Associative memory as energy minimisation: store patterns in the couplings,
hand the network a corrupted one, and let it walk downhill until it lands on
the memory. 209 lines of core across two update schedules.

| | |
|---|---|
| **Level** | L1 derive · L2 implement · L3 experiment |
| **Domain** | [`model.py`](model.py) — 98 lines, no dynamics loop in it |
| **Methods** | [`asynchronous.py`](methods/asynchronous.py) 23 · [`synchronous.py`](methods/synchronous.py) 17 |
| **Tests** | 37, split into domain, contract, and where the methods diverge |
| **Migrated from** | [`Optimization-Algorithms/4 Clasificación de eventos y detección de fallos`](https://github.com/FullFran/Optimization-Algorithms) (2024, master's course) |

## Layout

```
model.py              the domain: energy, Hebbian rule, update rule, invariants
methods/
  asynchronous.py     one unit at a time — energy descent guaranteed
  synchronous.py      all units at once — faster, no guarantee
solve.py              termination: sweep until fixed point or cycle
tests/
  test_model.py           domain laws, no dynamics
  test_methods.py         the contract, run against both schedules
  test_methods_differ.py  where they legitimately disagree
```

Same dependency rule as everywhere in this repo: **`methods/` imports `model`,
`model` imports nobody.** See [`docs/architecture.md`](../docs/architecture.md).

## 1. What problem does it solve

Store a handful of patterns. Later, present a corrupted or partial version of
one of them and get the original back — without an index, a lookup key, or a
search. The memory is not stored anywhere you can point at: it is a minimum of
an energy function, and recall is the network rolling into it.

## 2. The equations

Three lines and the model is complete.

**Energy** over bipolar states $s \in \lbrace -1,+1\rbrace ^N$:

$$E(s) = -\tfrac{1}{2}\thinspace s^{\mathsf T} W s$$

**Hebbian learning** — one pass, no gradient, no iteration:

$$W = \frac{1}{N}\sum_{\mu=1}^{P} p^{\mu} (p^{\mu})^{\mathsf T},
\qquad W_{ii} = 0$$

**Dynamics** — align each unit with the field the others exert on it:

$$h_i = \sum_j W_{ij} s_j, \qquad s_i \leftarrow \mathrm{sign}(h_i)$$

Two conditions carry the whole theory: $W$ symmetric and $W_{ii}=0$. Given
those, flipping one unit at a time changes the energy by

$$\Delta E = -\Delta s_i \thinspace h_i \le 0$$

so $E$ is a Lyapunov function and the network cannot wander forever. **That
argument needs the units to move one at a time.** Update them all at once and
it collapses — which is the difference between the two methods here, and it
is physics, not an implementation detail.

## 3. What I implemented

```
model.hebbian_weights()   the learning rule, diagonal cleared
model.energy()            E(s)
model.local_field()       h = W s
model.update_rule()       align with the field; on an exact tie, hold
model.overlap()           m = (1/N) a . b
model.check_weights()     symmetry and zero diagonal — the Lyapunov premises
methods.asynchronous      a sweep is N single-unit updates in random order
methods.synchronous       a sweep is one matrix-vector product
solve.relax()             sweep until a fixed point or a detected cycle
```

## 4. What I verified

37 tests, in three groups. Note what is *not* in the contract: energy descent.
Demanding it from every method would assert something false.

| Property | Scope |
|---|---|
| Weights symmetric, zero diagonal, equal to the averaged outer product | domain |
| Stored patterns sit below random states in energy | domain |
| A stored pattern is a fixed point of the update rule | domain |
| So is its mirror image −p, at identical energy | domain |
| sign(p₁+p₂+p₃) is a fixed point nobody stored | domain |
| A zero field leaves the unit alone — `sign(0)=0` would leave the hypercube | domain |
| States stay bipolar through relaxation | contract |
| A stored pattern does not move | contract |
| Recall from 5%, 15%, 25% flipped bits returns the memory exactly | contract |
| Relaxation always terminates — fixed point or detected cycle | contract |
| **Asynchronous: energy never increases, always reaches a fixed point** | async only |
| **Synchronous: energy can rise, and 2-cycles occur** | sync only |

### The experiments from the class activity

All five results of the original assignment, reproduced.

**[`recall.py`](experiments/recall.py)** — the stored patterns with their
energies, and reconstruction from 25% noise:

```
   pattern       energy        E/N
     cross      -320.50    -0.5564
      ring      -310.11    -0.5384
 diagonals      -319.22    -0.5542
      bars      -299.39    -0.5198
random state      -0.18    -0.0003   (mean of 200)

   pattern   overlap in  overlap out   sweeps           dE
     cross        0.500        1.000        2      -239.67
      ring        0.500        1.000        2      -231.42
 diagonals        0.500        1.000        2      -230.42
      bars        0.500        1.000        2      -224.06
```

A quarter of the bits wrong, and every pattern comes back exactly in two
sweeps. Stored states sit at E/N ≈ −0.55 while a random state sits at ≈ 0 —
the memories really are the valleys.

**[`associative_and_spurious.py`](experiments/associative_and_spurious.py)** —
and here the script did not get what it expected, which turned out to be the
more interesting outcome:

```
ring variant (never stored)     -> settles at overlap +0.715 with ring   SPURIOUS
checkerboard (unrelated)        -> settles exactly on −ring              a memory
sign(cross+ring+diagonals)      -> flows to ring                         a memory
```

The near-miss ring does **not** recover the stored ring: it stops in a nearby
valley that is not a memory. The unrelated checkerboard lands exactly on the
*mirror* of a memory, which is the sign symmetry from the domain tests showing
up in practice. And the textbook three-pattern mixture is not stable here at
all — it flows to `ring`.

That last one is not a bug, it is correlation. The glyphs share a lot of
structure, which reshapes the landscape. With uncorrelated patterns the
mixture behaves as the theory says, and the script checks it in the same run:

```
random patterns: mixture is a fixed point -> True
overlaps with the three memories: +0.490  +0.472  +0.545
```

**[`capacity.py`](experiments/capacity.py)** — the storage limit, error against
load P/N for three network sizes:

```
   P/N     N=100     N=250     N=500
 0.080    0.0000    0.0002    0.0001
 0.100    0.0005    0.0026    0.0011
 0.120    0.0100    0.0038    0.0056
 0.138    0.0160    0.0328    0.0412
 0.160    0.0370    0.0638    0.1040
 0.200    0.0700    0.1720    0.1577
 0.250    0.1220    0.3014    0.2968
```

The knee sits where theory puts it, at α_c ≈ 0.138. And the class observation
is reproduced: past the transition the error grows faster for larger networks
— at α = 0.16 the error roughly triples from N = 100 to N = 500. The
transition sharpens with size, as a phase transition should.

## 5. What I deliberately left out

- **Continuous / Hopfield–Tank networks.** Binary units only, so no TSP
  solving — a different use of the same energy idea.
- **Finite temperature.** These dynamics are Metropolis at T = 0: only moves
  that lower the energy are accepted. A Boltzmann machine is the T > 0 version.
- **Storage rules that beat Hebb.** No pseudo-inverse, no Storkey rule, both
  of which push capacity well past 0.138.
- **Modern / dense associative memory.** The exponential-capacity variants
  behind "Hopfield Networks is All You Need" are a separate entry.
- **Sparse or structured couplings.** `W` is a dense N×N array, which is what
  caps the usable image size.
- **Bias terms.** No external field.

## Where this stops being right

| Boundary | What happens |
|---|---|
| Correlated patterns | Recall degrades well before α_c; the glyph experiment above shows it |
| Load above ≈ 0.138 | Recall breaks down — measured, not assumed |
| Dense `W` | N² floats. The 2024 version used 75×75 images: 5625² ≈ 253 MB of couplings |
| Synchronous updates | No energy guarantee; may oscillate with period 2 |

## Provenance: the 2024 version

Original: `Optimization-Algorithms/4 Clasificación de eventos y detección de
fallos/hopfiled.py` (filename typo included), 4.1 KB, a `HopfieldNet` class
over 75×75 thresholded photographs.

The physics in it was right. What the rewrite changed:

| | 2024 | now |
|---|---|---|
| Normalisation | `weights /= len(patterns)` — divides by P, while the docstring says divide by N | divide by N |
| Activation | `np.sign`, which returns 0 on an exact tie and drops the unit off {−1,+1} | hold the current value |
| Termination | `update(steps=1)` — the caller guesses how many single-unit updates to run | sweep until fixed point or detected cycle |
| Schedules | asynchronous only | both, so the Lyapunov argument can be contrasted with the case where it fails |
| Tests | none | 37 |

The normalisation one is worth being precise about: dividing by P instead of N
is an overall scale on `W`, and `sign()` does not care about scale, so **the
dynamics were unaffected**. What it changes is the energy value, so energies
were not comparable between networks trained on different numbers of patterns
— which is exactly what the capacity experiment does.

The patterns here are generated glyphs rather than the original photographs:
those cannot go in a public repo, and photographs are strongly biased toward
one colour, which correlates the patterns and degrades recall for reasons that
have nothing to do with the model.

## Run it

```bash
uv run pytest hopfield                                       # 37 tests
uv run python hopfield/experiments/recall.py
uv run python hopfield/experiments/associative_and_spurious.py
uv run python hopfield/experiments/capacity.py               # ~20 s
```

## What this sets up

Hopfield is the first stop on the road to diffusion: a probability landscape
defined by an energy, and sampling implemented as descent on it. Change T = 0
to T > 0 and it is a Boltzmann machine; replace the explicit energy with a
learned score ∇ log p and the descent with a noise schedule, and it is a
diffusion model.
