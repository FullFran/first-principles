"""The domain: what light does at a boundary.

Every function here is a statement about nature. None of them knows how a
stack will be solved -- there is no matrix, no recursion, no linear algebra in
this file at all. Swap the algorithm and nothing below changes.

The dependency rule for this entry is one line:

    methods/ imports physics.        physics imports nobody.

Conventions
-----------
fields      exp(i(k.r - omega*t))
index       n = n' + i*n'', absorbing when n'' > 0
units       wavelength and thickness share one unit (nanometres by default)
"""

import numpy as np

__all__ = [
    "check_domain",
    "layer_cosines",
    "fresnel",
    "accumulated_phase",
    "normal_flux",
    "power_coefficients",
    "PASSIVITY_TOL",
]

# Slack for float noise when checking that an index is real or passive.
PASSIVITY_TOL = 1e-12


def check_domain(n):
    """Refuse the two cases where this physics returns nonsense quietly.

    Both were found by probing rather than by reasoning, which is exactly why
    they are written down: unguarded, an absorbing ambient returned R = 5.83
    with T = -4.82, and a gain medium returned T = 1.27 with A = -0.29.
    Neither raised, neither warned.
    """
    if n[0].imag > PASSIVITY_TOL:
        raise ValueError(
            "the ambient medium must be transparent: incident power is "
            f"undefined when the incoming wave already decays (got n[0] = {n[0]})"
        )
    if np.any(n.imag < -PASSIVITY_TOL):
        raise ValueError(
            "all media must be passive, Im(n) >= 0; the forward-decaying "
            "branch rule in layer_cosines() does not hold for gain"
        )


def layer_cosines(n, theta0):
    """cos(theta) in every layer, valid for absorbing media and beyond the
    critical angle.

    Snell's law in the form that survives both. The transverse wavevector
    n*sin(theta) is conserved, so

        cos(theta_k) = sqrt(1 - (n_0 sin(theta_0) / n_k)^2)

    evaluated in the complex plane. The arcsin form found in every textbook
    throws away exactly the two cases that matter: it returns nan past the
    critical angle and cannot represent a complex index at all.

    The root is then forced onto the branch that decays forward, so an
    absorbing layer attenuates instead of amplifying.
    """
    n = np.asarray(n, dtype=complex)
    transverse = n[0] * np.sin(theta0)
    cos_theta = np.sqrt(1.0 - (transverse / n) ** 2)

    q = n * cos_theta
    wrong_branch = (q.imag < 0) | ((q.imag == 0) & (q.real < 0))
    return np.where(wrong_branch, -cos_theta, cos_theta)


def fresnel(pol, n_i, n_j, cos_i, cos_j):
    """Amplitude reflection and transmission across a single interface.

    Continuity of the tangential fields, nothing more.
    """
    if pol == "s":
        denominator = n_i * cos_i + n_j * cos_j
        r = (n_i * cos_i - n_j * cos_j) / denominator
    elif pol == "p":
        denominator = n_j * cos_i + n_i * cos_j
        r = (n_j * cos_i - n_i * cos_j) / denominator
    else:
        raise ValueError(f"polarisation must be 's' or 'p', got {pol!r}")
    t = 2 * n_i * cos_i / denominator
    return r, t


def accumulated_phase(n_k, cos_k, thickness, wavelength):
    """Phase picked up crossing a layer once. Complex when the layer absorbs."""
    return 2 * np.pi / wavelength * n_k * cos_k * thickness


def normal_flux(pol, n, cos_theta):
    """Time-averaged power through unit interface area, up to a common factor.

    This is the quantity that makes T different from |t|^2, and the reason the
    two polarisations do not share a formula: they project onto the interface
    normal differently.
    """
    if pol == "s":
        return (n * cos_theta).real
    if pol == "p":
        return (n * np.conj(cos_theta)).real
    raise ValueError(f"polarisation must be 's' or 'p', got {pol!r}")


def power_coefficients(pol, r, t, n_in, cos_in, n_out, cos_out):
    """Reflectance and transmittance from the amplitude coefficients."""
    R = abs(r) ** 2
    T = abs(t) ** 2 * normal_flux(pol, n_out, cos_out) / normal_flux(pol, n_in, cos_in)
    return float(R), float(T)
