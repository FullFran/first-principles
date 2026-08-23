"""The domain: what a Hopfield network *is*.

An energy function over bipolar states, a rule that writes memories into the
couplings, and the dynamics that walks downhill. No scheduling, no loops, no
convergence logic -- those are choices, and they live in `methods/`.

    methods/ imports model.        model imports nobody.

Conventions
-----------
states      vectors in {-1, +1}^N, stored as int8
weights     symmetric, zero diagonal (no self-coupling)
energy      E(s) = -1/2 s^T W s, with no external field
"""

import numpy as np

__all__ = [
    "hebbian_weights",
    "energy",
    "local_field",
    "update_rule",
    "check_weights",
    "check_state",
    "overlap",
]


def check_state(state):
    """States live on the corners of the hypercube, nowhere else."""
    values = np.unique(state)
    if not set(values.tolist()) <= {-1, 1}:
        raise ValueError(f"states must be bipolar, in {{-1, +1}}; found {values[:5]}")


def check_weights(weights):
    """The two conditions the Lyapunov argument rests on.

    Drop symmetry and energy stops being a function the dynamics minimises;
    keep a nonzero diagonal and a unit can flip on the strength of its own
    current value, which is not a memory, it is a latch.
    """
    if not np.allclose(weights, weights.T):
        raise ValueError("weights must be symmetric; energy descent depends on it")
    if not np.allclose(np.diag(weights), 0.0):
        raise ValueError("weights must have a zero diagonal; no self-coupling")


def hebbian_weights(patterns):
    """Write memories into the couplings: W = (1/N) sum_mu p_mu p_mu^T.

    Neurons that agree across the stored patterns end up positively coupled.
    That is the whole learning rule -- one pass, no gradient, no iteration.
    The diagonal is cleared afterwards.
    """
    patterns = np.atleast_2d(np.asarray(patterns))
    if patterns.shape[0] < 1:
        raise ValueError("need at least one pattern to build the couplings")
    check_state(patterns)

    size = patterns.shape[1]
    weights = patterns.T.astype(float) @ patterns.astype(float) / size
    np.fill_diagonal(weights, 0.0)
    return weights


def energy(weights, state):
    """E(s) = -1/2 s^T W s.

    The quantity the dynamics is trying to lower. Every stored pattern sits in
    a local minimum -- and so does every state nobody asked for that happens
    to sit in one too, which is where spurious attractors come from.
    """
    state = np.asarray(state, dtype=float)
    return float(-0.5 * state @ weights @ state)


def local_field(weights, state):
    """h_i = sum_j W_ij s_j -- the pull the rest of the network exerts on i."""
    return weights @ np.asarray(state, dtype=float)


def update_rule(field, current):
    """Align with the local field; on an exact tie, stay put.

    `np.sign` would return 0 here and drop the unit off the hypercube
    altogether. Holding the current value is the convention that keeps the
    state space closed, and ties are not as rare as they look at small N.
    """
    current = np.asarray(current, dtype=np.int8)
    field = np.asarray(field, dtype=float)
    return np.where(field > 0, 1, np.where(field < 0, -1, current)).astype(np.int8)


def overlap(a, b):
    """m = (1/N) a . b -- 1 for identical states, -1 for exact mirrors."""
    a = np.asarray(a, dtype=float)
    return float(a @ np.asarray(b, dtype=float) / a.size)
