"""The four measurements the derivation in `docs/model.md` rests on.

Unlike the other three experiments, these are not from the class activity --
they exist because writing the derivation required numbers that nothing in the
entry measured yet, and a claim in a document is worth exactly as much as the
run behind it.

Each figure makes one point, and the point is printed above the plot:

  1. the napkin is exactly right about the first step and wrong about the
     fixed point, by a factor of twenty
  2. basins collapse long before capacity does, so the memories at alpha_c are
     stable and unreachable
  3. an exact tie is forbidden by parity, and float64 sees a seventh of the
     ones that are allowed
  4. descent is monotone into the wrong answer, and there are more wrong
     answers than right ones

Figures land in `docs/figures/`, which is tracked, unlike `experiments/out/`:
these are published alongside the derivation rather than scratch output.
"""

import itertools
import math
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
from patterns import NAMES, NEAR_MISS, SHAPE, as_pattern, glyph, library

FIGURES = Path(__file__).resolve().parents[1] / "docs" / "figures"
ALPHA_C = 0.138

INK, GRID = "#1b1b1b", "#d8d8d8"
MEASURED, THEORY, WARN, COOL = "#c0392b", "#2c3e50", "#e08a1e", "#2e7d94"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
})


def gaussian_tail(x):
    """Q(x) = P(Z > x) for a standard normal."""
    return 0.5 * math.erfc(x / math.sqrt(2.0))


def random_patterns(count, size, rng):
    return rng.choice([-1, 1], size=(count, size)).astype(np.int8)


# --- 1. the avalanche -------------------------------------------------------

def avalanche(size=1000, trials=12,
              loads=(0.02, 0.05, 0.08, 0.10, 0.12, 0.138, 0.16, 0.20, 0.25, 0.30)):
    """One-step error tracks the napkin; the fixed point leaves it behind."""
    print("\n1. THE AVALANCHE  (N = %d, %d pattern sets per load)" % (size, trials))
    print(f"  {'alpha':>7} {'P':>5} {'one step':>10} {'Q(1/sqrt a)':>12} {'relaxed':>10}")
    one_step, relaxed, napkin = [], [], []
    for load in loads:
        count = max(1, round(load * size))
        step_errors, final_errors = [], []
        for trial in range(trials):
            rng = np.random.default_rng(100 + trial)
            patterns = random_patterns(count, size, rng)
            weights = model.hebbian_weights(patterns)
            target = patterns[0]
            moved = model.update_rule(model.local_field(weights, target), target)
            step_errors.append(float(np.mean(moved != target)))
            settled = solve.relax(weights, target.copy(), method="asynchronous",
                                  seed=trial, max_sweeps=30)
            final_errors.append(float(np.mean(settled.state != target)))
        one_step.append(np.mean(step_errors))
        relaxed.append(np.mean(final_errors))
        napkin.append(gaussian_tail(1.0 / math.sqrt(load)))
        print(f"  {load:>7.3f} {count:>5d} {one_step[-1]:>10.4f} "
              f"{napkin[-1]:>12.4f} {relaxed[-1]:>10.4f}")

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    grid = np.linspace(min(loads), max(loads), 300)
    ax.plot(grid, [gaussian_tail(1 / math.sqrt(a)) for a in grid], color=THEORY,
            lw=1.6, label=r"napkin:  $Q(1/\sqrt{\alpha})$")
    # an exact zero has no place on a log axis; hide those points rather than
    # letting matplotlib clip them into a spike at the edge
    shown = np.array(loads)
    step = np.where(np.array(one_step) > 0, one_step, np.nan)
    final = np.where(np.array(relaxed) > 0, relaxed, np.nan)
    ax.plot(shown, step, "o", color=THEORY, ms=6, mfc="white", mew=1.6,
            label="measured, one update")
    ax.plot(shown, final, "o-", color=MEASURED, lw=1.8, ms=6,
            label="measured, after relaxing")
    ax.axvline(ALPHA_C, color="0.45", ls="--", lw=1)
    ax.annotate(r"$\alpha_c = 0.138$", xy=(ALPHA_C, 3e-4), xytext=(0.142, 1.5e-4),
                color="0.35", fontsize=9)
    gap = loads.index(0.16)
    ax.annotate("", xy=(0.16, relaxed[gap]), xytext=(0.16, one_step[gap]),
                arrowprops=dict(arrowstyle="<->", color=MEASURED, lw=1.4))
    ax.annotate("the avalanche:\n20x the estimate", xy=(0.163, 0.025),
                color=MEASURED, fontsize=9.5)
    ax.set(yscale="log", xlabel=r"load   $\alpha = P/N$",
           ylabel="fraction of bits recalled wrong", ylim=(1e-4, 1.0))
    ax.set_title("The estimate is exactly right about the wrong quantity",
                 fontsize=11.5, pad=10)
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    save(fig, "avalanche.png")


# --- 2. basins --------------------------------------------------------------

