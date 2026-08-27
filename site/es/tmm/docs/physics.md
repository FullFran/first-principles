<!-- translated-from: 9f0d83b7a3f0 -->

# Luz a través de una pila de películas delgadas

> La física detrás de [`tmm/`](../README.md), derivada del problema y no de la
> fórmula. Lee esto si quieres saber *por qué* las ecuaciones de
> `tmm/physics.py` son esas y no otras.

Este documento sigue un ciclo, y el ciclo es lo importante:

```
phenomenon → question → order of magnitude → assumptions → minimal model
   → equations → scale analysis → closed forms → simulation → validation
   → limits of the model → next question
```

El medio es lo que enseña una carrera. Los dos extremos — plantear la pregunta y
saber dónde se acaba el modelo — son lo que de verdad separa a quien resuelve
problemas nuevos de quien aplica fórmulas. Así que aquí el espacio es para los
dos extremos.

**Contenidos**

1. [El fenómeno](#1-el-fenómeno)
2. [Para qué sirven las multicapas](#2-para-qué-sirven-las-multicapas)
3. [Antes de calcular](#3-antes-de-calcular)
4. [Por qué falla la respuesta ingenua](#4-por-qué-falla-la-respuesta-ingenua)
5. [El modelo mínimo](#5-el-modelo-mínimo)
6. [Las ecuaciones](#6-las-ecuaciones)
7. [Componer la pila: tres formas, una física](#7-componer-la-pila-tres-formas-una-física)
8. [Análisis de escalas: leer la respuesta en la fase](#8-análisis-de-escalas-leer-la-respuesta-en-la-fase)
9. [Formas cerradas que vale la pena memorizar](#9-formas-cerradas-que-vale-la-pena-memorizar)
10. [Lo que mostró la simulación](#10-lo-que-mostró-la-simulación)
11. [Dónde el modelo deja de ser cierto](#11-dónde-el-modelo-deja-de-ser-cierto)
12. [Lo esencial](#12-lo-esencial)
13. [Preguntas abiertas](#13-preguntas-abiertas)
14. [Referencias](#14-referencias)

---

## 1. El fenómeno

Una pompa de jabón es líquido incoloro y tiene un color violento. Un charco con
una gota de aceite encima tiene color. El caparazón de un escarabajo tiene color
y no lleva pigmento alguno. Tus gafas tienen un brillo morado; el elemento
frontal de un objetivo de cámara lo tiene verde. Un espejo láser parece un trozo
de vidrio y devuelve el 99.999% de lo que le llega.

Todos son el mismo objeto: **unas pocas capas de material transparente, cada una
de una fracción de longitud de onda de espesor, apiladas una sobre otra.**

En ninguno hay absorción haciendo el trabajo. El color no es un tinte. Es
interferencia — el mismo fenómeno que dos altavoces cancelándose en una
habitación, funcionando a $5\times10^{14}$ Hz.

> **La pregunta.**
> Una pila de $N$ capas paralelas, cada una con índice de refracción $n_k$ y
> espesor $d_k$. Una onda plana llega desde fuera con ángulo $\theta_0$ y
> longitud de onda en vacío $\lambda$.
> **¿Qué fracción de la potencia incidente vuelve, y qué fracción atraviesa?**

Llámalas $R$ y $T$. Ese es todo el problema directo, y es lo que calcula
`tmm/`.

Dale la vuelta — elige los $n_k$ y $d_k$ para que $R(\lambda,\theta)$ sea la
curva que quieres — y tienes el problema inverso, que es una industria entera.
El problema directo tiene que ser exacto y barato primero, porque el inverso lo
llama unos cuantos millones de veces.

---

## 2. Para qué sirven las multicapas

Vale la pena repasarlo antes de cualquier ecuación, porque las aplicaciones te
dicen qué régimen de las ecuaciones importa.

### 2.1 Eliminar un reflejo (recubrimientos antirreflejantes)

El vidrio desnudo refleja alrededor del 4% por superficie. Suena despreciable
hasta que cuentas superficies: un objetivo de cámara de seis elementos tiene
doce, y $0.9574^{12} = 0.59$ — **se pierde el 41% de la luz**, y la mayor parte
no se pierde: va rebotando dentro del tubo del objetivo produciendo destellos
parásitos y lavando el contraste.

El silicio desnudo es peor. Con $n \approx 3.9$ la cara frontal de una célula
solar refleja $\left(\frac{1-3.9}{1+3.9}\right)^2 = 0.35$ antes de que el
semiconductor tenga oportunidad — el 35% de la luz. Una sola capa de cuarto de
onda de nitruro de silicio lo baja al 0.02% en la longitud de onda de diseño.
Esa única capa vale más que casi toda la optimización de proceso que viene
después.

La historia es una buena lección sobre fijarse en las cosas, y vale la pena
contarla bien. Los niveles de verificación siguen el convenio del libro: **A**
es documentado, idealmente desde una fuente primaria; **B** es una
reconstrucción; **C** es una historia que se cuenta en todas partes y que no
pude rastrear.

::: **El vidrio que funcionaba mejor una vez estropeado** · *Verificación: A.*

En 1886 Rayleigh se fijó en algo que debería haber sido un error: el vidrio
**deslustrado** transmitía *más* luz que el vidrio fresco. Las lentes viejas,
guardadas en habitaciones húmedas, habían criado una película química — y eran
más luminosas que las que se habían cuidado.

Eso es justo lo contrario de toda intuición sobre óptica. La suciedad debería
dispersar y absorber. La razón de que no lo haga es
[§4](#4-por-qué-falla-la-respuesta-ingenua): la película tiene un espesor de una
fracción de longitud de onda, así que sus dos superficies reflejan *en oposición
de fase* y se cancelan. No hay nada absorbiéndose ni nada limpiándose; dos
reflejos se están destruyendo el uno al otro.

Taylor patentó el deslustrado químico deliberado en 1904 y nunca lo hizo
reproducible — no se controlan cien nanómetros con un baño químico. Smakula, en
Zeiss, patentó los recubrimientos evaporados en 1935, y la industria moderna de
recubrimientos empieza ahí, porque la deposición en vacío es el primer proceso
capaz de acertar un espesor de unos pocos cientos de átomos a propósito
([§8.1](#81-el-cuarto-de-onda-delta--pi2)).

::: **Y fue un secreto militar** · *Verificación: B — muy repetido, y no he
visto la propia orden de clasificación.*

La patente de Zeiss de 1935 fue, según se cuenta, clasificada por Alemania, por
una razón que suena rara hasta que cuentas superficies. Una lente recubierta
pierde el 1% por superficie en vez del 4%, y un telémetro o un periscopio tiene
una docena: la diferencia es entre que llegue el 59% de la luz y que llegue el
89% ([§2.1](#21-eliminar-un-reflejo-recubrimientos-antirreflejantes)). Al
anochecer, esa es la diferencia entre ver un barco y no verlo.

El recubrimiento antirreflejante es un caso genuino de física de interferencias
como arma, y de que las mismas ecuaciones merezcan clasificarse en una década e
imprimirse en un libro de texto de grado en la siguiente.

### 2.2 Conseguir un reflejo perfecto (espejos de Bragg / DBR)

Apila pares de cuarto de onda de índice alto y bajo y cada reflexión parcial
vuelve en fase. La reflectancia se acerca a 1 exponencialmente en el número de
periodos, sin metal y por tanto sin pérdida por absorción.

- **Láseres de semiconductor.** Un VCSEL tiene una ganancia de una fracción de
  un por ciento por pasada, así que los espejos de su cavidad deben superar el
  99.9%. Nada metálico hace eso. 20–40 periodos de AlAs/GaAs sí.
- **Litografía EUV.** A 13.5 nm todo material absorbe y nada refracta de forma
  útil — no hay lentes. Todo el tren óptico son espejos multicapa de Mo/Si, ~50
  bicapas, ~70% de reflectancia cada uno. Cada espejo de la cadena te cuesta un
  30%, y por eso hay los menos posibles físicamente.
- **Detectores de ondas gravitacionales.** Las masas de prueba de LIGO son
  recubrimientos multicapa donde el presupuesto de *pérdidas* es de partes por
  millón, y donde el ruido térmico del recubrimiento es una fuente de ruido
  limitante para el instrumento.

### 2.3 Elegir qué colores pasan (filtros)

Divisores de haz dicroicos, filtros notch, cubos de filtros para microscopía de
fluorescencia, recubrimientos de baja emisividad para ventanas, espejos de
calor, filtros de línea láser. La misma matemática, apuntada a una curva
objetivo en vez de a un solo número.

### 2.4 Color sin pigmento (color estructural)

Alas de mariposa Morpho, élitros de escarabajo, plumas de pavo real, escamas de
pez, el interior de una concha. La biología descubrió las pilas dieléctricas
mucho antes que Zeiss. La firma es la dependencia con el ángulo: un pigmento no
cambia de tono cuando lo inclinas y una multicapa siempre lo hace, porque
$\delta \propto \cos\theta$.

### 2.5 Medir cosas (elipsometría)

Ejecuta el modelo *hacia atrás* contra unos $(\Psi, \Delta)$ medidos y recuperas
el espesor y el índice de una película con precisión sub-nanométrica. La
elipsometría es una de las técnicas de metrología más usadas en las fábricas de
semiconductores, y el modelo directo que lleva dentro es exactamente el de este
documento.

### Artículos que vale la pena leer

| Referencia | Por qué |
|---|---|
| [Abelès, *Ann. Phys.* **12**, 596 (1950)](https://www.annphys.org/articles/anphys/abs/1950/05/anphys19501205p596/anphys19501205p596.html) | La formulación de matriz característica $2\times2$. El origen de «TMM» |
| [Rouard, *Ann. Phys.* **11**, 291 (1937)](https://www.annphys.org/articles/anphys/abs/1937/07/anphys19371107p291/anphys19371107p291.html) | La recursión, trece años antes. La misma física, distinta contabilidad |
| [Yeh, Yariv & Hong, *JOSA* **67**, 423 (1977)](https://opg.optica.org/abstract.cfm?URI=josa-67-4-423) | Teoría de Bloch de pilas periódicas. De donde sale la fórmula de la banda de rechazo |
| [Li, *JOSA A* **13**, 1024 (1996)](https://opg.optica.org/josaa/abstract.cfm?uri=josaa-13-5-1024) | Por qué el producto de matrices es numéricamente inestable y la recursión no |
| [Katsidis & Siapkas, *Appl. Opt.* **41**, 3978 (2002)](https://opg.optica.org/ao/abstract.cfm?uri=ao-41-19-3978) | Capas coherentes, parcialmente coherentes e incoherentes en un mismo marco |
| [Byrnes, *Multilayer optical calculations*, arXiv:1603.02720](https://arxiv.org/abs/1603.02720) | La redacción moderna y cuidadosa: cortes de rama, ambientes absorbentes, por qué $T \neq \lvert t\rvert^2$ |
| [Fink et al., *Science* **282**, 1679 (1998)](https://www.science.org/doi/10.1126/science.282.5394.1679) | Una pila 1D que refleja a *todo* ángulo — el espejo omnidireccional |
| [Tikhonravov, Trubetskov & DeBell, *Appl. Opt.* **35**, 5493 (1996)](https://opg.optica.org/ao/abstract.cfm?uri=ao-35-28-5493) | Optimización por agujas: el problema inverso hecho bien |

Libros: Born & Wolf §1.6 para la derivación, *Thin-Film Optical Filters* de
Macleod para la práctica de diseño, *Optical Waves in Layered Media* de Yeh para
la teoría de medios periódicos.

---

## 3. Antes de calcular

La regla del libro: **escribe un número antes de leer la sección siguiente.** El
aprendizaje está en la distancia entre tu número y el real, y esa distancia no
existe si no te comprometiste.

> 1. Una capa antirreflejante de cuarto de onda para luz verde sobre vidrio.
>    **¿Qué espesor, en nanómetros?** ¿Cuántos átomos son?
> 2. Necesitas un espejo con $R \gt 0.999$ construido con capas de $n_H = 2.3$ y
>    $n_L = 1.45$. **¿Cuántos pares?** ¿Diez? ¿Cincuenta? ¿Quinientos?
> 3. Un espejo de Bragg diseñado para 550 nm refleja una banda, no una línea.
>    **¿Qué ancho tiene esa banda?** ¿Y apilar más periodos la ensancha?

Respuestas en [§8](#8-análisis-de-escalas-leer-la-respuesta-en-la-fase) y
[§9](#9-formas-cerradas-que-vale-la-pena-memorizar). Dos de las tres son una
línea de aritmética. Si puedes hacerlas en una servilleta no necesitas que el
código se compruebe a sí mismo — ya sabes la respuesta con un margen de unos
pocos por ciento, y el trabajo del código pasa a ser confirmar una predicción en
vez de producir una sorpresa.

---

## 4. Por qué falla la respuesta ingenua

El primer modelo tentador: la luz llega a la interfaz 1, una fracción $R_1$
rebota; el resto llega a la interfaz 2, una fracción rebota; súmalas.

$$R_{\text{naive}} \stackrel{?}{=} R_{01} + T_{01}R_{12}T_{10} + \dots$$

Esto es incorrecto, y lo es de una forma que vale la pena entender porque el
mismo error aparece por todas partes en la física de ondas.

**Las potencias no se suman. Se suman las amplitudes.** Las ondas parciales que
salen de vuelta de la pila son coherentes entre sí — tienen una fase relativa
definida, fijada por el camino óptico extra que recorrió cada una. Lo que llega
al detector es

$$r_{\text{total}} = \sum_m r_m e^{i\phi_m},
\qquad R = \left|\sum_m r_m e^{i\phi_m}\right|^2
\neq \sum_m |r_m|^2$$

Los términos cruzados *son* el fenómeno. Quítalos y la pompa de jabón es gris.

Dos consecuencias que lo convierten en algo más que un tecnicismo:

- **$R$ puede ser mayor que la suma de las partes** (espejo de Bragg: 20
  interfaces que reflejan un 8% cada una dan un 99.99%, no 20×8%), **o menor**
  (recubrimiento AR: dos interfaces que reflejan ~2% cada una dan 0.0%).
- **Un modelo que suma potencias no puede producir ninguna de las dos.** No es
  una aproximación peor; es una situación física distinta — la incoherente, que
  es lo que obtienes de verdad si la capa es más gruesa que la longitud de
  coherencia de la fuente ([§11](#11-dónde-el-modelo-deja-de-ser-cierto)).

![Izquierda: reflectancia de una capa de cuarto de onda sobre vidrio frente a la
longitud de onda. El cálculo coherente cae muy por debajo tanto del resultado
que suma potencias como del vidrio desnudo; el resultado que suma potencias es
una línea horizontal. Derecha: reflectancia de una pila de Bragg frente al
número de periodos, coherente frente a incoherente.](figures/coherence.png)

**Qué concluir:** el modelo que suma potencias no es una versión más burda de la
misma respuesta. Fíjate en que el *espesor de la capa no puede aparecer en
ninguna parte de él* — una pila incoherente no tiene forma de saber que una capa
es un cuarto de onda, así que su respuesta es la misma a toda longitud de onda,
y a 16 periodos llega a 0.65 donde la pila real llega a 0.999999. Los términos
cruzados no son una corrección. Son el fenómeno.

Así que el problema es: sumar un número infinito de ondas parciales coherentes.
Suena mal. Se colapsa en dos líneas de álgebra, y ese colapso es la parte bonita
de la derivación.

---

## 5. El modelo mínimo

Cada supuesto de abajo compra una simplificación concreta, y todos ellos fallan
en algún sitio real. Listarlos no es ceremonia — la lista *es* el dominio de
validez, y es lo que los tests nunca te pueden decir.

| Supuesto | Qué compra | Dónde se rompe |
|---|---|---|
| Onda plana monocromática, $e^{-i\omega t}$ | Una $\lambda$, un $\theta$, sin paquetes de onda | Haces enfocados, pulsos ultracortos, desplazamiento de Goos–Hänchen |
| Capas infinitas y planas en $x,y$ | Invariancia traslacional ⇒ $k_x$ conservado ⇒ Snell | Rugosidad, redes de difracción, aperturas finitas, dispersión |
| $n_k$ homogéneo a trozos e isótropo | Un índice escalar por capa | Birrefringencia, índice gradual, cristales líquidos |
| No magnético, $\mu = 1$ | La impedancia es $1/n$, no $\sqrt{\mu/\varepsilon}$ | Metamateriales, medios magnéticos, RF |
| Respuesta lineal y local | Superposición; $n$ independiente de la intensidad | Óptica no lineal, dispersión espacial |
| Medios pasivos, $\mathrm{Im} n \ge 0$ | La rama que decae hacia delante está bien definida | Medios con ganancia, láseres — **rechazados** por `check_domain` |
| Ambiente transparente, $\mathrm{Im} n_0 = 0$ | La potencia incidente está bien definida | Inmersión en un líquido absorbente — **rechazada** |
| Coherencia total de extremo a extremo | Las amplitudes se suman en todas partes | Sustratos gruesos, fuentes de banda ancha ([§11](#11-dónde-el-modelo-deja-de-ser-cierto)) |
| $n$ constante, no $n(\lambda)$ | Un índice por material | Cualquier espectro real en un rango amplio |

Ese es el modelo. Fíjate en lo que **no** supone: no supone que las capas sean
delgadas, ni sin pérdidas, ni que el ángulo sea pequeño, ni que haya pocas. La
absorción y la reflexión total interna salen gratis, siempre que el álgebra se
haga en el plano complejo y la rama se elija físicamente. Ese es todo el truco
de la sección siguiente.

---

## 6. Las ecuaciones

### 6.1 De Maxwell a dos problemas escalares

En una región sin fuentes, lineal, isótropa y no magnética, toda componente del
campo $\psi$ obedece la ecuación de Helmholtz

$$\nabla^2\psi + k_0^2 n^2 \psi = 0, \qquad k_0 = \frac{2\pi}{\lambda}$$

con $\lambda$ la longitud de onda **en vacío**. Dos hechos estructurales
colapsan esto en algo que un ordenador puede hacer en veinte líneas.

**Hecho 1 — la estructura solo depende de $z$.** Es invariante bajo traslación
en $x$ y en $y$. Así que podemos buscar soluciones de la forma
$\psi(x,z) = \psi(z)\thinspace e^{ik_x x}$, tomando el plano de incidencia como $xz$.
En cualquier interfaz la condición de contorno debe cumplirse para *todo* $x$, y
dos funciones de $x$ coinciden en todas partes solo si su dependencia en $x$ es
idéntica. Por tanto:

$$\boxed{\enspace k_x \text{ is the same in every layer}\enspace}$$

Esta es la ley de Snell. No «una ley sobre rayos que se doblan» — una **ley de
conservación impuesta por una simetría**, exactamente igual que la conservación
del momento a partir de la invariancia traslacional. Escribir
$k_x = k_0 n_k \sin\theta_k$ devuelve el familiar
$n_0\sin\theta_0 = n_k\sin\theta_k$, pero la forma de cantidad conservada es la
que sobrevive cuando $n$ es complejo y $\theta$ deja de ser un ángulo.

**Hecho 2 — el problema vectorial se parte en dos.** Con el plano de incidencia
fijado, las ecuaciones de Maxwell se desacoplan en dos problemas escalares
independientes:

| | Campo transversal | También llamada | Imagen física |
|---|---|---|---|
| **s** | $E = E_y\hat y$ | TE, $\sigma$ | $E$ perpendicular al plano de incidencia |
| **p** | $H = H_y\hat y$ | TM, $\pi$ | $E$ en el plano de incidencia |

Todo estado de polarización es una superposición de estos dos, así que resolver
ambos lo resuelve todo. Por eso el código arrastra un argumento `pol` por todas
las funciones en vez de una matriz $4\times4$: la física ya nos diagonalizó el
problema por bloques.

### 6.2 El vector de onda longitudinal, y por qué $\arcsin$ es una trampa

Dentro de la capa $k$, $k_x^2 + k_{z,k}^2 = k_0^2 n_k^2$, así que

$$k_{z,k} = k_0\sqrt{n_k^2 - \left(n_0\sin\theta_0\right)^2}
\equiv k_0\thinspace n_k\cos\theta_k,
\qquad
\cos\theta_k = \sqrt{1 - \left(\frac{n_0\sin\theta_0}{n_k}\right)^2}$$

Esto es [`physics.layer_cosines()`](../physics.py). Dos cosas al respecto.

**Nunca calcules $\theta_k = \arcsin(\cdot)$ y luego tomes su coseno.** La ruta
del libro de texto tira precisamente los dos regímenes interesantes:

- pasado el ángulo crítico el argumento excede 1 y `arcsin` devuelve `nan`;
- para $n_k$ complejo el ángulo no es un número real en absoluto y el concepto
  de «el ángulo en la capa absorbente» deja de ser útil.

Trabaja con $\cos\theta_k$ como número complejo desde el principio y ambos casos
son solo... aritmética. La reflexión total interna se convierte en un
$\cos\theta$ puramente imaginario; la absorción, en uno complejo. Ningún caso
especial.

**La raíz cuadrada tiene dos ramas, y elegir entre ellas es física, no
numérica.** $\sqrt{\cdot}$ devuelve $\pm$; la onda $e^{ik_z z}$ decae o crece al
avanzar. El requisito físico es que un medio pasivo atenúe:

$$\mathrm{Im}\negthinspace \left(n_k\cos\theta_k\right) \ge 0
\qquad\text{and, when that is zero,}\qquad
\mathrm{Re}\negthinspace \left(n_k\cos\theta_k\right) \gt 0$$

La primera condición dice *decae hacia delante, nunca amplifiques*. La segunda
escoge la onda propagante que lleva energía en $+z$ en el caso sin pérdidas,
donde la primera condición por sí sola no decide. En el código:

```python
q = n * cos_theta
wrong_branch = (q.imag < 0) | ((q.imag == 0) & (q.real < 0))
return np.where(wrong_branch, -cos_theta, cos_theta)
```

Este es el ejemplo más claro de toda la entrada de una regla que *parece*
numérica y que en realidad es una afirmación sobre la naturaleza — y por eso
vive en `physics.py` y no en un solver. Equivócate y la conservación de la
energía se seguirá cumpliendo a la perfección; simplemente estarás simulando un
medio que amplifica la luz.

### 6.3 Fresnel: continuidad de los campos tangenciales

En una interfaz sin carga ni corriente libres, las componentes tangenciales de
$\mathbf{E}$ y $\mathbf{H}$ son continuas. Ese es el único ingrediente. Escribe
$c_k \equiv \cos\theta_k$ y toma una onda de amplitud unidad en el medio $i$ que
incide sobre el medio $j$.

**Polarización s.** $E_y$ es tangencial, así que $1 + r = t$. La componente
magnética tangencial es $H_x = -\dfrac{k_z}{\omega\mu_0}E_y$, así que la
continuidad de $H_x$ da $n_ic_i(1-r) = n_jc_jt$. Dos ecuaciones, dos incógnitas:

$$r^s_{ij} = \frac{n_ic_i - n_jc_j}{n_ic_i + n_jc_j},
\qquad
t^s_{ij} = \frac{2n_ic_i}{n_ic_i + n_jc_j}$$

**Polarización p.** Ahora la tangencial es $H_y$ y
$E_x = \dfrac{k_z}{\omega\varepsilon_0 n^2}H_y$, así que los mismos dos pasos
con $n \to 1/n$ en el sitio adecuado dan

$$r^p_{ij} = \frac{n_jc_i - n_ic_j}{n_jc_i + n_ic_j},
\qquad
t^p_{ij} = \frac{2n_ic_i}{n_jc_i + n_ic_j}$$

Esto es [`physics.fresnel()`](../physics.py), literalmente.

> **Un aviso de convención que a la gente le cuesta días.** Para la polarización
> p, el $t^p$ de arriba es el cociente de las *magnitudes* de los campos
> eléctricos, no de sus componentes $x$. Distintos libros toman decisiones
> distintas aquí, y por eso la fórmula de la transmitancia de §6.5 se ve
> distinta en distintos libros. También es por eso que, en esta convención,
> $r^p = -r^s$ en incidencia normal: un artefacto del convenio de signos, no
> física. $R^s = R^p$ en $\theta = 0$, como debe ser — en incidencia normal no
> hay plano de incidencia respecto al que polarizarse.

**Brewster sale de inmediato.** $r^p = 0$ cuando $n_jc_i = n_ic_j$. Combinado
con Snell eso da

$$\tan\theta_B = \frac{n_j}{n_i}$$

y a ese ángulo $\theta_i + \theta_j = 90°$. La lectura física: la onda reflejada
la radian dipolos excitados en el medio $j$, que oscilan a lo largo de
$\mathbf{E}_j$; en Brewster esa dirección *es* la dirección hacia la que tendría
que ir el rayo reflejado, y un dipolo no radia a lo largo de su propio eje. No
existe nada análogo para s, cuyos dipolos son siempre perpendiculares al plano.
Esta es la afirmación que [`experiments/brewster.py`](../experiments/brewster.py)
comprueba numéricamente.

### 6.4 La fase a través de una capa

Cruzar una vez una capa de espesor $d_k$ multiplica la amplitud por
$e^{i k_{z,k} d_k}$, así que definimos

$$\delta_k = \frac{2\pi}{\lambda}\thinspace n_k \cos\theta_k\thinspace d_k$$

[`physics.accumulated_phase()`](../physics.py). Parte real = avance de fase;
parte imaginaria = atenuación, ya que
$e^{i\delta} = e^{i\mathrm{Re}\delta}e^{-\mathrm{Im}\delta}$. Para un medio
pasivo en la rama correcta $\mathrm{Im}\delta \ge 0$, así que
$|e^{i\delta}| \le 1$ **siempre**. Recuerda esa desigualdad: es toda la razón
por la que uno de los dos solvers no puede desbordar
([§7.4](#74-la-misma-física-distinta-numérica)).

**Ese es todo el dominio.** Snell, Fresnel, fase. Tres ideas, ~40 líneas de
Python. Todo lo que viene después es contabilidad — y lo que persigue la
[arquitectura](../../docs/architecture.md) del repositorio es que la contabilidad
sea exactamente la parte que puedes intercambiar.

### 6.5 Potencia: por qué $T \neq |t|^2$

$R = |r|^2$ es seguro: la onda reflejada viaja en el mismo medio que la
incidente, así que el cociente de potencias es el cociente de $|E|^2$. La
transmisión no lo es, porque la onda transmitida vive en un medio *distinto* y
viaja con otro ángulo. Lo que se conserva es la componente del vector de
Poynting promediado en el tiempo **normal a la interfaz**:

$$S_z = \tfrac12\mathrm{Re}\left(\mathbf{E}\times\mathbf{H}^{\ast}\right)_z$$

Haciendo esa integral para cada polarización, con los convenios de campo de
§6.3:

$$S_z^{\thinspace s} \propto \mathrm{Re}(n\cos\theta)\thinspace |E|^2,
\qquad
S_z^{\thinspace p} \propto \mathrm{Re}(n\cos^{\ast}\negthinspace \theta)\thinspace |E|^2$$

De ahí [`physics.normal_flux()`](../physics.py) y

$$T^s = |t|^2\thinspace \frac{\mathrm{Re}(n_fc_f)}{\mathrm{Re}(n_0c_0)},
\qquad
T^p = |t|^2\thinspace \frac{\mathrm{Re}(n_fc_f^{\ast})}{\mathrm{Re}(n_0c_0^{\ast})},
\qquad
A = 1 - R - T$$

El conjugado en el caso p no es una errata y no es cosmético — es la diferencia
entre que el campo transversal sea $\mathbf{E}$ o $\mathbf{H}$, y solo importa
cuando $\cos\theta$ es complejo, es decir, exactamente cuando una capa absorbe o
has pasado el ángulo crítico. Que es exactamente cuando menos probable es que te
des cuenta de que lo hiciste mal.

Para medios transparentes en incidencia normal degenera al familiar
$T = |t|^2 n_f/n_0$, y pasado el ángulo crítico
$\mathrm{Re}(n_fc_f) = 0$ da $T = 0$ exactamente, sin ningún caso especial en
el código.

> **Dónde muerde esto.** Si el *ambiente* absorbe, «potencia incidente» no tiene
> un significado único — la onda entrante ya va decayendo, así que su intensidad
> depende de dónde la midas. Sin protección, esta entrada devolvía
> $R = 5.83$, $T = -4.82$ y no se quejaba. Por eso `check_domain()` lanza una
> excepción en vez de aproximar. Véase Byrnes §5 para el argumento completo.

---

## 7. Componer la pila: tres formas, una física

### 7.1 Una película: sumar la serie infinita (Airy)

Ambiente 0, película 1 de fase $\delta$, sustrato 2. Enumera las ondas parciales
que salen de vuelta:

$$r = r_{01} + t_{01}r_{12}t_{10}e^{2i\delta}
      + t_{01}r_{12}r_{10}r_{12}t_{10}e^{4i\delta} + \cdots
    = r_{01} + t_{01}t_{10}r_{12}e^{2i\delta}\sum_{m\ge0}\left(r_{10}r_{12}e^{2i\delta}\right)^m$$

Una serie geométrica. Súmala y luego usa las **relaciones de Stokes**, que se
siguen directamente de las fórmulas de Fresnel de arriba:

$$r_{10} = -r_{01},\qquad t_{01}t_{10} = 1 - r_{01}^2$$

y todo se colapsa:

$$\boxed{\enspace r = \frac{r_{01} + r_{12}e^{2i\delta}}{1 + r_{01}r_{12}e^{2i\delta}}\enspace}$$

Infinitos rebotes, una fracción. Esta es la fórmula de Airy, y es la forma
cerrada más útil de toda la materia — cada test de `test_physics.py` que
comprueba una sola película contra «la respuesta analítica» comprueba contra
esta.

Fíjate en el denominador. Es una resonancia: cuando
$r_{01}r_{12}e^{2i\delta} \to -1$ la respuesta explota. Eso es una cavidad
Fabry–Pérot, y es el mismo denominador que aparecerá en la recursión.

### 7.2 Muchas películas: plegar de una en una (Rouard)

El truco está en que a la fórmula de Airy le da igual que el «medio 2» sea un
semiespacio. Sustituye $r_{12}$ por el coeficiente de reflexión efectivo de
*todo lo que hay debajo de la película* y puedes recurrir. Empieza en el
sustrato y sube:

$$r_k = \frac{\rho_k + r_{k+1}e^{2i\delta_{k+1}}}{1 + \rho_k r_{k+1}e^{2i\delta_{k+1}}},
\qquad
t_k = \frac{\tau_k\thinspace t_{k+1}\thinspace e^{i\delta_{k+1}}}{1 + \rho_k r_{k+1}e^{2i\delta_{k+1}}}$$

donde $\rho_k,\tau_k$ son los coeficientes de Fresnel desnudos de la interfaz
$k \to k+1$, y $\delta_{k+1}$ es la fase a través de la capa inmediatamente
inferior. Esto es [`methods/recursion.py`](../methods/recursion.py), y es el
método de Rouard (1937).

### 7.3 Muchas películas: multiplicar matrices (Abelès)

Como alternativa, sigue el par de amplitudes $(A_k, B_k)$ — la que va hacia
delante y la que va hacia atrás — en cada capa, y observa que tanto las
interfaces como la propagación actúan sobre ese par de forma **lineal**.
Convertir la descripción de scattering en una descripción de transferencia
(usando las mismas relaciones de Stokes) da

$$I_{ij} = \frac{1}{t_{ij}}\begin{pmatrix}1 & r_{ij}\cr r_{ij} & 1\end{pmatrix},
\qquad
P_k = \begin{pmatrix}e^{-i\delta_k} & 0\cr 0 & e^{i\delta_k}\end{pmatrix}$$

y la pila es simplemente su producto:

$$M = I_{01}P_1I_{12}P_2\cdots I_{N-1,N}$$

Impón que no haya onda hacia atrás en el sustrato,
$(A_0,B_0)^\top = M(A_N,0)^\top$ con $A_0 = 1$, y lee

$$t = \frac{1}{M_{00}}, \qquad r = \frac{M_{10}}{M_{00}}$$

[`methods/transfer_matrix.py`](../methods/transfer_matrix.py). Escribir
$I$ en términos de los coeficientes de Fresnel en vez de en la forma de libro de
texto $D_iP D_i^{-1}$ elimina un `linalg.inv` por capa — el original de 2024 lo
llamaba dos veces por capa sin razón.

### 7.4 La misma física, distinta numérica

Los dos solvers coinciden hasta $10^{-13}$, cosa que la suite verifica. *No* son
igual de buenos.

$P_k$ contiene $e^{+i\delta_k}$, cuyo módulo es $e^{+\mathrm{Im}\delta_k}$
— **crece** exponencialmente en una capa absorbente. El cociente final
$r = M_{10}/M_{00}$ cancela ese crecimiento analíticamente, así que la respuesta
sigue siendo correcta... hasta que $M_{00}$ supera el rango del float y la
cancelación se convierte en `inf/inf`. Medido en esta entrada: unos 20 µm de
metal en una sola capa, y entonces $r$ pasa a `NaN` sin ningún aviso.

La recursión no puede hacer esto. Todo factor que toca es $e^{i\delta}$ con
$|e^{i\delta}| \le 1$ para una capa pasiva (§6.4), así que la recursión solo
puede encoger. Se desborda por abajo con elegancia hasta cero allí donde el
producto de matrices explota.

![Arriba: reflectancia de una única capa absorbente frente a su espesor,
calculada de las dos formas. Las dos curvas se superponen y luego la de matriz
de transferencia se corta. Abajo: la diferencia entre ellas, a la escala de un
bit de doble precisión.](figures/ceiling.png)

**Qué concluir:** no hay una pérdida gradual de precisión que te avise. Los dos
solvers coinciden hasta $7\times10^{-16}$ — un bit o dos de doble precisión — en
todo espesor donde ambos funcionan, y luego uno de ellos deja de devolver un
número siquiera. Medido aquí: la última respuesta finita a 20.6 µm y `NaN` a
20.7 µm.

Esta es la misma inestabilidad que hace inservible la formulación de matriz de
transferencia para redes gruesas, y la razón de que las implementaciones de RCWA
usen matrices de scattering en su lugar — véase Li (1996), que es la referencia
estándar sobre exactamente este fallo.

**Y esto es la recompensa de la [arquitectura](../../docs/architecture.md).** Dos
métodos, un `physics.py`: la física es idéntica hasta $10^{-13}$ y solo difiere
el techo numérico. Poder decir esa frase con confianza es toda la razón por la
que las ecuaciones viven en un fichero que no importa nada.

---

## 8. Análisis de escalas: leer la respuesta en la fase

Antes de ejecutar nada, mira $\delta = \frac{2\pi}{\lambda}n d\cos\theta$ y
pregunta qué valores importan. Casi todo diseño clásico es una afirmación sobre
$\delta$.

### 8.1 El cuarto de onda, $\delta = \pi/2$

$$n\thinspace d\cos\theta = \frac{\lambda}{4}
\quad\Longrightarrow\quad
d = \frac{\lambda}{4n\cos\theta}$$

El viaje de ida y vuelta dentro de la capa es $2\delta = \pi$. Combinado con el
cambio de signo que da la reflexión sobre un índice más alto, las reflexiones
parciales consecutivas vuelven **en fase** — constructiva, un espejo — o **en
oposición de fase** — destructiva, un recubrimiento AR — según el orden de los
índices.

*Respuesta a la pregunta 1:* el MgF₂ ($n=1.38$) a 550 nm necesita
$d = 550/(4\times1.38) = 99.6$ nm. Unas **330 capas atómicas**. Ese número es la
razón de que los recubrimientos AR tuvieran que esperar a la deposición en
vacío: no se llega a cien nanómetros puliendo.

### 8.2 La media onda, $\delta = \pi$ — la capa ausente

Entonces $P_k = \mathrm{diag}(e^{-i\pi}, e^{i\pi}) = -I$, que invierte el
signo de todo el producto de matrices. Así que $r = M_{10}/M_{00}$ queda
**completamente inalterado**, y $t$ gana una fase $\pi$ con $|t|$ sin cambios.

Una capa de media onda es invisible en potencia a su longitud de onda de diseño,
sea cual sea su índice. No es invisible a ninguna otra longitud de onda, que es
lo que la hace útil — es la forma de añadir un rasgo espectral sin perturbar el
punto de diseño. También es una prueba afilada de si tu convenio de fase es
correcto, y está en `test_physics.py` exactamente por eso.

### 8.3 Admitancia: un cuarto de onda invierte

Para una capa de cuarto de onda en incidencia normal, la matriz característica
lleva la admitancia de entrada $Y$ de todo lo que hay debajo a

$$Y \longmapsto \frac{n^2}{Y}$$

Todo el diseño con cuartos de onda se sigue de iterar ese único mapa.

**AR de una capa.** Una capa sobre un sustrato: $Y = n_1^2/n_s$. Reflexión cero
requiere $Y = n_0$, así que

$$\boxed{\thinspace n_1 = \sqrt{n_0 n_s}\thinspace }$$

Para el vidrio, $\sqrt{1.52} = 1.23$. Ningún material duradero tiene un índice
tan bajo — el MgF₂ con 1.38 es el suelo práctico, y da un 1.3% en vez de un 0%,
y por eso los recubrimientos AR reales usan varias capas en vez de una. Esa
distancia entre $\sqrt{n_0n_s}$ y lo que ofrece la química es toda la razón de
que el diseño AR multicapa exista como campo.

**Pila de Bragg.** $(HL)^N$ sobre un sustrato: aplica el mapa $2N$ veces.

$$Y = n_s\left(\frac{n_H}{n_L}\right)^{2N},
\qquad
R = \left(\frac{n_0 - Y}{n_0 + Y}\right)^2$$

Para $Y \gg n_0$ esto se linealiza de forma preciosa:

$$1 - R  \simeq \frac{4n_0}{n_s}\left(\frac{n_L}{n_H}\right)^{2N}$$

**Cada periodo añadido multiplica la fuga por $(n_L/n_H)^2$.** Con
$n_H/n_L = 2.3/1.45$ ese factor es 0.40 — cada par reduce lo que atraviesa en
2.5×.

*Respuesta a la pregunta 2:* $R \gt 0.999$ requiere $Y \gt 4n_0/10^{-3} = 4000$,
así que $(1.586)^{2N} \gt 2632$, así que $N \gt 8.5$: **nueve pares.** Ni
cincuenta ni quinientos. Las exponenciales son la razón de que el diseño de
espejos sea fácil y de que a `experiments/bragg_mirror.py` le bastaran 16
periodos para llegar a seis nueves.

### 8.4 Ancho de la banda de rechazo — el que *no* mejora

Los bordes de banda de una pila periódica infinita están donde la fase de Bloch
de un periodo se vuelve compleja,
$\left|\tfrac12\mathrm{Tr}M_{\text{period}}\right| = 1$. Para un periodo de
cuarto de onda eso da

$$\frac{\Delta\lambda}{\lambda_0} = \frac{4}{\pi}\arcsin\negthinspace \left(\frac{n_H-n_L}{n_H+n_L}\right)$$

*Respuesta a la pregunta 3:* con 2.3/1.45 eso es **0.291**, es decir, 160 nm de
ancho a 550 nm. Y fíjate en lo que *no* está en la fórmula: $N$. **Más periodos
compran profundidad, nunca anchura.** La anchura la fija solo el contraste de
índices. Aquí el primer instinto de todo el mundo es equivocado, y por eso vale
la pena medirlo en vez de afirmarlo — y por eso `bragg_mirror.py` imprime la
anchura medida junto a la analítica.

![Izquierda: luz que se fuga a través de una pila de cuarto de onda frente al
número de periodos, en escala logarítmica, con la estimación en forma cerrada.
Derecha: los bordes de la banda de rechazo en nanómetros frente al número de
periodos, para dos contrastes de índice, cada uno contra su banda exacta
dibujada como una franja fija.](figures/depth_not_width.png)

**Qué concluir:** los dos paneles responden a dos preguntas distintas que es
fácil confundir. La profundidad cae exponencialmente en $N$ y aterriza sobre la
estimación de servilleta a lo largo de siete décadas. La anchura no se mueve con
$N$ en absoluto — las franjas son la banda de Bloch exacta y ningún $N$ aparece
en la fórmula que las dibuja. Lo que crece es la *medición*: un umbral del 99%
del pico solo puede encontrar la banda una vez que la cima es lo bastante plana
como para tener un 99% del que hablar, y por eso el propio experimento de la
entrada informa de una anchura que deriva hacia arriba a $N$ bajo.

Para ensanchar una banda de rechazo necesitas contraste, o varias pilas con
longitudes de onda de diseño escalonadas (un espejo «chirpeado»). Para alcanzar
*todos* los ángulos y ambas polarizaciones a la vez necesitas una condición
sobre el contraste que la mayoría de los pares de materiales no cumplen — ese es
el resultado de Fink et al. (1998).

### 8.5 Ángulo: por qué los recubrimientos viran al azul cuando los inclinas

$\delta \propto \cos\theta_k$, así que inclinar *reduce* la fase, y la longitud
de onda de diseño baja:

$$\lambda_{\text{design}}(\theta) \approx \lambda_0\sqrt{1 - \left(\frac{n_0\sin\theta_0}{n_{\text{eff}}}\right)^2}$$

Todo filtro dieléctrico vira al azul con el ángulo. Tus gafas se ven más moradas
de canto; un espejo dicroico en un microscopio hay que especificarlo a 45°, no
en incidencia normal. Esta es también la huella que distingue el color
estructural del pigmento, en la naturaleza y en un laboratorio.

![Reflectancia de una pila de cuarto de onda de ocho periodos frente a la
longitud de onda, a cuatro ángulos de incidencia. Toda la banda de rechazo se
desplaza hacia longitudes de onda más cortas a medida que crece el
ángulo.](figures/blueshift.png)

**Qué concluir:** la banda no se difumina ni se debilita al inclinarla — se
*mueve*, en bloque, y mantiene su forma. Medido aquí: 66 nm hacia el azul entre
incidencia normal y 60°. Un pigmento no puede hacer esto, y por eso la
dependencia con el ángulo es la prueba de un segundo para el color estructural.

### 8.6 El ángulo crítico

Para $n_0 \gt n_1$ y $\sin\theta_0 \gt n_1/n_0$, $\cos\theta_1$ se vuelve
puramente imaginario. En la rama física $n_1c_1 = i\thinspace |n_1c_1|$, así que
con $n_0c_0$ real,

$$r = \frac{n_0c_0 - i|n_1c_1|}{n_0c_0 + i|n_1c_1|}
\quad\Longrightarrow\quad
|r| = 1 \text{ exactly},\qquad T = 0 \text{ exactly}$$

Reflexión total interna sin casos especiales, sin `nan`, y con un campo
evanescente no nulo en el medio 1 que no lleva potencia neta a través de la
frontera. Lo único que hizo que esto funcionara fue elegir la rama correctamente
en §6.2.

---

## 9. Formas cerradas que vale la pena memorizar

Esto es contra lo que compruebas el código. Contrastar dos solvers demuestra que
coinciden; contrastar contra una forma cerrada demuestra que son *correctos*.
Cada fila de aquí es un test en [`../tests/`](../tests/).

| Situación | Resultado |
|---|---|
| Incidencia normal, una interfaz | $R = \left(\dfrac{n_0-n_1}{n_0+n_1}\right)^2$ |
| Aire/vidrio, normal | $R = 0.04$ |
| Ángulo de Brewster | $R^p = 0$ en $\theta_B = \arctan(n_j/n_i)$ |
| Ángulo crítico y más allá | $R = 1$, $T = 0$, exactamente |
| Una película, cualquier $\delta$ | $r = \dfrac{r_{01}+r_{12}e^{2i\delta}}{1+r_{01}r_{12}e^{2i\delta}}$ (Airy) |
| Capa única de cuarto de onda | $R = \left(\dfrac{n_0n_s-n_1^2}{n_0n_s+n_1^2}\right)^2$ |
| AR ideal de una capa | $n_1 = \sqrt{n_0n_s}$ |
| Capa de media onda | ausente: $R$ sin cambios en $\lambda_0$ |
| Pila de cuarto de onda $(HL)^N$ | $Y = n_s(n_H/n_L)^{2N}$, $R = \left(\dfrac{n_0-Y}{n_0+Y}\right)^2$ |
| Fuga de la pila, $N$ grande | $1-R \simeq \dfrac{4n_0}{n_s}\left(\dfrac{n_L}{n_H}\right)^{2N}$ |
| Ancho de la banda de rechazo | $\dfrac{\Delta\lambda}{\lambda_0} = \dfrac{4}{\pi}\arcsin\dfrac{n_H-n_L}{n_H+n_L}$ |
| Cualquier pila sin pérdidas | $R + T = 1$, a todo ángulo, ambas polarizaciones |
| Pila simétrica invertida | $R$ sin cambios |

**Un aviso sobre la penúltima fila.** $R + T = 1$ es el test que todo el mundo
escribe primero y por sí solo no vale casi nada. En esta entrada se cumplió con
seis decimales sobre tres resultados físicamente *incorrectos* — un ambiente
absorbente que devolvía $R = 5.83$, un medio con ganancia que devolvía
$A = -0.29$. Una ley de conservación restringe tu contabilidad, no tu física.
Las formas cerradas están por encima, y el acuerdo entre métodos por debajo de
ambos.

---

## 10. Lo que mostró la simulación

La regla del libro: **predice antes de ejecutar.** Cada experimento de la entrada
está construido como una predicción con un número pegado, no como una gráfica
que admirar. Las figuras de todo este documento salen de
[`stack.py`](../experiments/stack.py), que existe porque la derivación sostiene
cuatro cosas que nada en la entrada había graficado.

**[`bragg_mirror.py`](../experiments/bragg_mirror.py)** — predicción: la
reflectancia de pico sigue exactamente la transformación de admitancia, y el
ancho de la banda de rechazo no se mueve con $N$.

```
 periods     R peak   analytic   stopband
       2   0.658887   0.658887     0.0909
       4   0.936438   0.936438     0.1101
       8   0.998363   0.998363     0.2319
      16   0.999999   0.999999     0.2927

analytic stopband (infinite stack): 0.2911
```

Seis decimales en el pico. El ancho converge a 0.2911 por abajo — el valor
medido usa un umbral burdo del 99% del pico, que solo cobra sentido una vez que
la banda es genuinamente plana, de ahí la deriva a $N$ bajo. La estimación de
servilleta de §8.3 también acierta: para $N=8$ predice una fuga de
$1.639\times10^{-3}$ contra un $1.637\times10^{-3}$ medido, y se mantiene dentro
del 0.2% hasta $N=16$.

**[`brewster.py`](../experiments/brewster.py)** — predicción: el mínimo de
$R^p$ está en $\arctan(n_2/n_1)$ y es un cero verdadero.

```
       interface      found   arctan(n2/n1)    Rp at min
    air -> glass    56.651d         56.659d    7.677e-09
  air -> silicon    75.557d         75.548d    1.090e-07
    glass -> air    33.339d         33.341d    2.352e-09
```

Un cero verdadero, limitado por la rejilla angular y no por la física.

La tabla de verificación completa vive en [el README de la entrada](../README.md)
§4.

---

## 11. Dónde el modelo deja de ser cierto

La sección que más importa, y la que suele faltar.

### 11.1 Coherencia — el supuesto que falla primero

Todo lo anterior suma amplitudes, lo que exige que las ondas parciales tengan
una fase relativa estable. Solo la tienen si el camino de ida y vuelta es más
corto que la **longitud de coherencia** de la fuente:

$$L_c \approx \frac{\lambda^2}{\Delta\lambda}$$

| Fuente | $\Delta\lambda$ | $L_c$ a 550 nm |
|---|---|---|
| Luz solar / luz blanca | ~300 nm | ~1 µm |
| LED | ~30 nm | ~10 µm |
| Láser de HeNe | ~0.002 nm | ~15 cm |

Por eso el campo se llama óptica de películas *delgadas*. Una capa de 100 nm es
coherente para cualquier fuente. **Un sustrato de vidrio de 1 mm no lo es** — a
la luz del día, sus dos caras no interfieren, y el tratamiento correcto suma
*potencias* ahí mientras suma amplitudes dentro del recubrimiento. Ese es el
problema mixto coherente/incoherente, y Katsidis & Siapkas (2002) es la
referencia para él. Esta entrada no lo implementa, y cualquier recubrimiento
real sobre un sustrato real lo necesita.

### 11.2 El resto de la lista

| Límite | Qué pasa de verdad | Esta entrada |
|---|---|---|
| Ambiente absorbente | Potencia incidente indefinida; daba $R=5.83$, $T=-4.82$ | `ValueError` |
| Medio con ganancia, $\mathrm{Im}n\lt 0$ | La regla de la rama de decaimiento hacia delante se rompe; daba $A=-0.29$ | `ValueError` |
| ~20 µm de metal, una capa | $M_{00}$ desborda, $r \to$ `NaN` | usa `method="recursion"` |
| Dispersión $n(\lambda)$ | Todo espectro está sutilmente mal | no modelada — $n$ es constante |
| Rugosidad de la interfaz | Dispersión fuera de la dirección especular; $R+T\lt 1$ sin absorción | no modelada |
| Birrefringencia / anisotropía | s y p dejan de desacoplarse; hace falta $4\times4$ | no modelada |
| Haces enfocados o de pulso corto | Ensanchamiento angular/espectral, desplazamiento de Goos–Hänchen | no modelados |
| No linealidad | $n(I)$; la superposición falla | no modelada |
| Capas más delgadas que ~2 nm | El $n$ de volumen deja de significar nada | fuera de las premisas del modelo |

Dos de esas filas existen porque alguien **sondeó** los bordes, no porque nadie
razonara hasta llegar ahí. La suite estaba en verde y los dos agujeros estaban
abiertos de par en par. Que es la lección general y la razón de que esta sección
exista siquiera:

> Una suite de tests demuestra los casos que se te ocurrieron. Los límites de un
> modelo se encuentran atacándolo, no releyéndolo.

---

## 12. Lo esencial

- Una multicapa es **interferencia, no absorción**. Las amplitudes se suman; las
  potencias no. Todo fenómeno de este documento es un término cruzado.
- **Snell es una ley de conservación** — $k_x$ se conserva porque la estructura
  es invariante en $x$. Escrita así sobrevive a los índices complejos y a la
  reflexión total interna; escrita como $\arcsin$ no.
- **Fresnel es solo continuidad** de los campos tangenciales. Dos líneas de
  álgebra por polarización, y Brewster sale de $r^p = 0$.
- Todo el dominio son **tres ecuaciones**: Snell, Fresnel, fase. Todo lo demás
  es contabilidad — y la contabilidad es la parte que puedes intercambiar.
- **El corte de rama es física.** Elegir $\mathrm{Im}(n\cos\theta)\ge0$
  es la afirmación de que los medios pasivos atenúan. Equivócate y la
  conservación de la energía sigue pasando.
- **$T \neq |t|^2$.** La transmitancia lleva el cociente del flujo de energía
  normal, y las dos polarizaciones proyectan de forma distinta — con un
  conjugado que solo importa exactamente cuando no notarías que falta.
- **La suma infinita de rebotes es una serie geométrica** y se colapsa en la
  fórmula de Airy. La recursión y el producto de matrices son dos formas de
  iterar ese único resultado.
- **El cuarto de onda invierte la admitancia.** Los recubrimientos AR, los
  espejos de Bragg y la regla $\sqrt{n_0n_s}$ son todos ese único mapa aplicado
  un número distinto de veces.
- **Más periodos compran profundidad, nunca anchura.** El ancho de la banda de
  rechazo depende solo del contraste.
- **$R+T=1$ es un test débil.** Se cumplió sobre tres respuestas incorrectas.
  Las formas cerradas primero, el acuerdo entre métodos el último.
- **La coherencia es el supuesto que falla primero** en cualquier dispositivo
  real, y falla en el sustrato, no en el recubrimiento.

---

## 13. Preguntas abiertas

Cosas que este documento deliberadamente no responde, más o menos en orden de
cuánto enseñarían:

- **Pilas mixtas coherentes/incoherentes.** El tratamiento físicamente correcto
  de un recubrimiento sobre un sustrato de 1 mm bajo una fuente de banda ancha.
  Esta es la mayor brecha entre esta entrada y una herramienta usable.
- **El perfil de campo dentro de la pila.** $R$ y $T$ no dicen nada sobre
  *dónde* se absorbe la luz. Para una célula solar o un OLED esa distribución
  espacial es todo el objetivo de diseño, y sale de conservar $(A_k,B_k)$ en vez
  de descartarlos.
- **El problema inverso.** Dado un $R(\lambda)$ objetivo, encuentra las capas.
  La optimización por agujas (Tikhonravov 1996) es la respuesta clásica; los
  sustitutos de ML son la moda actual. Conviene saber que el modelo directo se
  llama millones de veces, así que la estabilidad numérica de §7.4 deja de ser
  académica.
- **Por qué un reflector omnidireccional necesita una condición de contraste.**
  Fink et al. (1998) — un resultado genuinamente no obvio que se sigue del mismo
  análisis de Bloch que §8.4.
- **Qué pasa cuando el periodo deja de ser periódico.** Espejos chirpeados,
  filtros rugate, pilas cuasiperiódicas y desordenadas — donde el argumento de
  Bloch ya no se aplica y el producto de matrices es todo lo que tienes.

---

## 14. Referencias

**Fundacionales**

- **Abelès, F.** *Recherches sur la propagation des ondes électromagnétiques
  sinusoïdales dans les milieux stratifiés. Application aux couches minces.*
  Annales de Physique **12**, 596–640 (1950).
  [enlace](https://www.annphys.org/articles/anphys/abs/1950/05/anphys19501205p596/anphys19501205p596.html)
  — el método de la matriz característica.
- **Rouard, P.** *Études des propriétés optiques des lames métalliques très
  minces.* Annales de Physique **11**, 291–384 (1937).
  [enlace](https://www.annphys.org/articles/anphys/abs/1937/07/anphys19371107p291/anphys19371107p291.html)
  — la recursión, trece años antes de las matrices.
- **Born, M. & Wolf, E.** *Principles of Optics*, §1.6. La derivación canónica
  de la óptica de medios estratificados.

**Pilas periódicas**

- **Yeh, P., Yariv, A. & Hong, C.-S.** *Electromagnetic propagation in periodic
  stratified media. I. General theory.* JOSA **67**, 423–438 (1977).
  [enlace](https://opg.optica.org/abstract.cfm?URI=josa-67-4-423)
  — ondas de Bloch, bordes de banda, de donde sale §8.4.
- **Fink, Y. et al.** *A dielectric omnidirectional reflector.* Science **282**,
  1679–1682 (1998).
  [enlace](https://www.science.org/doi/10.1126/science.282.5394.1679)
- **Joannopoulos, J. D. et al.** *Photonic Crystals: Molding the Flow of Light*,
  2ª ed. (2008). Una pila de cuarto de onda es un cristal fotónico 1D; cap. 4.

**Numérica — la parte que la mayoría de los textos se salta**

- **Li, L.** *Formulation and comparison of two recursive matrix algorithms for
  modeling layered diffraction gratings.* JOSA A **13**, 1024–1035 (1996).
  [enlace](https://opg.optica.org/josaa/abstract.cfm?uri=josaa-13-5-1024)
  — por qué las matrices de transferencia explotan y las de scattering no. §7.4
  en un solo artículo.
- **Byrnes, S. J.** *Multilayer optical calculations.* arXiv:1603.02720.
  [enlace](https://arxiv.org/abs/1603.02720)
  — cortes de rama, ambientes absorbentes, el conjugado de la polarización p,
  capas incoherentes. El acompañante del paquete de Python `tmm`, y el
  tratamiento moderno más claro de las trampas.
- **Katsidis, C. C. & Siapkas, D. I.** *General transfer-matrix method for
  optical multilayer systems with coherent, partially coherent, and incoherent
  interference.* Applied Optics **41**, 3978–3987 (2002).
  [enlace](https://opg.optica.org/ao/abstract.cfm?uri=ao-41-19-3978)

**Diseño y práctica**

- **Macleod, H. A.** *Thin-Film Optical Filters*, 4ª ed. (2010). El libro del
  profesional — diagramas de admitancia, materiales reales, tolerancia de
  fabricación.
- **Yeh, P.** *Optical Waves in Layered Media* (1988).
- **Tikhonravov, A. V., Trubetskov, M. K. & DeBell, G. W.** *Application of the
  needle optimization technique to the design of optical coatings.* Applied
  Optics **35**, 5493–5508 (1996).
  [enlace](https://opg.optica.org/ao/abstract.cfm?uri=ao-35-28-5493)

**Color estructural**

- **Vukusic, P. & Sambles, J. R.** *Photonic structures in biology.* Nature
  **424**, 852–855 (2003).
- **Kinoshita, S., Yoshioka, S. & Miyazaki, J.** *Physics of structural colors.*
  Reports on Progress in Physics **71**, 076401 (2008).

---

*Código: [`../physics.py`](../physics.py) y [`../methods/`](../methods/) ·
Entrada: [`../README.md`](../README.md) · Arquitectura de todo el repositorio:
[`docs/architecture.md`](../../docs/architecture.md)*
