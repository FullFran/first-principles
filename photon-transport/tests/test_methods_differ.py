"""Where the estimators part company -- and why that is the point.

Both are unbiased: they estimate the same number and the contract suite pins
both against Beer-Lambert. They differ in variance, by factors that reach the
absurd, and that difference is a property of the estimator rather than of the
physics. A contract that demanded a common variance would be asserting
something false; one that demanded no variance would exclude the honest one.
"""

import numpy as np
import pytest

import physics
import solve
from methods import ALL as METHODS


def spread(method, mu=1.0, thickness=1.0, half_angle=np.pi / 4,
           photons=200_000, seed=0):
    rng = np.random.default_rng(seed)
    cos_theta, _ = physics.sample_direction(rng, photons, half_angle)
    return float(np.var(METHODS[method].contributions(
        rng, cos_theta, mu, thickness), ddof=1))


def test_the_analog_estimator_reports_one_bit_per_photon():
    """Each photon got through or it did not, so the sample is a coin flip and
    nothing else. Everything the geometry knows is discarded."""
    rng = np.random.default_rng(0)
    cos_theta, _ = physics.sample_direction(rng, 5_000, np.pi / 4)
    weights = METHODS["analog"].contributions(rng, cos_theta, 1.0, 1.0)
    assert set(np.unique(weights)) <= {0.0, 1.0}


def test_the_weighted_estimator_reports_a_probability_per_photon():
    rng = np.random.default_rng(0)
    cos_theta, _ = physics.sample_direction(rng, 5_000, np.pi / 4)
    weights = METHODS["weighted"].contributions(rng, cos_theta, 1.0, 1.0)
    assert len(np.unique(weights)) > 1_000
    assert np.all((weights > 0.0) & (weights < 1.0))


def test_the_analog_variance_is_binomial_and_ignores_the_cone():
    """Var = T(1-T) whatever the geometry, because the estimator only ever
    sees a yes or a no."""
    for half_angle in (0.0, np.pi / 12, np.pi / 4):
        reference = physics.cone_transmittance(1.0, 1.0, half_angle)
        measured = spread("analog", half_angle=half_angle)
        assert measured == pytest.approx(reference * (1 - reference), rel=0.05)


def test_weighting_removes_variance_and_narrowing_the_cone_removes_more():
    """The only randomness left in the weighted estimator is the spread of
    path lengths across the cone, so closing the cone closes the gap between
    it and an exact calculation. The analog one does not improve at all."""
    ratios = []
    for half_angle in (np.pi / 4, np.pi / 12, np.pi / 36):
        ratios.append(spread("analog", half_angle=half_angle)
                      / spread("weighted", half_angle=half_angle))
    assert ratios[0] > 100
    assert ratios == sorted(ratios), "narrowing the cone must widen the gap"
    assert ratios[-1] > 100 * ratios[0]


def test_a_collimated_beam_makes_the_weighted_estimator_exact():
    """Every photon travels the same distance, so every contribution is the
    same number and there is nothing left to be uncertain about. The analog
    estimator still flips a coin per photon and still needs an error bar."""
    exact = solve.transmitted(1.0, 1.0, 0.0, 50_000, "weighted", seed=0)
    sampled = solve.transmitted(1.0, 1.0, 0.0, 50_000, "analog", seed=0)

    assert exact.error < 1e-15
    assert exact.value == pytest.approx(physics.transmittance(1.0, 1.0), rel=1e-12)
    assert sampled.error > 1e-3


def test_the_weighted_estimator_needs_far_fewer_photons_for_the_same_error():
    """The practical statement of the same fact.

    Error falls as 1/sqrt(N) for both, so matching an error bar costs photons
    in proportion to variance: N_weighted = N_analog * Var_w / Var_a. At a 45
    degree cone that ratio is about 1/165, and the doubling search below lands
    on 2048 against 200000 -- about one percent of the budget for the same
    answer to the same precision.
    """
    budget = 200_000
    target = solve.transmitted(1.0, 1.0, np.pi / 4, budget, "analog", seed=0).error
    photons = 2
    while solve.transmitted(1.0, 1.0, np.pi / 4, photons, "weighted",
                            seed=0).error > target:
        photons *= 2
        assert photons <= budget, "weighted should not need the same budget"
    assert photons < budget // 50
