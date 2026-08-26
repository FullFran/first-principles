"""Domain tests: the target, its density, and the closed forms it implies.

Nothing here runs a chain. If these fail the reference is wrong, and then no
sampler can be judged at all -- which is the whole reason the reference is
computed by quadrature rather than by a second sampler.
"""

import numpy as np
import pytest

import distribution as dist


# --- the closed forms -------------------------------------------------------

@pytest.mark.parametrize("temperature", [0.25, 0.5, 1.0, 2.0, 4.0])
def test_the_gaussian_second_moment_is_the_temperature(temperature):
    """E = x^2/2 gives p proportional to exp(-x^2/2T), a normal of variance T.
    The one target where a sampler has nowhere to hide."""
    assert dist.exact_moment(dist.GAUSSIAN, temperature, 2) == pytest.approx(
        temperature, rel=1e-6)


def test_the_gaussian_is_symmetric():
    assert dist.exact_moment(dist.GAUSSIAN, 1.0, 1) == pytest.approx(0.0, abs=1e-9)
    assert dist.exact_probability(dist.GAUSSIAN, 1.0, low=0.0) == pytest.approx(0.5)


def test_the_support_is_wide_enough_to_not_truncate():
    """The reference has to be more accurate than anything it judges. At +-6
    the Gaussian was already wrong in the fourth decimal at T = 2, which is
    larger than the error a long chain has."""
    narrow = dist.Target(dist.GAUSSIAN.name, dist.GAUSSIAN.energy,
                         dist.GAUSSIAN.gradient, support=(-6.0, 6.0))
    assert abs(dist.exact_moment(narrow, 2.0, 2) - 2.0) > 1e-4
    assert abs(dist.exact_moment(dist.GAUSSIAN, 2.0, 2) - 2.0) < 1e-6


def test_cooling_the_double_well_concentrates_it_in_the_lower_minimum():
    populations = [dist.exact_probability(dist.DOUBLE_WELL, T)
                   for T in (2.0, 1.0, 0.5, 0.2, 0.05)]
    assert populations == sorted(populations)
    assert populations[-1] > 0.999


def test_the_leftover_population_follows_the_energy_gap():
    """The sharper claim, and the one worth testing.

    An earlier version of this asserted the cold population was 1.0 to a
    millionth and failed at 0.9999930. That residue is not quadrature error --
    it is exp(-dE/T) with dE the gap between the two minima, which at T = 0.05
    is 6e-6. The test was wrong and the physics was right.

    So assert the law instead of a round number: across three decades of
    population the ratio to exp(-dE/T) stays put. The constant it stays at is
    not 1 but about 1.1, which is the ratio of the two wells' widths -- the
    prefactor a Laplace approximation puts in front.
    """
    grid = np.linspace(-2, 2, 200_001)[:, None]
    energy = dist.DOUBLE_WELL.energy(grid)
    gap = energy[grid[:, 0] < 0].min() - energy[grid[:, 0] > 0].min()
    assert gap > 0

    prefactors = []
    for temperature in (0.05, 0.1, 0.2):
        left = 1.0 - dist.exact_probability(dist.DOUBLE_WELL, temperature)
        prefactors.append(left / np.exp(-gap / temperature))
    assert min(prefactors) > 1.0 and max(prefactors) < 1.25
    assert max(prefactors) / min(prefactors) < 1.1


def test_the_double_well_has_two_minima_separated_by_a_barrier():
    grid = np.linspace(-2, 2, 4001)[:, None]
    energy = dist.DOUBLE_WELL.energy(grid)
    left = energy[grid[:, 0] < 0].min()
    right = energy[grid[:, 0] > 0].min()
    barrier = energy[np.abs(grid[:, 0]) < 0.2].min()
    assert right < left < barrier


# --- the density ------------------------------------------------------------

def test_only_energy_differences_matter():
    """Shifting an energy by a constant multiplies every weight by the same
    factor and cancels out of every ratio. That is why Z never has to be
    computed, and it is the premise both methods rest on."""
    shifted = dist.Target("shifted", lambda x: dist.GAUSSIAN.energy(x) + 137.0,
                          dist.GAUSSIAN.gradient, dist.GAUSSIAN.support)
    points = np.array([[0.3], [-1.2]])
    original = dist.boltzmann_weight(dist.GAUSSIAN, points, 1.0)
    moved = dist.boltzmann_weight(shifted, points, 1.0)
    assert original[0] / original[1] == pytest.approx(moved[0] / moved[1])
    assert dist.exact_moment(shifted, 1.0, 2) == pytest.approx(
        dist.exact_moment(dist.GAUSSIAN, 1.0, 2))


def test_a_colder_gaussian_is_a_narrower_one():
    assert dist.exact_moment(dist.GAUSSIAN, 0.25, 2) < dist.exact_moment(
        dist.GAUSSIAN, 1.0, 2)


# --- gradients --------------------------------------------------------------

@pytest.mark.parametrize("name", ["gaussian", "double_well", "free"])
def test_the_gradient_is_the_derivative_of_the_energy(name):
    """Langevin follows this vector, so if it is wrong the chain samples a
    different distribution and says nothing. Checked the same way `mlp/` checks
    backpropagation: against a derivative computed another way."""
    target = dist.TARGETS[name]
    points = np.linspace(-1.8, 1.8, 25)[:, None]
    step = 1e-6
    numeric = np.array([
        (target.energy(p + step) - target.energy(p - step)) / (2 * step)
        for p in points])
    assert np.allclose(target.gradient(points)[:, 0], numeric, atol=1e-5)


def test_the_free_target_has_no_energy_and_no_gradient():
    """Langevin on this is Brownian motion, which is the bridge to diffusion."""
    points = np.array([[-3.0], [0.0], [7.0]])
    assert np.all(dist.FREE.energy(points) == 0.0)
    assert np.all(dist.FREE.gradient(points) == 0.0)


# --- shapes -----------------------------------------------------------------

def test_energy_maps_a_state_to_a_scalar_and_a_batch_to_a_vector():
    assert np.ndim(dist.GAUSSIAN.energy(np.array([1.0, 2.0]))) == 0
    assert dist.GAUSSIAN.energy(np.zeros((7, 3))).shape == (7,)


# --- invariants -------------------------------------------------------------

@pytest.mark.parametrize("temperature", [0.0, -1.0])
def test_a_non_positive_temperature_is_rejected(temperature):
    """T = 0 is not a distribution but a delta on the minimum, and the dynamics
    that finds it is the descent in hopfield/ and mlp/, not a sampler."""
    with pytest.raises(ValueError, match="temperature must be positive"):
        dist.check_temperature(temperature)
    with pytest.raises(ValueError, match="temperature must be positive"):
        dist.exact_moment(dist.GAUSSIAN, temperature)
