"""Does the simulation reproduce the law it was built from?

Beer-Lambert is not an input to either estimator. The analog one samples free
paths and counts survivors; the weighted one integrates the survival
probability. That both land on exp(-mu*L/cos(theta)), averaged over the cone,
is the check that the sampling is right.

Prediction before running: a straight line on a log axis for a collimated
beam, with a slope of exactly -mu, and a curve that bends away from it as the
cone opens, because tilted photons cross more material.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

FIGURES = Path(__file__).resolve().parents[1] / "docs" / "figures"

import physics
import solve

MU = 1.0
THICKNESSES = np.linspace(0.0, 5.0, 11)
PHOTONS = 100_000


def main():
    print(f"mu = {MU} per unit length, {PHOTONS} photons per point\n")
    fig, ax = plt.subplots(figsize=(8.2, 4.8))

    for half_angle, colour in ((0.0, "#2c3e50"), (np.pi / 4, "#c0392b")):
        label = f"{np.degrees(half_angle):.0f} degree cone"
        print(f"--- {label} ---")
        print(f"  {'thickness':>10} {'analytic':>11} {'analog':>22} {'weighted':>22}")
        exact, analog, weighted, errors = [], [], [], []
        # A different seed per point, on purpose. Reusing one seed across a
        # sweep reuses the same free paths, so every point is pulled the same
        # way and an honest 1-sigma scatter reads as a systematic bias. The
        # error bars are right either way; only the eye is fooled.
        for index, thickness in enumerate(THICKNESSES):
            reference = physics.cone_transmittance(MU, thickness, half_angle)
            a = solve.transmitted(MU, thickness, half_angle, PHOTONS, "analog", seed=index)
            w = solve.transmitted(MU, thickness, half_angle, PHOTONS, "weighted", seed=index)
            exact.append(reference); analog.append(a.value)
            weighted.append(w.value); errors.append(a.error)
            print(f"  {thickness:>10.2f} {reference:>11.6f} "
                  f"{a.value:>13.6f}+-{a.error:<7.5f} "
                  f"{w.value:>13.6f}+-{w.error:<7.5f}")

        grid = np.linspace(0, THICKNESSES[-1], 300)
        ax.semilogy(grid, [physics.cone_transmittance(MU, t, half_angle) for t in grid],
                    color=colour, lw=1.6, label=f"closed form, {label}")
        ax.errorbar(THICKNESSES, analog, yerr=errors, fmt="o", color=colour,
                    ms=5, mfc="white", mew=1.4, capsize=3,
                    label=f"analog, {label}")
        print()

    ax.set(xlabel="slab thickness  (mean free paths)", ylabel="transmitted fraction",
           ylim=(1e-3, 1.5))
    ax.set_title("Beer-Lambert recovered, and bent by the cone", fontsize=11, pad=10)
    ax.legend(frameon=False, fontsize=8.5)
    fig.tight_layout()

    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "beer_lambert.png", dpi=140, facecolor="white",
                bbox_inches="tight", pad_inches=0.22)
    print(f"figure -> docs/figures/beer_lambert.png")


if __name__ == "__main__":
    main()
