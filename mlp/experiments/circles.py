"""The original task, reproduced honestly.

Two concentric rings, one hidden stack, three step rules on the same gradient.
The 2024 notebook trained one network with one rule and watched an animation;
this reports what actually happened, with a number attached.

The prediction, before running: all three separate the rings, because the
task is easy and the architecture is more than enough. What they should not
agree on is how long it takes.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

FIGURES = Path(__file__).resolve().parents[1] / "docs" / "figures"

import model
import solve
from datasets import grid, rings

TOPOLOGY = [2, 8, 8, 1]
ACTIVATIONS = ["tanh", "tanh", "sigmoid"]
EPOCHS, RATE, BATCH = 400, 0.5, 64


def main():
    inputs, targets = rings(count=500, seed=0)
    holdout, holdout_targets = rings(count=500, seed=99)

    print(f"{len(inputs)} points, topology {TOPOLOGY}, rate {RATE}, batch {BATCH}\n")
    print(f"{'method':>10} {'final loss':>12} {'train acc':>11} {'held-out acc':>13} "
          f"{'epochs to 0.15':>16}")

    fig, axes = plt.subplots(1, len(solve.METHODS) + 1, figsize=(15, 3.6))
    curves = {}
    for column, name in enumerate(sorted(solve.METHODS)):
        network = model.initialise(TOPOLOGY, ACTIVATIONS, seed=1)
        result = solve.train(network, inputs, targets, method=name, rate=RATE,
                             epochs=EPOCHS, batch_size=BATCH, seed=0)
        curves[name] = result.losses
        reached = next((i for i, v in enumerate(result.losses) if v < 0.15), None)
        print(f"{name:>10} {result.losses[-1]:>12.5f} "
              f"{solve.accuracy(network, inputs, targets):>11.3f} "
              f"{solve.accuracy(network, holdout, holdout_targets):>13.3f} "
              f"{reached if reached is not None else 'never':>16}")

        xs, ys, mesh = grid(inputs)
        surface = model.predict(network, mesh).reshape(len(ys), len(xs))
        ax = axes[column]
        ax.contourf(xs, ys, surface, levels=np.linspace(0, 1, 21), cmap="coolwarm")
        ax.contour(xs, ys, surface, levels=[0.5], colors="white", linewidths=1.6)
        ax.scatter(*inputs[targets[:, 0] == 1].T, s=6, c="#b03a2e", edgecolors="none")
        ax.scatter(*inputs[targets[:, 0] == 0].T, s=6, c="#1f4e79", edgecolors="none")
        ax.set_title(name, fontsize=10)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")

    ax = axes[-1]
    for name, losses in curves.items():
        ax.semilogy(losses, lw=1.7, label=name)
    ax.set(xlabel="epoch", ylabel="loss")
    ax.set_title("the same gradient, three step rules", fontsize=10)
    ax.legend(frameon=False, fontsize=8)

    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "circles.png", dpi=140, facecolor="white",
                bbox_inches="tight", pad_inches=0.22)
    print(f"\nfigure -> docs/figures/circles.png")


if __name__ == "__main__":
    main()
