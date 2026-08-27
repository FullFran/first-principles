<!-- translated-from: 749d577b361d -->

# Renormalización

Aléjate. Si el sistema se parece a sí mismo con un parámetro distinto, tienes
un mapa, y el punto crítico es donde ese mapa se queda quieto. En percolación
el cálculo entero es un polinomio — y para un bloque de dos es
$2p^2 - p^4$, cuyo punto fijo es la razón áurea. 419 líneas de núcleo.

| | |
|---|---|
| **Nivel** | L1 derivar · L2 implementar · L3 experimentar |
| **Dominio** | [`flow.py`](flow.py) — 190 líneas, sin barrido de tamaño de bloque dentro |
| **Métodos** | [`enumeration.py`](methods/enumeration.py) 25 · [`sampling.py`](methods/sampling.py) 38 |
| **Tests** | 71, divididos en dominio, contrato y donde los métodos divergen |
| **Actúa sobre** | [`forest-fire/`](../forest-fire/), que es de donde sale el umbral |

## Estructura

```
flow.py               the domain: the block rule, the map, its fixed points
methods/
  enumeration.py      count every configuration — exact, and stops at b = 4
  sampling.py         count a sample at fixed occupancy — error bars, no ceiling
solve.py              the plain scheme, and the cell-to-cell one
experiments/
  convergence.py      does a bigger block give a better answer? (half of one)
  noise.py            what the sampler's error bars actually are
                      figures go to experiments/out/ until a derivation uses them
tests/
  test_flow.py            domain laws, no scheme chosen
  test_methods.py         the contract, run against both
  test_methods_differ.py  where they legitimately disagree
```

La misma regla de dependencias que en todo este repositorio: **`methods/` importa `flow`,
`flow` no importa a nadie.** Véase [`docs/architecture.md`](../docs/architecture.md).

## 1. Qué problema resuelve

[`forest-fire/`](../forest-fire/) tiene un umbral: por debajo de una densidad de
árboles de $p_c = 0.5927460$ un fuego no puede cruzar la red, por encima sí. El
número está medido, y quedan dos preguntas.

**¿Por qué es ese número?** Y, mucho más extraño, **¿por qué sistemas que no
tienen nada en común comparten los mismos exponentes críticos?** Un imán, un
líquido en su punto crítico y una red percolante tienen constituyentes
distintos, interacciones distintas y física distinta, y sus exponentes coinciden.

La respuesta a las dos es una sola idea: engrosa la escala, y mira qué sobrevive.

## 2. Las ecuaciones

Agrupa la red en bloques de $b \times b$ sitios y pregunta cuándo un bloque
cuenta como ocupado en la escala gruesa. La conexión es lo que tiene que
sobrevivir — un bloque lleno de sitios desconectados no conduce — así que el
criterio es que percole.

Entonces la densidad gruesa es un polinomio en la fina:

$$R(p) = \sum_k N_k\thinspace p^k (1-p)^{b^2 - k}$$

con $N_k$ el número de configuraciones percolantes que tienen $k$ sitios
ocupados. Ese es el grupo de renormalización entero para este problema: **un
polinomio.**

Para $b = 2$ con una regla de arriba abajo es lo bastante pequeño para hacerlo
en papel — $R(p) = 2p^2 - p^4$ — y $R(p^{\ast}) = p^{\ast}$ se factoriza como
$(p-1)(p^2 + p - 1) = 0$, lo que da

$$p^{\ast} = \frac{\sqrt5 - 1}{2} = 0.618034$$

la razón áurea, a un 4.3% del umbral verdadero.

**El punto fijo es inestable**, y eso es lo importante. Por debajo, el engrosado
de escala repetido lleva la densidad a cero y el sistema parece vacío a escalas
grandes; por encima, a uno. Solo exactamente sobre él el sistema se ve igual a
todas las escalas, que es lo que significa la invariancia de escala en un punto
crítico.

El exponente sale de la pendiente. Un paso multiplica la distancia al punto fijo
por $\lambda = dR/dp$ mientras divide las longitudes entre $b$, así que si
$\xi \sim |p - p^{\ast}|^{-\nu}$ entonces

$$\nu = \frac{\ln b}{\ln \lambda}$$

