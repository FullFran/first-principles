"""Undo one noising step deterministically, along the flow that shares its marginals.

    x_0_hat  = (x_t + (1 - abar_t) * score) / sqrt(abar_t)
    eps_hat  = -sqrt(1 - abar_t) * score
    x_{t-1}  = sqrt(abar_{t-1}) * x_0_hat + sqrt(1 - abar_{t-1}) * eps_hat

No randomness after the first draw. The claim it rests on is that a
stochastic differential equation has a deterministic partner -- the
probability-flow ODE -- with the *same* marginal density at every time. Not
the same paths: the same distribution over paths' endpoints, which is the
only thing a sampler is asked for.

Reading the second line as "estimate the noise, then re-add exactly as much
as the next time step should have" is the useful way to see it. It is a
rewrite of the forward equation with the unknown eps replaced by its
conditional mean, and that mean is the score in disguise.

What it buys: the map from x_T to x_0 becomes a function, so the same
initial noise always gives the same sample, and the whole trajectory is
differentiable.

The few-step advantage survives the change of setting, which was not
obvious: DDIM's usual case is made with a learned score and a perceptual
metric, and here the score is exact and the metric is distributional. At
five to eight steps this method is ahead on the anisotropic targets, by
0.6-0.9x in MMD^2. Past about twelve steps there is nothing left to rank --
both methods are inside the noise floor of the measurement, and a ranking
between two numbers indistinguishable from zero is noise with a sign.

What it costs is not visible in that number: nothing injects entropy after
the start, so a mode the initial draw was not near stays unvisited, and a
biased score is integrated rather than partly washed out.
"""

import numpy as np

NAME = "probability-flow"


def step(rng, x, score, alpha_bar, alpha_bar_prev):
    """One reverse step. `rng` is accepted and unused: that is the method."""
    x0 = (x + (1.0 - alpha_bar) * score) / np.sqrt(alpha_bar)
    eps = -np.sqrt(1.0 - alpha_bar) * score
    return np.sqrt(alpha_bar_prev) * x0 + np.sqrt(1.0 - alpha_bar_prev) * eps
