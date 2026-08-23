"""Update schedules for the same energy function.

A method exposes NAME and sweep(weights, state, rng) -> new state. It decides
*when* units are updated; what an update is belongs to the model.
"""

from . import asynchronous, synchronous

ALL = {module.NAME: module for module in (asynchronous, synchronous)}
