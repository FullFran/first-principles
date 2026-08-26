"""How much does the shape of the landscape cost you?

Stretch one input axis and the problem is untouched: same points, same
labels, separable by the same shape. What changes is the geometry of the
surface the optimiser walks over -- the contours go from round to a long
narrow canyon, and the gradient stops pointing at the minimum.

The claim under test, from chapter 10 of the book: conditioning does not
change the cost of a step. It changes how many steps you need.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import model
import solve
from datasets import rings

STRETCHES = (1, 3, 10, 30, 100, 300)
TARGET, RATE, BUDGET = 0.15, 0.05, 400


def epochs_to_reach(method, inputs, targets):
    network = model.initialise([2, 8, 8, 1], ["tanh", "tanh", "sigmoid"], seed=1)
    for epoch in range(1, BUDGET + 1):
        result = solve.train(network, inputs, targets, method=method, rate=RATE,
                             epochs=1, batch_size=64, seed=epoch, tolerance=0.0)
        if result.losses[-1] < TARGET:
            return epoch
    return None


def main():
    print(f"epochs to push the loss below {TARGET}, budget {BUDGET}, rate {RATE}\n")
    names = sorted(solve.METHODS)
    print(f"{'stretch':>9} " + " ".join(f"{n:>10}" for n in names))

    results = {name: [] for name in names}
    for stretch in STRETCHES:
        inputs, targets = rings(count=400, seed=0, stretch=float(stretch))
        row = []
        for name in names:
            hit = epochs_to_reach(name, inputs, targets)
            results[name].append(hit)
            row.append(f"{hit if hit else '>' + str(BUDGET):>10}")
        print(f"{stretch:>9} " + " ".join(row))

    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    for name in names:
        shown = [v if v is not None else np.nan for v in results[name]]
        ax.loglog(STRETCHES, shown, "o-", lw=1.8, ms=6, label=name)
        for stretch, value in zip(STRETCHES, results[name]):
            if value is None:
                ax.plot(stretch, BUDGET, "x", ms=9, color="0.35")
    ax.annotate("x = never, inside the budget", xy=(STRETCHES[0] * 1.1, BUDGET * 0.72),
                fontsize=8.5, color="0.35")
    ax.set(xlabel="stretch applied to one input axis",
           ylabel=f"epochs to reach loss {TARGET}")
    ax.set_title("The same problem, a worse-shaped landscape", fontsize=11)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "conditioning.png", dpi=140, bbox_inches="tight")
    print(f"\nfigure -> {out / 'conditioning.png'}")


if __name__ == "__main__":
    main()
