"""The domain: what a feed-forward network *is*.

A stack of affine maps with a nonlinearity between them, a loss, and the
gradient of that loss with respect to every parameter. No training loop, no
step rule, no stopping criterion -- those are choices, and they live in
`methods/` and `solve.py`.

    methods/ imports model.        model imports nobody.

Conventions
-----------
X           (samples, features) -- samples along the first axis, always
W           (fan_in, fan_out)
b           (1, fan_out)
loss        a MEAN over samples, so gradients are means too and the step size
            does not silently depend on how many rows you passed
derivatives f_prime(z) takes the pre-activation, never the activation
"""

import numpy as np

__all__ = [
    "Layer", "initialise", "forward", "predict", "gradients",
    "ACTIVATIONS", "LOSSES", "check_topology", "check_batch", "flat_gradient",
]


class Layer:
    """One affine map and the nonlinearity that follows it."""

    __slots__ = ("weights", "bias", "activation")

    def __init__(self, weights, bias, activation):
        self.weights = weights
        self.bias = bias
        self.activation = activation

    def __repr__(self):
        fan_in, fan_out = self.weights.shape
        return f"Layer({fan_in}->{fan_out}, {self.activation})"


# --- activations ------------------------------------------------------------
#
# Each entry is (f, f_prime) and BOTH take the pre-activation z. The 2024
# version wrote sigmoid's derivative as a*(1-a) and fed it the activation,
# which is correct for sigmoid and tanh and silently wrong for anything else.
# Taking z costs one recomputation and makes swapping an activation safe.

def _sigmoid(z):
    # exp(-|z|) never overflows; the branch keeps the algebra exact either way
    positive = z >= 0
    result = np.empty_like(z, dtype=float)
    result[positive] = 1.0 / (1.0 + np.exp(-z[positive]))
    tail = np.exp(z[~positive])
    result[~positive] = tail / (1.0 + tail)
    return result


ACTIVATIONS = {
    "sigmoid": (_sigmoid, lambda z: _sigmoid(z) * (1.0 - _sigmoid(z))),
    "tanh": (np.tanh, lambda z: 1.0 - np.tanh(z) ** 2),
    "relu": (lambda z: np.maximum(0.0, z), lambda z: (z > 0).astype(float)),
    "identity": (lambda z: z, lambda z: np.ones_like(z, dtype=float)),
}


# --- losses -----------------------------------------------------------------
#
# Each entry is (loss, dloss/d_output). Both are means over samples.

# Both are a MEAN over samples and a SUM over outputs. Getting that convention
# wrong is not cosmetic: `np.mean` over the whole array divides by samples x
# outputs, so with a two-column target the gradient is off by exactly 2 and
# with three columns by exactly 3. Nothing crashes, training still descends,
# and the effective learning rate is quietly wrong. The finite-difference check
# in tests/test_model.py caught this here, with relative errors of 1.0 and 2.0.

def _bce(predicted, target):
    p = np.clip(predicted, 1e-12, 1.0 - 1e-12)
    per_sample = -np.sum(target * np.log(p) + (1 - target) * np.log(1 - p), axis=1)
    return float(np.mean(per_sample))


def _bce_gradient(predicted, target):
    p = np.clip(predicted, 1e-12, 1.0 - 1e-12)
    return (p - target) / (p * (1 - p)) / target.shape[0]


LOSSES = {
    "mse": (lambda p, t: float(np.mean(np.sum((p - t) ** 2, axis=1))),
            lambda p, t: 2.0 * (p - t) / t.shape[0]),
    "bce": (_bce, _bce_gradient),
}


# --- invariants -------------------------------------------------------------

def check_topology(topology, activations):
    if len(topology) < 2:
        raise ValueError("a network needs at least an input and an output width")
    if any(width < 1 for width in topology):
        raise ValueError(f"every layer needs at least one unit; got {topology}")
    if len(activations) != len(topology) - 1:
        raise ValueError(
            f"{len(topology) - 1} layers need {len(topology) - 1} activations, "
            f"got {len(activations)}")
    unknown = set(activations) - set(ACTIVATIONS)
    if unknown:
        raise ValueError(f"unknown activation(s) {sorted(unknown)}; "
                         f"available: {sorted(ACTIVATIONS)}")


