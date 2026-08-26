"""The same machinery optimises or samples, depending on one number.

Metropolis at a fixed temperature draws from exp(-E/T). Lower the temperature
while it runs and the same code stops exploring and starts converging on the
lowest energy it can find. That is simulated annealing, and the only thing
that changed is that T became a function of time.

The claim from chapter 10 of the book, tested here: optimising and sampling
are the same operation at two temperatures. Too cold and the chain never
leaves where it started; too hot and it never settles; only cooling does both.

Prediction: the fixed-cold run stays in whichever well it began in, the
fixed-hot run finds the right well and then keeps leaving it, and the cooled
run finds it and stays.

One thing measured while setting this up, because the first version of it
predicted the wrong outcome. The proposal width has to be *smaller than the
distance between the wells* or none of this is true: at a width of 0.5 the
frozen chain proposes a jump straight from one minimum to the other, the move
is downhill so it is accepted whatever the temperature, and the barrier never
enters into it. Annealing is a cure for local moves. Give a chain moves large
enough to clear the barrier in one step and there was no problem to solve --
and also no chance of that working in any real number of dimensions.
"""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import distribution as dist
import solve
from methods import ALL as METHODS

STEPS, SCALE, START = 60_000, 0.25, -1.0


def cooled(schedule, seed=0):
    """One Metropolis chain whose temperature follows a schedule.

    Written here rather than in solve.py on purpose: a time-dependent
    temperature is no longer a chain with a stationary distribution, so it is
    not a sampler and does not belong behind the sampler contract. It is an
    optimiser that borrows the sampler's step.
    """
    rng = np.random.default_rng(seed)
    state = np.array([START])
    trace, energies = np.empty(STEPS), np.empty(STEPS)
    for index in range(STEPS):
        temperature = schedule(index / STEPS)
        state, _ = METHODS["metropolis"].step(
            rng, state, dist.DOUBLE_WELL, temperature, SCALE)
        trace[index] = state[0]
        energies[index] = dist.DOUBLE_WELL.energy(state)
    return trace, energies


def main():
    grid = np.linspace(-2, 2, 200_001)[:, None]
    best = float(dist.DOUBLE_WELL.energy(grid).min())
    where = float(grid[np.argmin(dist.DOUBLE_WELL.energy(grid)), 0])
    print(f"global minimum: E = {best:.5f} at x = {where:+.4f}, starting at {START}\n")

    runs = {
        "frozen  (T = 0.02)": lambda _: 0.02,
        "hot     (T = 2.0)": lambda _: 2.0,
        "cooled  (2.0 -> 0.02)": lambda progress: 2.0 * (0.01 ** progress),
    }

    print(f"  {'schedule':>22} {'final x':>9} {'final E':>10} {'best E seen':>12} "
          f"{'ended in':>10}")
    traces = {}
    for label, schedule in runs.items():
        trace, energies = cooled(schedule)
        traces[label] = (trace, energies)
        print(f"  {label:>22} {trace[-1]:>+9.4f} {energies[-1]:>10.5f} "
              f"{energies.min():>12.5f} "
              f"{'right' if trace[-1] > 0 else 'LEFT well':>10}")

    verdicts = {label: ("the right well" if trace[-1] > 0 else "the WRONG well")
                for label, (trace, _) in traces.items()}
    print()
    for label, verdict in verdicts.items():
        print(f"  {label.strip():<22} ended in {verdict}")
    print("\n  frozen never had the energy to cross, so it optimised whichever well")
    print("  it happened to start in. hot crossed constantly and never settled --")
    print("  it is sampling, not optimising. Only cooling did both: it explored")
    print("  while it was hot enough to, then froze where it found.")

    fig, (left, right) = plt.subplots(1, 2, figsize=(11.4, 4.4))
    colours = ("#2e7d94", "#e08a1e", "#c0392b")
    for (label, (trace, _)), colour in zip(traces.items(), colours):
        left.plot(trace, lw=0.6, color=colour, alpha=0.85, label=label.strip())
    left.axhline(where, color="0.35", ls="--", lw=1.2)
    left.annotate("global minimum", xy=(STEPS * 0.55, where + 0.12),
                  fontsize=8.5, color="0.35")
    left.set(xlabel="step", ylabel="x", ylim=(-2, 2))
    left.set_title("Where each schedule spends its time", fontsize=10.5, pad=8)
    left.legend(frameon=False, fontsize=8.5, loc="upper left")

    for (label, (_, energies)), colour in zip(traces.items(), colours):
        right.plot(np.minimum.accumulate(energies), lw=1.6, color=colour,
                   label=label.strip())
    right.axhline(best, color="0.35", ls="--", lw=1.2, label="global minimum")
    right.set(xlabel="step", ylabel="best energy seen so far")
    right.set_title("Only cooling both explores and settles", fontsize=10.5, pad=8)
    right.legend(frameon=False, fontsize=8.5)

    fig.tight_layout()
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "annealing.png", dpi=140, bbox_inches="tight")
    print(f"\nfigure -> {out / 'annealing.png'}")


if __name__ == "__main__":
    main()
