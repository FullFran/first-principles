"""The domain: a lattice, three states, and the one rule that connects them.

Growth, ignition, and the spread of fire to a neighbour. No timestep loop, no
choice about when a fire finishes -- those are choices, and they live in
`methods/` and `solve.py`.

    methods/ imports lattice.        lattice imports nobody.

Conventions
-----------
grid        (L, L) of int8, one of EMPTY / TREE / FIRE
p           probability that an empty site grows a tree, per site per step
f           probability that a tree is struck by lightning, per site per step
periodic    wrap-around by default, so no site is special; the percolation
            experiment turns it off, because spanning needs edges to span
"""

import numpy as np

__all__ = [
    "EMPTY", "TREE", "FIRE", "P_C",
    "empty_grid", "density", "grow", "strike", "spread", "cluster", "spans",
    "check_rates", "check_grid",
]

EMPTY, TREE, FIRE = np.int8(0), np.int8(1), np.int8(2)

P_C = 0.5927460
"""Site percolation threshold on a square lattice with four neighbours.

Not derived here and not derivable in closed form -- it is known numerically to
far more digits than this, and it is the closed form this entry checks itself
against. Everything about the model's critical behaviour is a statement about
where the tree density sits relative to it.
"""


# --- invariants -------------------------------------------------------------

def check_rates(p, f):
    """The model is only what it claims to be when f << p << 1.

    Growth has to be slow compared with everything (or the forest is just full)
    and lightning slower still (or a fire never finds a grown cluster). The
    regime is the model; outside it the same code computes something else.
    """
    if not 0.0 < p <= 1.0:
        raise ValueError(f"growth probability must lie in (0, 1], got {p}")
    if not 0.0 < f <= 1.0:
        raise ValueError(f"lightning probability must lie in (0, 1], got {f}")
    if f >= p:
        raise ValueError(
            f"lightning ({f}) must be well below growth ({p}); the separation "
            "of timescales is the model, not a detail")


def check_grid(grid):
    values = set(np.unique(grid).tolist())
    if not values <= {int(EMPTY), int(TREE), int(FIRE)}:
        raise ValueError(f"a site must be empty, a tree or on fire; found {values}")


# --- the rules --------------------------------------------------------------

def empty_grid(size):
    if size < 2:
        raise ValueError(f"a lattice needs at least two sites a side, got {size}")
    return np.zeros((size, size), dtype=np.int8)


def density(grid):
    """Fraction of sites holding a tree. The order parameter of the model."""
    return float(np.mean(grid == TREE))


def grow(grid, p, rng):
    """Empty sites become trees with probability p. Returns how many did."""
    sprouting = (grid == EMPTY) & (rng.random(grid.shape) < p)
    grid[sprouting] = TREE
    return int(np.count_nonzero(sprouting))


def strike(grid, f, rng):
    """Which trees lightning hit this step. A mask, not an action.

    Returning the mask rather than setting them alight is what lets `solve.py`
    treat each strike as its own fire. Burning every struck site in one call
    would merge two independent fires into one event whenever two strikes land
    in the same step -- and the number of strikes per step grows with the area,
    so that is not a rare case on a large lattice.
    """
    return (grid == TREE) & (rng.random(grid.shape) < f)


def spread(burning, periodic=True):
    """The four sites a fire reaches next. The only spatial rule in the model."""
    if periodic:
        return (np.roll(burning, 1, 0) | np.roll(burning, -1, 0)
                | np.roll(burning, 1, 1) | np.roll(burning, -1, 1))
    out = np.zeros_like(burning)
    out[1:] |= burning[:-1]
    out[:-1] |= burning[1:]
    out[:, 1:] |= burning[:, :-1]
    out[:, :-1] |= burning[:, 1:]
    return out


def cluster(grid, seed, periodic=True):
    """Every tree connected to `seed`, by repeated spreading.

    An iterated dilation rather than a recursive flood fill. Recursion blows
    the stack precisely on the large clusters, which are the ones the size
    distribution is about, so it fails exactly where it matters.
    """
    frontier = np.asarray(seed, dtype=bool) & (grid == TREE)
    found = np.zeros(grid.shape, dtype=bool)
    while frontier.any():
        found |= frontier
        frontier = spread(frontier, periodic) & (grid == TREE) & ~found
    return found


def spans(grid, periodic=False):
    """Does a connected group of trees reach from the top edge to the bottom?

    The percolation question, and the reason it needs open boundaries: with
    wrap-around every column already touches every edge and "spanning" stops
    meaning anything.
    """
    top = np.zeros(grid.shape, dtype=bool)
    top[0] = grid[0] == TREE
    return bool((cluster(grid, top, periodic) & (np.arange(grid.shape[0])[:, None]
                                                 == grid.shape[0] - 1)).any())
