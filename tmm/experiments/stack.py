"""The four measurements the derivation in `docs/physics.md` rests on.

Unlike `brewster.py` and `bragg_mirror.py`, which reproduce results the entry
already claimed, these exist because the derivation argues four things that
nothing in the entry plotted -- and an argument in a document is worth exactly
as much as the run behind it.

Each figure makes one point:

  1. amplitudes add and powers do not, and a power-adding model cannot produce
     an anti-reflection coating or a Bragg mirror at all -- it is a different
     physical situation, not a coarser one
  2. more periods buy depth, never width: depth falls exponentially in the
     number of periods, the stopband is fixed by index contrast alone
  3. the two solvers agree to machine precision right up to a wall that only
     the matrix product hits
  4. every dielectric filter shifts blue when you tilt it, which is the
     fingerprint that separates structural colour from pigment

Figures land in `docs/figures/`, which is tracked, unlike `experiments/out/`:
these are published alongside the derivation rather than scratch output.
"""

import math
import sys
import warnings
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from solve import RT

FIGURES = Path(__file__).resolve().parents[1] / "docs" / "figures"

DESIGN = 550.0
N_AIR, N_HIGH, N_LOW, N_SUB = 1.0, 2.3, 1.45, 1.52
N_MGF2 = 1.38

INK, GRID = "#1b1b1b", "#d8d8d8"
MEASURED, THEORY, WARN, COOL = "#c0392b", "#2c3e50", "#e08a1e", "#2e7d94"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
})


def bragg(periods, high=N_HIGH, low=N_LOW):
    n = [N_AIR] + [high, low] * periods + [N_SUB]
    d = [0] + [DESIGN / (4 * high), DESIGN / (4 * low)] * periods + [0]
    return n, d


def spectrum(n, d, wavelengths, theta=0.0):
    return np.array([RT("s", n, d, lam, theta)[0] for lam in wavelengths])


def incoherent(n):
    """Compose the interfaces by adding POWERS instead of amplitudes.

    Walk up from the substrate summing each geometric series in intensity.
    Note what cannot appear anywhere in this function: the layer thicknesses.
    An incoherent stack has no way to know a layer is a quarter wave, which is
    why it can reproduce neither of the phenomena the entry is about.
    """
    n = np.asarray(n, dtype=float)
    reflectance = 0.0
    for i in range(len(n) - 2, -1, -1):
        r = ((n[i] - n[i + 1]) / (n[i] + n[i + 1])) ** 2
        reflectance = r + (1 - r) ** 2 * reflectance / (1 - r * reflectance)
    return reflectance


def band_edges(high=N_HIGH, low=N_LOW):
    """Exact stopband from Bloch theory: |1/2 Tr M_period| = 1.

    For a quarter-wave pair both layers share delta = (pi/2)(lambda0/lambda),
    and the edges sit at delta = pi/2 +- arcsin((nH-nL)/(nH+nL)). No periods
    anywhere in that expression -- which is the whole point of figure 2.
    """
    half = math.asin((high - low) / (high + low))
    return ((math.pi / 2) * DESIGN / (math.pi / 2 + half),
            (math.pi / 2) * DESIGN / (math.pi / 2 - half))


def measured_edges(spec, wavelengths):
    """The crude 99%-of-peak band the entry's experiment measures.

    It reports a band that grows with N. The band itself does not: what grows
    is the reflectance's ability to reach 99% of its own peak across it, so
    the threshold only becomes meaningful once the top is genuinely flat.
    """
    inside = wavelengths[spec > 0.99 * spec.max()]
    if len(inside) < 2:
        return None, None
    return float(inside.min()), float(inside.max())


# --- 1. amplitudes add, powers do not ---------------------------------------

