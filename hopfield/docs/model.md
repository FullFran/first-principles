# Memory as a landscape

> The theory behind [`hopfield/`](../README.md), derived from the problem rather
> than from the formula. Read this if you want to know *why* the equations in
> `hopfield/model.py` are those and not others.

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
2. [What associative memory is for](#2-what-associative-memory-is-for)
3. [Before you calculate](#3-before-you-calculate)
4. [Why the naive answer fails](#4-why-the-naive-answer-fails)
5. [The minimal model](#5-the-minimal-model)
6. [The equations](#6-the-equations)
7. [Two schedules, one energy](#7-two-schedules-one-energy)
8. [Scale analysis: reading the answer off the crosstalk](#8-scale-analysis-reading-the-answer-off-the-crosstalk)
9. [Closed forms worth memorising](#9-closed-forms-worth-memorising)
10. [What the simulation showed](#10-what-the-simulation-showed)
11. [Where the model stops being true](#11-where-the-model-stops-being-true)
12. [The essentials](#12-the-essentials)
13. [Open questions](#13-open-questions)
14. [References](#14-references)

---

## 1. The phenomenon

You hear three notes and the whole song arrives. You see a quarter of a face
across a bar and you know who it is before you know that you know. Someone
says "it was that film with the... the boat" and forty seconds later the title
surfaces on its own, without you searching for it.

None of that is how a computer remembers. A computer remembers by **address**:
you hand it a key, it hands you back a value, and if the key is wrong by one
bit you get nothing. What you just did is remember by **content**: the
fragment *is* the query, the query is a corrupted version of the answer, and
the retrieval degrades smoothly instead of failing.

That is the phenomenon. It has three properties worth naming because a model
has to reproduce all three:

- **No key.** The probe and the stored item live in the same space.
- **Graceful degradation.** Half the pattern is enough. A quarter often is.
- **No search.** The time to recall does not grow with how much you know.

> **The question.**
> $N$ two-state units. $P$ patterns $p^{1},\dots,p^{P}$, each a vector in
> $\lbrace -1,+1\rbrace^{N}$, are to be stored. Later a corrupted probe
> arrives.
> **What dynamics returns the stored pattern, how corrupted may the probe be,
> and how large can $P$ get before the whole thing stops working?**

Those three questions have three different answers and they are the content of
this document. The last one has a number attached — $P \simeq 0.138\thinspace N$
— and the number is much smaller than almost everyone guesses.

---

## 2. What associative memory is for

Worth going through before any equations, because the applications tell you
which regime of the equations matters.

### 2.1 A model of what a brain might be doing

This is the original motivation and it is still the strongest one. Hopfield's
1982 paper is titled *Neural networks and physical systems with emergent
collective computational abilities*, and the claim in that title is the whole
idea: **a computational property — content-addressable memory — emerging from
a physical system nobody designed to have it.**

The units are not storing anything. No neuron holds "the cat". The memory is a
property of the *couplings*, distributed across all of them, and it is
recovered by letting the system relax. Damage a fraction of the units and the
memory degrades rather than disappearing, which is what biological memory
actually does and what a lookup table conspicuously does not.

The 2024 Nobel Prize in Physics went to Hopfield and Hinton for this line of
work — for using tools from statistical physics to build machines that learn.

### 2.2 Optimisation: any cost function is an energy

The dynamics here minimises $E(s) = -\tfrac12 s^{\mathsf T}Ws$. Turn that
around: **give me a problem whose cost is a quadratic form over binary
variables and I will build a network that descends it.** That is the
Hopfield–Tank construction (1985), which encoded the travelling salesman
problem in exactly this shape.

The honest history is that it worked badly on TSP — the constraints have to be
smuggled in as penalty terms and the network cheerfully finds invalid tours —
but the *idea* survived and is now enormous. Quadratic unconstrained binary
optimisation (QUBO) is the input format of every quantum annealer and every
Ising-machine accelerator built in the last decade. They are all solving the
problem in this document, in hardware.

The connection runs the other way too, and it is the more useful direction:
this network is a **spin glass at zero temperature**. Everything the physics
of disordered magnets knows about rugged landscapes — metastable states,
frustration, why annealing helps — transfers directly.

### 2.3 Content-addressable memory in hardware

Routers do this for real, millions of times a second. A TCAM (ternary
content-addressable memory) is handed a destination address and returns the
matching routing-table entry in one clock cycle by comparing against every
stored word in parallel. Different mechanism entirely — no dynamics, no
energy — but the same interface, and it is worth knowing that the "look up by
content" problem has a brutally direct silicon answer that costs a great deal
of power.

### 2.4 Error correction

A codeword corrupted by noise, restored to the nearest valid codeword. Written
that way it is the same problem, and the Hopfield network is a (bad) decoder:
the stored patterns are the codewords and the basins of attraction are the
decoding regions. It is bad because Hebbian storage wastes most of the
capacity ([§8.6](#86-the-cost-of-a-coupling)), which is precisely why coding
theory builds its codes algebraically instead. Useful as a sanity check on
what "capacity" ought to mean.

### 2.5 The road to everything downstream

| Change one thing | And you get |
|---|---|
| $T = 0 \to T \gt 0$ | Boltzmann machine — sampling instead of descending |
| Visible units $\to$ hidden units | Restricted Boltzmann machines, deep belief nets |
| Quadratic $E \to$ higher-order $E$ | Dense associative memory: capacity grows as $N^{k-1}$ |
| Discrete $\to$ continuous states | Hopfield 1984, and the modern Hopfield layer |
| Explicit $E \to$ learned $\nabla \log p$ | Score matching, and then diffusion models |

The fourth row is worth pausing on. Ramsauer et al. (2020) showed that a
continuous Hopfield network with an exponential interaction has an update rule
that **is** the attention mechanism of a transformer — one step of
$\mathrm{softmax}(\beta QK^{\mathsf T})V$ is one step of retrieval in an
associative memory with exponentially many stored patterns. The title of that
paper, *Hopfield Networks is All You Need*, is a joke that turned out to be
approximately true.

### Papers worth reading

| Reference | Why |
|---|---|
| [Hopfield, *PNAS* **79**, 2554 (1982)](https://www.pnas.org/doi/10.1073/pnas.79.8.2554) | The paper. Energy, Hebbian storage, asynchronous descent — nine pages |
| [Little, *Math. Biosci.* **19**, 101 (1974)](https://doi.org/10.1016/0025-5564(74)90031-5) | The synchronous version, eight years earlier, and largely unread |
| [Amit, Gutfreund & Sompolinsky, *PRL* **55**, 1530 (1985)](https://doi.org/10.1103/PhysRevLett.55.1530) | Where $\alpha_c = 0.138$ comes from. Replica theory, not counting |
| [McEliece et al., *IEEE Trans. Inf. Theory* **33**, 461 (1987)](https://doi.org/10.1109/TIT.1987.1057328) | The other capacity, $N/(4\ln N)$, for *every* pattern exactly |
| [Gardner, *J. Phys. A* **21**, 257 (1988)](https://doi.org/10.1088/0305-4470/21/1/030) | $\alpha_{\max} = 2$ for the best possible couplings. Hebb wastes 93% |
| [Goles-Chacc, Fogelman-Soulié & Pellegrin, *Discrete Appl. Math.* **12**, 261 (1985)](https://doi.org/10.1016/0166-218X(85)90029-0) | Why synchronous updates give period 1 or 2 and never 3 |
| [Hopfield & Tank, *Biol. Cybern.* **52**, 141 (1985)](https://doi.org/10.1007/BF00339943) | Optimisation as relaxation. Instructive partly because it failed |
| [Krotov & Hopfield, *NeurIPS* (2016)](https://arxiv.org/abs/1606.01164) | Higher-order energies break the $0.138\thinspace N$ ceiling |
| [Ramsauer et al., arXiv:2008.02217](https://arxiv.org/abs/2008.02217) | The modern Hopfield layer is attention |

Books: Hertz, Krogh & Palmer, *Introduction to the Theory of Neural
Computation*, ch. 2–3 for the clearest derivation; Amit, *Modeling Brain
Function* for the statistical mechanics; MacKay, *Information Theory,
Inference and Learning Algorithms*, ch. 42 for the information-theoretic view
and the best single page on why capacity is what it is.

### A note on the history

Three things in this story are worth knowing because they repeat.

**The synchronous model came first and got no credit.** W. A. Little published
the parallel-update version in 1974, complete with the persistent-states
argument. Hopfield's 1982 contribution was the asynchronous schedule and the
energy function — which sounds like a detail and is the entire difference
between "this sometimes settles" and "this provably settles"
([§7](#7-two-schedules-one-energy)). The lesson is not that Little was robbed;
it is that **the guarantee was the contribution**, and guarantees are what
survive.

**The physics was borrowed wholesale.** By 1982 the theory of spin glasses —
disordered magnets with competing interactions — was a mature field, and
Hopfield's model is a spin glass with a particular choice of couplings.
Importing it meant that within three years Amit, Gutfreund and Sompolinsky
could compute the capacity exactly using replica theory built for a completely
different problem. Recognising that your problem is somebody else's solved
problem is worth more than most original work.

**Forty-two years to a Nobel Prize.** The field was declared dead at least
twice in between.

---

## 3. Before you calculate

The rule from the book: **write a number down before you read the next
section.** The learning is in the gap between your number and the real one,
and the gap does not exist if you did not commit.

> 1. The entry stores $24\times24$ glyphs, so $N = 576$ units. **How many
>    patterns fit before recall breaks?** Ten? Five hundred? Half a million?
> 2. You want to store one-megapixel images this way, so $N = 10^{6}$.
>    **How much RAM does $W$ take, and how many images fit in it?** Compare
>    that with just saving the images in a folder.
> 3. The $N = 576$ network has $2^{576}$ states and you stored four patterns.
>    Every run ends somewhere. **How many *other* states is it able to stop
>    on?** None? A handful? More than the memories?

Answers in [§8](#8-scale-analysis-reading-the-answer-off-the-crosstalk) and
[§10](#10-what-the-simulation-showed). All three are arithmetic on one
formula. The third one is the question most people have never thought to ask,
and it is the one that decides whether you can trust an answer the network
gives you.

---

## 4. Why the naive answer fails

There are three naive answers here, and they fail in increasingly interesting
ways. The third one fails so subtly that it is still quoted as correct.

### 4.1 "Just keep a list and compare against it"

Store the patterns in an array; on a query, compute the distance to each and
return the closest. This works. It is also not a model of anything, and it
fails all three properties from [§1](#1-the-phenomenon) in one go: recall cost
grows linearly in $P$, there is a distinguished place where each memory lives
(so damage is catastrophic rather than graceful), and nothing emerges — you
implemented the answer directly.

Worth stating explicitly because it is the baseline the model has to *beat on
a different axis than accuracy*. Nearest-neighbour search is strictly more
accurate than a Hopfield network. The interesting claim is that a system with
no search, no index and no central controller can approximate it at all.

### 4.2 "Superpose the patterns and hope"

The real first idea, and it is nearly right. Write every pattern into the same
couplings by adding them up:

$$W = \frac{1}{N}\sum_{\mu=1}^{P} p^{\mu}\left(p^{\mu}\right)^{\mathsf T}$$

Now probe with a stored pattern $p^{\nu}$ and look at the field pulling on
unit $i$ ([§6.3](#63-hebb-is-forced-not-chosen) does this properly):

$$h_i \thinspace p^{\nu}_i = \underbrace{1 - \frac{1}{N}}_{\text{signal}}
\thinspace + \underbrace{\frac{1}{N}\sum_{\mu\neq\nu}\thinspace p^{\mu}_i\thinspace p^{\nu}_i
\sum_{j\neq i} p^{\mu}_j p^{\nu}_j}_{\text{crosstalk}}$$

The signal is what you wanted. The crosstalk is every *other* memory leaking
into this one, and it does not vanish — it is a sum of $\sim PN$ random signs,
so it is small but not zero, and it grows with $P$.

**The memories interfere with each other, and interference is the whole
subject.** Everything from here on is an accounting of that second term.

### 4.3 "So compute when the crosstalk beats the signal" — and this is the subtle one

The crosstalk has mean zero and, treating the signs as independent, standard
deviation $\sqrt{(P-1)/N} \simeq \sqrt{\alpha}$ where $\alpha \equiv P/N$.
Verified directly:

| $N$ | $P$ | measured s.d. | $\sqrt{(P-1)/N}$ |
|---|---|---|---|
| 400 | 20 | 0.2106 | 0.2179 |
| 1000 | 50 | 0.2250 | 0.2214 |
| 2000 | 200 | 0.3295 | 0.3154 |

A unit is dragged the wrong way when the crosstalk is more negative than $-1$,
which for a Gaussian happens with probability

$$P_{\text{err}} = Q\negthinspace\left(\frac{1}{\sqrt{\alpha}}\right),
\qquad Q(x) = \tfrac12\thinspace\mathrm{erfc}\negthinspace\left(x/\sqrt2\right)$$

Demand $P_{\text{err}} \lt 0.01$ and you get $\alpha \lt 0.185$. Clean
argument, honest statistics, and **the answer is wrong.** The real ceiling is
$\alpha_c = 0.138$.

Here is why, measured at $N = 1000$, averaged over 12 pattern sets, probing
with a stored pattern and letting it relax:

| $\alpha$ | one-step error | $Q(1/\sqrt{\alpha})$ | error after relaxing |
|---|---|---|---|
| 0.05 | 0.0000 | 0.0000 | 0.0000 |
| 0.10 | 0.0009 | 0.0008 | 0.0014 |
| 0.138 | 0.0034 | 0.0036 | 0.0095 |
| 0.16 | 0.0049 | 0.0062 | **0.1064** |
| 0.20 | 0.0121 | 0.0127 | **0.2707** |
| 0.25 | 0.0212 | 0.0228 | 0.3334 |

![Recall error against load. The hollow circles, measured after a single
update, sit on the analytic curve across three decades. The filled curve,
measured after letting the network relax, peels away from it just past the
critical load.](figures/avalanche.png)

**What to conclude:** the napkin is not approximately right; it is **exactly
right about the wrong quantity.** Column two matches column three to the third
decimal at every load, and then column four leaves both of them behind by a
factor of twenty.

The missing physics is an **avalanche**. The estimate computes the probability
that a unit flips *given the other units are all correct*. But once a few units
have flipped, they are wrong, and a wrong unit contributes to everyone else's
crosstalk with the wrong sign. Above a critical load the feedback is
self-sustaining and the state slides away from the memory entirely. Below it,
the errors are corrected on the next pass.

That is a **phase transition**, it needs self-consistency rather than a single
pass to find, and locating it exactly is what Amit, Gutfreund and Sompolinsky
did in 1985 with replica theory. The gap between 0.185 and 0.138 is the price
of ignoring feedback.

> The general lesson, and it is not about neural networks: a first-order
> estimate that assumes everything else stays put will be right about the
> first step and can be arbitrarily wrong about the fixed point. Whenever the
> quantity you perturb feeds back into the perturbation, expect a transition
> the napkin cannot see.

---

## 5. The minimal model

Every assumption below buys a specific simplification, and every one of them
fails somewhere real. Listing them is not ceremony — the list *is* the domain
of validity, and it is the thing the tests can never tell you.

| Assumption | What it buys | Where it breaks |
|---|---|---|
| States are bipolar, $s\in\lbrace -1,+1\rbrace^{N}$ | A finite state space, so descent must terminate | Graded neurons, rate codes, continuous relaxations |
| Couplings are **symmetric**, $W_{ij}=W_{ji}$ | An energy exists at all | Real synapses are directed — no energy, no guarantee |
| **Zero diagonal**, $W_{ii}=0$ | Each update is a move on the true energy | Self-coupling turns a unit into a latch |
| Energy is **quadratic** in $s$ | Pairwise couplings; $N^2$ parameters | Higher-order terms give far more capacity |
| No external field, $b_i = 0$ | Global sign symmetry, $E(-s)=E(s)$ | Biased patterns need a threshold |
| Updates are **deterministic** | $T=0$: only downhill moves | Finite temperature, Boltzmann machines |
| One unit at a time | The Lyapunov argument | Parallel updates — a different theorem |
| Patterns are **uncorrelated** | Crosstalk is zero-mean noise | Real data is correlated, and recall degrades early |
| Hebbian storage | One pass, no iteration, local rule | Pseudo-inverse and Storkey store far more |
| $W$ stored densely | Simplicity | $N^2$ floats is the real ceiling |

That is the model. Notice what it does **not** assume: it does not assume the
patterns are orthogonal, or that $P$ is small, or that the probe is close to a
memory. All of those turn out to matter enormously, and the model tells you so
by producing wrong answers rather than by refusing.

Two rows are load-bearing in a way the others are not. **Symmetry** and **zero
diagonal** are the two premises of the descent theorem, and
[§6.4](#64-the-descent-theorem-and-where-each-premise-enters) breaks each one
on purpose to show what it was holding up.

---

## 6. The equations

### 6.1 Turning "recall" into "descend"

The problem as stated in [§1](#1-the-phenomenon) is not yet mathematics. There
is one move that makes it mathematics, and it is the only genuinely creative
step in the whole subject:

> **Stop asking how to retrieve a pattern. Ask what landscape would make the
> patterns the places a ball rolls to.**

If such a landscape exists, retrieval is not an algorithm you design — it is
what happens when you let go. The probe is a starting position, the memory is
the bottom of a valley, and the basin of attraction is exactly the set of
probes that work. All three properties from §1 come for free: no key (a
position is not a key), graceful degradation (the basin has width), no search
(you go downhill, you do not look around).

This is the same reframing the book makes about optimisation generally — that
an enormous number of apparently unrelated problems are one problem wearing
different clothes, and that recognising the shape is worth more than any
technique. Fermat's principle, a crystal forming, a fitted model, a delivery
route and this network are all the same sentence: *something is being
minimised.*

### 6.2 Why the energy is quadratic

We need a function $E:\lbrace -1,+1\rbrace^{N}\to\mathbb{R}$. Take the
constraints in order.

**It must be built from interactions between units**, because the whole point
is that the memory lives in the couplings and not in the units. A term
depending on $s_i$ alone is a bias, and it stores nothing about any pattern.

**It must be invariant under a global sign flip**, $E(-s) = E(s)$. The labels
$+1$ and $-1$ are a convention; nothing physical distinguishes them. This kills
every odd-order term.

**It should be the lowest order that works.** The lowest even order above a
constant is two.

Those three give, uniquely up to scale,

$$\boxed{\enspace E(s) = -\frac{1}{2}\sum_{i,j} W_{ij}\thinspace s_i s_j
= -\frac{1}{2}\thinspace s^{\mathsf T} W s\enspace}$$

with $W$ symmetric (the antisymmetric part of any $W$ contributes nothing to
the quadratic form — it cancels identically, which is the first hint that
symmetry is not optional but automatic *in the energy*, and therefore that an
asymmetric network is following something the energy cannot see). This is
[`model.energy()`](../model.py).

The factor $-\tfrac12$ is bookkeeping: the minus makes agreement between
positively-coupled units *lower* the energy, and the half compensates for
counting each pair twice.

**And the "lowest order that works" is a choice, not a law.** Take the energy
to order $k$ instead and the capacity rises from $N$ to $N^{k-1}$. That is
exactly what dense associative memories do (Krotov & Hopfield 2016), and it is
the single most productive place to attack this model.

### 6.3 Hebb is forced, not chosen

Most treatments state the Hebbian rule and then verify it works. Run it the
other way: **demand that the patterns be fixed points and see what $W$ is left
to be.**

We want a rule that (i) is *local* — $W_{ij}$ may depend only on what units
$i$ and $j$ do in the patterns, because there is no central authority to
compute anything else; (ii) is *symmetric*, so an energy exists; (iii) respects
the same sign symmetry as the energy, $W(p) = W(-p)$; and (iv) is *additive*
over patterns, one pass with no revisiting.

Any function of two bipolar variables can be written
$f(a,b) = c_0 + c_1 a + c_2 b + c_3\thinspace ab$, since $a^2 = b^2 = 1$
kills everything else. Locality allows all four terms. Symmetry in $i
\leftrightarrow j$ forces $c_1 = c_2$. Invariance under $p \to -p$ kills $c_1$
and $c_2$ entirely. The constant $c_0$ shifts every coupling equally and
stores nothing. **One term survives.**

$$W_{ij} = \frac{1}{N}\sum_{\mu} p^{\mu}_i p^{\mu}_j \quad (i \neq j),
\qquad W_{ii} = 0$$

which is [`model.hebbian_weights()`](../model.py) and, read aloud, is Hebb's
1949 sentence: units that agree across the stored patterns end up positively
coupled. There was never a choice to make.

**Does it work?** Probe with $p^{\nu}$ and compute the field:

$$\left(Wp^{\nu}\right)_i = \frac{1}{N}\sum_{j\neq i}\sum_{\mu}
p^{\mu}_i p^{\mu}_j p^{\nu}_j = \frac{N-1}{N}\thinspace p^{\nu}_i
\thinspace + \thinspace \frac{1}{N}\sum_{\mu\neq\nu} p^{\mu}_i
\sum_{j\neq i} p^{\mu}_j p^{\nu}_j$$

so $h_i\thinspace p^{\nu}_i = 1 - 1/N + \text{crosstalk}$, and the pattern is a
fixed point exactly when the crosstalk never reaches $-1$ at any unit. At
$N=400$, $P=3$ the measured mean of $h_i p_i$ is $0.9938$ against
$1 - 1/N = 0.9975$, with a minimum of $0.9425$ — comfortably positive
everywhere, so the pattern does not move. Push $P$ up and eventually some unit
loses; that is [§8](#8-scale-analysis-reading-the-answer-off-the-crosstalk).

The scale $1/N$ does nothing to the dynamics — $\mathrm{sign}$ ignores a
positive multiplier — but it makes energies comparable between networks of
different sizes, which is the only reason the capacity experiment produces a
readable plot. The 2024 version of this code divided by $P$ instead, which is
harmless for recall and quietly ruins any comparison.

### 6.4 The descent theorem, and where each premise enters

Now the payoff. Update unit $k$ and nothing else. Split the energy into the
terms that involve $k$ and the terms that do not, using $W$ symmetric:

$$E(s) = -\frac{1}{2}\sum_{i,j\neq k} W_{ij}s_i s_j
\thinspace-\thinspace s_k \sum_{j\neq k} W_{kj}s_j
\thinspace-\thinspace \frac{1}{2}W_{kk}\thinspace s_k^2$$

The first group does not change. The third does not change either, because
$s_k^2 = 1$ whichever value $s_k$ takes. So, writing
$g_k \equiv \sum_{j\neq k} W_{kj}s_j$ for the field from *everyone else*,

$$\boxed{\enspace \Delta E = -\thinspace\Delta s_k \thinspace g_k\enspace}$$

Verified to $7\times10^{-15}$ over 500 single-unit flips. Now the two premises,
and what each is holding up:

**Zero diagonal.** The update rule uses the *full* field
$h_k = \sum_j W_{kj}s_j = g_k + W_{kk}s_k$, while the energy only responds to
$g_k$. When $W_{kk}=0$ the two coincide, the unit aligns with the very quantity
whose sign decides $\Delta E$, and descent follows. When $W_{kk}\neq 0$ they
part company and the guarantee evaporates. It is not a rounding concern:

- $W_{kk} \gt 0$ biases the unit towards whatever it already is. It stops
  taking downhill moves and freezes. That is a latch, not a memory.
- $W_{kk} \lt 0$ biases it *against* itself. Measured with $W_{kk} = -2$ on a
  random symmetric $W$: asynchronous updates raise the energy and keep raising
  it, exactly as $\Delta E = -\Delta s_k g_k$ predicts once $\mathrm{sign}(h_k)
  \neq \mathrm{sign}(g_k)$.

**Symmetry.** Drop it and the derivation above fails at the first line: the two
cross terms no longer combine. The dynamics follows $W$, the energy only ever
sees $(W + W^{\mathsf T})/2$, and there is no reason for the system to
minimise a function it is not looking at. Measured on random asymmetric $W$ at
$N=8$ with a fixed update order: **asynchronous limit cycles of period 2 and
period 3** — states that recur forever. With symmetric $W$ that is impossible,
which is the next paragraph.

**Termination.** Note that a flip only happens when $g_k \neq 0$ strictly,
because [`update_rule`](../model.py) holds the current value on a tie. So
every flip that actually occurs has

$$\Delta E = -\thinspace\Delta s_k\thinspace g_k = -2\thinspace|g_k| \lt 0$$

**strictly.** The energy therefore never repeats a value, so the state never
repeats, and the state space is finite. A finite set with no repeats is a
finite walk: the dynamics reaches a fixed point in a bounded number of steps
and stays. Not "usually converges" — cannot do anything else.

That is worth reading twice, because it means the tie convention is not
defensive tidiness. It is what turns $\Delta E \le 0$ into $\Delta E \lt 0$,
and a non-strict inequality proves nothing about termination.

### 6.5 The tie, and an exact parity law

`np.sign(0)` returns $0$, which is not in $\lbrace -1,+1\rbrace$ — a unit
updated that way falls off the hypercube and the state stops being a state.
[`model.update_rule()`](../model.py) holds the current value instead. The
docstring says ties "are not as rare as they look at small $N$". That is a
testable claim, so it should be tested, and the answer is sharper than
expected.

The field is $N h_i = \sum_{j\neq i} C_{ij}s_j$ with
$C_{ij} = \sum_{\mu}p^{\mu}_i p^{\mu}_j$ an integer, so a tie is an exact
integer identity and floating point has nothing to do with it. Write
$q_j = (p^1_j,\dots,p^P_j)$; then

$$N h_i = q_i \cdot v, \qquad v_{\mu} = \sum_{j\neq i} p^{\mu}_j s_j$$

Each $v_{\mu}$ is a sum of $N-1$ terms of $\pm1$, so it has the parity of
$N-1$. The dot product is a signed sum of $P$ such numbers, so $Nh_i$ has the
parity of $P(N-1)$. **A tie requires $Nh_i = 0$, which requires that parity to
be even.** Hence:

$$\boxed{\enspace P(N-1)\ \text{odd}\ \Longrightarrow\ \text{an exact tie is
impossible}\enspace}$$

Predicted first, then measured over 60 pattern sets $\times$ 30 states each:

| $N$ | $P$ | $P(N-1)$ | predicted | measured tie rate |
|---|---|---|---|---|
| 20 | 3 | odd | impossible | 0.0000% |
| 20 | 4 | even | possible | 11.12% |
| 21 | 3 | even | possible | 10.60% |
| 100 | 3 | odd | impossible | 0.0000% |
| 101 | 3 | even | possible | 4.72% |
| 576 | 5 | odd | impossible | 0.0000% |
| 577 | 3 | even | possible | 1.87% |
| 577 | 5 | even | possible | 1.52% |

![Fraction of local fields that are exactly zero, against network size, in
exact integer arithmetic. One series sits at a few percent and decays slowly;
the other is flat at exactly zero at every size; a third shows what float64
reports for the first.](figures/parity.png)

**What to conclude:** this is not a rate that happens to be small. It is
either a few percent or exactly zero, and an integer parity decides which —
there is nothing in between, at any size.

Ten predictions, ten hits, and the rate decays roughly as $1/\sqrt{N}$ in the
even case rather than vanishing. **This entry's own headline experiment sits on
the wrong side of it**: $N = 576$ glyphs with $P = 4$ gives $P(N-1) = 2300$,
even, and 3.5% of unit fields on random states are exact ties. The convention
is load-bearing in the code as shipped, not in a hypothetical.

One numerical sting in the tail. Those are the *true* ties, computed in exact
integer arithmetic. Ask `float64` how many it sees:

| $N$ | true ties | reported as `h == 0` | missed |
|---|---|---|---|
| 20 | 11.67% | 4.53% | 61% |
| 60 | 3.99% | 0.08% | 98% |
| 200 | 3.41% | 0.10% | 97% |
| 576 | 1.58% | 0.23% | 86% |

A mathematically exact zero, accumulated through hundreds of floating-point
additions, arrives as $10^{-17}$ and the unit silently takes a direction
chosen by rounding. Nothing raises, nothing warns, and every test still
passed. The dynamics is not wrong — a hair either side of zero is a legitimate
tie-break — but **the code's own guard is only catching a seventh of the cases
it was written for**, and no amount of re-reading the source would have found
that. It took integer arithmetic to see it.

Both halves are now in [`test_model.py`](../tests/test_model.py): the parity
law as six cases that must and must not tie, and the float64 shortfall as a
test that documents the gap rather than pretending it is closed.

---

## 7. Two schedules, one energy

In [`tmm/`](../../tmm/README.md), the sibling entry, the two solvers agree to
$10^{-13}$ and any disagreement would be a bug. Here the two methods disagree
on purpose, and the disagreement is a theorem.

### 7.1 Asynchronous: the Lyapunov argument holds

One unit at a time, in random order.
[`methods/asynchronous.py`](../methods/asynchronous.py) is four lines because
§6.4 already did the work: every flip strictly lowers $E$, the state space is
finite, so the run **reaches a fixed point and cannot cycle**. Ever. For any
symmetric $W$ with zero diagonal, from any starting state, under any update
order.

The price is that the trajectory depends on the order, so which memory you land
on when the probe is ambiguous is a function of the random seed. The run is
seeded for that reason.

### 7.2 Synchronous: a different theorem, not the absence of one

Update every unit at once from the same field.
[`methods/synchronous.py`](../methods/synchronous.py) is one matrix-vector
product per sweep and much faster. The §6.4 derivation collapses immediately:
it assumed *everything else stayed put*, and now nothing does. The energy is
free to rise, and it does.

But "no guarantee" is the lazy reading, and it is wrong. There is still a
Lyapunov function — it just lives on **pairs of consecutive states**:

$$F\left(s(t), s(t{+}1)\right) = -\thinspace s(t)^{\mathsf T} W\thinspace s(t{+}1)$$

To see that it never increases, use $s(t{+}1) = \mathrm{sign}(Ws(t))$ and
symmetry:

$$\Delta F = -\thinspace s(t{+}1)^{\mathsf T}W\left[s(t{+}2) - s(t)\right]
= -\sum_i \left(\thinspace|h_i| - h_i\thinspace s_i(t)\thinspace\right) \le 0$$

with $h = W s(t{+}1)$, because $h_i s_i(t{+}2) = |h_i|$ by construction and
$|h_i| \ge h_i s_i(t)$ always. The same finiteness argument then applies to
$F$, and equality forces $s(t{+}2) = s(t)$.

**Therefore the synchronous dynamics converges to a cycle of period 1 or 2 and
nothing else.** No period 3, no chaos, no drift. That is the theorem of
Goles-Chacc, Fogelman-Soulié and Pellegrin (1985), and it is a much stronger
statement than "sometimes oscillates".

Both halves verified. Over 600 runs at four different $(N,P)$:

```
max increase of F across every step:  2.8e-14      (must be <= 0)
period histogram over 600 runs:       {1: 442, 2: 158}
```

Nothing but 1 and 2, and $F$ never rose above numerical noise. Both are
asserted in [`test_methods_differ.py`](../tests/test_methods_differ.py),
alongside a third test that catches $E$ rising and $F$ not rising on the same
trajectory — two accountants, one run.

### 7.3 What the contract suite may and may not demand

This is the architectural point of the entry, and it is the mirror image of
`tmm/`'s.

[`tests/test_methods.py`](../tests/test_methods.py) is parametrised over every
registered method and asserts what all of them must do: stay bipolar, leave a
stored pattern alone, recall from noise, terminate. It deliberately does
**not** assert energy descent. Adding that line would look like thoroughness
and would be asserting something false about half the methods.

The differences live in
[`tests/test_methods_differ.py`](../tests/test_methods_differ.py), stated as
positive claims about each schedule rather than as exemptions:
asynchronous never increases $E$ and always reaches a fixed point; synchronous
can increase $E$ and does fall into 2-cycles.

> A shared contract is only worth having if it is the intersection of what the
> implementations actually guarantee. The moment it contains a clause that one
> implementation cannot satisfy, either the test is wrong or the method does
> not belong — and it is worth knowing which before you write the code that
> depends on it.

---

## 8. Scale analysis: reading the answer off the crosstalk

Almost everything about this model is a statement about one ratio:

$$\alpha \equiv \frac{P}{N}$$

Not $P$. Not $N$. The **load**. A network of a million units is not better at
remembering than one of a hundred — it is better at remembering *proportionally
more things*, and no better at all at remembering each one.

### 8.1 Signal against noise

From [§6.3](#63-hebb-is-forced-not-chosen), the stability of unit $i$ in
pattern $\nu$ is decided by

$$h_i\thinspace p^{\nu}_i = \underbrace{1 - 1/N}_{\text{signal, size } 1}
\thinspace + \thinspace \underbrace{C_i}_{\text{noise, s.d. } \sqrt{\alpha}}$$

The signal does not grow with $N$. The noise does not shrink with $N$. Only
their ratio matters, and that ratio is $1/\sqrt{\alpha}$. Every capacity
statement below is a different threshold on that one number.

### 8.2 A first threshold: one bit wrong

$P_{\text{err}} = Q(1/\sqrt{\alpha})$, verified to the third decimal in
[§4.3](#43-so-compute-when-the-crosstalk-beats-the-signal--and-this-is-the-subtle-one).
Ask for at most one wrong bit in a recalled pattern of $N$ units:

$$N\thinspace Q\negthinspace\left(\frac{1}{\sqrt{\alpha}}\right) \lt 1$$

*Answer to question 1, first version.* At $N = 576$ that needs
$Q \lt 1/576$, so $1/\sqrt{\alpha} \gt 2.92$, so $\alpha \lt 0.117$:
**67 patterns.**

### 8.3 The real threshold: the avalanche

The estimate above assumes the other $N-1$ units are correct. They are not, and
their errors feed back. The self-consistent treatment gives a genuine phase
transition at

$$\boxed{\enspace\alpha_c = 0.138\enspace}$$

*Answer to question 1, second version:* $0.138 \times 576 =$ **79 patterns.**
Not five hundred, not half a million. A network of 576 units and 331 776
couplings holds seventy-nine 576-bit patterns.

The transition is sharp and it sharpens with $N$, which is what a phase
transition does and what the entry's capacity experiment measures directly. The
sign of it in the measured data is the jump in the last column of
[§4.3](#43-so-compute-when-the-crosstalk-beats-the-signal--and-this-is-the-subtle-one):
error $0.0095$ at $\alpha = 0.138$ and $0.1064$ at $\alpha = 0.16$. Eleven
times worse for a 16% increase in load.

### 8.4 A third threshold: *every* pattern, exactly

Demand that all $P$ patterns are recalled with no errors at all, with
probability approaching 1. The requirement now scales with $P$ as well as $N$,
and the answer is not a constant $\alpha$ at all:

$$P_{\max} \simeq \frac{N}{4\ln N}$$

*Answer to question 1, third version:* $576/(4\ln 576) =$ **23 patterns.**

Three defensible criteria, three answers — 23, 67, 79 — spanning a factor of
3.4. **"Capacity" is not a property of the network; it is a property of the
question.** Anyone quoting one number without saying which failure they are
tolerating is quoting a number they have not thought about.

### 8.5 Basins shrink long before capacity does

Capacity asks whether a memory is *stable*. Usefulness asks how far away you
can start and still get there. Measured: fraction of successful exact recalls,
$N = 500$, 20 trials per cell, against the fraction of bits corrupted in the
probe.

| $\alpha$ | 5% | 10% | 20% | 30% | 40% | 45% | 50% |
|---|---|---|---|---|---|---|---|
| 0.02 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.50 | 0.00 |
| 0.05 | 1.00 | 1.00 | 1.00 | 1.00 | 0.75 | 0.05 | 0.00 |
| 0.10 | 0.75 | 0.75 | 0.70 | 0.50 | 0.00 | 0.00 | 0.00 |
| 0.138 | 0.30 | 0.30 | 0.25 | 0.00 | 0.00 | 0.00 | 0.00 |

![Fraction of probes recalled exactly, against how corrupted the probe was,
for four loads. At the lowest load the curve is flat to 40% corruption; at the
critical load it starts below a third and is dead by 30%.](figures/basins.png)

**What to conclude:** capacity and usefulness are different questions. Three
things fall out of that table.

**The 50% column is zero everywhere, and must be.** A probe with half its bits
flipped has overlap zero with the target: it contains no information about
which memory you meant. That column is not a failure of the model, it is the
model reporting that the question was empty.

**At low load the basins are enormous** — 40% corruption still recovers
perfectly at $\alpha = 0.02$. That is the property that makes this interesting
at all.

**At $\alpha_c$ the basins have already collapsed.** At the "critical" load the
network recalls a 5%-corrupted probe 30% of the time. The memories are
technically still stable — that is what $\alpha_c$ measures — and they are
useless, because nothing can reach them. **Capacity is an upper bound on a
quantity nobody wants.** The load you can actually work at is several times
smaller, and that gap is invisible unless you measure basins rather than
stability.

### 8.6 The cost of a coupling

Stored information is $P \times N$ bits. Couplings are $N^2$ numbers. At
capacity:

$$\frac{P N}{N^2} = \alpha_c = 0.138\ \text{bits per coupling}$$

*Answer to question 2.* At $N = 10^6$, $W$ has $10^{12}$ entries: **8 TB in
float64**, holding 138 000 images that occupy 17 GB as raw bits. You spend
**464 bits of RAM per bit stored**, and the ratio is $64/\alpha_c$ — it does
not improve with size, ever, because both scale as $N^2$.

So: never as a storage technology. Always as a model of how content-addressing
could work without a controller.

And the 0.138 is not the architecture's fault. Gardner (1988) computed the
maximum over *all* symmetric couplings, not just Hebbian ones, and got
$\alpha_{\max} = 2$ — **2 bits per coupling, a factor of 14 more.** The
information is in the couplings; the one-pass local learning rule simply
cannot reach it. Pseudo-inverse storage gets $\alpha = 1$ at the cost of a
matrix inversion, and Storkey's rule improves on Hebb while staying local and
incremental.

> $\alpha_c = 0.138$ is a fact about **Hebb**, not about Hopfield networks.
> That distinction is worth holding on to, because "the model tops out here"
> and "this particular one-pass rule tops out here" lead to completely
> different next moves.

---

## 9. Closed forms worth memorising

These are what you check code against. Cross-checking two methods proves they
agree; checking against a closed form proves they are *right*. Every row here
is a test in [`../tests/`](../tests/).

| Situation | Result |
|---|---|
| Energy | $E = -\tfrac12\thinspace s^{\mathsf T}Ws$ |
| Hebbian couplings | $W = \tfrac1N\sum_{\mu}p^{\mu}(p^{\mu})^{\mathsf T}$, $W_{ii}=0$ |
| Single-unit flip | $\Delta E = -\thinspace\Delta s_k\thinspace g_k$, $g_k = \sum_{j\neq k}W_{kj}s_j$ |
| An actual flip | $\Delta E = -2\thinspace|g_k| \lt 0$, strictly |
| Field on a stored pattern | $h_i p^{\nu}_i = 1 - 1/N + \text{crosstalk}$ |
| Crosstalk s.d. | $\sqrt{(P-1)/N} \simeq \sqrt{\alpha}$ |
| One-step error rate | $Q\left(1/\sqrt{\alpha}\right)$ |
| Energy of a stored pattern (random $p$) | $E \simeq -(N-1)/2$, so $E/N \simeq -0.5$ |
| Energy of a random state | mean $0$, s.d. $\simeq\sqrt{P/2}$ |
| Sign symmetry | $E(-s) = E(s)$; every memory has a mirror |
| Three-pattern mixture | $\mathrm{sign}(p^1+p^2+p^3)$ is a fixed point nobody stored |
| Capacity, stable memories | $\alpha_c = 0.138$ |
| Capacity, all patterns exact | $P_{\max}\simeq N/(4\ln N)$ |
| Capacity, optimal couplings | $\alpha_{\max} = 2$ (Gardner) |
| Information density | $\alpha$ bits per coupling |
| Synchronous dynamics | period 1 or 2, never more |
| Synchronous Lyapunov function | $F = -\thinspace s(t)^{\mathsf T}Ws(t{+}1)$, non-increasing |
| Exact ties | impossible iff $P(N-1)$ is odd |

**A warning about row eight.** "Stored patterns sit lower than random states"
is the test everybody writes first and it is nearly worthless. It passes at
$\alpha = 0.5$, far past capacity, where recall is destroyed — the memories are
*still* in local minima, they simply have exponentially many neighbours that
are too. An energy comparison constrains your bookkeeping, not your recall.
The rows about error rates and basins outrank it, and cross-method agreement
ranks below both.

---

## 10. What the simulation showed

The book's rule: **predict before you run.** Every experiment in the entry is
built as a prediction with a number attached, not as a plot to admire. The
third one produced the opposite of what it predicted, which is why it is the
most useful. The figures throughout this document come from
[`landscape.py`](../experiments/landscape.py), which exists because writing
the derivation needed numbers nothing in the entry measured yet.

### 10.1 Recall — [`recall.py`](../experiments/recall.py)

Prediction: stored patterns sit near $E/N = -0.5$, random states near $0$, and
a 25%-corrupted probe returns the memory exactly.

```
N = 576 units, P = 4 patterns, load = 0.0069

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

Every pattern returns exactly, in two sweeps, from a probe with a quarter of
its bits wrong. Random states sit at $E/N = -0.0003$ against the memories'
$-0.55$: the memories really are the valleys, and everything else really is
the plain.

**But the napkin says $-0.4991$ and the glyphs are at $-0.52$ to $-0.56$.**
The wells are *deeper* than theory predicts, and the reason is that the glyphs
are correlated — pairwise overlaps run from $-0.29$ to $+0.17$ rather than the
$\pm 1/\sqrt{N} \approx 0.04$ of random patterns. Correlated patterns
reinforce each other's couplings and dig deeper holes.

Deeper holes, and worse recall. That is not a contradiction and it is the
subject of §10.3. Checked against uncorrelated patterns, where the napkin is
exact:

| $N$ | $P$ | measured $E/N$ | $-(N-1)/2N$ |
|---|---|---|---|
| 400 | 3 | $-0.4968$ | $-0.4988$ |
| 400 | 20 | $-0.4956$ | $-0.4988$ |
| 1000 | 50 | $-0.4997$ | $-0.4995$ |

### 10.2 Capacity — [`capacity.py`](../experiments/capacity.py)

Prediction: the error against load has a knee at $\alpha_c = 0.138$, and the
transition sharpens with $N$.

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

The knee sits where theory puts it. And the sharpening is visible in the right
direction, which is the counter-intuitive part: **past the transition the
larger networks are worse.** At $\alpha = 0.16$ the error roughly triples from
$N=100$ to $N=500$. A bigger network is not a safer one — it is a network with
a crisper edge, better below the threshold and worse above it. That is exactly
what happens to a magnet as you take the thermodynamic limit, and it is the
clearest evidence in the entry that this really is a phase transition rather
than a gradual degradation.

### 10.3 Spurious states — [`associative_and_spurious.py`](../experiments/associative_and_spurious.py)

Prediction: a probe resembling a stored pattern recovers it, and
$\mathrm{sign}(p^1+p^2+p^3)$ is a stable state nobody stored.

Both predictions failed, and the failures are the most instructive output in
the entry.

```
ring variant (never stored)
  overlap: cross=+0.451  ring=+0.715  diagonals=-0.076  bars=-0.465
  closest: ring (+0.715)   sweeps: 2   E: -268.06
  landed on a stored memory: NO — spurious

checkerboard (unrelated)
  closest: ring (-1.000)   sweeps: 2   E: -310.11
  landed on a stored memory: yes

sign(cross + ring + diagonals)
  closest: ring (+1.000)   sweeps: 3   E: -310.11
  landed on a stored memory: yes
```

**The near-miss does not recover the memory.** A ring that is shifted and
differently proportioned stops at overlap $+0.715$ — recognisably ring-like,
not the ring — in a valley at $E = -268.06$ against the stored ring's
$-310.11$. A shallower minimum, sitting between the probe and the memory,
catching the ball on the way down. The network answered confidently and it
answered wrong, and nothing in the run indicates that: it converged, the energy
fell monotonically, the state is a genuine fixed point.

**The unrelated probe lands exactly on $-p$.** The checkerboard settles on the
mirror of the ring at identical energy, which is the sign symmetry from §6.2
showing up as behaviour rather than as a test assertion. Every memory you store
comes with an anti-memory you did not, at the same depth, and there is no
mechanism in the model that prefers one.

**The textbook mixture state is not stable here** — it flows to `ring`. That
one is correlation again, and the script checks the control in the same run:

```
random patterns: mixture is a fixed point -> True
overlaps with the three memories: +0.490  +0.472  +0.545
```

With uncorrelated patterns the mixture behaves exactly as theory says. The
glyphs share too much structure, and the landscape is reshaped enough that a
textbook result stops holding.

### 10.4 How many spurious states are there?

![Left: the probe, the state it settles on, and the stored ring it never
reaches, with their energies. Right: fixed points found by exhaustive
enumeration at N = 16, split into stored memories with their mirrors and
states nobody stored.](figures/spurious.png)

**What to conclude:** the run converged, the energy fell monotonically, the
final state is a genuine fixed point — and the answer is wrong. Nothing in the
trajectory distinguishes this from a correct recall.

*Answer to question 3.* Enumerate all $2^N$ states for small $N$ and count
exactly which are fixed points, averaged over 5 pattern sets:

| $N$ | $P$ | $\alpha$ | memories + mirrors | total fixed points | spurious |
|---|---|---|---|---|---|
| 16 | 1 | 0.06 | 2.0 | 2.0 | 0.0 |
| 16 | 2 | 0.13 | 4.0 | 4.0 | 0.0 |
| 16 | 3 | 0.19 | 6.0 | 10.4 | 4.4 |
| 16 | 4 | 0.25 | 7.6 | 17.2 | 9.6 |
| 20 | 3 | 0.15 | 6.0 | 8.8 | 2.8 |
| 20 | 5 | 0.25 | 6.4 | 13.6 | 7.2 |

Read the last row carefully. Ten states were stored (five patterns and their
mirrors); **6.4 of them survived as fixed points** — past capacity, some
memories are no longer stable — and the network can stop on 13.6 states, more
than half of which nobody asked for. The known asymptotic result is worse than
this table suggests: the number of metastable states grows *exponentially* in
$N$ while the number of memories grows linearly.

So the answer to question 3 is: **far more places to stop than things you
stored, and the ratio gets worse with every pattern you add.** Which means a
converged answer is not evidence of a correct answer. If it matters, check the
overlap with a stored pattern; the network will not tell you on its own.

---

## 11. Where the model stops being true

The section that matters most, and the one that is usually missing.

### 11.1 Correlation — the assumption that fails first

Every capacity number in this document assumes the patterns are independent
random signs. Nothing you would want to store is.

Photographs are mostly sky or mostly background. Text is mostly common
characters. Sensor readings are mostly the normal state. All of them have
overlaps far larger than the $\pm1/\sqrt{N}$ of random vectors, and the
crosstalk analysis of [§8.1](#81-signal-against-noise) is built on that
$\sqrt{\alpha}$ scaling. When patterns are correlated the crosstalk stops being
zero-mean noise and becomes a systematic pull.

Two consequences, both visible in this entry:

- **Recall degrades far below $\alpha_c$.** The glyph experiment runs at
  $\alpha = 0.0069$ — twenty times below capacity — and still produces a
  spurious attractor on a near-miss probe.
- **The energies mislead.** Correlated patterns sit *deeper* than the
  uncorrelated formula predicts ($-0.55$ against $-0.50$), so the naive health
  check reads as *better than expected* on precisely the runs where recall is
  worst.

This is why the entry generates glyphs instead of using the original 2024
photographs. It is not a licensing convenience: photographs are strongly biased
towards one colour, that bias correlates every pattern with every other, and
the resulting failure has nothing to do with the model under test. Choosing
data that isolates the phenomenon is part of designing the experiment.

The fix is known — pseudo-inverse storage handles correlated patterns properly,
at the cost of no longer being local or one-pass — and is not implemented here.

### 11.2 The rest of the list

| Limit | What actually happens | This entry |
|---|---|---|
| Load above $\approx 0.138$ | Avalanche; recall error jumps 20× over the napkin | measured, not assumed |
| Load above $\approx 0.05$ | Basins collapse while memories stay "stable" | measured in §8.5 |
| Correlated patterns | Spurious attractors 20× below capacity | shown in §10.3 |
| Spurious states | Exponentially many; a converged answer proves nothing | counted in §10.4 |
| Mirror states $-p$ | Always present, same energy, no way to prefer $p$ | tested |
| $W$ symmetric | Required for an energy; asymmetric gives limit cycles | `ValueError` |
| $W_{ii} \neq 0$ | Latching, or energy that climbs | `ValueError` |
| Synchronous updates | Energy can rise; period-2 cycles | characterised, not forbidden |
| Exact ties | Real whenever $P(N-1)$ is even; float64 misses ~90% | law tested; the float gap documented, not fixed |
| Dense $W$ | $N^2$ floats — 8 TB at one megapixel | the real ceiling on size |
| Finite temperature | Only downhill moves; no escape from a bad basin | not modelled — $T = 0$ |
| Better storage rules | Pseudo-inverse $\alpha=1$, Gardner $\alpha=2$ | not implemented |
| Higher-order energies | Capacity $N^{k-1}$ instead of $0.138N$ | a separate entry |

Three of those rows exist because someone **probed** the edges rather than
reasoning about them: the avalanche gap, the basin collapse, and the parity law
with its floating-point blind spot. The suite was green in all three cases, and
in the third the code contained an explicit guard that was catching one case in
seven without anyone noticing.

> A test suite proves the cases you thought of. The limits of a model are
> found by attacking it, not by re-reading it.

---

## 12. The essentials

- **The creative step is reframing retrieval as descent.** Once memories are
  minima of a landscape, no-key, graceful-degradation and no-search all follow
  for free instead of being features you implement.
- **The energy is forced.** Interactions only, invariant under $s \to -s$,
  lowest order that works $\Rightarrow$ $E = -\tfrac12 s^{\mathsf T}Ws$.
- **Hebb is forced too.** Local, symmetric, sign-invariant, additive
  $\Rightarrow$ $W_{ij} \propto \sum_{\mu} p^{\mu}_i p^{\mu}_j$. It is a
  derivation, not a postulate.
- **$\Delta E = -\Delta s_k g_k$ is the whole theory**, and $g_k$ is the field
  from *everyone else*. Zero diagonal is what makes the unit align with $g_k$
  rather than with $g_k$ plus itself.
- **The tie convention closes the proof.** Holding on $g_k = 0$ makes every
  real flip strictly downhill, and strict is what forbids cycles on a finite
  state space.
- **Symmetry and zero diagonal are premises, not hygiene.** Break either and
  the measured dynamics cycles or climbs.
- **Synchronous updates have a theorem too**, on pairs of states — period 1 or
  2, never 3. "No guarantee" is the lazy reading.
- **The napkin is exactly right about the first step and wrong about the fixed
  point.** $Q(1/\sqrt{\alpha})$ matches to three decimals and misses the
  avalanche by 20×. Feedback makes phase transitions, and phase transitions are
  invisible to first-order estimates.
- **Capacity is a property of the question**: 23, 67 or 79 patterns at $N=576$
  depending on what failure you tolerate.
- **Basins collapse long before capacity does.** At $\alpha_c$ the memories are
  stable and unreachable. Measure basins, not stability.
- **$\alpha_c = 0.138$ indicts Hebb, not the architecture.** Optimal couplings
  reach $\alpha = 2$ — a factor of 14 left on the table by insisting the rule
  be local and one-pass.
- **Convergence is not correctness.** Spurious minima outnumber memories, they
  are reached confidently, and the energy falls monotonically all the way into
  the wrong one.

---

## 13. Open questions

Things this document deliberately does not answer, roughly in order of how much
they would teach:

- **What does finite temperature buy?** These dynamics are Metropolis at
  $T = 0$: only improving moves are accepted, so the first valley wins. Turn
  the temperature up and the same landscape becomes a Boltzmann machine, and
  the spurious minima of §10.3 become escapable. The book's argument that
  sampling and optimising are the same operation at two temperatures is exactly
  this model, and it is one parameter away.
- **How far do better storage rules actually get?** Pseudo-inverse reaches
  $\alpha = 1$ and Gardner's bound is 2. Implementing the projection rule and
  measuring where *its* basins collapse would separate "the couplings cannot
  hold more" from "Hebb cannot find it" experimentally rather than by citation.
- **What does the landscape look like between the minima?** Every statement
  here is about fixed points. Nothing in the entry measures barrier heights,
  basin shapes, or how the basins tile the hypercube — and basin geometry is
  what actually determines whether recall works.
- **Why does correlation deepen the wells and ruin the recall?** Both are
  measured in §10.1 and §10.3 and the mechanism connecting them is not derived
  anywhere in this document.
- **Where exactly does the higher-order energy buy its capacity?** Dense
  associative memories reach $N^{k-1}$, and the modern Hopfield layer reaches
  exponentially many patterns and turns out to be attention. That is a separate
  entry, and it starts by relaxing the single word "quadratic" in §6.2.

---

## 14. References

**Foundational**

- **Hopfield, J. J.** *Neural networks and physical systems with emergent
  collective computational abilities.* PNAS **79**, 2554–2558 (1982).
  [link](https://www.pnas.org/doi/10.1073/pnas.79.8.2554) — the paper.
- **Little, W. A.** *The existence of persistent states in the brain.*
  Mathematical Biosciences **19**, 101–120 (1974).
  [link](https://doi.org/10.1016/0025-5564(74)90031-5) — the synchronous model,
  eight years earlier.
- **Hebb, D. O.** *The Organization of Behavior* (1949). The learning rule, in
  words, thirty-three years before the network.
- **Hopfield, J. J.** *Neurons with graded response have collective
  computational properties like those of two-state neurons.* PNAS **81**,
  3088–3092 (1984). [link](https://www.pnas.org/doi/10.1073/pnas.81.10.3088)

**Capacity — the part that needed statistical mechanics**

- **Amit, D. J., Gutfreund, H. & Sompolinsky, H.** *Storing infinite numbers of
  patterns in a spin-glass model of neural networks.* Physical Review Letters
  **55**, 1530–1533 (1985).
  [link](https://doi.org/10.1103/PhysRevLett.55.1530) — where $0.138$ comes
  from.
- **Amit, D. J., Gutfreund, H. & Sompolinsky, H.** *Statistical mechanics of
  neural networks near saturation.* Annals of Physics **173**, 30–67 (1987).
- **McEliece, R. J., Posner, E. C., Rodemich, E. R. & Venkatesh, S. S.** *The
  capacity of the Hopfield associative memory.* IEEE Transactions on
  Information Theory **33**, 461–482 (1987).
  [link](https://doi.org/10.1109/TIT.1987.1057328) — $N/(4\ln N)$.
- **Gardner, E.** *The space of interactions in neural network models.*
  Journal of Physics A **21**, 257–270 (1988).
  [link](https://doi.org/10.1088/0305-4470/21/1/030) — $\alpha_{\max}=2$ for
  optimal couplings. The paper that separates the rule from the architecture.

**Dynamics**

- **Goles-Chacc, E., Fogelman-Soulié, F. & Pellegrin, D.** *Decreasing energy
  functions as a tool for studying threshold networks.* Discrete Applied
  Mathematics **12**, 261–277 (1985).
  [link](https://doi.org/10.1016/0166-218X(85)90029-0) — period 1 or 2 under
  parallel updates, and the pair Lyapunov function of §7.2.
- **Cohen, M. A. & Grossberg, S.** *Absolute stability of global pattern
  formation and parallel memory storage by competitive neural networks.* IEEE
  Transactions on Systems, Man and Cybernetics **13**, 815–826 (1983). The
  continuous-time Lyapunov result.

**Better storage rules**

- **Personnaz, L., Guyon, I. & Dreyfus, G.** *Information storage and retrieval
  in spin-glass like neural networks.* Journal de Physique Lettres **46**,
  359–365 (1985). The pseudo-inverse (projection) rule, $\alpha = 1$.
- **Storkey, A.** *Increasing the capacity of a Hopfield network without
  sacrificing functionality.* ICANN (1997). Local and incremental, and better
  than Hebb.

**Optimisation and the spin-glass connection**

- **Hopfield, J. J. & Tank, D. W.** *Neural computation of decisions in
  optimization problems.* Biological Cybernetics **52**, 141–152 (1985).
  [link](https://doi.org/10.1007/BF00339943)
- **Sherrington, D. & Kirkpatrick, S.** *Solvable model of a spin-glass.*
  Physical Review Letters **35**, 1792–1796 (1975). The physics that got
  imported.
- **Kirkpatrick, S., Gelatt, C. D. & Vecchi, M. P.** *Optimization by simulated
  annealing.* Science **220**, 671–680 (1983). The same landscape, with the
  temperature turned back on.

**Where it went next**

- **Krotov, D. & Hopfield, J. J.** *Dense associative memory for pattern
  recognition.* NeurIPS (2016). [link](https://arxiv.org/abs/1606.01164)
- **Ramsauer, H. et al.** *Hopfield Networks is All You Need.* arXiv:2008.02217
  (2020). [link](https://arxiv.org/abs/2008.02217) — the modern Hopfield layer
  is the attention mechanism.
- **Hinton, G. E. & Sejnowski, T. J.** *Optimal perceptual inference.* CVPR
  (1983). The Boltzmann machine: this model at $T \gt 0$.

**Books**

- **Hertz, J., Krogh, A. & Palmer, R. G.** *Introduction to the Theory of
  Neural Computation* (1991), ch. 2–3. The clearest derivation of everything in
  §6 and §8.
- **Amit, D. J.** *Modeling Brain Function: The World of Attractor Neural
  Networks* (1989). The statistical mechanics in full.
- **MacKay, D. J. C.** *Information Theory, Inference and Learning Algorithms*
  (2003), ch. 42. The information-theoretic reading of capacity, and the best
  short account of why it is what it is.

---

*Code: [`../model.py`](../model.py) and [`../methods/`](../methods/) ·
Entry: [`../README.md`](../README.md) · Repo-wide architecture:
[`docs/architecture.md`](../../docs/architecture.md)*
