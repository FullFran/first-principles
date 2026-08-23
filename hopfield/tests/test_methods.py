"""Contract tests: what every update rule must satisfy, whatever it is.

Register a method in `methods/` and it inherits this suite. What it must NOT
inherit is the energy-descent guarantee, which is asynchronous-only and lives
in test_methods_differ.py -- that difference is physics, not a bug.
"""

import numpy as np
import pytest

import model
import solve
from methods import ALL as METHODS

METHOD_NAMES = sorted(METHODS)
pytestmark = pytest.mark.parametrize("method", METHOD_NAMES)


def random_patterns(count, size, seed=0):
    rng = np.random.default_rng(seed)
    return rng.choice([-1, 1], size=(count, size)).astype(np.int8)


def corrupt(pattern, fraction, seed=1):
    rng = np.random.default_rng(seed)
    flipped = pattern.copy()
    idx = rng.choice(pattern.size, size=int(fraction * pattern.size), replace=False)
    flipped[idx] *= -1
    return flipped


def test_state_stays_bipolar(method):
    patterns = random_patterns(3, 200)
    w = model.hebbian_weights(patterns)
    result = solve.relax(w, corrupt(patterns[0], 0.2), method=method, seed=0)
    assert set(np.unique(result.state)) <= {-1, 1}


def test_a_stored_pattern_does_not_move(method):
    patterns = random_patterns(3, 400)
    w = model.hebbian_weights(patterns)
    result = solve.relax(w, patterns[1], method=method, seed=0)
    assert np.array_equal(result.state, patterns[1])
    assert result.converged


@pytest.mark.parametrize("fraction", [0.05, 0.15, 0.25])
def test_recall_from_noise(method, fraction):
    """Well below capacity, a corrupted memory must come back exactly."""
    patterns = random_patterns(3, 400)
    w = model.hebbian_weights(patterns)
    result = solve.relax(w, corrupt(patterns[0], fraction), method=method, seed=0)
    assert np.array_equal(result.state, patterns[0])


def test_recall_is_sign_symmetric(method):
    """Starting from a corrupted -p must land on -p, not on p."""
    patterns = random_patterns(3, 400)
    w = model.hebbian_weights(patterns)
    result = solve.relax(w, corrupt(-patterns[0], 0.1), method=method, seed=0)
    assert np.array_equal(result.state, -patterns[0])


def test_relaxation_always_terminates(method):
    """Either a fixed point or a detected cycle -- never a silent max_sweeps."""
    patterns = random_patterns(6, 120)
    w = model.hebbian_weights(patterns)
    rng = np.random.default_rng(7)
    for _ in range(5):
        start = rng.choice([-1, 1], size=120).astype(np.int8)
        result = solve.relax(w, start, method=method, seed=0, max_sweeps=300)
        assert result.converged or result.cycle_length is not None


def test_energy_history_matches_the_states(method):
    patterns = random_patterns(3, 200)
    w = model.hebbian_weights(patterns)
    result = solve.relax(w, corrupt(patterns[0], 0.3), method=method, seed=0)
    assert result.energies[-1] == pytest.approx(model.energy(w, result.state))
    assert len(result.energies) == result.sweeps + 1


def test_dimension_mismatch_is_rejected(method):
    w = model.hebbian_weights(random_patterns(2, 10))
    with pytest.raises(ValueError, match="length"):
        solve.relax(w, np.ones(7, dtype=np.int8), method=method, seed=0)


def test_unknown_method_is_rejected(method):
    w = model.hebbian_weights(random_patterns(2, 10))
    with pytest.raises(ValueError, match="unknown method"):
        solve.relax(w, np.ones(10, dtype=np.int8), method="quantum-annealing", seed=0)
