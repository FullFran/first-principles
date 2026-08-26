"""What the estimator choice looks like, rather than what it measures.

A radiograph is this entry's physics with a detector behind it: a source, an
object whose thickness varies from place to place, and a count of the photons
that made it through each pixel. Nothing new is needed -- the optical depth of
a chord through a sphere is analytic, and both estimators already take an
array of thicknesses.

The point is that the variance argument in variance.py stops being a number
here. Give both estimators the same photon budget and the difference between
"one bit per photon" and "the exact survival probability" is the difference
between a grainy image and a clean one, at identical cost.

That is also why dose matters in a real X-ray: the noise in the image is the
counting noise of the photons the patient absorbed, and the only analog way to
halve it is to quadruple the exposure.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from methods import ALL as METHODS

RESOLUTION = 160
PHOTONS_PER_PIXEL = 120
FIELD = 1.3

# a low-attenuation body holding two denser inclusions, in mean free paths
BODY = dict(centre=(0.0, 0.0), radius=1.0, mu=0.8)
INCLUSIONS = [dict(centre=(-0.34, 0.22), radius=0.20, mu=6.0),
              dict(centre=(0.30, -0.18), radius=0.12, mu=6.0)]


def chord(x, y, centre, radius):
    """Length of the straight path through a sphere, per pixel. Analytic."""
    offset = (x - centre[0]) ** 2 + (y - centre[1]) ** 2
    inside = offset < radius ** 2
    return np.where(inside, 2.0 * np.sqrt(np.clip(radius ** 2 - offset, 0, None)), 0.0)


def optical_depth():
    """Sum of mu * path over everything the ray crosses.

    An inclusion displaces the body it sits inside, so its chord is charged at
    the difference of the two attenuations rather than added on top. Getting
    that wrong makes dense objects look denser than they are, which is exactly
    the artefact a real reconstruction has to avoid.
    """
    axis = np.linspace(-FIELD, FIELD, RESOLUTION)
    x, y = np.meshgrid(axis, axis)
    depth = BODY["mu"] * chord(x, y, BODY["centre"], BODY["radius"])
    for inclusion in INCLUSIONS:
        depth += (inclusion["mu"] - BODY["mu"]) * chord(
            x, y, inclusion["centre"], inclusion["radius"])
    return axis, depth


def image(method, depth, photons, seed=0):
    """Expose the detector. Collimated, so every ray crosses depth exactly."""
    rng = np.random.default_rng(seed)
    thickness = np.repeat(depth.ravel(), photons)
    cos_theta = np.ones_like(thickness)
    weights = METHODS[method].contributions(rng, cos_theta, 1.0, thickness)
    return weights.reshape(depth.shape + (photons,)).mean(axis=-1)


def main():
    axis, depth = optical_depth()
    truth = np.exp(-depth)
    print(f"{RESOLUTION}x{RESOLUTION} detector, {PHOTONS_PER_PIXEL} photons per pixel, "
          f"{RESOLUTION**2 * PHOTONS_PER_PIXEL:,} photons in total\n")
    print(f"optical depth spans {depth.min():.2f} to {depth.max():.2f} mean free paths")
    print(f"so transmission spans {truth.min():.4f} to {truth.max():.4f}\n")

    print(f"  {'estimator':>10} {'RMS error vs exact':>20} {'worst pixel':>13}")
    frames = {}
    for method in sorted(METHODS):
        frames[method] = image(method, depth, PHOTONS_PER_PIXEL)
        residual = frames[method] - truth
        print(f"  {method:>10} {np.sqrt(np.mean(residual**2)):>20.6f} "
              f"{np.abs(residual).max():>13.6f}")

    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.2))
    for ax, (title, frame) in zip(axes, (
            ("analog: one bit per photon", frames["analog"]),
            ("weighted: the survival probability", frames["weighted"]),
            ("exact  $e^{-\\tau}$", truth))):
        ax.imshow(frame, cmap="bone", vmin=0, vmax=1, origin="lower",
                  extent=(-FIELD, FIELD, -FIELD, FIELD))
        ax.set_title(title, fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])

    fig.suptitle(f"The same {PHOTONS_PER_PIXEL} photons per pixel, twice",
                 fontsize=11.5, y=1.0)
    fig.tight_layout()

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "radiograph.png", dpi=140, bbox_inches="tight")

    row = RESOLUTION // 2 + int(0.22 / (2 * FIELD) * RESOLUTION)
    fig2, ax = plt.subplots(figsize=(8.2, 4.0))
    ax.plot(axis, frames["analog"][row], lw=1.0, color="#c0392b", label="analog")
    ax.plot(axis, frames["weighted"][row], lw=1.8, color="#2c3e50", label="weighted")
    ax.plot(axis, truth[row], "--", lw=1.4, color="0.5", label="exact")
    ax.set(xlabel="position across the detector", ylabel="transmitted fraction")
    ax.set_title("One row through the upper inclusion", fontsize=11, pad=10)
    ax.legend(frameon=False, fontsize=9)
    fig2.tight_layout()
    fig2.savefig(out / "radiograph_profile.png", dpi=140, bbox_inches="tight")
    print(f"\nfigures -> {out}/radiograph.png, {out}/radiograph_profile.png")


if __name__ == "__main__":
    main()
