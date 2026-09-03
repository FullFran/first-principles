"""Run a reverse process and report how far its samples are from the truth.

Owns the schedule, the loop and the verdict, not the mathematics. The domain
supplies the score; `methods/` supplies one step; this file decides how many
steps there are, how big they get, and whether the answer is any good.

The schedule is the only real choice here, and it is about where to spend
steps: abar travels from ~1 to ~0, and spending steps uniformly in t spends
most of them where the density is already Gaussian and nothing is left to
decide.

Being wrong is measurable here in a way it is not for real data, because the
target has a closed form. `discrepancy` is an unbiased MMD against exact
draws, and its own noise floor is measured by comparing exact draws to each
other -- so the threshold is a measurement rather than a guess.
"""

from dataclasses import dataclass

import numpy as np

import process
from methods import ALL as METHODS

__all__ = ["sample", "Samples", "METHODS", "DEFAULT_METHOD", "SCHEDULES",
           "cosine_schedule", "linear_schedule", "discrepancy", "exact_draws",
           "noise_floor"]

DEFAULT_METHOD = "ancestral"
ABAR_MIN = 1e-4
"""Where the schedule stops, not zero: `process` refuses abar below its floor,
and at 1e-4 the remaining signal is already four orders below the noise."""


def cosine_schedule(steps):
    """abar_t = cos^2(pi/2 * (t/T + s)/(1 + s)), the Nichol-Dhariwal form.

    The offset keeps the first step from being a no-op. Returned descending,
    from data to noise, because that is the order the forward process runs
    and the reverse walks it backwards.
    """
    s = 0.008
    t = np.linspace(0.0, 1.0, steps + 1)
    f = np.cos((t + s) / (1.0 + s) * np.pi / 2.0) ** 2
    abar = f / f[0]
    return np.clip(abar, ABAR_MIN, 1.0)


def linear_schedule(steps):
    """The original DDPM schedule: beta linear, abar their running product.

    Kept because it shows what the step count is for. At 200 steps it ends at
    abar = 0.13, so the reverse process starts from pure noise while the
    schedule still claims a tenth of the signal survives; it needs about a
    thousand to reach the floor, which is why the paper used T = 1000.
    """
    beta = np.linspace(1e-4, 0.02, steps)
    abar = np.concatenate([[1.0], np.cumprod(1.0 - beta)])
    return np.clip(abar, ABAR_MIN, 1.0)


SCHEDULES = {"cosine": cosine_schedule, "linear": linear_schedule}


@dataclass(frozen=True)
class Samples:
    """What a run produced, and how far it landed from the target."""
    target: str
    method: str
    schedule: str
    steps: int
    draws: np.ndarray
    discrepancy: float
    noise_floor: float

    @property
    def within_noise(self):
        """True when the gap to the target is inside what exact draws show."""
        return self.discrepancy <= self.noise_floor


def exact_draws(mixture, n, rng):
    """Sample the target directly. The thing the reverse process is imitating."""
    which = rng.choice(mixture.components, size=n, p=mixture.weights)
    out = np.empty((n, mixture.dim))
    for k in range(mixture.components):
        rows = which == k
        if rows.any():
            out[rows] = rng.multivariate_normal(
                mixture.means[k], mixture.covariances[k], size=int(rows.sum())
            )
    return out


def _median_bandwidth(a, b):
    """The median heuristic: a length scale read off the data, not chosen."""
    pooled = np.vstack([a, b])
    take = pooled[:: max(1, len(pooled) // 200)]
    d2 = ((take[:, None, :] - take[None, :, :]) ** 2).sum(-1)
    med = np.median(d2[d2 > 0])
    return np.sqrt(med / 2.0) if med > 0 else 1.0


def discrepancy(a, b, bandwidth=None):
    """Unbiased MMD^2 with a Gaussian kernel, between two sets of draws.

    Unbiased matters: the biased estimator is positive even for two samples
    of the same distribution, so it cannot answer the only question asked.
    """
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    h = _median_bandwidth(a, b) if bandwidth is None else bandwidth

    def k(u, v):
        return np.exp(-((u[:, None, :] - v[None, :, :]) ** 2).sum(-1) / (2 * h * h))

    kaa, kbb, kab = k(a, a), k(b, b), k(a, b)
    n, m = len(a), len(b)
    np.fill_diagonal(kaa, 0.0)
    np.fill_diagonal(kbb, 0.0)
    return (kaa.sum() / (n * (n - 1))
            + kbb.sum() / (m * (m - 1))
            - 2.0 * kab.mean())


def noise_floor(mixture, n, rng, repeats=5):
    """How far two sets of exact draws disagree: the threshold nobody chose.

    Over several pairs and taken at the top, not averaged. One pair is itself
    a noisy number, and a noisy measurement against a noisy threshold is how
    a test becomes a coin flip -- which this one was, passing at 100 steps,
    failing at 200 and passing again at 400 on the same target.
    """
    return max(
        abs(discrepancy(exact_draws(mixture, n, rng), exact_draws(mixture, n, rng)))
        for _ in range(repeats)
    )


def sample(target="bimodal", method=DEFAULT_METHOD, schedule="cosine",
           steps=200, draws=2000, seed=0, score_fn=None):
    """Walk `draws` points from noise back to the target and score the result.

    `score_fn(x, abar) -> array` replaces the exact score. That argument is
    the entry: pass nothing and the sampler runs on the truth, pass a learned
    score and every number below says how much was lost by learning it.
    """
    if target not in process.TARGETS:
        raise ValueError(f"unknown target {target!r}; have {sorted(process.TARGETS)}")
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}; have {sorted(METHODS)}")
    if schedule not in SCHEDULES:
        raise ValueError(f"unknown schedule {schedule!r}; have {sorted(SCHEDULES)}")
    if steps < 1:
        raise ValueError(f"steps must be at least 1, got {steps}")
    if draws < 2:
        raise ValueError(f"draws must be at least 2, got {draws}")

    mixture = process.TARGETS[target]
    stepper = METHODS[method].step
    abar = SCHEDULES[schedule](steps)
    rng = np.random.default_rng(seed)

    if score_fn is None:
        def score_fn(x, ab):
            return process.score(mixture, x, ab)

    x = rng.standard_normal((draws, mixture.dim))
    for i in range(len(abar) - 1, 0, -1):
        x = stepper(rng, x, score_fn(x, abar[i]), abar[i], abar[i - 1])

    truth = exact_draws(mixture, draws, rng)
    return Samples(
        target=target, method=method, schedule=schedule, steps=steps,
        draws=x, discrepancy=discrepancy(x, truth),
        noise_floor=noise_floor(mixture, draws, rng),
    )
