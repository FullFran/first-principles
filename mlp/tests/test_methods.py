"""Contract tests: what every step rule must satisfy, whatever it is.

Register a method in `methods/` and it inherits this suite. What it must NOT
inherit is any claim about *how fast* it gets there, or about surviving a
badly scaled problem -- those differ by design and live in
test_methods_differ.py.
"""

import numpy as np
import pytest

import model
import solve
from methods import ALL as METHODS

METHOD_NAMES = sorted(METHODS)
pytestmark = pytest.mark.parametrize("method", METHOD_NAMES)


def rings(count=300, seed=0):
    """Two concentric rings: the smallest task no single line can solve."""
    rng = np.random.default_rng(seed)
    angle = rng.uniform(0, 2 * np.pi, count)
    inner = rng.random(count) > 0.5
    radius = np.where(inner, 0.3, 1.0) + rng.normal(0, 0.12, count)
    return (np.c_[radius * np.cos(angle), radius * np.sin(angle)],
            inner.astype(float)[:, None])


def fresh():
    return model.initialise([2, 8, 8, 1], ["tanh", "tanh", "sigmoid"], seed=1)


def test_the_loss_goes_down(method):
    inputs, targets = rings()
    result = solve.train(fresh(), inputs, targets, method=method,
                         rate=0.05, epochs=60, batch_size=64, seed=0)
    assert result.losses[-1] < result.losses[0]


def test_the_rings_are_separated(method):
    """The whole point of a hidden layer. A single linear boundary cannot do
    this, so reaching high accuracy is evidence the nonlinearity is working."""
    inputs, targets = rings()
    network = fresh()
    solve.train(network, inputs, targets, method=method,
                rate=0.5, epochs=400, batch_size=64, seed=0)
    assert solve.accuracy(network, inputs, targets) > 0.95


def test_a_run_is_reproducible(method):
    inputs, targets = rings()
    runs = []
    for _ in range(2):
        network = fresh()
        result = solve.train(network, inputs, targets, method=method,
                             rate=0.1, epochs=30, batch_size=32, seed=4)
        runs.append((result.losses, model.predict(network, inputs)))
    assert runs[0][0] == runs[1][0]
    assert np.array_equal(runs[0][1], runs[1][1])


def test_shapes_survive_training(method):
    inputs, targets = rings()
    network = fresh()
    before = [(l.weights.shape, l.bias.shape) for l in network]
    solve.train(network, inputs, targets, method=method,
                rate=0.1, epochs=20, batch_size=64, seed=0)
    assert [(l.weights.shape, l.bias.shape) for l in network] == before
    assert all(np.all(np.isfinite(l.weights)) for l in network)


def test_every_method_is_handed_the_same_gradient(method):
    """The model does not know which optimiser is running. If this ever fails,
    a step rule has leaked into the domain."""
    inputs, targets = rings(count=40)
    reference = model.initialise([2, 5, 1], ["tanh", "sigmoid"], seed=3)
    expected = model.flat_gradient(reference, inputs, targets, "bce")

    network = model.initialise([2, 5, 1], ["tanh", "sigmoid"], seed=3)
    seen = model.flat_gradient(network, inputs, targets, "bce")
    METHODS[method].step(network, model.gradients(network, inputs, targets, "bce"),
                         METHODS[method].initialise(network), 0.01)
    assert np.array_equal(seen, expected)


def test_training_reports_why_it_stopped(method):
    inputs, targets = rings()
    result = solve.train(fresh(), inputs, targets, method=method,
                         rate=0.05, epochs=5, batch_size=64, seed=0)
    assert result.reason == "ran out of epochs"
    assert result.converged is False
    assert len(result.losses) == result.epochs + 1


def test_a_flat_run_converges_rather_than_exhausting_epochs(method):
    """A zero learning rate cannot move, so the loop must notice and say so
    instead of burning every epoch."""
    inputs, targets = rings()
    result = solve.train(fresh(), inputs, targets, method=method,
                         rate=0.0, epochs=500, batch_size=64, seed=0)
    assert result.converged
    assert result.reason == "loss stopped moving"
    assert result.epochs < 500


def test_dimension_mismatch_is_rejected(method):
    with pytest.raises(ValueError, match="takes 2 features"):
        solve.train(fresh(), np.zeros((4, 5)), np.zeros((4, 1)), method=method)


def test_unknown_method_is_rejected(method):
    inputs, targets = rings(count=20)
    with pytest.raises(ValueError, match="unknown method"):
        solve.train(fresh(), inputs, targets, method="l-bfgs")
