"""Estimators for the same transmitted fraction.

A method exposes NAME and contributions(rng, cos_theta, mu, thickness), which
returns one number in [0, 1] per photon. The mean of those numbers estimates
the transmitted fraction and their spread is its uncertainty, so the caller
never needs to know which estimator produced them.

Both methods here are unbiased and one of them is enormously cheaper for the
same error bar. That is a property of the estimator, not of the physics.
"""

from . import analog, weighted

ALL = {module.NAME: module for module in (analog, weighted)}
