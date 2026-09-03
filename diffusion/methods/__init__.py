"""Ways to walk a noised sample back to the distribution it came from.

A method exposes NAME and step(rng, x, score, alpha_bar, alpha_bar_prev),
which returns the state one step closer to the data.

Neither is handed the target, only a score already evaluated at the current
state. That is the seam the entry is built on: swap an exact score for a
learned one and not a line here changes, which is what makes the exact score
an answer key rather than a shortcut.

They differ in one term. One samples the reverse transition and the other
integrates the flow that shares its marginals, so they agree on where the
samples end up and disagree on every path taken to get there.
"""

from . import ancestral, probability_flow

ALL = {module.NAME: module for module in (ancestral, probability_flow)}
