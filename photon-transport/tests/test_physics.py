"""Domain tests: emission, attenuation, geometry and the closed form.

Nothing here runs an estimator. If these fail the physics is wrong; if these
pass and a method fails, the estimator is wrong.
"""

import ast
from pathlib import Path

import numpy as np
import pytest

import physics


# --- the closed form --------------------------------------------------------

def test_beer_lambert_at_normal_incidence():
    for mu, thickness in ((1.0, 1.0), (0.5, 3.0), (7.0, 0.1)):
        assert physics.transmittance(mu, thickness) == pytest.approx(
            np.exp(-mu * thickness))


def test_transparent_medium_transmits_everything():
    assert physics.transmittance(0.0, 5.0) == pytest.approx(1.0)


def test_zero_thickness_transmits_everything():
    assert physics.transmittance(9.0, 0.0) == pytest.approx(1.0)


def test_transmittance_falls_with_thickness_and_with_attenuation():
    assert physics.transmittance(1.0, 2.0) < physics.transmittance(1.0, 1.0)
    assert physics.transmittance(2.0, 1.0) < physics.transmittance(1.0, 1.0)


def test_the_only_length_scale_is_the_mean_free_path():
    """mu and thickness never appear apart, only as the product mu*thickness.
    Two slabs with the same optical depth are the same slab."""
    assert physics.transmittance(0.5, 4.0) == pytest.approx(
        physics.transmittance(4.0, 0.5))
    assert physics.mean_free_path(4.0) == pytest.approx(0.25)


# --- geometry ---------------------------------------------------------------

def test_a_tilted_photon_crosses_more_material():
    assert physics.slab_path(1.0, 1.0) == pytest.approx(1.0)
    assert physics.slab_path(0.5, 1.0) == pytest.approx(2.0)
    assert physics.slab_path(np.cos(np.pi / 3), 3.0) == pytest.approx(6.0)


def test_the_angular_dependence_is_entirely_one_over_cosine():
    cos_theta = np.array([1.0, 0.9, 0.5, 0.1])
    assert np.allclose(physics.transmittance(1.0, 1.0, cos_theta),
                       np.exp(-1.0 / cos_theta))


# --- the cone average -------------------------------------------------------

def test_a_collimated_cone_is_beer_lambert_exactly():
    assert physics.cone_transmittance(1.0, 1.0, 0.0) == pytest.approx(
        physics.transmittance(1.0, 1.0), rel=1e-12)


def test_opening_the_cone_lowers_the_transmitted_fraction():
    """Every off-axis photon crosses more material than an axial one, and none
    crosses less, so widening the cone can only attenuate more."""
    previous = physics.cone_transmittance(1.0, 1.0, 0.0)
    for half_angle in (np.pi / 36, np.pi / 12, np.pi / 6, np.pi / 4):
        current = physics.cone_transmittance(1.0, 1.0, half_angle)
        assert current < previous
        previous = current


def test_the_cone_average_is_bracketed_by_its_extremes():
    """It averages exp(-mu L / c) over c in [cos a, 1], so it must sit between
    the axial ray and the most tilted one."""
    mu, thickness, half_angle = 1.3, 2.0, np.pi / 5
    average = physics.cone_transmittance(mu, thickness, half_angle)
    assert physics.transmittance(mu, thickness, np.cos(half_angle)) < average
    assert average < physics.transmittance(mu, thickness, 1.0)


# --- sampling ---------------------------------------------------------------

def test_directions_are_uniform_over_solid_angle_not_over_the_angle():
    """The discriminating test. dOmega = sin(theta) dtheta dphi, so cos(theta)
    is the flat variable. Sampling theta uniformly instead crowds photons
    towards the axis, and the mean cosine is the fingerprint:

        uniform in cos(theta):  <cos> = (1 + cos a)/2
        uniform in theta:       <cos> = sin(a)/a

    which differ by 5% at a = 45 degrees, and never by zero.
    """
    half_angle = np.pi / 4
    rng = np.random.default_rng(0)
    cos_theta, _ = physics.sample_direction(rng, 400_000, half_angle)

    correct = (1.0 + np.cos(half_angle)) / 2.0
    wrong = np.sin(half_angle) / half_angle
    assert cos_theta.mean() == pytest.approx(correct, abs=2e-3)
    assert abs(cos_theta.mean() - wrong) > 0.02


