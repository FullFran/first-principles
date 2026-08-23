"""Where the two methods part company -- and why that is physics.

In `tmm/` the two solvers agreed to 1e-13 and any disagreement would have been
a bug. Here they genuinely disagree, and the disagreement is the textbook
result: energy descent is guaranteed for asynchronous updates and not for
synchronous ones. A contract suite that demanded both would be asserting
something false.
"""

import numpy as np
import pytest

import model
import solve


def random_patterns(count, size, seed=0):
    rng = np.random.default_rng(seed)
    return rng.choice([-1, 1], size=(count, size)).astype(np.int8)


def test_asynchronous_energy_never_increases():
    """One unit at a time, with symmetric W and zero diagonal, every flip
    lowers E or leaves it alone. This is the Lyapunov argument."""
    patterns = random_patterns(4, 200)
    w = model.hebbian_weights(patterns)
    rng = np.random.default_rng(3)
    for _ in range(10):
        start = rng.choice([-1, 1], size=200).astype(np.int8)
        energies = solve.relax(w, start, method="asynchronous", seed=0).energies
        assert np.all(np.diff(energies) <= 1e-12)


def test_asynchronous_always_reaches_a_fixed_point():
    """A decreasing function on a finite state space has nowhere else to go."""
    patterns = random_patterns(5, 150)
    w = model.hebbian_weights(patterns)
    rng = np.random.default_rng(4)
    for _ in range(10):
        start = rng.choice([-1, 1], size=150).astype(np.int8)
        result = solve.relax(w, start, method="asynchronous", seed=0, max_sweeps=500)
        assert result.converged
        assert result.cycle_length is None


def test_synchronous_can_fall_into_a_two_cycle():
    """Updating everything at once breaks the Lyapunov argument: the network
    settles into a fixed point OR oscillates with period two."""
    patterns = random_patterns(12, 60)
    w = model.hebbian_weights(patterns)
    rng = np.random.default_rng(5)
    cycles = 0
    for _ in range(40):
        start = rng.choice([-1, 1], size=60).astype(np.int8)
        result = solve.relax(w, start, method="synchronous", seed=0, max_sweeps=200)
        if result.cycle_length == 2:
            cycles += 1
    assert cycles > 0, "no 2-cycle found; the synchronous characterisation is wrong"


def test_synchronous_energy_can_go_up():
    """Direct consequence of the above, stated on its own so a regression here
    is unambiguous."""
    patterns = random_patterns(12, 60)
    w = model.hebbian_weights(patterns)
    rng = np.random.default_rng(6)
    increased = False
    for _ in range(40):
        start = rng.choice([-1, 1], size=60).astype(np.int8)
        energies = solve.relax(w, start, method="synchronous", seed=0, max_sweeps=200).energies
        if np.any(np.diff(energies) > 1e-9):
            increased = True
            break
    assert increased
