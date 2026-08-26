"""A fire burns its whole cluster before anything else happens.

This is the separated-timescale limit, and it is what the model is defined in:
lightning strikes, the connected group of trees it belongs to burns to the
ground, and only then does the forest grow again. Nothing regrows inside the
fire, so the burned area is exactly the cluster that was standing when the
strike landed.

It is also the only version with a clean interpretation, because "the size of
the fire" and "the size of the cluster" are the same number. The moment growth
overlaps with burning those two part company, which is the next file.
"""

from lattice import TREE, EMPTY, cluster

NAME = "instantaneous"


def burn(grid, seed, rng, p):
    """`rng` and `p` are unused: nothing grows while this fire is burning."""
    consumed = cluster(grid, seed)
    grid[consumed] = EMPTY
    return int(consumed.sum())
