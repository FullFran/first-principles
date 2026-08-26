"""Never absorb a photon. Carry its survival probability instead.

The free path is only ever used to ask one question -- did it exceed the slab
path? -- and that question has a known answer in expectation:

    P(free path > slab path) = exp(-mu * slab_path)

So integrate it analytically rather than sampling it. Each photon contributes
its exact survival probability, and the estimator is unbiased because the mean
of the indicator was that probability all along.

This is implicit capture, and it is what every serious transport code does.
What it buys is the removal of one whole source of randomness: the only
variance left is the spread of path lengths across the cone. Collimate the
beam and there is nothing left to be uncertain about -- the estimator becomes
exact while the analog one still flips coins.

The catch is that it only works while the path through the medium is known in
advance, which is true here because nothing scatters. Add scattering and the
path becomes a random walk, and this shortcut has to be earned again.
"""

import numpy as np

from physics import slab_path

NAME = "weighted"


def contributions(rng, cos_theta, mu, thickness):
    cos_theta = np.asarray(cos_theta, dtype=float)
    return np.exp(-mu * slab_path(cos_theta, thickness))