def basins(size=500, trials=24,
           loads=(0.02, 0.05, 0.10, 0.138),
           fractions=(0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.45, 0.5)):
    """How far away you can start, which is not what capacity measures."""
    print("\n2. BASINS  (N = %d, %d trials per cell) -- fraction recalled exactly"
          % (size, trials))
    print(f"  {'alpha':>7} " + " ".join(f"{f:>6.0%}" for f in fractions))
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    for load, colour in zip(loads, (COOL, "#4a9d5f", WARN, MEASURED)):
        count = max(1, round(load * size))
        row = []
        for fraction in fractions:
            hits = 0
            for trial in range(trials):
                rng = np.random.default_rng(900 + trial)
                patterns = random_patterns(count, size, rng)
                weights = model.hebbian_weights(patterns)
                target = patterns[0]
                probe = target.copy()
                flips = int(fraction * size)
                if flips:
                    probe[rng.choice(size, size=flips, replace=False)] *= -1
                settled = solve.relax(weights, probe, method="asynchronous",
                                      seed=trial, max_sweeps=40)
                hits += int(np.array_equal(settled.state, target))
            row.append(hits / trials)
        print(f"  {load:>7.3f} " + " ".join(f"{v:>6.2f}" for v in row))
        label = rf"$\alpha$ = {load}" + ("  (capacity)" if load == ALPHA_C else "")
        ax.plot(fractions, row, "o-", color=colour, lw=1.8, ms=5, label=label)

    ax.axvline(0.5, color="0.45", ls="--", lw=1)
    ax.annotate("no information\nleft in the probe", xy=(0.5, 0.30),
                xytext=(0.395, 0.34), color="0.35", fontsize=9, ha="center",
                arrowprops=dict(arrowstyle="->", color="0.45", lw=1))
    ax.set(xlabel="fraction of the probe's bits corrupted",
           ylabel="fraction recalled exactly", ylim=(-0.04, 1.06))
    ax.set_title("At capacity the memories are stable and unreachable",
                 fontsize=11.5, pad=10)
    ax.legend(frameon=False, loc="lower left", fontsize=9)
    save(fig, "basins.png")


# --- 3. the parity law ------------------------------------------------------

def integer_field(patterns, states):
    gram = patterns.T.astype(np.int64) @ patterns.astype(np.int64)
    np.fill_diagonal(gram, 0)
    return np.asarray(states, dtype=np.int64) @ gram.T


def parity(sizes=(20, 40, 60, 100, 200, 350, 576), count=4, trials=25, states=25):
    """Ties are forbidden by parity, or they are common. Never in between."""
    print("\n3. THE PARITY LAW  (P = %d and P = %d, exact integer arithmetic)"
          % (count, count + 1))
    print(f"  {'N':>5} {'P':>3} {'P(N-1)':>7} {'true ties':>11} {'float64 sees':>13}")
    series = {}
    for patterns_count in (count, count + 1):
        true_rates, float_rates = [], []
        for size in sizes:
            ties = seen = total = 0
            for trial in range(trials):
                rng = np.random.default_rng(17 * trial + patterns_count)
                pats = random_patterns(patterns_count, size, rng)
                probes = random_patterns(states, size, rng)
                weights = model.hebbian_weights(pats)
                ties += int(np.count_nonzero(integer_field(pats, probes) == 0))
                seen += int(np.count_nonzero(
                    probes.astype(float) @ weights.T == 0))
                total += probes.size
            true_rates.append(ties / total)
            float_rates.append(seen / total)
            parity_word = "odd" if (patterns_count * (size - 1)) % 2 else "even"
            print(f"  {size:>5} {patterns_count:>3} {parity_word:>7} "
                  f"{true_rates[-1]:>10.3%} {float_rates[-1]:>12.3%}")
        series[patterns_count] = (true_rates, float_rates)

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    even_true, even_float = series[count]
    odd_true, _ = series[count + 1]
    ax.plot(sizes, even_true, "o-", color=MEASURED, lw=1.8, ms=6,
            label=rf"$P(N-1)$ even  ($P$ = {count}) — exact arithmetic")
    ax.plot(sizes, even_float, "s--", color=WARN, lw=1.6, ms=5,
            label=rf"$P(N-1)$ even  ($P$ = {count}) — what float64 reports")
    ax.plot(sizes, odd_true, "o-", color=THEORY, lw=1.8, ms=6,
            label=rf"$P(N-1)$ odd  ($P$ = {count + 1}) — forbidden by parity")
    ax.annotate("exactly zero, at every size", xy=(200, 0), xytext=(150, 0.013),
                color=THEORY, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=THEORY, lw=1.2))
    ax.set(xscale="log", xlabel="units  $N$",
           ylabel="fraction of local fields that are exactly zero")
    ax.set_xticks(list(sizes)); ax.set_xticklabels([str(s) for s in sizes])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_title("A tie is impossible, or it is common — parity decides",
                 fontsize=11.5, pad=10)
    ax.legend(frameon=False, fontsize=9)
    save(fig, "parity.png")


