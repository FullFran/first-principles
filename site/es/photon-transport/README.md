<!-- translated-from: 85ff577088ee -->

# Transporte de fotones

Fotones de una fuente, una lámina que absorbe algunos de ellos, un detector que
cuenta el resto. Dos estimadores para el mismo número: uno simula lo que hace
cada fotón, el otro lo integra. Coinciden, y uno de ellos necesita 200 000×
menos fotones. 282 líneas de núcleo.

| | |
|---|---|
| **Nivel** | L1 derivar · L2 implementar · L3 experimentar |
| **Dominio** | [`physics.py`](physics.py) — 136 líneas, sin bucle de muestreo dentro |
| **Métodos** | [`analog.py`](methods/analog.py) 25 · [`weighted.py`](methods/weighted.py) 32 |
| **Tests** | 56, repartidos entre dominio, contrato y dónde divergen los métodos |
| **Migrado desde** | [`Physics-simulations/Iter_rad_material`](https://github.com/FullFran/Physics-simulations) (2024) |

## Estructura

```
docs/physics.md       the derivation, from the phenomenon down
docs/figures/         the figures it argues from — tracked, unlike out/
physics.py            the domain: emission, free paths, geometry, Beer-Lambert
methods/
  analog.py           sample a free path; the photon gets through or it does not
  weighted.py         never absorb — carry the survival probability
solve.py              run photons, return a value with an error bar
experiments/
  beer_lambert.py     recover the law the estimators were never told
  variance.py         the same answer, and one keeps almost no randomness
  radiograph.py       what that difference looks like as an image
tests/
  test_physics.py         domain laws, no estimator involved
  test_methods.py         the contract, run against both estimators
  test_methods_differ.py  where they legitimately disagree
```

La misma regla de dependencias que en todo este repositorio: **`methods/` importa
`physics`, `physics` no importa a nadie.** Véase
[`docs/architecture.md`](../docs/architecture.md).

## 1. Qué problema resuelve

Una fuente emite fotones dentro de un cono. A cierta distancia hay una lámina de
material que los absorbe, y detrás de ella un detector. **¿Qué fracción llega?**

Eso es una radiografía, y es también diseño de blindaje, dosimetría y toda
pregunta del tipo «cuánto de esto atraviesa aquello» en física de radiaciones.
La respuesta analítica existe para esta geometría, que es exactamente lo que
hace que valga la pena construirlo: puedes contrastar la simulación con algo.

## 2. Las ecuaciones

Tres ideas y el modelo está completo. Derivado desde el problema hacia abajo
—para qué sirve esto, de dónde salió Monte Carlo, las estimaciones de orden de
magnitud, y dónde se acaba todo— en [`docs/physics.md`](docs/physics.md).

**Emisión dentro de un cono.** El elemento de ángulo sólido es
$d\Omega = \sin\theta\thinspace d\theta\thinspace d\phi$, así que la variable
plana es el coseno, no el ángulo:

$$p(\theta)\thinspace d\theta = \sin\theta\thinspace d\theta
\quad\Longleftrightarrow\quad
p(\cos\theta)\thinspace d(\cos\theta) = d(\cos\theta)$$

**El camino libre.** La probabilidad de que un fotón sobreviva una distancia $s$
cae exponencialmente, así que la distancia hasta su siguiente interacción se
muestrea invirtiendo eso:

$$p(s) = \mu\thinspace e^{-\mu s}
\qquad\Longrightarrow\qquad
s = -\frac{\ln U}{\mu}, \quad U \sim \mathcal{U}(0,1]$$

**La geometría.** Un fotón con ángulo $\theta$ atraviesa una lámina de espesor
$L$ a lo largo de un camino de longitud $L/\cos\theta$. Ese único factor es toda
la dependencia angular, y juntas las tres dan la forma cerrada:

$$\boxed{\enspace T = \exp\negthinspace\left(-\frac{\mu L}{\cos\theta}\right)\enspace}$$

Beer–Lambert. Promediada sobre el cono se convierte en una integral exponencial
sin forma elemental, evaluada por cuadratura en
[`cone_transmittance()`](physics.py) con una precisión muy por encima de
cualquier tirada de Monte Carlo — que es lo que la hace una referencia y no una
segunda opinión.

Nótese que $\mu$ y $L$ nunca aparecen por separado. **Hay una sola escala de
longitud, el camino libre medio $1/\mu$**, y todo resultado es función
únicamente de la profundidad óptica $\mu L$.

## 3. Qué implementé

```
physics.sample_direction()    uniform over solid angle, not over the angle
physics.sample_free_path()    inverse transform of the exponential
physics.slab_path()           L / cos(theta)
physics.transmittance()       Beer-Lambert
physics.cone_transmittance()  the same, averaged over the cone by quadrature
physics.check_medium/cone()   passive media, and cones that stay under 90 degrees
methods.analog                sample a free path; count survivors
methods.weighted              never absorb; carry exp(-mu * path)
solve.transmitted()           mean, standard error, photon count, method
```

## 4. Qué verifiqué

56 tests, en tres grupos. Fíjate en lo que *no* está en el contrato: la
varianza. Exigir una varianza común afirmaría algo falso, y exigir que no la
haya dejaría fuera al estimador honesto.

| Propiedad | Alcance |
|---|---|
| **Beer–Lambert con incidencia normal, para varios μ y L** | dominio |
| μ y L solo aparecen como su producto | dominio |
| Un fotón inclinado atraviesa exactamente 1/cos θ más material | dominio |
| Un cono colimado se reduce exactamente a Beer–Lambert | dominio |
| Abrir el cono solo puede bajar la transmisión | dominio |
| El promedio del cono queda acotado entre su rayo axial y el más inclinado | dominio |
| **Las direcciones son uniformes en ángulo sólido, no en el ángulo** | dominio |
| Los caminos libres son exponenciales — comprobado sobre la función de supervivencia, no sobre la media | dominio |
| Un camino libre nunca es infinito | dominio |
| Se rechazan los medios con ganancia, los espesores negativos, los conos de 90° y los rayos rasantes | dominio |
| **Ambos estimadores caen dentro de 4σ de la forma cerrada, en 5 geometrías** | contrato |
| Las láminas transparentes y las de espesor cero transmiten exactamente 1 | contrato |
| Las contribuciones son probabilidades, en [0, 1] | contrato |
| El error cae como 1/√N | contrato |
| Una tirada es reproducible a partir de su semilla | contrato |
| **El analógico reporta un bit por fotón; el ponderado, un continuo** | divergen |
| **La varianza analógica es binomial T(1−T) e ignora el cono** | divergen |
| **Estrechar el cono ensancha la brecha sin límite** | divergen |
| **Un haz colimado hace exacto al estimador ponderado** | divergen |
| **El ponderado iguala la barra de error del analógico con menos del 2% de los fotones** | divergen |

La fila que paga la entrada es la primera de contrato. Contrastar dos
estimadores entre sí prueba que coinciden; contrastarlos con Beer–Lambert prueba
que son correctos. Ambos se contrastaron con la forma cerrada *antes* de
contrastarse entre sí.

### Los experimentos

**[`beer_lambert.py`](experiments/beer_lambert.py)** — predicción: una recta en
un eje logarítmico para un haz colimado, que se curva conforme el cono se abre.
A ninguno de los estimadores se le dice la ley.

```
--- 45 degree cone ---
   thickness    analytic                 analog               weighted
        1.00    0.308413      0.306910+-0.00146      0.308490+-0.00011
        3.00    0.030532      0.031040+-0.00055      0.030548+-0.00003
        5.00    0.003171      0.003350+-0.00018      0.003169+-0.00001
```

Una nota metodológica que vale más que la gráfica. La primera versión usaba una
sola semilla para todos los puntos del barrido, lo que reutiliza los mismos
caminos libres, tira de todos los puntos en la misma dirección y convierte una
dispersión honesta de 1σ en algo que se lee como un sesgo sistemático — la
columna analógica quedaba por encima de la teoría en *todos* los espesores. Las
barras de error eran correctas en todo momento; solo el ojo se dejó engañar.
Ahora la semilla varía en cada punto.

**[`variance.py`](experiments/variance.py)** — predicción: la brecha crece sin
límite conforme el cono se estrecha, y la varianza analógica no se mueve nada.

```
   cone          T   binomial T(1-T)    analog var    weighted var        ratio
    45d   0.308413          0.213294      0.213201       1.298e-03    1.643e+02
    15d   0.361540          0.230829      0.230730       1.355e-05    1.703e+04
     5d   0.367179          0.232358      0.232242       1.639e-07    1.417e+06
     1d   0.367851          0.232537      0.232422       2.617e-10    8.882e+08

to match the analog error bar of 0.000730 at 400000 photons,
  a 45-degree cone needs    2435 weighted photons (   164x fewer)
  a 15-degree cone needs      24 weighted photons ( 16666x fewer)
  a  5-degree cone needs       2 weighted photons (200000x fewer)
```

La varianza analógica es $T(1-T)$ hasta la cuarta cifra decimal en todos los
ángulos de cono — es el lanzamiento de una moneda y nada de la geometría le
llega. La varianza ponderada cae aproximadamente como $\alpha^4$, porque la
única aleatoriedad que queda es la dispersión de las longitudes de camino a lo
ancho del cono, y esa dispersión escala como $1-\cos\alpha \sim \alpha^2$.

**[`radiograph.py`](experiments/radiograph.py)** — el mismo argumento, como
imagen. Una esfera con dos inclusiones más densas, 120 fotones por píxel, ambos
estimadores.

```
   estimator   RMS error vs exact   worst pixel
      analog             0.027925      0.170133
    weighted             0.000000      0.000000
```

Presupuesto de fotones idéntico, y una imagen sale granulada mientras la otra es
exacta. Por eso también importa la dosis en una radiografía real: el ruido es la
estadística de conteo de los fotones que el paciente absorbió, y la única manera
analógica de reducirlo a la mitad es cuadruplicar la exposición.

## 5. Qué dejé fuera deliberadamente

- **Dispersión.** Aquí cada fotón viaja en línea recta hasta que se absorbe. La
  dispersión Compton domina a energías diagnósticas y convierte el camino en un
  paseo aleatorio, que es lo que hace difícil el transporte real — y lo que
  elimina el atajo del estimador ponderado.
- **Energía.** Monocromático de principio a fin. El μ real depende fuertemente
  de la energía, y el endurecimiento del haz — el espectro desplazándose
  conforme la parte blanda se absorbe primero — es un efecto de primer orden en
  radiografía.
- **Los canales de interacción.** Fotoeléctrico, Rayleigh, Compton y producción
  de pares son aquí un único coeficiente de atenuación. La versión de 2024 tenía
  esbozos de los cuatro; véase abajo.
- **Reconstrucción.** Esto proyecta. Recuperar el objeto a partir de las
  proyecciones es tomografía, y es otra entrada.
- **Física del detector.** Conteo perfecto, sin eficiencia, sin desenfoque, sin
  crosstalk entre píxeles.
- **Ray tracing en el sentido gráfico.** Sin reflexión, refracción ni sombreado.
  Nunca fue eso.

## Dónde esto deja de ser correcto

| Frontera | Qué pasa |
|---|---|
| Dispersión | Los caminos rectos son incorrectos, y el estimador ponderado pierde su camino analítico |
| Espectros anchos | Un solo μ no puede representar el endurecimiento del haz; la transmisión no es exponencial en L |
| Cono acercándose a 90° | El camino en la lámina diverge; se rechaza en vez de aproximarse |
| Láminas muy gruesas | El estimador analógico devuelve casi solo ceros y su error relativo se dispara |
| Un estimador de varianza cero | «Dentro de 3σ» pierde todo sentido — véase abajo |
| Profundidad óptica grande con ponderación | Los pesos hacen underflow hasta cero mucho antes de que lo hiciera el conteo analógico |

**La trampa de σ merece su propia línea**, porque mordió durante el desarrollo.
El estimador ponderado sobre un haz colimado da a cada fotón la misma
contribución, así que su error estándar es ruido de coma flotante y no una
dispersión. Dividir por él convirtió una diferencia de 0.2 ulp en **447 σ**.
Cuanto mejor es el estimador, más frágil se vuelve una comprobación de «dentro
de tres sigmas», y `Estimate.sigma_from` ahora acota por abajo el denominador a
lo que la aritmética puede resolver.

## Procedencia: la versión de 2024

Original: `Iter_rad_material/rayosnew.py` y `unfoton.py`, más un notebook. La
física era correcta — muestreo en coseno, el camino libre exponencial, y un
camino en la lámina calculado como la distancia 3D entre los puntos de entrada y
salida, que es $L/\cos\theta$ dando un rodeo. Lo que cambió la reescritura:

| | 2024 | ahora |
|---|---|---|
| Incertidumbre | `len(passed)/Nphoto`, y nada más | media ± error estándar, siempre |
| Verdad de referencia | ninguna; la simulación nunca se contrastó con una ley | cada estimador anclado antes que nada a Beer–Lambert |
| Estimador | solo el analógico | dos, tras un contrato, con la brecha de varianza medida |
| Reproducibilidad | `np.random` pelado, sin semilla | un `rng` explícito, con semilla por tirada |
| `log(rand())` | `rand()` puede devolver 0.0, dando un camino infinito | muestrea en (0, 1] para que la singularidad sea inalcanzable |
| Ángulo del cono | `maxtheta` por defecto y nunca propagado, así que no se podía cambiar | un parámetro en todas partes |
| Bucle | bucle de Python sobre los fotones, recalculando las coordenadas dos veces por fotón | vectorizado sobre todo el lote |
| Trabajo sin terminar | `fotoelectrico`, `comtom` y `pares` son `pass`; `raileight` vuelve a muestrear el mismo cono y no es Rayleigh | dispersión declarada fuera de alcance en su lugar |
| Tests | ninguno | 56 |

Las dos primeras filas son las que importan. **Un resultado de Monte Carlo sin
barra de error no es una medida** — no hay forma de saber si un desacuerdo con
la teoría es un bug o el tamaño de la muestra. Y una simulación que nunca se
contrasta con una forma cerrada solo se contrasta con tus expectativas, que es
justo lo único que se suponía que debía poner a prueba.

## Ejecútalo

```bash
uv run pytest photon-transport                            # 56 tests
uv run python photon-transport/experiments/beer_lambert.py
uv run python photon-transport/experiments/variance.py
uv run python photon-transport/experiments/radiograph.py
```

## Qué prepara esto

La mitad Monte Carlo del repositorio. [`hopfield/`](../hopfield/) muestrea un
paisaje a temperatura cero y [`mlp/`](../mlp/) desciende por uno; esta estima
una integral lanzándole dardos, y paga el $1/\sqrt{N}$ que eso conlleva. Añade
dispersión y se convierte en un paseo aleatorio, que es la misma matemática que
la difusión — y lo siguiente que vale la pena construir.
