"""Where the step rules part company -- and why that is the point.

Every method here receives the same gradient from the same model. They differ
only in what they do with it, so any difference in behaviour is a property of
the step rule and nothing else. The contract suite deliberately says nothing
about speed or about surviving a badly scaled problem, because demanding
either from every method would assert something false.
"""

import numpy as np
import pytest

import model
import solve
from methods import ALL as METHODS


def rings(count=300, seed=0, stretch=1.0):
    """The rings, optionally with one axis stretched.

    Stretching an input axis stretches the loss surface in weight space. The
    problem is unchanged -- the same points, the same labels, separable by the
    same shape -- and only the geometry the optimiser walks over is different.
    """
    rng = np.random.default_rng(seed)
    angle = rng.uniform(0, 2 * np.pi, count)
    inner = rng.random(count) > 0.5
    radius = np.where(inner, 0.3, 1.0) + rng.normal(0, 0.12, count)
    inputs = np.c_[radius * np.cos(angle), radius * np.sin(angle)]
    return inputs * np.array([stretch, 1.0]), inner.astype(float)[:, None]


def fresh():
    return model.initialise([2, 8, 8, 1], ["tanh", "tanh", "sigmoid"], seed=1)


def epochs_to_reach(method, inputs, targets, target_loss, rate, budget):
    """How many epochs before the loss drops below a threshold, or None."""
    network = fresh()
    for epoch in range(1, budget + 1):
        result = solve.train(network, inputs, targets, method=method, rate=rate,
                             epochs=1, batch_size=64, seed=epoch, tolerance=0.0)
        if result.losses[-1] < target_loss:
            return epoch
    return None


def test_adam_survives_a_stretched_axis_and_plain_descent_does_not():
    """One input axis scaled by 100. Same points, same labels, same answer --
    a different landscape. Dividing by sqrt of the running mean square makes
    Adam's step scale-free per coordinate, which is preconditioning learned as
    it goes; plain descent has no such defence and stalls."""
    inputs, targets = rings(stretch=100.0)
    assert epochs_to_reach("adam", inputs, targets, 0.15, 0.05, 120) is not None
    assert epochs_to_reach("sgd", inputs, targets, 0.15, 0.05, 300) is None


def test_adam_needs_far_fewer_epochs_even_when_well_conditioned():
    """Conditioning does not change the cost of a step. It changes how many
    steps you need, which is why the curvature is worth paying for."""
    inputs, targets = rings()
    adam = epochs_to_reach("adam", inputs, targets, 0.15, 0.05, 300)
    plain = epochs_to_reach("sgd", inputs, targets, 0.15, 0.05, 300)
    assert adam is not None and plain is not None
    assert plain > 10 * adam


def test_sgd_is_the_only_stateless_rule():
    network = fresh()
    assert METHODS["sgd"].initialise(network) is None
    assert METHODS["momentum"].initialise(network) is not None
    assert METHODS["adam"].initialise(network) is not None


@pytest.mark.parametrize("method, grows", [("sgd", False), ("momentum", True)])
def test_only_a_stateful_rule_accelerates_on_a_repeated_gradient(method, grows):
    """Hand the same gradient twice. Plain descent takes the same step both
    times; momentum takes a larger second one, because agreeing gradients are
    exactly what its velocity accumulates."""
    inputs, targets = rings(count=40)
    network = model.initialise([2, 5, 1], ["tanh", "sigmoid"], seed=3)
    grads = model.gradients(network, inputs, targets, "bce")
    state = METHODS[method].initialise(network)

    steps = []
    for _ in range(2):
        before = network[0].weights.copy()
        state = METHODS[method].step(network, grads, state, 0.01)
        steps.append(np.linalg.norm(network[0].weights - before))

    assert (steps[1] > steps[0] * 1.5) if grows else (steps[1] == pytest.approx(steps[0]))
