# Looking at the same thing from further away

> The theory behind [`renormalisation/`](../README.md), derived from the
> problem rather than from the formula. Read this if you want to know *why*
> the equations in `renormalisation/flow.py` and `renormalisation/methods/`
> are those and not others.

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
7. [Two ways to count](#7-two-ways-to-count)
8. [Scale analysis: what a bigger block does not fix](#8-scale-analysis-what-a-bigger-block-does-not-fix)
9. [Closed forms worth memorising](#9-closed-forms-worth-memorising)
10. [What the simulation showed](#10-what-the-simulation-showed)
11. [Where the model stops being true](#11-where-the-model-stops-being-true)
12. [The essentials](#12-the-essentials)
13. [Open questions](#13-open-questions)
14. [References](#14-references)

---

## 1. The phenomenon

Take a lattice and occupy each site independently with probability $p$. At low
$p$ the occupied sites form small islands. At high $p$ they form one connected
mass spanning the whole system. In between, at $p_c = 0.5927460$, something
happens that is not a gradual crossover: the connected cluster becomes
infinite, and every length scale in the system diverges at once.

That much [`forest-fire/`](../../forest-fire/) measures. It leaves two
questions, and the second one is genuinely strange.

**Why is the threshold that number?**

And: **why do systems with nothing in common share the same exponents?** Near
its critical point a magnet's correlation length diverges as
$|T - T_c|^{-\nu}$. So does a liquid's, approaching its critical point. So
does a percolating lattice's, approaching $p_c$. The three systems are made of
different things, held together by different forces, and described by
different equations — and in two dimensions they fall into classes within
which $\nu$ is *identical*, to every digit anyone has measured.

That should be alarming. Physics does not usually let you forget what
something is made of.

The answer to both questions is one idea, and it is almost embarrassingly
simple: **look at the system from further away, and see what survives.**

## 2. What this is for

### 2.1 Critical phenomena, which is where it was invented

Phase transitions — magnetisation, boiling, superconductivity, the onset of a
percolating cluster. The renormalisation group is the reason we can compute
critical exponents at all, and the reason we know which systems share them.

### 2.2 Quantum field theory

The same machinery, invented twice. In field theory the "coarse-graining" is
integrating out high-momentum modes, the "flow" is the running of coupling
constants with energy scale, and the fixed points classify which theories
make sense at all. That the two subjects turned out to be one subject is the
main reason Wilson's work mattered as much as it did.

### 2.3 Anywhere a system has no characteristic scale

Turbulence, fracture, earthquakes, neural avalanches, the size distribution of
forest fires. Whenever a measured quantity follows a power law over decades,
the reason is that the system has no preferred length, and the tool for a
system with no preferred length is this one.

### 2.4 History

::: **Percolation was invented to describe fluid in a random medium** ·
*Verification: A — Broadbent & Hammersley, Math. Proc. Cambridge Phil. Soc.
53(3), 1957, 629–641, which names the field and states its examples.*

Simon Broadbent and John Hammersley wrote the founding paper in 1957. They
posed the question in general terms — how do the random properties of a
*medium* govern the passage of a *fluid* through it — and were explicit that
neither word should be taken literally. The examples they list include solute
through solvent, electrons over an atomic lattice, molecules through a porous
solid, and **disease through a community**.

That last one is worth stopping on. The epidemiological reading of percolation
is not a later application invented when the tools got good. It is in the
paper that named the field, in 1957, alongside the chemistry. What
[`forest-fire/`](../../forest-fire/) does with lightning and trees, and what
an epidemic model does with contacts and infections, were the same question
from the first day.

::: **Blocks of spins, and a question nobody could answer** ·
*Verification: A — Kadanoff (1966) for the block-spin construction and the
scaling relations it explains.*

By the 1960s the problem was sharp and stuck. Experiments gave critical
exponents. Mean-field theory gave different ones, and was demonstrably wrong —
Onsager's exact solution of the two-dimensional Ising model had shown that in
1944. Various empirical relations *between* the exponents had been noticed,
but nobody could derive them.

In 1966 Leo Kadanoff proposed something that sounds more like a change of
attitude than a calculation. Near the critical point the correlation length is
enormous — much larger than the lattice spacing — so **group the spins into
blocks, replace each block by a single effective spin, and ask what the
resulting system looks like.** If the answer is "the same system with a
different temperature", you have a map, and everything follows from the map.

His argument explained the empirical scaling relations. What it did not do was
compute anything: the block transformation was a picture, not a procedure.

::: **Turning a picture into a calculation** ·
*Verification: A — Wilson's two 1971 papers, and the 1982 Nobel Prize.
B for the reading of why it took five years, which is interpretation.*

Kenneth Wilson recast Kadanoff's block transformation in differential form and
made it something you could actually compute with — an $\varepsilon$-expansion
that produced exponents, and a framework in which a fixed point of the flow
*is* a critical point and its unstable directions *are* the relevant
parameters. He published two consecutive papers in 1971 and was awarded the
Nobel Prize in 1982.

The result that mattered most is the one this entry is built to show. The flow
has fixed points, and a fixed point does not remember how you got to it.
Microscopic details are *irrelevant* in the technical sense: they shrink under
the flow. Whatever survives is shared by everything that flows to the same
fixed point, and that is the mechanism behind universality. The magnet and the
liquid do not agree by coincidence. They agree because both are being carried
to the same place.

::: **And a small one, on this entry's own arithmetic** ·
*Verification: A — the factorisation is on paper in section 6.*

The $b = 2$ recursion for site percolation, $R(p) = 2p^2 - p^4$, has fixed
point $(\sqrt5 - 1)/2$: the golden ratio, 4.3% away from the true threshold.
It is a nice number and it is worth being clear that it is a coincidence of
the smallest possible block, not a deep fact about percolation. Section 8
shows what happens when you make the block bigger, which is not what you would
guess.

#### Papers worth reading

- **Broadbent & Hammersley (1957)**. Where percolation gets its name and its
  first questions.
- **Kadanoff (1966)**. The block-spin idea, before it could compute anything.
- **Wilson (1971)**, and the 1982 Nobel lecture, which is unusually readable
  and explains the motivation better than the papers do.
- **Reynolds, Stanley & Klein (1980)**. Real-space RG for percolation, the
  cell-to-cell scheme, and where the numbers in section 10 come from.
- **Stauffer & Aharony**, *Introduction to Percolation Theory*. The standard
  text, and the source of $p_c = 0.5927460$ and $\nu = 4/3$.

## 3. Before you calculate

**The renormalisation group is not a group.** It has no inverses:
coarse-graining destroys information and you cannot go back. It is a
semigroup, and the name is a historical accident everyone has agreed to keep.

**A fixed point is not a solution of the model.** It is a statement about what
the model looks like at large scales. The critical point is where the system
looks the same at every magnification, which is precisely the condition for
the coarse-graining map to leave it alone.

**Nothing here computes a partition function.** That is the whole appeal. The
question "what is the threshold" is answered by a property of a map, not by
summing over configurations, and the map for a small block is a polynomial you
can factor by hand.

## 4. Why the naive answer fails

**Simulate a bigger lattice.** This is what `forest-fire/` does, and it works
— it is where $p_c = 0.5927460$ comes from. But it gives you a number and no
understanding, and it cannot answer the universality question at all: to
discover that a magnet and a lattice share $\nu$ by simulation, you would have
to simulate both and then be surprised.

**Do perturbation theory in the interaction.** At a critical point every
length scale contributes equally, so there is no small parameter. The
expansions diverge. This is why the problem stood open for decades: the
standard tool of theoretical physics simply does not apply.

**Use mean-field theory.** Replace the neighbours by their average. It is
solvable, it gives the wrong exponents, and Onsager proved it wrong in 1944.
The reason it fails is exactly the reason the problem is hard: at the critical
point the fluctuations that mean-field theory averages away *are* the physics.

The way out is to stop trying to solve the system and start asking how it
changes when you look at it from further away.

## 5. The minimal model

Site percolation on a square lattice. Occupy each site independently with
probability $p$; ask whether occupied sites connect across the lattice.

It is the smallest model with a genuine critical point, and its coarse-graining
step is finite and exact: a $b \times b$ block has $2^{b^2}$ configurations,
and for small $b$ you can enumerate all of them. **The entire renormalisation
group becomes one polynomial**, which is a rare thing — in almost every other
application the flow is approximate and the approximation is the hard part.

## 6. The equations

### 6.1 The coarse-graining map

Group the lattice into $b \times b$ blocks and decide when a block counts as
occupied at the coarse scale. What must survive coarse-graining is
**connection** — a block of disconnected sites conducts nothing — so the
criterion is spanning.

The probability a block spans is a polynomial in $p$:

$$R(p) = \sum_k N_k \, p^k (1-p)^{b^2 - k},$$

with $N_k$ the number of spanning configurations having exactly $k$ sites
occupied. That is it. The whole RG for this problem is that one line.

### 6.2 The smallest case, on paper

For $b = 2$ with a top-to-bottom rule, a block spans if either column is
full. Inclusion–exclusion gives

$$R(p) = 2p^2 - p^4.$$

Fixed points satisfy $R(p^\ast) = p^\ast$, which factors:

$$2p^2 - p^4 = p \iff p\,(p - 1)(p^2 + p - 1) = 0,$$

so besides the trivial $0$ and $1$,

$$p^\ast = \frac{\sqrt5 - 1}{2} = 0.618034.$$

The golden ratio, 4.3% above the true $p_c = 0.5927460$.

### 6.3 Why the fixed point must be unstable

Start slightly below $p^\ast$ and iterate: the density falls, and keeps
falling, until at large scales the system is empty. Start slightly above and
it rises to one. The fixed point repels in both directions.

That instability is not a defect — **it is what a critical point is.** A
stable fixed point would mean a whole range of $p$ looked the same at large
scales, which is what happens *off* criticality (everything flows to "empty"
or to "full"). Only exactly at $p^\ast$ does the system look identical at
every magnification, and only an unstable fixed point can do that.

### 6.4 An exponent out of a derivative

Near the fixed point, linearise. One coarse-graining step multiplies the
distance from $p^\ast$ by $\lambda = \mathrm{d}R/\mathrm{d}p$, while dividing
every length by $b$. If the correlation length behaves as
$\xi \sim |p - p^\ast|^{-\nu}$, then consistency between those two statements
requires

$$\xi' = \xi / b \quad\text{and}\quad |p' - p^\ast| = \lambda|p - p^\ast|
\;\;\Longrightarrow\;\; \nu = \frac{\ln b}{\ln \lambda}.$$

**A critical exponent from the slope of a polynomial.** Nothing about the
microscopic lattice appears in it — not the coordination number, not the
lattice constant, not what the sites are. That is universality, stated as a
formula, and it is why unrelated systems share exponents.

## 7. Two ways to count

The polynomial needs $N_k$, and there are two ways to get it.

**Enumeration** walks all $2^{b^2}$ configurations and checks each for
spanning. Exact, and the cost is what it says: $b = 4$ is 65,536
configurations, $b = 5$ is 33 million.

**Sampling** works at fixed occupancy $k$, drawing configurations and
estimating the spanning fraction, then multiplying by $\binom{b^2}{k}$.
Cheaper for large $b$, and it brings an error bar the exact method does not
have.

They are the same physics with different bookkeeping, and the contract suite
holds both to the same domain laws. That is the point of the split: the
domain file knows what spanning means and nothing about how you count.

## 8. Scale analysis: what a bigger block does not fix

Here is the obvious prediction, and it is worth writing down before looking:
**a bigger block should give a better answer.** The $b=2$ result is 4.3% off;
$b = 3$ and $b = 4$ have more room to represent the geometry, so the fixed
point should approach $p_c$ and the exponent should approach $4/3$.

It is not what happens.

![Left: the fixed point against block size for four schemes; the plain rules
sit on horizontal or diverging lines while cell-to-cell hugs the true
threshold. Right: error in the exponent, with the cell-to-cell bars several
times smaller than the plain ones.](figures/convergence.png)

The plain block-to-site schemes do not converge on $p_c$ as $b$ grows. The
"vertical" rule sits at 0.62 regardless of block size; the "either" rule moves
*away*, from 0.38 at $b=2$ toward 0.51; the "both" rule sits high near 0.71.
Enlarging the block does not help, because it does not touch the thing that is
wrong.

What is wrong is that the scheme compares **a block against a site**, and a
block and a site are not the same kind of object. A block has an interior, a
boundary, a shape; a site has none of these. Any error in the spanning rule is
therefore an error in the comparison itself, and it does not shrink with $b$
— it is systematic.

The fix is to compare **a block against a block** of a different size, which
is what `solve.cell_to_cell` does. Both sides are then the same kind of
object, most of what the rule gets wrong appears on both sides, and it
cancels. That is the whole idea, and it turns a 4–14% error into 0.3%.

## 9. Closed forms worth memorising

| Quantity | Form |
|---|---|
| The RG map | $R(p) = \sum_k N_k p^k (1-p)^{b^2-k}$ |
| $b = 2$, vertical spanning | $R(p) = 2p^2 - p^4$ |
| Its fixed point | $(\sqrt5-1)/2 = 0.618034$ |
| Exponent from the slope | $\nu = \ln b / \ln \lambda$, $\lambda = R'(p^\ast)$ |
| True values (2-D site percolation) | $p_c = 0.5927460$, $\nu = 4/3$ |
| Enumeration cost | $2^{b^2}$ |

## 10. What the simulation showed

**The paper result reproduces exactly.** $R(p) = 2p^2 - p^4$, fixed point at
the golden ratio, verified against the factorisation rather than against a
root finder.

**A bigger block is not the fix, and the figure is the argument.** Measured,
for the three plain rules at $b = 2, 3, 4$ and cell-to-cell on block pairs:

```
     either      2,3   0.559599    5.6%    1.2791    4.1%
     either      3,4   0.591046    0.3%    1.3758    3.2%
     either      2,4   0.574132    3.1%    1.3161    1.3%
```

The best of them reaches **0.591046 against 0.592746 — 0.3%** — out of blocks
of at most sixteen sites, with no simulation of a large lattice anywhere. The
threshold that `forest-fire/` needed a lattice sweep to measure falls out of a
polynomial in sixteen variables.

**The exponent is the harder number.** It comes from a derivative, and a
derivative of an approximate map is worse than the map. The best $\nu$ here is
1.3161 against $4/3$, which is 1.3%, and the plain schemes are off by up to
20%. Anyone quoting a real-space RG exponent to three digits is quoting the
scheme, not the physics.

**Which is the honest summary of the method.** Real-space RG on small blocks
is a machine for showing you *why* there is a threshold and *why* exponents
are universal, using arithmetic you can check by hand. It is not a machine for
computing either to high precision, and the entry says so rather than
presenting 0.3% as though the method were generally that good.

## 11. Where the model stops being true

**One parameter.** The real flow lives in an infinite-dimensional space of
couplings, and a real treatment tracks which directions are relevant and which
are irrelevant. Here there is a single $p$, so "irrelevant operators" — the
actual mechanism of universality — cannot be seen at all, only their
consequence.

**The spanning rule is a choice, and the answer depends on it.** Three rules
are implemented and they disagree by up to 14%. There is no principle in the
model that selects one; section 8 shows the disagreement mostly cancels when
both sides of the comparison are blocks, which is a workaround and not a
derivation.

**Blocks are not renormalisable in the strict sense.** A coarse-grained block
lattice is not really a site percolation problem with a new $p$: correlations
appear between blocks, and the map ignores them. It is the first term of
something, and the entry does not compute the second.

**$b$ is capped by $2^{b^2}$.** Exact enumeration stops around $b = 4$–$5$.
The sampling method goes further at the price of an error bar.

**Two dimensions, one lattice, one universality class.** Nothing here tests
universality; it exhibits the mechanism that would produce it.

## 12. The essentials

1. **Coarse-grain and see what survives.** The whole subject is one move.
2. **A critical point is an unstable fixed point of the coarse-graining map**,
   and it has to be unstable, or a range of parameters would look critical.
3. **A critical exponent is the slope of that map**, $\nu = \ln b / \ln
   \lambda$, with nothing microscopic in it. That is universality.
4. **A bigger block is not the fix.** The error is in comparing a block
   against a site; compare a block against a block and it cancels.
5. **The exponent is harder than the threshold**, because it is a derivative
   of an approximate map.

## 13. Open questions

- **Can the disagreement between spanning rules be made a bound rather than a
  nuisance?** Three rules bracket the answer; nothing here turns that into an
  interval anyone should trust.
- **Where does the cell-to-cell cancellation stop working?** It is measured on
  block pairs up to $(2,4)$ and explained by an argument about like-for-like
  comparison, not derived.
- **What does the flow look like with two couplings?** The single-parameter
  flow cannot show an irrelevant direction shrinking, which is the actual
  mechanism of universality rather than its consequence.
- **Does the golden ratio mean anything?** Almost certainly not — it is the
  smallest block's arithmetic. Worth stating because it is the kind of
  coincidence that invites a story.

## 14. References

- Broadbent, S. R., Hammersley, J. M. (1957). *Percolation processes*. Math.
  Proc. Cambridge Phil. Soc. 53(3), 629–641.
- Kadanoff, L. P. (1966). *Scaling laws for Ising models near $T_c$*.
- Onsager, L. (1944). The exact two-dimensional Ising solution, which showed
  mean-field exponents were wrong.
- Reynolds, P. J., Stanley, H. E., Klein, W. (1980). *Large-cell Monte Carlo
  renormalization group for percolation*. Phys. Rev. B 21, 1223.
- Stauffer, D., Aharony, A. *Introduction to Percolation Theory*.
- Wilson, K. G. (1971). *Renormalization group and critical phenomena*, I and
  II. Phys. Rev. B 4, 3174 and 3184.
- Wilson, K. G. (1982). Nobel lecture, *The renormalization group and critical
  phenomena*.
