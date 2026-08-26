"""Build the map, find where it stands still, and read the exponent off it.

Owns the two ways of asking the map a question, not the map itself.

`scheme` is the textbook version: coarse-grain a block of b sites down to one,
find p* where R(p) = p, and take the exponent from the slope there.

`cell_to_cell` is the same idea done better, and the entry exists partly to
show why it is needed. Mapping a block to a single *site* compares a lattice
with a lattice of a different kind, and the mismatch does not go away as the
block grows -- measured, the fixed point of the plain scheme is stuck around
0.62 from b = 2 to b = 4. Comparing two *blocks* of different size cancels most
of it, because both sides of the comparison are the same kind of object.
"""

from dataclasses import dataclass

import numpy as np

import flow
from methods import ALL as METHODS

__all__ = ["scheme", "cell_to_cell", "Scheme", "Comparison",
           "METHODS", "DEFAULT_METHOD"]

DEFAULT_METHOD = "enumeration"


@dataclass(frozen=True)
class Scheme:
    size: int
    rule: str
    method: str
    polynomial: np.ndarray
    fixed_point: float
    derivative: float
    exponent: float

    def coarse(self, p):
        return flow.recursion(self.polynomial, self.size)(np.asarray(p, dtype=float))

    def error_in_threshold(self):
        return abs(self.fixed_point - flow.P_C) / flow.P_C

    def error_in_exponent(self):
        return abs(self.exponent - flow.NU) / flow.NU


@dataclass(frozen=True)
class Comparison:
    sizes: tuple
    rule: str
    method: str
    fixed_point: float
    exponent: float

    def error_in_threshold(self):
        return abs(self.fixed_point - flow.P_C) / flow.P_C

    def error_in_exponent(self):
        return abs(self.exponent - flow.NU) / flow.NU


def _polynomial(size, rule, method, **options):
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}; available: {sorted(METHODS)}")
    flow.check_block(size)
    flow.check_rule(rule)
    return METHODS[method].polynomial(size, rule, **options)


def scheme(size=2, rule="either", method=DEFAULT_METHOD, **options):
    """Coarse-grain a block down to one site and read off the critical point."""
    polynomial = _polynomial(size, rule, method, **options)
    coarse = flow.recursion(polynomial, size)
    point = flow.fixed_point(coarse)
    derivative = flow.slope(coarse, point)
    return Scheme(size=size, rule=rule, method=method, polynomial=polynomial,
                  fixed_point=point, derivative=derivative,
                  exponent=flow.exponent(size, derivative))


def cell_to_cell(small=3, large=4, rule="either", method=DEFAULT_METHOD, **options):
    """Solve R_small(p) = R_large(p) instead of R(p) = p.

    Both sides are blocks, so whatever the block rule gets wrong about being a
    lattice site cancels to leading order. The exponent then comes from the
    ratio of the two slopes at the common point:

        nu = ln(large / small) / ln(slope_large / slope_small)
    """
    if small >= large:
        raise ValueError(f"the second block must be larger, got {small} and {large}")
    first = flow.recursion(_polynomial(small, rule, method, **options), small)
    second = flow.recursion(_polynomial(large, rule, method, **options), large)

    def gap(p):
        return float(first(np.array(p)) - second(np.array(p)))

    low, high = 0.05, 0.98
    if gap(low) * gap(high) > 0:
        raise ValueError("the two block sizes do not cross in [0.05, 0.98]")
    while high - low > 1e-12:
        middle = 0.5 * (low + high)
        if gap(middle) * gap(low) > 0:
            low = middle
        else:
            high = middle
    point = 0.5 * (low + high)

    slopes = (flow.slope(first, point), flow.slope(second, point))
    if min(slopes) <= 0 or abs(slopes[1] - slopes[0]) < 1e-12:
        raise ValueError("the two slopes do not separate; no exponent to read")
    return Comparison(sizes=(small, large), rule=rule, method=method,
                      fixed_point=point,
                      exponent=float(np.log(large / small)
                                     / np.log(slopes[1] / slopes[0])))
