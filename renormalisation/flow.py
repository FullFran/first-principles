"""The domain: what coarse-graining does to a parameter.

A rule for when a block of sites counts as occupied, the map from the fine
density to the coarse one, and the fixed points of that map. No estimator, no
sampling, no block-size sweep -- those are choices, and they live in `methods/`
and `solve.py`.

    methods/ imports flow.        flow imports nobody.

The idea in one line: zoom out, and ask what the system looks like at the new
scale. If the answer has the same form with a different parameter, you have a
map p -> R(p), and everything about the critical point is a property of that
map rather than of any particular lattice.
"""

import numpy as np

__all__ = [
    "P_C", "NU", "RULES", "spans", "block_polynomial", "recursion",
    "fixed_point", "slope", "exponent", "check_block", "check_rule",
]

P_C = 0.5927460
"""Site percolation threshold on a square lattice. Known numerically, no closed
form, and the number this entry is trying to produce out of small blocks."""

NU = 4.0 / 3.0
"""Correlation-length exponent for 2D percolation. Exact, from conformal field
theory, and the second number to check against.

It is the more demanding of the two. A fixed point can land near p_c for
uninteresting reasons; the exponent comes from the *derivative* there and is
much harder to get by accident."""

RULES = ("vertical", "either", "both")
"""When does a coarse block count as occupied?

There is no single right answer, and that is not a defect -- it is the
statement that a renormalisation scheme is a *choice*, and different choices
approach the same fixed point differently. `vertical` asks for a top-to-bottom
path, `either` for a path in one direction or the other, `both` for paths in
both. Measured, the three do not converge alike: see the entry's experiments.
"""


def check_block(size):
    if size < 2:
        raise ValueError(f"a block needs at least two sites a side, got {size}")


def check_rule(rule):
    if rule not in RULES:
        raise ValueError(f"unknown rule {rule!r}; available: {list(RULES)}")


# --- the block rule ---------------------------------------------------------

def _reaches(block, start):
    frontier = start & block
    seen = frontier.copy()
    while frontier.any():
        nearby = np.zeros_like(frontier)
        nearby[1:] |= frontier[:-1]
        nearby[:-1] |= frontier[1:]
        nearby[:, 1:] |= frontier[:, :-1]
        nearby[:, :-1] |= frontier[:, 1:]
        frontier = nearby & block & ~seen
        seen |= frontier
    return seen


def spans(block, rule="either"):
    """Does this block of occupied sites count as occupied at the coarse scale?

    Connection is what survives coarse-graining -- a block that is full of
    trees but disconnected does not conduct, and the whole point of the map is
    to track whether things connect. Which is why the criterion is spanning and
    not, say, the majority of sites.
    """
    check_rule(rule)
    block = np.asarray(block, dtype=bool)
    size = block.shape[0]

    top = np.zeros(block.shape, dtype=bool)
    top[0] = True
    vertical = bool(_reaches(block, top)[-1].any())
    if rule == "vertical":
        return vertical

    left = np.zeros(block.shape, dtype=bool)
    left[:, 0] = True
    horizontal = bool(_reaches(block, left)[:, -1].any())
    return (vertical or horizontal) if rule == "either" else (vertical and horizontal)


# --- the map ----------------------------------------------------------------

def recursion(polynomial, size):
    """Turn a count of spanning configurations into the map R(p).

    A block of `size` squared sites with exactly k occupied happens with
    probability p^k (1-p)^(n-k), so

        R(p) = sum over k of  (spanning configurations with k occupied) p^k (1-p)^(n-k)

    R is a polynomial of degree n. That is the entire renormalisation group for
    this problem: one polynomial, and every question below is a question about
    it.
    """
    polynomial = np.asarray(polynomial, dtype=float)
    total = size * size
    if polynomial.shape != (total + 1,):
        raise ValueError(f"a {size}x{size} block needs {total + 1} coefficients, "
                         f"got {polynomial.shape[0]}")
    powers = np.arange(total + 1)

    def coarse(p):
        p = np.asarray(p, dtype=float)
        return np.sum(polynomial * p[..., None] ** powers
                      * (1.0 - p[..., None]) ** (total - powers), axis=-1)
    return coarse


def block_polynomial(size, rule="either"):
    """Spanning configurations by occupied count, by exhaustive enumeration.

    Exact and 2^(size^2) work: fine to size 4, hopeless by size 5. The
    alternative is in `methods/`.
    """
    import itertools
    check_block(size)
    check_rule(rule)
    total = size * size
    counts = np.zeros(total + 1, dtype=np.int64)
    for configuration in itertools.product([False, True], repeat=total):
        block = np.array(configuration).reshape(size, size)
        if spans(block, rule):
            counts[int(block.sum())] += 1
    return counts


# --- what the map says ------------------------------------------------------

def fixed_point(coarse, low=0.05, high=0.98, tolerance=1e-12):
    """Where R(p) = p, other than the trivial p = 0 and p = 1.

    The unstable one. Below it, coarse-graining drives the density to zero and
    the system looks empty at large scales; above it, to one, and it looks
    solid. Only exactly at the fixed point does it look the same at every
    scale, which is what "scale invariance at a critical point" means.
    """
    def gap(p):
        return float(coarse(np.array(p))) - p
    if gap(low) * gap(high) > 0:
        raise ValueError(f"no fixed point bracketed in [{low}, {high}]")
    while high - low > tolerance:
        middle = 0.5 * (low + high)
        if gap(middle) * gap(low) > 0:
            low = middle
        else:
            high = middle
    return 0.5 * (low + high)


def slope(coarse, p, step=1e-6):
    """dR/dp. The rate at which coarse-graining pushes you away from the
    fixed point, and the only thing the exponent depends on."""
    return float((coarse(np.array(p + step)) - coarse(np.array(p - step))) / (2 * step))


def exponent(scale, derivative):
    """The correlation-length exponent from the flow.

    Near the fixed point, one coarse-graining step multiplies the distance from
    it by lambda = dR/dp while dividing lengths by the block size b. The
    correlation length must transform as xi -> xi/b, so if xi ~ |p - p*|^(-nu)
    then b^(-1) = lambda^(-nu), giving

        nu = ln(b) / ln(lambda)

    An exponent out of a derivative. Nothing about the microscopic lattice
    survives into it, which is what universality is.
    """
    if scale <= 1:
        raise ValueError(f"the block must actually coarsen, got scale {scale}")
    if derivative <= 1:
        raise ValueError(
            f"the fixed point must be unstable, got dR/dp = {derivative}; "
            "a stable one is not a critical point")
    return float(np.log(scale) / np.log(derivative))
