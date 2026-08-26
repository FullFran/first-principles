"""Simulate what a photon does. Sample a free path; it gets through or it does not.

This is analog Monte Carlo: every random number stands for something that
physically happens, and the answer is a count of survivors. It is the estimator
the 2024 version used and the one everybody writes first, because it is the
literal translation of the process.

Its cost is that each photon reports one bit. A photon that is absorbed tells
you only that it was absorbed, and the resulting estimate carries the full
binomial noise of a coin flip -- variance T(1-T), no matter how narrow the
beam or how well you understand the geometry.
"""

import numpy as np

from physics import sample_free_path, slab_path

NAME = "analog"


def contributions(rng, cos_theta, mu, thickness):
    cos_theta = np.asarray(cos_theta, dtype=float)
    path = slab_path(cos_theta, thickness)
    free = sample_free_path(rng, cos_theta.size, mu)
    return (free > path).astype(float)
