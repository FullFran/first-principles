"""The domain: what you are trying to sample from, and what counts as right.

An energy, the density it defines, and the closed forms that density implies.
No chain, no proposal, no step size -- those are choices, and they live in
`methods/` and `solve.py`.

    methods/ imports distribution.        distribution imports nobody.

Conventions
-----------
state       an array of shape (dim,) -- always, even in one dimension
batch       an array of shape (n, dim)
energy      sums over the last axis, so it maps either shape to a scalar or
            to (n,) with no branch on dimensionality

The whole subject exists because of one asymmetry. Given an energy E you can
evaluate it anywhere, and the density it defines

    p(x) = exp(-E(x)/T) / Z,      Z = integral of exp(-E/T) over everything

needs Z, which is an integral over the whole space. In any interesting number
of dimensions Z is unobtainable. So you can compute *ratios* of probabilities
and never a probability, and every method in `methods/` is a way of living
with exactly that.
"""

from dataclasses import dataclass

import numpy as np

__all__ = [
    "Target", "FREE", "GAUSSIAN", "DOUBLE_WELL", "TARGETS",
    "boltzmann_weight", "exact_moment", "exact_probability",
    "check_temperature",
]


@dataclass(frozen=True)
class Target:
    """An energy and its gradient. Everything else is derived from these two.

    `gradient` is what Langevin needs and Metropolis never asks for, which is
    the whole difference between them: one needs to know which way is downhill
    and the other only needs to compare two heights.
    """
    name: str
    energy: callable
    gradient: callable
    support: tuple = (-6.0, 6.0)
    """Where the quadrature reference integrates. It has to be wide enough that
    truncation is far below the error a chain will ever have: at +-6 the
    Gaussian reference was already wrong in the fourth decimal at T = 2."""


def check_temperature(temperature):
    """T = 0 is not a distribution. It is a delta on the minimum, and the
    dynamics that samples it is the descent in `hopfield/` and `mlp/`."""
    if temperature <= 0:
        raise ValueError(
            f"temperature must be positive, got {temperature}; at T = 0 the "
            "Boltzmann density is a delta on the minimum, not something to sample")


# --- the targets ------------------------------------------------------------

FREE = Target(
    name="free",
    energy=lambda x: np.zeros_like(np.asarray(x, dtype=float)),
    gradient=lambda x: np.zeros_like(np.asarray(x, dtype=float)),
    support=(-40.0, 40.0),
)
"""No energy at all. Langevin on this is pure Brownian motion, so the mean
square displacement grows as 2*T*t and the continuum limit is the diffusion
equation. It has no stationary distribution -- the walker never settles -- and
that is the point: it is the bridge, not a target."""

GAUSSIAN = Target(
    name="gaussian",
    energy=lambda x: 0.5 * np.sum(np.asarray(x, dtype=float) ** 2, axis=-1),
    gradient=lambda x: np.asarray(x, dtype=float),
    support=(-14.0, 14.0),
)
"""E = x^2/2 at T = 1 is the unit normal, whose every moment is known. The one
target where a sampler cannot hide."""

_TILT = 0.30

DOUBLE_WELL = Target(
    name="double_well",
    energy=lambda x: np.sum(
        (np.asarray(x, dtype=float) ** 2 - 1.0) ** 2
        - _TILT * np.asarray(x, dtype=float), axis=-1),
    gradient=lambda x: 4.0 * np.asarray(x, dtype=float)
    * (np.asarray(x, dtype=float) ** 2 - 1.0) - _TILT,
    support=(-2.5, 2.5),
)
"""Two minima separated by a barrier, tilted so the right one is lower. The
populations are exactly computable at any temperature, and a chain that never
crosses the barrier gets them exactly wrong while reporting nothing unusual."""

TARGETS = {t.name: t for t in (FREE, GAUSSIAN, DOUBLE_WELL)}


# --- the density, and what it implies ---------------------------------------

def boltzmann_weight(target, x, temperature):
    """exp(-E/T), the unnormalised density. Z is deliberately absent."""
    check_temperature(temperature)
    return np.exp(-target.energy(x) / temperature)


def _grid(target, nodes=400_001):
    """One-dimensional quadrature nodes, shaped (nodes, 1) to match a batch."""
    return np.linspace(target.support[0], target.support[1], nodes)[:, None]


def exact_moment(target, temperature, power=2, nodes=400_001):
    """<x^n> under the Boltzmann density, by quadrature in one dimension.

    Available here and nowhere real: normalising costs an integral over the
    whole space, which is the reason sampling exists. Having it for these
    targets is what turns "the chain looks converged" into a measurement.
    """
    check_temperature(temperature)
    grid = _grid(target, nodes)
    axis = grid[:, 0]
    weight = np.exp(-target.energy(grid) / temperature)
    return float(np.trapezoid(axis ** power * weight, axis)
                 / np.trapezoid(weight, axis))


def exact_probability(target, temperature, low=0.0, high=np.inf, nodes=400_001):
    """P(low < x < high) under the Boltzmann density, by quadrature.

    The sub-interval gets its own grid rather than a mask on the full one. A
    mask multiplies the integrand by a step, and a discontinuity drops the
    trapezoid rule from second order to first: masking put the symmetric
    Gaussian's P(x > 0) at 0.499986 instead of 0.5. A reference is only worth
    having while it is more accurate than everything it judges.
    """
    check_temperature(temperature)
    full = _grid(target, nodes)
    axis = full[:, 0]
    total = np.trapezoid(np.exp(-target.energy(full) / temperature), axis)

    start = max(low, target.support[0])
    stop = min(high, target.support[1])
    if stop <= start:
        return 0.0
    inside = np.linspace(start, stop, nodes)[:, None]
    part = np.trapezoid(np.exp(-target.energy(inside) / temperature), inside[:, 0])
    return float(part / total)
