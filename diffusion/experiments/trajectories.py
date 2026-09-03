"""The two ways back, drawn as paths -- and what the deterministic one is.

The contract suite says both methods land in the target. A distributional
distance integrates the paths away, so it cannot show what separates them.

Top: twelve trajectories from the *same* twelve starting points, so every
difference on the page is the method and not the seed. The deterministic
paths never cross. The stochastic ones cross constantly.

Bottom left is the claim this experiment exists for. In one dimension the
probability-flow ODE is not merely deterministic, it is **the monotone
quantile transport map**: a start at the u-th quantile of the noise lands at
the u-th quantile of the target. That is why the paths cannot cross, why the
endpoints are not at the modes -- quantiles go to quantiles, not everything
to maxima -- and why the mode a run reaches is decided entirely by its first
draw. Ancestral, on the same axis, is flat: it forgets where it began.

Bottom right: the transport map is exact only in the limit. The error is
first order in the step count, which is what a first-order integrator gives
and is worth seeing rather than assuming.

Prediction before running: the deterministic endpoints trace the exact
quantile curve, and ancestral traces a horizontal line.
"""

import math
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import process  # noqa: E402
import solve  # noqa: E402
from methods import ancestral, probability_flow  # noqa: E402

FIGURES = Path(__file__).resolve().parent.parent / "docs" / "figures"
MIXTURE = process.BIMODAL


def normal_cdf(x, mean=0.0, sd=1.0):
    """No scipy: the entry brings no dependency it does not already have."""
    return 0.5 * (1.0 + math.erf((x - mean) / (sd * math.sqrt(2.0))))


def target_cdf(v):
    """The marginal CDF of the mixture along x, which is what the map acts on."""
    return sum(
        w * normal_cdf(v, mu[0], math.sqrt(cov[0, 0]))
        for w, mu, cov in zip(MIXTURE.weights, MIXTURE.means, MIXTURE.covariances)
    )


def target_quantile(u, low=-10.0, high=10.0, tol=1e-12):
    """Bisection. The CDF is monotone, so nothing cleverer is needed."""
    for _ in range(200):
        mid = 0.5 * (low + high)
        if target_cdf(mid) < u:
            low = mid
        else:
            high = mid
        if high - low < tol:
            break
    return 0.5 * (low + high)


def walk(module, start, seed, steps, keep_path=False):
    rng = np.random.default_rng(seed)
    abar = solve.cosine_schedule(steps)
    x = start.copy()
    path = [x.copy()]
    for i in range(len(abar) - 1, 0, -1):
        x = module.step(rng, x, process.score(MIXTURE, x, abar[i]),
                        abar[i], abar[i - 1])
        if keep_path:
            path.append(x.copy())
    return np.array(path) if keep_path else x


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    starts = np.stack([np.linspace(-2.5, 2.5, 12), np.zeros(12)], axis=1)

    fig = plt.figure(figsize=(13, 9))
    top = [fig.add_subplot(2, 2, 1), fig.add_subplot(2, 2, 2)]
    for axis, (module, title) in zip(
            top, [(ancestral, "ancestral"), (probability_flow, "probability flow")]):
        path = walk(module, starts, seed=5, steps=120, keep_path=True)
        for lane in range(path.shape[1]):
            axis.plot(path[:, lane, 0], path[:, lane, 1], lw=1.0)
        axis.scatter(path[0, :, 0], path[0, :, 1], c="k", s=18, zorder=3,
                     label="start (pure noise)")
        axis.scatter(path[-1, :, 0], path[-1, :, 1], c="r", s=28, zorder=3,
                     label="end")
        axis.scatter(MIXTURE.means[:, 0], MIXTURE.means[:, 1], marker="x",
                     c="k", s=90, zorder=4, label="modes")
        axis.set_title(f"{title}: twelve paths, same twelve starts")
        axis.set_xlim(-4, 4)
        axis.set_ylim(-3, 3)
        axis.legend(loc="upper right", fontsize=8)

    # --- the transport map ---
    probe = np.linspace(-2.6, 2.6, 21)
    exact = np.array([target_quantile(normal_cdf(x)) for x in probe])
    flow = np.array([walk(probability_flow, np.array([[x, 0.0]]), 0, 400)[0, 0]
                     for x in probe])
    stoch = np.array([walk(ancestral, np.array([[x, 0.0]]), 7, 400)[0, 0]
                      for x in probe])

    left = fig.add_subplot(2, 2, 3)
    left.plot(probe, exact, "k-", lw=2, label=r"exact quantile map $F^{-1}(\Phi(x))$")
    left.plot(probe, flow, "o", ms=5, label="probability flow, 400 steps")
    left.plot(probe, stoch, "s", ms=4, label="ancestral, 400 steps")
    for mode in MIXTURE.means[:, 0]:
        left.axhline(mode, ls=":", c="grey", lw=0.8)
    left.set_xlabel("start $x$ (a draw from the noise)")
    left.set_ylabel("endpoint")
    left.legend(fontsize=8)
    left.set_title("where a given start lands")

    # --- and how fast it gets there ---
    counts = [50, 100, 200, 400, 800, 1600]
    errors = []
    print(f"{'steps':>7} {'worst error':>13} {'halving':>9}")
    for steps in counts:
        got = np.array([walk(probability_flow, np.array([[x, 0.0]]), 0, steps)[0, 0]
                        for x in probe])
        errors.append(np.abs(got - exact).max())
        ratio = f"{errors[-2] / errors[-1]:.1f}x" if len(errors) > 1 else "--"
        print(f"{steps:7d} {errors[-1]:13.2e} {ratio:>9}")

    right = fig.add_subplot(2, 2, 4)
    right.loglog(counts, errors, "o-", label="measured")
    right.loglog(counts, errors[0] * counts[0] / np.array(counts), "k--",
                 label=r"$1/N$")
    right.set_xlabel("steps")
    right.set_ylabel("worst error against the exact map")
    right.legend(fontsize=8)
    right.set_title("first order, over five doublings")

    fig.tight_layout()
    fig.savefig(FIGURES / "trajectories.png", dpi=140, facecolor="white",
                bbox_inches="tight")
    print("\n  figure -> docs/figures/trajectories.png")
    print(f"  ancestral endpoint spread over a 5.2-wide range of starts: "
          f"{stoch.max() - stoch.min():.3f}")


if __name__ == "__main__":
    main()
