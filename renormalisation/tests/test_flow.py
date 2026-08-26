"""Domain tests: the block rule, the map, and what the map says.

Nothing here chooses a scheme or a block size. If these fail the map is wrong;
if these pass and a scheme is off, the scheme is the thing that is off -- and
being off is not automatically a defect here, which is the entry's point.
"""

import numpy as np
import pytest

import flow


def block(rows):
    return np.array([[c == "#" for c in row] for row in rows], dtype=bool)


# --- the block rule ---------------------------------------------------------

def test_a_full_block_spans_and_an_empty_one_does_not():
    for rule in flow.RULES:
        assert flow.spans(np.ones((4, 4), dtype=bool), rule)
        assert not flow.spans(np.zeros((4, 4), dtype=bool), rule)


def test_a_single_column_spans_vertically_and_not_horizontally():
    """The three rules are genuinely different criteria, not three spellings of
    one. A bar connects two edges in one direction only."""
    bar = block(["#..", "#..", "#.."])
    assert flow.spans(bar, "vertical")
    assert flow.spans(bar, "either")
    assert not flow.spans(bar, "both")


def test_a_single_row_spans_horizontally_and_not_vertically():
    bar = block(["...", "###", "..."])
    assert not flow.spans(bar, "vertical")
    assert flow.spans(bar, "either")
    assert not flow.spans(bar, "both")


def test_a_cross_spans_in_both_directions():
    cross = block([".#.", "###", ".#."])
    assert all(flow.spans(cross, rule) for rule in flow.RULES)


def test_connection_is_what_counts_not_how_many_sites():
    """A block can be more than half full and still not conduct. That is why
    the criterion is spanning rather than a majority: coarse-graining has to
    preserve whether things connect, because that is what percolates."""
    diagonal = block(["#..", ".#.", "..#"])
    assert diagonal.sum() == 3
    assert not flow.spans(diagonal, "vertical")
    line = block(["#..", "#..", "#.."])
    assert line.sum() == 3
    assert flow.spans(line, "vertical")


# --- the map ----------------------------------------------------------------

def test_the_two_by_two_vertical_map_is_the_one_you_can_do_by_hand():
    """R(p) = 2p^2(1-p)^2 + 4p^3(1-p) + p^4, which collapses to 2p^2 - p^4."""
    coarse = flow.recursion(flow.block_polynomial(2, "vertical"), 2)
    grid = np.linspace(0, 1, 41)
    assert np.allclose(coarse(grid), 2 * grid ** 2 - grid ** 4)


def test_the_two_by_two_fixed_point_is_the_golden_ratio():
    """R(p) = p gives p^3 - 2p + 1 = 0, which factors as (p-1)(p^2 + p - 1).
    The root in (0, 1) is exactly (sqrt(5) - 1)/2."""
    coarse = flow.recursion(flow.block_polynomial(2, "vertical"), 2)
    golden = (np.sqrt(5) - 1) / 2
    assert flow.fixed_point(coarse) == pytest.approx(golden, abs=1e-9)
    assert golden == pytest.approx(0.618034, abs=1e-6)


@pytest.mark.parametrize("size", [2, 3])
@pytest.mark.parametrize("rule", flow.RULES)
def test_an_empty_lattice_stays_empty_and_a_full_one_stays_full(size, rule):
    """R(0) = 0 and R(1) = 1 always. Those are the two trivial fixed points,
    and they are the two things coarse-graining flows towards."""
    coarse = flow.recursion(flow.block_polynomial(size, rule), size)
    assert float(coarse(np.array(0.0))) == pytest.approx(0.0)
    assert float(coarse(np.array(1.0))) == pytest.approx(1.0)


@pytest.mark.parametrize("size", [2, 3])
@pytest.mark.parametrize("rule", flow.RULES)
def test_the_map_is_increasing(size, rule):
    """More trees cannot make a block less likely to conduct."""
    grid = np.linspace(0.01, 0.99, 60)
    coarse = flow.recursion(flow.block_polynomial(size, rule), size)
    assert np.all(np.diff(coarse(grid)) > -1e-12)


@pytest.mark.parametrize("size", [2, 3])
@pytest.mark.parametrize("rule", flow.RULES)
def test_the_fixed_point_is_unstable(size, rule):
    """dR/dp > 1 there, which is what makes it a critical point rather than an
    attractor. Coarse-graining pushes you away from it in both directions, so a
    system only looks the same at every scale if it sits exactly on it."""
    coarse = flow.recursion(flow.block_polynomial(size, rule), size)
    point = flow.fixed_point(coarse)
    assert flow.slope(coarse, point) > 1.0


def test_the_flow_runs_away_from_the_fixed_point_in_both_directions():
    coarse = flow.recursion(flow.block_polynomial(3, "either"), 3)
    point = flow.fixed_point(coarse)
    below, above = point - 0.05, point + 0.05
    for _ in range(6):
        below = float(coarse(np.array(below)))
        above = float(coarse(np.array(above)))
    assert below < 0.02 and above > 0.98


# --- the exponent -----------------------------------------------------------

def test_the_exponent_comes_from_the_slope_and_the_scale():
    assert flow.exponent(2, 2.0) == pytest.approx(1.0)
    assert flow.exponent(4, 2.0) == pytest.approx(2.0)
    assert flow.exponent(2, 4.0) == pytest.approx(0.5)


def test_a_stable_fixed_point_has_no_exponent():
    with pytest.raises(ValueError, match="must be unstable"):
        flow.exponent(2, 0.8)


def test_a_block_that_does_not_coarsen_has_no_exponent():
    with pytest.raises(ValueError, match="actually coarsen"):
        flow.exponent(1, 2.0)


# --- invariants -------------------------------------------------------------

def test_a_block_smaller_than_two_is_rejected():
    with pytest.raises(ValueError, match="two sites a side"):
        flow.check_block(1)


def test_an_unknown_rule_is_rejected():
    with pytest.raises(ValueError, match="unknown rule"):
        flow.spans(np.ones((2, 2), dtype=bool), "majority")


def test_a_polynomial_of_the_wrong_length_is_rejected():
    with pytest.raises(ValueError, match="coefficients"):
        flow.recursion(np.zeros(3), 2)
