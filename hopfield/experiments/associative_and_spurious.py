"""Two things the network does that nobody asked it to.

Reproduces the third and fourth results of the class activity.

  1. Associative recall: feed a pattern the network has never seen but which
     resembles a stored one. In class this was a photo of a different cat
     recovering the stored cat; here it is the letter N, which shares both
     uprights with the stored H.

  2. Spurious attractors: the network always stops somewhere, because every
     local minimum of E is a fixed point whether anyone stored it or not.

What actually comes out is more interesting than the script expected, and the
numbers below are reported as they land rather than as they were meant to:
see the README for what actually happens.
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
from patterns import NAMES, NEAR_MISS, SHAPE, as_pattern, checker, glyph, library

SEED = 0


def near_miss():
    """A letter that was never stored, and looks like one that was.

    N overlaps the stored H at +0.78 -- they share both uprights and differ
    only in the bar. If associative recall works the way it is advertised,
    this should come back as H.
    """
    return as_pattern(glyph(NEAR_MISS))


def report(weights, patterns, probe, label):
    result = solve.relax(weights, probe, method="asynchronous", seed=SEED)
    overlaps = {n: model.overlap(result.state, p) for n, p in zip(NAMES, patterns)}
    best, value = max(overlaps.items(), key=lambda kv: abs(kv[1]))
    is_memory = any(np.array_equal(result.state, s)
                    for p in patterns for s in (p, -p))
    print(f"\n{label}")
    print(f"  overlap with each memory: " +
          "  ".join(f"{n}={v:+.3f}" for n, v in overlaps.items()))
    print(f"  closest: {best} ({value:+.3f})   sweeps: {result.sweeps}   "
          f"E: {result.energies[-1]:.2f}")
    print(f"  landed on a stored memory: {'yes' if is_memory else 'NO — spurious'}")
    return result, is_memory


def main():
    patterns = library()
    weights = model.hebbian_weights(patterns)

    probes = [
        (f"{NEAR_MISS} — never stored, looks like H", near_miss()),
        ("checkerboard — genuinely unrelated", as_pattern(checker())),
        ("sign(M + A + T)",
         model.update_rule(patterns[:3].sum(axis=0), patterns[0])),
    ]

    fig, axes = plt.subplots(2, len(probes), figsize=(9, 6))
    for col, (label, probe) in enumerate(probes):
        result, is_memory = report(weights, patterns, probe, label)
        for row, (state, title) in enumerate((
            (probe, label), (result.state, "settles to" +
                             ("" if is_memory else " (spurious)")))):
            ax = axes[row, col]
            ax.imshow(np.asarray(state).reshape(SHAPE), cmap="binary_r", vmin=-1, vmax=1)
            ax.set_title(title, fontsize=8)
            ax.axis("off")

    print("\n" + "-" * 68)
    print("contrast: is the canonical mixture stable with UNCORRELATED patterns?")
    rng = np.random.default_rng(SEED)
    random_patterns = rng.choice([-1, 1], size=(3, patterns.shape[1])).astype(np.int8)
    random_weights = model.hebbian_weights(random_patterns)
    mixture = model.update_rule(random_patterns.sum(axis=0), random_patterns[0])
    settled = solve.relax(random_weights, mixture, method="asynchronous", seed=SEED)
    print(f"  random patterns: mixture is a fixed point -> "
          f"{np.array_equal(settled.state, mixture)}")
    print(f"  overlaps with the three memories: " + "  ".join(
        f"{model.overlap(settled.state, p):+.3f}" for p in random_patterns))
    print("  the glyphs above are correlated, which reshapes the landscape;")
    print("  with orthogonal-ish memories the textbook mixture state survives.")

    fig.tight_layout()
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "associative_and_spurious.png", dpi=140)
    print(f"\nfigure -> {out / 'associative_and_spurious.png'}")


if __name__ == "__main__":
    main()
