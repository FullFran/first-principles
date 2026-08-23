"""Transfer Matrix Method for stratified media.

Reflection and transmission of a plane wave crossing a stack of parallel,
homogeneous, isotropic layers. Built from Snell's law and the Fresnel
equations and nothing else -- no solver, no fitting, no special cases.

Conventions
-----------
fields      exp(i(k.r - omega*t))
index       n = n' + i*n'', absorbing when n'' > 0
units       wavelength and thickness share one unit (nanometres by default)
geometry    `n` and `d` describe the same layers, ambient first and
            substrate last; d[0] and d[-1] are ignored because those two
            media are semi-infinite

The stack matrix is a product of two alternating pieces:

    M = I(0,1) . P(1) . I(1,2) . P(2) . ... . I(N-2,N-1)

with I an interface matrix written directly in terms of the Fresnel
coefficients, and P the phase accumulated while crossing a layer.
"""

import numpy as np

__all__ = ["amplitudes", "RT", "fresnel", "layer_cosines"]

# Slack for float noise when checking that an index is real or passive.
PASSIVITY_TOL = 1e-12


def layer_cosines(n, theta0):
    """cos(theta) in every layer, valid for absorbing media and beyond the
    critical angle.

    Snell's law is applied in the form that survives both: the transverse
    wavevector n*sin(theta) is conserved, so

        cos(theta_k) = sqrt(1 - (n_0 sin(theta_0) / n_k)^2)

    evaluated in the complex plane. Writing it as arcsin (as the textbook
    scalar version does) throws away exactly the two cases that matter --
    it returns nan past the critical angle and cannot represent a complex
    index at all.

    The square root is then forced onto the branch that decays forward, so
    an absorbing layer attenuates instead of amplifying.
    """
    n = np.asarray(n, dtype=complex)
    transverse = n[0] * np.sin(theta0)
    cos_theta = np.sqrt(1.0 - (transverse / n) ** 2)

    # Forward-decaying branch: Im(n cos) > 0, or Re(n cos) > 0 when lossless.
    q = n * cos_theta
    wrong_branch = (q.imag < 0) | ((q.imag == 0) & (q.real < 0))
    return np.where(wrong_branch, -cos_theta, cos_theta)


def fresnel(pol, n_i, n_j, cos_i, cos_j):
    """Amplitude reflection and transmission across a single interface."""
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


def _interface_matrix(pol, n_i, n_j, cos_i, cos_j):
    r, t = fresnel(pol, n_i, n_j, cos_i, cos_j)
    return np.array([[1.0, r], [r, 1.0]], dtype=complex) / t


def _propagation_matrix(n_k, cos_k, thickness, wavelength):
    delta = 2 * np.pi / wavelength * n_k * cos_k * thickness
    return np.array([[np.exp(-1j * delta), 0.0], [0.0, np.exp(1j * delta)]])


def _check_domain(n):
    """Refuse the two cases where this formulation returns nonsense quietly.

    Both were found by probing rather than by reasoning, which is the point of
    having them here: unguarded, an absorbing ambient returned R = 5.83 with
    T = -4.82, and a gain medium returned T = 1.27 with A = -0.29. Neither
    raised, neither warned.
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


def amplitudes(pol, n, d, wavelength, theta0=0.0):
    """Amplitude coefficients (r, t) of the whole stack."""
    if len(n) != len(d):
        raise ValueError(f"n and d must have the same length, got {len(n)} and {len(d)}")
    if len(n) < 2:
        raise ValueError("a stack needs at least an ambient and a substrate")
    if pol not in ("s", "p"):
        raise ValueError(f"polarisation must be 's' or 'p', got {pol!r}")

    n = np.asarray(n, dtype=complex)
    _check_domain(n)
    cos_theta = layer_cosines(n, theta0)

    matrix = _interface_matrix(pol, n[0], n[1], cos_theta[0], cos_theta[1])
    for k in range(1, len(n) - 1):
        matrix = (
            matrix
            @ _propagation_matrix(n[k], cos_theta[k], d[k], wavelength)
            @ _interface_matrix(pol, n[k], n[k + 1], cos_theta[k], cos_theta[k + 1])
        )

    r = matrix[1, 0] / matrix[0, 0]
    t = 1.0 / matrix[0, 0]
    return r, t


def RT(pol, n, d, wavelength, theta0=0.0):
    """Power reflectance and transmittance of the stack.

    T is not |t|^2. It carries the ratio of the normal energy flux between
    substrate and ambient, and that projection differs between the two
    polarisations -- which is why the p case conjugates the cosine.
    """
    r, t = amplitudes(pol, n, d, wavelength, theta0)

    n = np.asarray(n, dtype=complex)
    cos_theta = layer_cosines(n, theta0)
    if pol == "s":
        flux_ratio = (n[-1] * cos_theta[-1]).real / (n[0] * cos_theta[0]).real
    else:
        flux_ratio = (n[-1] * np.conj(cos_theta[-1])).real / (
            n[0] * np.conj(cos_theta[0])
        ).real

    R = float(abs(r) ** 2)
    T = float(abs(t) ** 2 * flux_ratio)
    return R, T
