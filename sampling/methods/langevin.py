"""Follow the gradient downhill and add noise proportional to the temperature.

    x <- x - grad(E) * dt + sqrt(2 * T * dt) * xi

The normaliser vanishes here too, for a different reason. The drift is the
gradient of the log density,

    grad log p = -grad(E)/T - grad(log Z) = -grad(E)/T

and the gradient of a constant is zero. That quantity has a name -- the score
-- and a diffusion model is a network that learns it instead of deriving it
from an energy anyone wrote down.

Set T = 0 and this is the gradient descent of `mlp/`. Set the energy to zero
and it is Brownian motion, with mean square displacement 2*T*t. It contains
both, and the interesting behaviour is in between.

What it costs is that this is unadjusted: nothing rejects, so nothing enforces
detailed balance, and the discretisation leaves a bias of order dt that does
not go away with more samples. It is a chain for a distribution *near* the
target. `docs`-level detail: on E = x^2/2 the stationary variance is exactly
1/(1 - dt/2) rather than 1, which is a closed form for being wrong.
"""

import numpy as np

NAME = "langevin"


def step(rng, state, target, temperature, scale):
    """`scale` is the time step dt, not a proposal width."""
    drift = target.gradient(state) * scale
    noise = np.sqrt(2.0 * temperature * scale) * rng.standard_normal(state.shape)
    # nothing is ever rejected, which is exactly where the bias comes from
    return state - drift + noise, True
