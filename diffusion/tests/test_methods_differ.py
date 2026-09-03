"""Where the two samplers stop agreeing, and what that costs each of them.

The contract suite says they land in the same place. This one says they get
there differently, because a contract both methods pass is only interesting
if there is something left over that separates them.

The separation is one term. Ancestral samples the reverse transition and
carries noise; probability-flow integrates the flow with the same marginals
and carries none. Everything below follows from that single difference.
"""

import math

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


def _target_cdf(v):
    """The marginal CDF of BIMODAL along x. No scipy, and none needed."""
    return sum(
        w * 0.5 * (1.0 + math.erf((v - mu[0]) / (math.sqrt(cov[0, 0]) * math.sqrt(2.0))))
        for w, mu, cov in zip(process.BIMODAL.weights, process.BIMODAL.means,
                              process.BIMODAL.covariances)
    )


def _normal_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _walk_from(module, x0, steps, seed=0):
    """Run the reverse process from a chosen start, which `solve.sample` does
    not offer: it draws its own noise, and these two claims are about what a
    *given* start does. The loop is the one in `solve.sample`, nothing more."""
    rng = np.random.default_rng(seed)
    abar = solve.cosine_schedule(steps)
    x = np.array([[x0, 0.0]])
    for i in range(len(abar) - 1, 0, -1):
        x = module.step(rng, x, process.score(process.BIMODAL, x, abar[i]),
                        abar[i], abar[i - 1])
    return x[0, 0]


def _flow_endpoint(x0, steps):
    from methods import probability_flow
    return _walk_from(probability_flow, x0, steps)


def test_the_flow_is_the_quantile_transport_map():
    """In one dimension the probability-flow ODE is not merely deterministic:
    it is *the* monotone map carrying the noise onto the target, so a start at
    the u-th quantile of the noise lands at the u-th quantile of the target.

    Checked as a rank statement rather than by inverting anything: run the map
    and ask what fraction of the target lies below where it landed. That is
    the cleanest form of the claim and it needs only a CDF.

    It explains three things the figures show and no other property does. The
    paths cannot cross, because a monotone map has no room to. The endpoints
    are not at the modes, because quantiles go to quantiles. And the mode a
    run reaches is decided by its first draw and nothing after it.
    """
    for x0 in [-2.0, -0.8, -0.2, 0.2, 0.8, 2.0]:
        landed = _target_cdf(_flow_endpoint(x0, 800))
        assert abs(landed - _normal_cdf(x0)) < 5e-3, x0


def test_the_transport_map_is_exact_only_in_the_limit():
    """First order in the step count: halve the step and halve the error.

    Worth asserting rather than assuming, because it is the whole cost of the
    method. The measured ratios over five doublings are 2.0, 2.0, 2.0, 1.9,
    1.9, so the bound below is loose on purpose -- it is testing the order,
    not the constant.
    """
    probe = [-2.0, -0.8, 0.8, 2.0]
    exact = [_normal_cdf(x) for x in probe]

    def worst(steps):
        return max(abs(_target_cdf(_flow_endpoint(x, steps)) - u)
                   for x, u in zip(probe, exact))

    coarse, fine = worst(100), worst(400)
    assert coarse > fine, "more steps must not be worse"
    assert 2.5 < coarse / fine < 6.0, f"expected ~4x for 4x the steps, got {coarse / fine:.1f}"


def test_ancestral_forgets_where_it_started():
    """The mirror image of the map. Across a range of starts five units wide
    the endpoint moves by hundredths: the sample comes from the noise injected
    along the way, not from the point the walk began at."""
    from methods import ancestral as anc
    ends = [_walk_from(anc, x0, 400, seed=7) for x0 in np.linspace(-2.5, 2.5, 9)]
    assert max(ends) - min(ends) < 0.2, f"spread {max(ends) - min(ends):.3f}"
