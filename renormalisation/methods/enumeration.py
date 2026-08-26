"""Count every configuration. There are 2^(b*b) of them.

Exact, with no statistical error at all, which is what makes it the reference
the sampler is checked against.

And it is 2^(b*b). A block of 4 is 65536 configurations and takes a moment; a
block of 5 is 33 million and does not finish; a block of 6 is 6.9e10 and never
will. The wall is not gradual -- each extra row of the block squares the work
twice over.
"""

from flow import block_polynomial

NAME = "enumeration"
FEASIBLE_UP_TO = 4


def polynomial(size, rule="either", **_):
    if size > FEASIBLE_UP_TO:
        raise ValueError(
            f"a {size}x{size} block is 2^{size*size} configurations, which is "
            f"{2**(size*size):.3g}. Enumeration stops at {FEASIBLE_UP_TO}; use "
            "the sampling method.")
    return block_polynomial(size, rule).astype(float)
