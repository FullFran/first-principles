"""The domain: what noise does to a density, and the score that undoes it.

A forward process that destroys a distribution, and the closed forms that
destruction implies. No sampler, no step schedule, no network -- those are
choices, and they live in `methods/` and `solve.py`.

    methods/ imports process.          process imports nobody.

Conventions
-----------
state       an array of shape (dim,) -- always, even in one dimension
batch       an array of shape (n, dim)
alpha_bar   the scalar abar_t in (0, 1]: the fraction of the signal left at
            time t. 1 is the data, 0 is pure noise. Every closed form here
            takes abar rather than t, because t only ever enters through it

The whole subject exists because of one asymmetry, the mirror of the one in
`sampling/`. There you can evaluate a density anywhere and cannot normalise
it. Here you can *sample* -- you have data -- and cannot evaluate it
anywhere: there is no formula for the density of photographs.

Reversing the forward process needs neither. It needs grad log q_t(x), and a
score is the gradient of a logarithm, so the normaliser differentiates away
before it is ever needed. That is the trick entire.

Which leaves the question this entry exists to answer -- if the score is
learned, how would you know it is right? So the target is a Gaussian
mixture, the one family whose noised score stays exactly computable, because
a Gaussian mixture convolved with Gaussian noise is a Gaussian mixture:

    p_0   = sum_k w_k N(mu_k, Sigma_k)
    q_t   = sum_k w_k N(sqrt(abar) mu_k, abar Sigma_k + (1 - abar) I)

The mixture is not the interesting case. It is the case with an answer key.
"""

from dataclasses import dataclass

import numpy as np

__all__ = [
    "Mixture", "TWO_MOONS_ISH", "BIMODAL", "SHIFTED", "TARGETS",
    "noised_parameters", "log_density", "score", "posterior_mean",
    "expected_noise", "check_alpha_bar",
]

ALPHA_BAR_FLOOR = 1e-8
"""At abar = 0 exactly the mixture has forgotten which component it came
from and the softmax below is over identical logits. Refusing is more
honest than returning -x as if it had been derived."""


def check_alpha_bar(alpha_bar):
    """abar is a fraction of signal, so it lives in (0, 1]."""
    alpha_bar = float(alpha_bar)
    if not ALPHA_BAR_FLOOR <= alpha_bar <= 1.0:
        raise ValueError(
            f"alpha_bar must lie in [{ALPHA_BAR_FLOOR}, 1], got {alpha_bar}"
        )
    return alpha_bar


@dataclass(frozen=True)
class Mixture:
    """A Gaussian mixture: the target, and its own answer key.

    Full covariances rather than scalars on purpose: an isotropic mixture
    hides that the abar -> 1 limit arrives at different times along different
    axes, set by the smallest eigenvalue and not by the average.
    """
    name: str
    weights: np.ndarray     # (k,), sums to 1
    means: np.ndarray       # (k, dim)
    covariances: np.ndarray  # (k, dim, dim)

    def __post_init__(self):
        w, m, c = self.weights, self.means, self.covariances
        if w.ndim != 1 or m.ndim != 2 or c.ndim != 3:
            raise ValueError("weights (k,), means (k, dim), covariances (k, dim, dim)")
        if not (len(w) == len(m) == len(c)):
            raise ValueError(f"{len(w)} weights, {len(m)} means, {len(c)} covariances")
        if c.shape[1] != c.shape[2] or c.shape[1] != m.shape[1]:
            raise ValueError("covariances must be (k, dim, dim) matching means")
        if not np.isclose(w.sum(), 1.0):
            raise ValueError(f"weights must sum to 1, got {w.sum()}")
        if (w < 0).any():
            raise ValueError("weights must be non-negative")

    @property
    def dim(self):
        return self.means.shape[1]

    @property
    def components(self):
        return len(self.weights)


