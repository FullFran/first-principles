# Separating physics from numerics

> The equations are the invariant. The algorithm is a choice. Put them in
> different files and make the arrow point one way.

This is the architecture every entry in this repo follows. It is written down
because it survived contact with a real rewrite — and because, as it turns
out, it is not original. Half of computational science already works this way
under other names, and the [prior art](#prior-art) is worth reading.

## The rule

```
methods/ imports the domain.        The domain imports nobody.
```

One arrow, no exceptions. Everything below is a consequence.

## The shape

```
entry/
├── physics.py       the domain: the equations and their invariants
├── methods/         one file per algorithm, each importing the domain
│   ├── method_a.py
│   └── method_b.py
├── solve.py         orchestration: validate, dispatch, convert
└── tests/
    ├── test_physics.py         domain laws, no solver involved
    ├── test_methods.py         the contract, run against every method
    └── test_methods_agree.py   the methods cross-checked
```

A method receives quantities the domain already computed and returns the raw
result. It never re-derives physics on the side. Small entries collapse
`methods/` into one file; the arrow is what has to survive, not the folder
count.

## Why it pays: the swap test

Rearranging files buys nothing on its own. What buys something is this:

> **Swap the algorithm. Every physical law must still hold.**

If they do, you have separated what nature does from how you chose to compute
it. If one breaks, you had physics hiding inside your numerics and did not
know — which is the actual failure this architecture exists to catch, and it
is invisible in a monolithic file.

The corollary is the honest test of whether you understood the material at
all. Anyone can implement one algorithm and match a reference plot. Getting
two unrelated algorithms to agree to 1e-13 requires knowing which parts were
physics.

## The boundary is a test, not a folder

This is the part people skip. Directory structure enforces nothing. What makes
the boundary real is that **every method has to pass the same suite**:

```python
# tests/test_methods.py
from methods import ALL as METHODS

pytestmark = pytest.mark.parametrize("method", sorted(METHODS))
```

Register a new algorithm and it inherits the contract automatically. A method
that quietly assumes something physical will fail a law it never mentioned.

Without this, `physics.py` and `methods/` are two folders with a naming
convention between them.

## Where the line goes

The ambiguous cases are where the pattern earns its keep. The question that
resolves nearly all of them:

> **Would this change if I picked a different algorithm?** If no, it is domain.

| Concern | Side | Why |
|---|---|---|
| Governing equations, constitutive relations | domain | The statement about nature |
| Boundary and initial conditions | domain | Part of the problem, not the solution |
| Conservation laws, symmetries, invariants | domain | True regardless of how you integrate |
| Units and non-dimensionalisation | domain | Changes the equations, not the arithmetic |
| Branch cuts fixed by causality or passivity | domain | A physical requirement wearing numerical clothes |
| Validation of admissible inputs | domain | Passivity, positivity, thermodynamic bounds |
| Discretisation, integration scheme, step control | method | Pure choice |
| Convergence tolerance, iteration caps | method | Approximation budget |
| Overflow guards, reordering for stability | method | Artefacts of finite precision |
| Proposal distribution in Monte Carlo | method | Any ergodic proposal works |
| Acceptance criterion in Metropolis | domain | It *is* the Boltzmann distribution |
| Plotting, sweeps, file output | neither | Experiments, outside both |

That last pair is the sharpest illustration. In Metropolis Monte Carlo the
proposal is free and the acceptance ratio is not — moving the acceptance rule
into the sampler is exactly the mistake this layout is designed to make
obvious.

### Worked examples

| Entry | Domain | Methods |
|---|---|---|
| Transfer matrix | Snell, Fresnel, phase, energy flux | matrix product · Rouard recursion |
| Hopfield network | energy function, update rule | synchronous · asynchronous |
| DDPM | forward/reverse process, the loss | ancestral sampler · DDIM |
| Ising model | Hamiltonian, Boltzmann weight | Metropolis · Wolff cluster |
| N-body | gravitational force, energy | velocity Verlet · RK4 · symplectic |

The split is always the same sentence: **the equations, versus the algorithm
that discretises them.**

## Prior art

The idea is not new, and pretending otherwise would be the opposite of what
this repo is for. It shows up in at least four literatures that mostly do not
cite each other.

**Separation of concerns in scientific computing.** The general principle,
stated most directly in the theory-software translation literature: software
must separate the scientific question, the equations, the numerical methods
that solve them, and the infrastructure underneath — and the standard failure
mode is that it does not.
([Theory-Software Translation, arXiv:1910.09902](https://arxiv.org/pdf/1910.09902) ·
[On the Role of Mathematical Abstractions for Scientific Computing](https://link.springer.com/chapter/10.1007/978-0-387-35407-1_9))

**FEniCS, Firedrake and UFL.** The industrial-strength version. UFL declares
the variational form in near-mathematical notation — the physics — while a
form compiler and runtime own discretisation and execution. Firedrake's own
paper frames its contribution as "a more complete separation of concerns"
between numerical analysts and application specialists.
([Firedrake, arXiv:1501.01809](https://arxiv.org/abs/1501.01809) ·
[The FEniCS Project](https://www.siam.org/publications/siam-news/articles/the-fenics-project/))

**`scipy.integrate.solve_ivp`.** The version everyone has already used without
naming it: you hand it the ODE (domain) and pick `method="RK45"`, `"Radau"`,
`"BDF"`, `"LSODA"` (algorithm). `extensisq` extends it by passing a custom
`OdeSolver` — an open port in everything but vocabulary.
([SciPy docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) ·
[extensisq](https://pypi.org/project/extensisq/0.0.2/))

**Weather and climate models.** LFRic separates the science code from the
parallelisation and optimisation layer so the same physics survives changing
hardware.
([LFRic, arXiv:1809.07267](https://arxiv.org/pdf/1809.07267))

And the closest match, published July 2026: a framework proposing exactly this
physical-domain / numerical-method layering **for computational physics
education**, on the argument that monolithic code hides where domain knowledge
ends and computational strategy begins.
([Physical Systems as Objects, arXiv:2607.03457](https://arxiv.org/pdf/2607.03457))

## The testing half already has a name too

The split is not only structural — it is the standard epistemology of
computational science, where the two halves are called verification and
validation:

> **Verification** — am I solving the equations right? (numerics)
> **Validation** — am I solving the right equations? (physics)

The phrasing is Roache's, formalised in ASME V&V 10 (solid mechanics, 2006)
and V&V 20 (CFD and heat transfer).
([Roache, *Verification and Validation in Computational Science and Engineering*](https://www.amazon.com/Verification-Validation-Computational-Science-Engineering/dp/0913478083) ·
[ASME V&V 10](https://www.asme.org/codes-standards/find-codes-standards/standard-for-verification-and-validation-in-computational-solid-mechanics) ·
[ASME V&V 20 overview](https://www.semanticscholar.org/paper/An-Overview-of-ASME-V&V-20:-Standard-for-and-in-and-Coleman/5a2b34af86de4fac220df0f697b1afbe8bc24340))

Which is the whole point of the file split: `test_physics.py` and
`test_methods.py` are that distinction made structural, so a failure tells you
which of the two questions you got wrong.

Two more techniques from that literature map onto what small entries can
actually afford:

- **Exact and manufactured solutions.** MMS is described as the most rigorous
  code verification technique available; where a closed form already exists,
  use it directly. In `tmm/` those are the Fresnel coefficients, the Airy
  single-film formula and the quarter-wave admittance transform.
  ([MMS for code verification](https://link.springer.com/chapter/10.1007/978-3-319-70766-2_12) ·
  [Exact solutions, in *Verification and Validation in Scientific Computing*](https://www.cambridge.org/core/books/abs/verification-and-validation-in-scientific-computing/exact-solutions/DFB030CD8A8334FA13DF3B2A627964E4))
- **Code-to-code comparison.** Cross-checking independent implementations —
  what `test_methods_agree.py` does.

## Honest limits

**Two methods agreeing proves consistency, not correctness.** The V&V
literature is explicit that a strict hierarchy matters, precisely to avoid
being misled by fortuitous agreement between flawed implementations. Both of
this repo's solvers import the same `physics.py`; a wrong equation there would
be reproduced identically by both, to 1e-13, with the suite fully green. That
is why the domain tests against closed forms carry more weight than the
agreement test, and why the agreement test is listed last rather than first.

**An abstraction with one implementation is speculation.** Do not build
`methods/` on the theory that a second algorithm might arrive. In `tmm/` the
second one was earned by a measured defect: the transfer matrix overflows to
NaN past roughly 20 µm of metal and the recursion does not. Until something
like that shows up, one file is the right answer.

**Ceremony is the failure mode.** No entities, no use-case layer, no
dependency injection, no value object wrapping a complex number. This repo
caps a core at 500 lines, and a 150-line mechanism spread across twelve files
of interfaces has lost more than it gained. Take the dependency rule; leave
the architecture-astronaut apparatus.
