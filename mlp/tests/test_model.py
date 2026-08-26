"""Domain tests: the forward map, the loss, and the gradient. No training.

Nothing here runs an optimiser. If these fail the mathematics is wrong; if
these pass and a method fails, the step rule is wrong.

The load-bearing test is test_gradient_matches_finite_differences. Everything
else in this entry rests on backpropagation being the true derivative of the
loss, and the only way to know that is to compare it with a derivative
computed a completely different way. It has already earned its place: it
caught the loss averaging over samples x outputs while its gradient divided by
samples alone, which is invisible with one output column and off by exactly
the output width with more.
"""

import numpy as np
import pytest

import model


def numerical_gradient(network, inputs, targets, loss, epsilon=1e-6):
    """Central differences, one parameter at a time. Slow and independent."""
    pieces = []
    for layer in network:
        for tensor in (layer.weights, layer.bias):
            partial = np.zeros_like(tensor)
            for index in np.ndindex(tensor.shape):
                original = tensor[index]
                tensor[index] = original + epsilon
                high = model.LOSSES[loss][0](model.forward(network, inputs)[0], targets)
                tensor[index] = original - epsilon
                low = model.LOSSES[loss][0](model.forward(network, inputs)[0], targets)
                tensor[index] = original
                partial[index] = (high - low) / (2 * epsilon)
            pieces.append(partial)
    return np.concatenate([piece.ravel() for piece in pieces])


def sample(topology, loss, seed=0):
    rng = np.random.default_rng(seed)
    inputs = rng.normal(size=(12, topology[0]))
    if loss == "bce":
        targets = (rng.random((12, topology[-1])) > 0.5).astype(float)
    else:
        targets = rng.normal(size=(12, topology[-1]))
    return inputs, targets


# --- the gradient -----------------------------------------------------------

ARCHITECTURES = [
    ([2, 4, 1], ["tanh", "sigmoid"], "bce"),
    ([2, 8, 4, 1], ["tanh", "tanh", "sigmoid"], "bce"),
    ([4, 3, 1], ["sigmoid", "sigmoid"], "bce"),
    ([2, 5, 3], ["tanh", "sigmoid"], "bce"),
    ([3, 5, 2], ["relu", "identity"], "mse"),
    ([2, 6, 6, 3], ["relu", "tanh", "identity"], "mse"),
    ([5, 4, 4, 2], ["tanh", "relu", "identity"], "mse"),
]


@pytest.mark.parametrize("topology, activations, loss", ARCHITECTURES)
def test_gradient_matches_finite_differences(topology, activations, loss):
    """Backpropagation against a derivative computed another way entirely.

    Note the output widths in the table above: 1, 2 and 3. A gradient that is
    off by a constant factor per output column passes every single-output case
    and fails here, which is exactly how the averaging convention was caught.
    """
    network = model.initialise(topology, activations, seed=1)
    inputs, targets = sample(topology, loss)
    analytic = model.flat_gradient(network, inputs, targets, loss)
    numeric = numerical_gradient(network, inputs, targets, loss)
    relative = np.abs(analytic - numeric) / np.maximum(np.abs(numeric), 1e-8)
    assert relative.max() < 1e-5


@pytest.mark.parametrize("name", sorted(model.ACTIVATIONS))
def test_activation_derivative_matches_finite_differences(name):
    """f_prime takes z, not f(z). Feeding it the activation is the classic
    slip, and it is right for sigmoid and tanh and wrong for the rest."""
    f, f_prime = model.ACTIVATIONS[name]
    z = np.linspace(-3, 3, 41)
    z = z[np.abs(z) > 0.05]          # relu has a kink at 0; nothing is defined there
    step = 1e-6
    numeric = (f(z + step) - f(z - step)) / (2 * step)
    assert np.allclose(f_prime(z), numeric, atol=1e-6)


@pytest.mark.parametrize("name", sorted(model.LOSSES))
def test_loss_derivative_matches_finite_differences(name):
    loss, loss_gradient = model.LOSSES[name]
    rng = np.random.default_rng(3)
    targets = (rng.random((7, 2)) > 0.5).astype(float)
    predicted = rng.uniform(0.15, 0.85, size=(7, 2))
    step = 1e-6
    numeric = np.zeros_like(predicted)
    for index in np.ndindex(predicted.shape):
        original = predicted[index]
        predicted[index] = original + step
        high = loss(predicted, targets)
        predicted[index] = original - step
        low = loss(predicted, targets)
        predicted[index] = original
        numeric[index] = (high - low) / (2 * step)
    assert np.allclose(loss_gradient(predicted, targets), numeric, rtol=1e-5, atol=1e-9)


# --- what the forward map is ------------------------------------------------

def test_a_network_of_identities_is_exactly_a_linear_map():
    """With no nonlinearity, depth buys nothing: the composition of affine
    maps is affine. This is the reason activations exist."""
    network = model.initialise([3, 5, 4, 2], ["identity"] * 3, seed=2)
    combined = network[0].weights @ network[1].weights @ network[2].weights
    offset = (network[0].bias @ network[1].weights + network[1].bias
              ) @ network[2].weights + network[2].bias
    inputs = np.random.default_rng(0).normal(size=(6, 3))
    assert np.allclose(model.predict(network, inputs), inputs @ combined + offset)


def test_forward_shapes_follow_the_topology():
    network = model.initialise([3, 7, 2], ["relu", "sigmoid"], seed=0)
    output, (preactivations, activations) = model.forward(network, np.zeros((5, 3)))
    assert output.shape == (5, 2)
    assert [z.shape for z in preactivations] == [(5, 7), (5, 2)]
    assert [a.shape for a in activations] == [(5, 3), (5, 7), (5, 2)]


