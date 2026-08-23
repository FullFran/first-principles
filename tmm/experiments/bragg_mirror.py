"""Where does the stopband of a quarter-wave stack come from?

A Bragg mirror is not a coating that happens to be shiny. It is a resonance:
every layer is a quarter wave thick, so the partial reflections from all the
interfaces arrive back in phase and add coherently. Two consequences follow
from that single idea, and both are checked here against closed form:

  1. the peak reflectance grows with the index contrast raised to the number
     of periods, via the quarter-wave admittance transform
  2. the stopband width depends ONLY on the contrast, not on how many
     periods you stack -- more periods buy depth, never width
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import RT

DESIGN = 550.0
N_AIR, N_HIGH, N_LOW, N_SUB = 1.0, 2.3, 1.45, 1.52


def stack(periods):
    n = [N_AIR] + [N_HIGH, N_LOW] * periods + [N_SUB]
    d = [0] + [DESIGN / (4 * N_HIGH), DESIGN / (4 * N_LOW)] * periods + [0]
    return n, d


def analytic_peak(periods):
    admittance = (N_HIGH / N_LOW) ** (2 * periods) * N_SUB
    return ((N_AIR - admittance) / (N_AIR + admittance)) ** 2


def analytic_bandwidth():
    """Delta_lambda / lambda_0 for an infinite quarter-wave stack."""
    contrast = (N_HIGH - N_LOW) / (N_HIGH + N_LOW)
    return 4 / np.pi * np.arcsin(contrast)


def main():
    wavelengths = np.linspace(350, 900, 1200)
    fig, ax = plt.subplots(figsize=(9, 4.5))

    print(f"{'periods':>8} {'R peak':>10} {'analytic':>10} {'stopband':>10}")
    for periods in (2, 4, 8, 16):
        n, d = stack(periods)
        spectrum = np.array([RT("s", n, d, lam)[0] for lam in wavelengths])

        peak = spectrum.max()
        in_band = wavelengths[spectrum > 0.99 * peak]
        width = (in_band.max() - in_band.min()) / DESIGN if len(in_band) > 1 else 0.0
        print(f"{periods:>8} {peak:>10.6f} {analytic_peak(periods):>10.6f} {width:>10.4f}")

        ax.plot(wavelengths, spectrum, label=f"{periods} periods")

    print(f"\nanalytic stopband (infinite stack): {analytic_bandwidth():.4f}")

    ax.axvline(DESIGN, color="0.4", ls="--", lw=1, label="design wavelength")
    ax.set(xlabel="wavelength (nm)", ylabel="reflectance", ylim=(0, 1.02))
    ax.legend(frameon=False)
    ax.set_title(f"Quarter-wave stack, n_H={N_HIGH} / n_L={N_LOW}")
    fig.tight_layout()

    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "bragg_mirror.png", dpi=140)
    print(f"figure -> {out / 'bragg_mirror.png'}")


if __name__ == "__main__":
    main()
