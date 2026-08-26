"""Drive a method until the network stops improving.

Owns the loop, not the arithmetic: it shuffles, batches, calls the model for a
gradient and the method for a step, records the loss, and decides when to
stop. Every concern a method would otherwise reimplement lives here once.
"""

from dataclasses import dataclass

import numpy as np

import model
from methods import ALL as METHODS

__all__ = ["train", "Training", "METHODS", "DEFAULT_METHOD", "accuracy"]

DEFAULT_METHOD = "sgd"


@dataclass(frozen=True)
class Training:
    losses: list
    epochs: int
    converged: bool
    reason: str


def accuracy(network, inputs, targets, threshold=0.5):
    """Fraction of rows the network gets right, for a binary target."""
    predicted = (model.predict(network, inputs) > threshold).astype(float)
    return float(np.mean(np.all(predicted == np.asarray(targets), axis=1)))


def train(network, inputs, targets, method=DEFAULT_METHOD, loss="bce",
          rate=0.1, epochs=200, batch_size=None, seed=0, tolerance=1e-9):
    """Run epochs of minibatch descent and report why it stopped.

    `converged` means the loss stopped moving, not that the answer is good --
    a network that plateaus in a bad place converges just as firmly as one
    that plateaus in a good one. `reason` says which of the two exits fired,
    so a caller never has to guess whether it ran out of patience.
    """
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}; available: {sorted(METHODS)}")
    inputs = np.asarray(inputs, dtype=float)
    targets = np.asarray(targets, dtype=float)
    model.check_batch(network, inputs, targets)
    if loss not in model.LOSSES:
        raise ValueError(f"unknown loss {loss!r}; available: {sorted(model.LOSSES)}")

    solver = METHODS[method]
    state = solver.initialise(network)
    rng = np.random.default_rng(seed)
    samples = inputs.shape[0]
    size = samples if batch_size is None else min(batch_size, samples)

    losses = [model.LOSSES[loss][0](model.predict(network, inputs), targets)]
    for epoch in range(1, epochs + 1):
        order = rng.permutation(samples)
        for start in range(0, samples, size):
            batch = order[start:start + size]
            grads = model.gradients(network, inputs[batch], targets[batch], loss)
            state = solver.step(network, grads, state, rate)

        losses.append(model.LOSSES[loss][0](model.predict(network, inputs), targets))
        if not np.isfinite(losses[-1]):
            return Training(losses, epoch, False, "diverged")
        if abs(losses[-2] - losses[-1]) < tolerance:
            return Training(losses, epoch, True, "loss stopped moving")

    return Training(losses, epochs, False, "ran out of epochs")
