"""Solve the stack by recursion from the substrate up (Rouard's method).

Start with the last interface and fold one layer in at a time:

    R_k = (rho + R_next . e^{2i.delta}) / (1 + rho . R_next . e^{2i.delta})
    T_k = tau . T_next . e^{i.delta}   / (1 + rho . R_next . e^{2i.delta})

which is the Airy summation applied repeatedly -- the physics is identical to
the matrix product, only the bookkeeping differs.

Numerical character: for a passive layer Im(delta) >= 0, so every factor
e^{i.delta} has modulus <= 1. The recursion can only ever shrink, which is why
it underflows to zero gracefully where `transfer-matrix` overflows to NaN.
"""

import numpy as np

from physics import accumulated_phase, fresnel

NAME = "recursion"


def amplitudes(pol, n, d, wavelength, cos_theta):
    last = len(n) - 1
    r, t = fresnel(pol, n[last - 1], n[last], cos_theta[last - 1], cos_theta[last])

    for k in range(last - 2, -1, -1):
        layer = k + 1
        delta = accumulated_phase(n[layer], cos_theta[layer], d[layer], wavelength)
        one_way = np.exp(1j * delta)
        round_trip = one_way**2

        rho, tau = fresnel(pol, n[k], n[k + 1], cos_theta[k], cos_theta[k + 1])
        denominator = 1.0 + rho * r * round_trip
        r = (rho + r * round_trip) / denominator
        t = tau * t * one_way / denominator

    return r, t
