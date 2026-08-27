"""Contract tests: what every way of counting spanning blocks must satisfy.

Register a method in `methods/` and it inherits this suite. What it must NOT
inherit is being exact, or working at any block size -- one of them is both and
the other is neither, and the trade is the entry.
"""

import numpy as np
import pytest

import flow
import solve
from methods import ALL as METHODS

METHOD_NAMES = sorted(METHODS)
pytestmark = pytest.mark.parametrize("method", METHOD_NAMES)

OPTIONS = {"enumeration": {}, "sampling": {"draws": 2500, "seed": 0}}


def coefficients(method, size=3, rule="either"):
    return METHODS[method].polynomial(size, rule, **OPTIONS[method])


def test_the_empty_and_full_blocks_are_counted_exactly(method):
    """Zero occupied sites never span and every site occupied always does, and
    a sampler has no excuse for getting either wrong."""
    counts = coefficients(method)
    assert counts[0] == 0.0
    assert counts[-1] == 1.0


def test_no_count_exceeds_the_number_of_configurations(method):
    from math import comb
    size = 3
    counts = coefficients(method, size)
    for occupied, value in enumerate(counts):
        assert -1e-9 <= value <= comb(size * size, occupied) + 1e-9


def test_a_block_cannot_span_with_fewer_sites_than_a_side(method):
    """A three-wide block needs at least three occupied sites to cross."""
    counts = coefficients(method, 3)
    assert counts[1] == 0.0 and counts[2] == 0.0


def test_the_map_reaches_zero_and_one_at_the_ends(method):
    result = solve.scheme(3, "either", method, **OPTIONS[method])
    assert float(result.coarse(0.0)) == pytest.approx(0.0)
    assert float(result.coarse(1.0)) == pytest.approx(1.0)


def test_there_is_an_unstable_fixed_point(method):
    result = solve.scheme(3, "either", method, **OPTIONS[method])
    assert 0.05 < result.fixed_point < 0.95
    assert result.derivative > 1.0
    assert result.exponent > 0.0


def test_a_bigger_block_gets_closer_to_the_threshold(method):
    """With the `either` rule the plain scheme does improve, just slowly:
    measured, 36%, 20%, 14% off p_c at blocks of 2, 3 and 4."""
    errors = [solve.scheme(size, "either", method, **OPTIONS[method]).error_in_threshold()
              for size in (2, 3)]
    assert errors[1] < errors[0]


def test_cell_to_cell_beats_the_plain_scheme(method):
    """Comparing two blocks instead of a block against a site. Both sides are
    then the same kind of object, and the mismatch mostly cancels."""
    plain = solve.scheme(3, "either", method, **OPTIONS[method]).error_in_threshold()
    paired = solve.cell_to_cell(2, 3, "either", method,
                                **OPTIONS[method]).error_in_threshold()
    assert paired < plain


def test_a_run_is_reproducible(method):
    first = solve.scheme(3, "either", method, **OPTIONS[method])
    second = solve.scheme(3, "either", method, **OPTIONS[method])
    assert first.fixed_point == second.fixed_point


def test_unknown_method_is_rejected(method):
    with pytest.raises(ValueError, match="unknown method"):
        solve.scheme(2, "either", "wavelet")


def test_unknown_rule_is_rejected(method):
    with pytest.raises(ValueError, match="unknown rule"):
        solve.scheme(2, "diagonal", method, **OPTIONS[method])


def test_a_block_of_one_is_rejected(method):
    with pytest.raises(ValueError, match="two sites a side"):
        solve.scheme(1, "either", method, **OPTIONS[method])


def test_cell_to_cell_needs_the_second_block_to_be_larger(method):
    with pytest.raises(ValueError, match="must be larger"):
        solve.cell_to_cell(3, 3, "either", method, **OPTIONS[method])


def test_a_misspelled_option_is_rejected_rather_than_ignored(method):
    """The failure this catches is silent, which is the only reason it needs a
    test. Every method ends its signature in `**_`, so before this check
    `counting="sampling"` reached nothing, changed nothing, and came back with
    the enumerated default -- a plausible number for a question nobody asked.
    """
    with pytest.raises(ValueError, match="unknown option"):
        solve.scheme(3, "either", method, counting="sampling", **OPTIONS[method])


def test_cell_to_cell_rejects_it_too(method):
    with pytest.raises(ValueError, match="unknown option"):
        solve.cell_to_cell(3, 4, "either", method, drwas=500, **OPTIONS[method])


def test_an_option_another_method_understands_is_still_accepted(method):
    """The tolerance above it is deliberate and has to survive the rejection.

    `solve` hands the same options to whichever method is selected, so one call
    can be pointed at either one and enumeration ignores `draws`. Forbid that
    and this parametrized suite stops being writable at all.
    """
    solve.scheme(3, "either", method, draws=500, seed=0)


def test_and_the_accepted_options_actually_arrive(method):
    """Accepting a keyword and then dropping it would pass the test above."""
    first = solve.scheme(3, "either", method, draws=500, seed=0).polynomial
    second = solve.scheme(3, "either", method, draws=500, seed=1).polynomial
    moved = not np.array_equal(first, second)
    assert moved == (method == "sampling")
