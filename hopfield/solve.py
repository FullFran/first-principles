"""Drive a method until the network stops moving.

Owns termination, not dynamics: it runs sweeps, records the energy, and stops
on a fixed point or a detected cycle. Every loop that a method would otherwise
have to reimplement lives here once.
"""

from dataclasses import dataclass

import numpy as np

import model
from methods import ALL as METHODS

__all__ = ["relax", "Relaxation", "METHODS", "DEFAULT_METHOD"]

DEFAULT_METHOD = "asynchronous"


@dataclass(frozen=True)
class Relaxation:
    state: np.ndarray
    energies: list
    sweeps: int
    converged: bool
    cycle_length: int | None


def relax(weights, state, method=DEFAULT_METHOD, seed=0, max_sweeps=200):
    """Sweep until the state repeats itself.

    `converged` means a fixed point. `cycle_length` is set when the state
    returns to an earlier one instead -- which synchronous updates can do and
    asynchronous ones cannot.
    """
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}; available: {sorted(METHODS)}")
    weights = np.asarray(weights, dtype=float)
    state = np.asarray(state, dtype=np.int8)
    if state.size != weights.shape[0]:
        raise ValueError(
            f"state length {state.size} does not match {weights.shape[0]} units"
        )
    model.check_weights(weights)
    model.check_state(state)

    solver = METHODS[method]
    rng = np.random.default_rng(seed)

    energies = [model.energy(weights, state)]
    seen = {state.tobytes(): 0}

    for step in range(1, max_sweeps + 1):
        state = solver.sweep(weights, state, rng)
        energies.append(model.energy(weights, state))
        key = state.tobytes()
        if key in seen:
            period = step - seen[key]
            return Relaxation(state, energies, step, period == 1, None if period == 1 else period)
        seen[key] = step

    return Relaxation(state, energies, max_sweeps, False, None)