def test_directions_stay_inside_the_cone():
    rng = np.random.default_rng(1)
    for half_angle in (0.0, np.pi / 12, np.pi / 4, 1.5):
        cos_theta, azimuth = physics.sample_direction(rng, 5_000, half_angle)
        assert np.all(cos_theta >= np.cos(half_angle) - 1e-12)
        assert np.all(cos_theta <= 1.0)
        assert np.all((azimuth >= 0) & (azimuth < 2 * np.pi))


def test_free_paths_are_exponential():
    """Check the survival function rather than the mean: a wrong distribution
    with the right mean would pass a mean test and fail this one."""
    rng = np.random.default_rng(2)
    mu = 2.0
    paths = physics.sample_free_path(rng, 400_000, mu)
    assert paths.mean() == pytest.approx(1.0 / mu, rel=5e-3)
    for distance in (0.1, 0.5, 1.0, 2.0):
        survived = np.mean(paths > distance)
        assert survived == pytest.approx(np.exp(-mu * distance), abs=3e-3)


def test_a_free_path_is_never_infinite():
    """rng.random() returns [0, 1), and log(0) is -inf. Drawing 1 - U puts the
    sample on (0, 1] so the singularity is unreachable, not merely unlikely."""
    rng = np.random.default_rng(3)
    assert np.all(np.isfinite(physics.sample_free_path(rng, 200_000, 1.0)))


def test_a_transparent_medium_has_infinite_free_paths():
    rng = np.random.default_rng(4)
    assert np.all(np.isinf(physics.sample_free_path(rng, 10, 0.0)))
    assert np.isinf(physics.mean_free_path(0.0))


def test_sampling_is_reproducible_from_a_seed():
    first = physics.sample_free_path(np.random.default_rng(7), 100, 1.0)
    second = physics.sample_free_path(np.random.default_rng(7), 100, 1.0)
    assert np.array_equal(first, second)


# --- invariants -------------------------------------------------------------

def test_a_gain_medium_is_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        physics.transmittance(-1.0, 1.0)
    with pytest.raises(ValueError, match="non-negative"):
        physics.sample_free_path(np.random.default_rng(0), 5, -1.0)


def test_negative_thickness_is_rejected():
    with pytest.raises(ValueError, match="thickness"):
        physics.transmittance(1.0, -1.0)


def test_a_cone_reaching_ninety_degrees_is_rejected():
    """At pi/2 the path through the slab diverges: the photon travels parallel
    to it and never comes out the far side."""
    with pytest.raises(ValueError, match="half_angle"):
        physics.check_cone(np.pi / 2)
    with pytest.raises(ValueError, match="half_angle"):
        physics.sample_direction(np.random.default_rng(0), 5, 2.0)


def test_a_grazing_photon_is_rejected():
    with pytest.raises(ValueError, match="cos_theta must be positive"):
        physics.slab_path(0.0, 1.0)
    with pytest.raises(ValueError, match="cos_theta must be positive"):
        physics.slab_path(np.array([0.5, -0.1]), 1.0)


def test_the_domain_imports_no_method():
    """Rule 7, checked instead of asserted.

    Nothing else in this suite would notice a violation. The contract asks
    whether every method obeys the domain, which is the other direction, and
    an import written inside a function body does not even fail at
    collection -- the domain can `import methods`, use it, and leave the
    whole suite green.

    Deliberately shallow: it reads the imports the parser can see, so a
    module fetched through importlib at runtime would walk past it. It
    catches the way the mistake actually gets made.
    """
    domain = Path(__file__).resolve().parent.parent / "physics.py"

    imported = []
    for node in ast.walk(ast.parse(domain.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            imported += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.append(node.module)
            else:  # from . import methods
                imported += [alias.name for alias in node.names]

    offenders = sorted(
        name for name in imported
        if name == "methods" or name.startswith("methods.")
    )
    assert not offenders, (
        f"{domain.name} imports {offenders} -- the equations may not "
        f"import the algorithm; the arrow only points the other way"
    )
