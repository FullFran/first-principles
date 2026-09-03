"""Where the two samplers cross over, and why the usual telling misses it.

The received claim is that the deterministic sampler needs far fewer steps.
It is an argument about *learned* scores and perceptual metrics, and here the
score is exact and the metric is a distributional distance, so it is worth
asking whether it survives the change of setting.

Prediction before running: probability-flow wins at every step count, because
it has no injected noise to remove.

Half right, and the half that fails is a lesson about the measurement rather
than about the methods. Below about twelve steps the deterministic method is
ahead, by 0.6-0.9x on the anisotropic targets. Above it, both methods are
inside the noise floor, and the first version of this file went on ranking
them there and reported ancestral ahead by up to 5.6x. That was two numbers
indistinguishable from zero being divided by each other. The floor is now
printed and the ratio is withheld once both are under it.

Every number is averaged over six seeds. One run of either method is a noisy
number, and this comparison read off a single seed says whatever the seed
says -- an earlier version of it did exactly that and reported the opposite.

The crossover shows on the two anisotropic targets and not on `bimodal`,
which is the useful part of the negative result: two symmetric isotropic
wells are easy enough that both methods sit at the noise floor from about
eight steps on, and a comparison between two numbers that are both zero
reports whichever noise was larger.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import solve  # noqa: E402

STEPS = [5, 8, 12, 20, 50, 100, 200]
SEEDS = range(6)


def mean_gap(target, method, steps):
    """MMD^2 against exact draws, floored at zero and averaged over seeds.

    Floored because the unbiased estimator goes negative when the two sets
    are indistinguishable, and a negative distance averaged with a positive
    one reports an agreement that is not there.
    """
    return np.mean([
        max(solve.sample(target=target, method=method, steps=steps,
                         draws=400, seed=s).discrepancy, 0.0)
        for s in SEEDS
    ])


def main():
    for target in ["bimodal", "shifted", "arc"]:
        floor = solve.sample(target=target, steps=50, draws=400, seed=0).noise_floor
        print(f"\n=== {target} (noise floor {floor:.1e}) ===")
        print(f"{'steps':>6}  {'ancestral':>12}  {'prob-flow':>12}  {'ratio':>7}  ahead")
        for steps in STEPS:
            a = mean_gap(target, "ancestral", steps)
            p = mean_gap(target, "probability-flow", steps)
            if a < floor and p < floor:
                # a ratio between two numbers that are both indistinguishable
                # from zero is not a measurement of anything
                print(f"{steps:6d}  {a:12.2e}  {p:12.2e}  {'--':>7}  both at floor")
                continue
            ratio = p / max(a, floor)
            print(f"{steps:6d}  {a:12.2e}  {p:12.2e}  {ratio:6.1f}x  "
                  f"{'prob-flow' if ratio < 1 else 'ancestral'}")


if __name__ == "__main__":
    main()
