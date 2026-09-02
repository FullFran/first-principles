# Multilayer perceptron

Backpropagation is one application of the chain rule, written out. This entry
derives it, checks it against a derivative computed a completely different way,
and then contrasts three step rules that are handed exactly the same gradient.
394 lines of core across three optimisers.

| | |
|---|---|
| **Level** | L1 derive · L2 implement · L3 experiment |
| **Domain** | [`model.py`](model.py) — 210 lines, no training loop in it |
| **Methods** | [`sgd.py`](methods/sgd.py) 22 · [`momentum.py`](methods/momentum.py) 31 · [`adam.py`](methods/adam.py) 49 |
| **Tests** | 62, split into domain, contract, and where the methods diverge |
| **Migrated from** | [`Point_classifier/redNumpy.ipynb`](https://github.com/FullFran/Point_classifier) (2024) |

## Layout

```
docs/model.md         the derivation, from the phenomenon down
docs/figures/         the four figures it argues from — tracked, unlike out/
model.py              the domain: forward map, losses, and the gradient
methods/
  sgd.py              take the gradient, scaled
  momentum.py         accumulate a velocity
  adam.py             a step size per parameter, from its own history
solve.py              the loop: batching, epochs, termination
experiments/
  circles.py          the original task, three step rules
  conditioning.py     what a badly shaped landscape costs
  initialisation.py   where the 2024 initialiser stops working
  gradient_cost.py    why backpropagation exists: O(1) passes, not O(P)
tests/
  test_model.py           domain laws, no optimiser involved
  test_methods.py         the contract, run against every method
  test_methods_differ.py  where they legitimately disagree
```

Same dependency rule as everywhere in this repo: **`methods/` imports `model`,
`model` imports nobody.** See [`docs/architecture.md`](../docs/architecture.md).

## 1. What problem does it solve

Draw two concentric rings of points and label them by which ring they came
from. No straight line separates them, so no linear model can do it at any
accuracy above chance. Put one nonlinearity between two affine maps and the
problem becomes easy — and the question is how to find the parameters, given
that you can only measure how wrong you currently are.

## 2. The equations

Derived from the problem downwards — what the family is for, why finite
differences is the wrong answer, the scale analysis and where it all stops —
in [`docs/model.md`](docs/model.md).

A network is a composition of affine maps and nonlinearities:

$$a^{0} = x, \qquad z^{l} = a^{l-1}W^{l} + b^{l}, \qquad a^{l} = f_l\left(z^{l}\right)$$

Training needs $\partial L/\partial W^{l}$ for every layer. Write the chain
rule from the output backwards and it collapses into four lines:

$$\delta^{L} = \frac{\partial L}{\partial a^{L}} \odot f_L'\negthinspace\left(z^{L}\right)$$

$$\delta^{l} = \left(\delta^{l+1} \left(W^{l+1}\right)^{\mathsf T}\right)
\odot f_l'\negthinspace\left(z^{l}\right)$$

$$\frac{\partial L}{\partial W^{l}} = \left(a^{l-1}\right)^{\mathsf T}\delta^{l},
\qquad
\frac{\partial L}{\partial b^{l}} = \sum_{\text{samples}} \delta^{l}$$

That is the whole of backpropagation. **Nothing in it is a choice**: given the
architecture and the loss, the gradient is determined. It goes in `model.py`
for the same reason Snell and Fresnel go in `tmm/physics.py`.

What *is* a choice is the step you take once you have it, and that is
`methods/`:

$$\theta \leftarrow \theta - \eta\thinspace g
\qquad\text{or}\qquad
v \leftarrow \beta v + g,\ \theta \leftarrow \theta - \eta\thinspace v
\qquad\text{or}\qquad
\theta \leftarrow \theta - \eta\thinspace \frac{\hat m}{\sqrt{\hat v} + \varepsilon}$$

Three rules, one gradient. The contract suite asserts what all three must do;
what they must *not* be asked for is speed.

## 3. What I implemented

```
model.initialise()        He/Xavier scaling, chosen per activation
model.forward()           the forward map, keeping every z and a
model.gradients()         backpropagation — the four lines above
model.flat_gradient()     every gradient as one vector, for checking
model.ACTIVATIONS         sigmoid, tanh, relu, identity — each with f'(z)
model.LOSSES              mse, bce — each with dL/d(output)
methods.sgd / momentum / adam
solve.train()             epochs, minibatches, and why it stopped
solve.accuracy()          fraction of rows classified correctly
```

## 4. What I verified

62 tests, in three groups. Note what is *not* in the contract: how fast a
method converges, or whether it survives a badly scaled problem. Demanding
either from every method would assert something false.

| Property | Scope |
|---|---|
| **The gradient matches central finite differences, over 7 architectures** | domain |
| Every activation's `f'(z)` matches the numerical derivative of `f` | domain |
| Every loss's gradient matches the numerical derivative of the loss | domain |
| A network of identities is exactly one affine map | domain |
| A sigmoid output stays in [0, 1] and does not overflow at z = −10⁴ | domain |
| The loss is unchanged when the batch is duplicated | domain |
| Weight scale follows 1/√fan_in, and a wide stack stays off the flat part | domain |
| Bad topology, activation count, loss name and shapes are all rejected | domain |
| The loss goes down | contract |
| The rings are separated above 95% | contract |
| A run is reproducible from its seed | contract |
| Shapes survive training and stay finite | contract |
| Every method is handed an identical gradient | contract |
| A run that cannot move reports converged rather than burning every epoch | contract |
| **Adam survives a 100× stretched axis; plain descent does not** | differ |
| **Adam needs more than 10× fewer epochs even when well conditioned** | differ |
| **Only a stateful rule accelerates on a repeated gradient** | differ |

The first row is the one that pays for the entry. Everything else rests on
backpropagation being the true derivative of the loss, and the only way to know
that is to compute the derivative a completely different way and compare.

**It caught a real bug immediately.** The loss averaged over samples × outputs
while its gradient divided by samples alone. With one output column the two
agree and everything passes; with two columns the gradient is off by exactly 2
and with three by exactly 3. Nothing crashes, training still descends, and the
effective learning rate is quietly wrong. The check reported relative errors of
exactly 1.0 and 2.0, which is what pointed straight at the factor.

### The experiments

**[`circles.py`](experiments/circles.py)** — prediction: all three separate the
rings, and they should disagree on how long it takes.

```
    method   final loss   train acc  held-out acc   epochs to 0.15
      adam      0.02865       0.994         0.986                6
  momentum      0.00007       1.000         0.996                5
       sgd      0.00100       1.000         0.996               17
```

They disagree on something else instead. **Adam is the worst of the three
here**, ending on a loss 400× above momentum's, and the decision boundary shows
why: momentum and plain descent both find a smooth circle, while Adam's is an
angular polygon with a stray spike running off to one corner, and its loss
curve never stops bouncing. Dividing by the running root-mean-square makes
every coordinate move by about the same amount regardless of how small its
gradient is, which is exactly the insurance you want on a badly scaled problem
and pure cost on a well-scaled one. Adam is not a better optimiser. It is a
different trade.

**[`conditioning.py`](experiments/conditioning.py)** — stretch one input axis.
Same points, same labels, same separating shape; only the geometry of the
surface changes.

```
  stretch       adam   momentum        sgd
        1          6         53        170
        3          7         44        141
       10          7         53        162
       30          9        323        306
      100         24       >400       >400
      300        156       >400       >400
```

The claim from chapter 10 of the book, measured: conditioning does not change
the cost of a step, it changes how many steps you need. Between stretch 30 and
100 both plain descent and momentum fall off a cliff, while Adam degrades
gradually — 26× from end to end where the others go from 306 to never.

**[`initialisation.py`](experiments/initialisation.py)** — the 2024 notebook
drew every weight from `rand()*2-1`, so the spread was 0.577 whatever the layer
looked like. The correct scale shrinks as 1/√fan_in.

```
  width   1/sqrt(fan_in)   rand()*2-1      gap
      4          0.96221      0.67223     1.4x
      8          0.93587      0.51047     1.8x
     64          0.88696      0.17644     5.0x
   1024          0.87571      0.04364    20.1x
```

At the widths that notebook used — 4 and 8 units — the two are barely
different, which is why it trained fine. The gap grows as √width, so the same
code stops working the moment the layers get wide:

```
              init  epochs   final loss  accuracy  saturated  stopped because
    1/sqrt(fan_in)     120      0.00030     1.000      0.000  ran out of epochs
        rand()*2-1       2     13.81552     0.500      1.000  loss stopped moving
```

Read the last two columns together. **Every output saturates at exactly 0 or 1**,
so the derivative is exactly zero, no gradient flows, and the loop reports
**converged** after two epochs — with the loss having gone *up*, from 3.74 to
13.82, and accuracy at chance. Nothing raises. That is the case `solve.train`
was written to name honestly: converged is a statement about the loss not
moving, never about the answer being any good.

## 5. What I deliberately left out

- **Automatic differentiation.** The gradient is hand-derived, which is the
  entire point. A tape would hide the four lines this entry exists to show.
- **Convolutions, attention, normalisation layers, dropout.** Dense layers
  only.
- **Softmax and multi-class cross-entropy.** Binary targets only.
- **Learning-rate schedules, early stopping on a validation split, weight
  decay.** One fixed rate, and a plain epoch budget.
- **Second-order methods.** Newton and BFGS are what the conditioning
  experiment is really pointing at, and neither is here.
- **Anything about generalisation.** `circles.py` reports a held-out accuracy
  and nothing in the entry studies overfitting, capacity or regularisation.

## Where this stops being right

| Boundary | What happens |
|---|---|
| Wide layers with the wrong initialiser | Total saturation, zero gradient, and a **converged** report at chance accuracy |
| Adam on a well-scaled problem | Worse final loss than plain descent, and a visibly angular boundary |
| Stretched inputs beyond ~30× | Plain descent and momentum stop reaching the target at all |
| ReLU at exactly z = 0 | The derivative is undefined; the code returns 0 and the tests skip the kink |
| Sigmoid output with BCE | The generic `dL/da · f'(z)` form is 0/0 in the saturated limit; it is clipped, not fused |
| Dense `W` per layer | Everything is O(fan_in × fan_out) in memory, with no sparsity anywhere |
| No validation split in the loop | `solve.train` stops on the training loss; nothing here detects overfitting |

## Provenance: the 2024 version

Original: `Point_classifier/redNumpy.ipynb`, a notebook building a network in
NumPy over `sklearn.datasets.make_circles`. The mechanism in it was right — the
forward pass, the deltas, the shape of backprop — and it does classify the
rings. What the rewrite changed:

| | 2024 | now |
|---|---|---|
| Loss and gradient | Inconsistent. The displayed loss is the *negative* of BCE, and the gradient hardcoded next to it is the MSE delta. Neither is derived from the other | One `(loss, gradient)` pair per name, each checked against finite differences |
| Sign of the loss | Missing, then hidden by `abs()` before plotting, so the "loss curve" *rises* as the model improves | Signed, and it goes down |
| Output delta | `(a − y) · σ'(a)`, which is the MSE delta applied to a BCE loss | Whatever the chain rule gives for the loss you asked for |
| Derivative argument | `f'` receives the activation, not the pre-activation. Correct for sigmoid and tanh, silently wrong otherwise, and `relu` had no derivative at all | `f_prime(z)` everywhere, with a test per activation |
| Batch convention | `mean` for the bias and a `sum` for the weights, so the two groups train at rates differing by the batch size — 500× in the notebook | Both are means, and a test pins it |
| Initialisation | `rand()*2-1`, independent of fan-in | 1/√fan_in, with the failure measured |
| Optimiser | One, fused into the same function as the forward pass | Three behind a contract |
| `train()` | Forward, backward, update and inference in one function with a boolean flag | `forward`, `gradients`, `step`, `train` |
| Tests | none | 62 |

The first row is the interesting one. **The loss is never used to train** — the
gradient sits beside it as a separate hardcoded lambda — so the sign error and
the mismatched delta never affected the result, only the plot. A loss function
that is only ever displayed cannot be wrong in a way anyone notices, which is
precisely why the finite-difference check is the first test in this entry.

## Run it

```bash
uv run pytest mlp                                     # 62 tests
uv run python mlp/experiments/circles.py
uv run python mlp/experiments/conditioning.py         # ~40 s
uv run python mlp/experiments/initialisation.py
uv run python mlp/experiments/gradient_cost.py        # ~5 s, redraws docs/figures/
```

## What this sets up

The first entry here with a *learned* parameter, and the missing piece on the
road [`hopfield/`](../hopfield/) points at. Hopfield has an energy landscape
written down by hand; this has a landscape descended by gradient. Put them
together — learn the energy instead of prescribing it, and sample it instead of
minimising it — and the next stops are a Boltzmann machine and then diffusion.
