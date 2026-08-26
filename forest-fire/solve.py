"""Run the model and report one fire per fire.

Owns the timestep loop and the bookkeeping, not the rules. Its one real design
decision is in `step`: lightning is drawn over the whole lattice at once, and
each struck site that is still standing gets its **own** fire event.

That matters more than it looks. The expected number of strikes in a step is
f * density * L^2, which grows with the area, so on a large lattice several
strikes per step is the common case rather than a rare one. Burning them all
in one call and reporting the total merges independent fires into one event,
and inflates the size distribution by an amount that grows with L -- which is
exactly the variable a finite-size study is trying to isolate.
"""

from dataclasses import dataclass

import numpy as np

import lattice
from methods import ALL as METHODS

__all__ = ["run", "Fire", "Run", "METHODS", "DEFAULT_METHOD"]

DEFAULT_METHOD = "instantaneous"


@dataclass(frozen=True)
class Fire:
    size: int
    density_before: float
    step: int


@dataclass(frozen=True)
class Run:
    fires: list
    density: float
    grid: np.ndarray
    steps: int
    method: str

    @property
    def sizes(self):
        return np.array([fire.size for fire in self.fires], dtype=float)

    @property
    def largest(self):
        return int(self.sizes.max()) if self.fires else 0


def step(grid, p, f, rng, solver, index):
    """One growth round, then every strike as its own fire."""
    lattice.grow(grid, p, rng)
    struck = lattice.strike(grid, f, rng)
    fires = []
    for row, column in zip(*np.where(struck)):
        if grid[row, column] != lattice.TREE:
            continue                      # an earlier fire this step took it
        before = lattice.density(grid)
        seed = np.zeros(grid.shape, dtype=bool)
        seed[row, column] = True
        size = solver.burn(grid, seed, rng, p)
        if size:
            fires.append(Fire(size=size, density_before=before, step=index))
    return fires


def run(size=96, p=0.05, f=1e-3, steps=4000, method=DEFAULT_METHOD, seed=0,
        burn_in=0.25):
    """Run the model and return the fires, with the burn-in discarded.

    The burn-in is a confession. Starting from bare ground the first fires are
    small because there is nothing to burn, and counting them drags every
    statistic downward.
    """
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}; available: {sorted(METHODS)}")
    if steps < 1:
        raise ValueError(f"steps must be at least one, got {steps}")
    if not 0.0 <= burn_in < 1.0:
        raise ValueError(f"burn_in must be a fraction in [0, 1), got {burn_in}")
    lattice.check_rates(p, f)

    rng = np.random.default_rng(seed)
    grid = lattice.empty_grid(size)
    solver = METHODS[method]

    skip = int(burn_in * steps)
    fires, densities = [], []
    for index in range(steps):
        found = step(grid, p, f, rng, solver, index)
        if index >= skip:
            fires.extend(found)
            densities.append(lattice.density(grid))

    return Run(fires=fires, density=float(np.mean(densities)) if densities else 0.0,
               grid=grid, steps=steps, method=method)
