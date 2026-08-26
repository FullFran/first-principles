"""Where the two ways of counting part company.

They compute the same coefficients and agree wherever both can run. What
differs is that one of them stops.
"""

import numpy as np
import pytest

import flow
import solve
from methods import ALL as METHODS


def test_they_agree_wherever_both_can_run():
    """Same rule, same block, one exact and one sampled. If these ever drift
    apart the sampler is not sampling what it thinks it is."""
    for size in (2, 3, 4):
        exact = solve.scheme(size, "either", "enumeration")
        sampled = solve.scheme(size, "either", "sampling", draws=3000, seed=0)
        assert abs(exact.fixed_point - sampled.fixed_point) < 0.02


def test_enumeration_is_exactly_reproducible_and_sampling_is_not():
    """Two runs of the exact method agree to the last bit. Two runs of the
    sampler with different seeds do not, which is what an error bar is."""
    first = solve.scheme(3, "either", "enumeration").fixed_point
    second = solve.scheme(3, "either", "enumeration").fixed_point
    assert first == second

    seeds = [solve.scheme(3, "either", "sampling", draws=800, seed=s).fixed_point
             for s in range(4)]
    assert len(set(seeds)) > 1


def test_enumeration_refuses_a_block_it_cannot_finish():
    """2^25 configurations for a block of five, and 2^36 for a block of six.
    It is not slow there, it is impossible, and saying so is better than
    running until someone gives up."""
    with pytest.raises(ValueError, match="Enumeration stops at"):
        METHODS["enumeration"].polynomial(5, "either")


def test_sampling_keeps_going_where_enumeration_stops():
    """A block of five is 33 million configurations to enumerate and the same
    work as any other size to sample, because the binomial coefficient is a
    formula rather than a walk."""
    result = solve.scheme(5, "either", "sampling", draws=600, seed=0)
    assert 0.05 < result.fixed_point < 0.95
    assert result.derivative > 1.0


def test_the_sampler_converges_on_the_exact_answer_with_more_draws():
    exact = solve.scheme(3, "either", "enumeration").fixed_point
    errors = [abs(solve.scheme(3, "either", "sampling", draws=draws, seed=1).fixed_point
                  - exact) for draws in (100, 6000)]
    assert errors[1] < errors[0]


def test_only_the_plain_scheme_is_stuck_with_the_vertical_rule():
    """The rule is a choice and it matters. Asking for a top-to-bottom path
    only is a biased criterion, and the plain scheme built on it does not
    improve with block size -- measured, 0.618, 0.619, 0.619 at blocks of 2, 3
    and 4, against a true threshold of 0.5927. The `either` rule does improve,
    and cell-to-cell improves far faster than either of them.
    """
    stuck = [solve.scheme(size, "vertical").fixed_point for size in (2, 3, 4)]
    assert max(stuck) - min(stuck) < 0.01, "the vertical scheme barely moves"
    assert all(abs(p - flow.P_C) / flow.P_C > 0.03 for p in stuck)

    improving = [solve.scheme(size, "either").error_in_threshold()
                 for size in (2, 3, 4)]
    assert improving == sorted(improving, reverse=True)


def test_the_rules_bracket_the_true_threshold():
    """`either` is the loosest criterion and `both` the strictest, so their
    fixed points sit either side of the truth and close in on it from opposite
    directions. That is a far more useful thing than one number."""
    loose = solve.scheme(4, "either").fixed_point
    strict = solve.scheme(4, "both").fixed_point
    assert loose < flow.P_C < strict
    assert solve.scheme(2, "either").fixed_point < loose
    assert solve.scheme(2, "both").fixed_point > strict
