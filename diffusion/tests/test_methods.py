"""The contract: what every reverse sampler owes, whatever it does inside.

The claim under test is the only one that matters -- run the process
backwards from noise and the samples are draws from the target. It is
checkable here and not on real data because the target has a closed form,
and the threshold is measured rather than chosen: two independent sets of
exact draws disagree by some amount, and a sampler is allowed exactly that
much.

This is also the file that localises a bug. Both methods are handed the same
score, so anything they both fail is the domain's and anything only one
fails is that method's. That is how the ancestral drift was caught carrying
the cumulative abar where the per-step alpha belongs, while probability-flow
sat inside the floor.
"""

import numpy as np
import pytest

import process
import solve
from methods import ALL as METHODS

TARGETS = sorted(process.TARGETS)


@pytest.mark.parametrize("method", sorted(METHODS))
@pytest.mark.parametrize("target", TARGETS)
def test_the_samples_are_draws_from_the_target(method, target):
    run = solve.sample(target=target, method=method, steps=200, draws=500, seed=3)
    assert run.within_noise, (
        f"{method} on {target}: MMD^2 {run.discrepancy:.2e} above a floor of "
        f"{run.noise_floor:.2e}"
    )


@pytest.mark.parametrize("method", sorted(METHODS))
@pytest.mark.parametrize("target", TARGETS)
def test_the_first_two_moments_land(method, target):
    """Weaker than the distributional test and worth keeping: it says *where*
    a failure is, which a scalar discrepancy never does."""
    mixture = process.TARGETS[target]
    run = solve.sample(target=target, method=method, steps=200, draws=1500, seed=5)
    truth_mean = mixture.weights @ mixture.means
    spread = np.sqrt(np.diag(sum(
        w * (c + np.outer(m - truth_mean, m - truth_mean))
        for w, m, c in zip(mixture.weights, mixture.means, mixture.covariances)
    )))
    assert np.abs(run.draws.mean(axis=0) - truth_mean).max() < 0.15 * spread.max()
    assert np.abs(run.draws.std(axis=0) - spread).max() < 0.15 * spread.max()


@pytest.mark.parametrize("method", sorted(METHODS))
def test_every_mode_gets_visited(method):
    """A sampler that finds one well of two is not wrong on the mean and is
    wrong about everything else. BIMODAL is symmetric, so the split is 50/50
    and a collapse is unmissable."""
    run = solve.sample(target="bimodal", method=method, steps=200, draws=1200, seed=7)
    right = (run.draws[:, 0] > 0).mean()
    assert 0.42 < right < 0.58, f"{method} put {right:.0%} of its mass on one side"


@pytest.mark.parametrize("method", sorted(METHODS))
@pytest.mark.parametrize("schedule", sorted(solve.SCHEDULES))
def test_the_schedule_is_a_choice_and_not_a_requirement(method, schedule):
    run = solve.sample(target="bimodal", method=method, schedule=schedule,
                       steps=400, draws=400, seed=9)
    assert run.within_noise


@pytest.mark.parametrize("method", sorted(METHODS))
def test_the_shape_that_went_in_comes_back(method):
    run = solve.sample(target="shifted", method=method, steps=20, draws=64, seed=0)
    assert run.draws.shape == (64, process.SHIFTED.dim)
    assert np.isfinite(run.draws).all()


@pytest.mark.parametrize("method", sorted(METHODS))
def test_a_run_is_reproducible(method):
    a = solve.sample(target="arc", method=method, steps=50, draws=100, seed=42)
    b = solve.sample(target="arc", method=method, steps=50, draws=100, seed=42)
    assert np.array_equal(a.draws, b.draws)


@pytest.mark.parametrize("method", sorted(METHODS))
def test_a_score_that_is_handed_in_is_the_one_that_is_used(method):
    """The seam the entry is built on. If a wrong score does not produce
    wrong samples, the sampler is not using it and nothing else here means
    anything."""
    mixture = process.BIMODAL
    honest = solve.sample(target="bimodal", method=method, steps=100, draws=300, seed=1)
    lying = solve.sample(
        target="bimodal", method=method, steps=100, draws=300, seed=1,
        score_fn=lambda x, ab: 0.5 * process.score(mixture, x, ab),
    )
    assert not np.allclose(honest.draws, lying.draws)
    assert lying.discrepancy > honest.discrepancy


@pytest.mark.parametrize("bad", [
    dict(target="nonesuch"), dict(method="nonesuch"), dict(schedule="nonesuch"),
    dict(steps=0), dict(draws=1),
])
def test_nonsense_is_refused_rather_than_run(bad):
    with pytest.raises(ValueError):
        solve.sample(**bad)


def test_the_schedules_run_from_data_to_noise():
    for name, build in solve.SCHEDULES.items():
        abar = build(1000)
        assert abar[0] == pytest.approx(1.0, abs=1e-3), name
        assert abar[-1] < 0.05, name
        assert np.all(np.diff(abar) <= 0), f"{name} is not monotone"


def test_only_one_schedule_finishes_in_a_few_hundred_steps():
    """What the step count is actually for. Cosine is at the floor at any
    length; linear at 200 steps still claims a tenth of the signal survives,
    while the reverse process starts from pure noise regardless. That gap is
    the whole reason the original paper ran a thousand steps."""
    assert solve.cosine_schedule(200)[-1] < 1e-3
    assert solve.linear_schedule(200)[-1] > 0.1
    assert solve.linear_schedule(1000)[-1] < 1e-3
