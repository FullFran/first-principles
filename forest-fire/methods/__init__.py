"""Two ways to let a fire finish.

A method exposes NAME and burn(grid, seed, rng, p), which sets fire to the
cluster reachable from `seed` and returns how many trees it consumed. It
decides *how long a fire takes relative to the forest growing*; the rule for
what catches fire belongs to the lattice.

That is the model's central assumption made switchable. Drossel-Schwabl is
only critical when fires finish long before anything regrows, and having both
limits available is what lets the entry measure where that stops holding.
"""

from . import instantaneous, synchronous

ALL = {module.NAME: module for module in (instantaneous, synchronous)}
