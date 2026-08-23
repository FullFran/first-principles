"""Contract tests: every law, run against every numerical method.

This file is the boundary. The folder split is decoration without it -- what
actually forbids a method from smuggling physics of its own is that all of
them have to satisfy the same suite, and that they have to agree with each
other to machine precision.

Add a method to `methods/`, and it inherits this contract for free.
"""

import numpy as np
import pytest

import physics
import solve
from methods import ALL as METHODS

GREEN = 550.0
ANGLES = [0.0, 15.0, 30.0, 45.0, 60.0, 75.0]
POLARISATIONS = ["s", "p"]
METHOD_NAMES = sorted(METHODS)

pytestmark = pytest.mark.parametrize("method", METHOD_NAMES)


def fresnel_reference(pol, n1, n2, theta1):
    c1 = np.cos(theta1)
    c2 = np.cos(np.arcsin(n1 * np.sin(theta1) / n2))
    if pol == "s":
        return (n1 * c1 - n2 * c2) / (n1 * c1 + n2 * c2)
    return (n2 * c1 - n1 * c2) / (n2 * c1 + n1 * c2)


def airy_reference(pol, n0, n1, n2, thickness, theta0, wavelength=GREEN):
    """Single film by Airy summation -- uses the domain, not any method."""
    n = np.array([n0, n1, n2], dtype=complex)
    c = physics.layer_cosines(n, theta0)
    r01, _ = physics.fresnel(pol, n[0], n[1], c[0], c[1])
    r12, _ = physics.fresnel(pol, n[1], n[2], c[1], c[2])
    phase = np.exp(2j * physics.accumulated_phase(n[1], c[1], thickness, wavelength))
    return (r01 + r12 * phase) / (1 + r01 * r12 * phase)


# --- reduction to the single interface --------------------------------------

@pytest.mark.parametrize("pol", POLARISATIONS)
@pytest.mark.parametrize("angle", ANGLES)
def test_single_interface_matches_fresnel(method, pol, angle):
    theta = np.deg2rad(angle)
    r, _ = solve.amplitudes(pol, [1.0, 1.5], [0, 0], GREEN, theta, method=method)
    assert r == pytest.approx(fresnel_reference(pol, 1.0, 1.5, theta), abs=1e-12)


def test_air_glass_reflects_four_percent_at_normal_incidence(method):
    R, T = solve.RT("s", [1.0, 1.5], [0, 0], GREEN, method=method)
    assert R == pytest.approx(0.04, abs=1e-12)
    assert T == pytest.approx(0.96, abs=1e-12)


# --- energy bookkeeping -----------------------------------------------------

@pytest.mark.parametrize("pol", POLARISATIONS)
@pytest.mark.parametrize("angle", ANGLES)
def test_lossless_stack_conserves_energy(method, pol, angle):
    n = [1.0] + [2.3, 1.45] * 4 + [1.52]
    d = [0] + [60, 95] * 4 + [0]
    R, T = solve.RT(pol, n, d, GREEN, np.deg2rad(angle), method=method)
    assert R + T == pytest.approx(1.0, abs=1e-12)


# --- absorption, checked by value and not only by bound ---------------------

@pytest.mark.parametrize("pol", POLARISATIONS)
@pytest.mark.parametrize("n_film", [1.5 + 0.1j, 0.15 + 3.5j, 2.0 + 0.001j])
@pytest.mark.parametrize("angle", [0.0, 30.0, 60.0, 85.0])
def test_absorbing_film_matches_airy_closed_form(method, pol, n_film, angle):
    theta = np.deg2rad(angle)
    r, _ = solve.amplitudes(pol, [1.0, n_film, 1.52], [0, 80, 0], GREEN, theta, method=method)
    assert r == pytest.approx(airy_reference(pol, 1.0, n_film, 1.52, 80, theta), abs=1e-13)


@pytest.mark.parametrize("angle", ANGLES)
def test_absorbing_layer_absorbs_a_positive_amount(method, angle):
    for pol in POLARISATIONS:
        R, T = solve.RT(pol, [1.0, 1.5 + 0.1j, 1.0], [0, 100, 0], GREEN,
                        np.deg2rad(angle), method=method)
        assert 0.0 < 1.0 - R - T < 1.0


