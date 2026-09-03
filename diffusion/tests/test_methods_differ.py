"""Where the two samplers stop agreeing, and what that costs each of them.

The contract suite says they land in the same place. This one says they get
there differently, because a contract both methods pass is only interesting
if there is something left over that separates them.

The separation is one term. Ancestral samples the reverse transition and
carries noise; probability-flow integrates the flow with the same marginals
and carries none. Everything below follows from that single difference.
"""

import numpy as np
import pytest

import process
import solve


def test_the_flow_is_a_function_of_its_starting_noise():
    """Same seed, same sample, exactly -- not to a tolerance. That is what
    'deterministic' has to mean, and it is what makes the map invertible and
    the trajectory differentiable."""
    a = solve.sample(target="arc", method="probability-flow", steps=60, draws=200, seed=4)
    b = solve.sample(target="arc", method="probability-flow", steps=60, draws=200, seed=4)
    assert np.array_equal(a.draws, b.draws)


def test_ancestral_keeps_drawing_after_the_start():
    """The same initial noise does not fix an ancestral sample, because the
    method asks the generator for more at every step. Compared at equal seed
    against the deterministic method, whose answer is already pinned."""
    rng_a = np.random.default_rng(0)
    rng_b = np.random.default_rng(0)
    x0 = np.random.default_rng(99).standard_normal((200, 2))
    mixture = process.BIMODAL

    def walk(rng, module):
        x = x0.copy()
        abar = solve.cosine_schedule(60)
        for i in range(len(abar) - 1, 0, -1):
            x = module.step(rng, x, process.score(mixture, x, abar[i]),
                            abar[i], abar[i - 1])
        return x

    from methods import ancestral, probability_flow
    assert not np.allclose(walk(rng_a, ancestral), walk(rng_b, probability_flow))
    # and the deterministic one does not care which generator it was handed
    assert np.array_equal(walk(rng_a, probability_flow), walk(rng_b, probability_flow))


@pytest.mark.parametrize("target", ["shifted", "arc"])
def test_neither_survives_three_steps(target):
    """The floor is not a formality. At three steps both are an order of
    magnitude outside it, so a run landing inside is evidence and not the
    threshold being generous."""
    for method in ["ancestral", "probability-flow"]:
        run = solve.sample(target=target, method=method, steps=3, draws=400, seed=1)
        assert run.discrepancy > 10 * run.noise_floor


@pytest.mark.parametrize("target", ["shifted", "arc"])
def test_more_steps_is_monotonically_better_for_the_flow(target):
    """It integrates its error, so the error is the step size and nothing
    else. Averaged over seeds because a single run of either method is a
    noisy number -- which is how the first version of this suite managed to
    pass at 100 steps, fail at 200 and pass again at 400."""
    def gap(steps):
        return np.mean([
            max(solve.sample(target=target, method="probability-flow",
                             steps=steps, draws=300, seed=s).discrepancy, 0.0)
            for s in range(4)
        ])

    assert gap(5) > gap(20) > gap(100)


def test_the_flow_is_ahead_while_there_is_still_something_to_measure():
    """The few-step advantage, checked where the comparison means anything.

    Ancestral adds noise at every step, and at five steps there is no time
    left to remove it. Asserted only at a step count where both methods are
    still *above* the noise floor: past about twelve they are both inside it,
    and an earlier version of this test ranked them at fifty steps and
    reported a 5.6x gap between two numbers indistinguishable from zero.
    """
    def gap(method, steps):
        return np.mean([
            max(solve.sample(target="arc", method=method, steps=steps,
                             draws=300, seed=s).discrepancy, 0.0)
            for s in range(6)
        ])

    floor = solve.sample(target="arc", steps=50, draws=300, seed=0).noise_floor
    slow, fast = gap("ancestral", 5), gap("probability-flow", 5)
    assert slow > floor and fast > floor, "the comparison must be above the floor"
    assert fast < slow
