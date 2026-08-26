"""Accumulate a velocity instead of following each gradient literally.

    v <- beta * v + g,      parameter <- parameter - rate * v

Down the length of a canyon successive gradients agree, so the velocity adds
up and the effective step grows towards rate/(1-beta). Across the canyon they
alternate in sign and cancel. That is the whole mechanism: it is a low-pass
filter on the gradient, and the oscillation is exactly the high-frequency
component.
"""

import numpy as np

NAME = "momentum"
BETA = 0.9


def initialise(network):
    return [(np.zeros_like(layer.weights), np.zeros_like(layer.bias))
            for layer in network]


def step(network, grads, state, rate):
    for index, (layer, (weight_gradient, bias_gradient)) in enumerate(zip(network, grads)):
        weight_velocity, bias_velocity = state[index]
        weight_velocity = BETA * weight_velocity + weight_gradient
        bias_velocity = BETA * bias_velocity + bias_gradient
        layer.weights -= rate * weight_velocity
        layer.bias -= rate * bias_velocity
        state[index] = (weight_velocity, bias_velocity)
    return state
