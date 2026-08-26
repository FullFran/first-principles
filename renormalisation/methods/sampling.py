"""Estimate the same count, at a block size enumeration cannot reach.

The trick is what to sample. Drawing blocks at density p and counting spanning
ones estimates R(p) at that one p, and you would have to redo it for every p.

Instead sample *at fixed occupancy*: among the C(n, k) configurations with
exactly k sites occupied, what fraction spans? That is one number per k, it is
independent of p, and multiplying by C(n, k) gives the same coefficients
enumeration produces. One set of samples, and the whole polynomial.

The cost is a statistical error on every coefficient, and the benefit is that
C(n, k) is a binomial coefficient rather than something you have to walk
through -- so a block of six a side is the same work as a block of three.
"""

from math import comb

import numpy as np

from flow import spans

NAME = "sampling"


def polynomial(size, rule="either", draws=4000, seed=0, **_):
    total = size * size
    rng = np.random.default_rng(seed)
    counts = np.zeros(total + 1, dtype=float)

    for occupied in range(total + 1):
        if occupied == 0:
            continue
        if occupied == total:
            counts[occupied] = 1.0                    # the full block always spans
            continue
        hits = 0
        for _ in range(draws):
            flat = np.zeros(total, dtype=bool)
            flat[rng.choice(total, size=occupied, replace=False)] = True
            hits += spans(flat.reshape(size, size), rule)
        counts[occupied] = comb(total, occupied) * hits / draws
    return counts
