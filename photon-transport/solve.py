"""Run photons and report a number with an error bar on it.

Owns the run, not the physics: it draws directions, hands them to an estimator,
and turns the per-photon contributions into a mean and its uncertainty.

The uncertainty is not decoration. A Monte Carlo result without one is not a
measurement -- it is a number that happens to have come out of a computer, and
there is no way to tell whether a disagreement with theory is a bug or the
sample size. The 2024 version returned `len(passed)/Nphoto` and nothing else.
"""

from dataclasses import dataclass

import numpy as np

import physics
from methods import ALL as METHODS

__all__ = ["transmitted", "Estimate", "METHODS", "DEFAULT_METHOD"]

DEFAULT_METHOD = "analog"


@dataclass(frozen=True)
class Estimate:
    value: float
    error: float
    photons: int
    method: str

    def __str__(self):
        return f"{self.value:.6f} +- {self.error:.6f}  ({self.method}, {self.photons} photons)"

    def sigma_from(self, reference):
        """How many standard errors away a reference value sits.

        A zero-variance estimator makes the raw ratio meaningless, and that is
        not hypothetical: the weighted estimator on a collimated beam gives
        every photon the same contribution, so the standard error is float
        noise rather than a spread. Dividing by it turned a difference of
        0.2 ulp into 447 sigma -- the better the estimator, the more brittle a
        "within three sigma" check becomes.

        The floor is what the arithmetic can actually resolve at this value, so
        an exact estimator is compared against machine precision instead.
        """
        floor = np.finfo(float).eps * max(abs(self.value), 1.0)
        return abs(self.value - reference) / max(self.error, floor)


def transmitted(mu, thickness, half_angle=0.0, photons=100_000,
                method=DEFAULT_METHOD, seed=0):
    """The fraction of emitted photons that cross the slab, with its error.

    The error is the standard error of the mean, sigma/sqrt(N). It shrinks as
    1/sqrt(N) whatever the estimator, which is the central fact of Monte Carlo:
    one more digit of precision costs a hundred times the work.
    """
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}; available: {sorted(METHODS)}")
    if photons < 2:
        raise ValueError("need at least two photons to estimate a spread")
    physics.check_medium(mu, thickness)
    physics.check_cone(half_angle)

    rng = np.random.default_rng(seed)
    cos_theta, _ = physics.sample_direction(rng, photons, half_angle)
    weights = METHODS[method].contributions(rng, cos_theta, mu, thickness)

    return Estimate(
        value=float(np.mean(weights)),
        error=float(np.std(weights, ddof=1) / np.sqrt(photons)),
        photons=photons,
        method=method,
    )
