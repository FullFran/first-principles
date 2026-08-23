"""Deterministic glyphs to store in the network.

The class version used photographs (a cat, Batman, a self-portrait). Those
cannot live in a public repo, and photographs are also heavily biased towards
one colour, which correlates the patterns and quietly wrecks Hebbian recall.
These four are generated instead: same role, roughly balanced, reproducible
anywhere with no assets.
"""

import numpy as np

SIDE = 24
SHAPE = (SIDE, SIDE)


def _grid():
    axis = np.linspace(-1.0, 1.0, SIDE)
    return np.meshgrid(axis, axis)


def cross():
    x, y = _grid()
    return (np.abs(x) < 0.30) | (np.abs(y) < 0.30)


def ring():
    x, y = _grid()
    r = np.hypot(x, y)
    return (r > 0.45) & (r < 0.85)


def diagonals():
    x, y = _grid()
    return (np.abs(x - y) < 0.32) | (np.abs(x + y) < 0.32)


def bars():
    _, y = _grid()
    return (np.floor((y + 1) * 2.5) % 2) == 0


def checker():
    x, y = _grid()
    return ((np.floor((x + 1) * 2) + np.floor((y + 1) * 2)) % 2) == 0


def as_pattern(mask):
    return np.where(mask, 1, -1).astype(np.int8).ravel()


NAMES = ("cross", "ring", "diagonals", "bars")
LIBRARY = {"cross": cross, "ring": ring, "diagonals": diagonals,
           "bars": bars, "checker": checker}


def library(names=NAMES):
    return np.stack([as_pattern(LIBRARY[n]()) for n in names])


def render(state):
    grid = np.asarray(state).reshape(SHAPE)
    return "\n".join("".join("#" if v > 0 else "." for v in row) for row in grid)
