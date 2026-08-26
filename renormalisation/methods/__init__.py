"""Two ways to count spanning blocks.

A method exposes NAME and polynomial(size, rule, ...), returning the number of
spanning configurations at each occupied count -- the coefficients of R(p).
What it decides is *how* that count is obtained; what a spanning block is
belongs to the domain.

One is exact and stops working at a block of five a side. The other has error
bars and does not stop.
"""

from . import enumeration, sampling

ALL = {module.NAME: module for module in (enumeration, sampling)}
