"""Does putting out small fires cause big ones?

The argument is widely told: small fires consume fuel, so suppressing them
lets fuel accumulate, so the fire that eventually comes is worse. It is used
to explain Yellowstone in 1988 and a century of US fire policy.

**The prediction I wrote down, and got wrong.** Extinguish every fire below a
size threshold, leave its trees standing, and the tree density should climb and
the largest fire should grow with it.

It does not. Density 0.398 to 0.395 across thresholds from 0 to 200, and total
burned area 1.386M to 1.391M -- unchanged. There is a conservation law in the
way: at steady state the area burned per step is pinned by the area grown per
step, so putting a fire out does not save its fuel, it hands it to the next
one. I was ready to report that the paradox does not appear in this model.

**It does, on a different knob.** The literature puts the mechanism in the
*ignition rate* rather than in fighting fires once started, so this runs that
too: lower f, and the forest grows denser between fires because the fires are
further apart in time. That one is enormous -- 2000x fewer sparks takes the
largest fire from 1.5% of the forest to 98.6%.

Both are here because the difference between them is the part worth knowing.
They are different interventions in the real world too: preventing ignitions is
not the same act as fighting a fire that has started, and the model supports
only one of them.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import lattice as lat
import solve

FIGURES = Path(__file__).resolve().parents[1] / "docs" / "figures"
SIZE, GROWTH, STEPS = 96, 0.05, 5000
RATES = (2e-2, 5e-3, 1e-3, 2e-4, 5e-5, 1e-5)
THRESHOLDS = (0, 10, 50, 200)

INK = "#1b1b1b"
MEASURED, THEORY = "#c0392b", "#2c3e50"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.grid": True,
    "grid.color": "#d8d8d8", "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
})


def suppressed(size, p, f, steps, threshold, seed=0):
    """Like solve.run, but small fires are put out and their trees survive.

    Written here rather than in solve.py because it is not a way of finishing a
    fire -- it is an intervention on top of the model, and it needs to know a
    fire's size before deciding, which no honest fire-fighter does.
    """
    rng = np.random.default_rng(seed)
    grid = lat.empty_grid(size)
    sizes, densities, burned = [], [], 0
    for index in range(steps):
        lat.grow(grid, p, rng)
        for row, column in zip(*np.where(lat.strike(grid, f, rng))):
            if grid[row, column] != lat.TREE:
                continue
            seed_mask = np.zeros(grid.shape, dtype=bool)
            seed_mask[row, column] = True
            doomed = lat.cluster(grid, seed_mask)
            count = int(doomed.sum())
            if count < threshold:
                continue                       # put out; the trees live
            grid[doomed] = lat.EMPTY
            sizes.append(count)
            burned += count
        if index > steps // 3:
            densities.append(lat.density(grid))
    return np.array(sizes), float(np.mean(densities)), burned


def main():
    print(f"L = {SIZE} ({SIZE**2} sites), growth p = {GROWTH}, {STEPS} steps\n")
    print("1. LOWER THE IGNITION RATE")
    print(f"  {'f':>9} {'f/p':>8} {'density':>9} {'fires':>8} {'mean':>9} "
          f"{'largest':>9} {'of lattice':>11}")
    densities, largest, means = [], [], []
    for f in RATES:
        run = solve.run(size=SIZE, p=GROWTH, f=f, steps=STEPS, seed=0)
        densities.append(run.density)
        largest.append(run.largest / SIZE ** 2)
        means.append(run.sizes.mean())
        print(f"  {f:>9.0e} {f/GROWTH:>8.1e} {run.density:>9.3f} "
              f"{len(run.fires):>8} {run.sizes.mean():>9.1f} "
              f"{run.largest:>9} {100*largest[-1]:>10.1f}%")
    print(f"\n  {RATES[0]/RATES[-1]:.0f}x fewer sparks takes the largest fire from "
          f"{100*largest[0]:.1f}% of the forest to {100*largest[-1]:.1f}%.")
    print("  Note the last rows are limited by the box: a fire cannot exceed the")
    print("  lattice, so the effect saturates rather than continuing.")

    print("\n2. PUT OUT THE SMALL FIRES INSTEAD")
    print(f"  {'threshold':>10} {'density':>9} {'fires':>8} {'largest':>9} "
          f"{'total burned':>13}")
    for threshold in THRESHOLDS:
        sizes, density, burned = suppressed(SIZE, GROWTH, 5e-5, STEPS, threshold)
        print(f"  {threshold:>10} {density:>9.3f} {len(sizes):>8} "
              f"{(sizes.max() if len(sizes) else 0):>9} {burned:>13}")
    print("\n  The density does not move and neither does the total burned area,")
    print("  because at steady state burning has to balance growth. Putting a")
    print("  fire out does not save its fuel; it hands it to the next one.")

    fig, (left, right) = plt.subplots(1, 2, figsize=(11.2, 4.4))
    left.semilogx(RATES, densities, "o-", color=THEORY, lw=1.9, ms=6)
    left.axhline(lat.P_C, color="0.45", ls="--", lw=1.3)
    left.annotate(f"$p_c$ = {lat.P_C}", xy=(RATES[-1] * 1.3, lat.P_C + 0.012),
                  color="0.35", fontsize=9)
    left.set(xlabel="lightning rate  $f$", ylabel="tree density")
    left.invert_xaxis()
    left.set_title("Fewer sparks, denser forest", fontsize=10.5, pad=8)

    right.semilogx(RATES, [100 * v for v in largest], "o-", color=MEASURED,
                   lw=1.9, ms=6, label="largest fire")
    right.axhline(100, color="0.45", ls=":", lw=1.3)
    right.annotate("the whole lattice — the measurement saturates here",
                   xy=(RATES[2], 88), fontsize=8.5, color="0.35")
    right.set(xlabel="lightning rate  $f$",
              ylabel="largest fire, % of the forest", ylim=(0, 112))
    right.invert_xaxis()
    right.set_title("and the fires that happen take everything",
                    fontsize=10.5, pad=8)

    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / "ignition.png", dpi=140, facecolor="white",
                bbox_inches="tight", pad_inches=0.22)
    print("\n  figure -> docs/figures/ignition.png")


if __name__ == "__main__":
    main()