# --- 4. convergence is not correctness --------------------------------------

def near_miss():
    """The letter N, never stored, overlapping the stored H at +0.78."""
    return as_pattern(glyph(NEAR_MISS))


def spurious(enumerate_size=16, counts=(1, 2, 3, 4, 5), trials=6):
    """A monotone descent into a fixed point nobody stored, and a count of how
    many such places there are."""
    patterns = library()
    weights = model.hebbian_weights(patterns)
    probe = near_miss()
    settled = solve.relax(weights, probe, method="asynchronous", seed=0)
    stored_h = model.energy(weights, patterns[3])
    print("\n4a. A CONFIDENT WRONG ANSWER")
    print(f"  probe: the letter {NEAR_MISS}, never stored")
    print(f"  settles at E = {settled.energies[-1]:.2f} after {settled.sweeps} sweeps")
    print(f"  the stored H sits at E = {stored_h:.2f}")
    print(f"  overlap with the stored H: {model.overlap(settled.state, patterns[3]):+.3f}")
    print(f"  energy fell monotonically: "
          f"{bool(np.all(np.diff(settled.energies) <= 1e-9))}")

    print("\n4b. FIXED POINTS BY EXHAUSTIVE ENUMERATION  (N = %d, all 2^N states)"
          % enumerate_size)
    print(f"  {'P':>3} {'memories+mirrors':>18} {'total':>8} {'spurious':>10}")
    every_state = np.array(list(itertools.product([-1, 1], repeat=enumerate_size)),
                           dtype=np.int8)
    stored_counts, spurious_counts = [], []
    for count in counts:
        kept = spur = 0
        for trial in range(trials):
            rng = np.random.default_rng(300 + trial)
            pats = random_patterns(count, enumerate_size, rng)
            wts = model.hebbian_weights(pats)
            fields = every_state @ wts.T
            aligned = np.where(fields > 0, 1, np.where(fields < 0, -1, every_state))
            fixed = every_state[np.all(aligned == every_state, axis=1)]
            memories = {p.tobytes() for p in pats} | {(-p).tobytes() for p in pats}
            here = sum(1 for s in fixed if s.tobytes() in memories)
            kept += here; spur += len(fixed) - here
        stored_counts.append(kept / trials)
        spurious_counts.append(spur / trials)
        print(f"  {count:>3} {stored_counts[-1]:>18.1f} "
              f"{stored_counts[-1] + spurious_counts[-1]:>8.1f} "
              f"{spurious_counts[-1]:>10.1f}")

    fig = plt.figure(figsize=(11.4, 3.7))
    spec = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 2.0], wspace=0.55)

    glyphs = (
        (probe, "the probe", f"{NEAR_MISS}, never stored", None, "0.25"),
        (settled.state, "settles here", "a valley that is not a memory",
         settled.energies[-1], MEASURED),
        (patterns[3], "the stored H", "deeper, never reached",
         stored_h, THEORY),
    )
    for column, (state, title, caption, energy, colour) in enumerate(glyphs):
        panel = fig.add_subplot(spec[0, column])
        panel.imshow(np.asarray(state).reshape(SHAPE), cmap="binary_r",
                     vmin=-1, vmax=1)
        panel.set_xticks([]); panel.set_yticks([])
        for spine in panel.spines.values():
            spine.set_edgecolor(colour); spine.set_linewidth(2.0)
            spine.set_visible(True)
        panel.set_title(title, fontsize=10, color=colour, pad=6)
        label = caption if energy is None else f"{caption}\n$E$ = {energy:.0f}"
        panel.set_xlabel(label, fontsize=8.5, color="0.3", labelpad=6)

    right = fig.add_subplot(spec[0, 3])
    width = 0.62
    right.bar(counts, stored_counts, width, color=THEORY, label="memories + mirrors")
    right.bar(counts, spurious_counts, width, bottom=stored_counts,
              color=MEASURED, label="places nobody stored")
    right.set(xlabel="patterns stored  $P$",
              ylabel=f"fixed points  ($N$ = {enumerate_size})")
    right.set_xticks(list(counts))
    right.set_title("Every place a run is able to stop", fontsize=10.5, pad=6)
    right.legend(frameon=False, fontsize=9, loc="upper left")

    # no suptitle: the caption in docs/model.md states the conclusion, and a
    # figure that repeats its own caption is wasting the reader's attention
    save(fig, "spurious.png")


def save(fig, name):
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    # bbox_inches="tight" crops to the drawn content, so a label can never be
    # clipped by a figsize guessed in advance
    fig.savefig(FIGURES / name, dpi=140, facecolor="white",
                bbox_inches="tight", pad_inches=0.22)
    plt.close(fig)
    print(f"  figure -> docs/figures/{name}")


def main():
    avalanche()
    basins()
    parity()
    spurious()


if __name__ == "__main__":
    main()
