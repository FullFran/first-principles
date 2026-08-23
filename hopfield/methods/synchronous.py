"""Update every unit at once from the same field.

One matrix-vector product per sweep, so it is much faster -- and it gives up
the guarantee. With all units moving together the Lyapunov argument breaks:
the network reaches a fixed point *or* a period-2 oscillation, and the energy
is free to rise on the way. That is a real property of the dynamics, not a
defect of the implementation, which is why the contract suite does not ask
this method for monotone descent.
"""

from model import local_field, update_rule

NAME = "synchronous"


def sweep(weights, state, rng):
    return update_rule(local_field(weights, state), state)
