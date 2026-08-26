"""Contract tests: what every sampler must satisfy, whatever it is.

Register a method in `methods/` and it inherits this suite. What it must NOT
inherit is that its stationary distribution is the target -- Metropolis is
exact and unadjusted Langevin is not, and that difference is the entire point
of the entry. It lives in test_methods_differ.py.

So the contract asserts what both genuinely deliver: the chain moves, it stays
where the energy is low, it reproduces what symmetry alone fixes, and it
reports diagnostics that mean something.
"""

import numpy as np
import pytest

import distribution as dist
import solve
from methods import ALL as METHODS

METHOD_NAMES = sorted(METHODS)
pytestmark = pytest.mark.parametrize("method", METHOD_NAMES)

SCALES = {"metropolis": 1.0, "langevin": 0.02}


def run(method, target="gaussian", temperature=1.0, steps=50_000, **kwargs):
    return solve.chain(target, method, temperature, steps=steps,
                       scale=SCALES[method], seed=0, **kwargs)


def test_a_symmetric_target_gives_a_zero_mean(method):
    """Symmetry fixes the first moment whatever the step size, so both methods
    must get it. The second moment is where they part company."""
    chain = run(method)
    assert chain.sigma_from(0.0, power=1) < 4.0


def test_the_chain_visits_the_low_energy_region(method):
    """The weakest possible statement of working at all: more time is spent
    where exp(-E/T) is large than where it is small."""
    chain = run(method)
    near = np.mean(np.abs(chain.samples[:, 0]) < 1.0)
    far = np.mean(np.abs(chain.samples[:, 0]) > 2.0)
    assert near > 0.5 > far


def test_the_chain_actually_moves(method):
    chain = run(method, steps=5_000)
    assert len(np.unique(chain.samples[:, 0])) > 100
    assert chain.samples[:, 0].std() > 0.1


def test_a_run_is_reproducible(method):
    first, second = run(method, steps=5_000), run(method, steps=5_000)
    assert np.array_equal(first.samples, second.samples)


def test_a_colder_chain_stays_closer_to_the_minimum(method):
    """T sets the width of what gets explored. This is the same knob that turns
    a sampler into an optimiser as it goes to zero."""
    widths = [run(method, temperature=T).samples[:, 0].std()
              for T in (0.25, 1.0, 4.0)]
    assert widths == sorted(widths)


def test_the_shape_of_the_samples_follows_the_dimension(method):
    for dim in (1, 3):
        chain = solve.chain("gaussian", method, 1.0, steps=2_000,
                            scale=SCALES[method], dim=dim, seed=0)
        assert chain.samples.shape[1] == dim


def test_burn_in_is_discarded(method):
    full = run(method, steps=10_000, burn_in=0.0)
    trimmed = run(method, steps=10_000, burn_in=0.25)
    assert len(full.samples) == 10_000
    assert len(trimmed.samples) == 7_500
    assert np.array_equal(full.samples[2_500:], trimmed.samples)


def test_the_acceptance_rate_is_a_probability(method):
    assert 0.0 <= run(method, steps=5_000).acceptance <= 1.0


def test_correlated_samples_are_worth_less_than_independent_ones(method):
    """The diagnostic that matters here, and the reason sigma/sqrt(N) is not
    the error bar. A chain moves in small steps, so consecutive states are
    nearly the same state."""
    chain = run(method, steps=40_000)
    series = chain.samples[:, 0]
    assert solve.autocorrelation_time(series) > 1.0
    assert solve.effective_sample_size(series) < series.size

    naive = series.std(ddof=1) / np.sqrt(series.size)
    assert chain.error(power=1) > naive


def test_independent_draws_are_worth_their_face_value(method):
    """The control for the test above: on genuinely independent samples the
    correction has to do nothing, or it is measuring the estimator and not the
    chain."""
    independent = np.random.default_rng(0).standard_normal(50_000)
    assert solve.autocorrelation_time(independent) == pytest.approx(1.0, abs=0.15)


def test_unknown_method_is_rejected(method):
    with pytest.raises(ValueError, match="unknown method"):
        solve.chain("gaussian", method="gibbs", steps=100)


def test_unknown_target_is_rejected(method):
    with pytest.raises(ValueError, match="unknown target"):
        solve.chain("mexican_hat", method, steps=100, scale=SCALES[method])


def test_a_non_positive_temperature_is_rejected(method):
    with pytest.raises(ValueError, match="temperature must be positive"):
        solve.chain("gaussian", method, temperature=0.0, steps=100,
                    scale=SCALES[method])


def test_a_non_positive_scale_is_rejected(method):
    with pytest.raises(ValueError, match="scale must be positive"):
        solve.chain("gaussian", method, steps=100, scale=0.0)


def test_a_burn_in_of_everything_is_rejected(method):
    with pytest.raises(ValueError, match="burn_in"):
        solve.chain("gaussian", method, steps=100, scale=SCALES[method], burn_in=1.0)
