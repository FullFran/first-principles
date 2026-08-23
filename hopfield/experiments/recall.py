"""Store four patterns, then hand the network a corrupted one back.

Reproduces the first two results of the class activity: the stored patterns
with their energies, and reconstruction from a noisy input while the energy
falls. The energy trace is the point -- recall is not pattern matching, it is
a walk downhill on E(s) = -1/2 s^T W s, which is Metropolis at T = 0.
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
from patterns import NAMES, SHAPE, library

NOISE = 0.25
SEED = 0


def corrupt(pattern, fraction, rng):
    noisy = pattern.copy()
    idx = rng.choice(pattern.size, size=int(fraction * pattern.size), replace=False)
    noisy[idx] *= -1
    return noisy


def main():
    patterns = library()
    weights = model.hebbian_weights(patterns)
    rng = np.random.default_rng(SEED)

    print(f"N = {patterns.shape[1]} units, P = {len(patterns)} patterns, "
          f"load = {len(patterns) / patterns.shape[1]:.4f}\n")

    print(f"{'pattern':>10} {'energy':>12} {'E/N':>10}")
    for name, p in zip(NAMES, patterns):
        e = model.energy(weights, p)
        print(f"{name:>10} {e:>12.2f} {e / p.size:>10.4f}")

    random_energy = np.mean([
        model.energy(weights, rng.choice([-1, 1], size=patterns.shape[1]))
        for _ in range(200)
    ])
    print(f"\n{'random state':>10} {random_energy:>12.2f} "
          f"{random_energy / patterns.shape[1]:>10.4f}   (mean of 200)")

    fig, axes = plt.subplots(3, len(patterns), figsize=(11, 8.5))
    print(f"\nrecall from {NOISE:.0%} flipped bits")
    print(f"{'pattern':>10} {'overlap in':>12} {'overlap out':>12} {'sweeps':>8} {'dE':>12}")

    for col, (name, target) in enumerate(zip(NAMES, patterns)):
        noisy = corrupt(target, NOISE, rng)
        result = solve.relax(weights, noisy, method="asynchronous", seed=SEED)

        print(f"{name:>10} {model.overlap(noisy, target):>12.3f} "
              f"{model.overlap(result.state, target):>12.3f} "
              f"{result.sweeps:>8} {result.energies[-1] - result.energies[0]:>12.2f}")

        for row, (state, title) in enumerate((
            (target, f"stored: {name}"),
            (noisy, f"input ({NOISE:.0%} noise)"),
            (result.state, f"recalled ({result.sweeps} sweeps)"),
        )):
            ax = axes[row, col]
            ax.imshow(np.asarray(state).reshape(SHAPE), cmap="binary_r", vmin=-1, vmax=1)
            ax.set_title(title, fontsize=9)
            ax.axis("off")

    fig.tight_layout()
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "recall.png", dpi=140)

    fig2, ax = plt.subplots(figsize=(7, 4))
    for name, target in zip(NAMES, patterns):
        noisy = corrupt(target, NOISE, np.random.default_rng(SEED))
        energies = solve.relax(weights, noisy, seed=SEED).energies
        ax.plot(energies, marker="o", label=name)
    ax.set(xlabel="sweep", ylabel="energy", title="Energy descent during recall")
    ax.legend(frameon=False)
    fig2.tight_layout()
    fig2.savefig(out / "energy_descent.png", dpi=140)
    print(f"\nfigures -> {out}/recall.png, {out}/energy_descent.png")


if __name__ == "__main__":
    main()
