<!-- translated-from: b09e548e8b62 -->

# Muestreo de un paisaje de energía

Puedes evaluar una energía en cualquier punto y nunca puedes normalizarla. Dos
cadenas conviven con eso de formas distintas: una compara alturas y rechaza, la
otra sigue el gradiente y nunca rechaza. Una es exacta y la otra está sesgada en
una cantidad conocida. 342 líneas de núcleo.

| | |
|---|---|
| **Nivel** | L1 derivar · L2 implementar · L3 experimentar |
| **Dominio** | [`distribution.py`](distribution.py) — 152 líneas, sin ninguna cadena dentro |
| **Métodos** | [`metropolis.py`](methods/metropolis.py) 33 · [`langevin.py`](methods/langevin.py) 35 |
| **Tests** | 56, divididos en dominio, contrato y donde los métodos divergen |
| **Trabajo relacionado mío** | [`GPU-accelerated-Ising-Model`](https://github.com/FullFran/GPU-accelerated-Ising-Model) — Metropolis–Hastings sobre el modelo de Ising 3D, a una escala que esta entrada deliberadamente no tiene |

## Estructura

```
docs/distribution.md  the derivation, from the phenomenon down
docs/figures/         the figures it argues from — tracked, unlike out/
distribution.py       the domain: energies, gradients, the density, closed forms
methods/
  metropolis.py       propose and accept on a ratio — exact, and a random walk
  langevin.py         follow the gradient and add noise — biased by O(dt)
solve.py              run a chain, report what it is worth after correlation
experiments/
  gaussian.py         the bias, against its own closed form
  double_well.py      where a chain lies to you and nothing says so
  annealing.py        the same code optimises at T→0 and samples at fixed T
tests/
  test_distribution.py    domain laws, no chain involved
  test_methods.py         the contract, run against both samplers
  test_methods_differ.py  where they legitimately disagree
```

La misma regla de dependencias que en todo este repositorio: **`methods/` importa
`distribution`, `distribution` no importa a nadie.** Ver
[`docs/architecture.md`](../docs/architecture.md).

## 1. Qué problema resuelve

Tienes una energía $E(x)$ y quieres muestras de la densidad que define:

$$p(x) = \frac{e^{-E(x)/T}}{Z}, \qquad Z = \int e^{-E(x)/T}\thinspace dx$$

Puedes calcular $E$ en cualquier punto. **No puedes calcular $Z$** — es una
integral sobre todo el espacio, y en cualquier número interesante de dimensiones
es inalcanzable. Así que puedes calcular *razones* de probabilidades y nunca una
probabilidad.

Cada método de aquí es una manera de convivir exactamente con eso.

## 2. Las ecuaciones

Derivadas desde el problema hacia abajo — qué son las cadenas de Markov, de
dónde salieron (una discusión sobre el libre albedrío), el balance detallado, la
ergodicidad y dónde se acaba todo — en [`docs/distribution.md`](docs/distribution.md).

**Metropolis.** Propón $y$, acéptalo con

$$\min\negthinspace\left(1,\ \frac{p(y)}{p(x)}\right)
= \min\negthinspace\left(1,\ e^{-\left(E(y)-E(x)\right)/T}\right)$$

$Z$ se cancela porque está en el numerador y en el denominador. Rechazar es lo
que impone el balance detallado,

$$p(x)\thinspace q(x \to y)\thinspace A(x \to y)
= p(y)\thinspace q(y \to x)\thinspace A(y \to x)$$

así que la distribución estacionaria es la objetivo **exactamente, con cualquier
tamaño de paso**.

**Langevin.** Sigue el gradiente y añade ruido:

$$x \leftarrow x - \nabla E(x)\thinspace \Delta t
\thinspace + \thinspace \sqrt{2T\Delta t}\thinspace \xi$$

$Z$ también desaparece aquí, por otra razón. La deriva es el gradiente de la log
densidad, y $\log p = -E/T - \log Z$, así que

$$\nabla \log p = -\frac{\nabla E}{T}$$

porque el gradiente de una constante es cero.

> **Ambos métodos funcionan por la misma razón.** $Z$ es una constante, y ni una
> razón ni el gradiente de un logaritmo pueden ver una constante. Uno explota el
> primer hecho y el otro el segundo.

Ese gradiente de una log densidad tiene nombre — el **score** — y es lo que
aprende un modelo de difusión en lugar de derivarlo de una energía que alguien
escribió. Es aprendible *porque* nunca necesita $Z$.

Dos límites que conviene retener: pon $T = 0$ y Langevin es el descenso por
gradiente de [`mlp/`](../mlp/); pon $E = 0$ y es movimiento browniano, con
$\langle x^2\rangle = 2Tt$, cuyo límite continuo es la ecuación de difusión.

## 3. Qué implementé

```
distribution.Target           an energy and its gradient; everything else derives
distribution.GAUSSIAN         E = x²/2, every moment known
distribution.DOUBLE_WELL      two minima and a barrier, populations computable
distribution.FREE             no energy at all — Brownian motion
distribution.exact_moment()   ⟨xⁿ⟩ by quadrature, the reference
distribution.exact_probability()  P(a < x < b) by quadrature
methods.metropolis            propose, compare, accept or reject
methods.langevin              gradient step plus noise, never rejects
solve.chain()                 run it, and report the correlation-corrected error
solve.autocorrelation_time()  how many steps before the chain forgets
```

## 4. Qué verifiqué

56 tests, en tres grupos. Fíjate en lo que *no* está en el contrato: que la
cadena muestree la objetivo. Metropolis lo hace y Langevin sin ajustar no, y
exigírselo a los dos afirmaría algo falso.

| Propiedad | Alcance |
|---|---|
| El segundo momento de la gaussiana es exactamente la temperatura | dominio |
| **Solo importan las diferencias de energía** — desplaza E en 137 y nada cambia | dominio |
| Cada gradiente coincide con una derivada por diferencias finitas | dominio |
| La población sobrante del pozo doble sigue exp(−ΔE/T) | dominio |
| El soporte de la cuadratura es lo bastante ancho para no truncar | dominio |
| T ≤ 0 se rechaza — es una delta, no una distribución | dominio |
| Una objetivo simétrica da media cero, para los dos | contrato |
| La cadena visita la región de baja energía y de verdad se mueve | contrato |
| Una cadena más fría se queda más cerca del mínimo | contrato |
| **Las muestras correlacionadas valen menos que las independientes** | contrato |
| Las extracciones independientes valen su valor nominal — el control | contrato |
| **Metropolis no está sesgado con ningún tamaño de paso** | divergen |
| **Langevin está sesgado exactamente en 1/(1−Δt/2)** | divergen |
| Más muestras arreglan Metropolis y no arreglan Langevin | divergen |
| Solo Metropolis rechaza, y de ahí viene el sesgo | divergen |
| **Solo Langevin pide alguna vez el gradiente** | divergen |
| Una barrera atrapa a cualquiera de los dos, y ninguno lo dice | divergen |

La segunda fila de divergen es la que paga la entrada. Sobre $E = x^2/2$ la
actualización de Langevin es un AR(1), $x' = (1-\Delta t)x + \sqrt{2\Delta t}\thinspace\xi$,
cuya varianza estacionaria es $1/(1-\Delta t/2)$. **La respuesta equivocada tiene
forma cerrada**, y reproducir tu propio error exactamente es un test mucho más
afilado que acertar de forma aproximada.

### Los experimentos

**[`gaussian.py`](experiments/gaussian.py)** — predicción: Metropolis cae en 1
con cualquier tamaño de paso, Langevin cae en una curva que puedes dibujar de
antemano.

```
   step       langevin <x^2>   1/(1-dt/2)  sigma from 1
   0.50      1.334140+-0.0040     1.333333          82.6
   0.20      1.109683+-0.0056     1.111111          19.6
   0.10      1.050395+-0.0076     1.052632           6.6
   0.05      1.021036+-0.0106     1.025641           2.0
   0.02      0.998665+-0.0163     1.010101           0.1

   step     metropolis <x^2>  acceptance     tau  sigma from 1
   0.30      0.973953+-0.0124       0.905    29.7           2.1
   1.00      0.991364+-0.0058       0.705     6.3           1.5
   3.00      1.000194+-0.0053       0.374     5.2           0.0
```

Las dos se cumplieron, y apareció una tercera cosa que no estaba predicha. **Lee
hacia abajo las barras de error de Langevin, según el sesgo se encoge: 0.0040,
0.0056, 0.0076, 0.0106, 0.0163.** *Crecen*. Un paso más pequeño está menos
sesgado y más correlacionado, así que el tamaño de muestra efectivo se hunde y la
barra de error se ensancha hasta cubrir el sesgo. En Δt = 0.02 la cadena es
"compatible con 1" a 0.1σ solo porque se ha vuelto cuatro veces menos certera
sobre todo.

**No puedes arreglar el sesgo encogiendo el paso.** Lo cambias por correlación, y
la barra de error esconde el cambio educadamente.

Los dos métodos tienen un compromiso con el tamaño de paso y son compromisos
distintos. Metropolis cambia aceptación por exploración — con aceptación 0.905
los pasos son tan pequeños que τ es 30, con aceptación 0.374 τ es 5 — y *la
respuesta nunca se mueve*. Langevin cambia sesgo por correlación, y la respuesta
se mueve.

**[`double_well.py`](experiments/double_well.py)** — predicción: a temperatura
alta los dos recuperan las poblaciones, a temperatura baja una cadena puede
quedarse atascada.

```
     T  barrier/T  exact P(x>0)             metropolis               langevin
  1.00        1.2        0.6216     0.6219 ( 25428 x)     0.5757 (  2395 x)
  0.20        5.8        0.9449     0.9406 (  1030 x)     0.9998 (    16 x)
  0.10       11.7        0.9972     0.9972 (    18 x)     0.0000 (     0 x)
  0.05       23.3        1.0000     1.0000 (     0 x)     0.0000 (     0 x)
```

La cuenta entre paréntesis son los cruces de la barrera. En T = 0.10 **Langevin
informa de 0.0000 donde la verdad es 0.9972** — empezó en el pozo izquierdo, sus
pasos eran demasiado pequeños para salir escalando, y nunca salió. Con pinta de
convergida, monótona, con una barra de error que se encoge, y exactamente lo
contrario de la respuesta.

Y mira la última fila, que es la más afilada. **Metropolis acertó con cero
cruces.** Cruzó durante el burn-in y luego se quedó quieto. Una respuesta
correcta de una cadena que nunca muestreó la distribución no es una respuesta
correcta — es el mismo fallo, al que le tocó caer del lado bueno. El diagnóstico
atrapó lo que el número no podía.

**[`annealing.py`](experiments/annealing.py)** — el mismo código, tres programas
de temperatura.

```
              schedule   final x    final E  best E seen   ended in
    frozen  (T = 0.02)   -0.9985    0.29957      0.29415  LEFT well
     hot     (T = 2.0)   -0.4131    0.81173     -0.30543  LEFT well
 cooled  (2.0 -> 0.02)   +1.0202   -0.30440     -0.30543      right
```

Frozen nunca tuvo la energía para cruzar, así que optimizó el pozo en el que
empezó — y ni siquiera *vio* el mínimo global. Hot lo encontró y no se asentaba:
está muestreando, no optimizando. Solo cooled hizo las dos cosas.

Esto es el capítulo 10 del libro medido: optimizar y muestrear son la misma
operación a dos temperaturas.

**Una corrección que el montaje forzó.** La primera versión usaba una anchura de
propuesta de 0.5 y predecía que la cadena congelada se quedaría quieta. No lo
hizo — acabó en el pozo derecho. Con los pozos en ±1, una anchura de 0.5 propone
un salto directo de un mínimo al otro, el movimiento es cuesta abajo, y se acepta
sea cual sea la temperatura. **La barrera solo te atrapa si tus movimientos son
locales.** El recocido es una cura para los movimientos locales; una propuesta lo
bastante ancha para salvar la barrera de un paso significa que no había problema
— y ninguna esperanza de que eso funcione en un número real de dimensiones.

## 5. Qué dejé fuera deliberadamente

- **MALA.** Ajustar con Metropolis la propuesta de Langevin elimina el sesgo por
  completo y conserva el gradiente. Es el arreglo obvio, son dos líneas, y
  dejarlo fuera es lo que hace que el sesgo sea medible aquí.
- **Monte Carlo hamiltoniano.** La respuesta al problema del paseo aleatorio:
  usar momento para que la cadena viaje en vez de difundir.
- **Muestreo de Gibbs.** Que es lo que usa el modelo de Ising de mi otro repositorio.
- **Unidades ocultas y aprender una energía.** Una máquina de Boltzmann visible es
  el `DOUBLE_WELL` de esta entrada con más dimensiones. *Entrenar* una necesita
  divergencia contrastiva y la Z intratable, y eso es otra entrada.
- **Diagnósticos de convergencia más allá de una cadena.** Sin $\hat R$, sin
  varias cadenas, sin comparar la varianza dentro y entre cadenas — que es la
  forma estándar de atrapar exactamente el fallo del pozo doble de arriba.
- **Nada en dimensión alta.** Todas las objetivo de aquí son unidimensionales, que
  es donde viven las formas cerradas y donde el problema del paseo aleatorio es invisible.

## Dónde esto deja de ser cierto

| Frontera | Qué pasa |
|---|---|
| Langevin sin ajustar, cualquier Δt | Muestrea una distribución *cerca* de la objetivo, nunca la objetivo |
| Encoger Δt para arreglar eso | Cambia sesgo por correlación; la barra de error se ensancha para esconderlo |
| Una barrera mucho más alta que T | Cualquiera de las dos cadenas puede quedarse en un modo para siempre y reportarlo con confianza |
| Una respuesta correcta con cero cruces | No es evidencia de nada — mira el diagnóstico, no el número |
| Propuesta más ancha que la barrera | La barrera deja de importar, y el recocido también |
| Dimensión alta | La aceptación de Metropolis se hunde; un paseo aleatorio necesita ~d² pasos para cruzar |
| Una sola cadena | Nada de aquí puede detectar un modo que nunca visitó |

La última fila es el resumen honesto de los límites de la entrada. **Una sola
cadena no puede contarte nada de una parte de la distribución a la que nunca
llegó**, y ejecutarla más tiempo no cambia eso.

## Ejecútalo

```bash
uv run pytest sampling                              # 56 tests, ~22 s
uv run python sampling/experiments/gaussian.py      # ~30 s
uv run python sampling/experiments/double_well.py   # ~40 s
uv run python sampling/experiments/annealing.py
```

La suite más lenta del repositorio, y por una razón que no es un defecto: una
cadena es secuencial por definición, así que no hay nada que vectorizar. Todas
las demás entradas procesan su trabajo por lotes; esta no puede.

## Qué prepara esto

Difusión. Un modelo de difusión es Langevin con el score $\nabla \log p$
*aprendido* en lugar de derivado, más un programa de ruido — que es
[`annealing.py`](experiments/annealing.py) ejecutado en la otra dirección. Las
piezas ya están todas aquí: [`mlp/`](../mlp/) aprende una función a partir de sus
gradientes, [`hopfield/`](../hopfield/) tiene un paisaje de energía escrito a
mano, y esta tiene el muestreador que convierte lo uno en lo otro.
