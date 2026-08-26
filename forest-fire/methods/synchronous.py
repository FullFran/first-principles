"""A fire advances one ring per growth step, and the forest keeps growing.

The literal cellular automaton: every step, burning sites become empty, their
tree neighbours catch, and empty sites sprout with probability p -- including
sites the fire has already been through and sites just ahead of the front.

That last clause is the whole difference. A fire large enough to take many
steps is burning through a forest that is regrowing behind and beside it, so
the area it consumes is no longer the cluster that was standing when it
started. It can exceed it.

Both files compute the same thing in the limit that matters. Watching them
part company as f/p rises is how the entry measures what "separation of
timescales" is worth.

And above a growth rate of roughly 0.1 this fire **never goes out**. The forest
regrows behind the front fast enough to feed it forever, so the CA has a
transition of its own into endemic fire that the instantaneous version cannot
have, because in that one nothing grows while anything is burning. Measured:
at p = 0.005 a fire lasts 4 rings, at p = 0.02 and 0.05 about 50, and at
p = 0.1 it was still going after 3000. That is why `max_rings` exists and why
it raises instead of returning a number.
"""

import numpy as np

from lattice import EMPTY, FIRE, TREE, grow, spread

NAME = "synchronous"


def burn(grid, seed, rng, p, max_rings=10_000):
    """Run the fire to completion, growing the forest at every ring.

    Raises if the fire outlives `max_rings`, which is not a safety valve on a
    slow loop -- it is the model telling you the fire has become endemic and
    there is no size to report.
    """
    grid[seed & (grid == TREE)] = FIRE
    consumed = 0
    for _ in range(max_rings):
        burning = grid == FIRE
        if not burning.any():
            return consumed
        grid[burning] = EMPTY
        consumed += int(burning.sum())
        grid[spread(burning) & (grid == TREE)] = FIRE
        grow(grid, p, rng)
    raise RuntimeError(
        f"fire still burning after {max_rings} rings at p = {p}: regrowth is "
        "feeding the front faster than it burns out, so the fire never ends "
        "and has no size. Lower p, or use the instantaneous method.")
