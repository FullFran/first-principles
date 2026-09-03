"""What the forward process destroys, and what the score still knows.

The claim the whole subject rests on is that noising is easy and reversing it
is a gradient. This draws both halves.

Top row: the exact density q_t as abar falls. Two wells become one blob, and
the interesting part is *where* they stop being two -- not gradually, but over
a narrow range of abar, because what separates the modes is a distance and
what fills the gap is a variance, and one grows while the other does not.

Bottom row: the score field at the same times. It is a picture of the answer
key. Early it points at the nearest mode, and late it points at the origin
and has forgotten there were two -- which is the same statement as the top
row, read as a gradient instead of as a density.

Prediction before running: the field goes uninformative at roughly the abar
where the two noised components start to overlap, and that overlap is set by
the *smallest* eigenvalue of the data covariance, not by the mode separation
alone.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import process  # noqa: E402

FIGURES = Path(__file__).resolve().parent.parent / "docs" / "figures"
STAGES = [1.0, 0.7, 0.3, 0.05]
MIXTURE = process.BIMODAL


def separation(alpha_bar):
    """Mode gap over noised width, along the axis that separates the modes.

    Above 1 the modes are resolvable; below it they are one blob. The gap
    shrinks like sqrt(abar) and the width tends to 1, so this falls
    monotonically and crossing it is what "the modes merged" means.
    """
    _, covariances = process.noised_parameters(MIXTURE, alpha_bar)
    gap = np.sqrt(alpha_bar) * abs(MIXTURE.means[1, 0] - MIXTURE.means[0, 0])
    return gap / (2.0 * np.sqrt(covariances[0][0, 0]))


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    grid = np.linspace(-4.5, 4.5, 220)
    xx, yy = np.meshgrid(grid, grid)
    flat = np.stack([xx.ravel(), yy.ravel()], axis=1)

    print(f"{'abar':>6}  {'mode gap / width':>16}  resolvable")
    for alpha_bar in STAGES:
        ratio = separation(alpha_bar)
        print(f"{alpha_bar:6.2f}  {ratio:16.2f}  {'yes' if ratio > 1 else 'no'}")

    fig, axes = plt.subplots(2, len(STAGES), figsize=(4 * len(STAGES), 8))
    for column, alpha_bar in enumerate(STAGES):
        density = np.exp(process.log_density(MIXTURE, flat, alpha_bar))
        axes[0, column].contourf(xx, yy, density.reshape(xx.shape), levels=24)
        axes[0, column].set_title(
            rf"$\bar\alpha = {alpha_bar}$   gap/width = {separation(alpha_bar):.1f}"
        )

        coarse = np.linspace(-4.0, 4.0, 17)
        cx, cy = np.meshgrid(coarse, coarse)
        field = process.score(MIXTURE, np.stack([cx.ravel(), cy.ravel()], 1), alpha_bar)
        axes[1, column].quiver(cx, cy, field[:, 0].reshape(cx.shape),
                               field[:, 1].reshape(cx.shape), angles="xy")
        axes[1, column].set_title(r"$\nabla \log q_t$")

        for row in (0, 1):
            axes[row, column].set_aspect("equal")
            axes[row, column].set_xlim(-4.5, 4.5)
            axes[row, column].set_ylim(-4.5, 4.5)

    axes[0, 0].set_ylabel("density $q_t$")
    axes[1, 0].set_ylabel("score field")
    fig.tight_layout()
    fig.savefig(FIGURES / "collapse.png", dpi=140, facecolor="white",
                bbox_inches="tight")
    print("\n  figure -> docs/figures/collapse.png")


if __name__ == "__main__":
    main()
