# first-principles

Minimal implementations, rebuilt from the equations.

Every entry here exists to prove I understand a mechanism — not to compete
with a production library. If you need a transfer matrix solver, install
`tmm`. If you want to see whether I can derive one, read
[`tmm/physics.py`](tmm/physics.py).

This is also where my scattered didactic repos come to be rewritten. Course
notebooks from 2023–2024 that were never readable get one honest version
each, or they stay archived where they are.

## The rules

1. **A folder exists only once L2 is reached.** No placeholders, no empty
   READMEs waiting to be filled. The map below is allowed to be short; it is
   not allowed to lie.
2. **Nothing arrives by `git mv`.** Migrated code is rewritten to the
   standard or it does not come.
3. **Notebooks are not the core.** A `.ipynb` cannot be diffed or tested, so
   it cannot carry the claim "I understand this". Notebooks are for
   exploration; the core is a `.py`.
4. **The core stays in the 100–500 line band.** Not a law — a pressure. Four
   thousand lines to explain DDPM means a library got built by accident.
5. **Every entry states what it deliberately omits.** Knowing where the
   pedagogical model stops is the point.
6. **This repo is never a dependency.** It gets read, not imported. Real
   projects reimplement properly.
7. **The domain does not import the method.** The equations live in one file
   that knows no algorithm; the algorithms live beside it and depend on it,
   never the reverse. Enforced by a contract suite every method must pass —
   without that, the folders are decoration.
   Written up in [`docs/architecture.md`](docs/architecture.md), with where
   the line goes in the ambiguous cases and who else does this.

## Map

