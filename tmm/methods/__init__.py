"""Numerical strategies for solving a stack.

A method receives the physical quantities the domain already computed and
returns the amplitude coefficients (r, t). It is not allowed to know anything
else -- no Snell, no flux, no power. Adding one here enrols it automatically
in the contract suite, which is what keeps this from being folder theatre.
"""

from . import recursion, transfer_matrix

ALL = {module.NAME: module for module in (transfer_matrix, recursion)}
