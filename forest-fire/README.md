# Forest fire

Trees grow, lightning strikes, fire spreads to touching trees. Three rules and
no tuning, and the forest settles by itself at the density where fire can just
barely cross it. 220 lines of core.

| | |
|---|---|
| **Level** | L1 derive · L2 implement · L3 experiment |
| **Domain** | [`lattice.py`](lattice.py) — 133 lines, no timestep loop in it |
| **Methods** | [`instantaneous.py`](methods/instantaneous.py) 23 · [`synchronous.py`](methods/synchronous.py) 52 |
| **Tests** | 46, split into domain, contract, and where the methods diverge |
| **Related work of mine** | [`fire-percolation`](https://github.com/FullFran/fire-percolation) — the same model taken seriously, with real Spanish fire records and a power-law fitter |

## Layout

```
docs/lattice.md       the derivation, from the phenomenon down
docs/figures/         the figures it argues from — tracked, unlike out/
lattice.py            the domain: three states, growth, lightning, spreading
methods/
  instantaneous.py    the cluster burns before anything regrows
  synchronous.py      the fire advances one ring per step, and the forest grows
solve.py              the timestep loop, and one event per fire
experiments/
  percolation.py      the threshold, against p_c = 0.5927460
  ignition.py         fewer sparks, bigger fires — and the version that is false
tests/
  test_lattice.py         domain laws, no model run
  test_methods.py         the contract, run against both
  test_methods_differ.py  where they legitimately disagree
```

Same dependency rule as everywhere in this repo: **`methods/` imports
`lattice`, `lattice` imports nobody.** See
[`docs/architecture.md`](../docs/architecture.md).

## 1. What problem does it solve

A landscape burns from time to time. Most fires are small, a few are enormous,
and the distribution of sizes is broad enough that "the average fire" is not a
useful quantity.

The question is not how a particular fire spreads — that is meteorology. It is
**why the distribution looks the way it does**, and in particular why a system
nobody tuned should sit exactly at the point where a fire can just barely cross
it.

## 2. The equations

There are no equations, which is the point. Derived from the problem downwards
— why tuning a system to its critical point explains nothing, what the
threshold is, and where the whole thing stops being true — in
[`docs/lattice.md`](docs/lattice.md). There are three rules, applied to
every site each step:

1. A burning site becomes empty.
2. A tree next to a burning site catches fire.
3. An empty site grows a tree with probability $p$; a tree is struck by
   lightning with probability $f$.

Everything else is a consequence. The one number worth memorising is the
**site percolation threshold** on a square lattice,

$$p_c = 0.5927460$$

which is where a random forest first connects one edge to the other. It has no
closed form — it is known numerically — and it is what this entry checks itself
against.

The regime that makes the model interesting is $f \ll p \ll 1$: fires must
finish long before the forest regrows. That is not a detail, it is the model,
and [`check_rates`](lattice.py) refuses anything else.

## 3. What I implemented

```
lattice.P_C            the percolation threshold, as a closed form to test against
lattice.grow()         empty sites become trees with probability p
lattice.strike()       which trees lightning hit — a mask, not an action
lattice.spread()       the four sites a fire reaches next
lattice.cluster()      every tree connected to a seed, by repeated spreading
lattice.spans()        does a group of trees reach from one edge to the other
methods.instantaneous  the cluster burns before anything regrows
methods.synchronous    one ring per step, with the forest growing
solve.run()            the loop, returning one Fire per fire
```

## 4. What I verified

46 tests, in three groups. Note what is *not* in the contract: that a fire
equals the cluster that was standing when it started. That is true of one
method and false of the other, and the difference is the entry.

| Property | Scope |
|---|---|
| **Spanning crosses ½ at p_c = 0.5927, and the transition sharpens with L** | domain |
| Fire spreads to four neighbours and not diagonally | domain |
| A cluster stops at a gap; a bare site has none | domain |
| `strike` returns a mask and does not modify the lattice | domain |
| Lightning at or above the growth rate is rejected | domain |
| A fire consumes trees and leaves no site burning | contract |
| The forest reaches a steady density | contract |
| **Fewer ignitions make bigger fires, and a denser forest** | contract |
| Every fire is reported separately, not one per timestep | contract |
| **Instantaneous: a fire can never exceed the lattice** | differ |
| **Synchronous: a fire can burn more than the whole lattice** | differ |
| **They agree only when the forest grows slowly — and that is set by p, not f/p** | differ |
| **A fast-growing forest makes fire endemic, and it never goes out** | differ |

### The experiments

**[`percolation.py`](experiments/percolation.py)** — prediction: the crossing
sits at $p_c$, and the transition sharpens with the lattice.

```
       L   p where spanning crosses 1/2   width of the crossing
      16                         0.5867                  0.1367
      32                         0.5900                  0.0896
      64                         0.5917                  0.0625
     128                         0.5926                  0.0467
```

At L = 128 the measured crossing is 0.5926 against the true 0.5927460, and the
width has halved twice. That is a threshold, not a trend: on an infinite
lattice the curve would be a step.

**[`ignition.py`](experiments/ignition.py)** — the model's version of the fire
suppression argument, run two ways that disagree.

```
        f      f/p  density   fires    mean  largest  of lattice
    2e-02  4.0e-01    0.244  242893     7.2      136        1.5%
    1e-03  2.0e-02    0.350   12689    88.6     2209       24.0%
    2e-04  4.0e-03    0.374    2640   409.8     5396       58.6%
    1e-05  2.0e-04    0.528     193  4224.5     9083       98.6%
```

**Reduce the sparks 2000× and the largest fire goes from 1.5% of the forest to
98.6%** — the whole thing. The density rises from 0.24 to 0.53, past $p_c$.
That is the effect, and it is enormous.

Now the version everybody actually says, which is that putting out small fires
lets fuel build up. Let fires start, then extinguish any below a size threshold
and leave the trees standing:

```
 threshold   density    fires   largest  total burned
         0     0.398      953      7684       1385741
        10     0.397      643      7448       1388102
        50     0.396      484      7448       1388489
       200     0.395      402      7518       1391419
```

**Nothing happens.** The density does not move and the total burned area does
not move, and there is a reason: at steady state the area burned per step is
pinned by the area grown per step. Extinguishing a fire does not save its fuel,
it hands it to the next one.

So the mechanism is in **when fires start**, not in whether they are fought
once started. Both of those map onto real fire management, and they are not the
same intervention — worth knowing before quoting the model at a policy.

One caveat stated rather than buried: in the last rows of the first table the
fire covers 98.6% of the lattice, so the measurement is limited by the box, not
by the physics. That saturation is part of a live argument about whether this
model is critical at all — see below.

## 5. What I deliberately left out

- **The power-law exponent.** Fitting one properly needs care about `x_min`,
  goodness of fit and finite-size cutoffs, and getting it wrong is easy and
  invisible. [`fire-percolation`](https://github.com/FullFran/fire-percolation)
  does it, and its `FINDINGS.md` is a good account of how it goes wrong.
- **The sandpile.** Bak–Tang–Wiesenfeld is where self-organised criticality
  comes from and it is a different model; it deserves its own entry rather than
  a subsection here.
- **Renormalisation.** The reason $p_c$ and the exponents do not depend on the
  microscopic details is the renormalisation group, and it is the natural next
  entry rather than a paragraph in this one.
- **Immunity, wind, heterogeneous fuel, tree ageing.** All real, all standard
  extensions, none of them needed to see the phenomenon.
- **Real fire records.** Also in `fire-percolation`, with fifty years of
  Spanish data.

## Where this stops being right

| Boundary | What happens |
|---|---|
| **Is it even critical?** | Grassberger (2002) and Pruessner & Jensen (2002) showed the scaling is broken: there is no single power-law regime at any size tested |
| Growth rate above ~0.1, synchronous | The fire never goes out — regrowth feeds the front faster than it burns through |
| f not far below p | The two methods disagree by a factor of seven or more |
| Large lattices, fixed f | Strikes per step grows as $fL^2$; several fires per step breaks the separation of timescales silently |
| The largest fire near 100% | Limited by the box, not the physics |
| Fire suppression as a policy claim | The model supports the ignition-rate version and not the put-it-out version |
| A square lattice with four neighbours | $p_c$ is a property of the lattice, not of forests |

The first row is the honest headline. This model is the standard textbook
example of self-organised criticality, and the best current evidence is that it
is **not cleanly critical** — the apparent power law breaks up under scrutiny.
That is a better thing to know than the tidy version.

## Run it

```bash
uv run pytest forest-fire                              # 46 tests
uv run python forest-fire/experiments/percolation.py   # ~40 s
uv run python forest-fire/experiments/ignition.py      # ~2 min
```

## What this sets up

Renormalisation. The reason $p_c$ is what it is, and the reason critical
exponents do not care what the microscopic rules were, is that coarse-graining
the lattice flows the parameters towards a fixed point. On this model that
calculation is small enough to do by hand: a $2\times2$ block gives
$R(p) = 2p^2 - p^4$, and $R(p^{\ast}) = p^{\ast}$ has the solution
$p^{\ast} = (\sqrt5 - 1)/2 = 0.618$ — the golden ratio, 4% from the true
threshold, out of a quartic.

That is the next entry, and this one is the object it acts on.
