"""Undo one noising step by sampling from an approximation of its reverse.

    x_{t-1} <- (x_t + (1 - alpha_t) * score) / sqrt(alpha_t) + sigma_t * z

The forward step added Gaussian noise, so the exact reverse q(x_{t-1} | x_t)
is not Gaussian -- it is a Gaussian mixed over everything x_0 could have
been. The method works because for a small enough step it is *close* to
Gaussian, with a mean the score gives and a variance the schedule gives.

The noise term is the difference between this and `probability_flow`. It is
not decoration: dropping it while keeping this mean does not give you a
deterministic version of the same process, it gives you a different one, and
the drift here is wrong for that one by a factor of two on the score.
"""

import numpy as np

NAME = "ancestral"


def step(rng, x, score, alpha_bar, alpha_bar_prev):
    """One reverse step. `score` is grad log q_t already evaluated at `x`.

    The method never sees the target. It is handed a slope and asked to walk
    up it, which is exactly why the same code runs on an exact score and on
    a learned one.
    """
    alpha = alpha_bar / alpha_bar_prev
    mean = (x + (1.0 - alpha) * score) / np.sqrt(alpha)
    if alpha_bar_prev >= 1.0:
        # arriving at the data: there is no noise left to add
        return mean
    variance = (1.0 - alpha_bar_prev) / (1.0 - alpha_bar) * (1.0 - alpha)
    return mean + np.sqrt(variance) * rng.standard_normal(x.shape)
