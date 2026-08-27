<!-- translated-from: 07e85829d5f4 -->

# La memoria como paisaje

> La teoría detrás de [`hopfield/`](../README.md), derivada del problema y no
> de la fórmula. Lee esto si quieres saber *por qué* las ecuaciones de
> `hopfield/model.py` son esas y no otras.

Este documento sigue un ciclo, y el ciclo es lo que importa:

```
phenomenon → question → order of magnitude → assumptions → minimal model
   → equations → scale analysis → closed forms → simulation → validation
   → limits of the model → next question
```

La parte del medio es lo que enseña una carrera. Los dos extremos — plantear la
pregunta y saber dónde se detiene el modelo — son lo que de verdad separa a
quien resuelve problemas nuevos de quien aplica fórmulas. Así que aquí el
espacio se lo llevan los dos extremos.

**Contenidos**

1. [El fenómeno](#1-el-fenómeno)
2. [Para qué sirve la memoria asociativa](#2-para-qué-sirve-la-memoria-asociativa)
3. [Antes de calcular](#3-antes-de-calcular)
4. [Por qué falla la respuesta ingenua](#4-por-qué-falla-la-respuesta-ingenua)
5. [El modelo mínimo](#5-el-modelo-mínimo)
6. [Las ecuaciones](#6-las-ecuaciones)
7. [Dos esquemas, una energía](#7-dos-esquemas-una-energía)
8. [Análisis de escala: leer la respuesta en el crosstalk](#8-análisis-de-escala-leer-la-respuesta-en-el-crosstalk)
9. [Formas cerradas que vale la pena memorizar](#9-formas-cerradas-que-vale-la-pena-memorizar)
10. [Lo que mostró la simulación](#10-lo-que-mostró-la-simulación)
11. [Dónde el modelo deja de ser cierto](#11-dónde-el-modelo-deja-de-ser-cierto)
12. [Lo esencial](#12-lo-esencial)
13. [Preguntas abiertas](#13-preguntas-abiertas)
14. [Referencias](#14-referencias)

---

## 1. El fenómeno

Escuchas tres notas y llega la canción entera. Ves un cuarto de una cara al
otro lado de un bar y sabes quién es antes de saber que lo sabes. Alguien dice
"era esa película de... del barco" y cuarenta segundos después el título sale
a flote solo, sin que lo busques.

Nada de eso es como recuerda un ordenador. Un ordenador recuerda por
**dirección**: le entregas una clave, te devuelve un valor, y si la clave se
equivoca en un bit no obtienes nada. Lo que acabas de hacer es recordar por
**contenido**: el fragmento *es* la consulta, la consulta es una versión
corrupta de la respuesta, y la recuperación se degrada suavemente en vez de
fallar.

Ese es el fenómeno. Tiene tres propiedades que vale la pena nombrar porque un
modelo tiene que reproducir las tres:

- **Sin clave.** La sonda y el elemento almacenado viven en el mismo espacio.
- **Degradación gradual.** Medio patrón basta. Un cuarto, muchas veces también.
- **Sin búsqueda.** El tiempo de recuerdo no crece con cuánto sabes.

> **La pregunta.**
> $N$ unidades de dos estados. Hay que almacenar $P$ patrones
> $p^{1},\dots,p^{P}$, cada uno un vector en
> $\lbrace -1,+1\rbrace^{N}$. Más tarde llega una sonda corrupta.
> **¿Qué dinámica devuelve el patrón almacenado, cuán corrupta puede estar la
> sonda, y cuánto puede crecer $P$ antes de que todo deje de funcionar?**

Esas tres preguntas tienen tres respuestas distintas y son el contenido de este
documento. La última lleva un número pegado — $P \simeq 0.138\thinspace N$
— y el número es mucho más pequeño de lo que casi todo el mundo supone.

---

## 2. Para qué sirve la memoria asociativa

Vale la pena repasarlo antes de cualquier ecuación, porque las aplicaciones te
dicen qué régimen de las ecuaciones importa.

### 2.1 Un modelo de lo que un cerebro podría estar haciendo

Esta es la motivación original y sigue siendo la más fuerte. El artículo de
Hopfield de 1982 se titula *Neural networks and physical systems with emergent
collective computational abilities*, y la afirmación de ese título es toda la
idea: **una propiedad computacional — la memoria direccionable por contenido —
emergiendo de un sistema físico que nadie diseñó para tenerla.**

Las unidades no están almacenando nada. Ninguna neurona contiene "el gato". La
memoria es una propiedad de los *acoplamientos*, distribuida entre todos ellos,
y se recupera dejando que el sistema se relaje. Daña una fracción de las
unidades y la memoria se degrada en vez de desaparecer, que es lo que hace de
verdad la memoria biológica y lo que una tabla de consulta llamativamente no
hace.

El Premio Nobel de Física de 2024 fue para Hopfield y Hinton por esta línea de
trabajo — por usar herramientas de la física estadística para construir
máquinas que aprenden.

### 2.2 Optimización: cualquier función de coste es una energía

La dinámica de aquí minimiza $E(s) = -\tfrac12 s^{\mathsf T}Ws$. Dale la
vuelta: **dame un problema cuyo coste sea una forma cuadrática sobre variables
binarias y te construiré una red que lo desciende.** Esa es la construcción de
Hopfield–Tank (1985), que codificó el problema del viajante exactamente con
esta forma.

La historia honesta es que funcionó mal en el TSP — las restricciones hay que
colarlas como términos de penalización y la red encuentra alegremente
recorridos inválidos — pero la *idea* sobrevivió y ahora es enorme. La
optimización binaria cuadrática sin restricciones (QUBO) es el formato de
entrada de todo recocedor cuántico y de todo acelerador de máquina de Ising
construido en la última década. Todos están resolviendo el problema de este
documento, en hardware.

La conexión funciona también en el otro sentido, y es la dirección más útil:
esta red es un **vidrio de espín a temperatura cero**. Todo lo que la física de
los imanes desordenados sabe sobre paisajes accidentados — estados
metaestables, frustración, por qué ayuda el recocido — se transfiere
directamente.

### 2.3 Memoria direccionable por contenido en hardware

Los routers hacen esto de verdad, millones de veces por segundo. A una TCAM
(memoria ternaria direccionable por contenido) se le entrega una dirección de
destino y devuelve la entrada correspondiente de la tabla de rutas en un ciclo
de reloj comparando contra todas las palabras almacenadas en paralelo. Un
mecanismo completamente distinto — sin dinámica, sin energía — pero la misma
interfaz, y vale la pena saber que el problema de "buscar por contenido" tiene
una respuesta en silicio brutalmente directa que cuesta muchísima potencia.

### 2.4 Corrección de errores

Una palabra de código corrompida por el ruido, restaurada a la palabra de
código válida más cercana. Escrito así es el mismo problema, y la red de
Hopfield es un decodificador (malo): los patrones almacenados son las palabras
de código y las cuencas de atracción son las regiones de decodificación. Es
malo porque el almacenamiento hebbiano desperdicia la mayor parte de la
capacidad ([§8.6](#86-el-coste-de-un-acoplamiento)), que es precisamente por lo
que la teoría de códigos construye sus códigos algebraicamente. Útil como
comprobación de cordura sobre lo que "capacidad" debería significar.

### 2.5 El camino hacia todo lo que viene después

| Cambia una cosa | Y obtienes |
|---|---|
| $T = 0 \to T \gt 0$ | Máquina de Boltzmann — muestreo en vez de descenso |
| Unidades visibles $\to$ unidades ocultas | Máquinas de Boltzmann restringidas, redes de creencia profunda |
| $E$ cuadrática $\to$ $E$ de orden superior | Memoria asociativa densa: la capacidad crece como $N^{k-1}$ |
| Estados discretos $\to$ continuos | Hopfield 1984, y la capa Hopfield moderna |
| $E$ explícita $\to$ $\nabla \log p$ aprendido | Score matching, y luego los modelos de difusión |

La cuarta fila merece una pausa. Ramsauer et al. (2020) mostraron que una red
de Hopfield continua con una interacción exponencial tiene una regla de
actualización que **es** el mecanismo de atención de un transformer — un paso
de $\mathrm{softmax}(\beta QK^{\mathsf T})V$ es un paso de recuperación en una
memoria asociativa con exponencialmente muchos patrones almacenados. El título
de ese artículo, *Hopfield Networks is All You Need*, es una broma que resultó
ser aproximadamente cierta.

### Artículos que vale la pena leer

| Referencia | Por qué |
|---|---|
| [Hopfield, *PNAS* **79**, 2554 (1982)](https://www.pnas.org/doi/10.1073/pnas.79.8.2554) | El artículo. Energía, almacenamiento hebbiano, descenso asíncrono — nueve páginas |
| [Little, *Math. Biosci.* **19**, 101 (1974)](https://doi.org/10.1016/0025-5564(74)90031-5) | La versión síncrona, ocho años antes, y prácticamente sin leer |
| [Amit, Gutfreund & Sompolinsky, *PRL* **55**, 1530 (1985)](https://doi.org/10.1103/PhysRevLett.55.1530) | De dónde sale $\alpha_c = 0.138$. Teoría de réplicas, no conteo |
| [McEliece et al., *IEEE Trans. Inf. Theory* **33**, 461 (1987)](https://doi.org/10.1109/TIT.1987.1057328) | La otra capacidad, $N/(4\ln N)$, para *todos* los patrones exactamente |
| [Gardner, *J. Phys. A* **21**, 257 (1988)](https://doi.org/10.1088/0305-4470/21/1/030) | $\alpha_{\max} = 2$ para los mejores acoplamientos posibles. Hebb desperdicia el 93% |
| [Goles-Chacc, Fogelman-Soulié & Pellegrin, *Discrete Appl. Math.* **12**, 261 (1985)](https://doi.org/10.1016/0166-218X(85)90029-0) | Por qué las actualizaciones síncronas dan período 1 o 2 y nunca 3 |
| [Hopfield & Tank, *Biol. Cybern.* **52**, 141 (1985)](https://doi.org/10.1007/BF00339943) | Optimización como relajación. Instructivo en parte porque fracasó |
| [Krotov & Hopfield, *NeurIPS* (2016)](https://arxiv.org/abs/1606.01164) | Las energías de orden superior rompen el techo de $0.138\thinspace N$ |
| [Ramsauer et al., arXiv:2008.02217](https://arxiv.org/abs/2008.02217) | La capa Hopfield moderna es la atención |

Libros: Hertz, Krogh & Palmer, *Introduction to the Theory of Neural
Computation*, caps. 2–3 para la derivación más clara; Amit, *Modeling Brain
Function* para la mecánica estadística; MacKay, *Information Theory, Inference
and Learning Algorithms*, cap. 42 para la lectura teórico-informacional y la
mejor página suelta sobre por qué la capacidad es la que es.

### 2.6 Historia

Los niveles de verificación siguen la convención del libro: **A** es
documentado, idealmente desde una fuente primaria; **B** es una reconstrucción;
**C** es una historia que se cuenta en todas partes y que no he podido
documentar.

::: **Un físico que fue al congreso equivocado** · *Verificación: A — Hopfield
lo ha contado en varias entrevistas y el artículo de 1982 lo plantea así.*

John Hopfield no venía de la biología. Era un teórico de materia condensada:
había trabajado en Bell Labs, y en 1958 había introducido el **polaritón** — la
cuasipartícula que obtienes cuando la luz se acopla a una vibración de la red
con la fuerza suficiente para que ninguna de las dos siga siendo realmente ella
misma. Eso es más o menos lo más lejos de la neurociencia que llega una
carrera.

Lo que trajo consigo no fue una técnica sino un *reflejo*. Un físico que mira
un sistema grande de unidades que interactúan hace una pregunta concreta — ¿qué
magnitud minimiza esta cosa? — y esa pregunta no es natural para alguien
formado en neuronas. Los biólogos llevaban décadas construyendo modelos
neuronales. La función de energía es lo que un físico buscaría y nadie más.

El artículo de 1982 se titula *Neural networks and physical systems with
emergent collective computational abilities*, y la expresión que hace el
trabajo es **physical systems**. Es un argumento de que un cerebro puede
estudiarse igual que se estudia un imán.

::: **La idea ya estaba ahí, con la forma equivocada** · *Verificación: A.*

Tres cosas de esta historia vale la pena saberlas porque se repiten.

**El modelo síncrono llegó primero y no se llevó ningún crédito.** W. A. Little
publicó la versión de actualización en paralelo en 1974, con el argumento de
los estados persistentes incluido. La contribución de Hopfield en 1982 fue el
esquema asíncrono y la función de energía — que suena a detalle y es la
diferencia entera entre "esto a veces se asienta" y "esto se asienta
demostrablemente" ([§7](#7-dos-esquemas-una-energía)). La lección no es que a
Little le robaran; es que **la garantía fue la contribución**, y las garantías
son lo que sobrevive.

**La física se tomó prestada al por mayor.** Para 1982 la teoría de los vidrios
de espín — imanes desordenados con interacciones en competencia — era un campo
maduro, y el modelo de Hopfield es un vidrio de espín con una elección
particular de acoplamientos. Importarla significó que en tres años Amit,
Gutfreund y Sompolinsky pudieran calcular la capacidad exactamente usando
teoría de réplicas construida para un problema completamente distinto.
Reconocer que tu problema es el problema ya resuelto de otro vale más que la
mayor parte del trabajo original.

**Cuarenta y dos años hasta un Premio Nobel.** El premio de Física de 2024 fue
para Hopfield y Hinton, y el campo se declaró muerto al menos dos veces entre
medias — después de *Perceptrons* de Minsky y Papert en 1969, y otra vez a
finales de los ochenta, cuando las promesas adelantaron al hardware.

::: **Por qué fue realmente el premio** · *Verificación: A — el documento de
antecedentes científicos del comité Nobel.*

Vale la pena ser preciso sobre la mención de 2024, porque a menudo se cuenta
como un premio a la inteligencia artificial y no lo es. Es por **usar
herramientas de la física estadística para construir máquinas que aprenden** —
que es la dirección de marcha que documenta toda esta entrada. El propio
resumen del comité sobre la mitad de Hopfield es la función de energía y la
memoria asociativa de este documento; la de Hinton es la máquina de Boltzmann,
que es esa misma energía en $T \gt 0$.

Un premio de física por un resultado de informática, otorgado porque la física
era la parte estructural. Lo cual es o una vindicación o un error de categoría
según a quién preguntes, y vale la pena tener la discusión.

---

## 3. Antes de calcular

La regla del libro: **escribe un número antes de leer la siguiente sección.**
El aprendizaje está en la distancia entre tu número y el real, y esa distancia
no existe si no te comprometiste.

> 1. La entrada almacena letras de $24\times24$, así que $N = 576$ unidades.
>    **¿Cuántos patrones caben antes de que el recuerdo se rompa?** ¿Diez?
>    ¿Quinientos? ¿Medio millón?
> 2. Quieres almacenar así imágenes de un megapíxel, así que $N = 10^{6}$.
>    **¿Cuánta RAM ocupa $W$, y cuántas imágenes caben en ella?** Compáralo
>    con simplemente guardar las imágenes en una carpeta.
> 3. La red de $N = 576$ tiene $2^{576}$ estados y almacenaste cuatro patrones.
>    Toda ejecución termina en algún sitio. **¿En cuántos *otros* estados es
>    capaz de detenerse?** ¿En ninguno? ¿En un puñado? ¿En más que las
>    memorias?

Respuestas en [§8](#8-análisis-de-escala-leer-la-respuesta-en-el-crosstalk) y
[§10](#10-lo-que-mostró-la-simulación). Las tres son aritmética sobre una sola
fórmula. La tercera es la pregunta que la mayoría nunca ha pensado en hacer, y
es la que decide si puedes fiarte de una respuesta que te dé la red.

---

## 4. Por qué falla la respuesta ingenua

Aquí hay tres respuestas ingenuas, y fallan de formas cada vez más
interesantes. La tercera falla de forma tan sutil que todavía se cita como
correcta.

### 4.1 "Guarda una lista y compara contra ella"

Guarda los patrones en un array; ante una consulta, calcula la distancia a cada
uno y devuelve el más cercano. Esto funciona. Tampoco es un modelo de nada, y
falla las tres propiedades de [§1](#1-el-fenómeno) de una vez: el coste del
recuerdo crece linealmente en $P$, hay un lugar distinguido donde vive cada
memoria (así que el daño es catastrófico en vez de gradual), y no emerge nada
— implementaste la respuesta directamente.

Vale la pena decirlo explícitamente porque es la referencia a la que el modelo
tiene que *ganar en un eje distinto de la precisión*. La búsqueda del vecino
más cercano es estrictamente más precisa que una red de Hopfield. La afirmación
interesante es que un sistema sin búsqueda, sin índice y sin controlador
central pueda siquiera aproximarla.

### 4.2 "Superpón los patrones y confía"

La primera idea de verdad, y casi acierta. Escribe cada patrón en los mismos
acoplamientos sumándolos:

$$W = \frac{1}{N}\sum_{\mu=1}^{P} p^{\mu}\left(p^{\mu}\right)^{\mathsf T}$$

Ahora sondea con un patrón almacenado $p^{\nu}$ y mira el campo que tira de la
unidad $i$ ([§6.3](#63-hebb-no-se-elige-se-fuerza) lo hace bien):

$$h_i \thinspace p^{\nu}_i = \underbrace{1 - \frac{1}{N}}_{\text{signal}}
\thinspace + \underbrace{\frac{1}{N}\sum_{\mu\neq\nu}\thinspace p^{\mu}_i\thinspace p^{\nu}_i
\sum_{j\neq i} p^{\mu}_j p^{\nu}_j}_{\text{crosstalk}}$$

La señal es lo que querías. El crosstalk es cada una de las *otras* memorias
filtrándose en esta, y no desaparece — es una suma de $\sim PN$ signos
aleatorios, así que es pequeño pero no cero, y crece con $P$.

**Las memorias interfieren entre sí, y la interferencia es todo el tema.** Todo
lo que sigue a partir de aquí es una contabilidad de ese segundo término.

### 4.3 "Entonces calcula cuándo el crosstalk supera a la señal" — y esta es la sutil

El crosstalk tiene media cero y, tratando los signos como independientes,
desviación estándar $\sqrt{(P-1)/N} \simeq \sqrt{\alpha}$ donde
$\alpha \equiv P/N$. Verificado directamente:

| $N$ | $P$ | d.e. medida | $\sqrt{(P-1)/N}$ |
|---|---|---|---|
| 400 | 20 | 0.2106 | 0.2179 |
| 1000 | 50 | 0.2250 | 0.2214 |
| 2000 | 200 | 0.3295 | 0.3154 |

Una unidad es arrastrada en la dirección equivocada cuando el crosstalk es más
negativo que $-1$, lo que para una gaussiana ocurre con probabilidad

$$P_{\text{err}} = Q\negthinspace\left(\frac{1}{\sqrt{\alpha}}\right),
\qquad Q(x) = \tfrac12\thinspace\mathrm{erfc}\negthinspace\left(x/\sqrt2\right)$$

Exige $P_{\text{err}} \lt 0.01$ y obtienes $\alpha \lt 0.185$. Argumento
limpio, estadística honesta, y **la respuesta es incorrecta.** El techo real es
$\alpha_c = 0.138$.

Aquí está el porqué, medido en $N = 1000$, promediado sobre 12 conjuntos de
patrones, sondeando con un patrón almacenado y dejándolo relajar:

| $\alpha$ | error en un paso | $Q(1/\sqrt{\alpha})$ | error tras relajar |
|---|---|---|---|
| 0.05 | 0.0000 | 0.0000 | 0.0000 |
| 0.10 | 0.0009 | 0.0008 | 0.0014 |
| 0.138 | 0.0034 | 0.0036 | 0.0095 |
| 0.16 | 0.0049 | 0.0062 | **0.1064** |
| 0.20 | 0.0121 | 0.0127 | **0.2707** |
| 0.25 | 0.0212 | 0.0228 | 0.3334 |

![Error de recuerdo frente a carga. Los círculos huecos, medidos tras una sola
actualización, se sitúan sobre la curva analítica a lo largo de tres décadas.
La curva rellena, medida tras dejar relajar la red, se despega de ella justo
pasada la carga crítica.](figures/avalanche.png)

**Qué concluir:** la servilleta no es aproximadamente correcta; es
**exactamente correcta sobre la magnitud equivocada.** La columna dos coincide
con la columna tres hasta el tercer decimal a cualquier carga, y luego la
columna cuatro las deja a las dos atrás por un factor de veinte.

La física que falta es una **avalancha**. La estimación calcula la probabilidad
de que una unidad se voltee *dado que las demás unidades son todas correctas*.
Pero en cuanto unas pocas unidades se han volteado, son incorrectas, y una
unidad incorrecta contribuye al crosstalk de todas las demás con el signo
equivocado. Por encima de una carga crítica la realimentación se autosostiene y
el estado se desliza lejos de la memoria por completo. Por debajo, los errores
se corrigen en la siguiente pasada.

Eso es una **transición de fase**, hace falta autoconsistencia y no una sola
pasada para encontrarla, y localizarla exactamente es lo que hicieron Amit,
Gutfreund y Sompolinsky en 1985 con teoría de réplicas. La distancia entre
0.185 y 0.138 es el precio de ignorar la realimentación.

> La lección general, y no va de redes neuronales: una estimación de primer
> orden que supone que todo lo demás se queda quieto acertará sobre el primer
> paso y puede equivocarse arbitrariamente sobre el punto fijo. Siempre que la
> magnitud que perturbas realimente la perturbación, espera una transición que
> la servilleta no puede ver.

---

## 5. El modelo mínimo

Cada suposición de abajo compra una simplificación concreta, y todas ellas
fallan en algún sitio real. Enumerarlas no es ceremonia — la lista *es* el
dominio de validez, y es lo que los tests nunca podrán decirte.

| Suposición | Qué compra | Dónde se rompe |
|---|---|---|
| Los estados son bipolares, $s\in\lbrace -1,+1\rbrace^{N}$ | Un espacio de estados finito, así que el descenso debe terminar | Neuronas graduadas, códigos de tasa, relajaciones continuas |
| Los acoplamientos son **simétricos**, $W_{ij}=W_{ji}$ | Que exista siquiera una energía | Las sinapsis reales son dirigidas — sin energía, sin garantía |
| **Diagonal nula**, $W_{ii}=0$ | Cada actualización es un movimiento sobre la energía verdadera | El autoacoplamiento convierte una unidad en un biestable |
| La energía es **cuadrática** en $s$ | Acoplamientos por pares; $N^2$ parámetros | Los términos de orden superior dan mucha más capacidad |
| Sin campo externo, $b_i = 0$ | Simetría global de signo, $E(-s)=E(s)$ | Los patrones sesgados necesitan un umbral |
| Las actualizaciones son **deterministas** | $T=0$: solo movimientos cuesta abajo | Temperatura finita, máquinas de Boltzmann |
| Una unidad cada vez | El argumento de Lyapunov | Actualizaciones en paralelo — otro teorema |
| Los patrones están **no correlacionados** | El crosstalk es ruido de media cero | Los datos reales están correlacionados, y el recuerdo se degrada pronto |
| Almacenamiento hebbiano | Una pasada, sin iteración, regla local | La pseudoinversa y Storkey almacenan mucho más |
| $W$ almacenada densamente | Simplicidad | $N^2$ floats es el techo real |

Ese es el modelo. Fíjate en lo que **no** supone: no supone que los patrones
sean ortogonales, ni que $P$ sea pequeño, ni que la sonda esté cerca de una
memoria. Todo eso resulta importar enormemente, y el modelo te lo dice
produciendo respuestas incorrectas en vez de negándose.

Dos filas son estructurales de un modo en que las otras no lo son. La
**simetría** y la **diagonal nula** son las dos premisas del teorema de
descenso, y
[§6.4](#64-el-teorema-de-descenso-y-dónde-entra-cada-premisa) rompe cada una a
propósito para mostrar qué sostenía.

---

## 6. Las ecuaciones

### 6.1 Convertir "recordar" en "descender"

El problema tal como se plantea en [§1](#1-el-fenómeno) todavía no es
matemática. Hay un movimiento que lo convierte en matemática, y es el único
paso genuinamente creativo de toda la materia:

> **Deja de preguntar cómo recuperar un patrón. Pregunta qué paisaje haría de
> los patrones los sitios a los que rueda una bola.**

Si tal paisaje existe, la recuperación no es un algoritmo que diseñas — es lo
que ocurre cuando sueltas. La sonda es una posición inicial, la memoria es el
fondo de un valle, y la cuenca de atracción es exactamente el conjunto de
sondas que funcionan. Las tres propiedades de §1 salen gratis: sin clave (una
posición no es una clave), degradación gradual (la cuenca tiene anchura), sin
búsqueda (bajas, no miras alrededor).

Es el mismo replanteamiento que hace el libro sobre la optimización en general
— que un número enorme de problemas aparentemente inconexos son un solo
problema con ropa distinta, y que reconocer la forma vale más que cualquier
técnica. El principio de Fermat, un cristal formándose, un modelo ajustado, una
ruta de reparto y esta red son todos la misma frase: *algo se está
minimizando.*

### 6.2 Por qué la energía es cuadrática

Necesitamos una función $E:\lbrace -1,+1\rbrace^{N}\to\mathbb{R}$. Toma las
restricciones en orden.

**Debe construirse a partir de interacciones entre unidades**, porque toda la
gracia es que la memoria vive en los acoplamientos y no en las unidades. Un
término que depende solo de $s_i$ es un sesgo, y no almacena nada de ningún
patrón.

**Debe ser invariante bajo un cambio global de signo**, $E(-s) = E(s)$. Las
etiquetas $+1$ y $-1$ son una convención; nada físico las distingue. Esto mata
todos los términos de orden impar.

**Debe ser el orden más bajo que funcione.** El orden par más bajo por encima
de una constante es dos.

Esas tres dan, de forma única salvo escala,

$$\boxed{\enspace E(s) = -\frac{1}{2}\sum_{i,j} W_{ij}\thinspace s_i s_j
= -\frac{1}{2}\thinspace s^{\mathsf T} W s\enspace}$$

con $W$ simétrica (la parte antisimétrica de cualquier $W$ no aporta nada a la
forma cuadrática — se cancela idénticamente, que es la primera pista de que la
simetría no es opcional sino automática *en la energía*, y por tanto de que una
red asimétrica está siguiendo algo que la energía no puede ver). Esto es
[`model.energy()`](../model.py).

El factor $-\tfrac12$ es contabilidad: el menos hace que el acuerdo entre
unidades acopladas positivamente *baje* la energía, y el medio compensa contar
cada par dos veces.

**Y el "orden más bajo que funcione" es una elección, no una ley.** Lleva la
energía a orden $k$ y la capacidad sube de $N$ a $N^{k-1}$. Eso es exactamente
lo que hacen las memorias asociativas densas (Krotov & Hopfield 2016), y es el
sitio más productivo para atacar este modelo.

### 6.3 Hebb no se elige, se fuerza

La mayoría de los tratamientos enuncian la regla hebbiana y luego verifican que
funciona. Hazlo al revés: **exige que los patrones sean puntos fijos y mira qué
le queda a $W$ por ser.**

Queremos una regla que (i) sea *local* — $W_{ij}$ solo puede depender de lo que
hacen las unidades $i$ y $j$ en los patrones, porque no hay autoridad central
que calcule nada más; (ii) sea *simétrica*, para que exista una energía; (iii)
respete la misma simetría de signo que la energía, $W(p) = W(-p)$; y (iv) sea
*aditiva* sobre los patrones, una pasada sin revisitar.

Cualquier función de dos variables bipolares puede escribirse
$f(a,b) = c_0 + c_1 a + c_2 b + c_3\thinspace ab$, ya que $a^2 = b^2 = 1$
mata todo lo demás. La localidad permite los cuatro términos.
La simetría en $i \leftrightarrow j$ fuerza $c_1 = c_2$. La invariancia bajo $p \to -p$ mata $c_1$
y $c_2$ por completo. La constante $c_0$ desplaza todos los acoplamientos por
igual y no almacena nada. **Sobrevive un término.**

$$W_{ij} = \frac{1}{N}\sum_{\mu} p^{\mu}_i p^{\mu}_j \quad (i \neq j),
\qquad W_{ii} = 0$$

que es [`model.hebbian_weights()`](../model.py) y, leído en voz alta, es la
frase de Hebb de 1949: las unidades que coinciden a lo largo de los patrones
almacenados acaban acopladas positivamente. Nunca hubo una elección que hacer.

**¿Funciona?** Sondea con $p^{\nu}$ y calcula el campo:

$$\left(Wp^{\nu}\right)_i = \frac{1}{N}\sum_{j\neq i}\sum_{\mu}
p^{\mu}_i p^{\mu}_j p^{\nu}_j = \frac{N-1}{N}\thinspace p^{\nu}_i
\thinspace + \thinspace \frac{1}{N}\sum_{\mu\neq\nu} p^{\mu}_i
\sum_{j\neq i} p^{\mu}_j p^{\nu}_j$$

así que $h_i\thinspace p^{\nu}_i = 1 - 1/N + \text{crosstalk}$, y el patrón es
un punto fijo exactamente cuando el crosstalk nunca alcanza $-1$ en ninguna
unidad. En $N=400$, $P=3$ la media medida de $h_i p_i$ es $0.9938$ frente a
$1 - 1/N = 0.9975$, con un mínimo de $0.9425$ — cómodamente positiva en todas
partes, así que el patrón no se mueve. Sube $P$ y al final alguna unidad
pierde; eso es [§8](#8-análisis-de-escala-leer-la-respuesta-en-el-crosstalk).

La escala $1/N$ no le hace nada a la dinámica — $\mathrm{sign}$ ignora un
multiplicador positivo — pero hace comparables las energías entre redes de
tamaños distintos, que es la única razón por la que el experimento de capacidad
produce una gráfica legible. La versión de 2024 de este código dividía por $P$
en su lugar, lo cual es inocuo para el recuerdo y arruina en silencio cualquier
comparación.

### 6.4 El teorema de descenso, y dónde entra cada premisa

Ahora la recompensa. Actualiza la unidad $k$ y nada más. Separa la energía en
los términos que involucran a $k$ y los que no, usando que $W$ es simétrica:

$$E(s) = -\frac{1}{2}\sum_{i,j\neq k} W_{ij}s_i s_j
\thinspace-\thinspace s_k \sum_{j\neq k} W_{kj}s_j
\thinspace-\thinspace \frac{1}{2}W_{kk}\thinspace s_k^2$$

El primer grupo no cambia. El tercero tampoco cambia, porque $s_k^2 = 1$ tome
el valor que tome $s_k$. Así que, escribiendo
$g_k \equiv \sum_{j\neq k} W_{kj}s_j$ para el campo de *todos los demás*,

$$\boxed{\enspace \Delta E = -\thinspace\Delta s_k \thinspace g_k\enspace}$$

Verificado hasta $7\times10^{-15}$ sobre 500 volteos de una sola unidad. Ahora
las dos premisas, y qué sostiene cada una:

**Diagonal nula.** La regla de actualización usa el campo *completo*
$h_k = \sum_j W_{kj}s_j = g_k + W_{kk}s_k$, mientras que la energía solo
responde a $g_k$. Cuando $W_{kk}=0$ los dos coinciden, la unidad se alinea con
la mismísima magnitud cuyo signo decide $\Delta E$, y el descenso se sigue.
Cuando $W_{kk}\neq 0$ se separan y la garantía se evapora. No es una
preocupación de redondeo:

- $W_{kk} \gt 0$ sesga la unidad hacia lo que ya es. Deja de tomar movimientos
  cuesta abajo y se congela. Eso es un biestable, no una memoria.
- $W_{kk} \lt 0$ la sesga *contra* sí misma. Medido con $W_{kk} = -2$ sobre una
  $W$ simétrica aleatoria: las actualizaciones asíncronas suben la energía y
  siguen subiéndola, exactamente como predice $\Delta E = -\Delta s_k g_k$ en
  cuanto $\mathrm{sign}(h_k) \neq \mathrm{sign}(g_k)$.

**Simetría.** Quítala y la derivación de arriba falla en la primera línea: los
dos términos cruzados ya no se combinan. La dinámica sigue a $W$, la energía
solo llega a ver $(W + W^{\mathsf T})/2$, y no hay razón para que el sistema
minimice una función que no está mirando. Medido sobre $W$ asimétricas
aleatorias en $N=8$ con un orden de actualización fijo: **ciclos límite
asíncronos de período 2 y período 3** — estados que se repiten para siempre.
Con $W$ simétrica eso es imposible, que es el párrafo siguiente.

**Terminación.** Fíjate en que un volteo solo ocurre cuando $g_k \neq 0$
estrictamente, porque [`update_rule`](../model.py) mantiene el valor actual
ante un empate. Así que todo volteo que de verdad ocurre tiene

$$\Delta E = -\thinspace\Delta s_k\thinspace g_k = -2\thinspace|g_k| \lt 0$$

**estrictamente.** La energía, por tanto, nunca repite un valor, así que el
estado nunca se repite, y el espacio de estados es finito. Un conjunto finito
sin repeticiones es un paseo finito: la dinámica alcanza un punto fijo en un
número acotado de pasos y se queda. No "normalmente converge" — no puede hacer
otra cosa.

Eso vale la pena leerlo dos veces, porque significa que la convención de empate
no es pulcritud defensiva. Es lo que convierte $\Delta E \le 0$ en
$\Delta E \lt 0$, y una desigualdad no estricta no prueba nada sobre la
terminación.

### 6.5 El empate, y una ley de paridad exacta

`np.sign(0)` devuelve $0$, que no está en $\lbrace -1,+1\rbrace$ — una unidad
actualizada así se cae del hipercubo y el estado deja de ser un estado.
[`model.update_rule()`](../model.py) mantiene el valor actual en su lugar. El
docstring dice que los empates "no son tan raros como parecen a $N$ pequeño".
Es una afirmación comprobable, así que hay que comprobarla, y la respuesta es
más nítida de lo esperado.

El campo es $N h_i = \sum_{j\neq i} C_{ij}s_j$ con
$C_{ij} = \sum_{\mu}p^{\mu}_i p^{\mu}_j$ entero, así que un empate es una
identidad entera exacta y el punto flotante no tiene nada que ver. Escribe
$q_j = (p^1_j,\dots,p^P_j)$; entonces

$$N h_i = q_i \cdot v, \qquad v_{\mu} = \sum_{j\neq i} p^{\mu}_j s_j$$

Cada $v_{\mu}$ es una suma de $N-1$ términos de $\pm1$, así que tiene la
paridad de $N-1$. El producto escalar es una suma con signo de $P$ números así,
de modo que $Nh_i$ tiene la paridad de $P(N-1)$. **Un empate exige
$Nh_i = 0$, lo que exige que esa paridad sea par.** De ahí:

$$\boxed{\enspace P(N-1)\ \text{odd}\ \Longrightarrow\ \text{an exact tie is
impossible}\enspace}$$

Predicho primero, luego medido sobre 60 conjuntos de patrones $\times$ 30
estados cada uno:

| $N$ | $P$ | $P(N-1)$ | predicho | tasa de empate medida |
|---|---|---|---|---|
| 20 | 3 | impar | imposible | 0.0000% |
| 20 | 4 | par | posible | 11.12% |
| 21 | 3 | par | posible | 10.60% |
| 100 | 3 | impar | imposible | 0.0000% |
| 101 | 3 | par | posible | 4.72% |
| 576 | 5 | impar | imposible | 0.0000% |
| 577 | 3 | par | posible | 1.87% |
| 577 | 5 | par | posible | 1.52% |

![Fracción de campos locales que son exactamente cero, frente al tamaño de la
red, en aritmética entera exacta. Una serie se sitúa en unos pocos por ciento y
decae lentamente; la otra es plana en exactamente cero a cualquier tamaño; una
tercera muestra lo que float64 reporta para la primera.](figures/parity.png)

**Qué concluir:** esto no es una tasa que resulta ser pequeña. O es un pequeño
porcentaje o es exactamente cero, y una paridad entera decide cuál — no hay
nada intermedio, a ningún tamaño.

Diez predicciones, diez aciertos, y la tasa decae aproximadamente como
$1/\sqrt{N}$ en el caso par en vez de desaparecer. **El experimento estrella de
esta misma entrada cae del lado malo**: $N = 576$ glifos con $P = 4$ dan
$P(N-1) = 2300$, par, y el 3.5% de los campos de unidad sobre estados
aleatorios son empates exactos. La convención es estructural en el código tal
como se distribuye, no en un hipotético.

Un aguijón numérico al final. Esos son los empates *verdaderos*, calculados en
aritmética entera exacta. Pregúntale a `float64` cuántos ve:

| $N$ | empates reales | reportados como `h == 0` | perdidos |
|---|---|---|---|
| 20 | 11.67% | 4.53% | 61% |
| 60 | 3.99% | 0.08% | 98% |
| 200 | 3.41% | 0.10% | 97% |
| 576 | 1.58% | 0.23% | 86% |

Un cero matemáticamente exacto, acumulado a través de cientos de sumas en punto
flotante, llega como $10^{-17}$ y la unidad toma en silencio una dirección
elegida por el redondeo. Nada lanza una excepción, nada avisa, y todos los
tests siguieron pasando. La dinámica no es incorrecta — un pelo a un lado u
otro del cero es un desempate legítimo — pero **la propia guarda del código
solo está capturando una séptima parte de los casos para los que se escribió**,
y ninguna cantidad de relecturas del código lo habría encontrado. Hizo falta
aritmética entera para verlo.

Ambas mitades están ahora en [`test_model.py`](../tests/test_model.py): la ley
de paridad como seis casos que deben y no deben empatar, y el déficit de
float64 como un test que documenta la brecha en vez de fingir que está cerrada.

---

## 7. Dos esquemas, una energía

En [`tmm/`](../../tmm/README.md), la entrada hermana, los dos solvers coinciden
hasta $10^{-13}$ y cualquier discrepancia sería un bug. Aquí los dos métodos
discrepan a propósito, y la discrepancia es un teorema.

### 7.1 Asíncrono: el argumento de Lyapunov se sostiene

Una unidad cada vez, en orden aleatorio.
[`methods/asynchronous.py`](../methods/asynchronous.py) tiene cuatro líneas
porque §6.4 ya hizo el trabajo: todo volteo baja estrictamente $E$, el espacio
de estados es finito, así que la ejecución **alcanza un punto fijo y no puede
ciclar**. Nunca. Para cualquier $W$ simétrica con diagonal nula, desde
cualquier estado inicial, bajo cualquier orden de actualización.

El precio es que la trayectoria depende del orden, así que en qué memoria
aterrizas cuando la sonda es ambigua es función de la semilla aleatoria. La
ejecución fija la semilla por esa razón.

### 7.2 Síncrono: otro teorema, no la ausencia de uno

Actualiza todas las unidades a la vez desde el mismo campo.
[`methods/synchronous.py`](../methods/synchronous.py) es un producto
matriz-vector por barrido y mucho más rápido. La derivación de §6.4 se derrumba
de inmediato: suponía que *todo lo demás se quedaba quieto*, y ahora nada lo
hace. La energía es libre de subir, y sube.

Pero "sin garantía" es la lectura perezosa, y es incorrecta. Sigue habiendo una
función de Lyapunov — solo que vive sobre **pares de estados consecutivos**:

$$F\left(s(t), s(t{+}1)\right) = -\thinspace s(t)^{\mathsf T} W\thinspace s(t{+}1)$$

Para ver que nunca aumenta, usa $s(t{+}1) = \mathrm{sign}(Ws(t))$ y la
simetría:

$$\Delta F = -\thinspace s(t{+}1)^{\mathsf T}W\left[s(t{+}2) - s(t)\right]
= -\sum_i \left(\thinspace|h_i| - h_i\thinspace s_i(t)\thinspace\right) \le 0$$

con $h = W s(t{+}1)$, porque $h_i s_i(t{+}2) = |h_i|$ por construcción y
$|h_i| \ge h_i s_i(t)$ siempre. El mismo argumento de finitud se aplica
entonces a $F$, y la igualdad fuerza $s(t{+}2) = s(t)$.

**Por tanto la dinámica síncrona converge a un ciclo de período 1 o 2 y a nada
más.** Sin período 3, sin caos, sin deriva. Ese es el teorema de Goles-Chacc,
Fogelman-Soulié y Pellegrin (1985), y es una afirmación mucho más fuerte que "a
veces oscila".

Ambas mitades verificadas. Sobre 600 ejecuciones a cuatro $(N,P)$ distintos:

```
max increase of F across every step:  2.8e-14      (must be <= 0)
period histogram over 600 runs:       {1: 442, 2: 158}
```

Nada más que 1 y 2, y $F$ nunca subió por encima del ruido numérico. Ambas se
afirman en [`test_methods_differ.py`](../tests/test_methods_differ.py), junto a
un tercer test que captura que $E$ sube y $F$ no sube en la misma trayectoria
— dos contables, una ejecución.

### 7.3 Lo que el contrato puede y no puede exigir

Este es el punto arquitectónico de la entrada, y es la imagen especular del de
`tmm/`.

[`tests/test_methods.py`](../tests/test_methods.py) está parametrizado sobre
todos los métodos registrados y afirma lo que todos deben hacer: mantenerse
bipolares, dejar en paz un patrón almacenado, recordar desde el ruido,
terminar. Deliberadamente **no** afirma el descenso de la energía. Añadir esa
línea parecería minuciosidad y sería afirmar algo falso sobre la mitad de los
métodos.

Las diferencias viven en
[`tests/test_methods_differ.py`](../tests/test_methods_differ.py), enunciadas
como afirmaciones positivas sobre cada esquema en vez de como exenciones: el
asíncrono nunca aumenta $E$ y siempre alcanza un punto fijo; el síncrono puede
aumentar $E$ y sí cae en ciclos de 2 estados.

> Un contrato compartido solo vale la pena si es la intersección de lo que las
> implementaciones garantizan de verdad. En el momento en que contiene una
> cláusula que una implementación no puede satisfacer, o el test está mal o el
> método no pertenece ahí — y vale la pena saber cuál antes de escribir el
> código que depende de él.

---

## 8. Análisis de escala: leer la respuesta en el crosstalk

Casi todo sobre este modelo es una afirmación sobre un solo cociente:

$$\alpha \equiv \frac{P}{N}$$

No $P$. No $N$. La **carga**. Una red de un millón de unidades no recuerda
mejor que una de cien — recuerda mejor *proporcionalmente más cosas*, y no
recuerda nada mejor cada una.

### 8.1 Señal contra ruido

De [§6.3](#63-hebb-no-se-elige-se-fuerza), la estabilidad de la unidad $i$ en
el patrón $\nu$ la decide

$$h_i\thinspace p^{\nu}_i = \underbrace{1 - 1/N}_{\text{signal, size } 1}
\thinspace + \thinspace \underbrace{C_i}_{\text{noise, s.d. } \sqrt{\alpha}}$$

La señal no crece con $N$. El ruido no se encoge con $N$. Solo importa su
cociente, y ese cociente es $1/\sqrt{\alpha}$. Cada afirmación de capacidad de
abajo es un umbral distinto sobre ese único número.

### 8.2 Un primer umbral: un bit mal

$P_{\text{err}} = Q(1/\sqrt{\alpha})$, verificado hasta el tercer decimal en
[§4.3](#43-entonces-calcula-cuándo-el-crosstalk-supera-a-la-señal--y-esta-es-la-sutil).
Pide como mucho un bit erróneo en un patrón recordado de $N$ unidades:

$$N\thinspace Q\negthinspace\left(\frac{1}{\sqrt{\alpha}}\right) \lt 1$$

*Respuesta a la pregunta 1, primera versión.* En $N = 576$ eso exige
$Q \lt 1/576$, así que $1/\sqrt{\alpha} \gt 2.92$, así que $\alpha \lt 0.117$:
**67 patrones.**

### 8.3 El umbral real: la avalancha

La estimación de arriba supone que las otras $N-1$ unidades son correctas. No
lo son, y sus errores realimentan. El tratamiento autoconsistente da una
transición de fase genuina en

$$\boxed{\enspace\alpha_c = 0.138\enspace}$$

*Respuesta a la pregunta 1, segunda versión:* $0.138 \times 576 =$ **79
patrones.** No quinientos, no medio millón. Una red de 576 unidades y 331 776
acoplamientos guarda setenta y nueve patrones de 576 bits.

La transición es abrupta y se agudiza con $N$, que es lo que hace una
transición de fase y lo que el experimento de capacidad de la entrada mide
directamente. Su señal en los datos medidos es el salto en la última columna de
[§4.3](#43-entonces-calcula-cuándo-el-crosstalk-supera-a-la-señal--y-esta-es-la-sutil):
error $0.0095$ en $\alpha = 0.138$ y $0.1064$ en $\alpha = 0.16$. Once veces
peor por un aumento del 16% en la carga.

### 8.4 Un tercer umbral: *todos* los patrones, exactamente

Exige que los $P$ patrones se recuerden sin ningún error, con probabilidad
tendiendo a 1. El requisito escala ahora con $P$ además de con $N$, y la
respuesta no es en absoluto un $\alpha$ constante:

$$P_{\max} \simeq \frac{N}{4\ln N}$$

*Respuesta a la pregunta 1, tercera versión:* $576/(4\ln 576) =$ **23
patrones.**

Tres criterios defendibles, tres respuestas — 23, 67, 79 — que abarcan un
factor de 3.4. **La "capacidad" no es una propiedad de la red; es una propiedad
de la pregunta.** Quien cite un número sin decir qué fallo está tolerando está
citando un número sobre el que no ha pensado.

### 8.5 Las cuencas se encogen mucho antes que la capacidad

La capacidad pregunta si una memoria es *estable*. La utilidad pregunta desde
cuán lejos puedes partir y aun así llegar. Medido: fracción de recuerdos
exactos con éxito, $N = 500$, 20 pruebas por celda, frente a la fracción de
bits corrompidos en la sonda.

| $\alpha$ | 5% | 10% | 20% | 30% | 40% | 45% | 50% |
|---|---|---|---|---|---|---|---|
| 0.02 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.50 | 0.00 |
| 0.05 | 1.00 | 1.00 | 1.00 | 1.00 | 0.75 | 0.05 | 0.00 |
| 0.10 | 0.75 | 0.75 | 0.70 | 0.50 | 0.00 | 0.00 | 0.00 |
| 0.138 | 0.30 | 0.30 | 0.25 | 0.00 | 0.00 | 0.00 | 0.00 |

![Fracción de sondas recordadas exactamente, frente a cuán corrupta estaba la
sonda, para cuatro cargas. A la carga más baja la curva es plana hasta el 40%
de corrupción; a la carga crítica arranca por debajo de un tercio y está muerta
al 30%.](figures/basins.png)

**Qué concluir:** capacidad y utilidad son preguntas distintas. De esa tabla
salen tres cosas.

**La columna del 50% es cero en todas partes, y debe serlo.** Una sonda con la
mitad de sus bits volteados tiene solapamiento cero con el objetivo: no
contiene información sobre qué memoria querías. Esa columna no es un fallo del
modelo, es el modelo informando de que la pregunta estaba vacía.

**A carga baja las cuencas son enormes** — un 40% de corrupción todavía se
recupera perfectamente en $\alpha = 0.02$. Esa es la propiedad que hace que
esto sea interesante siquiera.

**En $\alpha_c$ las cuencas ya se han colapsado.** A la carga "crítica" la red
recuerda una sonda corrompida al 5% el 30% de las veces. Las memorias siguen
siendo técnicamente estables — eso es lo que mide $\alpha_c$ — y son inútiles,
porque nada puede alcanzarlas. **La capacidad es una cota superior sobre una
magnitud que nadie quiere.** La carga a la que puedes trabajar de verdad es
varias veces menor, y esa brecha es invisible a menos que midas cuencas en vez
de estabilidad.

### 8.6 El coste de un acoplamiento

La información almacenada son $P \times N$ bits. Los acoplamientos son $N^2$
números. En la capacidad:

$$\frac{P N}{N^2} = \alpha_c = 0.138\ \text{bits per coupling}$$

*Respuesta a la pregunta 2.* En $N = 10^6$, $W$ tiene $10^{12}$ entradas:
**8 TB en float64**, que guardan 138 000 imágenes que ocupan 17 GB como bits
crudos. Gastas **464 bits de RAM por bit almacenado**, y el cociente es
$64/\alpha_c$ — no mejora con el tamaño, nunca, porque ambos escalan como
$N^2$.

Así que: nunca como tecnología de almacenamiento. Siempre como modelo de cómo
podría funcionar el direccionamiento por contenido sin un controlador.

Y el 0.138 no es culpa de la arquitectura. Gardner (1988) calculó el máximo
sobre *todos* los acoplamientos simétricos, no solo los hebbianos, y obtuvo
$\alpha_{\max} = 2$ — **2 bits por acoplamiento, un factor de 14 más.** La
información está en los acoplamientos; la regla de aprendizaje local de una
sola pasada simplemente no puede alcanzarla. El almacenamiento por
pseudoinversa consigue $\alpha = 1$ a costa de una inversión de matriz, y la
regla de Storkey mejora a Hebb manteniéndose local e incremental.

> $\alpha_c = 0.138$ es un hecho sobre **Hebb**, no sobre las redes de
> Hopfield. Esa distinción vale la pena conservarla, porque "el modelo llega
> hasta aquí" y "esta regla concreta de una sola pasada llega hasta aquí"
> llevan a movimientos siguientes completamente distintos.

---

## 9. Formas cerradas que vale la pena memorizar

Esto es contra lo que compruebas el código. Contrastar dos métodos prueba que
coinciden; contrastar contra una forma cerrada prueba que son *correctos*. Cada
fila de aquí es un test en [`../tests/`](../tests/).

| Situación | Resultado |
|---|---|
| Energía | $E = -\tfrac12\thinspace s^{\mathsf T}Ws$ |
| Acoplamientos hebbianos | $W = \tfrac1N\sum_{\mu}p^{\mu}(p^{\mu})^{\mathsf T}$, $W_{ii}=0$ |
| Volteo de una sola unidad | $\Delta E = -\thinspace\Delta s_k\thinspace g_k$, $g_k = \sum_{j\neq k}W_{kj}s_j$ |
| Un volteo real | $\Delta E = -2\thinspace\lvert g_k\rvert \lt 0$, estrictamente |
| Campo sobre un patrón almacenado | $h_i p^{\nu}_i = 1 - 1/N + \text{crosstalk}$ |
| D.e. del crosstalk | $\sqrt{(P-1)/N} \simeq \sqrt{\alpha}$ |
| Tasa de error en un paso | $Q\left(1/\sqrt{\alpha}\right)$ |
| Energía de un patrón almacenado ($p$ aleatorio) | $E \simeq -(N-1)/2$, así que $E/N \simeq -0.5$ |
| Energía de un estado aleatorio | media $0$, d.e. $\simeq\sqrt{P/2}$ |
| Simetría de signo | $E(-s) = E(s)$; toda memoria tiene un espejo |
| Mezcla de tres patrones | $\mathrm{sign}(p^1+p^2+p^3)$ es un punto fijo que nadie almacenó |
| Capacidad, memorias estables | $\alpha_c = 0.138$ |
| Capacidad, todos los patrones exactos | $P_{\max}\simeq N/(4\ln N)$ |
| Capacidad, acoplamientos óptimos | $\alpha_{\max} = 2$ (Gardner) |
| Densidad de información | $\alpha$ bits por acoplamiento |
| Dinámica síncrona | período 1 o 2, nunca más |
| Función de Lyapunov síncrona | $F = -\thinspace s(t)^{\mathsf T}Ws(t{+}1)$, no creciente |
| Empates exactos | imposibles si y solo si $P(N-1)$ es impar |

**Una advertencia sobre la fila ocho.** "Los patrones almacenados están más
bajos que los estados aleatorios" es el test que todo el mundo escribe primero
y no vale casi nada. Pasa en $\alpha = 0.5$, muy pasada la capacidad, donde el
recuerdo está destruido — las memorias *siguen* en mínimos locales, simplemente
tienen exponencialmente muchos vecinos que también lo están. Una comparación de
energías restringe tu contabilidad, no tu recuerdo. Las filas sobre tasas de
error y cuencas la superan, y el acuerdo entre métodos está por debajo de
ambas.

---

## 10. Lo que mostró la simulación

La regla del libro: **predice antes de ejecutar.** Cada experimento de la
entrada está construido como una predicción con un número pegado, no como una
gráfica que admirar. El tercero produjo lo contrario de lo que predijo, y por
eso es el más útil. Las figuras de todo este documento salen de
[`landscape.py`](../experiments/landscape.py), que existe porque escribir la
derivación necesitaba números que nada en la entrada medía todavía.

### 10.1 Recuerdo — [`recall.py`](../experiments/recall.py)

Predicción: los patrones almacenados se sitúan cerca de $E/N = -0.5$, los
estados aleatorios cerca de $0$, y una sonda corrompida al 25% devuelve la
memoria exactamente.

```
N = 576 units, P = 4 patterns, load = 0.0069

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

Cada patrón vuelve exactamente, en dos barridos, desde una sonda con un cuarto
de sus bits mal — suficiente ruido para que las letras sean ilegibles para un
humano, como muestra la figura del README de la entrada. Los estados aleatorios
se sitúan en $E/N = 0.0000$ frente al $-0.58$ de las memorias: las memorias son
de verdad los valles, y todo lo demás es de verdad la llanura.

**Pero la servilleta dice $-0.4991$ y las letras están entre $-0.53$ y
$-0.63$.** Los pozos son *más profundos* de lo que predice la teoría, y la
razón es que las letras están correlacionadas — los solapamientos por pares van
de $+0.02$ a $+0.42$ en vez del $\pm 1/\sqrt{N} \approx 0.04$ de los patrones
aleatorios, porque cada glifo comparte un fondo con todos los demás. Los
patrones correlacionados refuerzan mutuamente sus acoplamientos y cavan
agujeros más profundos.

Esa correlación no es una molestia que haya que eliminar con ingeniería; es lo
que hace que estos patrones valgan la pena. **Tres de los cuatro conjuntos de
letras probados no recuerdan nada en absoluto** — `FRAN` y `AENX` devuelven
ambos 0 de 4 memorias desde un 25% de ruido, y el conjunto de cuatro letras
menos correlacionado del alfabeto llega a 2. `MATH` devuelve 4 de 4 hasta un
35% de ruido a lo largo de seis semillas. La propia predicción de la entrada,
que la correlación destroza el recuerdo hebbiano, es lo que decidió qué letras
podía usar.

Agujeros más profundos, y peor recuerdo. No es una contradicción y es el asunto
de §10.3. Comprobado contra patrones no correlacionados, donde la servilleta es
exacta:

| $N$ | $P$ | $E/N$ medido | $-(N-1)/2N$ |
|---|---|---|---|
| 400 | 3 | $-0.4968$ | $-0.4988$ |
| 400 | 20 | $-0.4956$ | $-0.4988$ |
| 1000 | 50 | $-0.4997$ | $-0.4995$ |

### 10.2 Capacidad — [`capacity.py`](../experiments/capacity.py)

Predicción: el error frente a la carga tiene un codo en $\alpha_c = 0.138$, y
la transición se agudiza con $N$.

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

El codo está donde lo pone la teoría. Y el afilado se ve en la dirección
correcta, que es la parte contraintuitiva: **pasada la transición las redes más
grandes son peores.** En $\alpha = 0.16$ el error se triplica aproximadamente
de $N=100$ a $N=500$. Una red más grande no es una red más segura — es una red
con un borde más nítido, mejor por debajo del umbral y peor por encima. Eso es
exactamente lo que le pasa a un imán cuando tomas el límite termodinámico, y es
la evidencia más clara de la entrada de que esto es realmente una transición de
fase y no una degradación gradual.

### 10.3 Estados espurios — [`associative_and_spurious.py`](../experiments/associative_and_spurious.py)

Predicción: una sonda que se parece a un patrón almacenado lo recupera, y
$\mathrm{sign}(p^1+p^2+p^3)$ es un estado estable que nadie almacenó.

La segunda se sostuvo. La primera no, y la forma en que falló es la salida más
instructiva de la entrada.

```
N — never stored, looks like H
  overlap: M=+0.528  A=+0.410  T=+0.160  H=+0.889
  closest: H (+0.889)   sweeps: 2   E: -361.47
  landed on a stored memory: NO — spurious

checkerboard — genuinely unrelated
  closest: A (-1.000)   sweeps: 2   E: -330.82
  landed on a stored memory: yes

sign(M + A + T)
  overlap: M=+0.392  A=+0.628  T=+0.628  H=+0.337
  closest: A (+0.628)   sweeps: 1   E: -302.51
  landed on a stored memory: NO — spurious
```

**El casi acierto no recupera la memoria.** La letra `N` comparte los dos
verticales con la `H` almacenada y difiere solo en la barra. Entrégasela y la
red se detiene en un solapamiento de $+0.889$ — reconociblemente parecida a una
H, no la H — en un valle en $E = -361.47$ frente al $-362.36$ de la H
almacenada. **Casi exactamente igual de profundo, e incorrecto.** Un mínimo
menos profundo situado entre la sonda y la memoria, atrapando la bola en el
camino de bajada.

La red respondió con confianza y respondió mal, y nada en la ejecución lo dice:
convergió, la energía cayó monótonamente, el estado es un punto fijo genuino.
La figura muestra lo que un lector puede comprobar y un número no — lo que sale
es visiblemente una H con la diagonal todavía comiéndosela.

**La sonda no relacionada aterriza exactamente en $-p$.** El tablero de ajedrez
se asienta en el espejo de `A` con energía idéntica, que es la simetría de
signo de §6.2 apareciendo como comportamiento en vez de como una aserción de
test. Cada memoria que almacenas viene con una antimemoria que no almacenaste,
a la misma profundidad, y no hay ningún mecanismo en el modelo que prefiera
una.

**El estado de mezcla es estable**, como dice la teoría. Eso es un cambio
respecto de la versión de esta entrada construida sobre formas abstractas,
donde en cambio colapsaba en una memoria: aquellas estaban correlacionadas de
otro modo, lo bastante para remodelar el paisaje y romper un resultado de libro
de texto. El control se ejecuta en cualquier caso:

```
random patterns: mixture is a fixed point -> True
overlaps with the three memories: +0.490  +0.472  +0.545
```

### 10.4 ¿Cuántos estados espurios hay?

![Izquierda: la letra N entregada a la red, el estado en el que se asienta, y
la H almacenada a la que nunca llega, con sus energías. Derecha: puntos fijos
encontrados por enumeración exhaustiva en N = 16, separados en memorias
almacenadas con sus espejos y estados que nadie
almacenó.](figures/spurious.png)

**Qué concluir:** la ejecución convergió, la energía cayó monótonamente, el
estado final es un punto fijo genuino — y la respuesta es incorrecta. Nada en
la trayectoria distingue esto de un recuerdo correcto.

*Respuesta a la pregunta 3.* Enumera los $2^N$ estados para $N$ pequeño y
cuenta exactamente cuáles son puntos fijos, promediado sobre 5 conjuntos de
patrones:

| $N$ | $P$ | $\alpha$ | memorias + espejos | puntos fijos totales | espurios |
|---|---|---|---|---|---|
| 16 | 1 | 0.06 | 2.0 | 2.0 | 0.0 |
| 16 | 2 | 0.13 | 4.0 | 4.0 | 0.0 |
| 16 | 3 | 0.19 | 6.0 | 10.4 | 4.4 |
| 16 | 4 | 0.25 | 7.6 | 17.2 | 9.6 |
| 20 | 3 | 0.15 | 6.0 | 8.8 | 2.8 |
| 20 | 5 | 0.25 | 6.4 | 13.6 | 7.2 |

Lee la última fila con cuidado. Se almacenaron diez estados (cinco patrones y
sus espejos); **6.4 de ellos sobrevivieron como puntos fijos** — pasada la
capacidad, algunas memorias ya no son estables — y la red puede detenerse en
13.6 estados, más de la mitad de los cuales nadie pidió. El resultado
asintótico conocido es peor de lo que sugiere esta tabla: el número de estados
metaestables crece *exponencialmente* en $N$ mientras que el número de memorias
crece linealmente.

Así que la respuesta a la pregunta 3 es: **muchos más sitios donde detenerse
que cosas almacenaste, y el cociente empeora con cada patrón que añades.** Lo
que significa que una respuesta convergida no es evidencia de una respuesta
correcta. Si importa, comprueba el solapamiento con un patrón almacenado; la
red no te lo va a decir por su cuenta.

---

## 11. Dónde el modelo deja de ser cierto

La sección que más importa, y la que normalmente falta.

### 11.1 Correlación — la suposición que falla primero

Todos los números de capacidad de este documento suponen que los patrones son
signos aleatorios independientes. Nada de lo que querrías almacenar lo es.

Las fotografías son en su mayor parte cielo o en su mayor parte fondo. El texto
es en su mayor parte caracteres comunes. Las lecturas de sensores son en su
mayor parte el estado normal. Todos ellos tienen solapamientos mucho mayores
que el $\pm1/\sqrt{N}$ de los vectores aleatorios, y el análisis del crosstalk
de [§8.1](#81-señal-contra-ruido) está construido sobre ese escalado
$\sqrt{\alpha}$. Cuando los patrones están correlacionados el crosstalk deja de
ser ruido de media cero y se convierte en un tirón sistemático.

Dos consecuencias, ambas visibles en esta entrada:

- **El recuerdo se degrada muy por debajo de $\alpha_c$.** El experimento de
  los glifos corre en $\alpha = 0.0069$ — veinte veces por debajo de la
  capacidad — y aun así produce un atractor espurio ante una sonda de casi
  acierto.
- **Las energías engañan.** Los patrones correlacionados se sitúan *más
  profundos* de lo que predice la fórmula no correlacionada ($-0.55$ frente a
  $-0.50$), así que la comprobación de salud ingenua se lee como *mejor de lo
  esperado* precisamente en las ejecuciones donde el recuerdo es peor.

Por eso, en vez de usar las fotografías originales de 2024, la entrada genera
glifos. No es una comodidad de licencias: las fotografías están fuertemente
sesgadas hacia un color, ese sesgo correlaciona cada patrón con todos los
demás, y el fallo resultante no tiene nada que ver con el modelo bajo prueba.
Elegir datos que aíslen el fenómeno es parte de diseñar el experimento.

El arreglo se conoce — el almacenamiento por pseudoinversa maneja los patrones
correlacionados como es debido, a costa de dejar de ser local y de una sola
pasada — y no está implementado aquí.

### 11.2 El resto de la lista

| Límite | Qué ocurre en realidad | Esta entrada |
|---|---|---|
| Carga por encima de $\approx 0.138$ | Avalancha; el error de recuerdo salta 20× sobre la servilleta | medido, no supuesto |
| Carga por encima de $\approx 0.05$ | Las cuencas colapsan mientras las memorias siguen "estables" | medido en §8.5 |
| Patrones correlacionados | Atractores espurios 20× por debajo de la capacidad | mostrado en §10.3 |
| Estados espurios | Exponencialmente muchos; una respuesta convergida no prueba nada | contados en §10.4 |
| Estados espejo $-p$ | Siempre presentes, misma energía, sin forma de preferir $p$ | testeado |
| $W$ simétrica | Requerida para que haya energía; asimétrica da ciclos límite | `ValueError` |
| $W_{ii} \neq 0$ | Enclavamiento, o energía que sube | `ValueError` |
| Actualizaciones síncronas | La energía puede subir; ciclos de período-2 | caracterizado, no prohibido |
| Empates exactos | Reales siempre que $P(N-1)$ es par; float64 se pierde ~90% | ley testeada; la brecha del float documentada, no arreglada |
| $W$ densa | $N^2$ floats — 8 TB a un megapíxel | el techo real del tamaño |
| Temperatura finita | Solo movimientos cuesta abajo; sin escape de una cuenca mala | no modelada — $T = 0$ |
| Mejores reglas de almacenamiento | Pseudoinversa $\alpha=1$, Gardner $\alpha=2$ | no implementadas |
| Energías de orden superior | Capacidad $N^{k-1}$ en vez de $0.138N$ | una entrada aparte |

Tres de esas filas existen porque alguien **sondeó** los bordes en vez de
razonar sobre ellos: la brecha de la avalancha, el colapso de las cuencas, y la
ley de paridad con su punto ciego de punto flotante. La batería estaba en verde
en los tres casos, y en el tercero el código contenía una guarda explícita que
capturaba un caso de cada siete sin que nadie se diera cuenta.

> Una batería de tests prueba los casos en los que pensaste. Los límites de un
> modelo se encuentran atacándolo, no releyéndolo.

---

## 12. Lo esencial

- **El paso creativo es replantear la recuperación como descenso.** Una vez que
  las memorias son mínimos de un paisaje, la ausencia de clave, la degradación
  gradual y la ausencia de búsqueda salen todas gratis en vez de ser
  características que implementas.
- **La energía está forzada.** Solo interacciones, invariante bajo
  $s \to -s$, el orden más bajo que funciona $\Rightarrow$
  $E = -\tfrac12 s^{\mathsf T}Ws$.
- **Hebb también está forzada.** Local, simétrica, invariante de signo, aditiva
  $\Rightarrow$ $W_{ij} \propto \sum_{\mu} p^{\mu}_i p^{\mu}_j$. Es una
  derivación, no un postulado.
- **$\Delta E = -\Delta s_k g_k$ es toda la teoría**, y $g_k$ es el campo de
  *todos los demás*. La diagonal nula es lo que hace que la unidad se alinee
  con $g_k$ en vez de con $g_k$ más ella misma.
- **La convención de empate cierra la demostración.** Mantener el valor cuando
  $g_k = 0$ hace que todo volteo real sea estrictamente cuesta abajo, y lo
  estricto es lo que prohíbe los ciclos en un espacio de estados finito.
- **La simetría y la diagonal nula son premisas, no higiene.** Rompe cualquiera
  de las dos y la dinámica medida cicla o sube.
- **Las actualizaciones síncronas también tienen un teorema**, sobre pares de
  estados — período 1 o 2, nunca 3. "Sin garantía" es la lectura perezosa.
- **La servilleta es exactamente correcta sobre el primer paso e incorrecta
  sobre el punto fijo.** $Q(1/\sqrt{\alpha})$ coincide hasta tres decimales y
  falla la avalancha por 20×. La realimentación hace transiciones de fase, y
  las transiciones de fase son invisibles para las estimaciones de primer
  orden.
- **La capacidad es una propiedad de la pregunta**: 23, 67 o 79 patrones en
  $N=576$ según qué fallo toleres.
- **Las cuencas colapsan mucho antes que la capacidad.** En $\alpha_c$ las
  memorias son estables e inalcanzables. Mide cuencas, no estabilidad.
- **$\alpha_c = 0.138$ acusa a Hebb, no a la arquitectura.** Los acoplamientos
  óptimos alcanzan $\alpha = 2$ — un factor de 14 dejado sobre la mesa por
  insistir en que la regla sea local y de una sola pasada.
- **Convergencia no es corrección.** Los mínimos espurios superan en número a
  las memorias, se alcanzan con confianza, y la energía cae monótonamente todo
  el camino hasta el equivocado.

---

## 13. Preguntas abiertas

Cosas que este documento deliberadamente no responde, aproximadamente en orden
de cuánto enseñarían:

- **¿Qué compra la temperatura finita?** Esta dinámica es Metropolis en
  $T = 0$: solo se aceptan los movimientos que mejoran, así que gana el primer
  valle. Sube la temperatura y el mismo paisaje se convierte en una máquina de
  Boltzmann, y los mínimos espurios de §10.3 pasan a ser escapables. El
  argumento del libro de que el muestreo y la optimización son la misma
  operación a dos temperaturas es exactamente este modelo, y está a un
  parámetro de distancia.
- **¿Hasta dónde llegan de verdad las mejores reglas de almacenamiento?** La
  pseudoinversa alcanza $\alpha = 1$ y la cota de Gardner es 2. Implementar la
  regla de proyección y medir dónde colapsan *sus* cuencas separaría "los
  acoplamientos no pueden guardar más" de "Hebb no puede encontrarlo"
  experimentalmente y no por cita.
- **¿Qué aspecto tiene el paisaje entre los mínimos?** Toda afirmación de aquí
  es sobre puntos fijos. Nada en la entrada mide alturas de barrera, formas de
  cuenca, ni cómo las cuencas teselan el hipercubo — y la geometría de las
  cuencas es lo que de verdad determina si el recuerdo funciona.
- **¿Por qué la correlación ahonda los pozos y arruina el recuerdo?** Ambas
  cosas se miden en §10.1 y §10.3 y el mecanismo que las conecta no se deriva
  en ninguna parte de este documento.
- **¿Dónde compra exactamente su capacidad la energía de orden superior?** Las
  memorias asociativas densas alcanzan $N^{k-1}$, y la capa Hopfield moderna
  alcanza exponencialmente muchos patrones y resulta ser la atención. Esa es
  una entrada aparte, y empieza relajando la única palabra "cuadrática" de
  §6.2.

---

## 14. Referencias

**Fundacionales**

- **Hopfield, J. J.** *Neural networks and physical systems with emergent
  collective computational abilities.* PNAS **79**, 2554–2558 (1982).
  [enlace](https://www.pnas.org/doi/10.1073/pnas.79.8.2554) — el artículo.
- **Little, W. A.** *The existence of persistent states in the brain.*
  Mathematical Biosciences **19**, 101–120 (1974).
  [enlace](https://doi.org/10.1016/0025-5564(74)90031-5) — el modelo síncrono,
  ocho años antes.
- **Hebb, D. O.** *The Organization of Behavior* (1949). La regla de
  aprendizaje, en palabras, treinta y tres años antes de la red.
- **Hopfield, J. J.** *Neurons with graded response have collective
  computational properties like those of two-state neurons.* PNAS **81**,
  3088–3092 (1984). [enlace](https://www.pnas.org/doi/10.1073/pnas.81.10.3088)

**Capacidad — la parte que necesitó mecánica estadística**

- **Amit, D. J., Gutfreund, H. & Sompolinsky, H.** *Storing infinite numbers of
  patterns in a spin-glass model of neural networks.* Physical Review Letters
  **55**, 1530–1533 (1985).
  [enlace](https://doi.org/10.1103/PhysRevLett.55.1530) — de donde sale el
  $0.138$.
- **Amit, D. J., Gutfreund, H. & Sompolinsky, H.** *Statistical mechanics of
  neural networks near saturation.* Annals of Physics **173**, 30–67 (1987).
- **McEliece, R. J., Posner, E. C., Rodemich, E. R. & Venkatesh, S. S.** *The
  capacity of the Hopfield associative memory.* IEEE Transactions on
  Information Theory **33**, 461–482 (1987).
  [enlace](https://doi.org/10.1109/TIT.1987.1057328) — $N/(4\ln N)$.
- **Gardner, E.** *The space of interactions in neural network models.*
  Journal of Physics A **21**, 257–270 (1988).
  [enlace](https://doi.org/10.1088/0305-4470/21/1/030) — $\alpha_{\max}=2$ para
  acoplamientos óptimos. El artículo que separa la regla de la arquitectura.

**Dinámica**

- **Goles-Chacc, E., Fogelman-Soulié, F. & Pellegrin, D.** *Decreasing energy
  functions as a tool for studying threshold networks.* Discrete Applied
  Mathematics **12**, 261–277 (1985).
  [enlace](https://doi.org/10.1016/0166-218X(85)90029-0) — período 1 o 2 bajo
  actualizaciones en paralelo, y la función de Lyapunov de pares de §7.2.
- **Cohen, M. A. & Grossberg, S.** *Absolute stability of global pattern
  formation and parallel memory storage by competitive neural networks.* IEEE
  Transactions on Systems, Man and Cybernetics **13**, 815–826 (1983). El
  resultado de Lyapunov en tiempo continuo.

**Mejores reglas de almacenamiento**

- **Personnaz, L., Guyon, I. & Dreyfus, G.** *Information storage and retrieval
  in spin-glass like neural networks.* Journal de Physique Lettres **46**,
  359–365 (1985). La regla de la pseudoinversa (proyección), $\alpha = 1$.
- **Storkey, A.** *Increasing the capacity of a Hopfield network without
  sacrificing functionality.* ICANN (1997). Local e incremental, y mejor que
  Hebb.

**Optimización y la conexión con el vidrio de espín**

- **Hopfield, J. J. & Tank, D. W.** *Neural computation of decisions in
  optimization problems.* Biological Cybernetics **52**, 141–152 (1985).
  [enlace](https://doi.org/10.1007/BF00339943)
- **Sherrington, D. & Kirkpatrick, S.** *Solvable model of a spin-glass.*
  Physical Review Letters **35**, 1792–1796 (1975). La física que se importó.
- **Kirkpatrick, S., Gelatt, C. D. & Vecchi, M. P.** *Optimization by simulated
  annealing.* Science **220**, 671–680 (1983). El mismo paisaje, con la
  temperatura vuelta a encender.

**A dónde fue después**

- **Krotov, D. & Hopfield, J. J.** *Dense associative memory for pattern
  recognition.* NeurIPS (2016). [enlace](https://arxiv.org/abs/1606.01164)
- **Ramsauer, H. et al.** *Hopfield Networks is All You Need.* arXiv:2008.02217
  (2020). [enlace](https://arxiv.org/abs/2008.02217) — la capa Hopfield moderna
  es el mecanismo de atención.
- **Hinton, G. E. & Sejnowski, T. J.** *Optimal perceptual inference.* CVPR
  (1983). La máquina de Boltzmann: este modelo en $T \gt 0$.

**Libros**

- **Hertz, J., Krogh, A. & Palmer, R. G.** *Introduction to the Theory of
  Neural Computation* (1991), caps. 2–3. La derivación más clara de todo lo que
  hay en §6 y §8.
- **Amit, D. J.** *Modeling Brain Function: The World of Attractor Neural
  Networks* (1989). La mecánica estadística completa.
- **MacKay, D. J. C.** *Information Theory, Inference and Learning Algorithms*
  (2003), cap. 42. La lectura teórico-informacional de la capacidad, y el mejor
  relato breve de por qué es lo que es.

---

*Código: [`../model.py`](../model.py) y [`../methods/`](../methods/) ·
Entrada: [`../README.md`](../README.md) · Arquitectura de todo el repo:
[`docs/architecture.md`](../../docs/architecture.md)*
