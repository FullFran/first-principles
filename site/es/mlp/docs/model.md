<!-- translated-from: db8634b7e6c9 -->

# Aprender una función que nadie escribió

> La derivación que hay detrás de [`mlp/`](../README.md), construida desde el
> problema y no desde la fórmula. Lee esto si quieres saber *por qué* las
> ecuaciones de `mlp/model.py` son esas y no otras.

Este documento sigue un ciclo, y el ciclo es lo que importa:

```
phenomenon → question → order of magnitude → assumptions → minimal model
   → equations → scale analysis → closed forms → simulation → validation
   → limits of the model → next question
```

El centro es lo que enseña una carrera. Los dos extremos —plantear la pregunta
y saber dónde se detiene el modelo— son lo que de verdad separa a quien
resuelve problemas nuevos de quien aplica fórmulas. Así que aquí los dos
extremos se llevan el espacio.

**Contenido**

1. [El fenómeno](#1-el-fenómeno)
2. [Para qué sirve esto](#2-para-qué-sirve-esto)
3. [Antes de calcular](#3-antes-de-calcular)
4. [Por qué falla la respuesta ingenua](#4-por-qué-falla-la-respuesta-ingenua)
5. [El modelo mínimo](#5-el-modelo-mínimo)
6. [Las ecuaciones](#6-las-ecuaciones)
7. [Un gradiente, tres reglas de paso](#7-un-gradiente-tres-reglas-de-paso)
8. [Análisis de escalas: fan-in y la forma del valle](#8-análisis-de-escalas-fan-in-y-la-forma-del-valle)
9. [Formas cerradas que vale la pena memorizar](#9-formas-cerradas-que-vale-la-pena-memorizar)
10. [Lo que mostró la simulación](#10-lo-que-mostró-la-simulación)
11. [Dónde el modelo deja de ser cierto](#11-dónde-el-modelo-deja-de-ser-cierto)
12. [Lo esencial](#12-lo-esencial)
13. [Preguntas abiertas](#13-preguntas-abiertas)
14. [Referencias](#14-referencias)

---

## 1. El fenómeno

Aquí hay algo que sabes hacer y no sabes explicar. Alguien te enseña cuarenta
fotografías de escritura a mano y te pregunta cuáles dicen "7". Las aciertas
todas. Ahora escribe la regla que usaste. No una descripción: una regla, lo
bastante precisa como para que otra persona pudiera seguirla sin haber visto
nunca un 7.

No puedes. Nadie puede. Y aun así la regla está claramente *ahí dentro*, porque
la aplicas en una décima de segundo y coincides con todos los demás que lo
intentan.

Esa es la situación de la que trata esta entrada: **una función de la que
puedes dar ejemplos y que no puedes escribir.** La jugada es dejar de intentar
escribirla y escribir en su lugar una familia de funciones lo bastante amplia
como para contener algo cercano a ella, más un procedimiento para buscar dentro
de esa familia usando solo los ejemplos.

> **La pregunta.**
> Una familia de funciones $f_\theta$ con $P$ números ajustables $\theta$, y una
> pérdida $L(\theta)$ que mide lo mal que $f_\theta$ reproduce los ejemplos.
> **¿Cómo encuentras un $\theta$ que haga $L$ pequeña?**

La respuesta que da todo el mundo es "baja por la pendiente", y es correcta. Lo
que hace interesante el tema es que las dos preguntas obvias que vienen después
—*cuánto cuesta saber hacia dónde se baja* y *cuántos pasos hace falta bajar*—
tienen respuestas nada obvias, y son las que deciden si algo de esto funciona.

Esas dos preguntas son [§4](#4-por-qué-falla-la-respuesta-ingenua) y
[§8](#8-análisis-de-escalas-fan-in-y-la-forma-del-valle).

---

## 2. Para qué sirve esto

### 2.1 Es todo el aprendizaje automático moderno, y no es una exageración

Todo modelo grande entrenado en la última década es este documento más
ingeniería. La arquitectura cambia —convoluciones, atención, conexiones
residuales—, la pérdida cambia y el optimizador recibe refinamientos. La parte
que no cambia es: define una función diferenciable, define una pérdida, obtén
el gradiente por acumulación inversa, da un paso. Un transformer con
$10^{12}$ parámetros se entrena con las cuatro ecuaciones de
[§6.3](#63-las-cuatro-líneas).

El Premio Nobel de Física de 2024 fue para Hopfield y Hinton, y la mitad de
Hinton es en buena medida por haber hecho funcionar ese bucle.

### 2.2 La familia sí es lo bastante amplia

El teorema de aproximación universal dice que una red con una capa oculta y una
activación no polinómica puede aproximar cualquier función continua sobre un
compacto con la precisión que quieras, si tiene suficientes unidades. Cybenko
lo demostró para sigmoides en 1989; Hornik lo generalizó en 1991; Leshno et al.
precisaron que la condición real es que no sea polinómica en 1993.

Vale la pena saber con precisión qué compra eso, porque se vende de más
constantemente. Dice que tal red **existe**. No dice nada sobre cuántas
unidades, nada sobre cómo encontrarla y nada sobre si la que encuentres a
partir de datos finitos funcionará con cualquier otra cosa. El teorema elimina
una excusa y deja intacto todo problema difícil.

### 2.3 La acumulación inversa es más antigua y más amplia que las redes neuronales

Lo que deriva §6 es diferenciación automática en modo inverso, especializada a
una pila de capas. La técnica general precede en décadas a su uso en
aprendizaje y se usa mucho más allá de él: métodos adjuntos en dinámica de
fluidos e inversión sísmica, análisis de sensibilidad en modelos climáticos,
optimización de formas en aerodinámica y toda simulación física que necesite la
derivada de una salida respecto de diez mil entradas.

La regla práctica que hace que valga la pena aprenderlo una vez, bien: **el
modo inverso te da el gradiente de un escalar respecto de $P$ entradas por un
múltiplo constante del coste de evaluar la función.** El modo directo te da la
derivada de $P$ salidas respecto de una entrada por el mismo precio. Cuál
quieres lo decide la forma de tu problema, no la moda.

### 2.4 Historia

Los niveles de verificación siguen la convención del libro: **A** es
documentado, idealmente desde una fuente primaria; **B** es una reconstrucción;
**C** es una historia que se cuenta en todas partes y que no he podido
documentar.

::: **Publicado tres veces antes de que nadie se diera cuenta** · *Verificación:
A — la historia anotada de Schmidhuber (2015) traza la cadena y todas las
fuentes primarias se conservan.*

La acumulación inversa la publicó **Seppo Linnainmaa en 1970**, en una tesis de
máster finlandesa, y no trataba de aprendizaje en absoluto. Era un método
general para seguir el error de redondeo acumulado de un algoritmo: necesitas
la sensibilidad de la salida a cada cantidad intermedia, y la forma eficiente
de obtenerla es barrer hacia atrás. La regla de la cadena, en la dirección que
compensa, cuatro años antes de que nadie la aplicara a una red.

**Paul Werbos** la aplicó a redes en 1974, en su tesis doctoral de Harvard. No
llegó a ninguna parte. Él ha dicho que la razón fue que después de *Perceptrons*
nadie escuchaba ningún argumento sobre redes neuronales.

La técnica se hizo famosa con **Rumelhart, Hinton y Williams en 1986**,
dieciséis años después de Linnainmaa, en cuatro páginas de *Nature*.

La lección no es que el artículo de 1986 no lo mereciera: hizo la idea
utilizable, mostró para qué servía y demostró que las capas ocultas aprendían
*representaciones*, que es la parte que importaba. La lección es que **una idea
publicada en el campo equivocado, en el idioma equivocado y en el momento
equivocado todavía no es una idea que nadie tenga**, y que la distancia entre
ambas cosas puede ser de dieciséis años.

::: **Un artículo de cuatro páginas y un invierno de veintiocho años** ·
*Verificación: B — la afirmación causal sobre* Perceptrons *la discuten los
historiadores; la cronología no.*

La historia estándar es que *Perceptrons* (1969), de Minsky y Papert, demostró
que una red de una sola capa no puede calcular XOR, mató el campo, y que la
retropropagación lo revivió en 1986.

La cronología es correcta. La causalidad se discute: Minsky y Papert fueron
explícitos en que su resultado no cubría las redes multicapa, los patrones de
financiación son más desordenados que el relato, y varios historiadores han
rebatido la lectura de que "el libro mató un campo".

Pero algo sí se detuvo, y el contenido *matemático* es indiscutible y está en
esta entrada: una composición de mapas afines es afín, así que la profundidad
sin una no linealidad no compra nada
([§6.1](#61-el-mapa-hacia-delante)). XOR necesita una frontera curva. Todo lo
posterior a 1986 es lo que puedes hacer una vez que sabes entrenar la capa
intermedia.

### Artículos que vale la pena leer

| Referencia | Por qué |
|---|---|
| [Rumelhart, Hinton & Williams, *Nature* **323**, 533 (1986)](https://www.nature.com/articles/323533a0) | El artículo que lo asentó. Cuatro páginas |
| Linnainmaa (1970), tesis de máster, Univ. Helsinki | Acumulación inversa, dieciséis años antes, en otro campo |
| [Werbos (1974), tesis doctoral de Harvard](https://www.researchgate.net/publication/35657389) | Aplicada a redes, también ignorada |
| [Cybenko, *Math. Control Signals Systems* **2**, 303 (1989)](https://doi.org/10.1007/BF02551274) | Una capa oculta basta: existencia, y nada más |
| [Leshno et al., *Neural Networks* **6**, 861 (1993)](https://doi.org/10.1016/S0893-6080(05)80131-5) | La condición real es que no sea polinómica |
| [Glorot & Bengio, *AISTATS* (2010)](https://proceedings.mlr.press/v9/glorot10a.html) | Por qué la escala de inicialización es $1/\sqrt{\text{fan}}$ y no una cuestión de gusto |
| [He et al., *ICCV* (2015)](https://arxiv.org/abs/1502.01852) | El mismo argumento rehecho para ReLU, que da el factor 2 |
| [Kingma & Ba, arXiv:1412.6980](https://arxiv.org/abs/1412.6980) | Adam. Lee §2 y después lee la fe de erratas de la demostración de convergencia |
| [Reddi, Kale & Kumar, *ICLR* (2018)](https://arxiv.org/abs/1904.09237) | La demostración del artículo de Adam es incorrecta, y Adam sigue funcionando |
| [Baydin et al., *JMLR* **18**, 1 (2018)](https://jmlr.org/papers/v18/17-468.html) | Diferenciación automática en serio: de qué es un caso particular la retropropagación |

Libros: *Neural Networks and Deep Learning* de Nielsen, cap. 2, para la
derivación más clara de §6; Goodfellow, Bengio & Courville, cap. 6 y 8;
Nocedal & Wright para la mitad de optimización hecha en serio.

---

## 3. Antes de calcular

La regla del libro: **escribe un número antes de leer la sección siguiente.** El
aprendizaje está en la distancia entre tu número y el real, y esa distancia no
existe si no te comprometiste.

> 1. Una red con $P$ parámetros. Quieres $\partial L/\partial\theta_i$ para cada
>    uno de ellos. **¿Cuántas veces tienes que evaluar la pérdida?**
>    ¿$P$? ¿$2P$? ¿Menos?
> 2. Una capa oculta con 1024 entradas por unidad. **¿Cómo de grandes deben ser
>    sus pesos?** El cuaderno de 2024 al que sustituye esta entrada usaba una
>    dispersión de 0.577 en todas las anchuras. ¿Qué hace eso aquí?
> 3. Multiplicas una característica de entrada por 100 y no cambias nada más.
>    Los mismos puntos, las mismas etiquetas, la misma forma separadora.
>    **¿Cuántos pasos más necesita el descenso por gradiente?** ¿El doble?
>    ¿Diez veces?

Respuestas en [§4](#4-por-qué-falla-la-respuesta-ingenua) y
[§8](#8-análisis-de-escalas-fan-in-y-la-forma-del-valle). La primera es la
razón de que exista la retropropagación. La tercera tiene una respuesta que no
es un número.

---

## 4. Por qué falla la respuesta ingenua

Una derivada es un límite de un cociente de diferencias, y tienes una
computadora, así que:

$$\frac{\partial L}{\partial\theta_i} \approx
\frac{L(\theta + \varepsilon e_i) - L(\theta - \varepsilon e_i)}{2\varepsilon}$$

Esto es correcto. Es contra lo que [`tests/test_model.py`](../tests/test_model.py)
contrasta la retropropagación, y si alguna vez discrepan, lo que está mal es la
retropropagación. Así que la pregunta no es si funciona.

**La pregunta es cuánto cuesta, y la respuesta es un desastre.**

Cada parámetro necesita su propio par de evaluaciones, así que un gradiente
completo cuesta $2P$ pasadas hacia delante. La retropropagación cuesta una
pasada hacia delante y una pasada hacia atrás —un múltiplo constante de una
sola evaluación— **sea cual sea $P$.** Eso no es un ahorro de factor constante.
Es otra clase de complejidad, y es toda la razón de que exista el campo.

![Izquierda: tiempo de un gradiente completo frente al número de parámetros,
log-log, para diferencias finitas y para retropropagación. Derecha: el mayor
error relativo de un cociente de diferencias frente al tamaño de paso, para
diferencias centradas y hacia delante.](figures/gradient_cost.png)

**Qué concluir:** medido sobre la propia red de esta entrada, la
retropropagación es 21× más rápida con 37 parámetros y **4147× más rápida con
4417**, y la razón no tiene techo: el panel izquierdo es una recta contra otra
casi plana. Un modelo con $10^9$ parámetros necesitaría $2\times10^9$ pasadas
hacia delante por paso de gradiente; a un milisegundo cada una, son 23 días
para un paso.

**Respuesta a la pregunta 1: una vez**, con buena aproximación. Una pasada
hacia delante y una pasada hacia atrás, independientemente de $P$.

**Y encima no es preciso.** El panel derecho es la otra mitad del argumento, y
es la que la gente olvida. Un cociente de diferencias queda atrapado entre dos
errores que tiran en direcciones opuestas:

$$\text{error} \simeq \underbrace{\frac{\varepsilon^2}{6}\left|L'''\right|}_{\text{truncation}}
\thinspace + \thinspace \underbrace{\frac{\epsilon_{\text{mach}}|L|}{\varepsilon}}_{\text{cancellation}}$$

Un paso demasiado grande y el cociente no es la derivada. Demasiado pequeño y
$L(\theta+\varepsilon)$ y $L(\theta-\varepsilon)$ coinciden en sus primeros
dígitos, la resta los tira, y lo que sobrevive es ruido de redondeo dividido
por un número pequeño. Medido aquí, lo mejor que consigue cualquier paso es un
error relativo de $10^{-8}$ para diferencias centradas y $4\times10^{-6}$ para
las de hacia delante.

**La retropropagación no tiene ese suelo, porque nunca toma diferencia
alguna.** Es exacta salvo por la aritmética. Vale la pena decirlo sin rodeos:
el método lento es además el impreciso, y no hay régimen en el que lo prefieras
salvo el que importa: comprobar que el rápido es correcto.

---

## 5. El modelo mínimo

Cada supuesto de abajo compra una simplificación concreta, y cada uno de ellos
falla en algún sitio real. Enumerarlos no es ceremonia: la lista *es* el
dominio de validez, y es lo que los tests nunca pueden decirte.

| Supuesto | Qué compra | Dónde se rompe |
|---|---|---|
| Las capas son **mapas afines densos** | Una matriz por capa; el gradiente es un matmul | Convoluciones, atención, cualquier cosa con pesos compartidos |
| La no linealidad es **elemento a elemento** | $f'(z)$ es un vector, así que el jacobiano es diagonal y nunca se materializa | Softmax, capas de normalización: ambas acoplan unidades entre sí |
| La red es una **cadena** | Un $\delta$ por capa, propagado en orden | Conexiones de salto, ramificaciones, recurrencia |
| Todo es **diferenciable** | La regla de la cadena se aplica siquiera | ReLU exactamente en cero; umbrales duros; muestreo |
| La pérdida es una **suma sobre muestras independientes** | Los gradientes promedian; los minilotes son estimaciones insesgadas | Pérdidas de ranking, pérdidas contrastivas, cualquier cosa por pares |
| Los parámetros son **reales sin restricciones** | El descenso simple es una jugada legal | Restricciones, cuantización, estructura discreta |
| Precisión completa en todo momento | No hacen falta trucos de escalado | Entrenamiento en fp16, donde el gradiente hace underflow |
| **Una sola tasa de aprendizaje fija** | Un solo número sobre el que razonar | Todo entrenamiento real usa un calendario |
| La pérdida de entrenamiento es el objetivo | El bucle puede parar con ella | Generalización: ver [§11](#11-dónde-el-modelo-deja-de-ser-cierto) |

Ese es el modelo. Fíjate en lo que **no** supone: no supone que la red sea poco
profunda, ni que las activaciones sean sigmoides, ni que la pérdida sea el
error cuadrático. Profundidad, activación y pérdida son intercambiables dentro
de este marco, que es exactamente por lo que el marco sobrevivió a toda
elección concreta hecha en 1986.

---

## 6. Las ecuaciones

### 6.1 El mapa hacia delante

Una capa es un mapa afín seguido de una no linealidad elemento a elemento:

$$a^{0} = x, \qquad z^{l} = a^{l-1}W^{l} + b^{l}, \qquad a^{l} = f_l\negthinspace\left(z^{l}\right)$$

con $x$ de forma (muestras, características) y $W^{l}$ de forma (fan-in,
fan-out). Las muestras corren a lo largo del primer eje en todo momento, lo
cual es una convención y solo importa porque ser inconsistente con ella es la
fuente más común de errores silenciosos de forma en redes escritas a mano.

**Por qué la no linealidad no es opcional.** Compón dos mapas afines y obtienes
un mapa afín:

$$\left(xW^{1} + b^{1}\right)W^{2} + b^{2}
= x\left(W^{1}W^{2}\right) + \left(b^{1}W^{2} + b^{2}\right)$$

Cien capas de `identity` son una sola matriz, y ninguna cantidad de profundidad
compra una frontera de decisión curva. Esa afirmación es un test —
`test_a_network_of_identities_is_exactly_a_linear_map` — precisamente porque es
la razón de que exista cada una de las otras líneas.

### 6.2 La regla de la cadena, en la dirección que compensa

Queremos $\partial L/\partial W^{l}$ para cada $l$. La ruta directa es
preguntar cómo depende $L$ de $W^{l}$ empujando hacia delante, y eso es el
desastre $O(P)$ de [§4](#4-por-qué-falla-la-respuesta-ingenua), porque la
influencia de cada parámetro recorre su propio camino hasta la salida.

Invierte la dirección. Define

$$\delta^{l} \equiv \frac{\partial L}{\partial z^{l}}$$

— la sensibilidad de la pérdida a la *preactivación* de la capa $l$. Ese es
todo el truco, y la razón de que funcione es que **cada parámetro de la capa
$l$ influye en la pérdida solo a través de $z^{l}$.** Una vez que conoces
$\delta^{l}$, los parámetros de esa capa están a un paso, y las capas de abajo
están a un paso de $\delta^{l}$. Nada se calcula dos veces.

Empieza en la salida. $L$ depende de $z^{L}$ a través de $a^{L} = f_L(z^{L})$, y
$f_L$ es elemento a elemento, así que su jacobiano es diagonal y la regla de la
cadena es un producto y no una multiplicación de matrices:

$$\delta^{L} = \frac{\partial L}{\partial a^{L}} \odot f_L'\negthinspace\left(z^{L}\right)$$

Ahora baja un paso. $z^{l}$ influye en $L$ solo a través de $a^{l}$, que entra
en $z^{l+1} = a^{l}W^{l+1} + b^{l+1}$. Por tanto

$$\frac{\partial L}{\partial a^{l}} = \delta^{l+1}\left(W^{l+1}\right)^{\mathsf T},
\qquad
\delta^{l} = \left(\delta^{l+1}\left(W^{l+1}\right)^{\mathsf T}\right)
\odot f_l'\negthinspace\left(z^{l}\right)$$

y por último, como $z^{l} = a^{l-1}W^{l} + b^{l}$ es lineal en los parámetros,

$$\frac{\partial L}{\partial W^{l}} = \left(a^{l-1}\right)^{\mathsf T}\delta^{l},
\qquad
\frac{\partial L}{\partial b^{l}} = \sum_{\text{samples}}\delta^{l}$$

### 6.3 Las cuatro líneas

$$\boxed{\enspace
\begin{aligned}
\delta^{L} &= \partial L/\partial a^{L} \odot f_L'\negthinspace\left(z^{L}\right)\cr
\delta^{l} &= \left(\delta^{l+1}\left(W^{l+1}\right)^{\mathsf T}\right)\odot f_l'\negthinspace\left(z^{l}\right)\cr
\partial L/\partial W^{l} &= \left(a^{l-1}\right)^{\mathsf T}\delta^{l}\cr
\partial L/\partial b^{l} &= \textstyle\sum \delta^{l}
\end{aligned}\enspace}$$

Eso es [`model.gradients()`](../model.py), literalmente, en ocho líneas de
Python. **Nada en ello es una elección.** Dadas la arquitectura y la pérdida, el
gradiente queda determinado: no hay respuesta correcta alternativa, ni ajuste,
ni aproximación. Por eso mismo pertenece al archivo de dominio, junto al mapa
hacia delante, y por eso lo que *haces* con el gradiente está en otro sitio.

Fíjate también en lo que cuesta la pasada hacia atrás: un matmul contra
$W^{l+1}$ y otro contra $a^{l-1}$ por capa, que es el mismo orden que costó la
pasada hacia delante. De ahí el múltiplo constante de
[§4](#4-por-qué-falla-la-respuesta-ingenua), y de ahí todo el tema.

### 6.4 Tres trampas que no se anuncian

**$f'$ toma $z$, no $a$.** Para una sigmoide la derivada cumple
$\sigma'(z) = \sigma(z)\left(1 - \sigma(z)\right) = a(1-a)$,
así que puedes escribirla en términos de la
activación y ahorrarte un recálculo. Funciona para la sigmoide y funciona para
la tanh. Hazlo, y en el momento en que alguien cambie la activación la derivada
estará mal en silencio: y seguirá entrenando, solo que mal. La versión de 2024
hacía exactamente esto, y tenía una `relu` definida sin derivada alguna,
esperando. Aquí `f_prime(z)` toma la preactivación en todos los casos, y hay un
test por activación que la contrasta con una derivada numérica.

**La pérdida y su gradiente tienen que ser la misma función.** Si la pérdida
promedia sobre muestras $\times$ salidas mientras su gradiente divide solo por
las muestras, ambos discrepan exactamente en la anchura de salida. Nada
revienta, el entrenamiento sigue descendiendo, y la tasa de aprendizaje
efectiva está silenciosamente equivocada por un factor de 2 o 3. **Ese fallo
estuvo en esta entrada**, y la comprobación por diferencias finitas lo encontró
antes de que existiera un bucle de entrenamiento, con errores relativos de
exactamente 1.0 y 2.0, que es la firma de un error de factor constante: un
gradiente $k$ veces demasiado grande aparece como $|k-1|$.

**Media o suma, y sé consistente.** $\partial L/\partial b^{l}$ es una suma
sobre muestras porque la propia definición de $L$ ya lleva el $1/n$. Promedia
uno y suma el otro y los dos grupos de parámetros entrenan a ritmos que
difieren en el tamaño del lote: 500× en el cuaderno al que esto sustituye. Un
test lo fija afirmando que la pérdida no cambia cuando se duplica el lote.

---

## 7. Un gradiente, tres reglas de paso

Todo lo anterior produce un vector $g$. Qué hacer con él es una elección
genuinamente abierta, y aquí es donde empieza `methods/`.

$$\underbrace{\theta \leftarrow \theta - \eta\thinspace g}_{\text{sgd}}
\qquad
\underbrace{v \leftarrow \beta v + g,\quad \theta \leftarrow \theta - \eta\thinspace v}_{\text{momentum}}
\qquad
\underbrace{\theta \leftarrow \theta - \eta\thinspace\frac{\hat m}{\sqrt{\hat v} + \varepsilon}}_{\text{adam}}$$

**El descenso simple** sigue el gradiente literalmente. Su debilidad es pura
geometría: el gradiente es perpendicular a las curvas de nivel, lo cual apunta
al mínimo solo cuando las curvas son círculos.

**Momentum** filtra el gradiente con un paso bajo. A lo largo de un valle, los
gradientes sucesivos coinciden y la velocidad se acumula hacia
$\eta/(1-\beta)$: una amplificación de 10× con $\beta = 0.9$. A través del
valle se alternan y se cancelan. La oscilación *es* la componente de alta
frecuencia, y el filtrado es todo el mecanismo.

**Adam** mantiene una media y una media cuadrática móviles por parámetro y
divide por la raíz de la segunda. Eso hace que el tamaño de paso de cada
coordenada sea independiente de la magnitud de su gradiente, lo cual es un
precondicionador diagonal estimado sobre la marcha. La corrección de sesgo
$1/(1-\beta^t)$ importa más de lo que parece: $m$ y $v$ empiezan en cero, así
que las primeras medias quedan arrastradas hacia cero, y sin la corrección los
primeros pasos son demasiado pequeños.

**Una nota sobre la demostración de convergencia de Adam.** El artículo de 2014
contiene una. Es incorrecta: Reddi, Kale y Kumar (2018) exhiben un problema
convexo en el que Adam no converge, y el fallo está en cómo la demostración
trata el término de segundo momento. Adam sigue siendo uno de los optimizadores
más usados del mundo. Vale la pena detenerse ahí: **un método puede ser
enormemente útil y no tener ninguna garantía válida, y saber cuál de las dos
cosas tienes es una pregunta distinta de si usarlo.**

### 7.1 Qué puede y qué no puede exigir el contrato

[`tests/test_methods.py`](../tests/test_methods.py) está parametrizado sobre
todos los métodos registrados y afirma lo que todos ellos deben hacer: reducir
la pérdida, separar los anillos, ser reproducibles a partir de una semilla,
preservar las formas, recibir un gradiente idéntico e informar de por qué
pararon.

Deliberadamente **no** afirma nada sobre la velocidad ni sobre sobrevivir a un
problema mal escalado. Añadir cualquiera de las dos cosas parecería rigor y
sería afirmar algo falso sobre al menos un método, que es la misma decisión de
diseño que la de [`hopfield/`](../../hopfield/README.md) al negarse a exigir
descenso de energía a su calendario síncrono.

---

## 8. Análisis de escalas: fan-in y la forma del valle

Dos números deciden si un entrenamiento funciona siquiera, y ninguno es la tasa
de aprendizaje.

### 8.1 La escala de los pesos la fija el fan-in

Una unidad calcula $z = \sum_{i=1}^{n} w_i x_i$ sobre $n = \text{fan-in}$
entradas. Si los $w_i$ son independientes con varianza $\sigma_w^2$ y los $x_i$
tienen varianza $\sigma_x^2$, **las varianzas se suman**:

$$\mathrm{Var}(z) = n\thinspace\sigma_w^2\thinspace\sigma_x^2$$

Para que $z$ mantenga la misma dispersión que $x$ capa tras capa —que es lo que
lo mantiene lejos de la parte plana de la activación— necesitamos

$$\boxed{\enspace\sigma_w = \frac{1}{\sqrt{n}}\enspace}$$

Eso es toda la inicialización de Xavier. ReLU descarta la mitad negativa y por
tanto reduce la varianza a la mitad, que es por lo que la inicialización de He
pone un 2 bajo la raíz. Ambas están en `model.initialise()`, y
`test_weight_scale_follows_one_over_root_fan_in` fija la ley y no la constante.

![Pendiente media de la activación en la capa oculta más profunda frente a la
anchura de capa, para el escalado correcto y para una dispersión fija de 0.577,
con las anchuras que usaba el cuaderno original sombreadas.](figures/initialisation.png)

**Qué concluir:** *respuesta a la pregunta 2.* Con $n = 1024$ la dispersión
correcta es $1/32 = 0.031$; un valor fijo de 0.577 es **18× demasiado grande**,
y la pendiente medida de la activación en la capa más profunda se desploma de
0.88 a 0.044. Pero mira la banda sombreada: con las cuatro y ocho unidades que
el cuaderno usaba de verdad, los dos esquemas están dentro de un factor de 1.4
y entrenaba perfectamente. **El fallo era invisible a la escala a la que se
escribió y fatal un orden de magnitud más arriba**, que es el tipo más caro.

### 8.2 El número de condición decide el número de pasos

Para un cuenco cuadrático con autovalores del hessiano
$\lambda_{\min}\dots\lambda_{\max}$ y $\kappa = \lambda_{\max}/\lambda_{\min}$,
el descenso por gradiente con el mejor paso fijo contrae la distancia al mínimo
en un factor

$$\frac{\lVert\theta_{k+1} - \theta^{\ast}\rVert}{\lVert\theta_k - \theta^{\ast}\rVert}
\simeq \frac{\kappa - 1}{\kappa + 1}$$

Con $\kappa = 1$ eso es cero: un paso. Con $\kappa = 1000$ es $0.998$, así que
necesitas miles. **El coste por paso no cambia; lo único que se mueve es el
número de pasos**, que es por lo que el condicionamiento duele tanto y es tan
fácil pasarlo por alto: nada en el perfil parece mal.

![Épocas necesarias para alcanzar una pérdida objetivo frente al estiramiento
aplicado a un eje de entrada, para las tres reglas de paso, log-log, con cruces
que marcan las ejecuciones que nunca la alcanzaron.](figures/conditioning.png)

**Qué concluir:** *respuesta a la pregunta 3: no hay número, porque no es una
ralentización, es un precipicio.* Entre 30× y 100× tanto el descenso simple
como momentum pasan de unos cientos de épocas a no alcanzar nunca el objetivo,
mientras que Adam se degrada de forma gradual en todo el barrido, de 6 épocas a
156. Su normalización por coordenada es un precondicionador, y el
precondicionamiento es precisamente la defensa contra $\kappa$.

La lectura práctica no es "usa Adam". Es que **reescalar tus entradas es gratis
y precondiciona el problema directamente**, y que recurrir a un optimizador más
sofisticado para compensar datos sin normalizar es pagar por un arreglo que
podías haber tenido por una línea.

---

## 9. Formas cerradas que vale la pena memorizar

Esto es contra lo que contrastas el código. Contrastar dos métodos entre sí
demuestra que coinciden; contrastar contra una forma cerrada demuestra que son
*correctos*. Cada fila de aquí es un test en [`../tests/`](../tests/).

| Situación | Resultado |
|---|---|
| Pasada hacia delante | $z^{l} = a^{l-1}W^{l} + b^{l}$, $a^{l} = f_l(z^{l})$ |
| Sensibilidad de la salida | $\delta^{L} = \partial L/\partial a^{L}\odot f_L'(z^{L})$ |
| Recursión hacia atrás | $\delta^{l} = \left(\delta^{l+1}(W^{l+1})^{\mathsf T}\right)\odot f_l'(z^{l})$ |
| Gradiente de los pesos | $\partial L/\partial W^{l} = (a^{l-1})^{\mathsf T}\delta^{l}$ |
| Coste del gradiente | una pasada hacia delante y una hacia atrás, independiente de $P$ |
| Coste por diferencias | $2P$ pasadas hacia delante, con un suelo de error relativo cercano a $10^{-8}$ |
| Composición de mapas afines | afín: la profundidad sin una no linealidad no compra nada |
| Derivada de la sigmoide | $\sigma'(z) = \sigma(z)\left(1 - \sigma(z)\right)$ |
| Derivada de la tanh | $1 - \tanh^2(z)$ |
| Sigmoide $+$ BCE, fusionadas | $\delta^{L} = a^{L} - y$ exactamente; el $f'$ se cancela |
| Escala de Xavier | $\sigma_w = 1/\sqrt{n}$, a partir de $\mathrm{Var}(z) = n\sigma_w^2\sigma_x^2$ |
| Escala de He, para ReLU | $\sigma_w = \sqrt{2/n}$ |
| Contracción del descenso | $(\kappa-1)/(\kappa+1)$ por paso |
| Amplificación de momentum | $\eta/(1-\beta)$ a lo largo de una dirección consistente |
| Corrección de sesgo de Adam | dividir por $1 - \beta^{t}$ |

**Una advertencia sobre la fila diez.** Para una salida sigmoide bajo entropía
cruzada binaria el $f'$ se cancela analíticamente y $\delta^{L} = a - y$. Esta
entrada **no** las fusiona: calcula el genérico
$\partial L/\partial a \odot f'(z)$, que es
$\frac{a-y}{a(1-a)} \cdot a(1-a)$: matemáticamente idéntico y numéricamente
$0/0$ cuando la salida satura. Se recorta en lugar de fusionarse, lo cual es
honesto sobre el coste de mantener independientes la pérdida y la activación, y
es la razón de que [§11](#11-dónde-el-modelo-deja-de-ser-cierto) liste la
saturación en primer lugar.

---

## 10. Lo que mostró la simulación

La regla del libro: **predice antes de ejecutar.** Cada experimento aquí es una
predicción con un número pegado, no una gráfica para admirar. Dos de los tres
devolvieron algo distinto de lo predicho, y esos son los dos que vale la pena
leer.

### 10.1 Los anillos — [`circles.py`](../experiments/circles.py)

Predicción: las tres reglas separan los anillos, y discrepan en cuánto tardan.

```
    method   final loss   train acc  held-out acc   epochs to 0.15
      adam      0.02865       0.994         0.986                6
  momentum      0.00007       1.000         0.996                5
       sgd      0.00100       1.000         0.996               17
```

Discrepan en algo completamente distinto. **Adam es el peor de los tres**,
terminando 400× por encima de la pérdida de momentum, y la frontera de decisión
muestra por qué de un modo que el número no muestra.

![Fronteras de decisión de las tres reglas de paso sobre dos anillos
concéntricos, y sus curvas de pérdida en escala logarítmica.](figures/circles.png)

**Qué concluir:** momentum y el descenso simple encuentran ambos un círculo
suave, que es la forma correcta. Adam encuentra un **polígono angular con una
púa suelta que se escapa hacia una esquina**, y su curva de pérdida no deja
nunca de rebotar. Dividir por la raíz cuadrática media móvil mueve cada
coordenada más o menos lo mismo por pequeño que sea su gradiente: exactamente
el seguro que quieres en un problema mal escalado, y puro coste en uno bien
escalado, donde impide que la ejecución llegue a asentarse.

**Adam no es un optimizador mejor. Es un intercambio distinto**, y §8.2 es
donde ese intercambio compensa.

### 10.2 Condicionamiento — [`conditioning.py`](../experiments/conditioning.py)

Cubierto en [§8.2](#82-el-número-de-condición-decide-el-número-de-pasos). La
predicción se sostuvo: el mismo problema en un paisaje peor conformado cuesta
pasos y no aritmética. La sorpresa fue lo abrupto: un precipicio entre 30× y
100× en lugar de una pendiente.

### 10.3 Inicialización — [`initialisation.py`](../experiments/initialisation.py)

Predicción: `rand()*2-1` satura una pila **profunda**.

**Incorrecto, y vale la pena dejarlo registrado como incorrecto.** Medido, la
profundidad apenas importa y la anchura lo decide todo, porque esa dispersión
es 0.577 independientemente del fan-in mientras que la correcta encoge como
$1/\sqrt{n}$. La hipótesis se reescribió para ajustarse a la medición, y con
ella se reescribió el docstring de un test que afirmaba la historia de la
profundidad.

Lo que hace cuando falla es la mejor mitad:

```
              init  epochs   final loss  accuracy  saturated  stopped because
    1/sqrt(fan_in)     120      0.00030     1.000      0.000  ran out of epochs
        rand()*2-1       2     13.81552     0.500      1.000  loss stopped moving
```

Lee las dos últimas columnas juntas. **Todas y cada una de las salidas saturan
exactamente en 0 o en 1**, así que $f'(z)$ es exactamente cero, así que no
fluye gradiente, así que nada se mueve, y `solve.train` informa de
**convergido** tras dos épocas, con la pérdida habiendo *subido* de 3.74 a
13.82 y la exactitud en el azar. Nada lanza una excepción, nada avisa.

Ese es el caso que el docstring del bucle de entrenamiento se escribió para
nombrar: **convergido es una afirmación sobre que la pérdida dejó de moverse,
nunca sobre que la respuesta sea buena.** Un criterio de parada que no sabe
distinguir esas dos cosas informará de éxito en una red que no aprendió nada.

---

## 11. Dónde el modelo deja de ser cierto

La sección que más importa, y la que suele faltar.

### 11.1 Generalización — el supuesto que falla primero

Todo en este documento minimiza la pérdida **sobre los ejemplos que tienes**.
Nada en él dice nada sobre los ejemplos que no tienes.

Esa distancia no es un tecnicismo; es toda la diferencia entre ajustar y
aprender, y esta entrada está en el lado equivocado. `solve.train` para con la
pérdida de entrenamiento. `circles.py` imprime una exactitud sobre datos
reservados y ninguna parte del código la usa. No hay partición de validación en
el bucle, ni parada temprana, ni decaimiento de pesos, ni control de capacidad
de ningún tipo.

Los anillos son lo bastante fáciles como para que aquí no muerda —la exactitud
sobre datos reservados es 0.996 frente a 1.000 en el conjunto de entrenamiento—
y eso es suerte, no diseño. Apunta el mismo código a una tarea con más
parámetros que señal y llevará la pérdida de entrenamiento a cero mientras
empeora sin parar en aquello que querías, informando de números excelentes todo
el rato.

Esto tiene la misma forma que la advertencia del libro sobre optimizar un
sustituto: la pérdida es un modelo de lo que quieres, y optimizar un modelo de
lo que quieres con suficiente agresividad encontrará los lugares donde el
modelo y el deseo se separan.

### 11.2 El resto de la lista

| Límite | Qué ocurre en realidad | Esta entrada |
|---|---|---|
| Capas anchas, inicializador equivocado | Saturación total, gradiente cero, **convergido en el azar** | medido en §10.3 |
| Sigmoide saturada bajo BCE | El $\delta$ genérico es $0/0$; recortado en lugar de fusionado | recortado, documentado |
| Adam en un problema bien escalado | Peor pérdida final, frontera visiblemente angular | medido en §10.1 |
| Entradas estiradas más allá de ~30× | El descenso simple y momentum dejan de llegar | medido en §8.2 |
| ReLU exactamente en $z = 0$ | Derivada indefinida; el código devuelve 0 y los tests se saltan el pico | por convención |
| Unidades ReLU muertas | Una unidad atascada en $z \lt 0$ tiene gradiente cero para siempre | no detectado |
| Pilas profundas | El $\odot f'$ repetido encoge $\delta$ geométricamente | no modelado: sin residuales, sin normalización |
| Sobreajuste | La pérdida de entrenamiento baja, la exactitud sobre datos reservados no | no detectado, no defendido |
| fp16 o menos | El gradiente hace underflow y necesita escalado de la pérdida | no modelado |
| Pesos compartidos | Los gradientes deben acumularse entre usos | fuera de las premisas del modelo |

Dos de esas filas existen porque alguien **sondeó** en lugar de razonar: el
fallo de inicialización dependiente de la anchura, y el desajuste entre la
pérdida y su gradiente en §6.4. En ambos casos la suite estaba en verde y el
código parecía correcto.

> Una suite de tests demuestra los casos que se te ocurrieron. Los límites de un
> modelo se encuentran atacándolo, no releyéndolo.

---

## 12. Lo esencial

- El paso creativo es **renunciar a escribir la función** y escribir en su
  lugar una familia más una búsqueda.
- **La retropropagación no es cómo obtienes un gradiente: es cómo obtienes $P$
  de ellos por el precio de uno.** Las diferencias finitas también funcionan,
  cuestan $2P$ pasadas hacia delante y no bajan de un error relativo de
  $10^{-8}$.
- **El truco es $\delta^{l} = \partial L/\partial z^{l}$**, porque cada
  parámetro de una capa llega a la pérdida solo a través de la preactivación de
  esa capa. Nada se calcula dos veces.
- **Las cuatro líneas no son una elección.** Dadas la arquitectura y la pérdida
  el gradiente queda determinado, que es por lo que vive en el archivo de
  dominio.
- **La regla de paso sí es una elección**, y las tres de aquí son intercambios
  genuinamente distintos y no un orden de calidad.
- **$f'$ toma $z$, no $a$.** El atajo es correcto para la sigmoide y la tanh y
  silenciosamente incorrecto para todo lo demás.
- **La pérdida y su gradiente deben ser la misma función.** Un desajuste de
  factor constante es invisible con una sola salida y aparece como $|k-1|$ en
  una comprobación por diferencias finitas.
- **La escala de los pesos es $1/\sqrt{\text{fan-in}}$**, porque las varianzas
  se suman. Una dispersión fija funciona con anchura 8 y destruye la red con
  anchura 1024.
- **El condicionamiento cambia el número de pasos, no el coste de uno.** Y
  pasado cierto punto deja de ser una ralentización y se convierte en un
  precipicio.
- **Reescala tus entradas antes de mejorar tu optimizador.** Una de las dos
  cosas es gratis.
- **Convergido significa que la pérdida dejó de moverse.** No significa que la
  respuesta sea buena, y una red saturada lo cumple a la perfección.
- **Nada aquí mide la generalización**, que es lo único que alguien quería de
  verdad.

---

## 13. Preguntas abiertas

Cosas que este documento deliberadamente no responde, aproximadamente en orden
de cuánto enseñarían:

- **¿Por qué generaliza nada?** La red tiene parámetros suficientes para
  memorizar el conjunto de entrenamiento y no lo hace. Los argumentos clásicos
  de capacidad predicen que debería fallar y no falla, y el estado del arte
  honesto es que esto no está resuelto. Es además la mayor distancia entre esta
  entrada y cualquier cosa útil.
- **¿Qué aspecto tiene realmente la superficie de pérdida?** Todo aquí la trata
  como un valle. En dimensión alta, los puntos críticos son abrumadoramente
  sillas y no mínimos —la probabilidad de que los $P$ autovalores del hessiano
  sean todos positivos es evanescente—, así que el obstáculo son las mesetas, no
  los mínimos locales. Nada en esta entrada mide un solo autovalor.
- **¿Por qué ayuda el ruido del gradiente estocástico?** Los gradientes de
  minilote son estimaciones ruidosas, y el ruido parece favorecer los mínimos
  anchos, que parecen generalizar mejor. Las dos mitades de esa frase son
  empíricas.
- **¿Qué se rompe en una pila profunda?** Cada capa multiplica $\delta$ por
  otro $f'$, así que el gradiente encoge geométricamente con la profundidad.
  Las conexiones residuales y la normalización son las respuestas, y ninguna
  está aquí.
- **¿Cuándo compensa el segundo orden?** §8.2 es un anuncio a favor de usar la
  curvatura, y Newton cuesta $O(P^3)$ por paso. Toda la familia cuasi-Newton
  existe en esa distancia, y la razón de que perdiera frente a los métodos de
  primer orden a gran escala es una historia genuinamente interesante sobre
  memoria y no sobre matemáticas.

---

## 14. Referencias

**Fundacionales**

- **Rumelhart, D. E., Hinton, G. E. & Williams, R. J.** *Learning
  representations by back-propagating errors.* Nature **323**, 533–536 (1986).
  [enlace](https://www.nature.com/articles/323533a0)
- **Linnainmaa, S.** *The representation of the cumulative rounding error of
  an algorithm as a Taylor expansion of the local rounding errors.* Tesis de
  máster, Universidad de Helsinki (1970). La acumulación inversa, primero.
- **Werbos, P. J.** *Beyond regression: new tools for prediction and analysis
  in the behavioral sciences.* Tesis doctoral, Harvard (1974).
- **Baydin, A. G. et al.** *Automatic differentiation in machine learning: a
  survey.* JMLR **18**, 1–43 (2018).
  [enlace](https://jmlr.org/papers/v18/17-468.html) — de qué es un caso
  particular la retropropagación.

**Qué puede representar la familia**

- **Cybenko, G.** *Approximation by superpositions of a sigmoidal function.*
  Mathematics of Control, Signals and Systems **2**, 303–314 (1989).
  [enlace](https://doi.org/10.1007/BF02551274)
- **Hornik, K.** *Approximation capabilities of multilayer feedforward
  networks.* Neural Networks **4**, 251–257 (1991).
- **Leshno, M. et al.** *Multilayer feedforward networks with a nonpolynomial
  activation function can approximate any function.* Neural Networks **6**,
  861–867 (1993). [enlace](https://doi.org/10.1016/S0893-6080(05)80131-5)

**Inicialización y optimización**

- **Glorot, X. & Bengio, Y.** *Understanding the difficulty of training deep
  feedforward neural networks.* AISTATS (2010).
  [enlace](https://proceedings.mlr.press/v9/glorot10a.html) — §8.1 en un solo
  artículo.
- **He, K. et al.** *Delving deep into rectifiers.* ICCV (2015).
  [enlace](https://arxiv.org/abs/1502.01852)
- **Polyak, B. T.** *Some methods of speeding up the convergence of iteration
  methods.* USSR Comp. Math. **4**, 1–17 (1964). Momentum.
- **Kingma, D. P. & Ba, J.** *Adam: a method for stochastic optimization.*
  arXiv:1412.6980 (2014). [enlace](https://arxiv.org/abs/1412.6980)
- **Reddi, S. J., Kale, S. & Kumar, S.** *On the convergence of Adam and
  beyond.* ICLR (2018). [enlace](https://arxiv.org/abs/1904.09237) — la
  demostración de la referencia anterior no se sostiene.
- **Nocedal, J. & Wright, S.** *Numerical Optimization*, 2ª ed. (2006). La
  mitad de optimización, hecha en serio.

**El paisaje**

- **Dauphin, Y. et al.** *Identifying and attacking the saddle point problem
  in high-dimensional non-convex optimization.* NeurIPS (2014).
  [enlace](https://arxiv.org/abs/1406.2572)
- **Zhang, C. et al.** *Understanding deep learning requires rethinking
  generalization.* ICLR (2017). [enlace](https://arxiv.org/abs/1611.03530) —
  la primera pregunta de §13, planteada correctamente.

**Libros**

- **Nielsen, M.** *Neural Networks and Deep Learning*, cap. 2.
  [enlace](http://neuralnetworksanddeeplearning.com/chap2.html) — la derivación
  más clara de §6 que existe.
- **Goodfellow, I., Bengio, Y. & Courville, A.** *Deep Learning* (2016), cap. 6
  y 8.

---

*Código: [`../model.py`](../model.py) y [`../methods/`](../methods/) ·
Entrada: [`../README.md`](../README.md) · Arquitectura de todo el repositorio:
[`docs/architecture.md`](../../docs/architecture.md)*
