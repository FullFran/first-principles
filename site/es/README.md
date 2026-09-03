<!-- translated-from: 73a7ef9ea4b1 -->

# first-principles

Implementaciones mínimas, reconstruidas desde las ecuaciones.

Cada entrada existe aquí para demostrar que entiendo un mecanismo — no para
competir con una biblioteca de producción. Si necesitas un solver de matriz de
transferencia, instala `tmm`. Si quieres ver si sé derivar uno, lee
[`tmm/physics.py`](tmm/physics.py).

Aquí es también donde mis repos didácticos dispersos vienen a ser reescritos.
Los notebooks de curso de 2023–2024 que nunca llegaron a ser legibles reciben
una versión honesta cada uno, o se quedan archivados donde están.

## Las reglas

1. **Una carpeta existe solo cuando L2 ya se ha alcanzado.** Sin marcadores de
   posición, sin READMEs vacíos esperando a que los rellenen. El mapa de abajo
   puede ser corto; no puede mentir.
2. **Nada llega por `git mv`.** El código migrado se reescribe al estándar o no
   entra.
3. **Los notebooks no son el núcleo.** Un `.ipynb` no admite diff ni tests, así
   que no puede sostener la afirmación «entiendo esto». Los notebooks son para
   explorar; el núcleo es un `.py`.
4. **El núcleo se mantiene en la banda de 100–500 líneas.** No es una ley — es
   una presión. Cuatro mil líneas para explicar DDPM significan que se construyó
   una biblioteca por accidente.
5. **Cada entrada declara lo que omite deliberadamente.** Saber dónde se detiene
   el modelo pedagógico es justo el objetivo.
6. **Este repo nunca es una dependencia.** Se lee, no se importa. Los proyectos
   reales reimplementan como es debido.
7. **El dominio no importa el método.** Las ecuaciones viven en un archivo que no
   conoce ningún algoritmo; los algoritmos viven a su lado y dependen de él,
   nunca al revés. Lo impone una suite de contrato que todo método debe pasar —
   sin eso, las carpetas son decoración.
   Escrito en [`docs/architecture.md`](docs/architecture.md), con dónde va la
   línea en los casos ambiguos y quién más hace esto.

## Mapa

