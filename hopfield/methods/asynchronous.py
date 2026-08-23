"""Update one unit at a time, in random order.

A sweep is N single-unit updates. Because only one unit moves at a time and W
is symmetric with zero diagonal, each update can only lower the energy or
leave it unchanged -- E is a Lyapunov function, and on a finite state space
that forces convergence to a fixed point. No cycles, ever.

The price is that the trajectory depends on the order, so the run is seeded.
"""

import numpy as np

from model import local_field, update_rule

NAME = "asynchronous"


def sweep(weights, state, rng):
    state = state.copy()
    for unit in rng.permutation(state.size):
        field = weights[unit] @ state
        state[unit] = update_rule(field, state[unit])
    return state
