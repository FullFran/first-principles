# first-principles

Minimal implementations, rebuilt from the equations.

Every entry here exists to prove I understand a mechanism — not to compete
with a production library. If you need a transfer matrix solver, install
`tmm`. If you want to see whether I can derive one, read `tmm/core.py`.

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

## Map

| Topic | Derive | Implement | Experiment | Origin |
|---|:---:|:---:|:---:|---|
| [Transfer Matrix Method](tmm/) | ✓ | ✓ | ✓ | `Physics-simulations/Cristal_multicapa` (2024) |

**L1 derive** — I can reconstruct it from the equations.
**L2 implement** — I can write a minimal working version.
**L3 experiment** — I can modify it and predict what happens.

A row only gets a mark when it is true today, not when it once was.

## Anatomy of an entry

```
tmm/
├── README.md        the five questions, derivation included
├── core.py          the mechanism, nothing else
├── experiments/     things I ran and what they showed
└── tests/           properties the physics guarantees
```

The README answers five questions in order:

1. What problem does it solve?
2. What are the minimum equations?
3. What did I implement?
4. What did I verify?
5. What did I deliberately leave out?

Question 4 is the one that separates this from a folder of notebooks. Tests
assert properties — energy conservation, known analytic limits, symmetries —
not saved output. Question 5 is the one interviewers actually read.

## Migration backlog

Audited from GitHub, decided by contents rather than by name.

| Source repo | What's in it | Decision |
|---|---|---|
| `Physics-simulations/Cristal_multicapa` | matrix method, multilayer | **done** → [`tmm/`](tmm/) |
| `Physics-simulations/Iter_rad_material` | `rayosnew.py`, `unfoton.py` — photon transport by ray tracing | queued — feeds the same intuition as `snow-mcrt` |
| `Physics-simulations/Magnetic Mirrors` | charged particle in a magnetic bottle | queued — Boris pusher from the Lorentz force |
| `Point_classifier` | `redNumpy.ipynb`, net in pure NumPy | next — MLP from backprop |
| `Tema-3-...alta-dimensionalidad` + `Optimization-Algorithms/3` | simulated annealing, genetic, TSP — duplicated across two repos | merge into one entry |
| `minimalRandEM` | random-media EM, MATLAB | open it, then decide |
| `Physics-Informed-ML` | `Theory/` + `Examples/` | take the shape, not the content |
| `GPU-accelerated-Ising-Model` | `src/`, `tests/`, `pyproject.toml` | **stays out** — real project, not a sketch |
| `AI-Fundamentals` | Next.js app | **stays out** — no implementations in it |
| `llm-from-scratch` | `clases/`, `examenes/`, `notas/` | study vault; mine `experiments/` only |
| `computational_photonics` | died at `1_slab_waveguides` | nothing to rescue |

Migration is only finished when the source repo is archived on GitHub.
Otherwise the count of scattered repos goes up, not down.

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
uv run pytest              # every entry
uv run pytest tmm          # one entry
```