def coherence(periods=(1, 2, 3, 4, 6, 8, 12, 16)):
    wavelengths = np.linspace(380, 800, 900)
    ar = ([N_AIR, N_MGF2, N_SUB], [0, DESIGN / (4 * N_MGF2), 0])
    bare = ((N_AIR - N_SUB) / (N_AIR + N_SUB)) ** 2

    ar_coherent = spectrum(*ar, wavelengths)
    ar_incoherent = incoherent(ar[0])

    print("\n1. AMPLITUDES ADD, POWERS DO NOT")
    print(f"  bare glass                       R = {bare:.6f}")
    print(f"  one quarter wave of MgF2, coherent   R = {ar_coherent.min():.6f} "
          f"at {wavelengths[ar_coherent.argmin()]:.0f} nm")
    print(f"  the same layer, powers added         R = {ar_incoherent:.6f} "
          f"at every wavelength")
    print(f"  {'periods':>8} {'interfaces':>11} {'coherent':>10} {'incoherent':>11}")
    coherent_peaks, incoherent_peaks = [], []
    for count in periods:
        n, d = bragg(count)
        coherent_peaks.append(RT("s", n, d, DESIGN)[0])
        incoherent_peaks.append(incoherent(n))
        print(f"  {count:>8} {len(n) - 1:>11} {coherent_peaks[-1]:>10.6f} "
              f"{incoherent_peaks[-1]:>11.6f}")

    fig, (left, right) = plt.subplots(1, 2, figsize=(11.0, 4.3))

    left.plot(wavelengths, ar_coherent, color=MEASURED, lw=1.9,
              label="amplitudes added (the real answer)")
    left.axhline(ar_incoherent, color=THEORY, ls="-", lw=1.7,
                 label="powers added")
    left.axhline(bare, color="0.5", ls=":", lw=1.5, label="bare glass, no coating")
    left.axvline(DESIGN, color="0.6", ls="--", lw=1)
    left.annotate("the coating only works\nbecause of the cross terms",
                  xy=(DESIGN, ar_coherent.min()), xytext=(578, 0.0035),
                  color=MEASURED, fontsize=9,
                  arrowprops=dict(arrowstyle="->", color=MEASURED, lw=1.2))
    left.set(xlabel="wavelength (nm)", ylabel="reflectance", ylim=(0, 0.055))
    left.set_title("One quarter-wave layer on glass", fontsize=10.5, pad=8)
    left.legend(frameon=False, fontsize=8.5, loc="upper left")

    right.plot(periods, coherent_peaks, "o-", color=MEASURED, lw=1.9, ms=6,
               label="amplitudes added")
    right.plot(periods, incoherent_peaks, "s-", color=THEORY, lw=1.7, ms=5,
               label="powers added")
    right.set(xlabel="quarter-wave periods", ylabel="reflectance at 550 nm",
              ylim=(0, 1.05))
    right.set_title("A Bragg mirror, high index / low index", fontsize=10.5, pad=8)
    right.legend(frameon=False, fontsize=9, loc="center right")
    save(fig, "coherence.png")


# --- 2. depth, not width ----------------------------------------------------

