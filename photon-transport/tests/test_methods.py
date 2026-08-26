"""Contract tests: what every estimator must satisfy, whatever it is.

Register a method in `methods/` and it inherits this suite. What it must NOT
inherit is any claim about its variance -- that is the entire difference
between the two here, and it lives in test_methods_differ.py.
"""

import numpy as np
import pytest

import physics
import solve
from methods import ALL as METHODS

METHOD_NAMES = sorted(METHODS)
pytestmark = pytest.mark.parametrize("method", METHOD_NAMES)

CASES = [(1.0, 1.0, 0.0), (1.0, 1.0, np.pi / 12), (2.0, 0.5, np.pi / 4),
         (0.3, 4.0, np.pi / 6), (5.0, 1.0, np.pi / 8)]


@pytest.mark.parametrize("mu, thickness, half_angle", CASES)
def test_the_estimate_agrees_with_the_closed_form(method, mu, thickness, half_angle):
    """The test that decides whether any of this is right.

    Cross-checking two estimators proves they agree; checking against Beer-
    Lambert averaged over the cone proves they are correct. Four standard
    errors, so a correct estimator fails this by chance about once in
    sixteen thousand runs -- and the seed is fixed anyway.
    """
    reference = physics.cone_transmittance(mu, thickness, half_angle)
    estimate = solve.transmitted(mu, thickness, half_angle, 200_000, method, seed=0)
    assert estimate.sigma_from(reference) < 4.0


def test_a_transparent_slab_transmits_everything(method):
    estimate = solve.transmitted(0.0, 3.0, np.pi / 4, 5_000, method, seed=0)
    assert estimate.value == pytest.approx(1.0)
    assert estimate.error == pytest.approx(0.0)


def test_a_slab_of_no_thickness_transmits_everything(method):
    estimate = solve.transmitted(4.0, 0.0, np.pi / 4, 5_000, method, seed=0)
    assert estimate.value == pytest.approx(1.0)


def test_a_very_thick_slab_transmits_nothing(method):
    estimate = solve.transmitted(50.0, 2.0, np.pi / 8, 20_000, method, seed=0)
    assert estimate.value < 1e-6


def test_contributions_are_probabilities(method):
    """Every per-photon contribution has to be something that could be a
    transmitted fraction on its own, or the mean of them is not one either."""
    rng = np.random.default_rng(0)
    cos_theta, _ = physics.sample_direction(rng, 20_000, np.pi / 4)
    weights = METHODS[method].contributions(rng, cos_theta, 1.5, 1.0)
    assert weights.shape == cos_theta.shape
    assert np.all((weights >= 0.0) & (weights <= 1.0))


def test_a_run_is_reproducible(method):
    first = solve.transmitted(1.0, 1.0, np.pi / 4, 10_000, method, seed=11)
    second = solve.transmitted(1.0, 1.0, np.pi / 4, 10_000, method, seed=11)
    assert (first.value, first.error) == (second.value, second.error)


def test_the_error_falls_as_one_over_root_n(method):
    """The central fact of Monte Carlo, and the reason it is a last resort in
    low dimension: one more digit costs a hundred times the work."""
    coarse = solve.transmitted(1.0, 1.0, np.pi / 4, 10_000, method, seed=3)
    fine = solve.transmitted(1.0, 1.0, np.pi / 4, 160_000, method, seed=3)
    if coarse.error == 0.0:
        pytest.skip("a zero-variance estimator has no error to shrink")
    assert fine.error == pytest.approx(coarse.error / 4.0, rel=0.1)


def test_more_attenuation_transmits_less(method):
    values = [solve.transmitted(mu, 1.0, np.pi / 8, 50_000, method, seed=0).value
              for mu in (0.5, 1.0, 2.0, 4.0)]
    assert values == sorted(values, reverse=True)


def test_a_gain_medium_is_rejected(method):
    with pytest.raises(ValueError, match="non-negative"):
        solve.transmitted(-1.0, 1.0, 0.0, 1_000, method)


def test_too_few_photons_is_rejected(method):
    """One photon has a mean and no spread, so it cannot carry an error bar."""
    with pytest.raises(ValueError, match="at least two photons"):
        solve.transmitted(1.0, 1.0, 0.0, 1, method)


def test_unknown_method_is_rejected(method):
    with pytest.raises(ValueError, match="unknown method"):
        solve.transmitted(1.0, 1.0, 0.0, 1_000, method="ray-tracing")
