"""Solve the stack by multiplying 2x2 transfer matrices.

Each interface and each layer becomes a matrix acting on the pair
(forward, backward) amplitude, and the stack is their product:

    M = I(0,1) . P(1) . I(1,2) . P(2) ... I(N-2,N-1)

    I = (1/t) [[1, r], [r, 1]]        P = [[exp(-i.delta), 0], [0, exp(i.delta)]]

Writing the interface matrix in terms of the Fresnel coefficients removes the
matrix inversion the textbook D-P-D^-1 form needs twice per layer.

Numerical character: P grows like exp(|Im delta|) in an absorbing layer, so
M[0,0] overflows for absurdly thick metal (~20 um) and r goes NaN. The ratio
r = M10/M00 cancels the growth up to that point, which is why the failure is
sudden rather than gradual. `recursion` has no such ceiling.
"""

import numpy as np

from physics import accumulated_phase, fresnel

NAME = "transfer-matrix"


def _interface(pol, n_i, n_j, cos_i, cos_j):
    r, t = fresnel(pol, n_i, n_j, cos_i, cos_j)
    return np.array([[1.0, r], [r, 1.0]], dtype=complex) / t


def _propagation(n_k, cos_k, thickness, wavelength):
    delta = accumulated_phase(n_k, cos_k, thickness, wavelength)
    return np.array([[np.exp(-1j * delta), 0.0], [0.0, np.exp(1j * delta)]])


def amplitudes(pol, n, d, wavelength, cos_theta):
    matrix = _interface(pol, n[0], n[1], cos_theta[0], cos_theta[1])
    for k in range(1, len(n) - 1):
        matrix = (
            matrix
            @ _propagation(n[k], cos_theta[k], d[k], wavelength)
            @ _interface(pol, n[k], n[k + 1], cos_theta[k], cos_theta[k + 1])
        )
    return matrix[1, 0] / matrix[0, 0], 1.0 / matrix[0, 0]
