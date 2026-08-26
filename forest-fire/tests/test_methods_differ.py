"""Where the two ways of finishing a fire part company -- and why.

Both are handed the same lattice and the same rule for what catches. They
differ in one thing: whether the forest grows while a fire is burning. That is
the model's central assumption, and having both limits is what lets it be
measured instead of assumed.
"""

import numpy as np
import pytest

import lattice as lat
import solve
from methods import ALL as METHODS


def mean_size(method, p, ratio=0.01, size=40, steps=900, seed=0):
    result = solve.run(size=size, p=p, f=p * ratio, steps=steps,
                       method=method, seed=seed)
    return result.sizes.mean() if result.fires else float("nan")


def test_a_fire_cannot_outgrow_its_cluster_when_nothing_regrows():
    """In the instantaneous limit the burned area *is* the cluster that was
    standing, so it can never exceed the lattice."""
    result = solve.run(size=40, p=0.01, f=1e-4, steps=800,
                       method="instantaneous", seed=0)
    assert result.fires
    assert result.largest <= 40 * 40


def test_a_synchronous_fire_can_burn_more_than_the_whole_lattice():
    """Because the forest regrows behind the front. A fire that circles back
    through its own scar consumes the same ground twice, and the number it
    reports is an area burned rather than a cluster size. Those are different
    quantities and only the separation of timescales makes them agree."""
    result = solve.run(size=40, p=0.02, f=2e-4, steps=800,
                       method="synchronous", seed=0)
    assert result.fires
    assert result.largest > 40 * 40


def test_the_two_agree_only_when_the_forest_grows_slowly():
    """The sharp version of "separation of timescales", and it is not f/p.

    Holding f/p fixed and lowering p alone brings them together, because what
    matters is how much forest appears *during* one fire -- growth rate times
    fire duration. Measured on a 40-square lattice at f/p = 0.01, the ratio of
    mean fire sizes runs roughly 7, 2.1, 1.9, 1.0 as p falls from 0.02 to 0.002.

    The tolerance on the slow case is wide on purpose, and it is a statement
    about sample size rather than about physics: at p = 0.002 this budget only
    produces six to ten fires, so the ratio wanders between 0.94 and 1.66 across
    seeds. At p = 0.02 there are eighty and it sits between 6.6 and 9.3.
    """
    fast = mean_size("synchronous", 0.02) / mean_size("instantaneous", 0.02)
    slow = mean_size("synchronous", 0.002) / mean_size("instantaneous", 0.002)
    assert fast > 5.0, "at a fast-growing forest they must disagree badly"
    assert 0.5 < slow < 2.0, "at a slow-growing one they must converge"
    assert fast > slow


def test_a_fast_growing_forest_makes_fire_endemic():
    """Above a growth rate of roughly 0.1 the synchronous fire never goes out:
    regrowth feeds the front faster than it burns through. That is a transition
    the instantaneous version cannot have, because in it nothing grows while
    anything burns -- so it is a property of the method, not of the lattice."""
    grid = np.full((40, 40), lat.TREE, dtype=np.int8)
    seed = np.zeros((40, 40), dtype=bool)
    seed[20, 20] = True
    with pytest.raises(RuntimeError, match="endemic|never ends|still burning"):
        METHODS["synchronous"].burn(grid, seed, np.random.default_rng(0), 0.5,
                                    max_rings=400)


def test_only_the_synchronous_method_consumes_randomness_while_burning():
    """A structural difference, not a statistical one. The instantaneous burn
    never touches the generator, which is why it takes one at all only to keep
    the two interchangeable."""
    grid = np.full((10, 10), lat.TREE, dtype=np.int8)
    seed = np.zeros((10, 10), dtype=bool)
    seed[0, 0] = True
    rng = np.random.default_rng(0)
    before = rng.bit_generator.state["state"]["state"]
    METHODS["instantaneous"].burn(grid.copy(), seed, rng, 0.05)
    assert rng.bit_generator.state["state"]["state"] == before

    METHODS["synchronous"].burn(grid.copy(), seed, rng, 0.05)
    assert rng.bit_generator.state["state"]["state"] != before