def depth_and_width(periods=(2, 3, 4, 6, 8, 10, 12, 16, 20)):
    wavelengths = np.linspace(300, 1100, 4000)
    print("\n2. MORE PERIODS BUY DEPTH, NEVER WIDTH")
    for high, low in ((N_HIGH, N_LOW), (1.8, N_LOW)):
        lo, hi = band_edges(high, low)
        print(f"  nH/nL = {high}/{low}: exact stopband {lo:.1f}-{hi:.1f} nm "
              f"= {(hi - lo) / DESIGN:.4f} of the design wavelength, at every N")

    print(f"  {'periods':>8} {'1-R measured':>14} {'napkin':>12} "
          f"{'measured band 2.3/1.45':>24} {'measured band 1.8/1.45':>24}")
    leakage, napkin, edges = [], [], {}
    for high, low in ((N_HIGH, N_LOW), (1.8, N_LOW)):
        edges[high] = [measured_edges(spectrum(*bragg(count, high, low), wavelengths),
                                      wavelengths) for count in periods]
    for index, count in enumerate(periods):
        n, d = bragg(count)
        leakage.append(1 - RT("s", n, d, DESIGN)[0])
        napkin.append(4 * N_AIR / N_SUB * (N_LOW / N_HIGH) ** (2 * count))
        a, b = edges[N_HIGH][index]
        c, e = edges[1.8][index]
        print(f"  {count:>8} {leakage[-1]:>14.3e} {napkin[-1]:>12.3e} "
              f"{a:>11.1f}-{b:<12.1f} {c:>11.1f}-{e:<12.1f}")

    fig, (left, right) = plt.subplots(1, 2, figsize=(11.0, 4.3))

    left.semilogy(periods, leakage, "o-", color=MEASURED, lw=1.9, ms=6,
                  label="measured  $1-R$")
    left.semilogy(periods, napkin, "--", color=THEORY, lw=1.6,
                  label=r"napkin  $\frac{4n_0}{n_s}(n_L/n_H)^{2N}$")
    left.set(xlabel="quarter-wave periods  $N$", ylabel="light that leaks through")
    left.set_title("Depth: exponential in the number of periods",
                   fontsize=10.5, pad=8)
    left.legend(frameon=False, fontsize=9)

    span = (periods[0] - 0.8, periods[-1] + 0.8)
    for (high, colour) in ((N_HIGH, MEASURED), (1.8, COOL)):
        lo, hi = band_edges(high, N_LOW)
        # the exact band is a horizontal strip: no N appears in band_edges()
        right.axhspan(lo, hi, xmin=0, xmax=1, color=colour, alpha=0.13)
        right.axhline(lo, color=colour, ls="--", lw=1.3)
        right.axhline(hi, color=colour, ls="--", lw=1.3)
        right.annotate(rf"exact band, $n_H$ = {high}",
                       xy=(span[1] - 0.4, hi + 7), color=colour, fontsize=8.5,
                       ha="right")
        lows = [edge[0] for edge in edges[high]]
        highs = [edge[1] for edge in edges[high]]
        right.plot(periods, lows, "o-", color=colour, lw=1.7, ms=5)
        right.plot(periods, highs, "o-", color=colour, lw=1.7, ms=5)
    right.annotate("the bands never move;\nthe measurement grows into them",
                   xy=(11.5, 548), color="0.25", fontsize=9, ha="center")
    right.set(xlabel="quarter-wave periods  $N$", ylabel="wavelength (nm)",
              xlim=span, ylim=(440, 690))
    right.set_title("Width: set by contrast, and it never moves with $N$",
                    fontsize=10.5, pad=8)
    save(fig, "depth_not_width.png")


# --- 3. the numerical ceiling -----------------------------------------------

