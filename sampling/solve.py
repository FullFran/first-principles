"""Run a chain and report what it is worth, not just what it returned.

Owns the loop and the diagnostics, not the physics. Its job is the one thing
`photon-transport/` established and this entry has to repeat one level deeper:
a Monte Carlo result without an error bar is not a measurement.

The twist here is that the samples are *correlated*. A chain moves in small
steps, so consecutive states are nearly the same state, and sigma/sqrt(N) is
an underestimate of the error by however many steps it takes to forget where
it was. The honest denominator is the effective sample size,

    ESS = N / (1 + 2 * sum of the autocorrelations)

and it can be smaller than N by orders of magnitude without anything looking
wrong.
"""

from dataclasses import dataclass

import numpy as np

import distribution
from methods import ALL as METHODS

__all__ = ["chain", "Chain", "METHODS", "DEFAULT_METHOD",
           "autocorrelation_time", "effective_sample_size"]

DEFAULT_METHOD = "metropolis"


def autocorrelation_time(series, cutoff=6.0):
    """Integrated autocorrelation time, summed until the estimate goes noisy.

    Truncating matters: the tail of an empirical autocorrelation is noise, and
    summing all of it adds variance without adding signal. The window is the
    standard automatic rule -- stop once the lag exceeds `cutoff` times the
    running estimate.
    """
    series = np.asarray(series, dtype=float)
    series = series - series.mean()
    size = series.size
    if size < 4 or np.allclose(series, 0.0):
        return 1.0

    spectrum = np.fft.rfft(series, n=2 * size)
    correlation = np.fft.irfft(spectrum * np.conjugate(spectrum), n=2 * size)[:size]
    if correlation[0] <= 0:
        return 1.0
    correlation /= correlation[0]

    total = 1.0
    for lag in range(1, size):
        total += 2.0 * correlation[lag]
        if lag >= cutoff * total:
            break
    return float(max(total, 1.0))


def effective_sample_size(series):
    series = np.asarray(series, dtype=float)
    return float(series.size / autocorrelation_time(series))


@dataclass(frozen=True)
class Chain:
    samples: np.ndarray
    acceptance: float
    steps: int
    method: str
    temperature: float

    def mean(self, power=1):
        return float(np.mean(self.samples[:, 0] ** power))

    def error(self, power=1):
        """Standard error, corrected for how correlated the chain is."""
        series = self.samples[:, 0] ** power
        return float(np.std(series, ddof=1) / np.sqrt(effective_sample_size(series)))

    def sigma_from(self, reference, power=1):
        floor = np.finfo(float).eps * max(abs(self.mean(power)), 1.0)
        return abs(self.mean(power) - reference) / max(self.error(power), floor)


def chain(target="gaussian", method=DEFAULT_METHOD, temperature=1.0, steps=100_000,
          scale=1.0, start=None, dim=1, seed=0, burn_in=0.1):
    """Run one chain and return its samples with its diagnostics.

    `burn_in` is a fraction discarded from the front. It is a confession, not
    a fix: the chain starts wherever you put it and needs time to forget, and
    no amount of discarding helps a chain that never reached the right place
    at all -- see experiments/double_well.py.
    """
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}; available: {sorted(METHODS)}")
    if isinstance(target, str):
        if target not in distribution.TARGETS:
            raise ValueError(f"unknown target {target!r}; "
                             f"available: {sorted(distribution.TARGETS)}")
        target = distribution.TARGETS[target]
    if steps < 2:
        raise ValueError("need at least two steps to estimate anything")
    if not 0.0 <= burn_in < 1.0:
        raise ValueError(f"burn_in must be a fraction in [0, 1), got {burn_in}")
    if scale <= 0:
        raise ValueError(f"scale must be positive, got {scale}")
    distribution.check_temperature(temperature)

    rng = np.random.default_rng(seed)
    state = np.zeros(dim) if start is None else np.asarray(start, dtype=float).reshape(-1)
    solver = METHODS[method]

    samples = np.empty((steps, state.size))
    accepted = 0
    for index in range(steps):
        state, took_it = solver.step(rng, state, target, temperature, scale)
        samples[index] = state
        accepted += took_it

    keep = int(burn_in * steps)
    return Chain(samples=samples[keep:], acceptance=accepted / steps, steps=steps,
                 method=method, temperature=temperature)
