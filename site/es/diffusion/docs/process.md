<!-- translated-from: 84e38378424f -->

# Caminar el ruido hacia atrás

> La teoría detrás de [`diffusion/`](../README.md), derivada desde el problema
> y no desde la fórmula. Lee esto si quieres saber *por qué* las ecuaciones de
> `diffusion/process.py` y `diffusion/methods/` son esas y no otras.

Este documento sigue un ciclo, y el ciclo es lo importante:

```
phenomenon → question → order of magnitude → assumptions → minimal model
   → equations → scale analysis → closed forms → simulation → validation
   → limits of the model → next question
```

La parte central es lo que enseña una carrera. Los dos extremos — plantear la
pregunta y saber dónde se acaba el modelo — son lo que de verdad separa a
quien resuelve problemas nuevos de quien aplica fórmulas. Así que los dos
extremos se llevan el espacio aquí.

**Contenidos**

1. [El fenómeno](#1-el-fenómeno)
2. [Para qué sirve esto](#2-para-qué-sirve-esto)
3. [Antes de calcular](#3-antes-de-calcular)
4. [Por qué falla la respuesta ingenua](#4-por-qué-falla-la-respuesta-ingenua)
5. [El modelo mínimo](#5-el-modelo-mínimo)
6. [Las ecuaciones](#6-las-ecuaciones)
7. [Dos caminos de vuelta](#7-dos-caminos-de-vuelta)
8. [Análisis de escalas: cuándo se funden las modas](#8-análisis-de-escalas-cuándo-se-funden-las-modas)
9. [Formas cerradas que merece la pena memorizar](#9-formas-cerradas-que-merece-la-pena-memorizar)
10. [Qué mostró la simulación](#10-qué-mostró-la-simulación)
11. [Dónde deja de ser cierto el modelo](#11-dónde-deja-de-ser-cierto-el-modelo)
12. [Lo esencial](#12-lo-esencial)
13. [Preguntas abiertas](#13-preguntas-abiertas)
14. [Referencias](#14-referencias)

---

## 1. El fenómeno

Coge una fotografía. Añádele un poco de ruido gaussiano. Añade otro poco.
Sigue, y tras suficientes pasos la fotografía ha desaparecido: lo que queda es
indistinguible de la nieve de un televisor, y por mucho que mires no recuperas
al gato.

Nada de eso sorprende. Destruir información es fácil, y es la dirección en la
que corre todo en física.

Y aquí está lo sorprendente. **La destrucción es reversible — no para una
imagen concreta, sino para la distribución.** Existe un segundo proceso, que
corre hacia atrás en el tiempo, cuya estadística en cada instante coincide con
la del directo. Arráncalo desde nieve pura y produce una fotografía. No la que
tenías; *una* fotografía, extraída de la misma distribución de la que venían
las originales.

Y lo único que ese segundo proceso necesita saber, en cada punto del camino,
es un único campo vectorial: la dirección en la que la densidad con ruido
crece más deprisa.

$$\nabla_x \log q_t(x)$$

Eso es todo el asunto. El resto — los calendarios, las U-Net, las escalas de
guía, lo que te dibuja un astronauta a caballo — es ingeniería encima de un
teorema sobre cómo invertir una difusión.

La pregunta que responde este documento es por qué ese campo basta, y contra
qué compararías uno aprendido.

## 2. Para qué sirve esto

### 2.1 Modelado generativo

El uso obvio, y el que hizo famoso al tema. Todo generador de imágenes de uso
extendido — Stable Diffusion, Imagen, DALL·E 2 en adelante, Midjourney — es
este proceso con una red neuronal en lugar de la score exacta.

### 2.2 Problemas inversos, que resultan ser el mismo problema

Quitar ruido, rellenar huecos, desenfocar, superresolución, reconstrucción de
resonancia magnética. Todos preguntan lo mismo: dada una observación
corrompida, ¿cuál era la señal limpia? La sección 6.4 muestra que responder a
eso *es* estimar una score, por una identidad que nadie diseñó para ese fin.
Los modelos generativos se construyeron a partir de quitarruidos, y costó
treinta años darse cuenta de que un quitarruido ya era medio modelo
generativo.

### 2.3 Física estadística, que es de donde vino

El proceso directo es movimiento browniano. El inverso es una difusión
invertida en el tiempo, y la inversión temporal en un sistema disipativo es la
pregunta para la que existe la termodinámica del no equilibrio. El artículo de
2015 que arrancó el campo lo dice en el título, y su argumento es
explícitamente el de Jarzynski para diferencias de energía libre: un proceso
demasiado rápido para ser cuasiestático se puede analizar igual, si llevas la
cuenta del conjunto entero de caminos en vez de uno solo.

### 2.4 El espejo de `sampling/`

[`sampling/`](../../sampling/) tiene una energía que puedes evaluar en
cualquier sitio y un normalizador que no puedes calcular. Esto tiene muestras
que puedes extraer y una densidad que no puedes evaluar en ningún sitio. Los
dos problemas son espejos exactos, y los dos se resuelven con el mismo truco:
trabajar con un objeto que no puede ver una constante de normalización. Un
cociente no puede. El gradiente de un logaritmo, tampoco.

### 2.5 Historia

::: **Un teorema para circuitos eléctricos, sin usar durante treinta años** ·
*Verificación: A — Anderson, Stochastic Processes and their Applications 12(3),
1982, 313–326.*

Brian Anderson era un teórico del control en la Universidad de Newcastle, en
Australia, trabajando en filtrado y realización estocástica. En 1982 publicó
un artículo estableciendo que un proceso definido por una ecuación de difusión
en tiempo directo tiene asociado un modelo en tiempo inverso, y que la deriva
inversa difiere de la directa en un término que involucra el gradiente del
logaritmo de la densidad.

Ese es el teorema sobre el que corre el campo entero. Es la razón de que nada
de esto funcione.

Las aplicaciones que Anderson enumera son **realización estocástica,
procesamiento de señal y teoría de circuitos eléctricos**. No hay ni rastro de
modelado generativo, porque en 1982 no había nada que generar: ni conjunto de
datos, ni cómputo, ni razón alguna para querer un muestreador de la
distribución de las fotografías. El resultado se quedó en una revista de
teoría del control durante tres décadas, completo y correcto y sin usar para
aquello que acabaría haciendo posible.

Ahí hay una lección que no va de modelos de difusión. Las matemáticas nunca
fueron el cuello de botella.

::: **Una fórmula que llegó en una carta** ·
*Verificación: A — Robbins, Proc. Third Berkeley Symposium, 1956, acreditando
correspondencia personal con Maurice Tweedie; recuperada por Efron, JASA
106(496), 2011.*

En los años cincuenta Herbert Robbins estaba construyendo el bayes empírico:
la idea de que si estimas muchos parámetros a la vez, los datos pueden decirte
la prior. En su artículo del Simposio de Berkeley de 1956 reporta una fórmula
para la media posterior de un parámetro dada una observación con ruido, y la
acredita a **correspondencia privada con Maurice Tweedie**, un estadístico
británico que la había derivado hacia 1947 y que, hasta donde llega el
registro, nunca la publicó a su propio nombre.

La fórmula dice: para pasar de una observación con ruido a la mejor estimación
de la señal limpia, añade una corrección que es *exactamente proporcional a la
score de la marginal con ruido*.

$$\mathbb{E}[x_0 \mid x_t] = \frac{x_t + (1-\bar\alpha)\,\nabla \log q_t(x_t)}
{\sqrt{\bar\alpha}}$$

Léela de derecha a izquierda y dice que una score te da un quitarruido. Léela
de izquierda a derecha y dice que **un quitarruido te da una score** — que una
red entrenada solo para limpiar imágenes corrompidas ha aprendido, sin que
nadie lo pretendiera, el campo de gradientes de la distribución de los datos.

Ese es el puente entre las dos mitades de este asunto, y vino de una carta de
1947, publicada por otra persona en 1956, y prácticamente olvidada hasta que
Efron la recuperó en 2011.

::: **Dos grupos, dos direcciones, una ecuación** ·
*Verificación: A para los artículos y las fechas; B para la afirmación de que
las dos líneas de trabajo fueron independientes — es el relato estándar y
encaja con el registro de citas, pero no he visto a ninguno de los dos grupos
decirlo con esas palabras.*

Para 2019 había dos programas de investigación separados que no sabían que
eran el mismo.

**Desde la termodinámica.** Jascha Sohl-Dickstein y sus colaboradores
publicaron *Deep Unsupervised Learning using Nonequilibrium Thermodynamics* en
2015. Tiene la arquitectura entera: destruye los datos con una difusión,
aprende la inversa, muestrea corriéndola hacia atrás. Después Jonathan Ho,
Ajay Jain y Pieter Abbeel lo convirtieron en DDPM en 2020, y de golpe las
imágenes eran competitivas.

**Desde el score matching.** Aapo Hyvärinen había introducido el score
matching en 2005 — ajusta una densidad emparejando gradientes, y así el
normalizador no aparece nunca — pero requería la traza de una hessiana y era
intratable a escala. En 2011 Pascal Vincent demostró que el objetivo de
entrenamiento de un autocodificador que quita ruido es score matching
disfrazado, **eliminando las segundas derivadas por completo**. Yang Song y
Stefano Ermon construyeron sobre eso las redes de score condicionadas al ruido
en 2019.

En 2021 Song y sus coautores mostraron que las dos eran discretizaciones de la
misma EDE de Itô, y derivaron la EDO determinista que comparte sus marginales.
Dos comunidades habían pasado años caminando la una hacia la otra desde
extremos opuestos de un resultado que Anderson había demostrado en 1982.

::: **Por qué 2015 no se parecía a 2022** ·
*Verificación: C — repetido por todas partes, y no lo he contrastado contra
recuentos de citas. Trátalo como un relato plausible, no como un hecho.*

Lo que se cuenta habitualmente es que el artículo de 2015 fue ignorado durante
cinco años hasta que DDPM lo hizo funcionar. Se repite en todos lados y encaja
con lo que pasó después, pero no lo he comprobado contra el registro de citas
y tú tampoco deberías dármelo por bueno. Lo documentado es el hueco entre las
fechas y el salto en la calidad de las muestras.

#### Artículos que merece la pena leer

- **Anderson (1982)**, *Reverse-time diffusion equation models*. El teorema.
  Corto, y escrito para teóricos del control.
- **Robbins (1956)**, *An empirical Bayes approach to statistics*. Donde
  aparece impresa por primera vez la fórmula de Tweedie.
- **Hyvärinen (2005)**, *Estimation of non-normalized statistical models by
  score matching*. Por qué puedes ajustar una densidad que no sabes
  normalizar.
- **Vincent (2011)**, *A connection between score matching and denoising
  autoencoders*. El artículo que lo hizo tratable.
- **Sohl-Dickstein et al. (2015)**, *Deep unsupervised learning using
  nonequilibrium thermodynamics*. La arquitectura, cinco años antes.
- **Ho, Jain, Abbeel (2020)**, *Denoising diffusion probabilistic models*. El
  que funcionó.
- **Song et al. (2021)**, *Score-based generative modeling through stochastic
  differential equations*. La unificación, y la EDO de flujo de probabilidad.

## 3. Antes de calcular

Tres cosas conviene tener claras antes de cualquier ecuación, porque
equivocarse en ellas hace incomprensible todo lo demás.

**El proceso inverso no recupera tu imagen.** Produce *una* muestra de la
distribución. Correrlo desde el ruido en el que una fotografía concreta
degeneró no te devolverá esa fotografía. Nada de esto es una inversa en el
sentido corriente.

**El tiempo aparece solo a través de un escalar.** El proceso directo suele
escribirse como una cadena de pasos pequeños, pero cada paso compone, así que
el estado en el instante $t$ es una única gaussiana alrededor de los datos.
Todo en `process.py` toma $\bar\alpha$ y nunca $t$: no hay un segundo
parámetro escondido.

**La score es una propiedad de la densidad con ruido, no de los datos.** No
hay una score útil de la distribución de los datos en sí — para datos sobre
una variedad no existe. Añadir ruido no es solo una forma de destruir los
datos; es lo que hace que el gradiente esté definido siquiera.

## 4. Por qué falla la respuesta ingenua

Supón que quieres muestrear una distribución de la que solo tienes muestras.
Los enfoques obvios mueren todos, y mueren por razones que conviene conocer.

**Ajusta una densidad y muestréala.** Para muestrear una densidad
generalmente necesitas su normalizador, y en cualquier dimensión interesante
esa integral es inalcanzable. Es exactamente el muro alrededor del cual está
construido [`sampling/`](../../sampling/).

**Corre una cadena de Markov.** Ahora ya no necesitas el normalizador: los
cocientes lo cancelan. Pero una cadena tiene que *viajar*, y entre dos modas
separadas por una región de baja probabilidad viaja exponencialmente despacio.
Ese es el problema de la barrera, medido en `sampling/`, y los datos reales no
son otra cosa que modas.

**Aprende la score directamente y corre dinámica de Langevin sobre ella.** Más
cerca, y es lo que propone el score matching. Falla por dos razones que se
componen. Donde no hay datos no hay señal, así que la score aprendida es
basura exactamente en las regiones que una cadena debe cruzar. Y sobre una
variedad la score no está definida en absoluto.

El arreglo que hace funcionar todo es pequeño y extraño: **no aprendas una
score, aprende una familia de ellas, indexada por cuánto ruido añadiste.** Con
mucho ruido la densidad es ancha, la score está definida en todas partes y es
fácil de aprender. Con poco es afilada y difícil, pero para entonces ya estás
en la región correcta. El nivel de ruido es un parámetro de continuación, y el
muestreador entero es una homotopía desde un problema que sabes resolver hasta
el que no.

## 5. El modelo mínimo

Para preguntar si una score aprendida es buena necesitas un caso donde la
score verdadera se conozca. Esa es toda la restricción de diseño, y tiene
exactamente una familia de soluciones.

Una gaussiana convolucionada con una gaussiana es una gaussiana. Así que si
los datos son una **mezcla de gaussianas**, los datos con ruido son también
una mezcla de gaussianas, con parámetros que sabes escribir, a cualquier nivel
de ruido, siempre. Es la única familia no trivial que permanece cerrada bajo
el proceso directo.

Una mezcla no son datos interesantes. Ese es el sentido. Es el caso que tiene
solucionario, y la entrada existe para construir el solucionario, no para
admirar las muestras.

## 6. Las ecuaciones

### 6.1 El proceso directo

Añade ruido gaussiano en pasos pequeños, y compón los pasos. La composición es
otra gaussiana, así que el estado en cualquier instante es

$$x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1-\bar\alpha_t}\,\varepsilon,
\qquad \varepsilon \sim \mathcal{N}(0, I).$$

Un único escalar $\bar\alpha_t \in (0,1]$ carga con todo el tiempo: la
fracción de señal que todavía queda. En 1 tienes los datos. En 0 tienes una
normal estándar y los datos han desaparecido.

### 6.2 La mezcla sigue siendo una mezcla

Si $p_0 = \sum_k w_k \mathcal{N}(\mu_k, \Sigma_k)$ entonces

$$q_t = \sum_k w_k\, \mathcal{N}\!\left(\sqrt{\bar\alpha}\,\mu_k,\; S_k\right),
\qquad S_k = \bar\alpha\,\Sigma_k + (1-\bar\alpha) I.$$

Las medias encogen hacia el origen por $\sqrt{\bar\alpha}$; las covarianzas
interpolan hacia la identidad. Los pesos no se mueven nunca: el ruido no
cambia de qué componente vino una muestra, solo lo bien que puedes
distinguirlo.

### 6.3 La score, en forma cerrada

Deriva el logaritmo de esa suma y el normalizador se cae:

$$\nabla \log q_t(x) = -\sum_k r_k(x)\; S_k^{-1}\left(x - \sqrt{\bar\alpha}\,
\mu_k\right),$$

$$r_k(x) = \operatorname{softmax}_k \big[\log w_k + \log \mathcal{N}(x;
\sqrt{\bar\alpha}\mu_k, S_k)\big].$$

Un promedio, ponderado por responsabilidades, de hacia dónde tiraría cada
componente. Dos límites merecen comprobarse a mano, porque los dos cargan
peso:

- $\bar\alpha \to 1$: las responsabilidades se vuelven una asignación dura y
  la score apunta directamente a la componente a la que pertenece el punto.
- $\bar\alpha \to 0$: la densidad con ruido de cada componente es la misma
  normal estándar, las responsabilidades se aplanan a $w_k$, todos los tirones
  coinciden, y la score colapsa a $-x$. **No queda nada que invertir, que es
  exactamente por qué el proceso inverso puede arrancar desde ruido puro.**

### 6.4 Tweedie, y por qué un quitarruido es un modelo de score

Reordenado, el mismo objeto responde a otra pregunta:

$$\mathbb{E}[x_0 \mid x_t] = \frac{x_t + (1-\bar\alpha)\,\nabla \log q_t(x_t)}
{\sqrt{\bar\alpha}}, \qquad
\nabla \log q_t(x_t) = -\frac{\mathbb{E}[\varepsilon \mid x_t]}
{\sqrt{1-\bar\alpha}}.$$

Esto vale para **cualquier** $p_0$, no solo para una mezcla. Es la fórmula de
1947 de la sección 2.5, y es la razón de que una red entrenada para predecir
el ruido de una imagen corrompida sea un estimador de la score, lo pretendiera
alguien o no.

### 6.5 El proceso en tiempo inverso

El teorema de Anderson: una difusión directa tiene una pareja en tiempo
inverso cuya deriva es la directa *menos* un término en la score.
Discretizado sobre la malla de $\bar\alpha$, y con la score sustituida por la
predicción del ruido, el paso inverso es

$$x_{t-1} = \frac{x_t + (1-\alpha_t)\,\nabla \log q_t}{\sqrt{\alpha_t}}
+ \sigma_t z, \qquad \alpha_t = \frac{\bar\alpha_t}{\bar\alpha_{t-1}}.$$

El coeficiente es $1-\alpha_t$, la cantidad **por paso** — no
$1-\bar\alpha_t$, la acumulada. Equivocarse ahí no es un error pequeño: mira
la sección 10.

### 6.6 La EDO de flujo de probabilidad

Toda difusión tiene una pareja determinista con la misma densidad marginal en
todo instante. No los mismos caminos: la misma distribución en cada instante,
que es lo único que se le pide a un muestreador. Su discretización es

$$x_{t-1} = \sqrt{\bar\alpha_{t-1}}\,\hat x_0 + \sqrt{1-\bar\alpha_{t-1}}\,
\hat\varepsilon, \qquad
\hat x_0 = \frac{x_t + (1-\bar\alpha_t)\nabla \log q_t}{\sqrt{\bar\alpha_t}},
\quad \hat\varepsilon = -\sqrt{1-\bar\alpha_t}\,\nabla \log q_t.$$

Lee la segunda línea así: *estima el ruido, y luego vuelve a añadir
exactamente el que el siguiente instante debería tener.*

## 7. Dos caminos de vuelta

Difieren en un término — el $\sigma_t z$ — y todo lo demás se sigue de ahí.

| | ancestral | flujo de probabilidad |
|---|---|---|
| sortea del generador | en cada paso | una vez, al arrancar |
| el mapa de ruido a datos | no es una función | es una función |
| los caminos | se cruzan constantemente | no pueden cruzarse |
| una moda lejos del arranque | alcanzable | inalcanzable |
| un error de discretización | se lava en parte | se integra |

Las dos últimas filas son el mismo hecho leído dos veces, que es la forma
honesta de presentar un compromiso: el ruido que permite a una ejecución
cambiar de idea es el ruido que impide que sea reproducible.

## 8. Análisis de escalas: cuándo se funden las modas

El proceso directo no funde las modas gradualmente. Hay un umbral, y merece la
pena saber predecirlo antes de ejecutar nada.

Dos componentes separadas una distancia $d$ tienen medias con ruido separadas
$\sqrt{\bar\alpha}\,d$ — encogiendo. Sus anchuras con ruido son
$\sqrt{\bar\alpha \sigma^2 + (1-\bar\alpha)}$ — creciendo hacia 1. Así que la
resolubilidad

$$R(\bar\alpha) = \frac{\sqrt{\bar\alpha}\, d}
{2\sqrt{\bar\alpha \sigma^2 + (1-\bar\alpha)}}$$

cae monótonamente, y $R = 1$ es donde dos bultos se vuelven uno. Para el
objetivo bimodal ($d = 4$, $\sigma^2 = 0.3$) eso ocurre en
$\bar\alpha \approx 0.2$.

![Arriba: la densidad exacta según cae la fracción de señal, dos pozos
fundiéndose en un solo borrón. Abajo: el campo de la score en los mismos
cuatro instantes, con dos atractores al principio y un campo radial único al
final.](figures/collapse.png)

Medido:

```
  abar  mode gap / width  resolvable
  1.00              3.65  yes
  0.70              2.34  yes
  0.30              1.23  yes
  0.05              0.46  no
```

La consecuencia es de calendario. **Todas las decisiones interesantes ocurren
en una banda estrecha de $\bar\alpha$**, y un muestreador que reparte sus
pasos uniformemente en $t$ gasta la mayoría donde la densidad ya es gaussiana
y no queda nada que decidir. Para eso está un calendario coseno, y por eso el
lineal original necesitaba mil pasos para valer algo.

Fíjate en qué magnitud fija el umbral: la anchura con ruido la domina el
autovalor *más pequeño* de la covarianza de los datos, no el promedio. En un
conjunto anisótropo cada dirección pierde su estructura en un instante
distinto.

## 9. Formas cerradas que merece la pena memorizar

| Magnitud | Forma |
|---|---|
| Mezcla con ruido | $\sum_k w_k \mathcal{N}(\sqrt{\bar\alpha}\mu_k,\; \bar\alpha\Sigma_k + (1-\bar\alpha)I)$ |
| Score, $\bar\alpha \to 0$ | $-x$ |
| Quitarruido ↔ score | $\nabla \log q_t = -\mathbb{E}[\varepsilon|x_t]/\sqrt{1-\bar\alpha}$ |
| Media inversa | $(x_t + (1-\alpha_t)\nabla\log q_t)/\sqrt{\alpha_t}$ |
| Varianza inversa | $\frac{1-\bar\alpha_{t-1}}{1-\bar\alpha_t}(1-\alpha_t)$ |
| Las modas se funden en | $R(\bar\alpha) = 1$, $R = \sqrt{\bar\alpha}d \,/\, 2\sqrt{\bar\alpha\sigma^2 + 1 - \bar\alpha}$ |
| Mapa del flujo, 1-D | $x \mapsto F^{-1}(\Phi(x))$ |

## 10. Qué mostró la simulación

**La score es correcta.** Tres comprobaciones independientes, ninguna de las
cuales comparte una línea con la fórmula bajo examen: diferencias centradas
del logaritmo de la densidad (peor caso $1.7\times10^{-9}$), una derivación de
Tweedie no relacionada por condicionamiento gaussiano ($2.1\times10^{-14}$), y
la identidad del $\varepsilon$ (precisión de máquina).

**Un coeficiente equivocado es invisible en las matemáticas y evidente en las
muestras.** La primera versión de `ancestral.step` usaba $1-\bar\alpha_t$
donde va $1-\alpha_t$. Los dos métodos consumen la misma score, así que el
dominio quedó exonerado de inmediato: el flujo de probabilidad se sentaba
dentro del suelo de ruido mientras ancestral se sentaba en
$\text{MMD}^2 = 4\times10^{-1}$. Dos métodos sobre un dominio es lo que
convierte "algo va mal" en "el fallo está en este fichero".

**El muestreador determinista es el mapa de transporte por cuantiles.** No
solo determinista: en una dimensión es *el* mapa monótono que lleva el ruido
al objetivo, así que un arranque en el cuantil $u$ del ruido aterriza en el
cuantil $u$ del objetivo.

![Arriba: doce caminos desde los mismos doce arranques, enmarañados para
ancestral y sin cruzarse para el flujo. Abajo a la izquierda: final frente a
arranque, con el flujo sobre la curva exacta de cuantiles y ancestral plano.
Abajo a la derecha: el error contra el mapa exacto, de primer orden en el
número de pasos.](figures/trajectories.png)

Ese único hecho explica tres cosas que ninguna otra propiedad explica. Los
caminos no pueden cruzarse, porque un mapa monótono no tiene sitio para ello.
Los finales no caen en las modas, porque los cuantiles van a cuantiles. Y qué
moda alcanza una ejecución lo decide enteramente su primer sorteo.

Su imagen especular es lo que hace ancestral. Sobre un rango de puntos de
partida de cinco unidades de ancho, su punto final se mueve **0.024**: la
muestra sale del ruido inyectado por el camino, no de dónde empezó el paseo.

El mapa es exacto solo en el límite, y la aproximación es de primer orden
limpio:

```
  steps   worst error   halving
     50      5.50e-02        --
    100      2.80e-02      2.0x
    200      1.43e-02      2.0x
    400      7.30e-03      2.0x
    800      3.80e-03      1.9x
   1600      2.04e-03      1.9x
```

**Un umbral hay que medirlo.** La discrepancia es una MMD² insesgada contra
muestras exactas, y el suelo — cuánto discrepan dos conjuntos de muestras
*exactas* — se estimó primero a partir de un solo par. El test de contrato
entonces pasaba a 100 pasos, fallaba a 200 y volvía a pasar a 400 en el mismo
objetivo. Una medida ruidosa contra un umbral ruidoso es una moneda al aire
con bata de laboratorio. Ahora se toma sobre cinco pares, por arriba.

**Y una afirmación sobre presupuestos de pasos sobrevive solo en una
ventana.** La sabiduría recibida es que el muestreador determinista necesita
muchos menos pasos. Se sostiene entre cinco y ocho pasos — 0.6–0.9× en MMD² en
los objetivos anisótropos — lo cual merece saberse, porque el argumento
habitual se hace con una score aprendida y una métrica perceptual y ninguna de
las dos sobrevive a este escenario automáticamente. Pasados unos doce pasos
los dos métodos están dentro del suelo. Una versión anterior del experimento
siguió ordenándolos allí y reportó ancestral por delante 5.6×, que eran dos
números indistinguibles de cero divididos el uno por el otro.

## 11. Dónde deja de ser cierto el modelo

**Una mezcla no son datos.** Los datos reales viven cerca de una variedad de
baja dimensión, su score no existe a ruido cero, y no va a llegar ninguna
forma cerrada. Todo lo de aquí es el instrumento, no el espécimen.

**Dos dimensiones esconden el problema entero.** La razón de que el score
matching necesitara el truco de Vincent es una traza de hessiana que está bien
en 2-D y es imposible en $10^5$.

**La score es exacta, así que nada de aquí mide aprendizaje.** Todos los modos
de fallo de un modelo de difusión real — una score equivocada donde los datos
escasean, una red que suaviza entre modas, un calendario descuadrado con lo
que la red aprendió — son invisibles por construcción.

**La discretización es de malla fija.** La EDE en tiempo continuo y su EDO de
flujo de probabilidad son el enunciado general; DDPM y DDIM son una
discretización suya, y los integradores de orden superior lo hacen mejor que
el primer orden medido en la sección 10.

**$\bar\alpha$ se rechaza por debajo de $10^{-8}$**, y los calendarios paran en
$10^{-4}$. En cero exacto el softmax es sobre logits idénticos, y devolver
$-x$ sería reportar un límite como si se hubiera calculado.

## 12. Lo esencial

Si te quedas con cinco cosas de este documento:

1. **Destruir una distribución es fácil y reversible en ley.** No trayectoria
   a trayectoria: en distribución, que es todo lo que un muestreador necesita.
2. **El proceso inverso necesita un objeto: $\nabla \log q_t$.** Es el
   gradiente de un logaritmo, así que el normalizador se fue antes de empezar.
3. **Un quitarruido es un modelo de score.** La fórmula de Tweedie, de una
   carta de 1947, dice que la corrección de ruidoso a limpio es proporcional a
   la score.
4. **El ruido es un parámetro de continuación, no solo daño.** Hace que la
   score esté definida en todas partes y convierte un problema imposible en
   una homotopía desde uno fácil.
5. **Las modas se funden en un umbral, no gradualmente**, y el umbral lo fija
   el autovalor más pequeño de la covarianza de los datos.

## 13. Preguntas abiertas

- **¿Qué cuesta una score aprendida?** Todo lo de aquí es el solucionario; la
  entrada que lo usa todavía no existe. `solve.sample` toma un `score_fn`
  precisamente para que esa entrada no cambie ni una línea bajo `methods/`.
- **¿Dónde se equivoca primero la score aprendida?** La conjetura honesta es:
  en la banda estrecha de $\bar\alpha$ identificada en la sección 8, porque es
  donde la densidad tiene estructura y la señal de entrenamiento es más fina
  por unidad de consecuencia. Sin comprobar.
- **¿Sobrevive el resultado del mapa de transporte en más dimensiones?** En
  1-D el flujo es el mapa monótono de cuantiles. En 2-D y más no hay mapa
  monótono canónico, y a lo que converge la EDO es a uno concreto: ¿cuál?
- **¿La ventaja a pocos pasos del muestreador determinista es una propiedad de
  la score o de la métrica?** Medida aquí con una score exacta y MMD; la
  literatura la mide con una score aprendida y FID.

## 14. Referencias

- Anderson, B. D. O. (1982). *Reverse-time diffusion equation models*.
  Stochastic Processes and their Applications 12(3), 313–326.
- Efron, B. (2011). *Tweedie's formula and selection bias*. JASA 106(496).
- Ho, J., Jain, A., Abbeel, P. (2020). *Denoising diffusion probabilistic
  models*. NeurIPS.
- Hyvärinen, A. (2005). *Estimation of non-normalized statistical models by
  score matching*. JMLR 6, 695–709.
- Nichol, A., Dhariwal, P. (2021). *Improved denoising diffusion probabilistic
  models*. El calendario coseno usado en `solve.py`.
- Robbins, H. (1956). *An empirical Bayes approach to statistics*. Proc. Third
  Berkeley Symposium.
- Sohl-Dickstein, J., Weiss, E., Maheswaranathan, N., Ganguli, S. (2015).
  *Deep unsupervised learning using nonequilibrium thermodynamics*. ICML.
- Song, J., Meng, C., Ermon, S. (2020). *Denoising diffusion implicit models*.
- Song, Y., Ermon, S. (2019). *Generative modeling by estimating gradients of
  the data distribution*. NeurIPS.
- Song, Y., et al. (2021). *Score-based generative modeling through stochastic
  differential equations*. ICLR.
- Vincent, P. (2011). *A connection between score matching and denoising
  autoencoders*. Neural Computation 23(7), 1661–1674.
