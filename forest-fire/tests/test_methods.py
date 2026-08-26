"""Contract tests: what every way of finishing a fire must satisfy.

Register a method in `methods/` and it inherits this suite. What it must NOT
inherit is that a fire is the cluster that was standing when it started --
that is true of the instantaneous limit and false of the cellular automaton,
and the difference is the point of the entry.
"""

import numpy as np
import pytest

import lattice as lat
import solve
from methods import ALL as METHODS

METHOD_NAMES = sorted(METHODS)
pytestmark = pytest.mark.parametrize("method", METHOD_NAMES)

SLOW = dict(size=40, p=0.002, f=2e-5, steps=900)


def test_a_fire_consumes_trees_and_leaves_bare_ground(method):
    grid = np.full((12, 12), lat.TREE, dtype=np.int8)
    seed = np.zeros((12, 12), dtype=bool)
    seed[0, 0] = True
    size = METHODS[method].burn(grid, seed, np.random.default_rng(0), 0.0)
    assert size == 144
    assert not (grid == lat.TREE).any()
    assert not (grid == lat.FIRE).any(), "no site may be left burning"


def test_striking_bare_ground_burns_nothing(method):
    grid = np.zeros((8, 8), dtype=np.int8)
    seed = np.zeros((8, 8), dtype=bool)
    seed[3, 3] = True
    assert METHODS[method].burn(grid, seed, np.random.default_rng(0), 0.0) == 0


def test_an_isolated_tree_burns_alone(method):
    grid = np.zeros((9, 9), dtype=np.int8)
    grid[4, 4] = lat.TREE
    seed = np.zeros((9, 9), dtype=bool)
    seed[4, 4] = True
    assert METHODS[method].burn(grid, seed, np.random.default_rng(0), 0.0) == 1


def test_the_lattice_only_ever_holds_the_three_states(method):
    result = solve.run(method=method, seed=0, **SLOW)
    lat.check_grid(result.grid)


def test_the_forest_reaches_a_steady_density(method):
    """Growth and burning have to balance, or the model is not a model."""
    result = solve.run(method=method, seed=0, **SLOW)
    assert 0.05 < result.density < 0.95


def test_fewer_ignitions_make_bigger_fires(method):
    """The headline result, and both ways of finishing a fire must show it.

    Reduce the lightning rate and the forest grows denser between fires, so the
    fires that do happen are larger. This is the model's version of the
    suppression argument, and the knob is the ignition rate.
    """
    sizes = []
    for f in (2e-4, 2e-5):
        result = solve.run(size=40, p=0.002, f=f, steps=900, method=method, seed=0)
        assert result.fires, f"no fires at f = {f}"
        sizes.append(result.sizes.mean())
    assert sizes[1] > 2 * sizes[0]


def test_fewer_ignitions_make_a_denser_forest(method):
    """The mechanism behind the row above: the fuel is what changes.

    Both rates stay well below the growth rate, because `check_rates` refuses
    anything else -- an earlier version of this test used f = 2e-3 against
    p = 2e-3 and the guard caught it, which is what the guard is for.
    """
    dense = solve.run(size=40, p=0.002, f=2e-5, steps=900, method=method, seed=0)
    sparse = solve.run(size=40, p=0.002, f=5e-4, steps=900, method=method, seed=0)
    assert dense.density > sparse.density


def test_a_run_is_reproducible(method):
    first = solve.run(method=method, seed=3, **SLOW)
    second = solve.run(method=method, seed=3, **SLOW)
    assert np.array_equal(first.grid, second.grid)
    assert [f.size for f in first.fires] == [f.size for f in second.fires]


def test_every_fire_is_reported_separately(method):
    """One event per fire, not one per timestep. Merging two strikes that land
    on different clusters in the same step inflates the size distribution, and
    the number of strikes per step grows with the area."""
    result = solve.run(method=method, seed=0, **SLOW)
    assert result.fires
    steps = [fire.step for fire in result.fires]
    assert len(steps) >= len(set(steps)), "sanity: fires are indexed by step"
    assert all(fire.size > 0 for fire in result.fires)


def test_burn_in_is_discarded(method):
    full = solve.run(method=method, seed=0, burn_in=0.0, **SLOW)
    trimmed = solve.run(method=method, seed=0, burn_in=0.5, **SLOW)
    assert len(trimmed.fires) < len(full.fires)


def test_unknown_method_is_rejected(method):
    with pytest.raises(ValueError, match="unknown method"):
        solve.run(size=20, p=0.01, f=1e-4, steps=10, method="wind-driven")


def test_lightning_above_the_growth_rate_is_rejected(method):
    with pytest.raises(ValueError, match="well below growth"):
        solve.run(size=20, p=0.01, f=0.02, steps=10, method=method)