**Un exponente a partir de una derivada.** Nada de la red microscópica sobrevive
hasta él — eso es la universalidad, y este es el mecanismo que hay detrás.

## 3. Qué implementé

```
flow.P_C, flow.NU         the two numbers to be checked against
flow.spans()              when a coarse block counts as occupied — three rules
flow.block_polynomial()   the spanning counts, by exhaustive enumeration
flow.recursion()          the counts turned into the map R(p)
flow.fixed_point()        where R(p) = p, other than 0 and 1
flow.slope(), exponent()  dR/dp, and nu = ln(b)/ln(lambda)
methods.enumeration       exact, 2^(b*b) work
methods.sampling          at fixed occupancy, with a binomial coefficient
solve.scheme()            block to site
solve.cell_to_cell()      block to block, which is the one that works
```

## 4. Qué verifiqué

71 tests, en tres grupos. Fíjate en lo que *no* está en el contrato: acertar la
respuesta. Un esquema de renormalización es una **elección**, y elecciones
distintas aterrizan en sitios distintos — que es la entrada, no un defecto.

| Propiedad | Alcance |
|---|---|
| **El mapa vertical 2×2 es exactamente $2p^2 - p^4$** | dominio |
| **Su punto fijo es exactamente la razón áurea** | dominio |
| $R(0) = 0$ y $R(1) = 1$ — los dos puntos fijos triviales | dominio |
| El mapa es creciente: más árboles no pueden conducir menos | dominio |
| **El punto fijo es inestable, para toda regla y todo bloque** | dominio |
| El flujo se aleja de él en ambas direcciones | dominio |
| Lo que cuenta es la conexión, no cuántos sitios | dominio |
| Un punto fijo estable no tiene exponente | dominio |
| Los bloques vacío y lleno se cuentan exactamente | contrato |
| Un bloque no puede percolar con menos sitios que un lado | contrato |
| Hay un punto fijo inestable, y un exponente | contrato |
| **El de celda a celda le gana al esquema simple** | contrato |
| **Una opción mal escrita se rechaza en vez de ignorarse** | contrato |
| Una opción que solo entiende el *otro* método se sigue aceptando | contrato |
| **Los dos métodos de conteo coinciden allí donde ambos pueden ejecutarse** | divergen |
| **La enumeración rechaza un bloque que no puede terminar** | divergen |
| **El muestreo sigue adelante donde la enumeración se para** | divergen |
| **El esquema simple se queda atascado con la regla vertical** | divergen |
| **`either` y `both` acotan el umbral verdadero** | divergen |

**Las dos filas sobre opciones existen por un fallo que escribí yo usando esta
entrada.** Cada método termina su firma en `**_` a propósito: `solve` le pasa
las mismas opciones al método que se haya elegido, así que una misma llamada
puede apuntar a cualquiera de los dos y `enumeration` ignora `draws` sin
quejarse. Esa tolerancia es lo que hace que una sola suite de contrato se pueda
escribir contra ambos.

También significaba que una palabra clave mal escrita no llegaba a ninguna
parte:

```
scheme(3, "either", counting="sampling", draws=500, seed=0) -> 0.472628
scheme(3, "either", method="sampling",   draws=500, seed=0) -> 0.476323
scheme(3, "either")                                         -> 0.472628
```

El parámetro se llama `method`. Escrito `counting` caía en `**options`, no
llegaba a ninguna parte, y la llamada enumeraba en silencio — la tercera línea,
que es el valor por defecto — con la misma pinta que la segunda. Sin error, sin
aviso, un número perfectamente plausible para una pregunta que nadie hizo. Peor
aún: `drwas=500` se tragaba igual y usaba en silencio las 4000 tiradas por
defecto, así que un experimento que midiera *el error de muestreo frente al
tamaño de la muestra* no habría medido nada y lo habría dicho con toda
confianza.

El arreglo no es "rechazar lo que este método ignora" — eso rompería la
tolerancia de la que depende la arquitectura. La línea va un paso más afuera:
`solve` reúne las palabras clave que acepta **algún** método registrado y
rechaza todo lo que quede fuera de esa unión. Una opción que algún método
entiende puede ser ignorada por otro; una opción que ningún método entiende es
un error.

### El experimento

