"""Property tests for the transfer matrix implementation.

Every test here encodes something the physics guarantees, not something
the code happens to do. Three of them are direct regressions against
defects found in the 2024 original (see ../README.md).
"""

import numpy as np
import pytest

from core import RT, amplitudes

# Wavelength and thicknesses are in nanometres.
GREEN = 550.0
ANGLES = [0.0, 15.0, 30.0, 45.0, 60.0, 75.0]
POLARISATIONS = ["s", "p"]


def fresnel_reference(pol, n1, n2, theta1):
    """Closed-form single-interface coefficients, straight from the textbook."""
    c1 = np.cos(theta1)
    c2 = np.cos(np.arcsin(n1 * np.sin(theta1) / n2))
    if pol == "s":
        r = (n1 * c1 - n2 * c2) / (n1 * c1 + n2 * c2)
    else:
        r = (n2 * c1 - n1 * c2) / (n2 * c1 + n1 * c2)
    return r


# --- the substrate must actually exist -------------------------------------
# Regression: the original hardcoded n[0] as the exit medium, so an
# air/glass interface reported R = 0 instead of 0.04.

@pytest.mark.parametrize("pol", POLARISATIONS)
@pytest.mark.parametrize("angle", ANGLES)
def test_single_interface_matches_fresnel(pol, angle):
    theta = np.deg2rad(angle)
    r, _ = amplitudes(pol, [1.0, 1.5], [0, 0], GREEN, theta)
    assert r == pytest.approx(fresnel_reference(pol, 1.0, 1.5, theta), abs=1e-12)


def test_air_glass_reflects_four_percent_at_normal_incidence():
    R, T = RT("s", [1.0, 1.5], [0, 0], GREEN)
    assert R == pytest.approx(0.04, abs=1e-12)
    assert T == pytest.approx(0.96, abs=1e-12)


# --- energy bookkeeping -----------------------------------------------------
# Necessary but NOT sufficient: the original passed this while ignoring
# the substrate entirely.

@pytest.mark.parametrize("pol", POLARISATIONS)
@pytest.mark.parametrize("angle", ANGLES)
def test_lossless_stack_conserves_energy(pol, angle):
    n = [1.0] + [2.3, 1.45] * 4 + [1.52]
    d = [0] + [60, 95] * 4 + [0]
    R, T = RT(pol, n, d, GREEN, np.deg2rad(angle))
    assert R + T == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("angle", ANGLES)
def test_absorbing_layer_absorbs_a_positive_amount(angle):
    """Regression: the original reported A = -0.25 for a lossy film."""
    n = [1.0, 1.5 + 0.1j, 1.0]
    d = [0, 100, 0]
    for pol in POLARISATIONS:
        R, T = RT(pol, n, d, GREEN, np.deg2rad(angle))
        absorptance = 1.0 - R - T
        assert 0.0 < absorptance < 1.0


# --- angles the naive arcsin cannot represent -------------------------------

@pytest.mark.parametrize("pol", POLARISATIONS)
@pytest.mark.parametrize("angle", [45.0, 60.0, 80.0])
def test_total_internal_reflection_is_total(pol, angle):
    """Regression: the original returned nan past the critical angle."""
    R, T = RT(pol, [1.5, 1.0], [0, 0], GREEN, np.deg2rad(angle))
    assert np.isfinite(R) and np.isfinite(T)
    assert R == pytest.approx(1.0, abs=1e-12)
    assert T == pytest.approx(0.0, abs=1e-12)


# --- signatures only a correct stack produces -------------------------------

def test_brewster_angle_extinguishes_p_reflection():
    n1, n2 = 1.0, 1.5
    brewster = np.arctan(n2 / n1)
    R_p, _ = RT("p", [n1, n2], [0, 0], GREEN, brewster)
    R_s, _ = RT("s", [n1, n2], [0, 0], GREEN, brewster)
    assert R_p == pytest.approx(0.0, abs=1e-12)
    assert R_s > 0.1


def test_half_wave_layer_is_absentee():
    """A layer of optical thickness lambda/2 is invisible at that wavelength."""
    n_film = 2.2
    half_wave = GREEN / (2 * n_film)
    with_film = RT("s", [1.0, n_film, 1.52], [0, half_wave, 0], GREEN)
    bare = RT("s", [1.0, 1.52], [0, 0], GREEN)
    assert with_film[0] == pytest.approx(bare[0], abs=1e-12)


def test_index_matched_layer_is_invisible():
    matched = RT("s", [1.0, 1.52, 1.52], [0, 123.0, 0], GREEN, np.deg2rad(30))
    bare = RT("s", [1.0, 1.52], [0, 0], GREEN, np.deg2rad(30))
    assert matched[0] == pytest.approx(bare[0], abs=1e-12)


@pytest.mark.parametrize("pol", POLARISATIONS)
def test_quarter_wave_stack_matches_analytic_admittance(pol):
    """R for (HL)^N follows from the quarter-wave admittance transform."""
    n_air, n_high, n_low, n_sub, periods = 1.0, 2.3, 1.45, 1.52, 6
    n = [n_air] + [n_high, n_low] * periods + [n_sub]
    d = [0] + [GREEN / (4 * n_high), GREEN / (4 * n_low)] * periods + [0]

    admittance = (n_high / n_low) ** (2 * periods) * n_sub
    expected = ((n_air - admittance) / (n_air + admittance)) ** 2

    R, _ = RT(pol, n, d, GREEN)
    assert R == pytest.approx(expected, abs=1e-9)


def test_reversing_a_symmetric_stack_preserves_reflectance():
    """With the same medium on both sides, R does not care about layer order."""
    n = [1.0] + [2.3, 1.45, 1.8] * 3 + [1.0]
    d = [0] + [60, 95, 120] * 3 + [0]
    forward, _ = RT("p", n, d, GREEN, np.deg2rad(35))
    backward, _ = RT("p", n[::-1], d[::-1], GREEN, np.deg2rad(35))
    assert forward == pytest.approx(backward, abs=1e-12)


def test_layer_count_mismatch_is_rejected():
    with pytest.raises(ValueError):
        RT("s", [1.0, 1.5, 1.0], [0, 100], GREEN)


def test_unknown_polarisation_is_rejected():
    with pytest.raises(ValueError):
        RT("circular", [1.0, 1.5], [0, 0], GREEN)
