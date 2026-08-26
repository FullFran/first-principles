"""Why backpropagation exists at all.

You do not need it to get a gradient. Perturb each parameter, measure how the
loss moves, divide -- that is a derivative, it works, and it is what
tests/test_model.py checks backprop against. So the question the chain rule
answers is not "how do I get a gradient" but "how do I get all P of them
without paying for P of them".

Two measurements, and they are the whole argument:

  1. cost. Finite differences needs two forward passes per parameter, so 2P
     of them. Backpropagation needs one forward and one backward, whatever P
     is. The gap is a ratio, and it grows without limit.
  2. accuracy. A difference quotient is squeezed between truncation error,
     which wants a large step, and cancellation in the subtraction, which
     wants a small one. There is a floor no choice of step gets under, and
     backprop is not near it -- it is exact up to the arithmetic.
"""

import sys
import time
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import model
from datasets import rings

FIGURES = Path(__file__).resolve().parents[1] / "docs" / "figures"
WIDTHS = (4, 8, 16, 32, 64)
STEPS = (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10, 1e-12)

INK, GRID = "#1b1b1b", "#d8d8d8"
MEASURED, THEORY, WARN, COOL = "#c0392b", "#2c3e50", "#e08a1e", "#2e7d94"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
})


def parameters(network):
    return sum(layer.weights.size + layer.bias.size for layer in network)


def difference_quotient(network, inputs, targets, step, central=True):
    """The gradient the slow way. Two forward passes per parameter, or one."""
    loss = model.LOSSES["bce"][0]
    base = None if central else loss(model.forward(network, inputs)[0], targets)
    pieces = []
    for layer in network:
        for tensor in (layer.weights, layer.bias):
            partial = np.zeros_like(tensor)
            for index in np.ndindex(tensor.shape):
                original = tensor[index]
                tensor[index] = original + step
                high = loss(model.forward(network, inputs)[0], targets)
                if central:
                    tensor[index] = original - step
                    low = loss(model.forward(network, inputs)[0], targets)
                    partial[index] = (high - low) / (2 * step)
                else:
                    partial[index] = (high - base) / step
                tensor[index] = original
            pieces.append(partial)
    return np.concatenate([piece.ravel() for piece in pieces])


def cost(inputs, targets, repeats=20):
    print("\n1. THE COST OF A GRADIENT")
    print(f"  {'width':>7} {'parameters':>11} {'backprop (ms)':>15} "
          f"{'differences (ms)':>18} {'ratio':>8}")
    counts, backprop, differences = [], [], []
    for width in WIDTHS:
        network = model.initialise([2, width, width, 1],
                                   ["tanh", "tanh", "sigmoid"], seed=1)
        counts.append(parameters(network))

        start = time.perf_counter()
        for _ in range(repeats):
            model.gradients(network, inputs, targets, "bce")
        backprop.append((time.perf_counter() - start) / repeats * 1000)

        start = time.perf_counter()
        difference_quotient(network, inputs, targets, 1e-6)
        differences.append((time.perf_counter() - start) * 1000)

        print(f"  {width:>7} {counts[-1]:>11} {backprop[-1]:>15.3f} "
              f"{differences[-1]:>18.2f} {differences[-1]/backprop[-1]:>7.0f}x")
    return counts, backprop, differences


def accuracy(inputs, targets):
    print("\n2. THE ACCURACY OF A DIFFERENCE QUOTIENT")
    network = model.initialise([2, 6, 6, 1], ["tanh", "tanh", "sigmoid"], seed=1)
    exact = model.flat_gradient(network, inputs, targets, "bce")
    print(f"  {'step':>10} {'central':>12} {'forward':>12}")
    central, forward = [], []
    for step in STEPS:
        for kind, store in ((True, central), (False, forward)):
            approximate = difference_quotient(network, inputs, targets, step, kind)
            store.append(float(np.max(np.abs(approximate - exact)
                                      / np.maximum(np.abs(exact), 1e-12))))
        print(f"  {step:>10.0e} {central[-1]:>12.2e} {forward[-1]:>12.2e}")
    print(f"  best central: {min(central):.1e}   best forward: {min(forward):.1e}")
    print("  backpropagation is exact up to the arithmetic, at every step size,")
    print("  because it never takes a difference at all.")
    return central, forward


def main():
    inputs, targets = rings(count=64, seed=0)
    counts, backprop, differences = cost(inputs, targets)
    central, forward = accuracy(inputs, targets)

    fig, (left, right) = plt.subplots(1, 2, figsize=(11.2, 4.4))

    left.loglog(counts, differences, "o-", color=MEASURED, lw=1.9, ms=6,
                label="finite differences")
    left.loglog(counts, backprop, "o-", color=THEORY, lw=1.9, ms=6,
                label="backpropagation")
    reference = differences[0] * np.array(counts) / counts[0]
    left.loglog(counts, reference, ":", color="0.5", lw=1.5, label=r"$\propto P$")
    left.annotate(f"{differences[-1]/backprop[-1]:.0f}x at {counts[-1]} parameters",
                  xy=(counts[-1], np.sqrt(differences[-1] * backprop[-1])),
                  xytext=(counts[1] * 1.1, 6.0), color=MEASURED, fontsize=9)
    left.set(xlabel="parameters  $P$", ylabel="time for one full gradient (ms)")
    left.set_title("Cost: 2P forward passes, or one backward one",
                   fontsize=10.5, pad=8)
    left.legend(frameon=False, fontsize=9, loc="upper left")

    right.loglog(STEPS, central, "o-", color=MEASURED, lw=1.9, ms=6,
                 label="central difference")
    right.loglog(STEPS, forward, "s-", color=WARN, lw=1.7, ms=5,
                 label="forward difference")
    right.axhline(min(central), color=COOL, ls="--", lw=1.4)
    right.annotate(f"floor for the best step: {min(central):.0e}",
                   xy=(2e-10, min(central) * 1.6), color=COOL, fontsize=8.5)
    right.annotate("truncation\n(step too big)", xy=(2e-2, 2e-2), fontsize=8.5,
                   color="0.35", ha="center")
    right.annotate("cancellation\n(step too small)", xy=(2e-11, 1.2e-3), fontsize=8.5,
                   color="0.35", ha="center")
    right.set(xlabel="step  $\\varepsilon$",
              ylabel="largest relative error against backpropagation")
    right.invert_xaxis()
    right.set_title("Accuracy: squeezed from both sides", fontsize=10.5, pad=8)
    right.legend(frameon=False, fontsize=9, loc="upper center")

    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / "gradient_cost.png", dpi=140, facecolor="white",
                bbox_inches="tight", pad_inches=0.22)
    plt.close(fig)
    print(f"\n  figure -> docs/figures/gradient_cost.png")


if __name__ == "__main__":
    main()
