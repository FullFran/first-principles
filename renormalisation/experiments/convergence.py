"""Does a bigger block give a better answer?

The renormalisation group turns a critical point into a fixed point of a map,
and the map is computable by hand for a block of two. The obvious next question
is whether enlarging the block improves the number.

Prediction, written down first: it does, and the plain scheme converges on
p_c = 0.5927460 and nu = 4/3 as the block grows.

That is half right, and finding out which half is the experiment. Three rules
for when a coarse block counts as occupied, two ways of pairing blocks, and the
true values known independently.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import flow
import solve

# experiments/out/ is scratch and gitignored. These move to docs/figures/
# when a derivation argues from them, and not before -- an orphan
# docs/ directory is the map claiming something that is not there.
FIGURES = Path(__file__).resolve().parents[1] / "docs" / "figures"
SIZES = (2, 3, 4)
INK, MEASURED, THEORY, WARN = "#1b1b1b", "#c0392b", "#2c3e50", "#e08a1e"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.grid": True,
    "grid.color": "#d8d8d8", "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
})


def main():
    print(f"true values: p_c = {flow.P_C}, nu = {flow.NU:.6f}\n")

    print("1. THE PLAIN SCHEME: a block of b sites down to one site")
    print(f"  {'rule':>9} {'b':>3} {'p*':>10} {'error':>8} {'nu':>9} {'error':>8}")
    plain = {rule: [] for rule in flow.RULES}
    for rule in flow.RULES:
        for size in SIZES:
            result = solve.scheme(size, rule)
            plain[rule].append(result)
            print(f"  {rule:>9} {size:>3} {result.fixed_point:>10.6f} "
                  f"{result.error_in_threshold():>7.1%} {result.exponent:>9.4f} "
                  f"{result.error_in_exponent():>7.1%}")
        print()

    print("  The prediction failed for `vertical`: 0.618, 0.619, 0.619 -- it does")
    print("  not converge, it sits still. Asking for a top-to-bottom path only is")
    print("  a biased criterion and a bigger block does not cure the bias.")
    print("  `either` and `both` do improve, and they bracket the truth from")
    print("  opposite sides, which is worth more than one number that is close.\n")

    print("2. CELL TO CELL: solve R_small(p) = R_large(p) instead of R(p) = p")
    print(f"  {'rule':>9} {'blocks':>8} {'p*':>10} {'error':>8} {'nu':>9} {'error':>8}")
    paired = {}
    for rule in flow.RULES:
        for small, large in ((2, 3), (3, 4), (2, 4)):
            result = solve.cell_to_cell(small, large, rule)
            paired[(rule, small, large)] = result
            print(f"  {rule:>9} {f'{small},{large}':>8} {result.fixed_point:>10.6f} "
                  f"{result.error_in_threshold():>7.1%} {result.exponent:>9.4f} "
                  f"{result.error_in_exponent():>7.1%}")
        print()

    best = paired[("either", 3, 4)]
    print(f"  The best of them reaches {best.fixed_point:.6f} against "
          f"{flow.P_C}, which is {best.error_in_threshold():.1%},")
    print("  out of blocks of at most sixteen sites. Comparing two blocks rather")
    print("  than a block against a site cancels most of what the block rule gets")
    print("  wrong, because both sides are then the same kind of object.")

    fig, (left, right) = plt.subplots(1, 2, figsize=(11.2, 4.4))
    for rule, colour in zip(flow.RULES, (WARN, MEASURED, THEORY)):
        left.plot(SIZES, [r.fixed_point for r in plain[rule]], "o-", color=colour,
                  lw=1.8, ms=6, label=f"plain, {rule}")
    left.plot([2, 3, 4], [paired[("either", 2, 3)].fixed_point,
                          paired[("either", 3, 4)].fixed_point,
                          paired[("either", 2, 4)].fixed_point], "s--",
              color="#2e7d94", lw=1.7, ms=6, label="cell to cell, either")
    left.axhline(flow.P_C, color="0.4", ls="--", lw=1.4)
    left.annotate(f"$p_c$ = {flow.P_C}", xy=(2.05, flow.P_C + 0.012), fontsize=9,
                  color="0.35")
    left.set(xlabel="block size  $b$", ylabel="fixed point  $p^{\\ast}$")
    left.set_xticks(SIZES)
    left.set_title("A bigger block is not the fix", fontsize=10.5, pad=8)
    left.legend(frameon=False, fontsize=8.5)

    labels, errors, colours = [], [], []
    for rule in flow.RULES:
        labels.append(f"plain\n{rule}\nb=4")
        errors.append(100 * plain[rule][-1].error_in_exponent())
        colours.append("0.55")
    for small, large in ((2, 3), (3, 4), (2, 4)):
        labels.append(f"cell-cell\neither\n{small},{large}")
        errors.append(100 * paired[("either", small, large)].error_in_exponent())
        colours.append(MEASURED)
    right.bar(range(len(errors)), errors, color=colours, width=0.62)
    right.set_xticks(range(len(errors)))
    right.set_xticklabels(labels, fontsize=8)
    right.set(ylabel=r"error in $\nu$  (%)")
    right.set_title(r"and the exponent is the harder number", fontsize=10.5, pad=8)

    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / "convergence.png", dpi=140, facecolor="white",
                bbox_inches="tight", pad_inches=0.22)
    print("\n  figure -> docs/figures/convergence.png")


if __name__ == "__main__":
    main()