def _as_batch(x, dim):
    """Accept a state or a batch, return a batch and how to give it back."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        if x.shape[0] != dim:
            raise ValueError(f"state of dimension {dim} expected, got {x.shape[0]}")
        return x[None, :], True
    if x.ndim != 2 or x.shape[1] != dim:
        raise ValueError(f"batch of shape (n, {dim}) expected, got {x.shape}")
    return x, False


def noised_parameters(mixture, alpha_bar):
    """The mixture q_t, still a mixture. Means shrink, covariances inflate.

    Returns (means, covariances). The weights do not move: noise does not
    change which component a sample came from, only how well you can tell.
    """
    alpha_bar = check_alpha_bar(alpha_bar)
    eye = np.eye(mixture.dim)
    means = np.sqrt(alpha_bar) * mixture.means
    covariances = alpha_bar * mixture.covariances + (1.0 - alpha_bar) * eye
    return means, covariances


def _logits(mixture, x, alpha_bar):
    """log(w_k) + log N(x; sqrt(abar) mu_k, S_k), shape (n, k). Normalise
    across k for the responsibilities, log-sum-exp for the density."""
    means, covariances = noised_parameters(mixture, alpha_bar)
    out = np.empty((len(x), mixture.components))
    for k, (mu, cov) in enumerate(zip(means, covariances)):
        sign, logdet = np.linalg.slogdet(cov)
        if sign <= 0:
            raise ValueError("a noised covariance was not positive definite")
        delta = x - mu
        quad = np.einsum("ni,ij,nj->n", delta, np.linalg.inv(cov), delta)
        out[:, k] = -0.5 * (quad + logdet + mixture.dim * np.log(2.0 * np.pi))
    return out + np.log(mixture.weights), means, covariances


def _responsibilities(mixture, x, alpha_bar):
    """r_k(x): the posterior over components, by softmax over the logits."""
    logits, means, covariances = _logits(mixture, x, alpha_bar)
    weights = np.exp(logits - logits.max(axis=1, keepdims=True))
    return weights / weights.sum(axis=1, keepdims=True), means, covariances


def log_density(mixture, x, alpha_bar):
    """log q_t(x). Exact, which is the whole point of choosing a mixture."""
    batch, was_state = _as_batch(x, mixture.dim)
    logits, _, _ = _logits(mixture, batch, alpha_bar)
    peak = logits.max(axis=1, keepdims=True)
    out = peak[:, 0] + np.log(np.exp(logits - peak).sum(axis=1))
    return out[0] if was_state else out


def score(mixture, x, alpha_bar):
    """grad_x log q_t(x), in closed form.

        grad log q_t(x) = -sum_k r_k(x) S_k^-1 (x - sqrt(abar) mu_k)

    A responsibility-weighted average of where each component would pull. As
    abar falls the responsibilities flatten, the pulls agree, and the score
    collapses to -x: at the end of the forward process every component looks
    the same and there is nothing left to reverse.
    """
    batch, was_state = _as_batch(x, mixture.dim)
    resp, means, covariances = _responsibilities(mixture, batch, alpha_bar)
    out = np.zeros_like(batch)
    for k, (mu, cov) in enumerate(zip(means, covariances)):
        pull = np.linalg.solve(cov, (batch - mu).T).T
        out -= resp[:, k, None] * pull
    return out[0] if was_state else out


def posterior_mean(mixture, x, alpha_bar):
    """E[x_0 | x_t], by Tweedie's formula rather than by integrating.

        E[x_0 | x_t] = (x_t + (1 - abar) grad log q_t(x_t)) / sqrt(abar)

    Tweedie is not an approximation and does not assume the mixture. It holds
    for any p_0 under Gaussian noising, which is why a denoiser trained on
    photographs is a score estimator without anybody deciding it should be.
    """
    alpha_bar = check_alpha_bar(alpha_bar)
    s = score(mixture, x, alpha_bar)
    return (np.asarray(x, dtype=float) + (1.0 - alpha_bar) * s) / np.sqrt(alpha_bar)


def expected_noise(mixture, x, alpha_bar):
    """E[eps | x_t] = -sqrt(1 - abar) grad log q_t(x_t).

    The identity that lets a network predicting noise stand in for a score.
    At abar = 1 there is no noise to predict and the two sides are 0.
    """
    alpha_bar = check_alpha_bar(alpha_bar)
    return -np.sqrt(1.0 - alpha_bar) * score(mixture, x, alpha_bar)


def _mixture(name, weights, means, covariances):
    return Mixture(
        name=name,
        weights=np.asarray(weights, dtype=float),
        means=np.asarray(means, dtype=float),
        covariances=np.asarray(covariances, dtype=float),
    )


BIMODAL = _mixture(
    "bimodal",
    [0.5, 0.5],
    [[-2.0, 0.0], [2.0, 0.0]],
    [np.diag([0.3, 0.3]), np.diag([0.3, 0.3])],
)
"""Two symmetric wells. The reverse process has to choose, and it chooses
early: by small abar the responsibilities are already committed."""

SHIFTED = _mixture(
    "shifted",
    [0.7, 0.3],
    [[-1.0, -1.0], [2.5, 1.5]],
    [np.diag([0.5, 0.1]), np.diag([0.1, 0.5])],
)
"""Unequal weights, anisotropic and perpendicular. Smallest eigenvalue 0.1,
which is where the abar -> 1 asymptotics actually begin."""

TWO_MOONS_ISH = _mixture(
    "arc",
    [0.25, 0.25, 0.25, 0.25],
    [[-1.5, 0.5], [-0.5, -0.4], [0.5, -0.4], [1.5, 0.5]],
    [np.diag([0.08, 0.08])] * 4,
)
"""Four tight components on an arc: a curved manifold, which is the shape
real data has and a two-well toy does not."""

TARGETS = {m.name: m for m in (BIMODAL, SHIFTED, TWO_MOONS_ISH)}