def test_absorbing_substrate_is_allowed(method):
    R, T = solve.RT("s", [1.0, 1.5, 0.15 + 3.5j], [0, 100, 0], GREEN,
                    np.deg2rad(20), method=method)
    assert 0.0 <= R <= 1.0 and 0.0 <= T <= 1.0 and R + T <= 1.0


# --- signatures only a correct stack produces -------------------------------

@pytest.mark.parametrize("pol", POLARISATIONS)
@pytest.mark.parametrize("angle", [45.0, 60.0, 80.0])
def test_total_internal_reflection_is_total(method, pol, angle):
    R, T = solve.RT(pol, [1.5, 1.0], [0, 0], GREEN, np.deg2rad(angle), method=method)
    assert np.isfinite(R) and np.isfinite(T)
    assert R == pytest.approx(1.0, abs=1e-12)
    assert T == pytest.approx(0.0, abs=1e-12)


def test_brewster_angle_extinguishes_p_reflection(method):
    brewster = np.arctan(1.5 / 1.0)
    R_p, _ = solve.RT("p", [1.0, 1.5], [0, 0], GREEN, brewster, method=method)
    R_s, _ = solve.RT("s", [1.0, 1.5], [0, 0], GREEN, brewster, method=method)
    assert R_p == pytest.approx(0.0, abs=1e-12)
    assert R_s > 0.1


def test_half_wave_layer_is_absentee(method):
    n_film = 2.2
    with_film = solve.RT("s", [1.0, n_film, 1.52], [0, GREEN / (2 * n_film), 0],
                         GREEN, method=method)
    bare = solve.RT("s", [1.0, 1.52], [0, 0], GREEN, method=method)
    assert with_film[0] == pytest.approx(bare[0], abs=1e-12)


def test_index_matched_layer_is_invisible(method):
    matched = solve.RT("s", [1.0, 1.52, 1.52], [0, 123.0, 0], GREEN,
                       np.deg2rad(30), method=method)
    bare = solve.RT("s", [1.0, 1.52], [0, 0], GREEN, np.deg2rad(30), method=method)
    assert matched[0] == pytest.approx(bare[0], abs=1e-12)


@pytest.mark.parametrize("pol", POLARISATIONS)
def test_quarter_wave_stack_matches_analytic_admittance(method, pol):
    n_air, n_high, n_low, n_sub, periods = 1.0, 2.3, 1.45, 1.52, 6
    n = [n_air] + [n_high, n_low] * periods + [n_sub]
    d = [0] + [GREEN / (4 * n_high), GREEN / (4 * n_low)] * periods + [0]

    admittance = (n_high / n_low) ** (2 * periods) * n_sub
    expected = ((n_air - admittance) / (n_air + admittance)) ** 2

    R, _ = solve.RT(pol, n, d, GREEN, method=method)
    assert R == pytest.approx(expected, abs=1e-9)


def test_reversing_a_symmetric_stack_preserves_reflectance(method):
    n = [1.0] + [2.3, 1.45, 1.8] * 3 + [1.0]
    d = [0] + [60, 95, 120] * 3 + [0]
    forward, _ = solve.RT("p", n, d, GREEN, np.deg2rad(35), method=method)
    backward, _ = solve.RT("p", n[::-1], d[::-1], GREEN, np.deg2rad(35), method=method)
    assert forward == pytest.approx(backward, abs=1e-12)


# --- the guards reach every method ------------------------------------------

def test_absorbing_ambient_is_rejected(method):
    with pytest.raises(ValueError, match="ambient"):
        solve.RT("s", [1.0 + 0.05j, 1.5, 1.0], [0, 100, 0], GREEN, method=method)


def test_gain_medium_is_rejected(method):
    with pytest.raises(ValueError, match="passive"):
        solve.RT("s", [1.0, 1.5 - 0.05j, 1.0], [0, 200, 0], GREEN, method=method)


def test_layer_count_mismatch_is_rejected(method):
    with pytest.raises(ValueError, match="same length"):
        solve.RT("s", [1.0, 1.5, 1.0], [0, 100], GREEN, method=method)
