"""How many memories fit before the network starts inventing errors?

Reproduces the fifth result of the class activity: relative error against the
load P/N, for networks of several sizes, with a band for the spread across
trials.

The protocol is the one from class -- store P random patterns, hand back one
of them with a little noise, relax, and count how many bits come out wrong.
Below the critical load the error is essentially zero; above it the recalled
state drifts away from the memory and never comes back.

Theory puts the transition at alpha_c ~ 0.138 for random patterns.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import model
import solve

SIZES = (100, 250, 500)
LOADS = (0.02, 0.05, 0.08, 0.10, 0.12, 0.138, 0.16, 0.20, 0.25, 0.30, 0.40)
TRIALS = 20
PROBE_NOISE = 0.05
ALPHA_C = 0.138


def relative_error(size, load, trial):
    rng = np.random.default_rng(1000 * trial + size)
    count = max(1, int(round(load * size)))
    patterns = rng.choice([-1, 1], size=(count, size)).astype(np.int8)
    weights = model.hebbian_weights(patterns)

    target = patterns[rng.integers(count)]
    probe = target.copy()
    idx = rng.choice(size, size=max(1, int(PROBE_NOISE * size)), replace=False)
    probe[idx] *= -1

    result = solve.relax(weights, probe, method="asynchronous",
                         seed=trial, max_sweeps=30)
    return float(np.mean(result.state != target))


def main():
    fig, ax = plt.subplots(figsize=(8, 5))
    print(f"{'N':>6} {'P/N':>7} {'P':>5} {'error medio':>13} {'sd':>8}")

    for size in SIZES:
        means, sds = [], []
        for load in LOADS:
            errors = [relative_error(size, load, t) for t in range(TRIALS)]
            means.append(np.mean(errors))
            sds.append(np.std(errors))
            print(f"{size:>6} {load:>7.3f} {max(1, round(load*size)):>5} "
                  f"{means[-1]:>13.4f} {sds[-1]:>8.4f}")
        means, sds = np.array(means), np.array(sds)
        line, = ax.plot(LOADS, means, marker="o", label=f"N = {size}")
        ax.fill_between(LOADS, means - sds, means + sds, alpha=0.18,
                        color=line.get_color())
        print()

    ax.axvline(ALPHA_C, color="0.35", ls="--", lw=1,
               label=r"$\alpha_c \approx 0.138$")
    ax.set(xlabel="load  P / N", ylabel="relative error after recall",
           title="Hopfield storage limit")
    ax.legend(frameon=False)
    fig.tight_layout()

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "capacity.png", dpi=140)
    print(f"figure -> {out / 'capacity.png'}")


if __name__ == "__main__":
    main()
