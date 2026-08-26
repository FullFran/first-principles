"""Step rules for the same gradient.

A method exposes NAME, initialise(network) -> state, and
step(network, grads, state, rate) -> state. It decides *how far and in what
direction* to move given a gradient; computing that gradient belongs to the
model, and every method here receives exactly the same numbers.
"""

from . import adam, momentum, sgd

ALL = {module.NAME: module for module in (sgd, momentum, adam)}
