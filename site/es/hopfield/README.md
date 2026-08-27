<!-- translated-from: 08c1ffec79c7 -->

# Red de Hopfield

Memoria asociativa como minimización de energía: almacena patrones en los
acoplamientos, dale a la red uno corrupto y déjala bajar la pendiente hasta que
aterrice en la memoria. 209 líneas de núcleo repartidas en dos esquemas de actualización.

| | |
|---|---|
| **Nivel** | L1 derivar · L2 implementar · L3 experimentar |
| **Dominio** | [`model.py`](model.py) — 98 líneas, sin bucle de dinámica dentro |
| **Métodos** | [`asynchronous.py`](methods/asynchronous.py) 23 · [`synchronous.py`](methods/synchronous.py) 17 |
| **Tests** | 48, divididos en dominio, contrato y donde los métodos divergen |
| **Migrado desde** | [`Optimization-Algorithms/4 Clasificación de eventos y detección de fallos`](https://github.com/FullFran/Optimization-Algorithms) (2024, asignatura de máster) |

## Estructura

```
docs/model.md         the derivation, from the phenomenon down
docs/figures/         the four figures it argues from — tracked, unlike out/
model.py              the domain: energy, Hebbian rule, update rule, invariants
methods/
  asynchronous.py     one unit at a time — energy descent guaranteed
  synchronous.py      all units at once — faster, no guarantee
solve.py              termination: sweep until fixed point or cycle
experiments/
  recall.py                 store M A T H, hand one back corrupted
  associative_and_spurious.py   what it does that nobody asked for
  capacity.py               error against load, three network sizes
  landscape.py              the measurements behind the derivation's figures
tests/
  test_model.py           domain laws, no dynamics
  test_methods.py         the contract, run against both schedules
  test_methods_differ.py  where they legitimately disagree
```

La misma regla de dependencias que en todo este repositorio: **`methods/` importa `model`,
`model` no importa a nadie.** Véase [`docs/architecture.md`](../docs/architecture.md).

## 1. Qué problema resuelve

Almacena un puñado de patrones. Más tarde, presenta una versión corrupta o
parcial de uno de ellos y recupera el original — sin índice, sin clave de
búsqueda, sin búsqueda. La memoria no está guardada en ningún sitio que puedas
señalar: es un mínimo de una función de energía, y la recuperación es la red
cayendo dentro de él.

## 2. Las ecuaciones

Tres líneas y el modelo está completo. Derivado desde el problema hacia abajo —
para qué sirve la memoria asociativa, las estimaciones de orden de magnitud,
por qué la capacidad de servilleta está mal, el análisis de escalas y dónde se
acaba todo — en [`docs/model.md`](docs/model.md).

**Energía** sobre estados bipolares $s \in \lbrace -1,+1\rbrace ^N$:

$$E(s) = -\tfrac{1}{2}\thinspace s^{\mathsf T} W s$$

**Aprendizaje hebbiano** — una pasada, sin gradiente, sin iteración:

$$W = \frac{1}{N}\sum_{\mu=1}^{P} p^{\mu} (p^{\mu})^{\mathsf T},
\qquad W_{ii} = 0$$

**Dinámica** — alinea cada unidad con el campo que las demás ejercen sobre ella:

$$h_i = \sum_j W_{ij} s_j, \qquad s_i \leftarrow \mathrm{sign}(h_i)$$

Dos condiciones sostienen toda la teoría: $W$ simétrica y $W_{ii}=0$. Dadas
esas, voltear una unidad cada vez cambia la energía en

$$\Delta E = -\Delta s_i \thinspace h_i \le 0$$

así que $E$ es una función de Lyapunov y la red no puede vagar para siempre. **Ese
argumento necesita que las unidades se muevan de una en una.** Actualízalas todas a
la vez y se derrumba — que es la diferencia entre los dos métodos de aquí, y es
física, no un detalle de implementación.

## 3. Qué implementé

```
model.hebbian_weights()   the learning rule, diagonal cleared
model.energy()            E(s)
model.local_field()       h = W s
model.update_rule()       align with the field; on an exact tie, hold
model.overlap()           m = (1/N) a . b
model.check_weights()     symmetry and zero diagonal — the Lyapunov premises
methods.asynchronous      a sweep is N single-unit updates in random order
methods.synchronous       a sweep is one matrix-vector product
solve.relax()             sweep until a fixed point or a detected cycle
```

## 4. Qué verifiqué

48 tests, en tres grupos. Fíjate en lo que *no* está en el contrato: el descenso
de la energía. Exigírselo a todo método afirmaría algo falso.

| Propiedad | Alcance |
|---|---|
| Pesos simétricos, diagonal nula, iguales al producto exterior promediado | dominio |
| Los patrones almacenados quedan por debajo de los estados aleatorios en energía | dominio |
| Un patrón almacenado es un punto fijo de la regla de actualización | dominio |
| También lo es su imagen especular −p, con energía idéntica | dominio |
| sign(p₁+p₂+p₃) es un punto fijo que nadie almacenó | dominio |
| Un campo nulo deja la unidad en paz — `sign(0)=0` saldría del hipercubo | dominio |
| Los estados siguen siendo bipolares a lo largo de la relajación | contrato |
| Un patrón almacenado no se mueve | contrato |
| La recuperación desde 5%, 15%, 25% de bits volteados devuelve la memoria exactamente | contrato |
| La relajación siempre termina — punto fijo o ciclo detectado | contrato |
| Un empate exacto es imposible cuando P(N−1) es impar, y común cuando es par | dominio |
| float64 reporta menos empates de los que hay — documentado, no arreglado | dominio |
| **Asíncrono: la energía nunca aumenta, siempre alcanza un punto fijo** | solo async |
| **Síncrono: la energía puede subir, y aparecen ciclos de 2** | solo sync |
| **Síncrono: el periodo es 1 o 2 y nunca más** | solo sync |
| **Síncrono: F = −s(t)·W·s(t+1) nunca aumenta** | solo sync |

### Los experimentos de la actividad de clase

Los cinco resultados del trabajo original, reproducidos.

**[`recall.py`](experiments/recall.py)** — los patrones almacenados con sus
energías, y la reconstrucción a partir de 25% de ruido:

```
   pattern       energy        E/N
         M      -336.25    -0.5838
         A      -330.82    -0.5743
         T      -305.82    -0.5309
         H      -362.36    -0.6291
random state       0.03     0.0000   (mean of 200)

   pattern   overlap in  overlap out   sweeps           dE
         M        0.500        1.000        2      -258.90
         A        0.500        1.000        2      -244.76
         T        0.500        1.000        2      -233.68
         H        0.500        1.000        2      -271.28
```

Un cuarto de los bits mal — suficiente para que las letras sean ilegibles — y
cada uno vuelve exacto, en dos barridos. Los estados almacenados están en E/N ≈ −0.58
mientras que un estado aleatorio está en 0.0000: las memorias son de verdad los valles.

Los patrones son letras a propósito, y elegirlas exigió medir. La primera
versión usaba formas abstractas — un anillo, una cruz, barras diagonales — que
son balanceadas y reproducibles y no le dicen nada a quien lee, así que una
figura de una de ellas recuperada del ruido no demuestra nada que nadie pueda
comprobar a ojo. Las letras son reconocibles y están **correlacionadas por
construcción**, porque comparten un fondo: `FRAN` y `AENX` recuperan ambos 0 de
4 desde 25% de ruido, y el conjunto de cuatro letras menos correlacionado del
alfabeto llega a 2. `MATH` recupera 4 de 4 hasta 35% de ruido en seis semillas.
La mayoría de los conjuntos no funcionan.

**[`associative_and_spurious.py`](experiments/associative_and_spurious.py)** —
y aquí el script no obtuvo lo que esperaba, lo que resultó ser el desenlace más
interesante:

```
N — never stored, looks like H  -> settles at +0.889 with H, E = -361.47  SPURIOUS
checkerboard — unrelated        -> settles exactly on −A                  a memory
sign(M + A + T)                 -> settles at +0.628 with both A and T    SPURIOUS
```

**El casi acierto no recupera la memoria.** Dale a la red una `N` — que comparte
los dos trazos verticales con la `H` almacenada y solo difiere en la barra — y
se asienta en algo 0.889 parecido a `H` y no igual a ella, en un valle a
−361.47 frente a los −362.36 de la `H` almacenada. Casi igual de profundo, y
equivocado. La figura lo muestra sin rodeos: lo que sale es visiblemente una H
con la diagonal todavía comiéndosela.

El tablero de ajedrez no relacionado aterriza exactamente en **−A**, el espejo
de una memoria, que es la simetría de signo de los tests de dominio
manifestándose como comportamiento.

Y la mezcla de tres patrones de libro de texto es estable, como la teoría dice
que debe ser. Eso es un cambio respecto a la versión de esta entrada con glifos
abstractos, donde en cambio colapsaba en una memoria — aquellas formas estaban
lo bastante correlacionadas como para remodelar el paisaje. El script sigue
ejecutando el control no correlacionado:

```
random patterns: mixture is a fixed point -> True
overlaps with the three memories: +0.490  +0.472  +0.545
```

**[`capacity.py`](experiments/capacity.py)** — el límite de almacenamiento, error
frente a la carga P/N para tres tamaños de red:

```
   P/N     N=100     N=250     N=500
 0.080    0.0000    0.0002    0.0001
 0.100    0.0005    0.0026    0.0011
 0.120    0.0100    0.0038    0.0056
 0.138    0.0160    0.0328    0.0412
 0.160    0.0370    0.0638    0.1040
 0.200    0.0700    0.1720    0.1577
 0.250    0.1220    0.3014    0.2968
```

El codo está donde la teoría lo pone, en α_c ≈ 0.138. Y la observación de clase
se reproduce: pasada la transición el error crece más rápido en las redes más
grandes — en α = 0.16 el error se triplica aproximadamente de N = 100 a N = 500. La
transición se agudiza con el tamaño, como debe hacerlo una transición de fase.

## 5. Qué dejé fuera a propósito

- **Redes continuas / de Hopfield–Tank.** Solo unidades binarias, así que nada
  de resolver el TSP — un uso distinto de la misma idea de energía.
- **Temperatura finita.** Esta dinámica es Metropolis a T = 0: solo se aceptan
  los movimientos que bajan la energía. La versión a T > 0 es una máquina de Boltzmann.
- **Reglas de almacenamiento que superan a Hebb.** Ni pseudoinversa, ni regla de
  Storkey, y ambas empujan la capacidad muy por encima de 0.138.
- **Memoria asociativa moderna / densa.** Las variantes de capacidad exponencial
  detrás de "Hopfield Networks is All You Need" son una entrada aparte.
- **Acoplamientos dispersos o estructurados.** `W` es un array denso N×N, que es
  lo que limita el tamaño de imagen utilizable.
- **Términos de sesgo.** Sin campo externo.

## Dónde esto deja de ser correcto

| Frontera | Qué ocurre |
|---|---|
| Patrones correlacionados | La recuperación se degrada mucho antes de α_c; tres de cada cuatro conjuntos de letras probados no recuperan nada en absoluto |
| Carga por encima de ≈ 0.138 | La recuperación se rompe — medido, no supuesto |
| `W` densa | N² floats. La versión de 2024 usaba imágenes de 75×75: 5625² ≈ 253 MB de acoplamientos |
| Actualizaciones síncronas | Sin garantía de energía; puede oscilar con periodo 2 |

## Procedencia: la versión de 2024

Original: `Optimization-Algorithms/4 Clasificación de eventos y detección de
fallos/hopfiled.py` (typo del nombre de archivo incluido), 4.1 KB, una clase
`HopfieldNet` sobre fotografías de 75×75 umbralizadas.

La física que había en ella era correcta. Lo que cambió la reescritura:

| | 2024 | ahora |
|---|---|---|
| Normalización | `weights /= len(patterns)` — divide por P, mientras el docstring dice dividir por N | dividir por N |
| Activación | `np.sign`, que devuelve 0 en un empate exacto y saca la unidad de {−1,+1} | mantener el valor actual |
| Terminación | `update(steps=1)` — quien llama adivina cuántas actualizaciones de una sola unidad ejecutar | barrer hasta punto fijo o ciclo detectado |
| Esquemas | solo asíncrono | ambos, para poder contrastar el argumento de Lyapunov con el caso en que falla |
| Tests | ninguno | 37 |

La de la normalización merece precisión: dividir por P en vez de por N es un
factor de escala global sobre `W`, y a `sign()` no le importa la escala, así que
**la dinámica no se vio afectada**. Lo que cambia es el valor de la energía, de
modo que las energías no eran comparables entre redes entrenadas con distintos
números de patrones — que es exactamente lo que hace el experimento de capacidad.

Los patrones de aquí son letras escritas como arte literal en lugar de las
fotografías originales: esas no pueden ir en un repositorio público, y las
fotografías están muy sesgadas hacia un color, lo que correlaciona los patrones
y degrada la recuperación por razones que no tienen nada que ver con el modelo.
Las letras tienen el mismo problema en forma más leve, y por eso el conjunto
hubo que buscarlo en vez de elegirlo — véase §4.

## Ejecútalo

```bash
uv run pytest hopfield                                       # 48 tests
uv run python hopfield/experiments/recall.py
uv run python hopfield/experiments/associative_and_spurious.py
uv run python hopfield/experiments/capacity.py               # ~20 s
uv run python hopfield/experiments/landscape.py              # ~50 s, redraws docs/figures/
```

## Qué prepara esto

Hopfield es la primera parada en el camino hacia la difusión: un paisaje de
probabilidad definido por una energía, y el muestreo implementado como descenso
sobre él. Cambia T = 0 por T > 0 y es una máquina de Boltzmann; sustituye la
energía explícita por un score ∇ log p aprendido y el descenso por un calendario
de ruido, y es un modelo de difusión.
