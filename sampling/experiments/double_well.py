"""Where a chain lies to you, and nothing in the output says so.

Two minima with a barrier between them. The populations are exactly computable
at any temperature, so this is one of the rare cases where you can catch a
sampler being wrong instead of merely suspecting it.

Prediction: at high temperature both chains cross the barrier often and both
recover the right populations. At low temperature the barrier is many times
the thermal energy, crossings become rare, and a chain that starts in the
wrong well may never leave it -- reporting a converged-looking answer with a
shrinking error bar around a number that is not even close.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

FIGURES = Path(__file__).resolve().parents[1] / "docs" / "figures"

import distribution as dist
import solve

STEPS = 300_000
TEMPERATURES = (1.0, 0.5, 0.2, 0.1, 0.05)
SETTINGS = {"metropolis": 0.6, "langevin": 0.002}


def crossings(samples):
    signs = np.sign(samples)
    return int(np.count_nonzero(np.diff(signs) != 0))


def main():
    grid = np.linspace(-2, 2, 200_001)[:, None]
    energy = dist.DOUBLE_WELL.energy(grid)
    barrier = energy[np.abs(grid[:, 0]) < 0.2].min() - energy[grid[:, 0] > 0].min()
    print(f"barrier height above the lower minimum: {barrier:.3f}\n")
    print(f"  {'T':>6} {'barrier/T':>10} {'exact P(x>0)':>13} "
          f"{'metropolis':>22} {'langevin':>22}")

    exact, results = [], {name: [] for name in SETTINGS}
    for temperature in TEMPERATURES:
        exact.append(dist.exact_probability(dist.DOUBLE_WELL, temperature))
        row = ""
        for name, scale in SETTINGS.items():
            chain = solve.chain("double_well", name, temperature, steps=STEPS,
                                scale=scale, start=[-1.0], seed=1)
            fraction = float(np.mean(chain.samples[:, 0] > 0))
            results[name].append(fraction)
            row += f" {fraction:>10.4f} ({crossings(chain.samples[:, 0]):>6} x)"
        print(f"  {temperature:>6.2f} {barrier/temperature:>10.1f} "
              f"{exact[-1]:>13.4f}{row}")

    print("\n  the count in brackets is barrier crossings. Zero crossings means")
    print("  the chain never sampled the distribution -- only one well of it.")

    fig, (left, right) = plt.subplots(1, 2, figsize=(11.2, 4.4))

    axis = np.linspace(-2, 2, 800)
    left.plot(axis, dist.DOUBLE_WELL.energy(axis[:, None]), color="#2c3e50", lw=1.8)
    left.set(xlabel="x", ylabel="energy  $E(x)$")
    left.set_title("Two minima, one barrier, tilted right", fontsize=10.5, pad=8)

    right.plot(TEMPERATURES, exact, "o-", color="0.35", lw=1.8, ms=6,
               label="exact, by quadrature")
    for name, colour in (("metropolis", "#2c3e50"), ("langevin", "#c0392b")):
        right.plot(TEMPERATURES, results[name], "o--", color=colour, lw=1.7,
                   ms=6, label=name)
    right.annotate("never left the wrong well", xy=(0.05, 0.02),
                   xytext=(0.16, 0.18), color="#c0392b", fontsize=9,
                   arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.2))
    right.set(xlabel="temperature", ylabel="fraction of time in the right well",
              xscale="log", ylim=(-0.05, 1.08))
    right.invert_xaxis()
    right.set_title("Cooling does not make a chain more careful",
                    fontsize=10.5, pad=8)
    right.legend(frameon=False, fontsize=9, loc="lower left")

    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "double_well.png", dpi=140, facecolor="white",
                bbox_inches="tight", pad_inches=0.22)
    print(f"\nfigure -> docs/figures/double_well.png")


if __name__ == "__main__":
    main()