**[`convergence.py`](experiments/convergence.py)** — predicción, escrita antes:
agrandar el bloque mejora la respuesta, y el esquema simple converge a $p_c$ y
$\nu = 4/3$.

**Medio acierto, y la mitad equivocada es la interesante.**

```
1. THE PLAIN SCHEME
       rule   b         p*    error        nu    error
   vertical   2   0.618034     4.3%    1.6353    22.6%
   vertical   3   0.619260     4.5%    1.6245    21.8%
   vertical   4   0.619355     4.5%    1.6067    20.5%

     either   2   0.381966    35.6%    1.6353    22.6%
     either   3   0.472628    20.3%    1.5113    13.3%
     either   4   0.509355    14.1%    1.4853    11.4%
```

Con la regla vertical **el tamaño del bloque no hace nada** — 0.618, 0.619,
0.619. No converge despacio, se queda quieto. Pedir solo un camino de arriba
abajo es un criterio sesgado, y un bloque más grande no cura un sesgo.

Con `either` sí mejora, y lo llamativo es que `either` y `both` **acotan el
valor verdadero desde lados opuestos**: en $b = 4$ dan 0.509 y 0.708,
cerrándose sobre 0.5927 por debajo y por arriba. Dos esquemas que discrepan
valen más que uno que da la casualidad de que está cerca.

```
2. CELL TO CELL:  R_small(p) = R_large(p)  instead of  R(p) = p
       rule   blocks         p*    error        nu    error
     either      2,3   0.559599     5.6%    1.2791     4.1%
     either      3,4   0.591046     0.3%    1.3758     3.2%
     either      2,4   0.574132     3.1%    1.3161     1.3%
```

**0.591046 frente a un verdadero 0.5927460 — tres partes en mil**, a partir de
bloques de como mucho dieciséis sitios, y el exponente al 1.3%. Comparar dos
*bloques* en vez de un bloque contra un *sitio* cancela casi todo lo que la
regla de bloque hace mal, porque entonces los dos lados de la comparación son el
mismo tipo de objeto.

El esquema simple estaba comparando un bloque con un solo sitio y llamándolos la
misma cosa. No lo son, y por mucho que agrandes el bloque no lo serán.

**[`noise.py`](experiments/noise.py)** — la tabla de arriba dice que el muestreo
cuesta barras de error. Esto las mide, y las dos predicciones escritas antes de
correr nada eran deliberadamente de distinta naturaleza.

La primera es Monte Carlo del montón: la *dispersión* cae como
$1/\sqrt{\text{draws}}$, así que cuadruplicar las tiradas la reduce a la mitad.
La segunda no lo es: el punto fijo no es un promedio, es la **raíz** de
$R(p) = p$, y la raíz de un estimador insesgado no es un estimador insesgado de
la raíz. Desarrollando alrededor del punto verdadero, el desplazamiento de
primer orden se promedia a cero y lo que queda es de segundo orden — así que
debería haber también un *sesgo*, yendo como $1/\text{draws}$ en vez de como
$1/\sqrt{\text{draws}}$. El sesgo es mayor donde menos tiradas hay, y ahí es
donde se gastaron las semillas.

```
PLAIN B=3   exact fixed point 0.472628
  draws  seeds       mean   scatter  halving       bias  in SEM
    500     48   0.473681  0.006506       --  +0.001053     1.1
   2000     12   0.473578  0.003706     1.76  +0.000950     0.9
   8000     12   0.472463  0.002141     1.73  -0.000165    -0.3

CELL 3->4   exact fixed point 0.591046
  draws  seeds       mean   scatter  halving       bias  in SEM
    500     48   0.587668  0.020851       --  -0.003378    -1.1
   2000     12   0.586239  0.012956     1.61  -0.004806    -1.3
   8000     12   0.589753  0.005025     2.58  -0.001293    -0.9
```

**La primera predicción se cumple y la segunda no se puede medir, que es lo que
ella misma predijo sobre sí misma.** Las razones de dispersión son 1.76, 1.73,
1.61 y 2.58 frente al 2.00 que exige $1/\sqrt{4}$ — repartidas a su alrededor,
y una dispersión estimada con doce semillas es buena solo a un veinte por
ciento — eso es $1/\sqrt{2(n-1)}$, y es la dispersión y no la varianza — así que
un cociente de dos de ellas lo es a un treinta.

