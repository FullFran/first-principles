<!-- translated-from: 3a417849829a -->

# Mirar lo mismo desde más lejos

> La teoría detrás de [`renormalisation/`](../README.md), derivada desde el
> problema y no desde la fórmula. Lee esto si quieres saber *por qué* las
> ecuaciones de `renormalisation/flow.py` y `renormalisation/methods/` son
> esas y no otras.

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
7. [Dos formas de contar](#7-dos-formas-de-contar)
8. [Análisis de escalas: lo que un bloque mayor no arregla](#8-análisis-de-escalas-lo-que-un-bloque-mayor-no-arregla)
9. [Formas cerradas que merece la pena memorizar](#9-formas-cerradas-que-merece-la-pena-memorizar)
10. [Qué mostró la simulación](#10-qué-mostró-la-simulación)
11. [Dónde deja de ser cierto el modelo](#11-dónde-deja-de-ser-cierto-el-modelo)
12. [Lo esencial](#12-lo-esencial)
13. [Preguntas abiertas](#13-preguntas-abiertas)
14. [Referencias](#14-referencias)

---

## 1. El fenómeno

Coge una red y ocupa cada sitio de forma independiente con probabilidad $p$.
Con $p$ baja los sitios ocupados forman islas pequeñas. Con $p$ alta forman
una masa conectada que atraviesa el sistema entero. En medio, en
$p_c = 0.5927460$, pasa algo que no es una transición gradual: el clúster
conectado se vuelve infinito, y todas las escalas de longitud del sistema
divergen a la vez.

Eso lo mide [`forest-fire/`](../../forest-fire/). Y deja dos preguntas, y la
segunda es genuinamente extraña.

**¿Por qué el umbral es ese número?**

Y: **¿por qué sistemas que no tienen nada en común comparten los mismos
exponentes?** Cerca de su punto crítico, la longitud de correlación de un imán
diverge como $|T - T_c|^{-\nu}$. La de un líquido también, acercándose a su
punto crítico. La de una red percolante también, acercándose a $p_c$. Los tres
sistemas están hechos de cosas distintas, unidos por fuerzas distintas y
descritos por ecuaciones distintas — y en dos dimensiones caen en clases
dentro de las cuales $\nu$ es *idéntico*, hasta la última cifra que nadie haya
medido.

Eso debería alarmar. La física no suele permitirte olvidar de qué está hecho
algo.

La respuesta a las dos preguntas es una sola idea, y es casi vergonzosamente
simple: **mira el sistema desde más lejos, y ve qué sobrevive.**

## 2. Para qué sirve esto

### 2.1 Fenómenos críticos, que es donde se inventó

Transiciones de fase — magnetización, ebullición, superconductividad, la
aparición de un clúster percolante. El grupo de renormalización es la razón de
que podamos calcular exponentes críticos siquiera, y la razón de que sepamos
qué sistemas los comparten.

### 2.2 Teoría cuántica de campos

La misma maquinaria, inventada dos veces. En teoría de campos el
"engrosamiento" es integrar los modos de momento alto, el "flujo" es la
variación de las constantes de acoplamiento con la escala de energía, y los
puntos fijos clasifican qué teorías tienen sentido siquiera. Que los dos temas
resultaran ser uno es la razón principal de que el trabajo de Wilson importara
tanto como importó.

### 2.3 Cualquier sitio donde un sistema no tenga escala característica

Turbulencia, fractura, terremotos, avalanchas neuronales, la distribución de
tamaños de los incendios forestales. Siempre que una magnitud medida sigue una
ley de potencias durante décadas, la razón es que el sistema no tiene una
longitud preferida, y la herramienta para un sistema sin longitud preferida es
esta.

### 2.4 Historia

::: **La percolación se inventó para describir un fluido en un medio
aleatorio** ·
*Verificación: A — Broadbent y Hammersley, Math. Proc. Cambridge Phil. Soc.
53(3), 1957, 629–641, que da nombre al campo y enuncia sus ejemplos.*

Simon Broadbent y John Hammersley escribieron el artículo fundacional en 1957.
Plantearon la pregunta en términos generales — cómo gobiernan las propiedades
aleatorias de un *medio* el paso de un *fluido* a través de él — y fueron
explícitos en que ninguna de las dos palabras debía tomarse literalmente. Los
ejemplos que enumeran incluyen soluto a través de disolvente, electrones sobre
una red atómica, moléculas a través de un sólido poroso, y **enfermedad a
través de una comunidad**.

En esa última merece la pena pararse. La lectura epidemiológica de la
percolación no es una aplicación posterior inventada cuando las herramientas
mejoraron. Está en el artículo que dio nombre al campo, en 1957, junto a la
química. Lo que hace [`forest-fire/`](../../forest-fire/) con rayos y árboles,
y lo que hace un modelo epidémico con contactos e infecciones, fueron la misma
pregunta desde el primer día.

::: **Bloques de espines, y una pregunta que nadie sabía responder** ·
*Verificación: A — Kadanoff (1966) para la construcción de bloques de espín y
las relaciones de escala que explica.*

Para los años sesenta el problema estaba afilado y atascado. Los experimentos
daban exponentes críticos. La teoría de campo medio daba otros distintos, y
era demostrablemente falsa — la solución exacta de Onsager del modelo de Ising
bidimensional lo había mostrado en 1944. Se habían observado varias relaciones
empíricas *entre* los exponentes, pero nadie sabía derivarlas.

En 1966 Leo Kadanoff propuso algo que suena más a cambio de actitud que a
cálculo. Cerca del punto crítico la longitud de correlación es enorme — mucho
mayor que el espaciado de la red — así que **agrupa los espines en bloques,
sustituye cada bloque por un único espín efectivo, y pregunta a qué se parece
el sistema resultante.** Si la respuesta es "al mismo sistema con otra
temperatura", tienes un mapa, y todo se sigue del mapa.

Su argumento explicaba las relaciones de escala empíricas. Lo que no hacía era
calcular nada: la transformación de bloques era una imagen, no un
procedimiento.

::: **Convertir una imagen en un cálculo** ·
*Verificación: A — los dos artículos de Wilson de 1971 y el Nobel de 1982.
B para la lectura de por qué costó cinco años, que es interpretación.*

Kenneth Wilson reformuló la transformación de bloques de Kadanoff en forma
diferencial y la convirtió en algo con lo que se podía calcular de verdad — un
desarrollo en $\varepsilon$ que producía exponentes, y un marco en el que un
punto fijo del flujo *es* un punto crítico y sus direcciones inestables *son*
los parámetros relevantes. Publicó dos artículos consecutivos en 1971 y
recibió el Premio Nobel en 1982.

El resultado que más importa es el que esta entrada está construida para
mostrar. El flujo tiene puntos fijos, y un punto fijo no recuerda cómo
llegaste a él. Los detalles microscópicos son *irrelevantes* en el sentido
técnico: encogen bajo el flujo. Lo que sobrevive lo comparte todo lo que fluye
al mismo punto fijo, y ese es el mecanismo detrás de la universalidad. El imán
y el líquido no coinciden por casualidad. Coinciden porque a los dos los están
llevando al mismo sitio.

::: **Y una pequeña, sobre la aritmética de esta entrada** ·
*Verificación: A — la factorización está sobre el papel en la sección 6.*

La recursión $b = 2$ para percolación de sitios, $R(p) = 2p^2 - p^4$, tiene
punto fijo $(\sqrt5 - 1)/2$: la razón áurea, un 4.3% del umbral verdadero. Es
un número bonito y conviene tener claro que es una coincidencia del bloque más
pequeño posible, no un hecho profundo sobre la percolación. La sección 8
muestra qué pasa cuando agrandas el bloque, que no es lo que supondrías.

#### Artículos que merece la pena leer

- **Broadbent y Hammersley (1957)**. Donde la percolación recibe su nombre y
  sus primeras preguntas.
- **Kadanoff (1966)**. La idea de los bloques de espín, antes de que pudiera
  calcular nada.
- **Wilson (1971)**, y la conferencia Nobel de 1982, que es inusualmente
  legible y explica la motivación mejor que los artículos.
- **Reynolds, Stanley y Klein (1980)**. RG en espacio real para percolación,
  el esquema celda a celda, y de donde vienen los números de la sección 10.
- **Stauffer y Aharony**, *Introduction to Percolation Theory*. El texto
  estándar, y la fuente de $p_c = 0.5927460$ y $\nu = 4/3$.

## 3. Antes de calcular

**El grupo de renormalización no es un grupo.** No tiene inversas: engrosar
destruye información y no puedes volver atrás. Es un semigrupo, y el nombre es
un accidente histórico que todo el mundo ha acordado conservar.

**Un punto fijo no es una solución del modelo.** Es una afirmación sobre a qué
se parece el modelo a escalas grandes. El punto crítico es donde el sistema se
ve igual a cualquier aumento, que es exactamente la condición para que el mapa
de engrosamiento lo deje en paz.

**Aquí nada calcula una función de partición.** En eso está todo el atractivo.
La pregunta "cuál es el umbral" se responde con una propiedad de un mapa, no
sumando sobre configuraciones, y el mapa para un bloque pequeño es un
polinomio que puedes factorizar a mano.

## 4. Por qué falla la respuesta ingenua

**Simula una red mayor.** Es lo que hace `forest-fire/`, y funciona — de ahí
sale $p_c = 0.5927460$. Pero te da un número y ninguna comprensión, y no
puede responder en absoluto a la pregunta de la universalidad: para descubrir
por simulación que un imán y una red comparten $\nu$ tendrías que simular los
dos y luego sorprenderte.

**Haz teoría de perturbaciones en la interacción.** En un punto crítico todas
las escalas de longitud contribuyen por igual, así que no hay parámetro
pequeño. Los desarrollos divergen. Por eso el problema estuvo abierto durante
décadas: la herramienta estándar de la física teórica sencillamente no aplica.

**Usa teoría de campo medio.** Sustituye los vecinos por su promedio. Es
resoluble, da los exponentes equivocados, y Onsager la refutó en 1944. La
razón de que falle es exactamente la razón de que el problema sea difícil: en
el punto crítico las fluctuaciones que el campo medio promedia *son* la
física.

La salida es dejar de intentar resolver el sistema y empezar a preguntar cómo
cambia cuando lo miras desde más lejos.

## 5. El modelo mínimo

Percolación de sitios en una red cuadrada. Ocupa cada sitio de forma
independiente con probabilidad $p$; pregunta si los sitios ocupados conectan
de un lado al otro.

Es el modelo más pequeño con un punto crítico genuino, y su paso de
engrosamiento es finito y exacto: un bloque $b \times b$ tiene $2^{b^2}$
configuraciones, y para $b$ pequeña puedes enumerarlas todas. **El grupo de
renormalización entero se convierte en un polinomio**, que es algo raro — en
casi cualquier otra aplicación el flujo es aproximado y la aproximación es la
parte difícil.

## 6. Las ecuaciones

### 6.1 El mapa de engrosamiento

Agrupa la red en bloques $b \times b$ y decide cuándo un bloque cuenta como
ocupado a la escala gruesa. Lo que debe sobrevivir al engrosamiento es la
**conexión** — un bloque de sitios desconectados no conduce nada — así que el
criterio es atravesar.

La probabilidad de que un bloque atraviese es un polinomio en $p$:

$$R(p) = \sum_k N_k \, p^k (1-p)^{b^2 - k},$$

con $N_k$ el número de configuraciones que atraviesan teniendo exactamente $k$
sitios ocupados. Ya está. El RG entero de este problema es esa línea.

### 6.2 El caso más pequeño, sobre el papel

Para $b = 2$ con una regla de arriba a abajo, un bloque atraviesa si alguna de
las dos columnas está llena. Inclusión-exclusión da

$$R(p) = 2p^2 - p^4.$$

Los puntos fijos cumplen $R(p^\ast) = p^\ast$, que factoriza:

$$2p^2 - p^4 = p \iff p\,(p - 1)(p^2 + p - 1) = 0,$$

así que además de los triviales $0$ y $1$,

$$p^\ast = \frac{\sqrt5 - 1}{2} = 0.618034.$$

La razón áurea, un 4.3% por encima del verdadero $p_c = 0.5927460$.

### 6.3 Por qué el punto fijo tiene que ser inestable

Arranca ligeramente por debajo de $p^\ast$ e itera: la densidad cae, y sigue
cayendo, hasta que a escalas grandes el sistema está vacío. Arranca
ligeramente por encima y sube hasta uno. El punto fijo repele en las dos
direcciones.

Esa inestabilidad no es un defecto — **es lo que es un punto crítico.** Un
punto fijo estable significaría que todo un rango de $p$ se ve igual a escalas
grandes, que es lo que pasa *fuera* de la criticidad (todo fluye a "vacío" o a
"lleno"). Solo exactamente en $p^\ast$ se ve el sistema idéntico a cualquier
aumento, y solo un punto fijo inestable puede hacer eso.

### 6.4 Un exponente a partir de una derivada

Cerca del punto fijo, linealiza. Un paso de engrosamiento multiplica la
distancia a $p^\ast$ por $\lambda = \mathrm{d}R/\mathrm{d}p$, mientras divide
toda longitud por $b$. Si la longitud de correlación se comporta como
$\xi \sim |p - p^\ast|^{-\nu}$, la consistencia entre esas dos afirmaciones
exige

$$\xi' = \xi / b \quad\text{and}\quad |p' - p^\ast| = \lambda|p - p^\ast|
\;\;\Longrightarrow\;\; \nu = \frac{\ln b}{\ln \lambda}.$$

**Un exponente crítico a partir de la pendiente de un polinomio.** Nada de la
red microscópica aparece en él — ni el número de coordinación, ni la constante
de red, ni qué son los sitios. Eso es la universalidad, enunciada como
fórmula, y es por qué sistemas no relacionados comparten exponentes.

## 7. Dos formas de contar

El polinomio necesita $N_k$, y hay dos maneras de obtenerlo.

**La enumeración** recorre las $2^{b^2}$ configuraciones y comprueba cada una.
Exacta, y el coste es el que dice: $b = 4$ son 65,536 configuraciones, $b = 5$
son 33 millones.

**El muestreo** trabaja a ocupación fija $k$, sorteando configuraciones y
estimando la fracción que atraviesa, y luego multiplica por
$\binom{b^2}{k}$. Más barato para $b$ grande, y trae una barra de error que el
método exacto no tiene.

Son la misma física con distinta contabilidad, y la suite de contrato somete a
las dos a las mismas leyes del dominio. Ese es el sentido de la separación: el
fichero de dominio sabe qué significa atravesar y nada sobre cómo cuentas.

## 8. Análisis de escalas: lo que un bloque mayor no arregla

Aquí está la predicción obvia, y conviene escribirla antes de mirar: **un
bloque mayor debería dar una respuesta mejor.** El resultado de $b=2$ falla un
4.3%; $b = 3$ y $b = 4$ tienen más sitio para representar la geometría, así que
el punto fijo debería acercarse a $p_c$ y el exponente a $4/3$.

No es lo que pasa.

![Izquierda: el punto fijo frente al tamaño de bloque para cuatro esquemas;
las reglas simples se quedan en rectas horizontales o divergentes mientras
celda a celda se pega al umbral verdadero. Derecha: error en el exponente, con
las barras de celda a celda varias veces menores que las
simples.](figures/convergence.png)

Los esquemas simples de bloque a sitio no convergen a $p_c$ al crecer $b$. La
regla "vertical" se queda en 0.62 sea cual sea el tamaño del bloque; la regla
"either" se aleja, de 0.38 en $b=2$ hacia 0.51; la regla "both" se queda alta,
cerca de 0.71. Agrandar el bloque no ayuda, porque no toca lo que está mal.

Lo que está mal es que el esquema compara **un bloque contra un sitio**, y un
bloque y un sitio no son el mismo tipo de objeto. Un bloque tiene interior,
frontera, forma; un sitio no tiene nada de eso. Cualquier error en la regla de
atravesar es por tanto un error en la comparación misma, y no encoge con $b$:
es sistemático.

El arreglo es comparar **un bloque contra un bloque** de otro tamaño, que es
lo que hace `solve.cell_to_cell`. Los dos lados son entonces el mismo tipo de
objeto, la mayor parte de lo que la regla hace mal aparece en los dos lados, y
se cancela. Esa es toda la idea, y convierte un error del 4–14% en un 0.3%.

## 9. Formas cerradas que merece la pena memorizar

| Magnitud | Forma |
|---|---|
| El mapa RG | $R(p) = \sum_k N_k p^k (1-p)^{b^2-k}$ |
| $b = 2$, atravesar vertical | $R(p) = 2p^2 - p^4$ |
| Su punto fijo | $(\sqrt5-1)/2 = 0.618034$ |
| Exponente de la pendiente | $\nu = \ln b / \ln \lambda$, $\lambda = R'(p^\ast)$ |
| Valores verdaderos (percolación 2-D) | $p_c = 0.5927460$, $\nu = 4/3$ |
| Coste de la enumeración | $2^{b^2}$ |

## 10. Qué mostró la simulación

**El resultado de papel se reproduce exactamente.** $R(p) = 2p^2 - p^4$, punto
fijo en la razón áurea, verificado contra la factorización y no contra un
buscador de raíces.

**Un bloque mayor no es el arreglo, y la figura es el argumento.** Medido,
para las tres reglas simples en $b = 2, 3, 4$ y celda a celda sobre pares de
bloques:

```
     either      2,3   0.559599    5.6%    1.2791    4.1%
     either      3,4   0.591046    0.3%    1.3758    3.2%
     either      2,4   0.574132    3.1%    1.3161    1.3%
```

El mejor de ellos alcanza **0.591046 frente a 0.592746 — un 0.3%** — a partir
de bloques de dieciséis sitios como mucho, sin simular una red grande en
ningún sitio. El umbral que `forest-fire/` necesitó un barrido de red para
medir sale de un polinomio en dieciséis variables.

**El exponente es el número difícil.** Viene de una derivada, y la derivada de
un mapa aproximado es peor que el mapa. El mejor $\nu$ aquí es 1.3161 frente a
$4/3$, que es un 1.3%, y los esquemas simples se desvían hasta un 20%. Quien
cite un exponente de RG en espacio real con tres cifras está citando el
esquema, no la física.

**Que es el resumen honesto del método.** El RG en espacio real sobre bloques
pequeños es una máquina para mostrarte *por qué* hay un umbral y *por qué* los
exponentes son universales, con aritmética que puedes comprobar a mano. No es
una máquina para calcular ninguno de los dos con alta precisión, y la entrada
lo dice en vez de presentar el 0.3% como si el método fuera así de bueno en
general.

## 11. Dónde deja de ser cierto el modelo

**Un solo parámetro.** El flujo real vive en un espacio de acoplamientos de
dimensión infinita, y un tratamiento serio sigue qué direcciones son
relevantes y cuáles irrelevantes. Aquí hay una única $p$, así que los
"operadores irrelevantes" — el mecanismo real de la universalidad — no se ven
en absoluto, solo su consecuencia.

**La regla de atravesar es una elección, y la respuesta depende de ella.** Hay
tres reglas implementadas y discrepan hasta un 14%. No hay principio en el
modelo que seleccione una; la sección 8 muestra que la discrepancia se cancela
en su mayor parte cuando los dos lados de la comparación son bloques, lo cual
es un apaño y no una derivación.

**Los bloques no son renormalizables en sentido estricto.** Una red de bloques
engrosada no es realmente un problema de percolación de sitios con una $p$
nueva: aparecen correlaciones entre bloques, y el mapa las ignora. Es el
primer término de algo, y la entrada no calcula el segundo.

**$b$ está limitada por $2^{b^2}$.** La enumeración exacta se para hacia
$b = 4$–$5$. El método de muestreo va más allá al precio de una barra de
error.

**Dos dimensiones, una red, una clase de universalidad.** Aquí nada pone a
prueba la universalidad; se exhibe el mecanismo que la produciría.

## 12. Lo esencial

1. **Engrosa y ve qué sobrevive.** Todo el asunto es un solo movimiento.
2. **Un punto crítico es un punto fijo inestable del mapa de engrosamiento**,
   y tiene que ser inestable, o todo un rango de parámetros parecería crítico.
3. **Un exponente crítico es la pendiente de ese mapa**, $\nu = \ln b / \ln
   \lambda$, sin nada microscópico dentro. Eso es la universalidad.
4. **Un bloque mayor no es el arreglo.** El error está en comparar un bloque
   contra un sitio; compara bloque contra bloque y se cancela.
5. **El exponente es más difícil que el umbral**, porque es la derivada de un
   mapa aproximado.

## 13. Preguntas abiertas

- **¿Se puede convertir la discrepancia entre reglas en una cota en vez de en
  una molestia?** Tres reglas acotan la respuesta; nada de aquí lo convierte
  en un intervalo del que nadie deba fiarse.
- **¿Dónde deja de funcionar la cancelación de celda a celda?** Está medida
  sobre pares de bloques hasta $(2,4)$ y explicada por un argumento sobre
  comparar cosas del mismo tipo, no derivada.
- **¿Qué aspecto tiene el flujo con dos acoplamientos?** El flujo de un solo
  parámetro no puede mostrar una dirección irrelevante encogiendo, que es el
  mecanismo real de la universalidad y no su consecuencia.
- **¿Significa algo la razón áurea?** Casi con seguridad no — es la aritmética
  del bloque más pequeño. Merece decirse porque es el tipo de coincidencia que
  invita a un relato.

## 14. Referencias

- Broadbent, S. R., Hammersley, J. M. (1957). *Percolation processes*. Math.
  Proc. Cambridge Phil. Soc. 53(3), 629–641.
- Kadanoff, L. P. (1966). *Scaling laws for Ising models near $T_c$*.
- Onsager, L. (1944). La solución exacta del Ising bidimensional, que mostró
  que los exponentes de campo medio eran falsos.
- Reynolds, P. J., Stanley, H. E., Klein, W. (1980). *Large-cell Monte Carlo
  renormalization group for percolation*. Phys. Rev. B 21, 1223.
- Stauffer, D., Aharony, A. *Introduction to Percolation Theory*.
- Wilson, K. G. (1971). *Renormalization group and critical phenomena*, I y
  II. Phys. Rev. B 4, 3174 y 3184.
- Wilson, K. G. (1982). Conferencia Nobel, *The renormalization group and
  critical phenomena*.
