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


# --- the theorem the synchronous schedule does have ------------------------
#
# "No energy guarantee" is the lazy reading. Updating in parallel breaks the
# Lyapunov argument for E because that argument assumed everything else stayed
# put -- but a different Lyapunov function survives, defined on *pairs* of
# consecutive states:
#
#     F(s(t), s(t+1)) = -s(t) . W . s(t+1)
#
# With s(t+1) = sign(W s(t)) and W symmetric,
#
#     dF = -sum_i ( |h_i| - h_i s_i(t) ) <= 0,      h = W s(t+1)
#
# because h_i s_i(t+2) = |h_i| by construction. Finiteness then bounds the run,
# and equality forces s(t+2) = s(t). Hence period 1 or 2 and nothing else --
# Goles-Chacc, Fogelman-Soulie & Pellegrin (1985).

def synchronous_run(weights, start, max_sweeps=300):
    """Iterate the parallel map, returning the period and the trace of F."""
    state = start.copy()
    seen = {state.tobytes(): 0}
    pair_energies = []
    for step in range(1, max_sweeps + 1):
        nxt = model.update_rule(model.local_field(weights, state), state)
        pair_energies.append(
            float(-state.astype(float) @ weights @ nxt.astype(float))
        )
        state = nxt
        key = state.tobytes()
        if key in seen:
            return step - seen[key], pair_energies
        seen[key] = step
    return None, pair_energies


def test_synchronous_period_is_never_greater_than_two():
    """Not 'usually settles' -- the period is 1 or 2, with nothing else
    reachable. A period of 3 anywhere here would falsify the theorem."""
    weights = model.hebbian_weights(random_patterns(12, 60))
    rng = np.random.default_rng(21)
    periods = set()
    for _ in range(120):
        start = rng.choice([-1, 1], size=60).astype(np.int8)
        period, _ = synchronous_run(weights, start)
        assert period is not None, "the run did not close a cycle at all"
        periods.add(period)
    assert periods <= {1, 2}, f"period outside the theorem: {sorted(periods)}"
    assert periods == {1, 2}, "both outcomes should show up in 120 runs"


def test_synchronous_pair_energy_never_increases():
    """E is free to rise under parallel updates; F is not. This is the
    quantity that actually descends, and it is why the cycles are short."""
    weights = model.hebbian_weights(random_patterns(12, 60))
    rng = np.random.default_rng(22)
    for _ in range(40):
        start = rng.choice([-1, 1], size=60).astype(np.int8)
        _, pair_energies = synchronous_run(weights, start)
        assert np.all(np.diff(pair_energies) <= 1e-9)


def test_the_two_lyapunov_functions_disagree_on_the_same_run():
    """Stated together so the contrast is unambiguous: on at least one run E
    goes up while F does not. Same trajectory, two different accountants."""
    weights = model.hebbian_weights(random_patterns(12, 60))
    rng = np.random.default_rng(23)
    for _ in range(40):
        start = rng.choice([-1, 1], size=60).astype(np.int8)
        _, pair_energies = synchronous_run(weights, start)
        energies = solve.relax(weights, start, method="synchronous",
                               seed=0, max_sweeps=300).energies
        if np.any(np.diff(energies) > 1e-9):
            assert np.all(np.diff(pair_energies) <= 1e-9)
            return
    pytest.fail("no run raised E, so the contrast was never exercised")

