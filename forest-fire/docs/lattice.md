# A forest that keeps itself flammable

> The physics behind [`forest-fire/`](../README.md), derived from the problem
> rather than from the formula. Read this if you want to know *why* the rules
> in `forest-fire/lattice.py` are those and not others.

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
6. [The rules](#6-the-rules)
7. [Two ways to finish a fire](#7-two-ways-to-finish-a-fire)
8. [Scale analysis: one threshold and one ratio](#8-scale-analysis-one-threshold-and-one-ratio)
9. [Closed forms worth memorising](#9-closed-forms-worth-memorising)
10. [What the simulation showed](#10-what-the-simulation-showed)
11. [Where the model stops being true](#11-where-the-model-stops-being-true)
12. [The essentials](#12-the-essentials)
13. [Open questions](#13-open-questions)
14. [References](#14-references)

---

## 1. The phenomenon

Most forest fires are small. A few are enormous. Plot how many fires burned
each area and you do not get a bell curve with a typical size and a spread —
you get a straight line on log-log paper over four or five orders of
magnitude, which means there is no typical size at all.

That is already strange. "The average fire" is a number you can compute and
cannot use, because the average is dominated by the rare huge ones and
describes almost nothing that actually happens.

Stranger still: the same shape appears in earthquakes, avalanches, solar
flares, extinction events and the sizes of cities. Systems with nothing in
common, producing the same distribution.

> **The question.**
> Trees grow at some rate, lightning strikes at some rate, and fire spreads
> between touching trees.
> **Why should the forest end up at the density where fire can just barely
> cross it, without anybody tuning it there?**

That last clause is the whole subject. Getting a sharp transition out of a
model is easy: put the control parameter at the critical value by hand. Having
the system **arrive there on its own** is what needs explaining, and it is what
"self-organised criticality" names.

---

## 2. What this is for

### 2.1 Fire, which is the literal case

Malamud, Morein and Turcotte showed in 1998 that real fire records — US and
Australian, including reconstructed pre-history — have power-law frequency-area
statistics over many orders of magnitude, and that the frequency of small and
medium fires can be used to quantify the risk of large ones, the way it is done
for earthquakes.

That is the practical payoff, and it is a statistical one rather than a
predictive one: you cannot say when the big fire comes, and you can say how
often.

### 2.2 Everything else shaped like it

The same model, with the words changed, is a plausible sketch of epidemics on a
contact network, cascading failures in a power grid, avalanches in a sandpile,
and rumours in a crowd. In each, something spreads locally between neighbours,
something replenishes what it consumed, and the system sits near the point
where spreading just barely percolates.

Whether that resemblance is deep or superficial is genuinely contested, and
[§11](#11-where-the-model-stops-being-true) is where this document stops
taking it for granted.

### 2.3 The connection this repo cares about

A percolation threshold is a **critical point**, and the reason it does not
depend on the microscopic details is the renormalisation group. That is the
thread running from here to [§13](#13-open-questions): coarse-grain the
lattice, watch the parameters flow, and the details that do not survive the
zoom are the ones that never mattered.

### 2.4 History

Verification levels follow the convention of the book: **A** is documented,
ideally from a primary source; **B** is a reconstruction; **C** is a story told
everywhere that I could not source.

::: **A sandpile, and a very loud claim** · *Verification: A for the science;
B for the reception.*

In 1987 Per Bak, Chao Tang and Kurt Wiesenfeld published *Self-organized
criticality: an explanation of 1/f noise*. Their model was a sandpile: drop
grains one at a time, and when a column gets too steep it topples onto its
neighbours, which may topple in turn. The avalanche sizes come out power-law
distributed, and — this is the claim — **nobody set the slope**. The pile
builds itself to the angle where avalanches of every size are possible.

Bak thought this was the general explanation for why nature is full of power
laws, and said so at length, including in a book titled *How Nature Works*. He
was, by broad account, not a modest advocate. The field that grew up around the
idea has spent thirty years sorting the parts that hold from the parts that
were oversold, and this entry's model is one of the places that sorting
happened.

::: **Drossel and Schwabl, and a model that turned out to be harder than it
looked** · *Verification: A.*

Drossel and Schwabl published the forest-fire version in *Physical Review
Letters* in 1992: growth, lightning, spreading, and a self-organised critical
state in the limit $f \to 0$ **provided the timescales separate**. That proviso
is in the original abstract and it is the whole model, which is why
[`check_rates`](../lattice.py) refuses to run outside it.

For a decade it was the textbook example. Then Grassberger (2002) and Pruessner
and Jensen (2002) looked at large lattices and found the scaling is **broken**:
there is no single power-law regime, and what earlier work had fitted was a
mixture of a bulk that is not a power law and a cutoff that is not scaling.

The tidy story is that a simple model explains why fires are power-law
distributed. The true story is that the simplest model of self-organised
criticality is, on current evidence, not cleanly critical — and that this was
established by people taking the trouble to go to larger lattices. It is a
better lesson than the tidy one.

### Papers worth reading

| Reference | Why |
|---|---|
| [Bak, Tang & Wiesenfeld, *PRL* **59**, 381 (1987)](https://doi.org/10.1103/PhysRevLett.59.381) | Where self-organised criticality starts |
| [Drossel & Schwabl, *PRL* **69**, 1629 (1992)](https://link.aps.org/doi/10.1103/PhysRevLett.69.1629) | This model, with the timescale proviso in the abstract |
| [Malamud, Morein & Turcotte, *Science* **281**, 1840 (1998)](https://www.science.org/doi/10.1126/science.281.5384.1840) | Real fires really are power-law distributed |
| [Grassberger, *New J. Phys.* **4**, 17 (2002)](https://arxiv.org/abs/cond-mat/0202022) | The scaling is broken. Read it before quoting the model |
| [Pruessner & Jensen, *Phys. Rev. E* **65**, 056707 (2002)](https://arxiv.org/abs/cond-mat/0201306) | Independently, the same conclusion |
| [Stauffer & Aharony, *Introduction to Percolation Theory*](https://doi.org/10.1201/9781315274386) | Where $p_c$ and the exponents come from |
| [`fire-percolation`](https://github.com/FullFran/fire-percolation) | My own reproduction of the broken scaling, and fifty years of Spanish records |

---

## 3. Before you calculate

The rule from the book: **write a number down before you read the next
section.** The learning is in the gap between your number and the real one,
and the gap does not exist if you did not commit.

> 1. A forest with trees on half its sites. **Can a fire cross it?** Now 60% of
>    its sites. Same question. How different are those two answers?
> 2. You cut the number of lightning strikes by a factor of two thousand.
>    **What happens to the biggest fire that eventually comes?** Does it grow a
>    bit, or a lot?
> 3. Fire fighters put out every small fire and let the big ones run.
>    **What happens to the total area burned over a century?**

Answers in [§8](#8-scale-analysis-one-threshold-and-one-ratio) and
[§10](#10-what-the-simulation-showed). The first is the sharpest threshold in
this document. The third is the one I got wrong, and the mistake is in
[§10.2](#102-the-suppression-argument-run-two-ways).

---

## 4. Why the naive answer fails

### 4.1 "The forest burns at some average rate"

The tempting first model: fire consumes some fraction of the forest per year,
so write down a rate and be done.

That model has a typical fire size, and real fires do not. A distribution with
a power-law tail has no characteristic scale — the mean is dominated by the
largest events, and if the exponent is shallow enough the variance does not
even exist. **Reporting an average fire size is not a summary, it is a
category error**, in the same way that reporting an average earthquake would
be.

### 4.2 "Then tune the density to the critical point"

Better: fire crosses a forest only above a threshold density, so put the
density at the threshold and you get big fires.

This is correct and it explains nothing, because it requires someone to hold
the dial. A real forest has nobody adjusting its tree density, and the density
it settles at is an *output*.

**The move that makes the model interesting is closing that loop.** Let growth
push the density up and let fire push it down, and ask where it ends up. The
answer is: at the threshold, because below it fires cannot spread and growth
wins, and above it fires spread everywhere and burning wins. The critical
point is an attractor of the dynamics rather than a value someone chose.

That is what "self-organised" means, and it is the only genuinely new idea in
the model.

---

## 5. The minimal model

| Assumption | What it buys | Where it breaks |
|---|---|---|
| A square lattice, four neighbours | A single threshold to check against | $p_c$ is a property of the lattice, not of forests |
| Trees are identical | One state, not a fuel load | Species, age, moisture, terrain |
| Fire spreads to touching trees, always | No spread probability to tune | Firebreaks, wind, humidity, spotting |
| Growth is uniform and independent | One parameter $p$ | Seeds fall near parents; soil varies |
| Lightning is uniform and independent | One parameter $f$ | Human ignition clusters near roads |
| $f \ll p \ll 1$ | Fires finish before regrowth | The whole model — see [§7](#7-two-ways-to-finish-a-fire) |
| Periodic boundaries | No site is special | Real landscapes have coasts and edges |
| No wind, no slope, no season | Isotropy | All of fire behaviour, frankly |

That is the model. It contains no physics of combustion, no meteorology and no
biology, and the claim is that none of that matters for the *statistics* of
fire sizes. Whether that claim survives is [§11](#11-where-the-model-stops-being-true).

---

## 6. The rules

There are no equations here. There are three rules applied to every site each
step:

1. A burning site becomes empty.
2. A tree next to a burning site catches fire.
3. An empty site grows a tree with probability $p$; a tree is struck by
   lightning with probability $f$.

The only spatial content is rule 2, and it is one line —
[`spread()`](../lattice.py) is four shifted copies of a boolean array OR'd
together. A **cluster** is what you get by applying it until nothing new
catches, and that is the object the whole model is about: a fire burns a
cluster, not a radius.

> **One implementation note that is really a physics note.**
> [`strike()`](../lattice.py) returns a *mask* rather than setting fires.
> That is so the caller can give each struck tree its own fire. The expected
> number of strikes in a step is $f\rho L^2$, which grows with the area, so on
> a large lattice several strikes per step is the normal case — and burning
> them together reports two independent fires as one, inflating the size
> distribution by an amount that grows with $L$. Which is exactly the variable
> a finite-size study is trying to isolate.

---

## 7. Two ways to finish a fire

The rules above do not say how long a fire takes relative to the forest
growing, and that omission is the model's central assumption. `methods/` makes
it switchable.

**Instantaneous.** Lightning strikes, the connected cluster burns to the
ground, and only then does anything grow. The burned area *is* the cluster that
was standing. This is the limit the model is defined in.

**Synchronous.** The literal cellular automaton: each step, burning sites empty,
their neighbours catch, and empty sites sprout — including behind the front and
just ahead of it. A fire that takes many steps burns through a forest that is
regrowing around it, so the area consumed is no longer the cluster it started
in. **It can exceed the whole lattice**, because ground can burn twice.

The two agree in the limit that matters, and watching them part company is how
this entry measures what "separation of timescales" is worth
([§10.3](#103-when-the-two-methods-agree)).

---

## 8. Scale analysis: one threshold and one ratio

### 8.1 The threshold

Fill a lattice at random with density $p$ and ask whether trees connect one
edge to the other. Below a critical density, essentially never; above it,
essentially always:

$$\boxed{\enspace p_c = 0.5927460\enspace}$$

for site percolation on a square lattice with four neighbours. It has **no
closed form** — it is known numerically to many digits and that is all — which
makes it a genuine external reference rather than something the model could
have been fitted to.

*Answer to question 1.* At 50% a fire essentially never crosses; at 60% it
essentially always does. Ten percentage points, and the behaviour is
qualitatively different on either side. That is what a threshold means and it
is why "the forest is half full" is not a useful description of anything.

### 8.2 Strikes per step, which is not $f$

The regime the model needs is that fires are rare *and finish quickly*. Two
different conditions, and only one of them is about $f$ alone.

The expected number of strikes per step is

$$\langle\text{strikes}\rangle = f\thinspace\rho\thinspace L^2$$

so at fixed $f$ it **grows with the area**. A guard that only checks $f \ll p$
cannot see this, because it has no $L$ in it, and the regime can therefore fail
silently in exactly the sweep that varies $L$.

### 8.3 And the separation of timescales is set by $p$

The other condition — that a fire finishes before the forest regrows — is
about how much forest appears *during* one fire. That is growth rate times fire
duration, so it is controlled by $p$, **not by $f/p$**.

Measured, at $f/p$ held fixed at 0.01, the ratio of mean fire size between the
two methods:

| $p$ | 0.02 | 0.01 | 0.005 | 0.002 |
|---|---|---|---|---|
| synchronous / instantaneous | 7.0 | 2.1 | 1.9 | 1.0 |

Holding $f/p$ constant and lowering $p$ alone brings them together. That is the
sharp version of a phrase that usually gets waved through.

---

## 9. Closed forms worth memorising

| Situation | Result |
|---|---|
| Site percolation threshold, square lattice | $p_c = 0.5927460$ |
| Below $p_c$ | no spanning cluster, in the large-lattice limit |
| Above $p_c$ | spanning with probability approaching 1 |
| Strikes per step | $f\rho L^2$ — grows with area |
| Steady state | area burned per step $=$ area grown per step |
| Instantaneous method | burned area $=$ cluster size $\le L^2$ |
| Synchronous method | burned area can exceed $L^2$ |
| Endemic fire | above $p \approx 0.1$ the synchronous fire never goes out |
| Real fire records | power-law frequency-area, exponent 1.3 to 1.5 |
| Correlation length at $p_c$ | diverges — which is why finite lattices lie |

**A warning about the steady-state row**, because it is the one that decided
[§10.2](#102-the-suppression-argument-run-two-ways). It is a conservation law,
not an approximation: whatever grows must eventually burn, so the total area
burned per unit time is pinned by $p$ and the empty fraction. Any intervention
that does not change *growth* or *when fires start* cannot change it.

---

## 10. What the simulation showed

### 10.1 The threshold, measured

Prediction: the crossing sits at $p_c$, and the transition sharpens with the
lattice.

![Fraction of random lattices in which trees span from one edge to the other,
against tree density, for four lattice sizes, with the percolation threshold
marked.](figures/percolation.png)

```
     L   p where spanning crosses 1/2   width of the crossing
    16                         0.5867                  0.1367
    32                         0.5900                  0.0896
    64                         0.5917                  0.0625
   128                         0.5926                  0.0467
```

**What to conclude:** both halves held. At $L = 128$ the measured crossing is
0.5926 against the true 0.5927460, and the width has halved twice. On an
infinite lattice the curve would be a step; every finite lattice smears it, and
watching the smear shrink is what distinguishes a phase transition from a
gradual change.

### 10.2 The suppression argument, run two ways

Prediction, written down first: **extinguish every fire below a size threshold,
leave its trees standing, and the density should climb and the largest fire
grow with it.** That is the standard fuel-accumulation argument.

```
 threshold   density    fires   largest  total burned
         0     0.398      953      7684       1385741
        10     0.397      643      7448       1388102
        50     0.396      484      7448       1388489
       200     0.395      402      7518       1391419
```

**Wrong.** Nothing moves — not the density, not the largest fire, and not the
total burned area. The conservation law of §9 is in the way: whatever grows
must burn, so putting a fire out does not save its fuel, it hands it to the
next one.

I was ready to report that the paradox does not appear in this model. It does,
on a knob I had not turned. The mechanism is the **ignition rate**:

![Left: tree density against lightning rate, with the percolation threshold
marked. Right: the largest fire as a percentage of the forest, against the same
axis.](figures/ignition.png)

```
      f      f/p  density   fires    mean  largest  of lattice
  2e-02  4.0e-01    0.244  242893     7.2      136        1.5%
  1e-03  2.0e-02    0.350   12689    88.6     2209       24.0%
  2e-04  4.0e-03    0.374    2640   409.8     5396       58.6%
  1e-05  2.0e-04    0.528     193  4224.5     9083       98.6%
```

**What to conclude:** 2000× fewer sparks takes the largest fire from 1.5% of
the forest to 98.6%, and the density from 0.24 past $p_c$ to 0.53. Fewer
ignitions means longer between fires, means a denser forest when one finally
comes.

*Answer to question 3, and it is two answers.* The total area burned over a
century barely changes — that is the conservation law. **What changes is how it
is delivered**: as many small fires, or as one that takes everything. Those are
the same integral and very different centuries.

And they are different interventions in the real world too. Preventing
ignitions is not the same act as fighting a fire that has started, and only the
first one moves this model.

**One caveat stated rather than buried.** In the last row the fire covers 98.6%
of the lattice: that measurement is limited by the box, not by the physics. It
is also the crack through which §11 arrives.

### 10.3 When the two methods agree

Covered in [§8.3](#83-and-the-separation-of-timescales-is-set-by-p). The
prediction — that they converge as the forest grows more slowly — held, and the
sharp form of it was the surprise: the controlling parameter is $p$ and not
$f/p$.

A second thing fell out of it that was not predicted at all. **Above a growth
rate of roughly 0.1 the synchronous fire never goes out.** Regrowth feeds the
front faster than it burns through, so there is no fire size to report at all:

| $p$ | 0.005 | 0.02 | 0.05 | 0.1 |
|---|---|---|---|---|
| rings until it dies | 4 | 50 | 49 | still burning at 3000 |

The method raises rather than returning a number, because a fire that never
ends does not have a size. The instantaneous version cannot have that
transition at all, since nothing grows while anything is burning — so it is a
property of the *method*, which is the sharpest possible demonstration that
"how long a fire takes" was never a detail.

---

## 11. Where the model stops being true

### 11.1 It may not be critical at all

The headline, and it is not a small caveat.

This model is the standard example of self-organised criticality. For a decade
its fire-size distribution was quoted as a power law. Then Grassberger (2002)
and Pruessner and Jensen (2002) went to large lattices and found the scaling is
**broken**: there is no single power-law regime, and fits over the whole range
are describing a mixture of a bulk that is not scaling and a cutoff that is the
edge of the box.

[`fire-percolation`](https://github.com/FullFran/fire-percolation) reproduces
that independently — the fitted exponent moves by 7.3 against a combined
standard error of 0.54 across lattice sizes, and at large $L$ the fitter
abandons the bulk entirely and lands on the finite-size cutoff. Its
`FINDINGS.md` is worth reading as an account of how a plausible fit can be
meaningless.

The honest position: the *mechanism* here is real and worth understanding —
growth and burning balance at a threshold nobody set. The claim that this
produces clean critical scaling is not established, and the entry-level version
of the story is tidier than the evidence.

### 11.2 The rest of the list

| Limit | What actually happens | This entry |
|---|---|---|
| Large lattices | Strikes per step grows as $fL^2$; the timescale separation fails silently | guarded on $f<p$ only, and §8.2 says why that is not enough |
| Growth above $p\approx0.1$, synchronous | Fire becomes endemic and never ends | raises |
| $f$ not far below $p$ | The two methods disagree by a factor of seven | measured |
| Largest fire near $L^2$ | Limited by the box, not the physics | stated |
| Suppression as policy | The model supports the ignition-rate claim and not the put-it-out claim | measured, both ways |
| Square lattice, four neighbours | $p_c$ is a lattice property; real landscapes are not lattices | not modelled |
| Wind, slope, moisture, species | All of fire behaviour | not modelled |
| Human ignition | Clusters near roads; not uniform | not modelled |

---

## 12. The essentials

- **Power-law sizes mean no typical size.** "The average fire" is a number you
  can compute and cannot use.
- **Tuning a system to its critical point explains nothing.** The content is
  in a system that *arrives* there, because growth pushes up and burning pushes
  down and the threshold is where they balance.
- **$p_c = 0.5927460$**, with no closed form, which is what makes it a real
  external check.
- **A fire burns a cluster, not a radius**, and a cluster is one line of code
  applied until nothing new catches.
- **The steady state is a conservation law**: whatever grows must burn. Any
  intervention that changes neither growth nor when fires start cannot change
  the total.
- **Suppressing fires does not accumulate fuel. Preventing ignitions does.**
  Same integral, very different distribution, and different real-world acts.
- **Separation of timescales is set by the growth rate, not by $f/p$** — what
  matters is how much forest appears during one fire.
- **Above a growth rate of ~0.1 the fire never goes out.** A transition that
  belongs to the method, not the lattice.
- **Strikes per step grows with area**, so a regime check without $L$ in it
  cannot see the regime failing.
- **The textbook example of self-organised criticality is, on current
  evidence, not cleanly critical.** Larger lattices did that, not cleverer
  analysis.

---

## 13. Open questions

- **Why does $p_c$ not care about the details?** Because coarse-graining the
  lattice flows the parameters to a fixed point, and everything that does not
  survive the zoom never mattered. A $2\times2$ block gives
  $R(p) = 2p^2 - p^4$, and $R(p^{\ast}) = p^{\ast}$ factors to
  $p^{\ast} = (\sqrt5-1)/2 = 0.618$ — the golden ratio, 4% from the truth, out
  of a quartic. The exponent from the same calculation is 23% off, and watching
  that converge as the block grows is the next entry.
- **Is it critical or not?** Settling that needs finite-size scaling done
  properly, which is what `fire-percolation` is for and what §11.1 says is not
  settled.
- **What is the sandpile doing that this is not?** Bak–Tang–Wiesenfeld is a
  different model with a conservation law this one lacks, and the difference is
  suspected to matter for whether the criticality is genuine.
- **Do real fires follow this, or something else that also gives power laws?**
  Malamud says the statistics match; a matching distribution is weak evidence
  for a matching mechanism.
- **What does adding a firebreak do?** A structured intervention rather than a
  size threshold, and it is the one policy question this entry could answer and
  does not.

---

## 14. References

**Self-organised criticality**

- **Bak, P., Tang, C. & Wiesenfeld, K.** *Self-organized criticality: an
  explanation of 1/f noise.* Physical Review Letters **59**, 381 (1987).
  [link](https://doi.org/10.1103/PhysRevLett.59.381)
- **Bak, P.** *How Nature Works* (1996). The case, made at full volume.
- **Drossel, B. & Schwabl, F.** *Self-organized critical forest-fire model.*
  Physical Review Letters **69**, 1629 (1992).
  [link](https://link.aps.org/doi/10.1103/PhysRevLett.69.1629)

**And the case against**

- **Grassberger, P.** *Critical behaviour of the Drossel-Schwabl forest fire
  model.* New Journal of Physics **4**, 17 (2002).
  [link](https://arxiv.org/abs/cond-mat/0202022)
- **Pruessner, G. & Jensen, H. J.** *Broken scaling in the forest-fire model.*
  Physical Review E **65**, 056707 (2002).
  [link](https://arxiv.org/abs/cond-mat/0201306)

**Percolation**

- **Stauffer, D. & Aharony, A.** *Introduction to Percolation Theory*, 2nd ed.
  Where $p_c$, the exponents and the real-space renormalisation come from.
- **Newman, M. E. J. & Ziff, R. M.** *Efficient Monte Carlo algorithm and
  high-precision results for percolation.* Physical Review Letters **85**, 4104
  (2000). [link](https://arxiv.org/abs/cond-mat/0005264)

**Real fires**

- **Malamud, B. D., Morein, G. & Turcotte, D. L.** *Forest fires: an example of
  self-organized critical behavior.* Science **281**, 1840–1842 (1998).
  [link](https://www.science.org/doi/10.1126/science.281.5384.1840)

---

*Code: [`../lattice.py`](../lattice.py) and [`../methods/`](../methods/) ·
Entry: [`../README.md`](../README.md) · Repo-wide architecture:
[`docs/architecture.md`](../../docs/architecture.md)*
