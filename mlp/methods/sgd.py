"""Take the gradient, scaled. Nothing else.

The baseline every other rule has to beat, and on a well-conditioned problem
nothing beats it by much. Its weakness is entirely a matter of geometry: the
gradient points perpendicular to the contour lines, which is only the way to
the minimum when the contours are circles. Stretch them into a canyon and the
step points at the walls, so the path zigzags across it and creeps along it,
and the number of steps grows with the condition number.
"""

NAME = "sgd"


def initialise(network):
    return None


def step(network, grads, state, rate):
    for layer, (weight_gradient, bias_gradient) in zip(network, grads):
        layer.weights -= rate * weight_gradient
        layer.bias -= rate * bias_gradient
    return state
