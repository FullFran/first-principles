<!-- translated-from: 596e79338c4e -->

# Fotones a través de la materia

> La física detrás de [`photon-transport/`](../README.md), derivada del
> problema y no de la fórmula. Lee esto si quieres saber *por qué* las
> ecuaciones de `photon-transport/physics.py` son esas y no otras.

Este documento sigue un ciclo, y el ciclo es lo importante:

```
phenomenon → question → order of magnitude → assumptions → minimal model
   → equations → scale analysis → closed forms → simulation → validation
   → limits of the model → next question
```

El centro es lo que enseña una carrera. Los dos extremos —plantear la pregunta
y saber dónde se detiene el modelo— son lo que de verdad separa a quien
resuelve problemas nuevos de quien aplica fórmulas. Así que aquí el espacio es
para los dos extremos.

**Contenido**

1. [El fenómeno](#1-el-fenómeno)
2. [Para qué sirve](#2-para-qué-sirve)
3. [Antes de calcular](#3-antes-de-calcular)
4. [Por qué falla la respuesta ingenua](#4-por-qué-falla-la-respuesta-ingenua)
5. [El modelo mínimo](#5-el-modelo-mínimo)
6. [Las ecuaciones](#6-las-ecuaciones)
7. [Dos estimadores, una integral](#7-dos-estimadores-una-integral)
8. [Análisis de escalas: todo es profundidad óptica](#8-análisis-de-escalas-todo-es-profundidad-óptica)
9. [Formas cerradas que vale la pena memorizar](#9-formas-cerradas-que-vale-la-pena-memorizar)
10. [Lo que mostró la simulación](#10-lo-que-mostró-la-simulación)
11. [Dónde el modelo deja de ser cierto](#11-dónde-el-modelo-deja-de-ser-cierto)
12. [Lo esencial](#12-lo-esencial)
13. [Preguntas abiertas](#13-preguntas-abiertas)
14. [Referencias](#14-referencias)

---

## 1. El fenómeno

Pon una linterna contra la palma de la mano en una habitación oscura y la mano
brilla en rojo. No la superficie: la mano entera, iluminada desde dentro, y
solo en rojo. Levanta la mano contra el sol y distingues los huesos como formas
más oscuras.

Algo parecido ocurre en un hospital, con luz más dura y un detector en lugar de
un ojo, y produce una imagen del interior de una persona sin abrirla.

Todas son la misma situación: **la luz entra en un material, parte se absorbe,
y lo que sale por el otro lado lleva información sobre aquello que
atravesó.**

Fíjate en lo que *no* está ocurriendo. Nada se enfoca. No hay lente, no hay
formación de imagen, no hay reflexión. La imagen está hecha por completo de lo
que sobrevivió, y cada región oscura es un lugar por donde más luz no pasó.

> **La pregunta.**
> Una fuente emite fotones en un cono de semiángulo $\alpha$. Una lámina de
> material de espesor $L$ y coeficiente de atenuación $\mu$ se interpone,
> y un detector está detrás.
> **¿Qué fracción de los fotones emitidos llega?**

Ese es todo el problema directo, y es lo que calcula `photon-transport/`.
Invíertelo —mide lo que llega y deduce qué era el objeto— y tienes tomografía,
que es otra entrada.

---

## 2. Para qué sirve

### 2.1 Ver dentro de las cosas sin abrirlas

La obvia, y es enorme: radiografía, TC, mamografía, inspección industrial de
soldaduras y piezas fundidas, seguridad aeroportuaria y el examen no destructivo
de cuadros y momias. Todas son la misma medida —contar lo que pasó, por píxel—
y todas están limitadas por lo mismo, que es [§10.3](#103-una-imagen-de-la-diferencia).

### 2.2 Decidir detrás de cuánto material colocarse

El diseño de blindajes es el mismo cálculo apuntando a otro número. Cuánto
hormigón alrededor de un reactor, cuánto plomo en un delantal, a qué distancia
de la fuente hay que ponerse. La respuesta es siempre una exponencial, que es lo
que lo hace tratable y también lo que lo hace implacable: reducir a la mitad la
dosis transmitida cuesta un espesor fijo, y la capa decirreductora es
[§8](#8-análisis-de-escalas-todo-es-profundidad-óptica).

### 2.3 La dosis, que es lo que nadie quiere pagar

Cada fotón que forma una imagen radiográfica es un fotón que el paciente
absorbió. Eso no es un efecto secundario de la medida, *es* la medida: la imagen
está hecha de los que fueron detenidos. Así que calidad de imagen y dosis son la
misma magnitud vista dos veces, y [§10.3](#103-una-imagen-de-la-diferencia)
muestra cuál es el tipo de cambio.

### 2.4 Luz a través de cualquier cosa turbia

Las mismas matemáticas gobiernan la óptica de la niebla, la leche, el tejido
biológico, las atmósferas planetarias, el polvo interestelar y la nieve. Mi
propio [`snow-mcrt`](https://github.com/FullFran/snow-mcrt) es este problema con
la dispersión puesta de vuelta, que es el paso que esta entrada deliberadamente
no da ([§11](#11-dónde-el-modelo-deja-de-ser-cierto)).

### 2.5 Y es de donde salió Monte Carlo

No «una aplicación de Monte Carlo»: la razón de que exista. El método se inventó
para el transporte de neutrones, que es este problema con los neutrones
autorizados a multiplicarse, y la historia es [§2.6](#26-historia).

### 2.6 Historia

::: El solitario · *Verificación: A — Ulam lo cuenta él mismo en* Adventures of
a Mathematician.

En enero de 1946 Stanisław Ulam convalecía en Los Ángeles de una encefalitis
aguda que casi lo mata y que le había costado una craneotomía de urgencia. No
podía trabajar en nada serio, así que jugaba al solitario Canfield.

Canfield tiene una tasa de éxito famosamente mala. Aburrido, Ulam se preguntó
cuál era en realidad la probabilidad de completarlo, intentó atacarlo con
combinatoria, vio el tamaño del problema —y se dio cuenta de que sería mucho más
práctico jugar cien manos y contar.

**Lo interesante es lo que pensó a continuación**, que fue el problema de
difusión de neutrones en el que había estado trabajando.

Ese salto es menos obvio de lo que parece en retrospectiva. En el solitario la
probabilidad es la magnitud que quieres y jugar es el proceso natural, así que
simular es la jugada evidente. En la difusión de neutrones la magnitud que
quieres es *determinista* —el factor de multiplicación de una masa de material
fisible, un número fijo— y lo que tienes es una ecuación integrodiferencial en un
espacio de fases de seis dimensiones que nadie sabía resolver para geometrías
realistas.

El salto está en ver que **la ecuación describe el comportamiento medio de un
proceso aleatorio subyacente**, y que por tanto puedes estimarla siguiendo
trayectorias individuales muestreadas: dónde choca un neutrón, qué ocurre cuando
lo hace, adónde va después. En lugar de resolver la ecuación para la media,
**genera la media**.

Ulam se lo contó a von Neumann. En marzo de 1947 von Neumann escribió a Robert
Richtmyer una carta de once páginas que no era una carta de ideas sino un plan
de cálculo completo para el ENIAC: el problema físico, el esquema de muestreo de
trayectorias, el tratamiento de las secciones eficaces, la generación de números
aleatorios. El nombre vino del tío de Ulam, que pedía dinero prestado para jugar
en Monte Carlo.

::: La ley de Beer, que es sobre todo la de Bouguer · *Verificación: B — la
cronología está bien documentada; la razón de que el nombre cuajara, no.*

A la exponencial de este documento se la suele llamar ley de Beer–Lambert, y a
veces Beer–Lambert–Bouguer, que es más justo y sigue estando en el orden
equivocado. Pierre Bouguer publicó la absorción exponencial de la luz en 1729.
Lambert la reformuló en 1760, citando a Bouguer. La aportación de Beer en 1852
fue la dependencia con la *concentración* de un soluto absorbente, que es un
enunciado genuinamente distinto y el que los químicos necesitaban.

Es un caso pequeño del patrón que hay en todas estas entradas: la persona cuyo
nombre sobrevive es aquella cuya versión resultó útil al campo más amplio, no la
que llegó primero.

### Artículos y libros que vale la pena leer

| Referencia | Por qué |
|---|---|
| [Metropolis & Ulam, *JASA* **44**, 335 (1949)](https://doi.org/10.1080/01621459.1949.10483310) | El artículo que dio nombre al método |
| [Eckhardt, *Los Alamos Science* **15**, 131 (1987)](https://library.lanl.gov/cgi-bin/getfile?15-13.pdf) | Ulam, von Neumann y el ENIAC, con la carta |
| **Lux & Koblinger**, *Monte Carlo Particle Transport Methods* (1991) | El zoo de estimadores. La captura implícita es el §5 |
| **Attix**, *Introduction to Radiological Physics and Radiation Dosimetry* | De dónde salen los coeficientes de atenuación |
| [Berger et al., NIST XCOM](https://www.nist.gov/pml/xcom-photon-cross-sections-database) | Las tablas reales de $\mu$, por elemento, por energía |
| **Chandrasekhar**, *Radiative Transfer* (1950) | La teoría analítica que este método existe para evitar |

---

## 3. Antes de calcular

La regla del libro: **escribe un número antes de leer la sección siguiente.** El
aprendizaje está en la distancia entre tu número y el real, y esa distancia no
existe si no te comprometiste.

> 1. Una lámina que deja pasar la mitad de los fotones. **¿Qué espesor tiene**,
>    medido en caminos libres medios? ¿Y qué espesor tiene una que deja pasar
>    una décima parte: el doble, o algo distinto?
> 2. Una radiografía sale granulada y quieres la mitad de ruido. **¿Cuántos
>    fotones más?** ¿El doble? ¿Cuatro veces?
> 3. La fuente no es un láser, es un cono. **¿Abrir el cono deja pasar más o
>    menos luz a través de la lámina?** ¿Y por qué eso no es obvio?

Respuestas en [§8](#8-análisis-de-escalas-todo-es-profundidad-óptica). Las tres
son de una línea, y la tercera es la única que la gente falla.

---

## 4. Por qué falla la respuesta ingenua

Aquí hay dos respuestas ingenuas y fallan en direcciones opuestas.

### 4.1 «Resuelve la ecuación de transporte»

La descripción correcta de este problema es una ecuación integrodiferencial para
la densidad de fotones en posición, dirección y energía. Escrita, es exacta y es
una función sobre un espacio de fases de seis dimensiones, y para cualquier cosa
que no sea una lámina en el vacío nadie sabe resolverla.

Esta es la situación en la que estaba Ulam con los neutrones, y la salida es
toda la materia: **la ecuación describe la media de un proceso aleatorio, así
que genera el proceso en lugar de resolver para la media.** Ninguna geometría es
más difícil que otra, porque un fotón no sabe qué forma tiene el objeto: solo
pregunta cuánto falta hasta la siguiente interacción.

Ese intercambio no es gratis, y lo que cuesta es $1/\sqrt{N}$
([§8.3](#83-el-precio-de-lanzar-dardos)).

### 4.2 «Todos los fotones recorren una distancia L»

Tentador, y equivocado de dos maneras distintas.

**No todos recorren $L$.** Un fotón con ángulo $\theta$ atraviesa
$L/\cos\theta$ de material, así que un cono de direcciones es una dispersión de
longitudes de camino. Por eso la respuesta a la pregunta 3 de la servilleta es
*menos*: todo fotón fuera del eje ve más material que uno axial, y ninguno ve
menos, así que abrir el cono solo puede atenuar más.

**Y no existe tal cosa como «la» distancia que recorre un fotón antes de
interaccionar.** Es una variable aleatoria, extraída de una exponencial, y eso
no es una comodidad de modelado: es lo que significa «coeficiente de
atenuación». Un fotón no tiene memoria de cuánto lleva recorrido, así que su
probabilidad de interaccionar en el milímetro siguiente es la misma esté donde
esté, y la única distribución con esa propiedad es la exponencial
([§6.2](#62-el-camino-libre-y-por-qué-es-exponencial)).

Sustituir esa distribución por su media da la respuesta equivocada, porque
$\langle e^{-\mu s}\rangle \neq e^{-\mu\langle s\rangle}$. Las exponenciales no
conmutan con el promediado, que es la misma razón por la que falló la respuesta
ingenua en [`tmm/`](../../tmm/docs/physics.md) y volverá a fallar en cualquier
sitio donde una función no lineal se encuentre con una distribución.

---

## 5. El modelo mínimo

Cada suposición de abajo compra una simplificación concreta, y todas fallan en
algún sitio real. Enumerarlas no es ceremonia: la lista *es* el dominio de
validez, y es lo que los tests nunca te pueden decir.

| Suposición | Qué compra | Dónde se rompe |
|---|---|---|
| **Sin dispersión** — absorber o pasar | Líneas rectas; la longitud del camino se conoce antes de que el fotón se mueva | La dispersión Compton domina a energías de diagnóstico |
| Monocromático | Un solo $\mu$ | Las fuentes reales tienen espectro; el endurecimiento del haz es de primer orden |
| Una lámina homogénea | $\mu$ es un número, no un campo | Cualquier objeto real |
| Infinita en $x,y$ | Sin bordes por los que fugarse | Objetos pequeños, colimadores, detectores finitos |
| Fuente puntual | Un cono, un origen | Las fuentes extensas emborronan la imagen |
| Los fotones son independientes | La respuesta es una media sobre historias de un fotón | Siempre cierto aquí, y falso para luz coherente |
| $\mu \ge 0$ | La transmisión es como mucho 1 | Medios con ganancia — **rechazados** por `check_medium` |
| Semiángulo del cono $\lt \pi/2$ | El camino en la lámina es finito | Rayos rasantes — **rechazados** por `check_cone` |
| Un detector perfecto | Las cuentas son la medida | Eficiencia, borrosidad, crosstalk, tiempo muerto |

Ese es el modelo. Fíjate en lo que **no** supone: no supone que la lámina sea
fina, ni el cono estrecho, ni la atenuación débil. Todo eso sale correcto. La
única suposición que hace trabajo de verdad es la primera, y hace tanto trabajo
que merece su propia fila en
[§11](#11-dónde-el-modelo-deja-de-ser-cierto).

---

## 6. Las ecuaciones

### 6.1 Emisión: el coseno es la variable plana

Un cono de semiángulo $\alpha$ subtiende un ángulo sólido, y el elemento de
ángulo sólido es

$$d\Omega = \sin\theta\thinspace d\theta\thinspace d\phi$$

así que la densidad de direcciones en $\theta$ lleva ese $\sin\theta$ y la
densidad en $\cos\theta$ es plana:

$$p(\theta)\thinspace d\theta = \sin\theta\thinspace d\theta
\quad\Longleftrightarrow\quad
p(\cos\theta)\thinspace d(\cos\theta) = d(\cos\theta)$$

Muestrea el coseno uniformemente en $[\cos\alpha, 1]$ y el peso sale
automático. Muestrea $\theta$ uniformemente en su lugar —que es lo obvio de
teclear— y amontonas fotones hacia el eje. La huella es el coseno medio:

$$\text{uniform in }\cos\theta:\ \langle\cos\theta\rangle
= \frac{1+\cos\alpha}{2},
\qquad
\text{uniform in }\theta:\ \langle\cos\theta\rangle = \frac{\sin\alpha}{\alpha}$$

que difieren un 5% en $\alpha = 45°$ y nunca en cero. Eso es un test, y es el
más afilado de [`test_physics.py`](../tests/test_physics.py), porque una
distribución angular equivocada produce una respuesta *plausible*.

### 6.2 El camino libre, y por qué es exponencial

Un fotón en un medio uniforme no tiene memoria. Sea lo que sea lo que ya haya
sobrevivido, su probabilidad de interaccionar en el siguiente $ds$ es
$\mu\thinspace ds$: esa es la definición del coeficiente de atenuación.
Escribiendo $S(s)$ para la probabilidad de sobrevivir una distancia $s$,

$$S(s + ds) = S(s)\left(1 - \mu\thinspace ds\right)
\quad\Longrightarrow\quad
\frac{dS}{ds} = -\mu S
\quad\Longrightarrow\quad
S(s) = e^{-\mu s}$$

La ausencia de memoria *es* la exponencial; son el mismo enunciado. Así que la
distancia hasta la siguiente interacción tiene densidad $p(s) = \mu e^{-\mu s}$,
y para extraer de ella, invierte la probabilidad de supervivencia —que es
uniforme en $(0,1]$:

$$\boxed{\enspace s = -\frac{\ln U}{\mu}\enspace}$$

Esto es [`sample_free_path()`](../physics.py), y es todo el muestreo por
transformada inversa: **si puedes invertir la distribución acumulada, puedes
muestrearla con un único número uniforme.** Eso funciona aquí y falla en
general, y ese fallo es la razón de que exista
[`sampling/`](../../sampling/README.md).

> **Una línea de cuidado.** `rng.random()` devuelve $[0, 1)$, y $\ln 0$ es
> $-\infty$. Extraer $1 - U$ en su lugar sitúa la muestra en $(0, 1]$, lo que
> hace la singularidad **inalcanzable** en vez de meramente improbable. La
> versión de 2024 usaba `log(rand())` y habría producido un camino infinito
> aproximadamente una vez cada $10^{16}$ extracciones: nunca en una ejecución de
> test, y tarde o temprano en producción.

### 6.3 Geometría: un factor, y es el único

Un fotón que cruza una lámina de espesor $L$ con ángulo $\theta$ recorre

$$\ell = \frac{L}{\cos\theta}$$

por ella. Esa es toda la dependencia angular del problema. La versión de 2024 lo
calculaba como la distancia tridimensional entre los puntos de entrada y de
salida, que es el mismo número alcanzado por el camino largo.

### 6.4 Beer–Lambert

Junta las tres. Un fotón se transmite si su camino libre supera su camino en la
lámina, y la probabilidad de eso es la probabilidad de supervivencia evaluada
ahí:

$$\boxed{\enspace T(\theta)
= \mathbb{P}\left(s > \ell\right)
= \exp\negthinspace\left(-\frac{\mu L}{\cos\theta}\right)\enspace}$$

No es una aproximación, no es un ajuste: la función de supervivencia del §6.2
evaluada en la geometría del §6.3. Promediada sobre el cono queda

$$T = \frac{1}{1-\cos\alpha}
\int_{\cos\alpha}^{1} e^{-\mu L / c}\thinspace dc$$

que es una integral exponencial sin forma elemental. Se calcula por cuadratura en
[`cone_transmittance()`](../physics.py) —sobre una malla fija, con una precisión
muy por encima de lo que alcanza cualquier ejecución de Monte Carlo, que es lo
que la convierte en una **referencia** y no en una segunda opinión.

---

## 7. Dos estimadores, una integral

Todo lo anterior es la física. Lo que sigue es una elección, y es la elección de
la que trata esta entrada.

### 7.1 Analógico: simular lo que hace un fotón

Extrae un camino libre. Compáralo con el camino en la lámina. Cuenta los
supervivientes.

Cada número aleatorio representa algo que ocurre físicamente, y la respuesta es
un recuento. Es la traducción literal del proceso, es lo que hacía la versión de
2024, y es lo que todo el mundo escribe primero.

**Su coste es que cada fotón informa de un bit.** Un fotón que fue absorbido solo
te dice que fue absorbido. La estimación carga con todo el ruido binomial de una
moneda al aire, varianza $T(1-T)$, por estrecho que sea el haz y por bien que
entiendas la geometría.

### 7.2 Ponderado: integrar el dado en vez de lanzarlo

Mira para qué *sirve* el camino libre. Se extrae, se compara una vez y se tira:
solo responde a una pregunta, y esa pregunta tiene respuesta conocida en
esperanza:

$$\mathbb{P}\left(s > \ell\right) = e^{-\mu\ell}$$

Así que no lo muestrees. Cada fotón aporta su probabilidad de supervivencia
exacta, y el estimador es insesgado porque la media del indicador *era* esa
probabilidad desde el principio.

Esto es la **captura implícita**, y es lo que hace todo código de transporte
serio. Lo que compra es la eliminación de una fuente entera de aleatoriedad: la
única varianza que queda es la dispersión de longitudes de camino a lo largo del
cono.

$$\mathrm{Var}_{\text{analog}} = T(1-T),
\qquad
\mathrm{Var}_{\text{weighted}} = \mathrm{Var}_c\negthinspace\left(e^{-\mu L/c}\right)$$

Cierra el cono y la segunda se va a cero con él. La primera no se mueve nada.

### 7.3 Lo que el contrato puede y no puede exigir

[`tests/test_methods.py`](../tests/test_methods.py) está parametrizado sobre
todos los estimadores registrados y afirma lo que ambos deben hacer: aterrizar en
Beer–Lambert, devolver probabilidades, encoger como $1/\sqrt{N}$, ser
reproducibles.

No dice nada sobre la varianza, porque ahí es donde difieren en ocho órdenes de
magnitud y una afirmación compartida sería falsa. La misma decisión de diseño que
[`hopfield/`](../../hopfield/README.md) al negarse a exigir descenso de energía a
su esquema síncrono.

---

## 8. Análisis de escalas: todo es profundidad óptica

### 8.1 Hay una variable, y es adimensional

$\mu$ y $L$ nunca aparecen por separado. Aparecen como su producto

$$\tau = \mu L$$

la **profundidad óptica**, y todo resultado de este documento es función solo de
$\tau$. Un centímetro de algo que absorbe el doble es la misma lámina que dos
centímetros del original, exactamente, y un test lo fija.

Eso vale más de lo que suena. Significa que hay exactamente **una** escala de
longitud en el problema, el camino libre medio $1/\mu$, y que medir cualquier
cosa en esas unidades saca el material de la pregunta.

### 8.2 Capa hemirreductora y capa decirreductora

*Respuesta a la pregunta 1.* Impón $e^{-\tau} = 1/2$:

$$\tau_{1/2} = \ln 2 = 0.693, \qquad \tau_{1/10} = \ln 10 = 2.303$$

Así que la capa decirreductora es **3.3 veces** la capa hemirreductora, ni diez
veces ni el doble. Cada factor de dos cuesta el mismo espesor fijo, que es todo
el contenido de una exponencial y la razón de que los blindajes se citen así.

### 8.3 El precio de lanzar dardos

*Respuesta a la pregunta 2.* Una estimación de Monte Carlo tiene error
$\sigma/\sqrt{N}$. Reducir el ruido a la mitad necesita **cuatro veces** los
fotones, y un dígito decimal más necesita cien veces.

Ese es el coste fijo de la salida del
[§4.1](#41-resuelve-la-ecuación-de-transporte), y es por lo que la elección de
estimador importa tanto: no puede cambiar el $1/\sqrt{N}$, pero sí puede cambiar
el $\sigma$ que lo acompaña, y el
[§10.2](#102-la-misma-respuesta-con-una-fracción-de-los-fotones) lo cambia en
ocho órdenes de magnitud.

En una radiografía el tipo de cambio no es abstracto. El ruido es la estadística
de conteo de los fotones que el paciente absorbió, así que reducir a la mitad el
grano de una imagen significa cuadruplicar la dosis.

### 8.4 Abrir el cono

*Respuesta a la pregunta 3.* **Pasa menos.** Todo fotón fuera del eje atraviesa
$L/\cos\theta \gt L$ de material y ninguno atraviesa menos, así que ensanchar el
cono solo puede atenuar más.

La razón de que la gente dude es que están pensando en el detector, donde abrir
el cono reparte los mismos fotones sobre más área y cada píxel recibe menos. Esa
es otra pregunta con la misma respuesta, y confundirlas es como acabas dividiendo
dos veces por el ángulo sólido.

---

## 9. Formas cerradas que vale la pena memorizar

Estas son con las que compruebas el código. Contrastar dos estimadores demuestra
que coinciden; contrastar con Beer–Lambert demuestra que aciertan. Cada fila de
aquí es un test en [`../tests/`](../tests/).

| Situación | Resultado |
|---|---|
| Supervivencia a lo largo de una distancia | $S(s) = e^{-\mu s}$ |
| Muestra del camino libre | $s = -\ln U/\mu$ |
| Camino libre medio | $1/\mu$ |
| Camino en la lámina con ángulo $\theta$ | $L/\cos\theta$ |
| Transmisión, una dirección | $T = e^{-\mu L/\cos\theta}$ |
| Transmisión, sobre un cono | $\frac{1}{1-\cos\alpha}\int_{\cos\alpha}^{1}e^{-\mu L/c}\thinspace dc$ |
| Emisión, coseno medio | $(1+\cos\alpha)/2$ |
| Capa hemirreductora | $\tau = \ln 2 = 0.693$ |
| Capa decirreductora | $\tau = \ln 10 = 2.303$, es decir 3.3 capas hemirreductoras |
| Varianza analógica | $T(1-T)$, sea cual sea la geometría |
| Varianza ponderada | la dispersión de $e^{-\mu L/c}$ sobre el cono, $\sim\alpha^4$ |
| Error de Monte Carlo | $\sigma/\sqrt{N}$, para cualquier estimador |
| Dos láminas con igual $\mu L$ | idénticas, exactamente |

**Una advertencia sobre la última fila.** «Los dos estimadores coinciden» es el
test al que la gente recurre y es el más débil de aquí: coinciden porque están
estimando la misma integral, y coincidirían igual de contentos sobre una integral
equivocada si la física compartida estuviera mal. La forma cerrada está por
encima, y la forma cerrada se comprobó primero.

---

## 10. Lo que mostró la simulación

La regla del libro: **predice antes de ejecutar.** Los tres experimentos son
predicciones con un número pegado, no gráficas para admirar.

### 10.1 Beer–Lambert, recuperada

Predicción: una recta en eje logarítmico para un haz colimado, con pendiente
$-\mu$, que se dobla a medida que el cono se abre. A ninguno de los dos
estimadores se le dice la ley.

![Fracción transmitida frente al espesor de la lámina en eje logarítmico, para un
haz colimado y un cono de 45 grados, con la forma cerrada trazada a través de
puntos medidos con barras de error.](figures/beer_lambert.png)

**Qué concluir:** los dos estimadores aterrizan en una ley que no aparece en
ninguno de los dos. El analógico muestrea caminos libres y cuenta; el ponderado
integra una probabilidad de supervivencia; la exponencial es una consecuencia.

```
--- 45 degree cone ---
   thickness    analytic                 analog               weighted
        1.00    0.308413      0.306910+-0.00146      0.308490+-0.00011
        3.00    0.030532      0.031040+-0.00055      0.030548+-0.00003
        5.00    0.003171      0.003350+-0.00018      0.003169+-0.00001
```

**Una nota metodológica que vale más que la gráfica.** La primera versión usaba
una sola semilla para cada punto del barrido. Eso reutiliza los mismos caminos
libres, tira de todos los puntos en la misma dirección y convierte una dispersión
honesta de $1\sigma$ en lo que se lee como un sesgo sistemático: la columna
analógica quedaba por encima de la teoría a *todos* los espesores. Las barras de
error eran correctas en todo momento; solo el ojo se dejó engañar. Ahora la
semilla varía por punto.

### 10.2 La misma respuesta con una fracción de los fotones

Predicción: la brecha entre los estimadores crece sin límite a medida que el cono
se estrecha, y la varianza analógica no se mueve nada.

![Varianza por fotón frente al semiángulo del cono, log-log, para los dos
estimadores, con una línea de referencia de pendiente cuatro.](figures/variance.png)

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

**Qué concluir:** la varianza analógica es $T(1-T)$ hasta cuatro decimales en
todos los ángulos de cono. Es una moneda al aire, y **nada de lo que sabe la
geometría puede alcanzarla**: el estimador descarta esa información por
construcción. La varianza ponderada cae aproximadamente como $\alpha^4$, porque
la única aleatoriedad que queda es la dispersión de longitudes de camino, y esa
dispersión va como $1-\cos\alpha \sim \alpha^2$.

Un cono de cinco grados necesita **dos** fotones ponderados para igualar
cuatrocientos mil analógicos.

### 10.3 Una imagen de la diferencia

El mismo argumento deja de ser un número.

![Tres imágenes de detector de una esfera con dos inclusiones más densas:
analógica, ponderada y la transmisión exacta, con el mismo presupuesto de
fotones.](figures/radiograph.png)

```
   estimator   RMS error vs exact   worst pixel
      analog             0.027925      0.170133
    weighted             0.000000      0.000000
```

**Qué concluir:** presupuesto de fotones idéntico, 120 por píxel, y una imagen
sale granulada mientras la otra es exacta. El grano no es un artefacto de
renderizado: es el ruido binomial del §7.1, un bit por fotón, hecho visible.

Y aquí es donde el §8.3 deja de ser abstracto. En una radiografía real ese ruido
es la estadística de conteo de los fotones que el paciente absorbió, así que
reducirlo a la mitad significa cuadruplicar la dosis. El estimador ponderado
consigue la imagen limpia gratis porque es una *simulación*; una máquina real no
tiene esa opción.

---

## 11. Dónde el modelo deja de ser cierto

La sección que más importa, y la que suele faltar.

### 11.1 Dispersión — la suposición que falla primero

Todo aquí tiene fotones viajando en línea recta hasta que son absorbidos. Los
fotones reales a energías de diagnóstico sobre todo se **dispersan**: la
dispersión Compton les cambia la dirección y les quita algo de energía, y siguen
adelante.

Eso rompe la entrada en dos puntos distintos.

**La física.** Un fotón dispersado sigue llegando al detector, solo que desde la
dirección equivocada, sin llevar información sobre la línea por la que parecía
venir. En radiografía real los fotones dispersados son una niebla tendida sobre
la imagen, y quitarlos —con rejillas, huecos de aire, colimación— es buena parte
de para lo que sirve el hardware.

**Y el estimador.** El estimador ponderado funciona porque el camino a través del
medio se conoce *antes de que el fotón se mueva*. Añade dispersión y el camino se
convierte en un paseo aleatorio cuya longitud no se conoce de antemano, así que
la integración analítica del §7.2 no tiene nada que integrar. La captura
implícita sigue existiendo en los códigos con dispersión, pero hay que ganársela
otra vez en cada colisión en vez de recibirla una sola vez.

Ese es el resumen honesto del alcance de la entrada: es el caso en el que el
atajo está disponible.

### 11.2 El resto de la lista

| Límite | Qué ocurre en realidad | Esta entrada |
|---|---|---|
| Dispersión | Las líneas rectas son falsas; el atajo ponderado desaparece | no modelada |
| Espectro ancho | Los fotones blandos se absorben primero, así que $\mu$ baja con la profundidad; la transmisión no es exponencial en $L$ | no modelado |
| Láminas muy gruesas | El estimador analógico devuelve casi todo ceros y su error *relativo* explota | medido |
| Láminas muy gruesas, ponderado | Los pesos caen a cero por subdesbordamiento mucho antes de que lo hiciera el recuento analógico | sin protección |
| Cono acercándose a $\pi/2$ | El camino en la lámina diverge | `ValueError` |
| Medios con ganancia, $\mu \lt 0$ | Transmisión por encima de 1 | `ValueError` |
| Un estimador de varianza cero | «Dentro de 3σ» pierde el sentido: 0.2 ulp leídos como 447σ | acotado por abajo |
| Objetos inhomogéneos | $\mu$ es un campo, no un número | solo en la radiografía, a mano |
| Física del detector | Eficiencia, borrosidad, tiempo muerto, crosstalk | conteo perfecto |

La fila de σ merece su propia frase porque mordió durante el desarrollo. El
estimador ponderado sobre un haz colimado da a cada fotón la *misma*
contribución, así que su error estándar es ruido de coma flotante y no una
dispersión, y dividir por él convirtió una diferencia de 0.2 ulp en **447 errores
estándar**. **Cuanto mejor es el estimador, más frágil se vuelve una comprobación
de «dentro de tres sigma»**, que no es una frase que esperara escribir.

---

## 12. Lo esencial

- **La imagen está hecha de lo que sobrevivió.** Nada se enfoca, nada se
  refleja; cada región oscura es un lugar por donde más luz no logró pasar.
- **La ausencia de memoria es la exponencial.** La probabilidad de que un fotón
  interaccione en el milímetro siguiente no depende de cuánto lleva recorrido, y
  solo una distribución tiene esa propiedad.
- **Invertir la CDF la muestrea en una línea** —y eso funciona aquí y casi en
  ningún otro sitio, que es la razón de que exista MCMC.
- **Hay una variable y es $\mu L$.** Una escala de longitud, el camino libre
  medio, y todo lo demás es una razón respecto a ella.
- **Una capa decirreductora son 3.3 capas hemirreductoras**, ni diez ni dos.
- **Monte Carlo escapa de la ecuación de seis dimensiones generando la media en
  lugar de resolver para ella**, y el cargo fijo es $1/\sqrt{N}$.
- **Un estimador no puede cambiar el $1/\sqrt{N}$ y sí puede cambiar el
  $\sigma$** —aquí en ocho órdenes de magnitud, negándose a muestrear algo cuya
  esperanza ya conoce.
- **El estimador analógico descarta lo que sabe la geometría.** Un bit por
  fotón, varianza $T(1-T)$, no mejorable a base de entender.
- **El ruido de imagen es dosis.** Reduce el grano a la mitad, cuadruplica la
  exposición.
- **Un resultado de Monte Carlo sin barra de error no es una medida**, y una
  simulación que nunca se contrasta con una forma cerrada solo se contrasta con
  tus expectativas.

---

## 13. Preguntas abiertas

Cosas que este documento deliberadamente no responde, más o menos en orden de
cuánto enseñarían:

- **¿Qué cuesta la dispersión?** Elimina el atajo del estimador ponderado y
  convierte el camino en un paseo aleatorio. Ese paseo son las mismas matemáticas
  que la dinámica de Langevin de [`sampling/`](../../sampling/README.md) y, en el
  límite continuo, la ecuación de difusión. Es la mayor brecha que hay entre esta
  entrada y cualquier cosa utilizable.
- **¿Cómo ponderas sin conocer el camino?** La captura implícita sobrevive a la
  dispersión, pero hay que reganársela en cada colisión, y la contabilidad de la
  varianza es lo que hace difíciles los códigos de transporte reales.
- **¿Cuál es el estimador óptimo?** El ponderado gana al analógico aquí por
  negarse a muestrear una variable. Detrás de eso hay toda una familia —muestreo
  por importancia, splitting, ruleta rusa— y un enunciado con principios de
  cuándo compensa cada uno.
- **¿De dónde sale $\mu$?** Absorción fotoeléctrica, Compton, producción de
  pares, cada una con su propia dependencia de la energía y del número atómico.
  Esta entrada toma $\mu$ como dado, y todo lo interesante de los materiales está
  en cómo no lo es.
- **¿Cómo se invierte esto?** Medir proyecciones y recuperar el objeto es
  tomografía, y que sea posible siquiera es un teorema del siglo XIX sobre la
  transformada de Radon.

---

## 14. Referencias

**Monte Carlo, y de dónde vino**

- **Metropolis, N. & Ulam, S.** *The Monte Carlo method.* Journal of the
  American Statistical Association **44**, 335–341 (1949).
  [enlace](https://doi.org/10.1080/01621459.1949.10483310)
- **Eckhardt, R.** *Stan Ulam, John von Neumann, and the Monte Carlo method.*
  Los Alamos Science **15**, 131–143 (1987).
  [enlace](https://library.lanl.gov/cgi-bin/getfile?15-13.pdf) — incluye la
  carta de 1947 de von Neumann a Richtmyer.
- **Ulam, S.** *Adventures of a Mathematician* (1976). El solitario, en sus
  propias palabras.

**Transporte y estimadores**

- **Lux, I. & Koblinger, L.** *Monte Carlo Particle Transport Methods: Neutron
  and Photon Calculations* (1991). Captura implícita, splitting, ruleta rusa: la
  familia de reducción de varianza de la que esta entrada toma un miembro.
- **Chandrasekhar, S.** *Radiative Transfer* (1950). La teoría analítica, y una
  buena mirada a lo que estás evitando.
- **Spanier, J. & Gelbard, E. M.** *Monte Carlo Principles and Neutron
  Transport Problems* (1969).

**La física de $\mu$**

- **Attix, F. H.** *Introduction to Radiological Physics and Radiation
  Dosimetry* (1986).
- **Berger, M. J. et al.** *XCOM: Photon Cross Sections Database*, NIST.
  [enlace](https://www.nist.gov/pml/xcom-photon-cross-sections-database)
- **Bouguer, P.** *Essai d'optique sur la gradation de la lumière* (1729). La
  exponencial, primero.

---

*Código: [`../physics.py`](../physics.py) y [`../methods/`](../methods/) ·
Entrada: [`../README.md`](../README.md) · Arquitectura de todo el repositorio:
[`docs/architecture.md`](../../docs/architecture.md)*
