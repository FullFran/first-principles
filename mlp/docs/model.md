# Learning a function nobody wrote

> The derivation behind [`mlp/`](../README.md), built from the problem rather
> than from the formula. Read this if you want to know *why* the equations in
> `mlp/model.py` are those and not others.

This document follows one cycle, and the cycle is the point:

```
phenomenon → question → order of magnitude → assumptions → minimal model
   → equations → scale analysis → closed forms → simulation → validation
   → limits of the model → next question
```

The middle is what a degree teaches. The two ends — framing the question and
knowing where the model stops — are what actually separates people who solve
new problems from people who apply formulas. So the two ends get the space
here.

**Contents**

1. [The phenomenon](#1-the-phenomenon)
2. [What this is for](#2-what-this-is-for)
3. [Before you calculate](#3-before-you-calculate)
4. [Why the naive answer fails](#4-why-the-naive-answer-fails)
5. [The minimal model](#5-the-minimal-model)
6. [The equations](#6-the-equations)
7. [One gradient, three step rules](#7-one-gradient-three-step-rules)
8. [Scale analysis: fan-in and the shape of the valley](#8-scale-analysis-fan-in-and-the-shape-of-the-valley)
9. [Closed forms worth memorising](#9-closed-forms-worth-memorising)
10. [What the simulation showed](#10-what-the-simulation-showed)
11. [Where the model stops being true](#11-where-the-model-stops-being-true)
12. [The essentials](#12-the-essentials)
13. [Open questions](#13-open-questions)
14. [References](#14-references)

---

## 1. The phenomenon

Here is a thing you can do and cannot explain. Someone shows you forty
photographs of handwriting and asks which ones say "7". You get them all
right. Now write down the rule you used. Not a description — a rule, precise
enough that someone else could follow it without ever having seen a 7.

You cannot. Nobody can. And yet the rule is clearly *in there*, because you
apply it in a tenth of a second and you agree with everyone else who tries.

That is the situation this entry is about: **a function you can supply
examples of and cannot write down.** The move is to stop trying to write it,
and instead write down a family of functions wide enough to contain something
close to it, plus a procedure for searching that family using only the examples.

> **The question.**
> A family of functions $f_\theta$ with $P$ adjustable numbers $\theta$, and a
> loss $L(\theta)$ measuring how badly $f_\theta$ reproduces the examples.
> **How do you find a $\theta$ that makes $L$ small?**

The answer everyone gives is "go downhill", and it is right. What makes the
subject interesting is that the two obvious follow-up questions — *how much
does it cost to know which way is down*, and *how many steps does downhill
take* — have answers that are not obvious at all, and that decide whether any
of this works.

Those two questions are [§4](#4-why-the-naive-answer-fails) and
[§8](#8-scale-analysis-fan-in-and-the-shape-of-the-valley).

---

## 2. What this is for

### 2.1 It is the whole of modern machine learning, and that is not hyperbole

Every large model trained in the last decade is this document plus
engineering. The architecture changes — convolutions, attention, residual
connections — and the loss changes, and the optimiser gets refinements. The
part that does not change is: define a differentiable function, define a loss,
get the gradient by reverse accumulation, take a step. A transformer with
$10^{12}$ parameters is trained by the four equations in
[§6.3](#63-the-four-lines).

The 2024 Nobel Prize in Physics went to Hopfield and Hinton, and Hinton's half
is largely for making that loop work.

### 2.2 The family really is wide enough

The universal approximation theorem says a network with one hidden layer and a
non-polynomial activation can approximate any continuous function on a compact
set to any accuracy you like, given enough units. Cybenko proved it for
sigmoids in 1989; Hornik generalised it in 1991; Leshno et al. pinned down that
non-polynomial is the actual condition in 1993.

It is worth knowing precisely what that buys, because it is routinely
oversold. It says such a network **exists**. It says nothing about how many
units, nothing about finding it, and nothing about whether the one you find
from finite data will work on anything else. The theorem removes one excuse
and leaves every hard problem untouched.

### 2.3 Reverse accumulation is older and broader than neural networks

What §6 derives is reverse-mode automatic differentiation, specialised to a
layer stack. The general technique predates its use in learning by decades and
is used far outside it: adjoint methods in fluid dynamics and seismic
inversion, sensitivity analysis in climate models, shape optimisation in
aerodynamics, and every physics simulation that needs the derivative of one output with
respect to ten thousand inputs.

The rule of thumb that makes it worth learning once, properly: **reverse mode
gives you the gradient of one scalar with respect to $P$ inputs for a constant
multiple of the cost of evaluating the function.** Forward mode gives you the
derivative of $P$ outputs with respect to one input for the same price. Which
one you want is decided by the shape of your problem, not by fashion.

### 2.4 History

Verification levels follow the convention of the book: **A** is documented,
ideally from a primary source; **B** is a reconstruction; **C** is a story
told everywhere that I could not source.

::: **Published three times before anyone noticed** · *Verification: A —
Schmidhuber's annotated history (2015) traces the chain and the primary
sources are all extant.*

Reverse accumulation was published by **Seppo Linnainmaa in 1970**, in a
Finnish master's thesis, and it was not about learning at all. It was a
general method for tracking the accumulated rounding error of an algorithm —
you need the sensitivity of the output to every intermediate quantity, and the
efficient way to get it is to sweep backwards. The chain rule, in the
direction that pays, four years before anyone applied it to a network.

**Paul Werbos** applied it to networks in his 1974 Harvard PhD thesis. It went
nowhere. He has said the reason was that after *Perceptrons* nobody would
listen to a neural-network argument at all.

The technique became famous with **Rumelhart, Hinton and Williams in 1986**,
sixteen years after Linnainmaa, in four pages in *Nature*.

The lesson is not that the 1986 paper was undeserving — it made the idea
usable, showed what it was for, and demonstrated that the hidden layers
learned *representations*, which is the part that mattered. It is that **an
idea published in the wrong field, in the wrong language, at the wrong time is
not yet an idea anybody has**, and that the gap between the two can be sixteen
years.

::: **A four-page paper and a twenty-eight-year winter** · *Verification: B —
the causal claim about* Perceptrons *is contested by historians, and the
chronology is not.*

The standard story is that Minsky and Papert's *Perceptrons* (1969) proved a
single-layer network cannot compute XOR, killed the field, and that
backpropagation revived it in 1986.

The chronology is right. The causation is disputed — Minsky and Papert were
explicit that multi-layer networks were not covered by their result, funding
patterns are messier than the story, and several historians have pushed back
on the "book killed a field" reading.

But something did stop, and the *mathematical* content is unarguable and is in
this entry: a composition of affine maps is affine, so depth without a
nonlinearity buys nothing
([§6.1](#61-the-forward-map)). XOR needs a curved boundary. Everything after
1986 is what you can do once you can train the layer in between.

### Papers worth reading

| Reference | Why |
|---|---|
| [Rumelhart, Hinton & Williams, *Nature* **323**, 533 (1986)](https://www.nature.com/articles/323533a0) | The paper that made it stick. Four pages |
| Linnainmaa (1970), master's thesis, Univ. Helsinki | Reverse accumulation, sixteen years earlier, in another field |
| [Werbos (1974), Harvard PhD thesis](https://www.researchgate.net/publication/35657389) | Applied to networks, also ignored |
| [Cybenko, *Math. Control Signals Systems* **2**, 303 (1989)](https://doi.org/10.1007/BF02551274) | One hidden layer is enough — existence, and nothing more |
| [Leshno et al., *Neural Networks* **6**, 861 (1993)](https://doi.org/10.1016/S0893-6080(05)80131-5) | The real condition is non-polynomial |
| [Glorot & Bengio, *AISTATS* (2010)](https://proceedings.mlr.press/v9/glorot10a.html) | Why the initialisation scale is $1/\sqrt{\text{fan}}$ and not a taste |
| [He et al., *ICCV* (2015)](https://arxiv.org/abs/1502.01852) | The same argument redone for ReLU, giving the factor 2 |
| [Kingma & Ba, arXiv:1412.6980](https://arxiv.org/abs/1412.6980) | Adam. Read §2, and then read the convergence-proof erratum |
| [Reddi, Kale & Kumar, *ICLR* (2018)](https://arxiv.org/abs/1904.09237) | The proof in the Adam paper is wrong, and Adam still works |
| [Baydin et al., *JMLR* **18**, 1 (2018)](https://jmlr.org/papers/v18/17-468.html) | Automatic differentiation properly: what backprop is a special case of |

Books: Nielsen's *Neural Networks and Deep Learning* ch. 2 for the clearest
derivation of §6; Goodfellow, Bengio & Courville ch. 6 and 8; Nocedal & Wright
for the optimisation half done seriously.

---

## 3. Before you calculate

The rule from the book: **write a number down before you read the next
section.** The learning is in the gap between your number and the real one,
and the gap does not exist if you did not commit.

> 1. A network with $P$ parameters. You want $\partial L/\partial\theta_i$ for
>    every one of them. **How many times do you have to evaluate the loss?**
>    $P$? $2P$? Fewer?
> 2. A hidden layer with 1024 inputs per unit. **How large should its weights
>    be?** The 2024 notebook this entry replaces used a spread of 0.577 at
>    every width. What does that do here?
> 3. You multiply one input feature by 100 and change nothing else. Same
>    points, same labels, same separating shape. **How many more steps does
>    gradient descent need?** Twice? Ten times?

Answers in [§4](#4-why-the-naive-answer-fails) and
[§8](#8-scale-analysis-fan-in-and-the-shape-of-the-valley). The first is the
reason backpropagation exists. The third has an answer that is not a number.

---

## 4. Why the naive answer fails

A derivative is a limit of a difference quotient, and you have a computer, so:

$$\frac{\partial L}{\partial\theta_i} \approx
\frac{L(\theta + \varepsilon e_i) - L(\theta - \varepsilon e_i)}{2\varepsilon}$$

This is correct. It is what [`tests/test_model.py`](../tests/test_model.py)
checks backpropagation against, and if the two ever disagree, backpropagation
is what is wrong. So the question is not whether it works.

**The question is what it costs, and the answer is a disaster.**

Every parameter needs its own pair of evaluations, so a full gradient costs
$2P$ forward passes. Backpropagation costs one forward pass and one backward
pass — a constant multiple of a single evaluation — **whatever $P$ is.** That
is not a constant-factor saving. It is a different complexity class, and it is
the entire reason the field exists.

![Left: time for one full gradient against the number of parameters, log-log,
for finite differences and for backpropagation. Right: the largest relative
error of a difference quotient against the step size, for central and forward
differences.](figures/gradient_cost.png)

**What to conclude:** measured on this entry's own network, backpropagation is
21× faster at 37 parameters and **4147× faster at 4417**, and the ratio has no
ceiling — the left panel is a line against a nearly flat one. A model with
$10^9$ parameters would need $2\times10^9$ forward passes per gradient step;
at one millisecond each, that is 23 days for one step.

**Answer to question 1: once**, near enough. One forward pass and one
backward pass, independent of $P$.

**And it is not even accurate.** The right panel is the other half of the
argument, and it is the one people forget. A difference quotient is squeezed
between two errors pulling in opposite directions:

$$\text{error} \simeq \underbrace{\frac{\varepsilon^2}{6}\left|L'''\right|}_{\text{truncation}}
\thinspace + \thinspace \underbrace{\frac{\epsilon_{\text{mach}}|L|}{\varepsilon}}_{\text{cancellation}}$$

Too large a step and the quotient is not the derivative. Too small and
$L(\theta+\varepsilon)$ and $L(\theta-\varepsilon)$ agree in their leading
digits, the subtraction throws them away, and what survives is rounding noise
divided by a small number. Measured here, the best any step achieves is a
relative error of $10^{-8}$ for central differences and $4\times10^{-6}$ for
forward ones.

**Backpropagation has no such floor, because it never takes a difference at
all.** It is exact up to the arithmetic. That is worth stating plainly: the
slow method is also the inaccurate one, and there is no regime where you would
prefer it except the one that matters — checking that the fast one is right.

---

## 5. The minimal model

Every assumption below buys a specific simplification, and every one of them
fails somewhere real. Listing them is not ceremony — the list *is* the domain
of validity, and it is the thing the tests can never tell you.

| Assumption | What it buys | Where it breaks |
|---|---|---|
| Layers are **dense affine maps** | One matrix per layer; the gradient is a matmul | Convolutions, attention, anything with weight sharing |
| The nonlinearity is **elementwise** | $f'(z)$ is a vector, so the Jacobian is a diagonal and never materialises | Softmax, normalisation layers — both couple across units |
| The network is a **chain** | One $\delta$ per layer, propagated in order | Skip connections, branching, recurrence |
| Everything is **differentiable** | The chain rule applies at all | ReLU at exactly zero; hard thresholds; sampling |
| The loss is a **sum over independent samples** | Gradients average; minibatches are unbiased estimates | Ranking losses, contrastive losses, anything pairwise |
| Parameters are **unconstrained reals** | Plain descent is a legal move | Constraints, quantisation, discrete structure |
| Full precision throughout | No scaling tricks needed | fp16 training, where the gradient underflows |
| **One fixed learning rate** | One number to reason about | Every real training run uses a schedule |
| Training loss is the objective | The loop can stop on it | Generalisation — see [§11](#11-where-the-model-stops-being-true) |

That is the model. Notice what it does **not** assume: it does not assume the
network is shallow, or that the activations are sigmoids, or that the loss is
squared error. Depth, activation and loss are all swappable inside this
framework, which is exactly why the framework outlived every specific choice
made in 1986.

---

## 6. The equations

### 6.1 The forward map

A layer is an affine map followed by an elementwise nonlinearity:

$$a^{0} = x, \qquad z^{l} = a^{l-1}W^{l} + b^{l}, \qquad a^{l} = f_l\negthinspace\left(z^{l}\right)$$

with $x$ of shape (samples, features) and $W^{l}$ of shape (fan-in, fan-out).
Samples run along the first axis throughout, which is a convention and matters
only in that being inconsistent about it is the most common source of silent
shape bugs in hand-written networks.

**Why the nonlinearity is not optional.** Compose two affine maps and you get
an affine map:

$$\left(xW^{1} + b^{1}\right)W^{2} + b^{2}
= x\left(W^{1}W^{2}\right) + \left(b^{1}W^{2} + b^{2}\right)$$

A hundred layers of `identity` is a single matrix, and no amount of
depth buys a curved decision boundary. That claim is a test —
`test_a_network_of_identities_is_exactly_a_linear_map` — precisely because it
is the reason every other line exists.

### 6.2 The chain rule, in the direction that pays

We want $\partial L/\partial W^{l}$ for every $l$. The direct route is to ask
how $L$ depends on $W^{l}$ by pushing forwards, and that is the $O(P)$ disaster
of [§4](#4-why-the-naive-answer-fails), because each parameter's influence
travels its own path to the output.

Reverse the direction. Define

$$\delta^{l} \equiv \frac{\partial L}{\partial z^{l}}$$

— the sensitivity of the loss to the *pre-activation* of layer $l$. This is the
whole trick, and the reason it works is that **every parameter in layer $l$
influences the loss only through $z^{l}$.** Once you know $\delta^{l}$, the
parameters of that layer are one step away, and the layers below are one step
away from $\delta^{l}$. Nothing is computed twice.

Start at the output. $L$ depends on $z^{L}$ through $a^{L} = f_L(z^{L})$, and
$f_L$ is elementwise, so its Jacobian is diagonal and the chain rule is a
product rather than a matrix multiply:

$$\delta^{L} = \frac{\partial L}{\partial a^{L}} \odot f_L'\negthinspace\left(z^{L}\right)$$

Now step down. $z^{l}$ influences $L$ only through $a^{l}$, which enters
$z^{l+1} = a^{l}W^{l+1} + b^{l+1}$. So

$$\frac{\partial L}{\partial a^{l}} = \delta^{l+1}\left(W^{l+1}\right)^{\mathsf T},
\qquad
\delta^{l} = \left(\delta^{l+1}\left(W^{l+1}\right)^{\mathsf T}\right)
\odot f_l'\negthinspace\left(z^{l}\right)$$

and finally, since $z^{l} = a^{l-1}W^{l} + b^{l}$ is linear in the parameters,

$$\frac{\partial L}{\partial W^{l}} = \left(a^{l-1}\right)^{\mathsf T}\delta^{l},
\qquad
\frac{\partial L}{\partial b^{l}} = \sum_{\text{samples}}\delta^{l}$$

### 6.3 The four lines

$$\boxed{\enspace
\begin{aligned}
\delta^{L} &= \partial L/\partial a^{L} \odot f_L'\negthinspace\left(z^{L}\right)\cr
\delta^{l} &= \left(\delta^{l+1}\left(W^{l+1}\right)^{\mathsf T}\right)\odot f_l'\negthinspace\left(z^{l}\right)\cr
\partial L/\partial W^{l} &= \left(a^{l-1}\right)^{\mathsf T}\delta^{l}\cr
\partial L/\partial b^{l} &= \textstyle\sum \delta^{l}
\end{aligned}\enspace}$$

That is [`model.gradients()`](../model.py), verbatim, in eight lines of Python.
**Nothing in it is a choice.** Given the architecture and the loss, the
gradient is determined — there is no alternative correct answer, no tuning, no
approximation. That is exactly why it belongs in the domain file next to the
forward map, and why what you *do* with the gradient is somewhere else.

Note also what the reverse pass costs: one matmul against $W^{l+1}$ and one
against $a^{l-1}$ per layer, which is the same order as the forward pass did.
Hence the constant multiple of [§4](#4-why-the-naive-answer-fails), and hence
the whole subject.

### 6.4 Three traps that do not announce themselves

**$f'$ takes $z$, not $a$.** For a sigmoid the derivative obeys
$\sigma'(z) = \sigma(z)\left(1 - \sigma(z)\right) = a(1-a)$,
so you can write it in terms of the
activation and save a recomputation. It works for sigmoid and it works for
tanh. Do it, and the moment someone swaps in a different activation the
derivative is silently wrong — and it will still train, just badly. The 2024
version did exactly this, and had a `relu` defined with no derivative at all,
waiting. Here `f_prime(z)` takes the pre-activation everywhere, and there is a
test per activation checking it against a numerical derivative.

**The loss and its gradient have to be the same function.** If the loss
averages over samples $\times$ outputs while its gradient divides by samples
alone, the two disagree by exactly the output width. Nothing crashes, training
still descends, and the effective learning rate is quietly wrong by a factor
of 2 or 3. **That bug was in this entry**, and the finite-difference check
found it before there was a training loop — with relative errors of exactly
1.0 and 2.0, which is the signature of a constant-factor error: a gradient
that is $k$ times too large shows up as $|k-1|$.

**Mean or sum, and be consistent.** $\partial L/\partial b^{l}$ is a sum over
samples because $L$'s own definition already carries the $1/n$. Average one
and sum the other and the two parameter groups train at rates differing by the
batch size — 500× in the notebook this replaces. A test pins it by asserting
the loss does not change when the batch is duplicated.

---

## 7. One gradient, three step rules

Everything above produces a vector $g$. What to do with it is a genuinely open
choice, and this is where `methods/` begins.

$$\underbrace{\theta \leftarrow \theta - \eta\thinspace g}_{\text{sgd}}
\qquad
\underbrace{v \leftarrow \beta v + g,\quad \theta \leftarrow \theta - \eta\thinspace v}_{\text{momentum}}
\qquad
\underbrace{\theta \leftarrow \theta - \eta\thinspace\frac{\hat m}{\sqrt{\hat v} + \varepsilon}}_{\text{adam}}$$

**Plain descent** follows the gradient literally. Its weakness is pure
geometry: the gradient is perpendicular to the contour lines, which points at
the minimum only when the contours are circles.

**Momentum** low-pass filters the gradient. Along a valley, successive
gradients agree and the velocity accumulates towards $\eta/(1-\beta)$ — a 10×
amplification at $\beta = 0.9$. Across it they alternate and cancel. The
oscillation *is* the high-frequency component, and filtering is the whole
mechanism.

**Adam** keeps a running mean and mean square per parameter and divides by the
root of the second. That makes each coordinate's step size independent of its
gradient's magnitude, which is a diagonal preconditioner estimated as it goes.
The bias correction $1/(1-\beta^t)$ matters more than it looks: $m$ and $v$
start at zero, so early averages are dragged towards zero, and without the
correction the first steps are far too small.

**A note on Adam's convergence proof.** The 2014 paper contains one. It is
wrong — Reddi, Kale and Kumar (2018) exhibit a convex problem on which Adam
does not converge, and the flaw is in the proof's handling of the second-moment
term. Adam remains one of the most used optimisers in the world. That is worth
sitting with: **a method can be enormously useful and have no valid guarantee,
and knowing which of the two you have is a separate question from whether to
use it.**

### 7.1 What the contract may and may not demand

[`tests/test_methods.py`](../tests/test_methods.py) is parametrised over every
registered method and asserts what all of them must do: reduce the loss,
separate the rings, be reproducible from a seed, preserve shapes, receive an
identical gradient, and report why they stopped.

It deliberately does **not** assert anything about speed, or about surviving a
badly scaled problem. Adding either would look like thoroughness and would be
asserting something false about at least one method — which is the same design
decision as [`hopfield/`](../../hopfield/README.md) refusing to demand energy
descent from its synchronous schedule.

---

## 8. Scale analysis: fan-in and the shape of the valley

Two numbers decide whether a training run works at all, and neither is the
learning rate.

### 8.1 The weight scale is fixed by fan-in

A unit computes $z = \sum_{i=1}^{n} w_i x_i$ over $n = \text{fan-in}$ inputs.
If the $w_i$ are independent with variance $\sigma_w^2$ and the $x_i$ have
variance $\sigma_x^2$, **variances add**:

$$\mathrm{Var}(z) = n\thinspace\sigma_w^2\thinspace\sigma_x^2$$

For $z$ to keep the same spread as $x$ layer after layer — which is what keeps
it off the flat part of the activation — we need

$$\boxed{\enspace\sigma_w = \frac{1}{\sqrt{n}}\enspace}$$

That is the whole of Xavier initialisation. ReLU discards the negative half
and so halves the variance, which is why He initialisation puts a 2 under the
root. Both are in `model.initialise()`, and
`test_weight_scale_follows_one_over_root_fan_in` pins the law rather than the
constant.

![Mean slope of the activation in the deepest hidden layer against layer
width, for the correct scaling and for a fixed spread of 0.577, with the
widths the original notebook used shaded.](figures/initialisation.png)

**What to conclude:** *answer to question 2.* At $n = 1024$ the correct spread
is $1/32 = 0.031$; a fixed 0.577 is **18× too large**, and the measured slope
of the activation in the deepest layer collapses from 0.88 to 0.044. But look
at the shaded band: at the four and eight units the notebook actually used,
the two schemes are within a factor of 1.4 and it trained perfectly well.
**The bug was invisible at the scale it was written at and fatal one order of
magnitude up**, which is the most expensive kind.

### 8.2 The condition number decides the number of steps

For a quadratic bowl with Hessian eigenvalues $\lambda_{\min}\dots\lambda_{\max}$
and $\kappa = \lambda_{\max}/\lambda_{\min}$, gradient descent with the best
fixed step contracts the distance to the minimum by

$$\frac{\lVert\theta_{k+1} - \theta^{\ast}\rVert}{\lVert\theta_k - \theta^{\ast}\rVert}
\simeq \frac{\kappa - 1}{\kappa + 1}$$

At $\kappa = 1$ that is zero — one step. At $\kappa = 1000$ it is $0.998$, so
you need thousands. **The cost per step is unchanged; only the number of steps
moves**, which is why conditioning hurts so much and is so easy to overlook:
nothing in the profile looks wrong.

![Epochs needed to reach a target loss against the stretch applied to one
input axis, for the three step rules, log-log, with crosses marking runs that
never reached it.](figures/conditioning.png)

**What to conclude:** *answer to question 3 — there is no number, because it
is not a slowdown, it is a cliff.* Between 30× and 100× both plain descent and
momentum go from a few hundred epochs to never reaching the target at all,
while Adam degrades gradually across the whole sweep, 6 epochs to 156. Its
per-coordinate normalisation is a preconditioner, and preconditioning is
precisely the defence against $\kappa$.

The practical reading is not "use Adam". It is that **rescaling your inputs is
free and preconditions the problem directly**, and that reaching for a fancier
optimiser to compensate for un-normalised data is paying for a fix you could
have had for one line.

---

## 9. Closed forms worth memorising

These are what you check code against. Cross-checking two methods proves they
agree; checking against a closed form proves they are *right*. Every row here
is a test in [`../tests/`](../tests/).

| Situation | Result |
|---|---|
| Forward pass | $z^{l} = a^{l-1}W^{l} + b^{l}$, $a^{l} = f_l(z^{l})$ |
| Output sensitivity | $\delta^{L} = \partial L/\partial a^{L}\odot f_L'(z^{L})$ |
| Backward recursion | $\delta^{l} = \left(\delta^{l+1}(W^{l+1})^{\mathsf T}\right)\odot f_l'(z^{l})$ |
| Weight gradient | $\partial L/\partial W^{l} = (a^{l-1})^{\mathsf T}\delta^{l}$ |
| Cost of the gradient | one forward and one backward pass, independent of $P$ |
| Cost by differences | $2P$ forward passes, with a relative-error floor near $10^{-8}$ |
| Composition of affine maps | affine: depth without a nonlinearity buys nothing |
| Sigmoid derivative | $\sigma'(z) = \sigma(z)\left(1 - \sigma(z)\right)$ |
| tanh derivative | $1 - \tanh^2(z)$ |
| Sigmoid $+$ BCE, fused | $\delta^{L} = a^{L} - y$ exactly; the $f'$ cancels |
| Xavier scale | $\sigma_w = 1/\sqrt{n}$, from $\mathrm{Var}(z) = n\sigma_w^2\sigma_x^2$ |
| He scale, for ReLU | $\sigma_w = \sqrt{2/n}$ |
| Descent contraction | $(\kappa-1)/(\kappa+1)$ per step |
| Momentum amplification | $\eta/(1-\beta)$ along a consistent direction |
| Adam bias correction | divide by $1 - \beta^{t}$ |

**A warning about row ten.** For a sigmoid output under binary cross-entropy
the $f'$ cancels analytically and $\delta^{L} = a - y$. This entry does
**not** fuse them: it computes the generic $\partial L/\partial a \odot f'(z)$,
which is $\frac{a-y}{a(1-a)} \cdot a(1-a)$ — mathematically identical and
numerically $0/0$ when the output saturates. It is clipped rather than fused,
which is honest about the cost of keeping loss and activation independent, and
is the reason [§11](#11-where-the-model-stops-being-true) lists saturation
first.

---

## 10. What the simulation showed

The book's rule: **predict before you run.** Every experiment here is a
prediction with a number attached, not a plot to admire. Two of the three
returned something other than what was predicted, and those are the two worth
reading.

### 10.1 The rings — [`circles.py`](../experiments/circles.py)

Prediction: all three rules separate the rings, and they disagree on how long
it takes.

```
    method   final loss   train acc  held-out acc   epochs to 0.15
      adam      0.02865       0.994         0.986                6
  momentum      0.00007       1.000         0.996                5
       sgd      0.00100       1.000         0.996               17
```

They disagree on something else entirely. **Adam is the worst of the three**,
finishing 400× above momentum's loss, and the decision boundary shows why in a
way the number does not.

![Decision boundaries for the three step rules on two concentric rings, and
their loss curves on a log scale.](figures/circles.png)

**What to conclude:** momentum and plain descent both find a smooth circle,
which is the right shape. Adam finds an **angular polygon with a stray spike
running off to one corner**, and its loss curve never stops bouncing. Dividing
by the running root-mean-square moves every coordinate by about the same
amount however small its gradient is — exactly the insurance you want on a
badly scaled problem, and pure cost on a well-scaled one, where it stops the
run from ever settling.

**Adam is not a better optimiser. It is a different trade**, and §8.2 is where
the trade pays off.

### 10.2 Conditioning — [`conditioning.py`](../experiments/conditioning.py)

Covered in [§8.2](#82-the-condition-number-decides-the-number-of-steps). The
prediction held: the same problem in a worse-shaped landscape costs steps and
not arithmetic. The surprise was the sharpness — a cliff between 30× and 100×
rather than a slope.

### 10.3 Initialisation — [`initialisation.py`](../experiments/initialisation.py)

Prediction: `rand()*2-1` saturates a **deep** stack.

**Wrong, and worth recording as wrong.** Measured, depth barely matters and
width decides everything, because that spread is 0.577 regardless of fan-in
while the correct one shrinks as $1/\sqrt{n}$. The hypothesis was rewritten to
match the measurement, and a test docstring that asserted the depth story was
rewritten with it.

What it does when it fails is the better half:

```
              init  epochs   final loss  accuracy  saturated  stopped because
    1/sqrt(fan_in)     120      0.00030     1.000      0.000  ran out of epochs
        rand()*2-1       2     13.81552     0.500      1.000  loss stopped moving
```

Read the last two columns together. **Every single output saturates at exactly
0 or 1**, so $f'(z)$ is exactly zero, so no gradient flows, so nothing moves —
and `solve.train` reports **converged** after two epochs, with the loss having
gone *up* from 3.74 to 13.82 and accuracy sitting at chance. Nothing raises,
nothing warns.

That is the case the training loop's docstring was written to name:
**converged is a statement about the loss not moving, never about the answer
being any good.** A stopping criterion that cannot tell those apart will
report success on a network that learned nothing.

---

## 11. Where the model stops being true

The section that matters most, and the one that is usually missing.

### 11.1 Generalisation — the assumption that fails first

Everything in this document minimises the loss **on the examples you have**.
Nothing in it says anything about the examples you do not.

That gap is not a technicality; it is the entire difference between fitting
and learning, and this entry is on the wrong side of it. `solve.train` stops
on the training loss. `circles.py` prints a held-out accuracy and no part of
the code uses it. There is no validation split in the loop, no early stopping,
no weight decay, no capacity control of any kind.

The rings are easy enough that it does not bite here — held-out accuracy is
0.996 against 1.000 on the training set — and that is luck, not design. Point
the same code at a task with more parameters than signal and it will drive the
training loss to zero while getting steadily worse at the thing you wanted,
reporting excellent numbers throughout.

This is the same shape as the book's warning about optimising a proxy: the
loss is a model of what you want, and optimising a model of what you want
aggressively enough will find the places where the model and the want come
apart.

### 11.2 The rest of the list

| Limit | What actually happens | This entry |
|---|---|---|
| Wide layers, wrong initialiser | Total saturation, zero gradient, **converged at chance** | measured in §10.3 |
| Saturated sigmoid under BCE | Generic $\delta$ is $0/0$; clipped rather than fused | clipped, documented |
| Adam on a well-scaled problem | Worse final loss, visibly angular boundary | measured in §10.1 |
| Inputs stretched past ~30× | Plain descent and momentum stop arriving at all | measured in §8.2 |
| ReLU at exactly $z = 0$ | Derivative undefined; code returns 0 and the tests skip the kink | by convention |
| Dead ReLU units | A unit stuck at $z \lt 0$ has zero gradient forever | not detected |
| Deep stacks | Repeated $\odot f'$ shrinks $\delta$ geometrically | not modelled — no residuals, no normalisation |
| Overfitting | Training loss falls, held-out accuracy does not | not detected, not defended |
| fp16 or lower | The gradient underflows and needs loss scaling | not modelled |
| Weight sharing | Gradients must be accumulated across uses | outside the model's premises |

Two of those rows exist because someone **probed** rather than reasoned: the
width-dependent initialisation failure, and the mismatch between the loss and
its gradient in §6.4. In both cases the suite was green and the code looked
right.

> A test suite proves the cases you thought of. The limits of a model are
> found by attacking it, not by re-reading it.

---

## 12. The essentials

- The creative step is **giving up on writing the function** and writing a
  family plus a search instead.
- **Backpropagation is not how you get a gradient — it is how you get $P$ of
  them for the price of one.** Finite differences also works, costs $2P$
  forward passes, and cannot beat a relative error of $10^{-8}$.
- **The trick is $\delta^{l} = \partial L/\partial z^{l}$**, because every
  parameter in a layer reaches the loss only through that layer's
  pre-activation. Nothing is computed twice.
- **The four lines are not a choice.** Given the architecture and the loss the
  gradient is determined, which is why it lives in the domain file.
- **The step rule is a choice**, and the three here are genuinely different
  trades rather than a quality ordering.
- **$f'$ takes $z$, not $a$.** The shortcut is right for sigmoid and tanh and
  silently wrong for everything else.
- **The loss and its gradient must be the same function.** A constant-factor
  mismatch is invisible with one output and shows up as $|k-1|$ in a
  finite-difference check.
- **Weight scale is $1/\sqrt{\text{fan-in}}$**, because variances add. A fixed
  spread works at width 8 and destroys the network at width 1024.
- **Conditioning changes the number of steps, not the cost of one.** And past
  a point it stops being a slowdown and becomes a cliff.
- **Rescale your inputs before you upgrade your optimiser.** One is free.
- **Converged means the loss stopped moving.** It does not mean the answer is
  good, and a saturated network satisfies it perfectly.
- **Nothing here measures generalisation**, which is the only thing anyone
  actually wanted.

---

## 13. Open questions

Things this document deliberately does not answer, roughly in order of how
much they would teach:

- **Why does anything generalise?** The network has enough parameters to
  memorise the training set and does not. Classical capacity arguments predict
  it should fail and it does not, and the honest state of the art is that this
  is not settled. It is also the single biggest gap between this entry and
  anything useful.
- **What does the loss surface actually look like?** Everything here treats it
  as a valley. In high dimension, critical points are overwhelmingly saddles
  rather than minima — the probability that all $P$ Hessian eigenvalues are
  positive is vanishing — so the obstacle is plateaus, not local minima.
  Nothing in this entry measures a single eigenvalue.
- **Why does stochastic gradient noise help?** Minibatch gradients are noisy
  estimates, and the noise appears to favour wide minima, which appear to
  generalise better. Both halves of that sentence are empirical.
- **What breaks in a deep stack?** Each layer multiplies $\delta$ by another
  $f'$, so the gradient shrinks geometrically with depth. Residual connections
  and normalisation are the answers, and neither is here.
- **When is second order worth it?** §8.2 is an advertisement for using
  curvature, and Newton costs $O(P^3)$ per step. The whole quasi-Newton family
  exists in that gap, and the reason it lost to first-order methods at scale
  is a genuinely interesting story about memory rather than mathematics.

---

## 14. References

**Foundational**

- **Rumelhart, D. E., Hinton, G. E. & Williams, R. J.** *Learning
  representations by back-propagating errors.* Nature **323**, 533–536 (1986).
  [link](https://www.nature.com/articles/323533a0)
- **Linnainmaa, S.** *The representation of the cumulative rounding error of
  an algorithm as a Taylor expansion of the local rounding errors.* Master's
  thesis, University of Helsinki (1970). Reverse accumulation, first.
- **Werbos, P. J.** *Beyond regression: new tools for prediction and analysis
  in the behavioral sciences.* PhD thesis, Harvard (1974).
- **Baydin, A. G. et al.** *Automatic differentiation in machine learning: a
  survey.* JMLR **18**, 1–43 (2018).
  [link](https://jmlr.org/papers/v18/17-468.html) — what backpropagation is a
  special case of.

**What the family can represent**

- **Cybenko, G.** *Approximation by superpositions of a sigmoidal function.*
  Mathematics of Control, Signals and Systems **2**, 303–314 (1989).
  [link](https://doi.org/10.1007/BF02551274)
- **Hornik, K.** *Approximation capabilities of multilayer feedforward
  networks.* Neural Networks **4**, 251–257 (1991).
- **Leshno, M. et al.** *Multilayer feedforward networks with a nonpolynomial
  activation function can approximate any function.* Neural Networks **6**,
  861–867 (1993). [link](https://doi.org/10.1016/S0893-6080(05)80131-5)

**Initialisation and optimisation**

- **Glorot, X. & Bengio, Y.** *Understanding the difficulty of training deep
  feedforward neural networks.* AISTATS (2010).
  [link](https://proceedings.mlr.press/v9/glorot10a.html) — §8.1 in one paper.
- **He, K. et al.** *Delving deep into rectifiers.* ICCV (2015).
  [link](https://arxiv.org/abs/1502.01852)
- **Polyak, B. T.** *Some methods of speeding up the convergence of iteration
  methods.* USSR Comp. Math. **4**, 1–17 (1964). Momentum.
- **Kingma, D. P. & Ba, J.** *Adam: a method for stochastic optimization.*
  arXiv:1412.6980 (2014). [link](https://arxiv.org/abs/1412.6980)
- **Reddi, S. J., Kale, S. & Kumar, S.** *On the convergence of Adam and
  beyond.* ICLR (2018). [link](https://arxiv.org/abs/1904.09237) — the proof
  in the previous entry does not hold.
- **Nocedal, J. & Wright, S.** *Numerical Optimization*, 2nd ed. (2006). The
  optimisation half, done seriously.

**The landscape**

- **Dauphin, Y. et al.** *Identifying and attacking the saddle point problem
  in high-dimensional non-convex optimization.* NeurIPS (2014).
  [link](https://arxiv.org/abs/1406.2572)
- **Zhang, C. et al.** *Understanding deep learning requires rethinking
  generalization.* ICLR (2017). [link](https://arxiv.org/abs/1611.03530) —
  §13's first question, stated properly.

**Books**

- **Nielsen, M.** *Neural Networks and Deep Learning*, ch. 2.
  [link](http://neuralnetworksanddeeplearning.com/chap2.html) — the clearest
  derivation of §6 anywhere.
- **Goodfellow, I., Bengio, Y. & Courville, A.** *Deep Learning* (2016), ch. 6
  and 8.

---

*Code: [`../model.py`](../model.py) and [`../methods/`](../methods/) ·
Entry: [`../README.md`](../README.md) · Repo-wide architecture:
[`docs/architecture.md`](../../docs/architecture.md)*
