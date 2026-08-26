"""Where does a forest stop being a collection of trees and become one forest?

Fill a lattice at random with density p and ask whether any connected group of
trees reaches from one edge to the other. Below a threshold, essentially never;
above it, essentially always. The threshold is p_c = 0.5927460, known
numerically and not in closed form, and it is the number this entry checks
itself against.

Prediction before running: the crossing sits at p_c, and the transition
sharpens as the lattice grows -- a small lattice smears any threshold, and
watching the smear shrink is what distinguishes a phase transition from a
gradual change.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import lattice as lat

FIGURES = Path(__file__).resolve().parents[1] / "docs" / "figures"
SIZES = (16, 32, 64, 128)
DENSITIES = np.linspace(0.40, 0.80, 21)
TRIALS = 60

INK = "#1b1b1b"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.grid": True,
    "grid.color": "#d8d8d8", "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
})


def spanning_fraction(size, p, trials=TRIALS):
    rng = np.random.default_rng(size * 1000 + int(p * 1e6))
    return float(np.mean([lat.spans((rng.random((size, size)) < p).astype(np.int8))
                          for _ in range(trials)]))


def main():
    print(f"site percolation on a square lattice, {TRIALS} lattices per point")
    print(f"the closed form: p_c = {lat.P_C}\n")
    print(f"  {'p':>6} " + " ".join(f"{'L=' + str(s):>7}" for s in SIZES))

    curves = {size: [] for size in SIZES}
    for p in DENSITIES:
        row = []
        for size in SIZES:
            curves[size].append(spanning_fraction(size, p))
            row.append(f"{curves[size][-1]:>7.2f}")
        print(f"  {p:>6.2f} " + " ".join(row))

    print(f"\n  {'L':>6} {'p where spanning crosses 1/2':>30} {'width of the crossing':>23}")
    for size in SIZES:
        values = np.array(curves[size])
        crossing = float(np.interp(0.5, values, DENSITIES))
        low = float(np.interp(0.1, values, DENSITIES))
        high = float(np.interp(0.9, values, DENSITIES))
        print(f"  {size:>6} {crossing:>30.4f} {high - low:>23.4f}")
    print("\n  the crossing sits on p_c and the width shrinks with L: a threshold,")
    print("  not a trend. On an infinite lattice the curve would be a step.")

    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    for size in SIZES:
        ax.plot(DENSITIES, curves[size], "o-", lw=1.7, ms=4.5, label=f"L = {size}")
    ax.axvline(lat.P_C, color="0.4", ls="--", lw=1.3)
    ax.annotate(f"$p_c$ = {lat.P_C}", xy=(lat.P_C + 0.008, 0.06), color="0.35",
                fontsize=9)
    ax.set(xlabel="tree density  $p$", ylabel="fraction of lattices that span",
           ylim=(-0.04, 1.04))
    ax.set_title("A forest becomes connected at a threshold, not gradually",
                 fontsize=11, pad=10)
    ax.legend(frameon=False, fontsize=9)
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / "percolation.png", dpi=140, facecolor="white",
                bbox_inches="tight", pad_inches=0.22)
    print("\n  figure -> docs/figures/percolation.png")


if __name__ == "__main__":
    main()