def test_a_sigmoid_output_stays_in_the_unit_interval():
    network = model.initialise([2, 6, 1], ["tanh", "sigmoid"], seed=0)
    predicted = model.predict(network, np.random.default_rng(0).normal(0, 50, (40, 2)))
    assert np.all((predicted >= 0.0) & (predicted <= 1.0))


def test_sigmoid_does_not_overflow_on_large_negative_input():
    """exp(-z) overflows for z below about -745. The branch in _sigmoid is
    what keeps this from becoming inf and then nan."""
    with np.errstate(over="raise"):
        assert model.ACTIVATIONS["sigmoid"][0](np.array([-1e4, 0.0, 1e4])).tolist() \
            == [0.0, 0.5, 1.0]


# --- the loss ---------------------------------------------------------------

def test_bce_is_minimised_when_the_prediction_is_the_target():
    targets = np.array([[1.0], [0.0], [1.0]])
    perfect = model.LOSSES["bce"][0](targets.copy(), targets)
    for wrong in (0.5, 0.9, 0.1):
        blended = np.full_like(targets, wrong)
        assert model.LOSSES["bce"][0](blended, targets) > perfect


def test_loss_does_not_change_when_the_batch_is_duplicated():
    """A mean over samples, so the same data twice is the same number. If it
    were a sum, the step size would depend on how many rows you passed."""
    rng = np.random.default_rng(5)
    predicted = rng.uniform(0.1, 0.9, size=(8, 2))
    targets = (rng.random((8, 2)) > 0.5).astype(float)
    for name, (loss, _) in model.LOSSES.items():
        once = loss(predicted, targets)
        twice = loss(np.vstack([predicted] * 2), np.vstack([targets] * 2))
        assert once == pytest.approx(twice), name


# --- initialisation ---------------------------------------------------------

def test_weight_scale_follows_one_over_root_fan_in():
    """The whole content of He/Xavier. A unit sums fan_in terms, so their
    variance adds; scaling each weight by 1/sqrt(fan_in) keeps the sum's
    spread independent of width, and therefore keeps z off the flat part of
    the activation whatever the layer is."""
    for width in (16, 256, 1024):
        network = model.initialise([width, width, 1], ["tanh", "sigmoid"], seed=0)
        assert network[0].weights.std() == pytest.approx(1 / np.sqrt(width), rel=0.1)


def test_initialisation_keeps_a_wide_stack_off_the_flat_part():
    """The 2024 version drew from [-1, 1] regardless of fan-in, so its spread
    was 0.577 at every width while the correct one shrinks as 1/sqrt(fan_in).

    Measured, the gap between the two is 2.7x at width 16 and 21x at width
    1024: the notebook's four- and eight-unit layers were fine and the same
    code does not survive being made wide. That is why this test grows the
    width rather than the depth."""
    for width in (64, 256, 1024):
        topology = [8] + [width] * 4 + [1]
        network = model.initialise(topology, ["tanh"] * 4 + ["sigmoid"], seed=1)
        inputs = np.random.default_rng(0).normal(size=(64, 8))
        _, (preactivations, _) = model.forward(network, inputs)
        deepest = np.mean(model.ACTIVATIONS["tanh"][1](preactivations[-2]))
        assert deepest > 0.5, f"width {width} saturated: mean slope {deepest:.4f}"


def test_initialisation_is_reproducible():
    first = model.initialise([2, 4, 1], ["tanh", "sigmoid"], seed=7)
    second = model.initialise([2, 4, 1], ["tanh", "sigmoid"], seed=7)
    for a, b in zip(first, second):
        assert np.array_equal(a.weights, b.weights)


# --- invariants -------------------------------------------------------------

def test_topology_shorter_than_two_is_rejected():
    with pytest.raises(ValueError, match="at least an input"):
        model.initialise([4], [], seed=0)


def test_activation_count_must_match_the_layers():
    with pytest.raises(ValueError, match="activations"):
        model.initialise([2, 3, 1], ["tanh"], seed=0)


def test_unknown_activation_is_rejected():
    with pytest.raises(ValueError, match="unknown activation"):
        model.initialise([2, 3, 1], ["tanh", "swish"], seed=0)


def test_empty_layer_is_rejected():
    with pytest.raises(ValueError, match="at least one unit"):
        model.initialise([2, 0, 1], ["tanh", "sigmoid"], seed=0)


def test_unknown_loss_is_rejected():
    network = model.initialise([2, 3, 1], ["tanh", "sigmoid"], seed=0)
    with pytest.raises(ValueError, match="unknown loss"):
        model.gradients(network, np.zeros((2, 2)), np.zeros((2, 1)), loss="huber")


def test_wrong_feature_count_is_rejected():
    network = model.initialise([2, 3, 1], ["tanh", "sigmoid"], seed=0)
    with pytest.raises(ValueError, match="takes 2 features"):
        model.predict(network, np.zeros((4, 5)))


def test_wrong_target_shape_is_rejected():
    network = model.initialise([2, 3, 1], ["tanh", "sigmoid"], seed=0)
    with pytest.raises(ValueError, match="targets must be"):
        model.gradients(network, np.zeros((4, 2)), np.zeros((4, 3)))


def test_one_dimensional_input_is_rejected():
    network = model.initialise([2, 3, 1], ["tanh", "sigmoid"], seed=0)
    with pytest.raises(ValueError, match="samples, features"):
        model.predict(network, np.zeros(2))
