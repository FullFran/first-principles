"""Two chains for the same distribution, and only one of them is right.

The target is the unit normal, chosen because every moment of it is known and
a sampler has nowhere to hide. Metropolis is exact at any step size because
rejection enforces detailed balance. Unadjusted Langevin rejects nothing, so
the discretisation leaves a bias -- and on this target the bias has a closed
form, because the update is an AR(1):

    x' = (1 - dt) x + sqrt(2 dt) xi   ->   variance 1/(1 - dt/2)

Prediction before running: Metropolis lands on 1 whatever the step size, and
Langevin lands on 1/(1 - dt/2), which is a curve you can draw in advance.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import distribution as dist
import solve

STEPS = 400_000
SCALES = (0.5, 0.3, 0.2, 0.1, 0.05, 0.02)


def main():
    truth = dist.exact_moment(dist.GAUSSIAN, 1.0, 2)
    print(f"target <x^2> = {truth:.6f},  {STEPS} steps per chain\n")

    print(f"  {'step':>7} {'langevin <x^2>':>20} {'1/(1-dt/2)':>12} {'sigma from 1':>13}")
    measured, errors, predicted = [], [], []
    for scale in SCALES:
        chain = solve.chain("gaussian", "langevin", 1.0, steps=STEPS,
                            scale=scale, seed=0)
        measured.append(chain.mean(2)); errors.append(chain.error(2))
        predicted.append(1.0 / (1.0 - scale / 2.0))
        print(f"  {scale:>7.2f} {measured[-1]:>13.6f}+-{errors[-1]:<6.4f} "
              f"{predicted[-1]:>12.6f} {chain.sigma_from(truth, 2):>13.1f}")

    print(f"\n  {'step':>7} {'metropolis <x^2>':>20} {'acceptance':>11} "
          f"{'tau':>7} {'sigma from 1':>13}")
    for scale in (0.3, 1.0, 3.0):
        chain = solve.chain("gaussian", "metropolis", 1.0, steps=STEPS,
                            scale=scale, seed=0)
        print(f"  {scale:>7.2f} {chain.mean(2):>13.6f}+-{chain.error(2):<6.4f} "
              f"{chain.acceptance:>11.3f} "
              f"{solve.autocorrelation_time(chain.samples[:, 0] ** 2):>7.1f} "
              f"{chain.sigma_from(truth, 2):>13.1f}")

    fig, (left, right) = plt.subplots(1, 2, figsize=(11.2, 4.4))

    grid = np.linspace(0.01, 0.55, 200)
    left.plot(grid, 1.0 / (1.0 - grid / 2.0), color="#2c3e50", lw=1.7,
              label=r"closed form  $1/(1-\Delta t/2)$")
    left.errorbar(SCALES, measured, yerr=errors, fmt="o", color="#c0392b",
                  ms=6, capsize=3, label="langevin, measured")
    left.axhline(truth, color="0.45", ls="--", lw=1.3, label="the target, 1")
    left.set(xlabel=r"step  $\Delta t$", ylabel=r"$\langle x^2 \rangle$")
    left.set_title("The wrong answer has a closed form too", fontsize=10.5, pad=8)
    left.legend(frameon=False, fontsize=9)

    chains = {
        "metropolis": solve.chain("gaussian", "metropolis", 1.0, steps=STEPS,
                                  scale=1.0, seed=0),
        "langevin": solve.chain("gaussian", "langevin", 1.0, steps=STEPS,
                                scale=0.5, seed=0),
    }
    bins = np.linspace(-4, 4, 121)
    for name, colour in (("metropolis", "#2c3e50"), ("langevin", "#c0392b")):
        right.hist(chains[name].samples[:, 0], bins=bins, density=True,
                   histtype="step", lw=1.7, color=colour, label=name)
    centres = 0.5 * (bins[1:] + bins[:-1])
    right.plot(centres, np.exp(-centres ** 2 / 2) / np.sqrt(2 * np.pi), "--",
               color="0.45", lw=1.4, label="the target")
    right.set(xlabel="x", ylabel="density", yscale="log", ylim=(1e-4, 0.6))
    right.set_title(r"Langevin at $\Delta t = 0.5$: too wide, everywhere",
                    fontsize=10.5, pad=8)
    right.legend(frameon=False, fontsize=9)

    fig.tight_layout()
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "gaussian.png", dpi=140, bbox_inches="tight")
    print(f"\nfigure -> {out / 'gaussian.png'}")


if __name__ == "__main__":
    main()
