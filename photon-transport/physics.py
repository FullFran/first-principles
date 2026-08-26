"""The domain: what a photon crossing matter *is*.

An emission distribution, a law for how far a photon gets before it interacts,
the geometry of a slab, and the closed form both of those imply. No sampling
loop, no estimator, no stopping rule -- those are choices, and they live in
`methods/` and `solve.py`.

    methods/ imports physics.        physics imports nobody.

Conventions
-----------
mu          linear attenuation coefficient, in inverse length
thickness   slab thickness along z, same length unit as 1/mu
half_angle  half-opening of the emission cone, in radians; 0 is collimated
cos_theta   the direction cosine against the slab normal, never an angle
"""

import numpy as np

__all__ = [
    "sample_direction", "sample_free_path", "slab_path",
    "transmittance", "cone_transmittance", "mean_free_path",
    "check_medium", "check_cone",
]


# --- invariants -------------------------------------------------------------

def check_medium(mu, thickness):
    """A passive slab. Negative attenuation would amplify, which is a laser."""
    if mu < 0:
        raise ValueError(f"attenuation must be non-negative, got mu = {mu}")
    if thickness < 0:
        raise ValueError(f"thickness must be non-negative, got {thickness}")


def check_cone(half_angle):
    """At pi/2 a photon travels parallel to the slab and never leaves it."""
    if not 0.0 <= half_angle < np.pi / 2:
        raise ValueError(
            f"half_angle must be in [0, pi/2), got {half_angle}; at pi/2 the "
            "path through the slab is infinite")


# --- emission ---------------------------------------------------------------

def sample_direction(rng, count, half_angle):
    """Directions drawn uniformly over the solid angle of a cone.

    The trap here is sampling theta uniformly, which crowds photons towards the
    axis: a cone's solid angle element is dOmega = sin(theta) dtheta dphi, so
    the density in theta carries that sin(theta) and the density in cos(theta)
    is flat. Sample the cosine directly and the weighting is automatic.

        p(theta) d(theta) = sin(theta) d(theta)  <=>  p(cos) d(cos) = d(cos)
    """
    check_cone(half_angle)
    lowest = np.cos(half_angle)
    cos_theta = lowest + (1.0 - lowest) * rng.random(count)
    azimuth = 2.0 * np.pi * rng.random(count)
    return cos_theta, azimuth


# --- how far a photon gets --------------------------------------------------

def sample_free_path(rng, count, mu):
    """Distance to the next interaction, drawn from mu*exp(-mu*s).

    Inverse transform: the survival probability of a photon over a distance s
    is exp(-mu*s), which is uniform on (0, 1], so s = -ln(U)/mu.

    `rng.random()` returns [0, 1), where 0 would give an infinite path. Drawing
    1 - U instead puts the sample on (0, 1] and the singularity is unreachable
    rather than merely improbable.
    """
    if mu < 0:
        raise ValueError(f"attenuation must be non-negative, got mu = {mu}")
    if mu == 0:
        return np.full(count, np.inf)
    return -np.log1p(-rng.random(count)) / mu


def mean_free_path(mu):
    """The one length scale in the problem. Everything else is a ratio to it."""
    return np.inf if mu == 0 else 1.0 / mu


# --- geometry ---------------------------------------------------------------

def slab_path(cos_theta, thickness):
    """Distance travelled inside a slab of the given thickness.

    A tilted photon crosses more material than a normal one by exactly
    1/cos(theta), which is the whole of the angular dependence. The 2024
    version computed this as the 3D distance between the entry and exit points,
    which is the same number the long way round.
    """
    cos_theta = np.asarray(cos_theta, dtype=float)
    if np.any(cos_theta <= 0.0):
        raise ValueError("cos_theta must be positive; a photon at 90 degrees "
                         "never crosses the slab")
    return thickness / cos_theta


# --- the closed form --------------------------------------------------------

def transmittance(mu, thickness, cos_theta=1.0):
    """Beer-Lambert: the fraction of photons that cross without interacting.

        T = exp(-mu * thickness / cos(theta))

    This is not an approximation and not a fit. It is the survival probability
    of the exponential in `sample_free_path` evaluated at the slab path, and it
    is what every estimator in `methods/` has to reproduce.
    """
    check_medium(mu, thickness)
    return np.exp(-mu * slab_path(cos_theta, thickness))


def cone_transmittance(mu, thickness, half_angle, nodes=200001):
    """Beer-Lambert averaged over a cone, by quadrature.

        T = 1/(1 - cos(a)) * integral of exp(-mu*L/c) dc, c from cos(a) to 1

    The integral is an exponential integral and has no elementary form, so it
    is evaluated numerically -- but on a fixed grid to a precision far beyond
    what any Monte Carlo run reaches, which is what makes it a reference rather
    than a second opinion.
    """
    check_medium(mu, thickness)
    check_cone(half_angle)
    if half_angle == 0.0:
        return float(transmittance(mu, thickness, 1.0))
    lowest = np.cos(half_angle)
    grid = np.linspace(lowest, 1.0, nodes)
    return float(np.trapezoid(np.exp(-mu * thickness / grid), grid) / (1.0 - lowest))
