<!-- translated-from: 00f32ac4bf47 -->

# Método de la matriz de transferencia

Reflexión y transmisión de la luz a través de una pila de películas delgadas,
calculadas solo a partir de la ley de Snell y las ecuaciones de Fresnel. 259
líneas de núcleo repartidas en dos solvers que tienen que coincidir entre sí.

| | |
|---|---|
| **Nivel** | L1 derivar · L2 implementar · L3 experimentar |
| **Dominio** | [`physics.py`](physics.py) — 119 líneas, sin un solo algoritmo dentro |
| **Métodos** | [`transfer_matrix.py`](methods/transfer_matrix.py) 44 · [`recursion.py`](methods/recursion.py) 38 |
| **Tests** | 217, de los cuales la suite del contrato se ejecuta contra cada método |
| **Migrado de** | [`Physics-simulations/Cristal_multicapa`](https://github.com/FullFran/Physics-simulations) (2024, asignatura de máster) |

## Estructura

```
docs/physics.md       the derivation, from the phenomenon down
docs/figures/         the four figures it argues from — tracked, unlike out/
physics.py            the domain: Snell, Fresnel, phase, flux, invariants
methods/
  transfer_matrix.py  one way to solve the stack
  recursion.py        another way (Rouard), numerically better behaved
solve.py              orchestration: validate, dispatch, convert to power
experiments/
  bragg_mirror.py     peak reflectance and stopband against closed form
  brewster.py         the p-polarised zero, and where it sits
  stack.py            the measurements behind the derivation's figures
tests/
  test_physics.py     domain laws, no solver involved
  test_methods.py     the contract, parametrised over every method
  test_methods_agree.py   the methods cross-checked against each other
```

Una sola regla de dependencia: **`methods/` importa `physics`, `physics` no
importa a nadie.** Un método recibe cantidades que el dominio ya calculó y
devuelve amplitudes; nunca toca Snell, ni flujo, ni potencia.

La separación no es papeleo. Existe porque *la física es el invariante y el
algoritmo es una elección* — y la forma de demostrar que entiendes cuál es cuál
es cambiar el algoritmo y ver sobrevivir cada ley física. Eso es lo que hace
`test_methods.py`, y es lo único que hace real la frontera entre carpetas. Sin
él los directorios serían decoración.

## 1. Qué problema resuelve

La luz incide sobre una pila de capas paralelas con índices de refracción
distintos. En cada interfaz una parte se refleja y otra se transmite, y esas
ondas parciales interfieren. El TMM responde: **dada la pila, ¿qué fracción de
la potencia incidente vuelve y qué fracción la atraviesa, a cada longitud de
onda y cada ángulo?**

Invierte la pregunta y tienes diseño de materiales — elige las capas para que
la pila refleje exactamente lo que quieres. Eso es un espejo de Bragg, un
recubrimiento antirreflejante, un filtro dieléctrico.

## 2. Las ecuaciones

Solo tres ideas. Todo lo demás es contabilidad. Derivadas desde el problema
hacia abajo — para qué sirven las multicapas, las estimaciones de orden de
magnitud, el corte de rama, el análisis de escalas y dónde se acaba todo — en
[`docs/physics.md`](docs/physics.md).

**Snell**, escrita para que sobreviva a la absorción y a la reflexión total
interna. El vector de onda transversal $n\sin\theta$ se conserva, así que

$$\cos\theta_k = \sqrt{1 - \left(\frac{n_0\sin\theta_0}{n_k}\right)^2}$$

evaluado en el plano complejo. La forma con `arcsin` que aparece en todos los
libros de texto tira justo los dos casos interesantes.

**Fresnel**, de la continuidad de los campos tangenciales en una interfaz:

$$r^s_{ij} = \frac{n_i c_i - n_j c_j}{n_i c_i + n_j c_j}
\qquad
r^p_{ij} = \frac{n_j c_i - n_i c_j}{n_j c_i + n_i c_j}
\qquad c_k \equiv \cos\theta_k$$

**Fase**, acumulada al cruzar una capa de espesor $d_k$:

$$\delta_k = \frac{2\pi}{\lambda} n_k c_k d_k$$

Ese es todo el dominio. Los dos métodos son dos formas de componerlo.

**Matriz de transferencia** — convierte cada interfaz y cada capa en una matriz
$2\times2$ y multiplica:

$$I_{ij} = \frac{1}{t_{ij}}\begin{pmatrix}1 & r_{ij}\cr r_{ij} & 1\end{pmatrix}
\qquad
P_k = \begin{pmatrix}e^{-i\delta_k} & 0\cr 0 & e^{i\delta_k}\end{pmatrix}
\qquad
r = \frac{M_{10}}{M_{00}},\enspace t = \frac{1}{M_{00}}$$

**Recursión** — pliega una capa cada vez, empezando por el sustrato:

$$r_k = \frac{\rho + r_{k+1}e^{2i\delta}}{1 + \rho\thinspace r_{k+1}e^{2i\delta}}
\qquad
t_k = \frac{\tau\thinspace t_{k+1}e^{i\delta}}{1 + \rho\thinspace r_{k+1}e^{2i\delta}}$$

La misma física, aritmética distinta. Coinciden hasta $10^{-13}$, y esa
coincidencia se afirma en la suite.

Último paso, vale la pena ir despacio. $R = |r|^2$, pero **$T \neq |t|^2$** —
la transmitancia lleva el cociente de flujo normal de energía entre el sustrato
y el ambiente, y esa proyección cambia según la polarización:

$$T^s = |t|^2\thinspace \frac{\mathrm{Re}(n_f c_f)}{\mathrm{Re}(n_0 c_0)}
\qquad
T^p = |t|^2\thinspace \frac{\mathrm{Re}(n_f c_f^{\ast})}{\mathrm{Re}(n_0 c_0^{\ast})}$$

## 3. Qué implementé

```
physics.layer_cosines()       complex Snell with forward-decaying branch
physics.fresnel()             amplitude r, t at one interface
physics.accumulated_phase()   delta across a layer
physics.normal_flux()         the projection that makes T != |t|^2
physics.check_domain()        the invariants, enforced not assumed
methods.transfer_matrix       the matrix product
methods.recursion             Rouard's recursion
solve.amplitudes() / .RT()    dispatch and convert
```

Ninguna inversión de matrices en ningún sitio — escribir la matriz de interfaz
en términos de los coeficientes de Fresnel elimina el `linalg.inv` que la
versión de 2024 llamaba dos veces por capa.

## 4. Qué verifiqué

217 tests. Cada uno codifica algo que la física garantiza, y los del contrato
se ejecutan una vez por método.

| Propiedad | Por qué tiene dientes |
|---|---|
| Una sola interfaz reproduce el Fresnel de forma cerrada | El caso más básico de la óptica |
| Aire/vidrio → R = 0.04 a incidencia normal | El número que todo el mundo se sabe de memoria |
| Pila sin pérdidas: R + T = 1 a cualquier ángulo, en ambas polarizaciones | Contabilidad de energía |
| Película absorbente coincide con la forma cerrada de Airy hasta 1e-13 | Índice complejo tratado, no fingido |
| Película absorbente: 0 < A < 1 | La versión débil de la fila anterior, mantenida como red barata |
| Ambiente absorbente y medios con ganancia lanzan excepción | Los dos casos que antes fallaban en silencio |
| Pasado el ángulo crítico: R = 1 exacto, sin NaN | El corte de rama está bien |
| Brewster: Rp = 0 en arctan(n₂/n₁) | Física de la polarización, no solo álgebra |
| La capa de media onda es ausente | La convención de fase está bien |
| (HL)ᴺ coincide con la transformación de admitancia de cuarto de onda | La interferencia multicapa está bien |
| Invertir una pila simétrica preserva R | Caza bugs de alineación de índices |
| **Cada método coincide con todos los demás hasta 1e-13** | Dos algoritmos independientes, una respuesta |

Dos experimentos van más allá del pasa/falla hasta la predicción.

**[`experiments/bragg_mirror.py`](experiments/bragg_mirror.py)** — la
reflectancia de pico coincide con la admitancia analítica hasta seis decimales,
y el ancho de la banda de rechazo converge a la predicción que solo depende del
contraste:

```
 periods     R peak   analytic   stopband
       2   0.658887   0.658887     0.0909
       4   0.936438   0.936438     0.1101
       8   0.998363   0.998363     0.2319
      16   0.999999   0.999999     0.2927

analytic stopband (infinite stack): 0.2911
```

Más periodos compran **profundidad, nunca anchura** — la anchura la fija solo
el contraste de índices. (La anchura medida usa un umbral tosco del 99% del
pico, que solo cobra sentido cuando la banda ya es plana, de ahí la deriva a N
bajo.)

**[`experiments/brewster.py`](experiments/brewster.py)** — el mínimo numérico
de Rp cae en arctan(n₂/n₁) con la resolución de la malla, y es un cero real
(~1e-8, limitado por la malla angular):

```
       interface      found   arctan(n2/n1)    Rp at min
    air -> glass    56.651d         56.659d    7.677e-09
  air -> silicon    75.557d         75.548d    1.090e-07
    glass -> air    33.339d         33.341d    2.352e-09
```

## 5. Qué dejé fuera a propósito

- **Capas incoherentes / gruesas.** Todo aquí es plenamente coherente.
- **Anisotropía y medios magnéticos.** n escalar, μ = 1.
- **Perfiles de campo dentro de la pila.** Solo la r y la t exteriores.
- **Dispersión.** n es una constante, no n(λ).
- **Vectorización sobre la longitud de onda.** Un λ por llamada, a propósito —
  la composición sigue siendo legible. Un espectro es un bucle en el experimento.
- **Diseño inverso.** El original de 2024 llevaba atornillados un optimizador
  genético y un sustituto en Keras. Ese es otro problema y no pertenece a una
  implementación pensada para leerse.
- **Medios con ganancia y ambientes absorbentes.** No aproximados — rechazados.

## Dónde esto deja de ser correcto

Verificado dentro de un dominio, no en general. Los límites, medidos en vez de
supuestos:

| Límite | Qué pasa | Tratamiento |
|---|---|---|
| Ambiente con Im(n) > 0 | la potencia incidente no está definida; sin guarda devolvía R = 5.83, T = −4.82 | `ValueError` |
| Medio con ganancia, Im(n) < 0 | la regla de rama con decaimiento hacia delante deja de valer; sin guarda devolvía T = 1.27, A = −0.29 | `ValueError` |
| ~20 µm de metal en una capa | `transfer-matrix` desborda `M₀₀` y r se va a NaN | usa `method="recursion"`, que no puede crecer |
| Cualquier cosa de la lista de omisiones anterior | no modelado | fuera de alcance por diseño |

Los dos `ValueError` existen porque sondeando los encontré, no porque razonara
mi camino hasta ellos. Vale la pena dejarlo escrito: la suite estaba en verde y
los dos agujeros estaban abiertos de par en par. **Una suite de tests demuestra
los casos que se te ocurrieron.**

La tercera fila es la que paga la arquitectura. Dos métodos, un dominio: la
física es idéntica hasta 1e-13 y solo cambia el techo numérico, que es
exactamente la distinción que la separación de carpetas dice hacer.

## Ejecútalo

```bash
uv run pytest tmm                            # 217 tests
uv run python tmm/experiments/bragg_mirror.py
uv run python tmm/experiments/brewster.py
uv run python tmm/experiments/stack.py       # ~15 s, redraws docs/figures/
```

```python
from solve import RT
RT("s", [1.0, 2.3, 1.45, 1.52], [0, 60, 95, 0], 550.0)
RT("s", n, d, 550.0, method="recursion")     # same physics, different arithmetic
```
