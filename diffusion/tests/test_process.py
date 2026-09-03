"""Domain tests: what noise does to a density, checked without sampling anything.

Nothing here imports a method. If these fail the mathematics is wrong. If
these pass and a sampler still misses the target, the sampler is wrong --
and that separation is what found the one real bug in this entry, a reverse
drift carrying the cumulative abar where the per-step alpha belongs.

The score is checked three ways, all independent of the formula under test:
central differences of the log density, an unrelated Tweedie derivation by
Gaussian conditioning, and the eps identity.
"""

import ast
from pathlib import Path

import numpy as np
import pytest

import process

ABARS = [0.999, 0.9, 0.5, 0.1, 0.01]
TARGETS = list(process.TARGETS.values())


def finite_difference_score(mixture, x, alpha_bar, h=1e-5):
    """The score by central differences, knowing nothing about the closed form."""
    out = np.zeros_like(x)
    for i in range(x.shape[-1]):
        step = np.zeros(x.shape[-1])
        step[i] = h
        out[..., i] = (process.log_density(mixture, x + step, alpha_bar)
                       - process.log_density(mixture, x - step, alpha_bar)) / (2 * h)
    return out


def tweedie_by_conditioning(mixture, x, alpha_bar):
    """E[x_0 | x_t] by Gaussian conditioning, component by component.

    Shares no line with `posterior_mean`, which reaches the same quantity
    through the score. Two routes to one number is the only reason to trust
    either.
    """
    _, covariances = process.noised_parameters(mixture, alpha_bar)
    resp, _, _ = process._responsibilities(mixture, x, alpha_bar)
    out = np.zeros_like(x)
    for k in range(mixture.components):
        gain = np.sqrt(alpha_bar) * mixture.covariances[k] @ np.linalg.inv(covariances[k])
        centred = x - np.sqrt(alpha_bar) * mixture.means[k]
        out += resp[:, k, None] * (mixture.means[k] + centred @ gain.T)
    return out


@pytest.fixture
def points():
    return np.random.default_rng(11).normal(size=(60, 2)) * 1.5


@pytest.mark.parametrize("mixture", TARGETS, ids=lambda m: m.name)
@pytest.mark.parametrize("alpha_bar", ABARS)
def test_score_matches_finite_differences(mixture, alpha_bar, points):
    exact = process.score(mixture, points, alpha_bar)
    approx = np.array([finite_difference_score(mixture, p, alpha_bar) for p in points])
    assert np.abs(exact - approx).max() < 1e-6 * max(np.abs(exact).max(), 1.0)


@pytest.mark.parametrize("mixture", TARGETS, ids=lambda m: m.name)
@pytest.mark.parametrize("alpha_bar", ABARS)
def test_tweedie_agrees_with_gaussian_conditioning(mixture, alpha_bar, points):
    assert np.allclose(process.posterior_mean(mixture, points, alpha_bar),
                       tweedie_by_conditioning(mixture, points, alpha_bar),
                       rtol=1e-10, atol=1e-12)


@pytest.mark.parametrize("mixture", TARGETS, ids=lambda m: m.name)
@pytest.mark.parametrize("alpha_bar", [0.9, 0.5, 0.1])
def test_expected_noise_is_the_score_in_disguise(mixture, alpha_bar, points):
    """grad log q_t = -E[eps | x_t] / sqrt(1 - abar): the whole reason a
    network that predicts noise is a score model without being told."""
    eps = process.expected_noise(mixture, points, alpha_bar)
    assert np.allclose(process.score(mixture, points, alpha_bar),
                       -eps / np.sqrt(1.0 - alpha_bar), rtol=1e-12, atol=1e-14)


@pytest.mark.parametrize("mixture", TARGETS, ids=lambda m: m.name)
def test_no_noise_leaves_the_target_untouched(mixture):
    means, covariances = process.noised_parameters(mixture, 1.0)
    assert np.allclose(means, mixture.means)
    assert np.allclose(covariances, mixture.covariances)


@pytest.mark.parametrize("mixture", TARGETS, ids=lambda m: m.name)
def test_the_score_forgets_the_target_as_the_signal_dies(mixture, points):
    """At small abar every component looks alike, the responsibilities
    flatten, and the score collapses to -x. There is nothing left to reverse,
    which is exactly why the reverse process can start from pure noise."""
    assert np.abs(process.score(mixture, points, 1e-6) + points).max() < 1e-3


@pytest.mark.parametrize("mixture", TARGETS, ids=lambda m: m.name)
def test_noising_inflates_every_covariance_towards_the_identity(mixture):
    _, covariances = process.noised_parameters(mixture, 0.25)
    for noised, original in zip(covariances, mixture.covariances):
        assert np.linalg.det(noised) > np.linalg.det(original)
        assert np.allclose(noised, 0.25 * original + 0.75 * np.eye(mixture.dim))


@pytest.mark.parametrize("mixture", TARGETS, ids=lambda m: m.name)
def test_the_density_is_a_density(mixture):
    grid = np.mgrid[-6:6:0.05, -6:6:0.05].reshape(2, -1).T
    mass = np.exp(process.log_density(mixture, grid, 0.8)).sum() * 0.05 ** 2
    assert abs(mass - 1.0) < 1e-3


@pytest.mark.parametrize("alpha_bar", [0.0, -0.1, 1.5, np.nan])
def test_an_impossible_signal_fraction_is_refused(alpha_bar):
    with pytest.raises(ValueError):
        process.check_alpha_bar(alpha_bar)


def test_a_mixture_that_is_not_a_distribution_is_refused():
    with pytest.raises(ValueError):
        process.Mixture("bad", np.array([0.5, 0.2]), np.zeros((2, 2)),
                        np.stack([np.eye(2)] * 2))


def test_a_state_and_a_batch_give_the_same_answer():
    mixture = process.BIMODAL
    x = np.array([0.3, -1.2])
    assert np.allclose(process.score(mixture, x, 0.6),
                       process.score(mixture, x[None, :], 0.6)[0])


def test_the_domain_imports_no_method():
    """Rule 7, checked instead of asserted.

    Nothing else in this suite would notice a violation. The contract asks
    whether every method obeys the domain, which is the other direction, and
    an import written inside a function body does not even fail at
    collection -- the domain can `import methods`, use it, and leave the
    whole suite green.

    Deliberately shallow: it reads the imports the parser can see, so a
    module fetched through importlib at runtime would walk past it. It
    catches the way the mistake actually gets made.
    """
    domain = Path(__file__).resolve().parent.parent / "process.py"

    imported = []
    for node in ast.walk(ast.parse(domain.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            imported += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.append(node.module)
            else:  # from . import methods
                imported += [alias.name for alias in node.names]

    offenders = sorted(
        name for name in imported
        if name == "methods" or name.startswith("methods.")
    )
    assert not offenders, (
        f"{domain.name} imports {offenders} -- the equations may not "
        f"import the algorithm; the arrow only points the other way"
    )
