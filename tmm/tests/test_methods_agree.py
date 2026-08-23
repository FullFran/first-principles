"""The methods must not disagree, and where they do it must be numerics only.

Two independent algorithms landing on the same number to 1e-14 is stronger
evidence than either one passing a suite alone. Where they part company is
documented rather than hidden: see the numerical limits at the bottom.
"""

import itertools

import numpy as np
import pytest

import solve
from methods import ALL as METHODS

GREEN = 550.0

STACKS = [
    ("single interface", [1.0, 1.5], [0, 0]),
    ("bragg on glass", [1.0] + [2.3, 1.45] * 6 + [1.52], [0] + [60, 95] * 6 + [0]),
    ("absorbing film", [1.0, 1.5 + 0.1j, 1.52], [0, 80, 0]),
    ("thin metal", [1.0, 0.15 + 3.5j, 1.52], [0, 25, 0]),
    ("past critical angle", [1.5, 1.0], [0, 0]),
]


@pytest.mark.parametrize("label,n,d", STACKS, ids=[s[0] for s in STACKS])
@pytest.mark.parametrize("pol", ["s", "p"])
@pytest.mark.parametrize("angle", [0.0, 30.0, 55.0, 75.0])
def test_every_method_agrees_with_every_other(label, n, d, pol, angle):
    theta = np.deg2rad(angle)
    results = {
        name: solve.amplitudes(pol, n, d, GREEN, theta, method=name)
        for name in sorted(METHODS)
    }
    for (a, ra), (b, rb) in itertools.combinations(results.items(), 2):
        assert ra[0] == pytest.approx(rb[0], abs=1e-13), f"r disagrees: {a} vs {b}"
        assert ra[1] == pytest.approx(rb[1], abs=1e-13), f"t disagrees: {a} vs {b}"


# --- where they stop agreeing -----------------------------------------------

@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_transfer_matrix_dies_on_an_absurdly_thick_metal_layer():
    """Characterisation, not a wish: M00 overflows and takes r with it.

    Nothing physical lives here -- transmittance is already 1e-278 at 8 um --
    but the boundary is real and belongs in the record.
    """
    R, _ = solve.RT("s", [1.0, 0.15 + 3.5j, 1.52], [0, 20000, 0], GREEN,
                    method="transfer-matrix")
    assert np.isnan(R)


def test_recursion_survives_where_the_transfer_matrix_does_not():
    """Every factor in the recursion has modulus <= 1, so it cannot blow up."""
    R, T = solve.RT("s", [1.0, 0.15 + 3.5j, 1.52], [0, 20000, 0], GREEN,
                    method="recursion")
    assert np.isfinite(R) and R == pytest.approx(0.955793, abs=1e-5)
    assert T == 0.0
