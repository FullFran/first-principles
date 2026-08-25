"""Domain tests: the energy function and the learning rule, with no dynamics.

Nothing here runs a method. If these fail the model is wrong; if these pass
and a method fails, the algorithm is wrong.
"""

import numpy as np
import pytest

import model

RNG = np.random.default_rng(0)


def random_patterns(count, size, seed=0):
    rng = np.random.default_rng(seed)
    return rng.choice([-1, 1], size=(count, size)).astype(np.int8)


# --- the learning rule ------------------------------------------------------

def test_weights_are_symmetric():
    w = model.hebbian_weights(random_patterns(3, 40))
    assert np.allclose(w, w.T)


def test_no_self_connection():
    w = model.hebbian_weights(random_patterns(3, 40))
    assert np.allclose(np.diag(w), 0.0)


def test_weights_are_the_averaged_outer_product():
    patterns = random_patterns(2, 12)
    expected = sum(np.outer(p, p) for p in patterns) / 12
    np.fill_diagonal(expected, 0.0)
    assert np.allclose(model.hebbian_weights(patterns), expected)


# --- the energy function ----------------------------------------------------

def test_energy_is_the_quadratic_form():
    w = model.hebbian_weights(random_patterns(2, 8))
    state = random_patterns(1, 8)[0]
    assert model.energy(w, state) == pytest.approx(-0.5 * state @ w @ state)


def test_stored_patterns_sit_below_random_states():
    patterns = random_patterns(3, 200)
    w = model.hebbian_weights(patterns)
    stored = np.mean([model.energy(w, p) for p in patterns])
    noise = np.mean([model.energy(w, p) for p in random_patterns(20, 200, seed=99)])
    assert stored < noise


# --- what makes a memory a memory ------------------------------------------

def test_a_stored_pattern_is_a_fixed_point():
    """Well below capacity, sign(W p) must return p itself."""
    patterns = random_patterns(3, 400)
    w = model.hebbian_weights(patterns)
    for p in patterns:
        assert np.array_equal(model.update_rule(model.local_field(w, p), p), p)


def test_the_negated_pattern_is_also_a_fixed_point():
    """Hopfield energy is invariant under a global sign flip, so every memory
    comes with its mirror image whether you wanted it or not."""
    patterns = random_patterns(3, 400)
    w = model.hebbian_weights(patterns)
    for p in patterns:
        assert np.array_equal(model.update_rule(model.local_field(w, -p), -p), -p)
        assert model.energy(w, -p) == pytest.approx(model.energy(w, p))


def test_the_three_pattern_mixture_is_a_fixed_point():
    """The canonical spurious state: sign(p1 + p2 + p3) is stable even though
    nobody ever stored it."""
    patterns = random_patterns(3, 400)
    w = model.hebbian_weights(patterns)
    mixture = model.update_rule(patterns.sum(axis=0), patterns[0])
    assert not any(np.array_equal(mixture, p) for p in patterns)
    assert np.array_equal(model.update_rule(model.local_field(w, mixture), mixture), mixture)


# --- the update rule at the boundary ---------------------------------------

def test_zero_field_leaves_the_unit_alone():
    """sign(0) = 0 would drop the unit out of {-1, +1} entirely."""
    current = np.array([1, -1, 1], dtype=np.int8)
    result = model.update_rule(np.array([0.0, 0.0, 2.0]), current)
    assert np.array_equal(result, [1, -1, 1])
    assert set(np.unique(result)) <= {-1, 1}


# --- when the boundary is actually reached ---------------------------------
#
# The tie above is not hypothetical, and whether it can happen at all is fixed
# by an exact parity law rather than by luck. Writing N*h_i = q_i . v with
# q_j = (p^1_j, ..., p^P_j) and v_mu = sum_{j != i} p^mu_j s_j, each v_mu is a
# sum of N-1 terms of +-1 and so carries the parity of N-1. The dot product is
# a signed sum of P of them, so N*h_i carries the parity of P(N-1). Zero is
# even. An odd product therefore forbids the tie outright.
#
# These tests work in exact integer arithmetic on N*W, never on the float
# field: float64 rounds a true zero to ~1e-17 and reports no tie at all.

