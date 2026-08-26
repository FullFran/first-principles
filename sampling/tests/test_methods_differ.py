"""Where the samplers part company -- and why that is the point.

Both build a chain for the same target and both are handed the same energy.
Metropolis rejects moves, and rejection is what enforces detailed balance, so
its stationary distribution is the target *exactly* at any step size.
Unadjusted Langevin never rejects anything, so nothing enforces detailed
balance, and the discretisation leaves a bias of order dt that more samples
cannot remove.

A contract demanding both be unbiased would assert something false. A contract
demanding neither be would let a broken sampler through. So the claim lives
here, sharpened into the one form that can be tested exactly: Langevin is not
merely biased, it is biased by a known amount.
"""

import numpy as np
import pytest

import distribution as dist
import solve
from methods import ALL as METHODS


def second_moment(method, scale, steps=250_000, temperature=1.0, seed=0):
    chain = solve.chain("gaussian", method, temperature, steps=steps,
                        scale=scale, seed=seed)
    return chain.mean(2), chain.error(2)


def test_metropolis_is_unbiased_at_any_step_size():
    """Rejection is not wasted work -- it is the correction. Change the step
    size and the efficiency changes; the answer does not."""
    for scale in (0.3, 1.0, 3.0):
        value, error = second_moment("metropolis", scale)
        assert abs(value - 1.0) < 4.0 * error, f"scale {scale}: {value:.5f}"


def test_langevin_is_biased_by_exactly_the_amount_theory_says():
    """On E = x^2/2 at T = 1 the update is an AR(1),

        x' = (1 - dt) x + sqrt(2 dt) xi

    whose stationary variance is 2dt / (1 - (1-dt)^2) = 1 / (1 - dt/2). So the
    wrong answer has a closed form, and reproducing your own error exactly is
    a far sharper test than being approximately right.
    """
    for scale in (0.5, 0.2, 0.1):
        value, error = second_moment("langevin", scale)
        predicted = 1.0 / (1.0 - scale / 2.0)
        assert abs(value - predicted) < 4.0 * error, f"dt {scale}: {value:.5f}"
        assert abs(value - 1.0) > 5.0 * error, "the bias has to be visible"


def test_the_langevin_bias_is_first_order_in_the_step():
    """1/(1 - dt/2) - 1 = (dt/2)/(1 - dt/2), which is dt/2 to leading order,
    so halving the step halves the bias -- in the limit.

    The claim is about the limit and has to be tested as one. An earlier
    version asserted every ratio was within 10% of 2 starting from dt = 0.4,
    where the true ratio is 2.25: the higher-order terms are still there and
    the test was wrong about its own statement. What is true is that the
    ratios approach 2 from above as the step shrinks.
    """
    steps = (0.2, 0.1, 0.05, 0.025)
    biases = [1.0 / (1.0 - dt / 2.0) - 1.0 for dt in steps]
    ratios = [biases[i] / biases[i + 1] for i in range(len(biases) - 1)]

    assert all(r > 2.0 for r in ratios), "first order is approached from above"
    assert ratios == sorted(ratios, reverse=True), "and monotonically"
    assert ratios[-1] < 2.05
    # and it never reaches zero: no number of samples removes it
    assert min(biases) > 0.0


def test_more_samples_fix_metropolis_and_do_not_fix_langevin():
    """The practical face of the same fact. A chain with a bias converges --
    to the wrong number -- and its error bar shrinks around it, so it looks
    *more* certain the longer it runs."""
    distances = {}
    for method, scale in (("metropolis", 1.0), ("langevin", 0.2)):
        run = []
        for steps in (40_000, 400_000):
            value, error = second_moment(method, scale, steps=steps)
            run.append(abs(value - 1.0) / error)
        distances[method] = run

    assert distances["metropolis"][1] < 4.0
    assert distances["langevin"][1] > distances["langevin"][0]
    assert distances["langevin"][1] > 10.0


def test_only_metropolis_rejects_and_that_is_where_the_bias_comes_from():
    for method, scale, rejects in (("metropolis", 1.0, True), ("langevin", 0.2, False)):
        chain = solve.chain("gaussian", method, 1.0, steps=20_000,
                            scale=scale, seed=0)
        assert (chain.acceptance < 0.95) is rejects
    assert solve.chain("gaussian", "langevin", 1.0, steps=5_000,
                       scale=0.2, seed=0).acceptance == 1.0


def test_only_langevin_needs_the_gradient():
    """A structural difference, not a statistical one. Metropolis compares two
    heights; Langevin has to know which way is downhill. That is why a
    diffusion model can exist at all -- what it learns is the gradient of the
    log density, and there is nothing to learn if you only ever need ratios.
    """
    calls = {"energy": 0, "gradient": 0}

    def counted(kind, function):
        def wrapper(x):
            calls[kind] += 1
            return function(x)
        return wrapper

    for method, scale in (("metropolis", 1.0), ("langevin", 0.1)):
        calls["energy"] = calls["gradient"] = 0
        target = dist.Target("counted",
                             counted("energy", dist.GAUSSIAN.energy),
                             counted("gradient", dist.GAUSSIAN.gradient),
                             dist.GAUSSIAN.support)
        solve.chain(target, method, 1.0, steps=500, scale=scale, seed=0)
        if method == "metropolis":
            assert calls["gradient"] == 0 and calls["energy"] > 0
        else:
            assert calls["gradient"] > 0 and calls["energy"] == 0


def test_a_barrier_can_trap_either_of_them_and_neither_will_say_so():
    """The characteristic failure of MCMC, and it is not a bug in either
    method. At T = 0.05 the true population of the right well is 0.99999. With
    these settings Metropolis crosses the barrier and reports it; Langevin's
    steps are too small to climb, so it stays where it started and reports the
    exact opposite -- confidently, with a shrinking error bar, and with
    nothing in the output to suggest anything went wrong.
    """
    truth = dist.exact_probability(dist.DOUBLE_WELL, 0.05)
    assert truth > 0.999

    jumping = solve.chain("double_well", "metropolis", 0.05, steps=200_000,
                          scale=0.6, start=[-1.0], seed=1)
    crawling = solve.chain("double_well", "langevin", 0.05, steps=200_000,
                           scale=0.002, start=[-1.0], seed=2)

    assert np.mean(jumping.samples[:, 0] > 0) > 0.99
    assert np.mean(crawling.samples[:, 0] > 0) == 0.0
    assert np.all(crawling.samples[:, 0] < 0), "it never left the wrong well"
