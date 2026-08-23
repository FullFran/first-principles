"""Domain tests: statements about nature, checked without solving any stack.

Nothing here imports a method. If these fail, the physics is wrong. If these
pass and a method still fails, the algorithm is wrong. Keeping the two
diagnoses apart is the whole reason the split exists.
"""

import numpy as np
import pytest

import physics

GREEN = 550.0
ANGLES = [0.0, 15.0, 30.0, 45.0, 60.0, 75.0]


def fresnel_reference(pol, n1, n2, theta1):
    c1 = np.cos(theta1)
    c2 = np.cos(np.arcsin(n1 * np.sin(theta1) / n2))
    if pol == "s":
        return (n1 * c1 - n2 * c2) / (n1 * c1 + n2 * c2)
    return (n2 * c1 - n1 * c2) / (n2 * c1 + n1 * c2)


@pytest.mark.parametrize("pol", ["s", "p"])
@pytest.mark.parametrize("angle", ANGLES)
def test_fresnel_matches_the_textbook_form(pol, angle):
    theta = np.deg2rad(angle)
    n = np.array([1.0, 1.5], dtype=complex)
    cos_theta = physics.layer_cosines(n, theta)
    r, _ = physics.fresnel(pol, n[0], n[1], cos_theta[0], cos_theta[1])
    assert r == pytest.approx(fresnel_reference(pol, 1.0, 1.5, theta), abs=1e-12)


def test_snell_invariant_is_conserved_across_layers():
    n = np.array([1.0, 1.5, 2.3, 1.45], dtype=complex)
    theta0 = np.deg2rad(40)
    cos_theta = physics.layer_cosines(n, theta0)
    sin_theta = np.sqrt(1 - cos_theta**2)
    assert np.allclose(n * sin_theta, n[0] * np.sin(theta0), atol=1e-14)


def test_cosine_is_purely_imaginary_past_the_critical_angle():
    """Beyond total internal reflection the wave is evanescent, not travelling."""
    n = np.array([1.5, 1.0], dtype=complex)
    cos_theta = physics.layer_cosines(n, np.deg2rad(70))
    assert abs(cos_theta[1].real) < 1e-15
    assert cos_theta[1].imag > 0


@pytest.mark.parametrize("n_film", [1.5 + 0.1j, 0.15 + 3.5j])
@pytest.mark.parametrize("angle", ANGLES)
def test_absorbing_layer_decays_forward(n_film, angle):
    """The branch of the square root must attenuate, never amplify."""
    n = np.array([1.0, n_film], dtype=complex)
    cos_theta = physics.layer_cosines(n, np.deg2rad(angle))
    assert (n[1] * cos_theta[1]).imag > 0


@pytest.mark.parametrize("pol", ["s", "p"])
def test_normal_flux_is_positive_for_a_passive_medium(pol):
    n = np.array([1.0, 1.5 + 0.2j], dtype=complex)
    cos_theta = physics.layer_cosines(n, np.deg2rad(35))
    assert physics.normal_flux(pol, n[1], cos_theta[1]) > 0


def test_reflectance_is_the_squared_modulus():
    R, _ = physics.power_coefficients("s", 0.3 + 0.4j, 0.0, 1.0, 1.0, 1.0, 1.0)
    assert R == pytest.approx(0.25)


# --- domain invariants ------------------------------------------------------

def test_absorbing_ambient_is_rejected():
    with pytest.raises(ValueError, match="ambient"):
        physics.check_domain(np.array([1.0 + 0.05j, 1.5], dtype=complex))


def test_gain_medium_is_rejected():
    with pytest.raises(ValueError, match="passive"):
        physics.check_domain(np.array([1.0, 1.5 - 0.05j], dtype=complex))


def test_passive_stack_is_accepted():
    physics.check_domain(np.array([1.0, 1.5 + 0.2j, 1.52], dtype=complex))


def test_unknown_polarisation_is_rejected():
    with pytest.raises(ValueError, match="polarisation"):
        physics.fresnel("circular", 1.0, 1.5, 1.0, 1.0)
