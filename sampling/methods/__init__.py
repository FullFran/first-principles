"""Ways to build a chain whose stationary distribution is the target.

A method exposes NAME and step(rng, state, target, temperature, scale), which
returns the next state and whether the move was accepted.

Both methods here work for the same reason: the normaliser Z is a constant,
and neither a ratio of densities nor the gradient of a log density can see a
constant. One exploits the first fact and the other the second, and they pay
for it differently.
"""

from . import langevin, metropolis

ALL = {module.NAME: module for module in (metropolis, langevin)}
