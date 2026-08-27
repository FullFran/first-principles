"""How wrong is the sampled fixed point, and is it wrong in a direction?

Enumeration counts every configuration and gives an exact map. Sampling
estimates the same map from finite draws, which buys blocks enumeration cannot
reach and pays for them in error bars. The entry claims those error bars exist.
This measures them.

Two predictions, written down first, and they are different predictions:

  1. The SCATTER falls as 1/sqrt(draws). Quadruple the draws and the spread
     across seeds halves. This is ordinary Monte Carlo and would be a surprise
     if it failed.

  2. There is also a BIAS, and it does not fall at the same rate. The fixed
     point is not an average -- it is the ROOT of R(p) = p, and the root of an
     unbiased estimator is not an unbiased estimator of the root. Expanding
     around the true point, the first-order shift averages away and the
     leftover is second order, so bias ~ 1/draws while scatter ~ 1/sqrt(draws).

The second prediction is the one worth testing, because it says the bias is
*smaller* than the noise and gets relatively smaller still -- so the honest
outcome may be a bound rather than a number. Bias is largest where draws are
fewest, so that is where the seeds are spent.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import solve  # noqa: E402

SCHEMES = (
    ("plain b=3", lambda **k: solve.scheme(3, "either", **k)),
    ("cell 3->4", lambda **k: solve.cell_to_cell(3, 4, "either", **k)),
)
LADDER = ((500, 48), (2000, 12), (8000, 12))  # draws, seeds


def spread(build, draws, seeds):
    """Fixed points from independent seeds at one sample size."""
    return np.array([
        build(method="sampling", draws=draws, seed=s).fixed_point
        for s in range(seeds)
    ])


def main():
    print(__doc__.strip())

    for name, build in SCHEMES:
        exact = build(method="enumeration").fixed_point
        print(f"\n{'=' * 68}\n{name.upper()}   exact fixed point {exact:.6f}\n")
        print(f"{'draws':>7} {'seeds':>6} {'mean':>10} {'scatter':>9} "
              f"{'halving':>8} {'bias':>10} {'in SEM':>7}")

        previous = None
        for draws, seeds in LADDER:
            v = spread(build, draws, seeds)
            sd = v.std(ddof=1)
            sem = sd / np.sqrt(seeds)
            bias = v.mean() - exact

            # Quadrupling the draws should halve the scatter.
            ratio = f"{previous / sd:8.2f}" if previous else f"{'--':>8}"
            previous = sd

            print(f"{draws:>7} {seeds:>6} {v.mean():>10.6f} {sd:>9.6f} "
                  f"{ratio} {bias:>+10.6f} {bias / sem:>7.1f}")

        print("\n  'halving' is the scatter ratio to the row above; 1/sqrt(4)"
              " predicts 2.00.")
        print("  'in SEM' is the bias in standard errors of the mean. Under 2"
              " is not a\n  measurement of a bias -- it is a failure to"
              " distinguish one from zero.")


if __name__ == "__main__":
    main()
