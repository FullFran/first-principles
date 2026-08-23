"""Entry point: pick a method, get numbers out.

The only file that knows both sides. It validates the request, hands the
domain quantities to a method, and turns the amplitudes the method returns
back into power. Everything it does is orchestration; none of it is physics.
"""

import numpy as np

import physics
from methods import ALL as METHODS

__all__ = ["amplitudes", "RT", "METHODS", "DEFAULT_METHOD"]

DEFAULT_METHOD = "transfer-matrix"


def _prepare(pol, n, d, method):
    if len(n) != len(d):
        raise ValueError(f"n and d must have the same length, got {len(n)} and {len(d)}")
    if len(n) < 2:
        raise ValueError("a stack needs at least an ambient and a substrate")
    if pol not in ("s", "p"):
        raise ValueError(f"polarisation must be 's' or 'p', got {pol!r}")
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}; available: {sorted(METHODS)}")

    n = np.asarray(n, dtype=complex)
    physics.check_domain(n)
    return n, METHODS[method]


def amplitudes(pol, n, d, wavelength, theta0=0.0, method=DEFAULT_METHOD):
    """Amplitude coefficients (r, t) of the whole stack."""
    n, solver = _prepare(pol, n, d, method)
    cos_theta = physics.layer_cosines(n, theta0)
    return solver.amplitudes(pol, n, d, wavelength, cos_theta)


def RT(pol, n, d, wavelength, theta0=0.0, method=DEFAULT_METHOD):
    """Power reflectance and transmittance of the stack."""
    n, solver = _prepare(pol, n, d, method)
    cos_theta = physics.layer_cosines(n, theta0)
    r, t = solver.amplitudes(pol, n, d, wavelength, cos_theta)
    return physics.power_coefficients(
        pol, r, t, n[0], cos_theta[0], n[-1], cos_theta[-1]
    )
