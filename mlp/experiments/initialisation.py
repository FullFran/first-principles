"""Where the 2024 initialisation stops working, and why it took width to see.

The notebook drew every weight from rand()*2-1, so the spread was 0.577
whatever the layer looked like. The correct scale shrinks as 1/sqrt(fan_in),
because a unit sums fan_in terms and their variances add.

At the widths that notebook used -- 4 and 8 units -- the two are barely
different and it trained fine. The prediction under test is that the gap
between them grows as sqrt(width), so the same code stops working as soon as
the layers get wide.

What it does when it stops working is the part worth watching. It does not
warn, and it does not sit at a flat loss: it saturates every output at exactly
0 or 1, the derivative is exactly zero everywhere, no gradient flows, and the
training loop reports converged after two epochs. Converged is a statement
about the loss not moving, never about the answer being any good.
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
from datasets import rings, uniform_layers

WIDTHS = (4, 8, 16, 64, 256, 1024)
DEPTH = 4


def slope_at_depth(build, width, seed=1):
    """Mean tanh'(z) in the deepest hidden layer. 1 is linear, 0 is dead."""
    topology = [8] + [width] * DEPTH + [1]
    activations = ["tanh"] * DEPTH + ["sigmoid"]
    network = build(topology, activations, seed)
    inputs = np.random.default_rng(0).normal(size=(64, 8))
    _, (preactivations, _) = model.forward(network, inputs)
    return float(np.mean(model.ACTIVATIONS["tanh"][1](preactivations[-2])))


def main():
    print(f"mean tanh'(z) in the deepest hidden layer, {DEPTH} hidden layers\n")
    print(f"{'width':>7} {'1/sqrt(fan_in)':>16} {'rand()*2-1':>12} {'gap':>8}")
    scaled, uniform = [], []
    for width in WIDTHS:
        scaled.append(slope_at_depth(model.initialise, width))
        uniform.append(slope_at_depth(uniform_layers, width))
        print(f"{width:>7} {scaled[-1]:>16.5f} {uniform[-1]:>12.5f} "
              f"{scaled[-1] / uniform[-1]:>7.1f}x")

    print(f"\nthe consequence, on the rings, {DEPTH} hidden layers of 256:")
    inputs, targets = rings(count=400, seed=0)
    topology = [2] + [256] * DEPTH + [1]
    activations = ["tanh"] * DEPTH + ["sigmoid"]
    print(f"  {'init':>16} {'epochs':>7} {'final loss':>12} {'accuracy':>9} "
          f"{'saturated':>10}  stopped because")
    for label, build in (("1/sqrt(fan_in)", model.initialise),
                         ("rand()*2-1", uniform_layers)):
        network = build(topology, activations, 1)
        result = solve.train(network, inputs, targets, method="sgd", rate=0.5,
                             epochs=120, batch_size=64, seed=0)
        predicted = model.predict(network, inputs)
        saturated = float(np.mean((predicted < 1e-6) | (predicted > 1 - 1e-6)))
        print(f"  {label:>16} {result.epochs:>7} {result.losses[-1]:>12.5f} "
              f"{solve.accuracy(network, inputs, targets):>9.3f} "
              f"{saturated:>10.3f}  {result.reason}")

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.semilogx(WIDTHS, scaled, "o-", lw=1.9, ms=6, label=r"$1/\sqrt{fan_{in}}$")
    ax.semilogx(WIDTHS, uniform, "s--", lw=1.7, ms=6, label="rand()*2-1  (2024)")
    ax.axvspan(4, 8, color="0.75", alpha=0.35)
    ax.annotate("the widths the\nnotebook used", xy=(5.5, 0.55), ha="center",
                fontsize=8.5, color="0.3")
    ax.set(xlabel="units per hidden layer", ylabel="mean slope of the activation",
           ylim=(0, 1.05))
    ax.set_xticks(list(WIDTHS)); ax.set_xticklabels([str(w) for w in WIDTHS])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_title("The same initialiser, made wide", fontsize=11)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "initialisation.png", dpi=140, bbox_inches="tight")
    print(f"\nfigure -> {out / 'initialisation.png'}")


if __name__ == "__main__":
    main()