def integer_field(patterns, states):
    """N * h for every state, as exact integers. N*W is the Gram matrix."""
    gram = patterns.T.astype(np.int64) @ patterns.astype(np.int64)
    np.fill_diagonal(gram, 0)
    return np.asarray(states, dtype=np.int64) @ gram.T


def tie_rate(count, size, trials=10, states=20, seed=0):
    ties = total = 0
    for trial in range(trials):
        rng = np.random.default_rng(1000 * seed + trial)
        patterns = rng.choice([-1, 1], size=(count, size)).astype(np.int8)
        probes = rng.choice([-1, 1], size=(states, size)).astype(np.int8)
        fields = integer_field(patterns, probes)
        ties += int(np.count_nonzero(fields == 0))
        total += fields.size
    return ties / total


@pytest.mark.parametrize("size, count", [(20, 3), (100, 3), (576, 5)])
def test_an_exact_tie_is_impossible_when_p_times_n_minus_one_is_odd(size, count):
    """Parity forbids it. Not rare -- unreachable."""
    assert (count * (size - 1)) % 2 == 1, "these cases must have an odd product"
    assert tie_rate(count, size) == 0.0


@pytest.mark.parametrize("size, count", [(20, 4), (21, 3), (577, 3)])
def test_exact_ties_do_occur_when_p_times_n_minus_one_is_even(size, count):
    """And they stay at the percent level rather than dying out with N, which
    is why holding the current value is load-bearing and not defensive."""
    assert (count * (size - 1)) % 2 == 0, "these cases must have an even product"
    assert tie_rate(count, size) > 0.005


def test_the_entrys_own_glyph_setup_can_tie():
    """N = 576 with P = 4 gives P(N-1) = 2300, even. The convention matters in
    the configuration this entry actually ships and runs experiments on."""
    size, count = 576, 4
    assert (count * (size - 1)) % 2 == 0
    assert tie_rate(count, size) > 0.005


def test_float64_under_reports_the_ties_it_was_written_to_catch():
    """The guard is real and the arithmetic hides most of its work: an exact
    zero accumulated over hundreds of float additions arrives as ~1e-17, and
    the unit silently takes a direction chosen by rounding. Documented rather
    than fixed -- either side of a tie is a legitimate tie-break, but nobody
    should believe `h == 0` measures how often the branch is taken."""
    exact = seen = 0
    for trial in range(10):
        rng = np.random.default_rng(trial)
        patterns = rng.choice([-1, 1], size=(4, 60)).astype(np.int8)
        probes = rng.choice([-1, 1], size=(20, 60)).astype(np.int8)
        weights = model.hebbian_weights(patterns)

        exact += int(np.count_nonzero(integer_field(patterns, probes) == 0))
        seen += sum(int(np.count_nonzero(model.local_field(weights, s) == 0))
                    for s in probes)

    assert exact > 0, "these parameters must produce genuine ties"
    assert seen < exact


# --- domain invariants ------------------------------------------------------

def test_non_bipolar_pattern_is_rejected():
    with pytest.raises(ValueError, match="bipolar"):
        model.hebbian_weights(np.array([[1, 0, -1]]))


def test_asymmetric_weights_are_rejected():
    with pytest.raises(ValueError, match="symmetric"):
        model.check_weights(np.array([[0.0, 1.0], [2.0, 0.0]]))


def test_self_connection_is_rejected():
    with pytest.raises(ValueError, match="diagonal"):
        model.check_weights(np.array([[1.0, 0.0], [0.0, 1.0]]))


def test_empty_pattern_set_is_rejected():
    with pytest.raises(ValueError, match="at least one"):
        model.hebbian_weights(np.zeros((0, 5), dtype=np.int8))
