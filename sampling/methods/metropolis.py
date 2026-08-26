"""Propose a move, accept it on a ratio of densities.

    accept with probability  min(1, p(y)/p(x)) = min(1, exp(-(E(y)-E(x))/T))

The normaliser cancels because it appears in both numerator and denominator.
That is the entire trick, it is from 1953, and it is the reason sampling from
an unnormalised density is possible at all.

The chain it builds has the target as its stationary distribution *exactly*,
at any step size, because rejection is what enforces detailed balance:

    p(x) q(x -> y) A(x -> y) = p(y) q(y -> x) A(y -> x)

Rejecting is not wasted work. It is the correction.

What it costs is that the proposal knows nothing about the target -- it is a
blind random walk, and the step size has to be small enough to be accepted
and large enough to go somewhere. Those two demands fight, and in high
dimension the first one wins.
"""

import numpy as np

NAME = "metropolis"


def step(rng, state, target, temperature, scale):
    proposal = state + scale * rng.standard_normal(state.shape)
    change = target.energy(proposal) - target.energy(state)
    # exp of a positive change can overflow; a downhill move is always taken
    if change <= 0 or rng.random() < np.exp(-change / temperature):
        return proposal, True
    return state, False
