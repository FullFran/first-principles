"""Why does a single interface go completely dark for one polarisation?

At the Brewster angle the reflected and refracted rays are perpendicular.
The reflected wave would have to be radiated by dipoles oscillating along
their own axis, and a dipole does not radiate along its axis -- so the p
reflection vanishes exactly. Nothing cancels for s.

The claim under test: the numerical minimum of Rp sits at arctan(n2/n1),
and it is a true zero, not a small number.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from solve import RT

GREEN = 550.0
CASES = [("air -> glass", 1.0, 1.52), ("air -> silicon", 1.0, 3.88), ("glass -> air", 1.52, 1.0)]


def main():
    angles = np.linspace(0, 89.9, 4000)
    fig, axes = plt.subplots(1, len(CASES), figsize=(13, 4), sharey=True)

    print(f"{'interface':>16} {'found':>10} {'arctan(n2/n1)':>15} {'Rp at min':>12}")
    for ax, (label, n1, n2) in zip(axes, CASES):
        stack = ([n1, n2], [0, 0])
        R_s = np.array([RT("s", *stack, GREEN, np.deg2rad(a))[0] for a in angles])
        R_p = np.array([RT("p", *stack, GREEN, np.deg2rad(a))[0] for a in angles])

        found = angles[np.argmin(R_p)]
        expected = np.rad2deg(np.arctan(n2 / n1))
        print(f"{label:>16} {found:>9.3f}d {expected:>14.3f}d {R_p.min():>12.3e}")

        ax.plot(angles, R_s, label="s")
        ax.plot(angles, R_p, label="p")
        ax.axvline(expected, color="0.4", ls="--", lw=1)
        ax.set(xlabel="incidence angle (deg)", title=label, ylim=(0, 1.02))

    axes[0].set_ylabel("reflectance")
    axes[0].legend(frameon=False)
    fig.tight_layout()

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "brewster.png", dpi=140)
    print(f"figure -> {out / 'brewster.png'}")


if __name__ == "__main__":
    main()
