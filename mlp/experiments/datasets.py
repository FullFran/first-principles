"""The task, generated rather than downloaded.

The 2024 notebook used `sklearn.datasets.make_circles`. Two concentric rings
are the right problem -- the smallest one no single straight line can solve,
so any success is evidence the hidden layer is doing something -- but pulling
in scikit-learn to draw 500 points from a circle is a dependency this entry
does not need, and the generator is four lines.
"""

import numpy as np

__all__ = ["rings", "uniform_layers", "grid"]


def rings(count=500, seed=0, noise=0.12, inner=0.3, outer=1.0, stretch=1.0):
    """Two noisy concentric rings, labelled by which one a point came from.

    `stretch` scales the first axis. That leaves the problem identical -- same
    points, same labels, separable by the same shape -- and changes only the
    geometry of the surface an optimiser has to walk over.
    """
    rng = np.random.default_rng(seed)
    angle = rng.uniform(0, 2 * np.pi, count)
    is_inner = rng.random(count) > 0.5
    radius = np.where(is_inner, inner, outer) + rng.normal(0, noise, count)
    points = np.c_[radius * np.cos(angle), radius * np.sin(angle)]
    return points * np.array([stretch, 1.0]), is_inner.astype(float)[:, None]


def uniform_layers(topology, activations, seed=0):
    """Initialise the way the 2024 notebook did: rand()*2-1, ignoring fan-in.

    Kept here rather than in the model because it is not an option the entry
    offers -- it is the thing initialisation.py measures against.
    """
    import model
    rng = np.random.default_rng(seed)
    return [model.Layer(rng.random((fan_in, fan_out)) * 2 - 1,
                        rng.random((1, fan_out)) * 2 - 1, name)
            for fan_in, fan_out, name in
            zip(topology[:-1], topology[1:], activations)]


def grid(points, resolution=120, margin=0.25):
    """A mesh spanning the data, for drawing a decision boundary."""
    low = points.min(axis=0) - margin
    high = points.max(axis=0) + margin
    xs = np.linspace(low[0], high[0], resolution)
    ys = np.linspace(low[1], high[1], resolution)
    mesh_x, mesh_y = np.meshgrid(xs, ys)
    return xs, ys, np.c_[mesh_x.ravel(), mesh_y.ravel()]