| Topic | Derive | Implement | Experiment | Origin |
|---|:---:|:---:|:---:|---|
| [Transfer Matrix Method](tmm/) | ✓ | ✓ | ✓ | `Physics-simulations/Cristal_multicapa` (2024) |
| [Hopfield network](hopfield/) | ✓ | ✓ | ✓ | `Optimization-Algorithms/4` (2024) |
| [Multilayer perceptron](mlp/) | ✓ | ✓ | ✓ | `Point_classifier/redNumpy.ipynb` (2024) |
| [Photon transport](photon-transport/) | ✓ | ✓ | ✓ | `Physics-simulations/Iter_rad_material` (2024) |
| [Sampling an energy landscape](sampling/) | ✓ | ✓ | ✓ | new — the bridge the other three point at |
| [Forest fire](forest-fire/) | ✓ | ✓ | ✓ | new — sibling of [`fire-percolation`](https://github.com/FullFran/fire-percolation) |
| [Renormalisation](renormalisation/) | ✓ | ✓ | ✓ | new — acts on `forest-fire/` |
| [Diffusion](diffusion/) | ✓ | ✓ | ✓ | new — where three of the series below converge |

**L1 derive** — I can reconstruct it from the equations.
**L2 implement** — I can write a minimal working version.
**L3 experiment** — I can modify it and predict what happens.

A row only gets a mark when it is true today, not when it once was.

## Series

The map is in the order the entries were built and says nothing about what
leads where. These do.

**Monte Carlo** — estimating by throwing darts, and the $1/\sqrt{N}$ it costs
> [`photon-transport`](photon-transport/) → [`sampling`](sampling/)

**Energy landscapes** — remembering, optimising and sampling are all descent
> [`hopfield`](hopfield/) → [`sampling`](sampling/) → [`diffusion`](diffusion/)

**Learning a function** — gradients, and what you do once you have them
> [`mlp`](mlp/) → [`diffusion`](diffusion/)

**Critical points** — thresholds, and why the details stop mattering there
> [`forest-fire`](forest-fire/) → [`renormalisation`](renormalisation/) → [`diffusion`](diffusion/)

**Waves in matter**
> [`tmm`](tmm/)

Notice `sampling` appears twice and `diffusion` three times. **That is the
reason these are a view and not a directory tree.** Almost every entry belongs
to two or three of these — `hopfield` is a neural network, a spin glass and an
optimiser; `photon-transport` is Monte Carlo and radiation physics — and a
folder forces one parent and hides the rest. The connection worth showing is
often the one across the tree, not down it, which is the whole reason the same
mathematics keeps turning up in unrelated places.

So the directories stay flat and one entry can be in as many series as it
earns. Rule 1 applies here too: a series is allowed to be short, and it is not
allowed to lie, so anything not built says so.

Everything here is also a website, in English and Spanish:
**[www.fullfran.com/first-principles](https://www.fullfran.com/first-principles/)**.
It is generated from these files rather than written alongside them — see
[`site/`](site/) for why, and for what happens when a translation falls behind
the English it was made from.

Repo-wide write-ups live in [`docs/`](docs/) — right now the [physics/numerics
split](docs/architecture.md). Anything specific to one entry lives inside it,
in its own `docs/`: the derivations behind [`tmm/`](tmm/docs/physics.md),
[`hopfield/`](hopfield/docs/model.md), [`mlp/`](mlp/docs/model.md),
[`photon-transport/`](photon-transport/docs/physics.md),
[`sampling/`](sampling/docs/distribution.md),
[`forest-fire/`](forest-fire/docs/lattice.md) and
[`diffusion/`](diffusion/docs/process.md).

All of those except [`tmm/`](tmm/docs/physics.md) carry a history section,
because the people who got stuck on these problems are part of the
explanation. Historical claims are marked **A** (documented, ideally
primary), **B** (a reconstruction) or **C** (told everywhere and
unsourced), following the convention of
[*La servilleta y el ordenador*](https://github.com/FullFran/la-servilleta-y-el-ordenador).

## Anatomy of an entry

```
tmm/
├── README.md        the five questions, derivation included
├── docs/            the long-form derivation, when the entry earns one
├── physics.py       the domain: the equations, and nothing that solves them
├── methods/         one file per algorithm, each importing the domain
├── solve.py         orchestration: validate, dispatch, convert
├── experiments/     things I ran and what they showed
├── tests/           domain laws, plus a contract every method must pass
└── conftest.py      the entry root on sys.path, so the folder stands alone
```

A small enough entry may collapse `methods/` into a single file; none has
needed to yet. The rule that survives either way is the direction of the
arrow: **the equations never import the algorithm.** The payoff is concrete —
swap the algorithm, and every physical law has to keep holding. If it does,
you have separated what nature does from how you chose to compute it. If it
does not, you had physics hiding inside your numerics and did not know.

The README answers five questions in order:

1. What problem does it solve?
2. What are the minimum equations?
3. What did I implement?
4. What did I verify?
5. What did I deliberately leave out?

Question 4 is the one that separates this from a folder of notebooks. Tests
assert properties — energy conservation, known analytic limits, symmetries —
not saved output. Question 5 is the one interviewers actually read.

And a green suite is never a certificate. In `tmm/` it stayed green while two
whole classes of input returned nonsense silently; probing found them, not
reasoning. Every entry records where it stops being right.

## Migration backlog

Audited from GitHub, decided by contents rather than by name.

| Source repo | What's in it | Decision |
|---|---|---|
| [`Physics-simulations/Cristal_multicapa`](https://github.com/FullFran/Physics-simulations) | matrix method, multilayer | **done** → [`tmm/`](tmm/) · source archived |
| `Physics-simulations/Iter_rad_material` | `rayosnew.py`, `unfoton.py` — photons through an absorbing slab | **done** → [`photon-transport/`](photon-transport/) |
| `Physics-simulations/Magnetic Mirrors` | charged particle in a *uniform* field — `B = (0,0,10)`, six ODEs under `odeint`, no bottle and no mirror | **declined** — the contrast worth building was RK4 vs Boris, not the title |
| [`Optimization-Algorithms/4`](https://github.com/FullFran/Optimization-Algorithms) | `hopfiled.py`, Hopfield over thresholded photos | **done** → [`hopfield/`](hopfield/) |
| [`Point_classifier`](https://github.com/FullFran/Point_classifier) | `redNumpy.ipynb`, net in pure NumPy | **done** → [`mlp/`](mlp/) · source archived |
| `Tema-3-...alta-dimensionalidad` + `Optimization-Algorithms/3` | simulated annealing, genetic, TSP — duplicated across two repos | merge into one entry |
| `minimalRandEM` | random-media EM, MATLAB | open it, then decide |
| `Physics-Informed-ML` | `Theory/` + `Examples/` | take the shape, not the content |
| `GPU-accelerated-Ising-Model` | `src/`, `tests/`, `pyproject.toml` | **stays out** — real project, not a sketch |
| `AI-Fundamentals` | Next.js app | **stays out** — no implementations in it |
| `llm-from-scratch` | `clases/`, `examenes/`, `notas/` | study vault; mine `experiments/` only |
| `computational_photonics` | died at `1_slab_waveguides` | nothing to rescue |

Migration is only finished when the source repo is archived on GitHub **and**
carries a README pointing here. An archived repo with broken code and no
signpost is a trap, not an archive. Otherwise the count of scattered repos
goes up, not down.

## Not in here

Research projects that *consume* this knowledge live in their own repos and
keep their own standards — `snow-mcrt`, `fire-percolation`, `corona26`,
ForgePhoton. The relationship is one-way:

```
first-principles  ──reads──▶  me  ──builds──▶  real projects
```

Never an import.

## Run

```bash
uv run pytest tmm                                  # one entry
uv run pytest hopfield
uv run pytest mlp
uv run pytest photon-transport
uv run pytest sampling
uv run pytest forest-fire
uv run pytest renormalisation
uv run pytest diffusion
./run-tests                                        # all of them, one process each
```

One session per entry, deliberately. Entries are standalone, so more than one
of them defines `solve` and `methods`; put two on `sys.path` at once and the
first import wins silently. Running them separately is the price of being able
to copy a folder out and have it work.