| Tema | Derivar | Implementar | Experimentar | Origen |
|---|:---:|:---:|:---:|---|
| [Método de la matriz de transferencia](tmm/) | ✓ | ✓ | ✓ | `Physics-simulations/Cristal_multicapa` (2024) |
| [Red de Hopfield](hopfield/) | ✓ | ✓ | ✓ | `Optimization-Algorithms/4` (2024) |
| [Perceptrón multicapa](mlp/) | ✓ | ✓ | ✓ | `Point_classifier/redNumpy.ipynb` (2024) |
| [Transporte de fotones](photon-transport/) | ✓ | ✓ | ✓ | `Physics-simulations/Iter_rad_material` (2024) |
| [Muestreo de un paisaje de energía](sampling/) | ✓ | ✓ | ✓ | nuevo — el puente al que apuntan los otros tres |
| [Incendio forestal](forest-fire/) | ✓ | ✓ | ✓ | nuevo — hermano de [`fire-percolation`](https://github.com/FullFran/fire-percolation) |
| [Renormalización](renormalisation/) | ✓ | ✓ | ✓ | nuevo — actúa sobre `forest-fire/` |
| [Difusión](diffusion/) | ✓ | ✓ | ✓ | nuevo — donde convergen tres de las series de abajo |

**L1 derivar** — puedo reconstruirlo desde las ecuaciones.
**L2 implementar** — puedo escribir una versión mínima que funcione.
**L3 experimentar** — puedo modificarlo y predecir qué pasa.

Una fila recibe una marca solo cuando es cierta hoy, no cuando lo fue alguna vez.

## Series

El mapa está en el orden en que se construyeron las entradas y no dice nada
sobre qué lleva a qué. Estas sí.

**Monte Carlo** — estimar tirando dardos, y el $1/\sqrt{N}$ que cuesta
> [`photon-transport`](photon-transport/) → [`sampling`](sampling/)

**Paisajes de energía** — recordar, optimizar y muestrear son todos descenso
> [`hopfield`](hopfield/) → [`sampling`](sampling/) → [`diffusion`](diffusion/)

**Aprender una función** — gradientes, y qué haces una vez los tienes
> [`mlp`](mlp/) → [`diffusion`](diffusion/)

**Puntos críticos** — umbrales, y por qué los detalles dejan de importar ahí
> [`forest-fire`](forest-fire/) → [`renormalisation`](renormalisation/) → [`diffusion`](diffusion/)

**Ondas en la materia**
> [`tmm`](tmm/)

Fíjate en que `sampling` aparece dos veces y `diffusion` tres veces. **Esa es la
razón de que esto sea una vista y no un árbol de directorios.** Casi toda entrada
pertenece a dos o tres de estas — `hopfield` es una red neuronal, un vidrio de
espín y un optimizador; `photon-transport` es Monte Carlo y física de la
radiación — y una carpeta obliga a un único padre y esconde el resto. La conexión
que vale la pena mostrar suele ser la que cruza el árbol, no la que baja por él,
que es justamente la razón por la que las mismas matemáticas siguen apareciendo
en sitios sin relación.

Así que los directorios se quedan planos y una entrada puede estar en tantas
series como se gane. La regla 1 aplica también aquí: una serie puede ser corta, y
no puede mentir, así que todo lo que no está construido lo dice.

Todo esto es además una web, en inglés y en español:
**[www.fullfran.com/first-principles](https://www.fullfran.com/first-principles/)**.
Se genera a partir de estos archivos en lugar de escribirse junto a ellos — mira
[`site/`](site/) para saber por qué, y para saber qué pasa cuando una traducción
se queda atrás respecto del inglés del que se hizo.

Los textos que abarcan todo el repo viven en [`docs/`](docs/) — ahora mismo la
[separación física/numérica](docs/architecture.md). Todo lo específico de una
entrada vive dentro de ella, en su propio `docs/`: las derivaciones detrás de
[`tmm/`](tmm/docs/physics.md), [`hopfield/`](hopfield/docs/model.md),
[`mlp/`](mlp/docs/model.md),
[`photon-transport/`](photon-transport/docs/physics.md),
[`sampling/`](sampling/docs/distribution.md) y
[`forest-fire/`](forest-fire/docs/lattice.md) y
[`diffusion/`](diffusion/docs/process.md).

Todos ellos salvo [`tmm/`](tmm/docs/physics.md) llevan una sección de
historia, porque las personas que se atascaron con estos problemas son parte
de la explicación. Las afirmaciones
históricas se marcan **A** (documentada, idealmente primaria), **B** (una
reconstrucción) o **C** (contada en todas partes y sin fuente), siguiendo la
convención de
[*La servilleta y el ordenador*](https://github.com/FullFran/la-servilleta-y-el-ordenador).

## Anatomía de una entrada

```
tmm/
├── README.md        the five questions, derivation included
├── docs/            the long-form derivation, when the entry earns one
├── physics.py       the domain: the equations, and nothing that solves them
├── methods/         one file per algorithm, each importing the domain
├── solve.py         orchestration: validate, dispatch, convert
├── experiments/     things I ran and what they showed
├── tests/           domain laws, plus a contract every method must pass
└── conftest.py      the entry root on sys.path, so the folder stands alone
```

Una entrada lo bastante pequeña puede colapsar `methods/` en un solo archivo;
ninguna lo ha necesitado todavía. La regla que sobrevive en cualquiera de los dos casos es la dirección de la flecha: **las
ecuaciones nunca importan el algoritmo.** La recompensa es concreta — cambia el
algoritmo, y toda ley física tiene que seguir cumpliéndose. Si se cumple, has
separado lo que hace la naturaleza de cómo elegiste calcularlo. Si no, tenías
física escondida dentro de tu numérica y no lo sabías.

El README responde cinco preguntas en orden:

1. ¿Qué problema resuelve?
2. ¿Cuáles son las ecuaciones mínimas?
3. ¿Qué implementé?
4. ¿Qué verifiqué?
5. ¿Qué dejé fuera deliberadamente?

La pregunta 4 es la que separa esto de una carpeta de notebooks. Los tests
afirman propiedades — conservación de la energía, límites analíticos conocidos,
simetrías — no salidas guardadas. La pregunta 5 es la que los entrevistadores
leen de verdad.

Y una suite en verde nunca es un certificado. En `tmm/` se mantuvo verde mientras
dos clases enteras de entrada devolvían sinsentidos en silencio; las encontró el
sondeo, no el razonamiento. Cada entrada registra dónde deja de ser correcta.

## Backlog de migración

Auditado desde GitHub, decidido por contenido y no por nombre.

| Repo origen | Qué contiene | Decisión |
|---|---|---|
| [`Physics-simulations/Cristal_multicapa`](https://github.com/FullFran/Physics-simulations) | método de matrices, multicapa | **hecho** → [`tmm/`](tmm/) · fuente archivada |
| `Physics-simulations/Iter_rad_material` | `rayosnew.py`, `unfoton.py` — fotones a través de una lámina absorbente | **hecho** → [`photon-transport/`](photon-transport/) |
| `Physics-simulations/Magnetic Mirrors` | partícula cargada en un campo *uniforme* — `B = (0,0,10)`, seis EDOs bajo `odeint`, sin botella y sin espejo | **descartada** — el contraste que merecía construirse era RK4 frente a Boris, no el título |
| [`Optimization-Algorithms/4`](https://github.com/FullFran/Optimization-Algorithms) | `hopfiled.py`, Hopfield sobre fotos umbralizadas | **hecho** → [`hopfield/`](hopfield/) |
| [`Point_classifier`](https://github.com/FullFran/Point_classifier) | `redNumpy.ipynb`, red en NumPy puro | **hecho** → [`mlp/`](mlp/) · fuente archivada |
| `Tema-3-...alta-dimensionalidad` + `Optimization-Algorithms/3` | recocido simulado, genético, TSP — duplicado en dos repos | fusionar en una entrada |
| `minimalRandEM` | EM en medios aleatorios, MATLAB | abrirlo, y entonces decidir |
| `Physics-Informed-ML` | `Theory/` + `Examples/` | tomar la forma, no el contenido |
| `GPU-accelerated-Ising-Model` | `src/`, `tests/`, `pyproject.toml` | **se queda fuera** — proyecto real, no un boceto |
| `AI-Fundamentals` | app de Next.js | **se queda fuera** — no hay implementaciones dentro |
| `llm-from-scratch` | `clases/`, `examenes/`, `notas/` | bóveda de estudio; minar solo `experiments/` |
| `computational_photonics` | murió en `1_slab_waveguides` | nada que rescatar |

La migración solo termina cuando el repo origen está archivado en GitHub **y**
lleva un README que apunta aquí. Un repo archivado con código roto y sin señal es
una trampa, no un archivo. Si no, la cuenta de repos dispersos sube, no baja.

## Lo que no está aquí

Los proyectos de investigación que *consumen* este conocimiento viven en sus
propios repos y mantienen sus propios estándares — `snow-mcrt`,
`fire-percolation`, `corona26`, ForgePhoton. La relación es en un solo sentido:

```
first-principles  ──reads──▶  me  ──builds──▶  real projects
```

Nunca un import.

## Ejecutar

```bash
uv run pytest tmm                                  # one entry
uv run pytest hopfield
uv run pytest mlp
uv run pytest photon-transport
uv run pytest sampling
uv run pytest forest-fire
uv run pytest renormalisation
uv run pytest diffusion
./run-tests                                        # all of them, one process each
```

Una sesión por entrada, deliberadamente. Las entradas son autónomas, así que más
de una define `solve` y `methods`; pon dos a la vez en `sys.path` y el primer
import gana en silencio. Ejecutarlas por separado es el precio de poder copiar
una carpeta fuera y que funcione.
