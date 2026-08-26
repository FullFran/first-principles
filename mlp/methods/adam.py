"""Give every parameter its own step size, from its own gradient history.

    m <- b1*m + (1-b1)*g          the mean, as momentum has
    v <- b2*v + (1-b2)*g^2        the mean square, which is new
    parameter <- parameter - rate * m_hat / (sqrt(v_hat) + eps)

Dividing by sqrt(v) makes the step scale-free per coordinate: a parameter with
consistently small gradients still moves. That is why Adam is far less
sensitive to a badly scaled problem than plain descent -- it is preconditioning
with a diagonal estimate, learned as it goes.

The hats are bias correction. m and v start at zero, so the early averages are
pulled towards zero; dividing by (1 - beta^t) undoes exactly that, and without
it the first steps are far too small.
"""

import numpy as np

NAME = "adam"
BETA1, BETA2, EPSILON = 0.9, 0.999, 1e-8


def initialise(network):
    return {
        "step": 0,
        "mean": [(np.zeros_like(l.weights), np.zeros_like(l.bias)) for l in network],
        "square": [(np.zeros_like(l.weights), np.zeros_like(l.bias)) for l in network],
    }


def step(network, grads, state, rate):
    state["step"] += 1
    correction1 = 1.0 - BETA1 ** state["step"]
    correction2 = 1.0 - BETA2 ** state["step"]

    for index, (layer, gradient_pair) in enumerate(zip(network, grads)):
        new_mean, new_square = [], []
        for tensor, gradient, mean, square in zip(
                (layer.weights, layer.bias), gradient_pair,
                state["mean"][index], state["square"][index]):
            mean = BETA1 * mean + (1 - BETA1) * gradient
            square = BETA2 * square + (1 - BETA2) * gradient ** 2
            tensor -= rate * (mean / correction1) / (
                np.sqrt(square / correction2) + EPSILON)
            new_mean.append(mean)
            new_square.append(square)
        state["mean"][index] = tuple(new_mean)
        state["square"][index] = tuple(new_square)
    return state
