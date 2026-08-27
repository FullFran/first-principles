<!-- translated-from: 11e0377df7b0 -->

# Incendio forestal

Los árboles crecen, cae un rayo, el fuego se propaga a los árboles que se
tocan. Tres reglas y ningún ajuste, y el bosque se asienta por sí solo en la
densidad donde el fuego apenas logra atravesarlo. 220 líneas de núcleo.

| | |
|---|---|
| **Nivel** | L1 derivar · L2 implementar · L3 experimentar |
| **Dominio** | [`lattice.py`](lattice.py) — 133 líneas, sin bucle de pasos de tiempo dentro |
| **Métodos** | [`instantaneous.py`](methods/instantaneous.py) 23 · [`synchronous.py`](methods/synchronous.py) 52 |
| **Tests** | 46, repartidos entre dominio, contrato y donde los métodos divergen |
| **Trabajo relacionado mío** | [`fire-percolation`](https://github.com/FullFran/fire-percolation) — el mismo modelo tomado en serio, con registros reales de incendios españoles y un ajustador de leyes de potencias |

## Estructura

```
docs/lattice.md       the derivation, from the phenomenon down
docs/figures/         the figures it argues from — tracked, unlike out/
lattice.py            the domain: three states, growth, lightning, spreading
methods/
  instantaneous.py    the cluster burns before anything regrows
  synchronous.py      the fire advances one ring per step, and the forest grows
solve.py              the timestep loop, and one event per fire
experiments/
  percolation.py      the threshold, against p_c = 0.5927460
  ignition.py         fewer sparks, bigger fires — and the version that is false
tests/
  test_lattice.py         domain laws, no model run
  test_methods.py         the contract, run against both
  test_methods_differ.py  where they legitimately disagree
```

La misma regla de dependencias que en todo este repositorio: **`methods/`
importa `lattice`, `lattice` no importa a nadie.** Ver
[`docs/architecture.md`](../docs/architecture.md).

## 1. Qué problema resuelve

Un paisaje arde de vez en cuando. La mayoría de los incendios son pequeños,
unos pocos son enormes, y la distribución de tamaños es lo bastante ancha como
para que «el incendio medio» no sea una cantidad útil.

La pregunta no es cómo se propaga un incendio concreto — eso es meteorología.
Es **por qué la distribución tiene la forma que tiene**, y en particular por
qué un sistema que nadie ajustó habría de situarse exactamente en el punto
donde un incendio apenas logra atravesarlo.

## 2. Las ecuaciones

No hay ecuaciones, y eso es lo importante. Derivado desde el problema hacia
abajo — por qué ajustar un sistema a su punto crítico no explica nada, qué es
el umbral y dónde deja de ser cierto todo esto — en
[`docs/lattice.md`](docs/lattice.md). Hay tres reglas, aplicadas a cada sitio
en cada paso:

1. Un sitio en llamas queda vacío.
2. Un árbol junto a un sitio en llamas se prende.
3. Un sitio vacío hace crecer un árbol con probabilidad $p$; a un árbol lo
   alcanza un rayo con probabilidad $f$.

Todo lo demás es consecuencia. El único número que vale la pena memorizar es
el **umbral de percolación de sitio** en una red cuadrada,

$$p_c = 0.5927460$$

que es donde un bosque aleatorio conecta por primera vez un borde con el otro.
No tiene forma cerrada — se conoce numéricamente — y es contra lo que esta
entrada se verifica.

El régimen que hace interesante al modelo es $f \ll p \ll 1$: los incendios
deben terminar mucho antes de que el bosque vuelva a crecer. Eso no es un
detalle, es el modelo, y [`check_rates`](lattice.py) rechaza cualquier otra cosa.

## 3. Qué implementé

```
lattice.P_C            the percolation threshold, as a closed form to test against
lattice.grow()         empty sites become trees with probability p
lattice.strike()       which trees lightning hit — a mask, not an action
lattice.spread()       the four sites a fire reaches next
lattice.cluster()      every tree connected to a seed, by repeated spreading
lattice.spans()        does a group of trees reach from one edge to the other
methods.instantaneous  the cluster burns before anything regrows
methods.synchronous    one ring per step, with the forest growing
solve.run()            the loop, returning one Fire per fire
```

## 4. Qué verifiqué

46 tests, en tres grupos. Fíjate en lo que *no* está en el contrato: que un
incendio equivale al clúster que estaba en pie cuando empezó. Eso es cierto en
un método y falso en el otro, y esa diferencia es la entrada.

| Propiedad | Ámbito |
|---|---|
| **La percolación cruza ½ en p_c = 0.5927, y la transición se afila con L** | dominio |
| El fuego se propaga a cuatro vecinos y no en diagonal | dominio |
| Un clúster se detiene en un hueco; un sitio pelado no tiene ninguno | dominio |
| `strike` devuelve una máscara y no modifica la red | dominio |
| Se rechaza un rayo con tasa igual o superior a la de crecimiento | dominio |
| Un incendio consume árboles y no deja ningún sitio ardiendo | contrato |
| El bosque alcanza una densidad estacionaria | contrato |
| **Menos igniciones dan incendios más grandes, y un bosque más denso** | contrato |
| Cada incendio se reporta por separado, no uno por paso de tiempo | contrato |
| **Instantáneo: un incendio nunca puede exceder la red** | divergen |
| **Síncrono: un incendio puede quemar más que la red entera** | divergen |
| **Solo coinciden cuando el bosque crece despacio — y eso lo fija p, no f/p** | divergen |
| **Un bosque de crecimiento rápido vuelve endémico el fuego, y nunca se apaga** | divergen |

### Los experimentos

**[`percolation.py`](experiments/percolation.py)** — predicción: el cruce se
sitúa en $p_c$, y la transición se afila con la red.

```
       L   p where spanning crosses 1/2   width of the crossing
      16                         0.5867                  0.1367
      32                         0.5900                  0.0896
      64                         0.5917                  0.0625
     128                         0.5926                  0.0467
```

En L = 128 el cruce medido es 0.5926 frente al verdadero 0.5927460, y la
anchura se ha reducido a la mitad dos veces. Eso es un umbral, no una
tendencia: en una red infinita la curva sería un escalón.

**[`ignition.py`](experiments/ignition.py)** — la versión del modelo del
argumento de la supresión de incendios, ejecutada de dos maneras que discrepan.

```
        f      f/p  density   fires    mean  largest  of lattice
    2e-02  4.0e-01    0.244  242893     7.2      136        1.5%
    1e-03  2.0e-02    0.350   12689    88.6     2209       24.0%
    2e-04  4.0e-03    0.374    2640   409.8     5396       58.6%
    1e-05  2.0e-04    0.528     193  4224.5     9083       98.6%
```

**Reduce las chispas 2000× y el mayor incendio pasa del 1.5% del bosque al
98.6%** — el bosque entero. La densidad sube de 0.24 a 0.53, más allá de
$p_c$. Ese es el efecto, y es enorme.

Ahora la versión que todo el mundo dice en realidad, que es que apagar los
incendios pequeños deja que se acumule el combustible. Deja que los incendios
empiecen, luego extingue los que queden por debajo de un umbral de tamaño y
deja los árboles en pie:

```
 threshold   density    fires   largest  total burned
         0     0.398      953      7684       1385741
        10     0.397      643      7448       1388102
        50     0.396      484      7448       1388489
       200     0.395      402      7518       1391419
```

**No pasa nada.** La densidad no se mueve y el área total quemada no se mueve,
y hay una razón: en estado estacionario el área quemada por paso queda fijada
por el área crecida por paso. Extinguir un incendio no salva su combustible,
se lo entrega al siguiente.

Así que el mecanismo está en **cuándo empiezan los incendios**, no en si se
combaten una vez empezados. Ambas cosas se corresponden con la gestión real de
incendios, y no son la misma intervención — conviene saberlo antes de citar el
modelo frente a una política.

Una salvedad dicha en vez de enterrada: en las últimas filas de la primera
tabla el incendio cubre el 98.6% de la red, así que la medida está limitada
por la caja, no por la física. Esa saturación forma parte de una discusión viva
sobre si este modelo es crítico siquiera — ver más abajo.

## 5. Qué dejé fuera deliberadamente

- **El exponente de la ley de potencias.** Ajustar uno bien exige cuidado con
  `x_min`, la bondad del ajuste y los cortes de tamaño finito, y equivocarse es
  fácil e invisible. [`fire-percolation`](https://github.com/FullFran/fire-percolation)
  lo hace, y su `FINDINGS.md` es un buen relato de cómo sale mal.
- **El montón de arena.** Bak–Tang–Wiesenfeld es de donde viene la criticalidad
  autoorganizada y es un modelo distinto; merece su propia entrada en vez de
  una subsección aquí.
- **La renormalización.** La razón de que $p_c$ y los exponentes no dependan de
  los detalles microscópicos es el grupo de renormalización, y es la siguiente
  entrada natural en vez de un párrafo en esta.
- **Inmunidad, viento, combustible heterogéneo, envejecimiento de los árboles.**
  Todo real, todo extensiones estándar, ninguna necesaria para ver el fenómeno.
- **Registros reales de incendios.** También en `fire-percolation`, con
  cincuenta años de datos españoles.

## Dónde esto deja de ser cierto

| Frontera | Qué ocurre |
|---|---|
| **¿Es siquiera crítico?** | Grassberger (2002) y Pruessner & Jensen (2002) mostraron que el escalado está roto: no hay un único régimen de ley de potencias en ningún tamaño probado |
| Tasa de crecimiento por encima de ~0.1, síncrono | El fuego nunca se apaga — el rebrote alimenta el frente más rápido de lo que este quema |
| f no muy por debajo de p | Los dos métodos discrepan en un factor de siete o más |
| Redes grandes, f fijo | Los impactos por paso crecen como $fL^2$; varios incendios por paso rompen la separación de escalas de tiempo en silencio |
| El mayor incendio cerca del 100% | Limitado por la caja, no por la física |
| La supresión de incendios como afirmación de política | El modelo respalda la versión de la tasa de ignición y no la de apagarlos |
| Una red cuadrada con cuatro vecinos | $p_c$ es una propiedad de la red, no de los bosques |

La primera fila es el titular honesto. Este modelo es el ejemplo estándar de
libro de texto de criticalidad autoorganizada, y la mejor evidencia actual es
que **no es limpiamente crítico** — la aparente ley de potencias se descompone
bajo escrutinio. Eso es mejor saberlo que la versión ordenada.

## Ejecútalo

```bash
uv run pytest forest-fire                              # 46 tests
uv run python forest-fire/experiments/percolation.py   # ~40 s
uv run python forest-fire/experiments/ignition.py      # ~2 min
```

## Qué prepara esto

La renormalización. La razón de que $p_c$ sea lo que es, y la razón de que a
los exponentes críticos no les importe cuáles eran las reglas microscópicas,
es que el engrosado de escala de la red hace fluir los parámetros hacia un
punto fijo. En este modelo ese cálculo es lo bastante pequeño como para
hacerlo a mano: un bloque $2\times2$ da $R(p) = 2p^2 - p^4$, y
$R(p^{\ast}) = p^{\ast}$ tiene la solución
$p^{\ast} = (\sqrt5 - 1)/2 = 0.618$ — la proporción áurea, a un 4% del umbral
verdadero, salida de una cuártica.

Esa es la siguiente entrada, y esta es el objeto sobre el que actúa.