def ceiling(metal=1.5 + 3.0j):
    thicknesses = np.unique(np.concatenate([
        np.linspace(50, 18000, 60),
        np.linspace(18000, 30000, 90),
    ]))
    print(f"\n3. SAME PHYSICS, DIFFERENT CEILING  (one layer of n = {metal})")
    stack = [N_AIR, metal, N_SUB]
    matrix, recursion = [], []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for thickness in thicknesses:
            d = [0, float(thickness), 0]
            matrix.append(RT("s", stack, d, DESIGN, method="transfer-matrix")[0])
            recursion.append(RT("s", stack, d, DESIGN, method="recursion")[0])
    matrix, recursion = np.array(matrix), np.array(recursion)
    alive = np.isfinite(matrix)
    died = thicknesses[~alive].min() / 1000.0
    survived = thicknesses[alive].max() / 1000.0
    gap = np.abs(matrix - recursion)
    print(f"  the two solvers agree to {np.nanmax(gap[alive]):.1e} everywhere both run")
    print(f"  transfer-matrix last works at {survived:.2f} um and is non-finite "
          f"by {died:.2f} um")
    print(f"  recursion is finite at every thickness tried: "
          f"{bool(np.all(np.isfinite(recursion)))}, up to "
          f"{thicknesses.max() / 1000:.0f} um")

    microns = thicknesses / 1000.0
    floor = 1e-17
    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(8.6, 5.6), sharex=True,
        gridspec_kw=dict(height_ratios=[1.15, 1], hspace=0.12))

    for panel in (top, bottom):
        panel.axvspan(died, microns.max(), color=MEASURED, alpha=0.10)
        panel.axvline(died, color=MEASURED, ls="--", lw=1.5)

    top.plot(microns, recursion, "-", color=THEORY, lw=3.4, alpha=0.45,
             label="recursion")
    top.plot(microns[alive], matrix[alive], "-", color=MEASURED, lw=1.5,
             label="transfer matrix")
    top.annotate(f"$r$ goes NaN at {died:.1f} um\nand stays NaN",
                 xy=(died, recursion[0]), xytext=(died - 10.2, 0.560),
                 color=MEASURED, fontsize=9.5,
                 arrowprops=dict(arrowstyle="->", color=MEASURED, lw=1.2))
    top.set(ylabel="reflectance  $R$", ylim=(0.52, 0.70))
    top.set_title("Identical physics, and only one of them has a ceiling",
                  fontsize=11, pad=10)
    top.legend(frameon=False, fontsize=9, loc="lower left")

    bottom.semilogy(microns[alive], np.maximum(gap[alive], floor), "o",
                    color=THEORY, ms=3.6)
    bottom.axhline(np.finfo(float).eps, color="0.5", ls=":", lw=1.4)
    bottom.annotate("one bit of\ndouble precision", xy=(21.4, 2.0e-16),
                    color="0.4", fontsize=8.5)
    bottom.annotate("exact agreement\ndrawn on the floor",
                    xy=(21.4, floor * 1.15), color="0.55", fontsize=8)
    bottom.set(xlabel="thickness of the absorbing layer (um)",
               ylabel=r"$|R_{\mathrm{matrix}} - R_{\mathrm{rec}}|$",
               ylim=(floor / 2.2, 3e-15), xlim=(0, microns.max()))
    save(fig, "ceiling.png")


# --- 4. blueshift -----------------------------------------------------------

def blueshift(angles=(0, 20, 40, 60), periods=8):
    wavelengths = np.linspace(350, 800, 1600)
    n, d = bragg(periods)
    print(f"\n4. EVERY DIELECTRIC FILTER SHIFTS BLUE  ({periods} periods)")
    print(f"  {'angle':>7} {'band centre':>13} {'shift':>10}")
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    colours = (THEORY, COOL, WARN, MEASURED)
    reference = None
    for angle, colour in zip(angles, colours):
        spec = spectrum(n, d, wavelengths, np.deg2rad(angle))
        inside = wavelengths[spec > 0.99 * spec.max()]
        centre = 0.5 * (inside.min() + inside.max())
        reference = centre if reference is None else reference
        print(f"  {angle:>5}°  {centre:>12.1f} nm {centre - reference:>+9.1f} nm")
        ax.plot(wavelengths, spec, color=colour, lw=1.8, label=f"{angle}°")
        ax.axvline(centre, color=colour, ls=":", lw=1.2)
    ax.annotate("", xy=(487, 1.11), xytext=(562, 1.11), annotation_clip=False,
                arrowprops=dict(arrowstyle="->", color="0.35", lw=1.6))
    ax.annotate("band centre, 0 to 60 degrees", xy=(524, 1.13), ha="center",
                annotation_clip=False, color="0.35", fontsize=9)
    ax.set(xlabel="wavelength (nm)", ylabel="reflectance (s-polarised)",
           ylim=(0, 1.05))
    ax.set_title("Tilt it and the whole band walks towards the blue",
                 fontsize=11, pad=10)
    ax.legend(frameon=False, fontsize=9, title="incidence", loc="upper right")
    save(fig, "blueshift.png")


def save(fig, name):
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / name, dpi=140, facecolor="white",
                bbox_inches="tight", pad_inches=0.22)
    plt.close(fig)
    print(f"  figure -> docs/figures/{name}")


def main():
    coherence()
    depth_and_width()
    ceiling()
    blueshift()


if __name__ == "__main__":
    main()
