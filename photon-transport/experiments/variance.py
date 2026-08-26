"""Two unbiased estimators, and one of them is free.

Both answer the same question and the contract suite pins both against Beer-
Lambert, so neither is more correct than the other. What differs is how much
of the randomness each one keeps.

The analog estimator throws a die per photon and records a yes or a no, so its
variance is binomial, T(1-T), and no amount of understanding the geometry
improves it. The weighted estimator integrates that die analytically and keeps
only the randomness it cannot avoid -- the spread of path lengths across the
cone. Close the cone and that spread goes to zero with it.

Prediction: the ratio between them grows without bound as the cone narrows,
and the analog variance does not move at all.
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
from methods import ALL as METHODS

MU, THICKNESS, PHOTONS = 1.0, 1.0, 400_000
ANGLES = np.array([45, 30, 20, 15, 10, 7, 5, 3, 2, 1])


def variance(method, half_angle, seed=0):
    rng = np.random.default_rng(seed)
    cos_theta, _ = physics.sample_direction(rng, PHOTONS, half_angle)
    return float(np.var(METHODS[method].contributions(
        rng, cos_theta, MU, THICKNESS), ddof=1))


def main():
    print(f"mu*L = {MU * THICKNESS}, {PHOTONS} photons per point\n")
    print(f"{'cone':>7} {'T':>10} {'binomial T(1-T)':>17} {'analog var':>13} "
          f"{'weighted var':>15} {'ratio':>12}")

    analog, weighted, ratios = [], [], []
    for degrees in ANGLES:
        half_angle = np.radians(degrees)
        reference = physics.cone_transmittance(MU, THICKNESS, half_angle)
        analog.append(variance("analog", half_angle))
        weighted.append(variance("weighted", half_angle))
        ratios.append(analog[-1] / weighted[-1])
        print(f"{degrees:>6}d {reference:>10.6f} {reference*(1-reference):>17.6f} "
              f"{analog[-1]:>13.6f} {weighted[-1]:>15.3e} {ratios[-1]:>12.3e}")

    budget = solve.transmitted(MU, THICKNESS, np.radians(45), PHOTONS, "analog",
                               seed=0).error
    print(f"\nto match the analog error bar of {budget:.6f} at {PHOTONS} photons,")
    for degrees in (45, 15, 5):
        needed = max(2, int(np.ceil(PHOTONS * variance("weighted", np.radians(degrees))
                                    / variance("analog", np.radians(degrees)))))
        print(f"  a {degrees:>2}-degree cone needs {needed:>7} weighted photons "
              f"({PHOTONS // needed:>6}x fewer)")

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.loglog(ANGLES, analog, "o-", color="#c0392b", lw=1.9, ms=6,
              label="analog: binomial, and blind to the cone")
    ax.loglog(ANGLES, weighted, "o-", color="#2c3e50", lw=1.9, ms=6,
              label="weighted: only the spread of path lengths")
    reference_slope = weighted[0] * (ANGLES / ANGLES[0]) ** 4
    ax.loglog(ANGLES, reference_slope, ":", color="0.5", lw=1.5,
              label=r"$\propto \alpha^{4}$")
    ax.annotate(f"{ratios[-1]:.0e} times apart\nat one degree",
                xy=(ANGLES[-1] * 1.15, np.sqrt(analog[-1] * weighted[-1])),
                fontsize=9, color="0.25")
    ax.set(xlabel="cone half-angle (degrees)", ylabel="variance per photon")
    ax.invert_xaxis()
    ax.set_title("Same answer, same photons, and one keeps almost no randomness",
                 fontsize=11, pad=10)
    ax.legend(frameon=False, fontsize=9, loc="center left")
    fig.tight_layout()

    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "variance.png", dpi=140, facecolor="white",
                bbox_inches="tight", pad_inches=0.22)
    print(f"\nfigure -> docs/figures/variance.png")


if __name__ == "__main__":
    main()