def check_batch(network, inputs, targets=None):
    inputs = np.asarray(inputs, dtype=float)
    if inputs.ndim != 2:
        raise ValueError(f"inputs must be (samples, features), got shape {inputs.shape}")
    fan_in = network[0].weights.shape[0]
    if inputs.shape[1] != fan_in:
        raise ValueError(f"network takes {fan_in} features, got {inputs.shape[1]}")
    if targets is not None:
        targets = np.asarray(targets, dtype=float)
        fan_out = network[-1].weights.shape[1]
        if targets.shape != (inputs.shape[0], fan_out):
            raise ValueError(
                f"targets must be {(inputs.shape[0], fan_out)}, got {targets.shape}")


# --- building ---------------------------------------------------------------

def initialise(topology, activations, seed=0):
    """He/Xavier scaling, chosen per activation.

    Scale matters more than it looks. Draw uniformly from [-1, 1] as the 2024
    version did and a deep tanh or sigmoid stack saturates on the first pass,
    the derivative is ~0 everywhere, and nothing learns -- with no error, just
    a flat loss curve.
    """
    check_topology(topology, activations)
    rng = np.random.default_rng(seed)
    network = []
    for fan_in, fan_out, name in zip(topology[:-1], topology[1:], activations):
        gain = 2.0 if name == "relu" else 1.0
        scale = np.sqrt(gain / fan_in)
        network.append(Layer(
            weights=rng.normal(0.0, scale, size=(fan_in, fan_out)),
            bias=np.zeros((1, fan_out)),
            activation=name,
        ))
    return network


# --- the forward map --------------------------------------------------------

def forward(network, inputs):
    """Return the output and the cache backprop needs: every z and every a."""
    activations = [np.asarray(inputs, dtype=float)]
    preactivations = []
    for layer in network:
        z = activations[-1] @ layer.weights + layer.bias
        preactivations.append(z)
        activations.append(ACTIVATIONS[layer.activation][0](z))
    return activations[-1], (preactivations, activations)


def predict(network, inputs):
    check_batch(network, inputs)
    return forward(network, inputs)[0]


# --- the gradient -----------------------------------------------------------

def gradients(network, inputs, targets, loss="bce"):
    """dLoss/dW and dLoss/db for every layer. This is backpropagation.

    It is one application of the chain rule, written out. Nothing about it is
    a choice: given the architecture and the loss, the gradient is determined.
    What you then *do* with it is `methods/`.

        delta_L = dLoss/da_L * f'(z_L)
        delta_l = (delta_{l+1} @ W_{l+1}^T) * f'(z_l)
        dW_l    = a_{l-1}^T @ delta_l
        db_l    = sum(delta_l, over samples)

    The loss is a mean over samples and its derivative already carries the
    1/n, so both dW and db are means. The 2024 version averaged db and summed
    dW, which trained the two parameter groups at rates differing by the batch
    size -- 500x, in the notebook it shipped with.
    """
    if loss not in LOSSES:
        raise ValueError(f"unknown loss {loss!r}; available: {sorted(LOSSES)}")
    check_batch(network, inputs, targets)
    targets = np.asarray(targets, dtype=float)

    output, (preactivations, activations) = forward(network, inputs)
    delta = LOSSES[loss][1](output, targets)

    grads = [None] * len(network)
    for index in reversed(range(len(network))):
        delta = delta * ACTIVATIONS[network[index].activation][1](preactivations[index])
        grads[index] = (activations[index].T @ delta,
                        np.sum(delta, axis=0, keepdims=True))
        delta = delta @ network[index].weights.T
    return grads


def flat_gradient(network, inputs, targets, loss="bce"):
    """Every gradient as one vector, for checking against finite differences."""
    return np.concatenate([g.ravel() for pair in gradients(network, inputs, targets, loss)
                           for g in pair])