El sesgo nunca supera 1.3 errores estándar de su propia media, en ninguna fila,
para ninguno de los dos esquemas. **Eso no es una medida de un sesgo. Es una
incapacidad de distinguirlo de cero**, y dar el $+0.001053$ como si fuera un
número sería leer ruido. Lo que sí compra la ejecución es una cota: a 500
tiradas el sesgo del esquema simple está por debajo de unos 0.003 a dos sigmas,
frente a una dispersión de 0.0065 con esa misma muestra. Más pequeño que el
ruido, exactamente como decía la segunda predicción — y decía que ser más
pequeño que el ruido es justo lo que lo hace difícil de ver.

Por esto merece la pena correr la escalera en vez de un solo trabajo largo a
8000 tiradas. **Un único tamaño de muestra no puede distinguir un sesgo de una
dispersión**; solo verlos caer a ritmos distintos puede, y aquí uno de los dos
se negó a asomar por encima del suelo.

## 5. Qué dejé fuera deliberadamente

- **Renormalización en el espacio de momentos.** El método que Wilson usaba
  realmente, la expansión épsilon, y todo aquello por lo que en 1982 se dio el
  Nobel. En espacio real sobre percolación es la versión que puedes hacer a
  mano, y es un primo suyo, no la cosa en sí.
- **El modelo de Ising.** La renormalización por espín de bloque sobre Ising es
  el ejemplo resuelto canónico y necesita una constante de acoplamiento en vez
  de una probabilidad, así que el mapa es bidimensional y el flujo tiene
  direcciones.
- **Operadores relevantes e irrelevantes.** Con un parámetro hay un autovalor y
  no hay sitio para la clasificación que explica la universalidad como es
  debido.
- **Todos los demás exponentes.** $\beta$, $\gamma$, $\eta$ y las relaciones de
  escala entre ellos. $\nu$ es el que el flujo da directamente.
- **Bloques más grandes.** El muestreador llega a $b = 6$ y más allá; la entrada
  se para en 4 porque ahí es donde la enumeración todavía puede comprobarlo.

## Dónde esto deja de ser cierto

| Frontera | Qué pasa |
|---|---|
| **El esquema simple con una regla sesgada** | No converge en absoluto — 0.618, 0.619, 0.619 |
| Un bloque mapeado a un sitio | Compara dos objetos distintos; el de celda a celda existe por eso |
| Enumeración más allá de $b = 4$ | 2^25 configuraciones; rechaza en vez de colgarse |
| Muestreo | Barras de error en cada coeficiente, y ninguna respuesta exacta — la dispersión cae como $1/\sqrt{\text{draws}}$ y el sesgo se queda por debajo del suelo de ruido, ambos [medidos](experiments/noise.py) |
| Un solo parámetro | Los flujos reales son multidimensionales; esto no puede ver una dirección irrelevante |
| El exponente | Más difícil que el umbral, y el número que de verdad pone a prueba el esquema |

**La fila del exponente es la honesta.** Un punto fijo puede caer cerca de $p_c$
por razones poco interesantes — es un número en el intervalo unidad. $\nu$ sale
de la *derivada* en ese punto y es mucho más difícil de acertar por accidente,
que es por lo que la tabla de arriba reporta los dos y por lo que el esquema
simple se ve mucho peor en la segunda columna que en la primera.

## Ejecútalo

```bash
uv run pytest renormalisation                                # 71 tests, ~1 min
uv run python renormalisation/experiments/convergence.py     # ~60 s
uv run python renormalisation/experiments/noise.py           # ~8 min
```

## Qué prepara esto

Difusión, y no por analogía. El proceso directo de un modelo de difusión
destruye estructura poco a poco, y su proceso inverso la reconstruye — que es un
flujo en el espacio de distribuciones con un punto fijo en el ruido puro. El
vocabulario de aquí es el vocabulario de allí: engrosado de escala, un flujo,
qué sobrevive a él y qué no.

La única pieza que todavía falta para esa entrada es aprender un score en vez de
derivarlo, y [`mlp/`](../mlp/) ya sabe aprender una función a partir de sus
gradientes.
