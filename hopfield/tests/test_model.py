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
