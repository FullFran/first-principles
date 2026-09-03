"""Domain tests: the lattice, the rules, and the percolation threshold.

Nothing here runs the model. If these fail the rules are wrong; if these pass
and a method fails, the choice about how a fire finishes is wrong.
"""

import ast
from pathlib import Path

import numpy as np
import pytest

import lattice as lat


def occupied(size, p, seed=0):
    rng = np.random.default_rng(seed)
    return (rng.random((size, size)) < p).astype(np.int8)


# --- the closed form --------------------------------------------------------

def test_spanning_crosses_one_half_at_the_percolation_threshold():
    """p_c = 0.5927 is the closed form this entry checks itself against.

    Below it a random forest almost never connects two edges; above it, almost
    always. The crossing is what makes it a threshold rather than a trend.
    """
    below = np.mean([lat.spans(occupied(64, 0.50, s)) for s in range(30)])
    at = np.mean([lat.spans(occupied(64, lat.P_C, s)) for s in range(30)])
    above = np.mean([lat.spans(occupied(64, 0.68, s)) for s in range(30)])
    assert below < 0.1
    assert 0.25 < at < 0.75
    assert above > 0.9


def test_the_transition_sharpens_with_the_lattice():
    """A finite lattice smears the threshold; a bigger one smears it less. That
    is what makes it a phase transition rather than a crossover."""
    def width(size):
        low = np.mean([lat.spans(occupied(size, 0.55, s)) for s in range(24)])
        high = np.mean([lat.spans(occupied(size, 0.65, s)) for s in range(24)])
        return high - low
    assert width(96) >= width(24)


def test_an_empty_forest_never_spans_and_a_full_one_always_does():
    assert not lat.spans(np.zeros((16, 16), dtype=np.int8))
    assert lat.spans(np.ones((16, 16), dtype=np.int8))


# --- the rules --------------------------------------------------------------

def test_fire_spreads_to_four_neighbours_and_not_diagonally():
    burning = np.zeros((5, 5), dtype=bool)
    burning[2, 2] = True
    reached = lat.spread(burning, periodic=False)
    assert reached[1, 2] and reached[3, 2] and reached[2, 1] and reached[2, 3]
    assert not reached[1, 1] and not reached[3, 3]
    assert reached.sum() == 4


def test_spreading_wraps_around_only_when_asked():
    burning = np.zeros((5, 5), dtype=bool)
    burning[0, 0] = True
    assert lat.spread(burning, periodic=True)[4, 0]
    assert not lat.spread(burning, periodic=False)[4, 0]


def test_a_cluster_is_the_connected_group_and_stops_at_a_gap():
    grid = np.zeros((5, 5), dtype=np.int8)
    grid[1, 1:4] = lat.TREE           # a bar
    grid[3, 1:4] = lat.TREE           # another, not touching
    seed = np.zeros((5, 5), dtype=bool)
    seed[1, 1] = True
    found = lat.cluster(grid, seed, periodic=False)
    assert found.sum() == 3
    assert not found[3].any()


def test_a_cluster_of_a_bare_site_is_empty():
    grid = np.zeros((4, 4), dtype=np.int8)
    seed = np.zeros((4, 4), dtype=bool)
    seed[0, 0] = True
    assert lat.cluster(grid, seed).sum() == 0


def test_growth_only_fills_empty_sites():
    grid = np.zeros((20, 20), dtype=np.int8)
    grid[0] = lat.TREE
    rng = np.random.default_rng(0)
    lat.grow(grid, 1.0, rng)
    assert np.all(grid == lat.TREE)
    assert lat.density(grid) == pytest.approx(1.0)


def test_lightning_only_strikes_trees():
    grid = np.zeros((20, 20), dtype=np.int8)
    grid[:10] = lat.TREE
    struck = lat.strike(grid, 1.0, np.random.default_rng(0))
    assert struck[:10].all() and not struck[10:].any()


def test_strike_returns_a_mask_rather_than_setting_fires():
    """So the caller can give each strike its own fire. Burning them together
    would merge independent fires whenever two land in the same step, and the
    number of strikes per step grows with the area."""
    grid = np.full((8, 8), lat.TREE, dtype=np.int8)
    struck = lat.strike(grid, 1.0, np.random.default_rng(0))
    assert struck.dtype == bool
    assert np.all(grid == lat.TREE), "strike must not modify the lattice"


# --- invariants -------------------------------------------------------------

def test_lightning_at_or_above_the_growth_rate_is_rejected():
    """f << p is the model, not a detail: without it a fire never finds a
    grown cluster and there is nothing critical to see."""
    with pytest.raises(ValueError, match="well below growth"):
        lat.check_rates(0.01, 0.01)
    with pytest.raises(ValueError, match="well below growth"):
        lat.check_rates(0.01, 0.5)
    lat.check_rates(0.05, 1e-3)


@pytest.mark.parametrize("p, f", [(0.0, 1e-3), (1.5, 1e-3), (0.05, 0.0), (0.05, 2.0)])
def test_rates_outside_the_unit_interval_are_rejected(p, f):
    with pytest.raises(ValueError, match="must lie in"):
        lat.check_rates(p, f)


def test_a_lattice_smaller_than_two_is_rejected():
    with pytest.raises(ValueError, match="two sites a side"):
        lat.empty_grid(1)


def test_a_state_outside_the_three_is_rejected():
    with pytest.raises(ValueError, match="empty, a tree or on fire"):
        lat.check_grid(np.array([[0, 7]], dtype=np.int8))


def test_the_domain_imports_no_method():
    """Rule 7, checked instead of asserted.

    Nothing else in this suite would notice a violation. The contract asks
    whether every method obeys the domain, which is the other direction, and
    an import written inside a function body does not even fail at
    collection -- the domain can `import methods`, use it, and leave the
    whole suite green.

    Deliberately shallow: it reads the imports the parser can see, so a
    module fetched through importlib at runtime would walk past it. It
    catches the way the mistake actually gets made.
    """
    domain = Path(__file__).resolve().parent.parent / "lattice.py"

    imported = []
    for node in ast.walk(ast.parse(domain.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            imported += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.append(node.module)
            else:  # from . import methods
                imported += [alias.name for alias in node.names]

    offenders = sorted(
        name for name in imported
        if name == "methods" or name.startswith("methods.")
    )
    assert not offenders, (
        f"{domain.name} imports {offenders} -- the equations may not "
        f"import the algorithm; the arrow only points the other way"
    )
