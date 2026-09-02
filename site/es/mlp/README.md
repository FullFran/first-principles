<!-- translated-from: 9151b8f20c4c -->

# Perceptrón multicapa

La retropropagación es una aplicación de la regla de la cadena, escrita al
completo. Esta entrada la deriva, la contrasta con una derivada calculada de una
forma completamente distinta, y luego enfrenta tres reglas de actualización a las
que se les entrega exactamente el mismo gradiente. 394 líneas de núcleo
repartidas en tres optimizadores.

| | |
|---|---|
| **Nivel** | L1 derivar · L2 implementar · L3 experimentar |
| **Dominio** | [`model.py`](model.py) — 210 líneas, sin bucle de entrenamiento dentro |
| **Métodos** | [`sgd.py`](methods/sgd.py) 22 · [`momentum.py`](methods/momentum.py) 31 · [`adam.py`](methods/adam.py) 49 |
| **Tests** | 62, divididos en dominio, contrato y dónde divergen los métodos |
| **Migrado desde** | [`Point_classifier/redNumpy.ipynb`](https://github.com/FullFran/Point_classifier) (2024) |

## Estructura

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

La misma regla de dependencia que en todo este repositorio: **`methods/` importa
`model`, `model` no importa a nadie.** Véase
[`docs/architecture.md`](../docs/architecture.md).

## 1. Qué problema resuelve

Dibuja dos anillos concéntricos de puntos y etiquétalos según el anillo del que
vienen. Ninguna recta los separa, así que ningún modelo lineal puede hacerlo con
una precisión por encima del azar. Pon una no linealidad entre dos mapas afines y
el problema se vuelve fácil — y la pregunta es cómo encontrar los parámetros,
dado que solo puedes medir cuán equivocado estás ahora mismo.

## 2. Las ecuaciones

Derivadas desde el problema hacia abajo — para qué sirve la familia, por qué las
diferencias finitas son la respuesta equivocada, el análisis de escalas y dónde
todo se detiene — en [`docs/model.md`](docs/model.md).

Una red es una composición de mapas afines y no linealidades:

$$a^{0} = x, \qquad z^{l} = a^{l-1}W^{l} + b^{l}, \qquad a^{l} = f_l\left(z^{l}\right)$$

Entrenar necesita $\partial L/\partial W^{l}$ para cada capa. Escribe la regla de
la cadena desde la salida hacia atrás y se colapsa en cuatro líneas:

$$\delta^{L} = \frac{\partial L}{\partial a^{L}} \odot f_L'\negthinspace\left(z^{L}\right)$$

$$\delta^{l} = \left(\delta^{l+1} \left(W^{l+1}\right)^{\mathsf T}\right)
\odot f_l'\negthinspace\left(z^{l}\right)$$

$$\frac{\partial L}{\partial W^{l}} = \left(a^{l-1}\right)^{\mathsf T}\delta^{l},
\qquad
\frac{\partial L}{\partial b^{l}} = \sum_{\text{samples}} \delta^{l}$$

Eso es toda la retropropagación. **Nada en ella es una elección**: dadas la
arquitectura y la pérdida, el gradiente queda determinado. Va en `model.py` por la
misma razón por la que Snell y Fresnel van en `tmm/physics.py`.

Lo que *sí* es una elección es el paso que das una vez lo tienes, y eso es
`methods/`:

$$\theta \leftarrow \theta - \eta\thinspace g
\qquad\text{or}\qquad
v \leftarrow \beta v + g,\ \theta \leftarrow \theta - \eta\thinspace v
\qquad\text{or}\qquad
\theta \leftarrow \theta - \eta\thinspace \frac{\hat m}{\sqrt{\hat v} + \varepsilon}$$

Tres reglas, un gradiente. La suite de contrato comprueba lo que las tres deben
hacer; lo que *no* se les debe exigir es velocidad.

## 3. Qué implementé

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

## 4. Qué verifiqué

62 tests, en tres grupos. Fíjate en lo que *no* está en el contrato: cuán rápido
converge un método, o si sobrevive a un problema mal escalado. Exigir cualquiera
de las dos cosas a todos los métodos afirmaría algo falso.

| Propiedad | Alcance |
|---|---|
| **El gradiente coincide con diferencias finitas centradas, sobre 7 arquitecturas** | dominio |
| El `f'(z)` de cada activación coincide con la derivada numérica de `f` | dominio |
| El gradiente de cada pérdida coincide con la derivada numérica de la pérdida | dominio |
| Una red de identidades es exactamente un mapa afín | dominio |
| Una salida sigmoide se mantiene en [0, 1] y no desborda en z = −10⁴ | dominio |
| La pérdida no cambia cuando el lote se duplica | dominio |
| La escala de los pesos sigue 1/√fan_in, y una pila ancha se mantiene fuera de la zona plana | dominio |
| Topología, número de activaciones, nombre de la pérdida y formas incorrectos son todos rechazados | dominio |
| La pérdida baja | contrato |
| Los anillos quedan separados por encima del 95% | contrato |
| Una ejecución es reproducible a partir de su semilla | contrato |
| Las formas sobreviven al entrenamiento y siguen siendo finitas | contrato |
| A cada método se le entrega un gradiente idéntico | contrato |
| Una ejecución que no puede moverse informa de convergencia en lugar de quemar todas las épocas | contrato |
| **Adam sobrevive a un eje estirado 100×; el descenso simple no** | divergen |
| **Adam necesita más de 10× menos épocas incluso bien condicionado** | divergen |
| **Solo una regla con estado acelera ante un gradiente repetido** | divergen |

La primera fila es la que paga la entrada. Todo lo demás descansa sobre que la
retropropagación sea la verdadera derivada de la pérdida, y la única forma de
saberlo es calcular la derivada de una forma completamente distinta y comparar.

**Encontró un bug real de inmediato.** La pérdida promediaba sobre muestras ×
salidas mientras que su gradiente dividía solo entre muestras. Con una columna de
salida las dos coinciden y todo pasa; con dos columnas el gradiente se desvía por
exactamente 2 y con tres por exactamente 3. Nada revienta, el entrenamiento sigue
descendiendo, y la tasa de aprendizaje efectiva está silenciosamente equivocada.
La comprobación reportó errores relativos de exactamente 1.0 y 2.0, que es lo que
apuntó directamente al factor.

### Los experimentos

**[`circles.py`](experiments/circles.py)** — predicción: los tres separan los
anillos, y deberían discrepar en cuánto tardan.

```
    method   final loss   train acc  held-out acc   epochs to 0.15
      adam      0.02865       0.994         0.986                6
  momentum      0.00007       1.000         0.996                5
       sgd      0.00100       1.000         0.996               17
```

Discrepan en otra cosa. **Adam es el peor de los tres aquí**, terminando en una
pérdida 400× por encima de la de momentum, y la frontera de decisión muestra por
qué: momentum y el descenso simple encuentran ambos un círculo suave, mientras que
el de Adam es un polígono angular con una púa suelta que se escapa hacia una
esquina, y su curva de pérdida no deja de rebotar. Dividir por la raíz cuadrática
media acumulada hace que cada coordenada se mueva más o menos lo mismo sin
importar cuán pequeño sea su gradiente, que es exactamente el seguro que quieres
en un problema mal escalado y puro coste en uno bien escalado. Adam no es un
optimizador mejor. Es un intercambio distinto.

**[`conditioning.py`](experiments/conditioning.py)** — estira un eje de entrada.
Mismos puntos, mismas etiquetas, misma forma separadora; solo cambia la geometría
de la superficie.

```
  stretch       adam   momentum        sgd
        1          6         53        170
        3          7         44        141
       10          7         53        162
       30          9        323        306
      100         24       >400       >400
      300        156       >400       >400
```

La afirmación del capítulo 10 del libro, medida: el condicionamiento no cambia el
coste de un paso, cambia cuántos pasos necesitas. Entre estiramiento 30 y 100
tanto el descenso simple como momentum caen por un precipicio, mientras que Adam
se degrada gradualmente — 26× de un extremo al otro donde los otros pasan de 306
a nunca.

**[`initialisation.py`](experiments/initialisation.py)** — el cuaderno de 2024
extraía cada peso de `rand()*2-1`, así que la dispersión era 0.577 tuviera el
aspecto que tuviera la capa. La escala correcta encoge como 1/√fan_in.

```
  width   1/sqrt(fan_in)   rand()*2-1      gap
      4          0.96221      0.67223     1.4x
      8          0.93587      0.51047     1.8x
     64          0.88696      0.17644     5.0x
   1024          0.87571      0.04364    20.1x
```

En las anchuras que ese cuaderno usaba — 4 y 8 unidades — las dos apenas se
diferencian, que es por lo que entrenaba bien. La brecha crece como √width, así
que el mismo código deja de funcionar en cuanto las capas se vuelven anchas:

```
              init  epochs   final loss  accuracy  saturated  stopped because
    1/sqrt(fan_in)     120      0.00030     1.000      0.000  ran out of epochs
        rand()*2-1       2     13.81552     0.500      1.000  loss stopped moving
```

Lee las dos últimas columnas juntas. **Cada salida satura en exactamente 0 o 1**,
así que la derivada es exactamente cero, no fluye ningún gradiente, y el bucle
informa de **convergencia** tras dos épocas — con la pérdida habiendo *subido*, de
3.74 a 13.82, y la precisión en el azar. Nada lanza una excepción. Ese es el caso
que `solve.train` se escribió para nombrar honestamente: convergido es una
afirmación sobre que la pérdida no se mueve, nunca sobre que la respuesta sea
buena.

## 5. Qué dejé fuera deliberadamente

- **Diferenciación automática.** El gradiente está derivado a mano, que es todo el
  sentido. Una cinta escondería las cuatro líneas que esta entrada existe para
  mostrar.
- **Convoluciones, atención, capas de normalización, dropout.** Solo capas
  densas.
- **Softmax y entropía cruzada multiclase.** Solo objetivos binarios.
- **Planificaciones de la tasa de aprendizaje, parada temprana sobre una
  partición de validación, decaimiento de pesos.** Una tasa fija, y un
  presupuesto de épocas simple.
- **Métodos de segundo orden.** Newton y BFGS son a lo que apunta realmente el
  experimento de condicionamiento, y ninguno está aquí.
- **Nada sobre generalización.** `circles.py` reporta una precisión sobre datos
  reservados y nada en la entrada estudia el sobreajuste, la capacidad o la
  regularización.

## Dónde esto deja de ser cierto

| Límite | Qué ocurre |
|---|---|
| Capas anchas con el inicializador equivocado | Saturación total, gradiente cero, y un informe de **convergencia** con precisión de azar |
| Adam en un problema bien escalado | Peor pérdida final que el descenso simple, y una frontera visiblemente angular |
| Entradas estiradas más allá de ~30× | El descenso simple y momentum dejan de alcanzar el objetivo por completo |
| ReLU en exactamente z = 0 | La derivada no está definida; el código devuelve 0 y los tests se saltan el pico |
| Salida sigmoide con BCE | La forma genérica `dL/da · f'(z)` es 0/0 en el límite saturado; se recorta, no se fusiona |
| `W` densa por capa | Todo es O(fan_in × fan_out) en memoria, sin dispersión en ninguna parte |
| Sin partición de validación en el bucle | `solve.train` para según la pérdida de entrenamiento; nada aquí detecta el sobreajuste |

## Procedencia: la versión de 2024

Original: `Point_classifier/redNumpy.ipynb`, un cuaderno que construye una red en
NumPy sobre `sklearn.datasets.make_circles`. El mecanismo que tenía era correcto —
el paso hacia delante, las deltas, la forma de la retropropagación — y sí
clasifica los anillos. Lo que cambió la reescritura:

| | 2024 | ahora |
|---|---|---|
| Pérdida y gradiente | Inconsistentes. La pérdida mostrada es la *negativa* de la BCE, y el gradiente escrito a mano junto a ella es la delta de MSE. Ninguno se deriva del otro | Un par `(loss, gradient)` por nombre, cada uno contrastado con diferencias finitas |
| Signo de la pérdida | Ausente, y después escondido por `abs()` antes de graficar, así que la "curva de pérdida" *sube* a medida que el modelo mejora | Con signo, y baja |
| Delta de salida | `(a − y) · σ'(a)`, que es la delta de MSE aplicada a una pérdida BCE | Lo que dé la regla de la cadena para la pérdida que pediste |
| Argumento de la derivada | `f'` recibe la activación, no la preactivación. Correcto para sigmoide y tanh, silenciosamente erróneo en el resto, y `relu` no tenía derivada en absoluto | `f_prime(z)` en todas partes, con un test por activación |
| Convención de lote | `mean` para el sesgo y `sum` para los pesos, así que los dos grupos entrenan a tasas que difieren por el tamaño del lote — 500× en el cuaderno | Ambos son medias, y un test lo fija |
| Inicialización | `rand()*2-1`, independiente del fan-in | 1/√fan_in, con el fallo medido |
| Optimizador | Uno, fusionado en la misma función que el paso hacia delante | Tres detrás de un contrato |
| `train()` | Paso hacia delante, paso hacia atrás, actualización e inferencia en una función con una bandera booleana | `forward`, `gradients`, `step`, `train` |
| Tests | ninguno | 62 |

La primera fila es la interesante. **La pérdida nunca se usa para entrenar** — el
gradiente está a su lado como una lambda separada escrita a mano — así que el
error de signo y la delta desajustada nunca afectaron al resultado, solo a la
gráfica. Una función de pérdida que solo se muestra no puede estar equivocada de
una forma que alguien note, que es precisamente por lo que la comprobación por
diferencias finitas es el primer test de esta entrada.

## Ejecútalo

```bash
uv run pytest mlp                                     # 62 tests
uv run python mlp/experiments/circles.py
uv run python mlp/experiments/conditioning.py         # ~40 s
uv run python mlp/experiments/initialisation.py
uv run python mlp/experiments/gradient_cost.py        # ~5 s, redraws docs/figures/
```

## Qué prepara esto

La primera entrada aquí con un parámetro *aprendido*, y la pieza que faltaba en el
camino al que apunta [`hopfield/`](../hopfield/). Hopfield tiene un paisaje de
energía escrito a mano; esto tiene un paisaje descendido por gradiente. Júntalos —
aprende la energía en lugar de prescribirla, y muestréala en lugar de minimizarla
— y las siguientes paradas son una máquina de Boltzmann y luego difusión.
