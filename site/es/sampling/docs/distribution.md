<!-- translated-from: 4fac6c6ce2c3 -->

# Cadenas que olvidan dónde empezaron

> La teoría detrás de [`sampling/`](../README.md), derivada del problema
> y no de la fórmula. Lee esto si quieres saber *por qué* las
> ecuaciones de `sampling/distribution.py` y `sampling/methods/` son esas
> y no otras.

Este documento sigue un ciclo, y el ciclo es lo importante:

```
phenomenon → question → order of magnitude → assumptions → minimal model
   → equations → scale analysis → closed forms → simulation → validation
   → limits of the model → next question
```

La parte central es lo que enseña una carrera. Los dos extremos —plantear la
pregunta y saber dónde se detiene el modelo— son lo que de verdad separa a
quien resuelve problemas nuevos de quien aplica fórmulas. Así que aquí el
espacio se lo llevan los dos extremos.

**Contenido**

1. [El fenómeno](#1-el-fenómeno)
2. [Para qué sirve esto](#2-para-qué-sirve-esto)
3. [Antes de calcular](#3-antes-de-calcular)
4. [Por qué falla la respuesta ingenua](#4-por-qué-falla-la-respuesta-ingenua)
5. [El modelo mínimo](#5-el-modelo-mínimo)
6. [Las ecuaciones](#6-las-ecuaciones)
7. [Dos cadenas, una densidad](#7-dos-cadenas-una-densidad)
8. [Análisis de escalas: cuánto tarda en olvidar](#8-análisis-de-escalas-cuánto-tarda-en-olvidar)
9. [Formas cerradas que vale la pena memorizar](#9-formas-cerradas-que-vale-la-pena-memorizar)
10. [Lo que mostró la simulación](#10-lo-que-mostró-la-simulación)
11. [Dónde el modelo deja de ser cierto](#11-dónde-el-modelo-deja-de-ser-cierto)
12. [Lo esencial](#12-lo-esencial)
13. [Preguntas abiertas](#13-preguntas-abiertas)
14. [Referencias](#14-referencias)

---

## 1. El fenómeno

Aquí hay un hecho que debería resultar extraño y no se trata como tal.
**Puedes describir cuán probable es algo sin poder decir cuán probable es.**

Escribe una energía para una configuración —una proteína plegada de cierta
manera, un imán con sus espines apuntando a algún sitio, un conjunto de
parámetros ajustando unos datos— y ya has dicho todo sobre la probabilidad
relativa de cada configuración. Cuál de dos es más probable, y por qué factor
exacto, queda decidido. Lo que no tienes, y no puedes tener, es una sola
probabilidad, porque eso exige conocer el total sobre todo lo demás.

Para un sistema con $N$ componentes binarios ese total es una suma sobre $2^N$
términos. En $N = 300$ supera el número de átomos del universo observable.

> **La pregunta.**
> Una energía $E(x)$, evaluable en cualquier punto. La densidad que define,
> $p(x) = e^{-E(x)/T}/Z$, con $Z$ inalcanzable.
> **¿Cómo extraes muestras de $p$?**

No «cómo aproximas $Z$» —ese es un problema distinto y en su mayor parte
desesperado. Las muestras bastan para todo lo que alguien quiere de verdad:
promedios, incertidumbres, la forma de la distribución, las configuraciones
más probables. Y resulta que las muestras son alcanzables cuando la
probabilidad misma no lo es.

---

## 2. Para qué sirve esto

### 2.1 Física estadística, que es de donde vino

Un imán son $10^{23}$ espines con una energía, y toda pregunta sobre él es un
promedio sobre la distribución de Boltzmann. La función de partición es
exactamente la $Z$ de arriba y es exactamente igual de inalcanzable. El
muestreo no es aquí una comodidad numérica; es la única vía a la respuesta
para cualquier modelo que no sea exactamente resoluble, que son casi todos.

Mi propio [`GPU-accelerated-Ising-Model`](https://github.com/FullFran/GPU-accelerated-Ising-Model)
es este documento aplicado al modelo de Ising 3D a una escala que esta entrada
deliberadamente no tiene.

### 2.2 Inferencia bayesiana

La posterior es
$p(\theta \mid D) \propto p(D \mid \theta)\thinspace p(\theta)$,
y ese $\propto$ esconde una integral sobre el espacio de parámetros que nadie
puede hacer. Todo cálculo bayesiano moderno es una cadena, y Metropolis es
el antepasado de todos ellos.

### 2.3 Optimización, que es lo mismo en frío

Baja la temperatura mientras corre la cadena y deja de explorar y empieza a
converger hacia la energía más baja que puede encontrar. Eso es el recocido
simulado (Kirkpatrick, Gelatt & Vecchi, 1983), y lo único que cambió es que
$T$ pasó a ser una función del tiempo.
[§10.3](#103-el-mismo-código-optimizando) lo mide.

### 2.4 Sistemas complejos, y la palabra para lo que falla

Aquí es donde la entrada deja de ser un ejercicio de métodos numéricos.

Una cadena que no puede cruzar una barrera en el tiempo del que dispones no es
una cadena rota. Es un **vidrio**. La ergodicidad —la suposición de que una
trayectoria suficientemente larga visita los estados en proporción a su
probabilidad— es una afirmación sobre tiempo infinito, y todo sistema real y
toda cadena real tienen tiempo finito. Cuando ambos no coinciden, el sistema
tiene una distribución estacionaria a la que no puede llegar, y esa es la
definición de ruptura de ergodicidad.

No es un caso exótico. Es el vidrio de las ventanas, que es un líquido que no
consiguió encontrar su cristal. Es un vidrio de espín, que es
[`hopfield/`](../../hopfield/README.md) con acoplamientos aleatorios. Es la
razón de que plegar proteínas sea difícil y de que el recocido simulado tenga
que ser lento. **El experimento del doble pozo en
[§10.2](#102-donde-una-cadena-te-miente) es ese fenómeno en una dimensión**,
lo bastante pequeño como para tener una respuesta exacta sobre la que
equivocarse.

La cantidad relacionada es la **ralentización crítica**: cerca de una
transición de fase la longitud de correlación diverge, y con ella el tiempo
que necesita una cadena para producir una muestra independiente. El
diagnóstico que la detecta es el tiempo de autocorrelación en
[`solve.py`](../solve.py) —el mismo número, haciendo el mismo trabajo, en un
juguete unidimensional.

### 2.5 Historia

::: **Markov, Nekrasov y una discusión sobre el libre albedrío** ·
*Verificación: A — Basharin, Langville & Stewart (2004); Hayes (2013).*

Pavel Nekrasov era matemático en la Universidad de Moscú, antiguo seminarista
y parte de una escuela que tomaba la ley de los grandes números como prueba a
favor de la teología. Su argumento era así: la ley de los grandes números
exige ensayos independientes; las estadísticas sociales —tasas de
criminalidad, tasas de matrimonio— obedecen la ley de los grandes números;
por tanto los actos humanos son independientes; por tanto son libres.

Andrey Markov, en San Petersburgo, era ateo, republicano y, según todos los
testimonios, espectacularmente desagradable. Le pareció que el argumento era
basura, y en vez de decirlo **construyó un contraejemplo**: una sucesión de
variables que son explícitamente *dependientes* —la distribución de cada una
fijada por la anterior— y que obedece la ley de los grandes números de todos
modos.

Ese contraejemplo es la cadena de Markov. Existe porque alguien quería ganar
una discusión sobre el libre albedrío.

Markov tuvo entonces que demostrarlo sobre algo real, y lo que eligió fueron
**las primeras 20,000 letras del *Eugene Onegin* de Pushkin**, clasificadas a
mano en vocales y consonantes, contadas por pares. Midió la probabilidad de
que una vocal siga a una vocal y encontró que no era la probabilidad de que
aparezca una vocal —dependencia, en un texto, obedeciendo la ley de los
grandes números. Lo publicó en 1913.

En esta historia no hay ningún ordenador por ninguna parte. Hay un hombre con
un temperamento hostil, una novela en verso y veinte mil marcas de lápiz.

::: **Quién escribió el algoritmo de Metropolis** ·
*Verificación: A — Gubernatis,* Physics of Plasmas **12**, 057303 (2005),
*a partir de una entrevista con Marshall Rosenbluth poco antes de su muerte.*

El artículo de 1953 es *Equation of State Calculations by Fast Computing
Machines*, seis páginas, cinco autores en orden alfabético: Nicholas
Metropolis, Arianna W. Rosenbluth, Marshall N. Rosenbluth, Augusta H. Teller
y Edward Teller.

El relato de Marshall Rosenbluth sobre quién hizo qué:

- **Metropolis** aportó tiempo de máquina y la infraestructura del MANIAC. No
  participó en el desarrollo del algoritmo.
- **Edward Teller** hizo una sugerencia temprana importante: muestrear en el
  espacio de configuraciones en vez de en el espacio de momentos, ya que la
  parte cinética se integra analíticamente.
- **Augusta Teller** empezó parte de la programación.
- **Marshall y Arianna Rosenbluth** desarrollaron el algoritmo y escribieron
  el programa. Arianna Rosenbluth, doctora en física por Harvard, programó el
  MANIAC por completo.

Rosenbluth lo resumió diciendo que Metropolis no tuvo nada que ver con el
desarrollo más allá de proporcionar tiempo de cómputo.

El algoritmo se llama universalmente Metropolis. El orden alfabético puso su
nombre el primero en un artículo a cuya idea no contribuyó, y el nombre de la
persona que de verdad lo programó no está unido a nada.

### Artículos que vale la pena leer

| Referencia | Por qué |
|---|---|
| [Metropolis et al., *J. Chem. Phys.* **21**, 1087 (1953)](https://doi.org/10.1063/1.1699114) | Seis páginas. El algoritmo, y ver la historia de arriba |
| [Hastings, *Biometrika* **57**, 97 (1970)](https://doi.org/10.1093/biomet/57.1.97) | La generalización a propuestas asimétricas |
| [Gubernatis, *Phys. Plasmas* **12**, 057303 (2005)](https://doi.org/10.1063/1.1887186) | Quién lo hizo de verdad |
| [Basharin, Langville & Stewart, *Lin. Alg. Appl.* **386**, 3 (2004)](https://doi.org/10.1016/j.laa.2003.12.041) | Markov, Nekrasov y *Eugene Onegin* |
| [Roberts & Tweedie, *Bernoulli* **2**, 341 (1996)](https://doi.org/10.2307/3318418) | Por qué Langevin sin ajustar está sesgado, y MALA |
| [Roberts & Rosenthal, *Stat. Sci.* **16**, 351 (2001)](https://doi.org/10.1214/ss/1015346320) | La tasa de aceptación óptima, y por qué es 0.234 |
| [Neal, *Handbook of MCMC*, ch. 5 (2011)](https://arxiv.org/abs/1206.1901) | Hamiltonian Monte Carlo: el arreglo para los paseos aleatorios |
| [Song & Ermon, *NeurIPS* (2019)](https://arxiv.org/abs/1907.05600) | Langevin con un score *aprendido*. La salida de esta entrada |

---

## 3. Antes de calcular

La regla del libro: **escribe un número antes de leer la siguiente sección.**
El aprendizaje está en la distancia entre tu número y el real, y la distancia
no existe si no te comprometiste.

> 1. Quieres muestras de $p \propto e^{-E}$ en 100 dimensiones. El método
>    obvio es extraer uniformemente y quedarse con puntos en proporción a $p$.
>    **¿Qué fracción de las extracciones sobrevive?**
> 2. Una cadena corre un millón de pasos. **¿Cuántas muestras independientes
>    valen eso?** ¿Un millón? ¿Y qué tendrías que medir para saberlo?
> 3. Una barrera del doble de alta que la temperatura cuesta cierto número de
>    pasos cruzar. **Hazla cuatro veces más alta: ¿cuánto más lento?** ¿El
>    doble? ¿Cuatro veces?

Respuestas en [§4](#4-por-qué-falla-la-respuesta-ingenua) y
[§8](#8-análisis-de-escalas-cuánto-tarda-en-olvidar). La primera es la razón
de que existan las cadenas de Markov, y la tercera es la razón de que existan
los vidrios.

---

## 4. Por qué falla la respuesta ingenua

### 4.1 La asimetría con la que empieza todo

Puedes evaluar $E(x)$ en cualquier punto. No puedes evaluar

$$Z = \int e^{-E(x)/T}\thinspace dx$$

porque es una integral sobre todo el espacio. Así que puedes calcular

$$\frac{p(y)}{p(x)} = e^{-\left(E(y)-E(x)\right)/T}$$

para cualquier par de puntos —la $Z$ se cancela— y nunca puedes calcular
$p(x)$.

Todo en este documento es una manera de vivir con eso. Y el replanteamiento
útil no es «$Z$ es difícil» sino: **los cocientes bastan**, si puedes
encontrar un procedimiento que solo los pida a ellos.

### 4.2 Muestreo por rechazo, y lo mal que muere

La respuesta de manual: extrae $x$ de algo fácil, acéptalo con probabilidad
proporcional a $p(x)/q(x)$. Es correcto, no necesita cadena y produce muestras
genuinamente independientes.

También es inútil en cualquier número interesante de dimensiones, y la razón
vale la pena hacerla como aritmética en vez de aceptarla por fe.

Toma $p$ una gaussiana unitaria en $d$ dimensiones y $q$ una gaussiana con
desviación típica $\sigma \gt 1$. La mejor tasa de aceptación posible es
$\sigma^{-d}$ —el cociente de las normalizaciones. En $\sigma = 1.1$, apenas
un desajuste:

| $d$ | aceptación |
|---|---|
| 1 | 0.91 |
| 10 | 0.39 |
| 100 | $7\times10^{-5}$ |
| 1000 | $10^{-42}$ |

*Respuesta a la pregunta 1: esencialmente ninguna.* Y el fallo no se arregla
eligiendo mejor $q$, porque viene del volumen. En dimensión alta casi todo el
volumen de cualquier región está cerca de su frontera, y dos distribuciones
que parecen similares se concentran en cortezas que apenas se solapan.

**Así que la salida es renunciar a la independencia.** No extraigas un punto
nuevo; modifica el que tienes. Esa es toda la idea de una cadena de Markov, y
lo que cuesta es que las muestras consecutivas están correlacionadas
([§8](#8-análisis-de-escalas-cuánto-tarda-en-olvidar)).

### 4.3 Y una respuesta ingenua más sutil

Sigue el gradiente cuesta abajo y añade ruido. Eso es Langevin, está en
[`methods/langevin.py`](../methods/langevin.py), y es *casi* correcto
—correcto en el límite de tiempo continuo y equivocado con cualquier tamaño
de paso que puedas tomar de verdad.

El fallo es silencioso: la cadena converge, su barra de error se encoge, y
converge a la distribución equivocada.
[§7.3](#73-el-precio-de-no-rechazar-nunca) calcula exactamente cuánto de
equivocada.

---

## 5. El modelo mínimo

Cada suposición de abajo compra una simplificación concreta, y cada una de
ellas falla en algún sitio real.

| Suposición | Qué compra | Dónde se rompe |
|---|---|---|
| El objetivo es $e^{-E/T}$ | Una sola función escalar lo define todo | Distribuciones sin densidad; soportes discretos |
| $E$ es barata de evaluar | Millones de pasos son asequibles | Una verosimilitud que necesita resolver una EDP en cada llamada |
| $E$ es diferenciable | Langevin existe siquiera | Variables discretas; restricciones duras |
| $T \gt 0$ | Hay una distribución que muestrear | En $T = 0$ es una delta, y la dinámica es descenso |
| Una sola cadena | Simplicidad | Nada de aquí puede detectar un modo que nunca visitó |
| Una propuesta simétrica | El cociente de Metropolis no lleva $q$ dentro | La corrección de Hastings para propuestas asimétricas |
| Un tamaño de paso fijo | Un solo número sobre el que razonar | Todo muestreador real lo adapta |
| Una dimensión | Las formas cerradas existen | El problema del paseo aleatorio es invisible hasta que $d$ es grande |
| $T$ independiente del tiempo | La cadena tiene una distribución estacionaria | El recocido no tiene ninguna, y no es un muestreador |

La última fila importa más de lo que parece. **Una cadena con un calendario no
es un muestreador**, porque un objetivo en movimiento no tiene distribución
estacionaria a la que converger. Por eso el experimento de recocido escribe su
propio bucle en vez de pasar por `solve.chain`.

---

## 6. Las ecuaciones

### 6.1 Qué es una cadena de Markov

Una sucesión $x_0, x_1, x_2, \dots$ donde la distribución del siguiente estado
depende solo del actual:

$$\mathbb{P}\left(x_{t+1} \mid x_t, x_{t-1}, \dots, x_0\right)
= \mathbb{P}\left(x_{t+1} \mid x_t\right) \equiv K(x_t \to x_{t+1})$$

$K$ es el **núcleo de transición**. Esa única línea es toda la definición, y
es la que Markov escribió para ganarle a Nekrasov: las variables son
dependientes —cada una de la anterior— y ninguno de los argumentos que
necesitan independencia se aplica.

Una distribución $\pi$ es **estacionaria** para $K$ si dar un paso desde $\pi$
te deja en $\pi$:

$$\int \pi(x)\thinspace K(x \to y)\thinspace dx = \pi(y)$$

El plan ya es visible: **construye un $K$ cuya distribución estacionaria sea
la $p$ que quieres, córrelo y lee los estados.** Hay que arreglar dos cosas
—que $p$ sea estacionaria, y que la cadena llegue de verdad hasta ahí.

### 6.2 Balance detallado, que es una condición suficiente

La estacionariedad es una ecuación integral y difícil de imponer
directamente. Hay una condición más fuerte que es trivial de imponer y que la
implica:

$$\boxed{\enspace p(x)\thinspace K(x \to y) = p(y)\thinspace K(y \to x)\enspace}$$

**Balance detallado**: el flujo de probabilidad de $x$ a $y$ es igual al flujo
de vuelta. Integra ambos lados en $x$ y la estacionariedad cae sola, ya que
$K$ integra a uno.

Vale la pena ver que esto es una afirmación física y no un truco. Dice que la
cadena es *reversible* —una película suya proyectada al revés es
estadísticamente indistinguible— y eso es exactamente lo que significa
«equilibrio». Un sistema en equilibrio no tiene corriente neta en ninguna
parte, que es una afirmación más fuerte que «su distribución no está
cambiando».

### 6.3 Metropolis: imponerlo rechazando

Propón $y$ desde un $q(x \to y) = q(y \to x)$ simétrico, y acepta con
probabilidad $A(x \to y)$. Entonces $K(x \to y) = q(x \to y)A(x \to y)$ para
$y \neq x$, y el balance detallado exige

$$\frac{A(x \to y)}{A(y \to x)} = \frac{p(y)}{p(x)}
= e^{-\left(E(y)-E(x)\right)/T}$$

Cualquier $A$ que satisfaga ese cociente funciona. La elección que acepta tan
a menudo como es posible —y por tanto explora más rápido— es

$$\boxed{\enspace A(x \to y)
= \min\negthinspace\left(1,\ e^{-\Delta E/T}\right)\enspace}$$

$Z$ no aparece nunca, porque solo aparece el cociente. Nueve líneas de código,
1953, en una máquina con 1024 palabras de memoria.

**El rechazo no es trabajo desperdiciado.** Es el mecanismo. La cadena se
queda quieta exactamente con la frecuencia necesaria para que los flujos se
equilibren, y por eso la distribución estacionaria es el objetivo
*exactamente*, con cualquier tamaño de paso, sin ningún parámetro pequeño por
ninguna parte.

### 6.4 Langevin: imponerlo tomando un límite

La otra vía. Escribe un proceso estocástico en tiempo continuo cuya densidad
estacionaria sea $p$:

$$dx = -\nabla E(x)\thinspace \frac{dt}{T} \cdot T + \sqrt{2T}\thinspace dW
\quad\text{i.e.}\quad
dx = -\nabla E\thinspace dt + \sqrt{2T}\thinspace dW$$

La ecuación de Fokker–Planck para este proceso tiene $e^{-E/T}$ como solución
estacionaria —la deriva empuja la probabilidad cuesta abajo y la difusión la
empuja de vuelta hacia fuera, y $e^{-E/T}$ es donde se equilibran.

Aquí también desaparece $Z$, y por una razón distinta que vale la pena ver:

$$\log p = -\frac{E}{T} - \log Z
\quad\Longrightarrow\quad
\nabla \log p = -\frac{\nabla E}{T}$$

porque el gradiente de una constante es cero.

> **Las dos salidas son la misma salida.** $Z$ es una constante, y ni un
> cociente ni el gradiente de un logaritmo pueden ver una constante.
> Metropolis usa el primer hecho, Langevin el segundo.

Ese gradiente de una densidad logarítmica tiene nombre —el **score**— y es el
objeto que un modelo de difusión aprende en vez de derivarlo de una energía
que alguien escribiera. Es aprendible *precisamente porque* nunca necesita
$Z$: no hay nada que normalizar, así que no hay nada intratable que ajustar.

### 6.5 Ergodicidad, que es la suposición que nadie comprueba

La estacionariedad dice: si ya estás en $p$, te quedas. No dice que llegues
nunca.

Para eso necesitas que la cadena sea **irreducible** —capaz de alcanzar
cualquier región desde cualquier otra— y **aperiódica**. Con ambas, la cadena
converge a $p$ desde cualquier inicio, y los promedios temporales convergen a
esperanzas. Ese es el teorema ergódico, y es lo que autoriza todo el método.

También está enunciado para tiempo infinito, y toda ejecución es finita. Una
cadena que es irreducible en principio y tarda $e^{10}$ pasos en cruzar una
barrera no es, para tus fines, irreducible en absoluto. **El teorema es cierto
y no se aplica.** Esa distancia tiene nombre en física —ruptura de
ergodicidad— y es [§10.2](#102-donde-una-cadena-te-miente).

---

## 7. Dos cadenas, una densidad

### 7.1 Qué compra y qué cuesta Metropolis

**Exacto con cualquier tamaño de paso.** El rechazo impone el balance
detallado directamente, así que no hay parámetro de discretización ni sesgo
que encoger.

**Y es un paseo aleatorio ciego.** La propuesta no sabe nada del objetivo —da
un paso en una dirección aleatoria y pregunta después. El tamaño de paso tiene
que ser lo bastante pequeño para ser aceptado y lo bastante grande para ir a
alguna parte, y esas dos exigencias pelean. En $d$ dimensiones la tasa de
aceptación óptima cae a 0.234 y el número de pasos necesarios para recorrer la
distribución crece como $d^2$ (Roberts & Rosenthal 2001).

### 7.2 Qué compra Langevin

**Sabe hacia dónde está cuesta abajo.** El gradiente es información sobre el
objetivo que Metropolis nunca pide, y usarla convierte un paseo aleatorio en
una deriva dirigida. Esa es toda la razón de que existan los muestreadores
basados en gradiente y de que dominen en dimensión alta.

### 7.3 El precio de no rechazar nunca

Nada rechaza, así que nada impone el balance detallado, y la cadena
discretizada tiene una distribución estacionaria *cerca* de $p$ en vez de $p$.

En $E = x^2/2$ con $T=1$ la actualización es exactamente un proceso AR(1):

$$x' = (1 - \Delta t)\thinspace x + \sqrt{2\Delta t}\thinspace \xi$$

cuya varianza estacionaria resuelve $\sigma^2 = (1-\Delta t)^2\sigma^2 + 2\Delta t$:

$$\boxed{\enspace \sigma^2 = \frac{2\Delta t}{1 - (1-\Delta t)^2}
= \frac{1}{1 - \Delta t/2}\enspace}$$

El objetivo tiene varianza 1. **La respuesta equivocada tiene forma cerrada**,
es demasiado ancha en $\Delta t/2$ a primer orden, y ningún número de muestras
la elimina.

Reproducir tu propio error exactamente es una prueba mucho más afilada que
acertar aproximadamente, y es la prueba sobre la que está construida la
entrada.

**El arreglo tiene nombre.** Ajusta con Metropolis la propuesta de Langevin
—acéptala con el cociente de Metropolis, corregido por la asimetría de la
propuesta— y el sesgo desaparece mientras la información del gradiente se
queda. Eso es MALA, son unas dos líneas, y dejarlo fuera es lo que hace que el
sesgo sea medible aquí.

---

## 8. Análisis de escalas: cuánto tarda en olvidar

### 8.1 Un millón de muestras no son un millón de muestras

Los estados consecutivos de una cadena son casi el mismo estado. El número que
dice cuánto es el **tiempo de autocorrelación integrado**

$$\tau = 1 + 2\sum_{k=1}^{\infty} \rho(k),
\qquad \rho(k) = \mathrm{corr}\left(f(x_t), f(x_{t+k})\right)$$

y el recuento honesto de muestras independientes es

$$N_{\text{eff}} = \frac{N}{\tau},
\qquad
\text{error} = \frac{\sigma}{\sqrt{N_{\text{eff}}}}$$

*Respuesta a la pregunta 2: un millón dividido por $\tau$, y tienes que medir
$\tau$ para saberlo.* Depende del objetivo, del método, del tamaño de paso y
del observable, y rutinariamente está en las decenas o centenas. Reportar
$\sigma/\sqrt{N}$ en su lugar no es un error pequeño —es afirmar una precisión
que no tienes por un factor $\sqrt{\tau}$.

Ten en cuenta que la suma hay que truncarla. La cola de una autocorrelación
empírica es ruido, y sumarla entera añade varianza sin señal; la ventana
automática estándar es parar en cuanto el desfase supere unas pocas veces la
estimación corriente, que es lo que hace
[`autocorrelation_time()`](../solve.py).

### 8.2 Las barreras cuestan exponencialmente

*Respuesta a la pregunta 3.* El tiempo para cruzar una barrera de altura
$\Delta$ a temperatura $T$ crece como

$$t_{\text{cross}} \sim e^{\Delta/T}$$

que es la ley de Arrhenius, y el cálculo de Kramers de 1940 es de donde sale
el prefactor. Doblar $\Delta/T$ no dobla el tiempo: lo *eleva al cuadrado*.

Medido en el doble pozo con una cadena de Metropolis, pasos entre cruces:

| $\Delta/T$ | 1.17 | 1.95 | 2.92 | 3.89 | 4.67 | 5.84 |
|---|---|---|---|---|---|---|
| pasos por cruce | 11.8 | 17.9 | 33.2 | 64.4 | 118 | 282 |

Exponencial, con una barrera efectiva *más baja* que la del paisaje —la
pendiente ajustada está en torno a 0.7 en vez de 1— porque una propuesta de
anchura finita puede empezar a medio subir. Que es el mismo hecho que hizo que
el experimento de recocido se portara mal hasta que se hizo local la propuesta
([§10.3](#103-el-mismo-código-optimizando)).

### 8.3 Y eso es lo que es un vidrio

Extrapola la tabla. En $\Delta/T = 20$ el tiempo de cruce es $10^6$ pasos; en
40 es $10^{12}$; en 100 ningún ordenador y ningún laboratorio verá jamás uno.

La cadena sigue *teniendo* una distribución estacionaria. El teorema ergódico
sigue siendo cierto. Y el sistema se quedará en una cuenca durante más tiempo
que la edad del universo, así que la distribución que muestrea de verdad es la
restringida a esa cuenca.

Eso no es un artefacto numérico —es la física de los vidrios, de los vidrios
de espín, del plegamiento incorrecto de proteínas, de cualquier sistema cuyo
paisaje sea lo bastante rugoso. **[`hopfield/`](../../hopfield/README.md) es un
vidrio de espín**, y los mínimos espurios en los que queda atrapado son el
mismo fenómeno a $T = 0$.

La lectura de sistemas complejos de la entrada es exactamente esta: una
distribución estacionaria es una propiedad de la dinámica, y si puedes *verla*
es una propiedad de tu paciencia.

---

## 9. Formas cerradas que vale la pena memorizar

| Situación | Resultado |
|---|---|
| El objetivo | $p \propto e^{-E/T}$, y solo son calculables cocientes de ella |
| Balance detallado | $p(x)K(x\to y) = p(y)K(y\to x)$ |
| Aceptación de Metropolis | $\min(1, e^{-\Delta E/T})$ |
| Actualización de Langevin | $x \leftarrow x - \nabla E\thinspace\Delta t + \sqrt{2T\Delta t}\thinspace\xi$ |
| El score | $\nabla\log p = -\nabla E/T$ |
| Objetivo gaussiano, $E=x^2/2$ | $\langle x^2\rangle = T$ exactamente |
| Langevin sin ajustar sobre él | $\langle x^2\rangle = 1/(1-\Delta t/2)$ — el sesgo exacto |
| Langevin libre, $E=0$ | $\langle x^2\rangle = 2Tt$ — movimiento browniano |
| Tamaño de muestra efectivo | $N/\tau$ |
| Aceptación por rechazo en $d$ dimensiones | $\sigma^{-d}$ — sin esperanza |
| Aceptación óptima de Metropolis, $d$ grande | $0.234$ |
| Coste de recorrido del paseo aleatorio | $\sim d^2$ pasos |
| Tiempo de cruce de barrera | $\sim e^{\Delta/T}$ |
| Dos pozos, cociente de poblaciones | $e^{-\Delta E/T}$ por un cociente de anchuras |

**Una advertencia sobre la última fila.** Es tentador probar un muestreador
comprobando que el estado de baja energía está más poblado que el de alta
energía. Eso pasa en una cadena que nunca salió de un pozo, en una cadena
sesgada y en una cadena con la temperatura equivocada. Las formas cerradas con
números dentro tienen más rango que ella, y un diagnóstico tiene más rango que
las dos —mira la siguiente sección.

---

## 10. Lo que mostró la simulación

### 10.1 La respuesta equivocada, sobre su propia curva

Predicción: Metropolis aterriza en 1 con cualquier tamaño de paso; Langevin
aterriza en $1/(1-\Delta t/2)$, una curva que puedes dibujar antes de correr
nada.

![Izquierda: segundo momento medido frente al tamaño de paso para Langevin,
contra la curva de sesgo en forma cerrada y el objetivo. Derecha: histogramas
muestreados frente a la densidad objetivo en eje logarítmico.](figures/gaussian.png)

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

**Qué concluir**, y la tercera cosa no estaba predicha.

Ambas predicciones se sostuvieron. Ahora lee las barras de error de Langevin
hacia abajo mientras cae el sesgo: **0.0040, 0.0056, 0.0076, 0.0106, 0.0163.**
*Crecen*. Un paso más pequeño está menos sesgado y más correlacionado, el
tamaño de muestra efectivo se derrumba, y la barra de error se ensancha hasta
cubrir el sesgo. En $\Delta t = 0.02$ la cadena es «compatible con 1» a
$0.1\sigma$ solo porque se ha vuelto cuatro veces menos segura de todo.

**No puedes arreglar el sesgo encogiendo el paso.** Lo cambias por
correlación, y la barra de error esconde el intercambio con educación.

Ambos métodos tienen un compromiso con el tamaño de paso y son compromisos
distintos. Metropolis cambia aceptación por exploración —con 0.905 de
aceptación los pasos son tan pequeños que $\tau = 30$, con 0.374 de aceptación
$\tau = 5$— y *la respuesta no se mueve nunca*. Langevin cambia sesgo por
correlación, y la respuesta sí se mueve.

### 10.2 Donde una cadena te miente

![Izquierda: la energía del doble pozo. Derecha: fracción de tiempo en el pozo
derecho frente a la temperatura, para ambos muestreadores y la respuesta
exacta.](figures/double_well.png)

```
     T  barrier/T  exact P(x>0)             metropolis               langevin
  1.00        1.2        0.6216     0.6219 ( 25428 x)     0.5757 (  2395 x)
  0.20        5.8        0.9449     0.9406 (  1030 x)     0.9998 (    16 x)
  0.10       11.7        0.9972     0.9972 (    18 x)     0.0000 (     0 x)
  0.05       23.3        1.0000     1.0000 (     0 x)     0.0000 (     0 x)
```

El recuento entre paréntesis es el de cruces de barrera.

**Qué concluir:** en $T = 0.10$ **Langevin reporta 0.0000 donde la verdad es
0.9972.** Empezó en el pozo izquierdo, sus pasos eran demasiado pequeños para
salir trepando, y nunca salió —con aspecto de convergido, monótono, con la
barra de error encogiéndose, y exactamente lo contrario de la respuesta.

Y la última fila es la más afilada. **Metropolis acertó con cero cruces.**
Cruzó durante el calentamiento y luego se quedó quieto. Una respuesta correcta
de una cadena que nunca muestreó la distribución no es una respuesta correcta;
es el mismo fallo que dio la casualidad de caer del lado correcto.

**El diagnóstico pilló los dos. Ninguno de los números podía.** Ese es el
contenido práctico de §6.5: la irreducibilidad no es algo que puedas leer de
una estimación, y una cadena reporta su cuenca exactamente con la misma
confianza tanto si esa cuenca es la distribución como si no.

### 10.3 El mismo código, optimizando

![Izquierda: la trayectoria de tres calendarios de temperatura. Derecha: la
mejor energía que ha encontrado cada uno hasta el momento.](figures/annealing.png)

```
              schedule   final x    final E  best E seen   ended in
    frozen  (T = 0.02)   -0.9985    0.29957      0.29415  LEFT well
     hot     (T = 2.0)   -0.4131    0.81173     -0.30543  LEFT well
 cooled  (2.0 -> 0.02)   +1.0202   -0.30440     -0.30543      right
```

**Qué concluir:** la congelada nunca tuvo la energía para cruzar, así que
optimizó el pozo en el que empezó y ni siquiera *vio* el mínimo global. La
caliente lo encontró y no se asentaba —está muestreando, no optimizando. Solo
la enfriada hizo las dos cosas.

Optimizar y muestrear son la misma operación a dos temperaturas, que es el
argumento del capítulo 10 del libro, medido.

**Una corrección que forzó el montaje.** La primera versión usaba una anchura
de propuesta de 0.5 y predecía que la cadena congelada se quedaría quieta. No
lo hizo —acabó en el pozo derecho. Con los pozos en $\pm 1$, una anchura de
0.5 propone un salto directo de un mínimo al otro, el movimiento es cuesta
abajo, y se acepta a cualquier temperatura. **La barrera solo te atrapa si tus
movimientos son locales.** El recocido es una cura para los movimientos
locales, y una propuesta lo bastante ancha como para salvar la barrera de un
paso significa que no había problema que resolver —y ninguna posibilidad de
que eso funcione en un número real de dimensiones.

---

## 11. Dónde el modelo deja de ser cierto

| Límite | Qué pasa en realidad | Esta entrada |
|---|---|---|
| Langevin sin ajustar, cualquier $\Delta t$ | Muestrea una distribución cerca del objetivo, nunca él | medido; MALA dejado fuera |
| Encoger $\Delta t$ para arreglarlo | Cambia sesgo por correlación; la barra de error esconde el intercambio | medido |
| Una barrera mucho más alta que $T$ | Cualquiera de las dos cadenas se queda en un modo y lo reporta con confianza | medido |
| Una respuesta correcta con cero cruces | No es evidencia de nada | el diagnóstico, no el número |
| Propuesta más ancha que la barrera | La barrera deja de importar, y el recocido también | descubierto por las malas |
| Dimensión alta | La aceptación se derrumba; un paseo aleatorio necesita $\sim d^2$ pasos | solo una dimensión |
| Una sola cadena | No puede detectar un modo que nunca visitó | sin $\hat R$, sin cadenas múltiples |
| Una temperatura dependiente del tiempo | No hay distribución estacionaria; no es un muestreador | mantenida fuera de `solve.chain` |
| Una $E$ cara | Millones de evaluaciones dejan de ser gratis | supuesta barata |

**La fila de una sola cadena es el resumen honesto.** Nada en esta entrada
puede decirte nada sobre una parte de la distribución a la que nunca llegó, y
correrla más tiempo no cambia eso —cambia lo segura que parece la respuesta
equivocada. La defensa estándar son varias cadenas desde inicios dispersos y
una comparación de la varianza dentro de las cadenas y entre ellas, y no está
aquí.

---

## 12. Lo esencial

- **Puedes conocer todos los cocientes de probabilidades y ninguna
  probabilidad.** $Z$ es una integral sobre todo, y todo es demasiado grande.
- **Los cocientes bastan**, si el procedimiento solo los pide a ellos.
- **Ambos métodos esquivan $Z$ por la misma razón**: es una constante, y ni un
  cociente ni el gradiente de un logaritmo pueden ver una constante.
- **El gradiente de la densidad logarítmica es el score**, y es lo que aprende
  un modelo de difusión —aprendible exactamente porque no necesita
  normalizador.
- **El muestreo por rechazo muere de dimensión**, a un ritmo como
  $\sigma^{-d}$. Renuncia a la independencia, quédate con el punto que tienes,
  y tienes una cadena de Markov.
- **El balance detallado es reversibilidad**, y es una condición suficiente
  para la estacionariedad que puedes imponer movimiento a movimiento.
- **Rechazar es el mecanismo, no desperdicio.** Es lo que hace a Metropolis
  exacto con cualquier tamaño de paso.
- **No rechazar nunca es exactamente por qué Langevin está sesgado**, en
  $1/(1-\Delta t/2)$ sobre una gaussiana —una forma cerrada para estar
  equivocado.
- **Un millón de muestras son $N/\tau$ muestras.** Mide $\tau$ o exagera tu
  precisión por $\sqrt{\tau}$.
- **Las barreras cuestan $e^{\Delta/T}$.** Dobla el cociente y elevas el
  tiempo al cuadrado.
- **La ergodicidad es un teorema sobre tiempo infinito.** Cuando el tiempo del
  que dispones es más corto, el sistema tiene una distribución a la que no
  puede llegar —y eso es lo que es un vidrio.
- **Converger no es acertar, y una respuesta correcta no es evidencia.**
  Comprueba el diagnóstico.

---

## 13. Preguntas abiertas

- **¿Cuánto compra MALA en realidad?** Ajustar con Metropolis la propuesta de
  Langevin elimina el sesgo y conserva el gradiente. Dos líneas, y medir dónde
  se derrumba su tasa de aceptación diría cuándo el gradiente deja de ayudar.
- **¿Por qué el momento es la respuesta a los paseos aleatorios?** Hamiltonian
  Monte Carlo viaja balísticamente en vez de difundir, convirtiendo $d^2$ en
  aproximadamente $d^{1/4}$ en el coste de una muestra independiente. El
  mecanismo es un integrador simpléctico, que es el mismo objeto que el
  integrador de Boris.
- **¿Qué hace en realidad la dimensión alta?** Toda forma cerrada de aquí vive
  en una dimensión, que es exactamente donde el fallo interesante es invisible.
- **¿Cómo detectas un modo que nunca visitaste?** No puedes, en general —lo
  que hace que valga la pena saber con precisión qué pueden y qué no pueden
  ver los diagnósticos estándar.
- **¿Qué pasa cuando el score se aprende en vez de derivarse?** Sustituye
  $\nabla E$ por la salida de una red y Langevin se convierte en modelado
  generativo basado en score; añade un calendario de ruido recorrido al revés
  y es un modelo de difusión. Las piezas están en
  [`mlp/`](../../mlp/README.md) y aquí.

---

## 14. Referencias

**Fundacionales**

- **Metropolis, N., Rosenbluth, A. W., Rosenbluth, M. N., Teller, A. H. &
  Teller, E.** *Equation of state calculations by fast computing machines.*
  Journal of Chemical Physics **21**, 1087–1092 (1953).
  [enlace](https://doi.org/10.1063/1.1699114)
- **Hastings, W. K.** *Monte Carlo sampling methods using Markov chains and
  their applications.* Biometrika **57**, 97–109 (1970).
  [enlace](https://doi.org/10.1093/biomet/57.1.97)
- **Markov, A. A.** *An example of statistical investigation of the text*
  Eugene Onegin *concerning the connection of samples in chains* (1913).
  Traducido en Science in Context **19**, 591–600 (2006).

**La historia**

- **Gubernatis, J. E.** *Marshall Rosenbluth and the Metropolis algorithm.*
  Physics of Plasmas **12**, 057303 (2005).
  [enlace](https://doi.org/10.1063/1.1887186)
- **Basharin, G. P., Langville, A. N. & Naumov, V. A.** *The life and work of
  A. A. Markov.* Linear Algebra and its Applications **386**, 3–26 (2004).
  [enlace](https://doi.org/10.1016/j.laa.2003.12.041)
- **Hayes, B.** *First links in the Markov chain.* American Scientist **101**,
  92 (2013).

**Teoría y práctica**

- **Roberts, G. O. & Tweedie, R. L.** *Exponential convergence of Langevin
  distributions and their discrete approximations.* Bernoulli **2**, 341–363
  (1996). [enlace](https://doi.org/10.2307/3318418) — el sesgo, y MALA.
- **Roberts, G. O. & Rosenthal, J. S.** *Optimal scaling for various
  Metropolis-Hastings algorithms.* Statistical Science **16**, 351–367 (2001).
  [enlace](https://doi.org/10.1214/ss/1015346320) — de dónde sale 0.234.
- **Neal, R. M.** *MCMC using Hamiltonian dynamics.* Handbook of Markov Chain
  Monte Carlo, ch. 5 (2011). [enlace](https://arxiv.org/abs/1206.1901)
- **Kirkpatrick, S., Gelatt, C. D. & Vecchi, M. P.** *Optimization by simulated
  annealing.* Science **220**, 671–680 (1983).

**Sistemas complejos**

- **Kramers, H. A.** *Brownian motion in a field of force and the diffusion
  model of chemical reactions.* Physica **7**, 284–304 (1940). La tasa de
  escape.
- **Binder, K. & Young, A. P.** *Spin glasses: experimental facts, theoretical
  concepts, and open questions.* Reviews of Modern Physics **58**, 801 (1986).
- **Palmer, R. G.** *Broken ergodicity.* Advances in Physics **31**, 669 (1982).
  La versión precisa de §8.3.

**Hacia dónde va**

- **Song, Y. & Ermon, S.** *Generative modeling by estimating gradients of the
  data distribution.* NeurIPS (2019). [enlace](https://arxiv.org/abs/1907.05600)
- **Ho, J., Jain, A. & Abbeel, P.** *Denoising diffusion probabilistic models.*
  NeurIPS (2020). [enlace](https://arxiv.org/abs/2006.11239)

---

*Código: [`../distribution.py`](../distribution.py) y
[`../methods/`](../methods/) · Entrada: [`../README.md`](../README.md) ·
Arquitectura de todo el repositorio: [`docs/architecture.md`](../../docs/architecture.md)*
