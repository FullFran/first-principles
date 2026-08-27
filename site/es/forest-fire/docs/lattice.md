<!-- translated-from: f471935341f4 -->

# Un bosque que se mantiene inflamable

> La física detrás de [`forest-fire/`](../README.md), derivada del problema
> y no de la fórmula. Lee esto si quieres saber *por qué* las reglas
> de `forest-fire/lattice.py` son esas y no otras.

Este documento sigue un ciclo, y el ciclo es lo importante:

```
phenomenon → question → order of magnitude → assumptions → minimal model
   → equations → scale analysis → closed forms → simulation → validation
   → limits of the model → next question
```

La parte central es lo que enseña una carrera. Los dos extremos — plantear la
pregunta y saber dónde se detiene el modelo — son lo que de verdad separa a
quien resuelve problemas nuevos de quien aplica fórmulas. Así que aquí el
espacio se lo llevan los dos extremos.

**Contenido**

1. [El fenómeno](#1-el-fenómeno)
2. [Para qué sirve esto](#2-para-qué-sirve-esto)
3. [Antes de calcular](#3-antes-de-calcular)
4. [Por qué falla la respuesta ingenua](#4-por-qué-falla-la-respuesta-ingenua)
5. [El modelo mínimo](#5-el-modelo-mínimo)
6. [Las reglas](#6-las-reglas)
7. [Dos maneras de terminar un fuego](#7-dos-maneras-de-terminar-un-fuego)
8. [Análisis de escalas: un umbral y una razón](#8-análisis-de-escalas-un-umbral-y-una-razón)
9. [Formas cerradas que vale la pena memorizar](#9-formas-cerradas-que-vale-la-pena-memorizar)
10. [Lo que mostró la simulación](#10-lo-que-mostró-la-simulación)
11. [Dónde el modelo deja de ser cierto](#11-dónde-el-modelo-deja-de-ser-cierto)
12. [Lo esencial](#12-lo-esencial)
13. [Preguntas abiertas](#13-preguntas-abiertas)
14. [Referencias](#14-referencias)

---

## 1. El fenómeno

La mayoría de los incendios forestales son pequeños. Unos pocos son enormes.
Representa cuántos incendios quemaron cada área y no obtienes una campana con un
tamaño típico y una dispersión — obtienes una recta en papel log-log a lo largo
de cuatro o cinco órdenes de magnitud, lo que significa que no hay tamaño típico
en absoluto.

Eso ya es extraño. «El incendio medio» es un número que puedes calcular y no
puedes usar, porque la media está dominada por los raros enormes y no describe
casi nada de lo que de verdad ocurre.

Más extraño todavía: la misma forma aparece en terremotos, avalanchas,
fulguraciones solares, extinciones y los tamaños de las ciudades. Sistemas sin
nada en común, produciendo la misma distribución.

> **La pregunta.**
> Los árboles crecen a cierto ritmo, los rayos caen a cierto ritmo, y el fuego
> se propaga entre árboles que se tocan.
> **¿Por qué debería el bosque acabar en la densidad donde el fuego apenas puede
> cruzarlo, sin que nadie lo ajuste ahí?**

Esa última cláusula es todo el asunto. Sacar una transición abrupta de un modelo
es fácil: pon el parámetro de control en el valor crítico a mano. Que el sistema
**llegue ahí por sí solo** es lo que hay que explicar, y es lo que nombra la
«criticalidad autoorganizada».

---

## 2. Para qué sirve esto

### 2.1 El fuego, que es el caso literal

Malamud, Morein y Turcotte mostraron en 1998 que los registros reales de
incendios — estadounidenses y australianos, incluida la prehistoria
reconstruida — tienen estadísticas frecuencia-área de ley de potencias a lo
largo de muchos órdenes de magnitud, y que la frecuencia de los incendios
pequeños y medianos sirve para cuantificar el riesgo de los grandes, como se
hace con los terremotos.

Ese es el rédito práctico, y es estadístico y no predictivo: no puedes decir
cuándo llega el gran incendio, y sí puedes decir cada cuánto.

### 2.2 Todo lo demás con esa forma

El mismo modelo, cambiando las palabras, es un esbozo plausible de epidemias en
una red de contactos, fallos en cascada en una red eléctrica, avalanchas en un
montón de arena y rumores en una multitud. En cada uno, algo se propaga
localmente entre vecinos, algo repone lo que consumió, y el sistema se sitúa
cerca del punto donde la propagación apenas percola.

Si ese parecido es profundo o superficial está genuinamente en disputa, y
[§11](#11-dónde-el-modelo-deja-de-ser-cierto) es donde este documento deja de
darlo por hecho.

### 2.3 La conexión que le importa a este repositorio

Un umbral de percolación es un **punto crítico**, y la razón de que no dependa
de los detalles microscópicos es el grupo de renormalización. Ese es el hilo que
va de aquí a [§13](#13-preguntas-abiertas): engrosa la escala de la red, mira
fluir los parámetros, y los detalles que no sobreviven al zoom son los que nunca
importaron.

### 2.4 Historia

Los niveles de verificación siguen la convención del libro: **A** es
documentado, idealmente desde una fuente primaria; **B** es una reconstrucción;
**C** es una historia que se cuenta en todas partes y que no pude rastrear hasta
su origen.

::: **Un montón de arena, y una afirmación muy ruidosa** · *Verificación: A para
la ciencia; B para la recepción.*

En 1987 Per Bak, Chao Tang y Kurt Wiesenfeld publicaron *Self-organized
criticality: an explanation of 1/f noise*. Su modelo era un montón de arena:
deja caer granos de uno en uno, y cuando una columna se vuelve demasiado
empinada se derrumba sobre sus vecinas, que pueden derrumbarse a su vez. Los
tamaños de avalancha salen distribuidos según una ley de potencias y — esta es
la afirmación — **nadie fijó la pendiente**. El montón se construye a sí mismo
hasta el ángulo donde son posibles avalanchas de todos los tamaños.

Bak pensaba que esta era la explicación general de por qué la naturaleza está
llena de leyes de potencias, y lo dijo largamente, incluido un libro titulado
*How Nature Works*. Fue, según casi todos los relatos, un defensor poco modesto.
El campo que creció alrededor de la idea ha pasado treinta años separando las
partes que se sostienen de las que se vendieron de más, y el modelo de esta
entrada es uno de los lugares donde ocurrió esa separación.

::: **Drossel y Schwabl, y un modelo que resultó más difícil de lo que
parecía** · *Verificación: A.*

Drossel y Schwabl publicaron la versión de incendios forestales en *Physical
Review Letters* en 1992: crecimiento, rayos, propagación y un estado crítico
autoorganizado en el límite $f \to 0$ **siempre que las escalas temporales se
separen**. Esa salvedad está en el resumen original y es el modelo entero, y por
eso [`check_rates`](../lattice.py) se niega a ejecutarse fuera de ella.

Durante una década fue el ejemplo de manual. Después Grassberger (2002) y
Pruessner y Jensen (2002) miraron redes grandes y encontraron que el escalado
está **roto**: no hay un único régimen de ley de potencias, y lo que el trabajo
anterior había ajustado era una mezcla de un cuerpo que no es ley de potencias y
un corte que no es escalado.

La historia ordenada es que un modelo simple explica por qué los incendios
siguen una ley de potencias. La historia verdadera es que el modelo más simple
de criticalidad autoorganizada no es, con la evidencia actual, limpiamente
crítico — y que eso lo estableció gente que se tomó la molestia de ir a redes
más grandes. Es mejor lección que la ordenada.

### Artículos que vale la pena leer

| Referencia | Por qué |
|---|---|
| [Bak, Tang & Wiesenfeld, *PRL* **59**, 381 (1987)](https://doi.org/10.1103/PhysRevLett.59.381) | Donde empieza la criticalidad autoorganizada |
| [Drossel & Schwabl, *PRL* **69**, 1629 (1992)](https://link.aps.org/doi/10.1103/PhysRevLett.69.1629) | Este modelo, con la salvedad de las escalas temporales en el resumen |
| [Malamud, Morein & Turcotte, *Science* **281**, 1840 (1998)](https://www.science.org/doi/10.1126/science.281.5384.1840) | Los incendios reales sí siguen una ley de potencias |
| [Grassberger, *New J. Phys.* **4**, 17 (2002)](https://arxiv.org/abs/cond-mat/0202022) | El escalado está roto. Léelo antes de citar el modelo |
| [Pruessner & Jensen, *Phys. Rev. E* **65**, 056707 (2002)](https://arxiv.org/abs/cond-mat/0201306) | De forma independiente, la misma conclusión |
| [Stauffer & Aharony, *Introduction to Percolation Theory*](https://doi.org/10.1201/9781315274386) | De donde salen $p_c$ y los exponentes |
| [`fire-percolation`](https://github.com/FullFran/fire-percolation) | Mi propia reproducción del escalado roto, y cincuenta años de registros españoles |

---

## 3. Antes de calcular

La regla del libro: **escribe un número antes de leer la sección siguiente.** El
aprendizaje está en la distancia entre tu número y el real, y esa distancia no
existe si no te comprometiste.

> 1. Un bosque con árboles en la mitad de sus sitios. **¿Puede cruzarlo un
>    fuego?** Ahora en el 60% de sus sitios. Misma pregunta. ¿Cuánto difieren
>    esas dos respuestas?
> 2. Reduces el número de rayos por un factor de dos mil. **¿Qué le pasa al
>    mayor incendio que acaba llegando?** ¿Crece un poco, o mucho?
> 3. Los bomberos apagan todos los incendios pequeños y dejan correr los
>    grandes. **¿Qué le pasa al área total quemada a lo largo de un siglo?**

Respuestas en [§8](#8-análisis-de-escalas-un-umbral-y-una-razón) y
[§10](#10-lo-que-mostró-la-simulación). La primera es el umbral más nítido de
este documento. La tercera es la que fallé, y el error está en
[§10.2](#102-el-argumento-de-la-supresión-en-dos-direcciones).

---

## 4. Por qué falla la respuesta ingenua

### 4.1 «El bosque arde a cierto ritmo medio»

El primer modelo tentador: el fuego consume cierta fracción del bosque al año,
así que escribe una tasa y listo.

Ese modelo tiene un tamaño típico de incendio, y los incendios reales no. Una
distribución con cola de ley de potencias no tiene escala característica — la
media está dominada por los eventos mayores, y si el exponente es lo bastante
suave la varianza ni siquiera existe. **Informar de un tamaño medio de incendio
no es un resumen, es un error de categoría**, igual que lo sería informar de un
terremoto medio.

### 4.2 «Entonces ajusta la densidad al punto crítico»

Mejor: el fuego cruza un bosque solo por encima de una densidad umbral, así que
pon la densidad en el umbral y obtienes incendios grandes.

Esto es correcto y no explica nada, porque requiere que alguien sostenga el
mando. Un bosque real no tiene a nadie ajustando su densidad de árboles, y la
densidad en la que se asienta es una *salida*.

**El movimiento que hace interesante al modelo es cerrar ese bucle.** Deja que
el crecimiento empuje la densidad hacia arriba y que el fuego la empuje hacia
abajo, y pregunta dónde acaba. La respuesta es: en el umbral, porque por debajo
los incendios no pueden propagarse y gana el crecimiento, y por encima los
incendios se propagan por todas partes y gana la quema. El punto crítico es un
atractor de la dinámica y no un valor que alguien eligió.

Eso es lo que significa «autoorganizado», y es la única idea genuinamente nueva
del modelo.

---

## 5. El modelo mínimo

| Supuesto | Qué aporta | Dónde se rompe |
|---|---|---|
| Una red cuadrada, cuatro vecinos | Un único umbral contra el que contrastar | $p_c$ es una propiedad de la red, no de los bosques |
| Los árboles son idénticos | Un estado, no una carga de combustible | Especies, edad, humedad, terreno |
| El fuego se propaga a los árboles que toca, siempre | Ninguna probabilidad de propagación que ajustar | Cortafuegos, viento, humedad, focos secundarios |
| El crecimiento es uniforme e independiente | Un parámetro $p$ | Las semillas caen cerca de los padres; el suelo varía |
| Los rayos son uniformes e independientes | Un parámetro $f$ | La ignición humana se agrupa cerca de las carreteras |
| $f \ll p \ll 1$ | Los incendios terminan antes del rebrote | El modelo entero — ver [§7](#7-dos-maneras-de-terminar-un-fuego) |
| Fronteras periódicas | Ningún sitio es especial | Los paisajes reales tienen costas y bordes |
| Sin viento, sin pendiente, sin estación | Isotropía | Todo el comportamiento del fuego, francamente |

Ese es el modelo. No contiene física de la combustión, ni meteorología, ni
biología, y la afirmación es que nada de eso importa para la *estadística* de
los tamaños de incendio. Si esa afirmación sobrevive es [§11](#11-dónde-el-modelo-deja-de-ser-cierto).

---

## 6. Las reglas

Aquí no hay ecuaciones. Hay tres reglas aplicadas a cada sitio en cada paso:

1. Un sitio en llamas queda vacío.
2. Un árbol junto a un sitio en llamas se prende.
3. Un sitio vacío hace crecer un árbol con probabilidad $p$; a un árbol le cae
   un rayo con probabilidad $f$.

El único contenido espacial es la regla 2, y es una línea —
[`spread()`](../lattice.py) son cuatro copias desplazadas de un array booleano
unidas con OR. Un **clúster** es lo que obtienes al aplicarla hasta que nada
nuevo se prende, y ese es el objeto del que trata todo el modelo: un fuego quema
un clúster, no un radio.

> **Una nota de implementación que en realidad es una nota de física.**
> [`strike()`](../lattice.py) devuelve una *máscara* en lugar de prender fuegos.
> Es para que quien la llama pueda dar a cada árbol alcanzado su propio fuego.
> El número esperado de impactos en un paso es $f\rho L^2$, que crece con el
> área, así que en una red grande varios impactos por paso es el caso normal — y
> quemarlos juntos informa de dos fuegos independientes como uno solo, inflando
> la distribución de tamaños en una cantidad que crece con $L$. Que es
> exactamente la variable que un estudio de tamaño finito intenta aislar.

---

## 7. Dos maneras de terminar un fuego

Las reglas de arriba no dicen cuánto dura un fuego respecto a lo que tarda el
bosque en crecer, y esa omisión es el supuesto central del modelo. `methods/` lo
hace conmutable.

**Instantáneo.** Cae el rayo, el clúster conexo arde hasta el suelo, y solo
entonces crece algo. El área quemada *es* el clúster que estaba en pie. Este es
el límite en el que se define el modelo.

**Sincrónico.** El autómata celular literal: en cada paso, los sitios en llamas
se vacían, sus vecinos se prenden, y los sitios vacíos brotan — incluidos los de
detrás del frente y los de justo delante. Un fuego que tarda muchos pasos
atraviesa un bosque que rebrota a su alrededor, así que el área consumida ya no
es el clúster en el que empezó. **Puede superar la red entera**, porque el suelo
puede arder dos veces.

Los dos coinciden en el límite que importa, y verlos separarse es como esta
entrada mide lo que vale la «separación de escalas temporales»
([§10.3](#103-cuándo-coinciden-los-dos-métodos)).

---

## 8. Análisis de escalas: un umbral y una razón

### 8.1 El umbral

Llena una red al azar con densidad $p$ y pregunta si los árboles conectan un
borde con el otro. Por debajo de una densidad crítica, esencialmente nunca; por
encima, esencialmente siempre:

$$\boxed{\enspace p_c = 0.5927460\enspace}$$

para percolación de sitios en una red cuadrada con cuatro vecinos. **No tiene
forma cerrada** — se conoce numéricamente con muchos dígitos y eso es todo — lo
que la convierte en una referencia externa genuina y no en algo a lo que el
modelo pudiera haberse ajustado.

*Respuesta a la pregunta 1.* Al 50% un fuego esencialmente nunca cruza; al 60%
esencialmente siempre lo hace. Diez puntos porcentuales, y el comportamiento es
cualitativamente distinto a cada lado. Eso es lo que significa un umbral y es
por lo que «el bosque está medio lleno» no es una descripción útil de nada.

### 8.2 Rayos por paso, que no es $f$

El régimen que el modelo necesita es que los incendios sean raros *y terminen
rápido*. Dos condiciones distintas, y solo una de ellas trata de $f$ a solas.

El número esperado de impactos por paso es

$$\langle\text{strikes}\rangle = f\thinspace\rho\thinspace L^2$$

así que a $f$ fijo **crece con el área**. Una guarda que solo comprueba
$f \ll p$ no puede ver esto, porque no lleva ningún $L$ dentro, y por tanto el
régimen puede fallar en silencio justo en el barrido que varía $L$.

### 8.3 Y la separación de escalas temporales la fija $p$

La otra condición — que un fuego termine antes de que el bosque rebrote — trata
de cuánto bosque aparece *durante* un fuego. Eso es tasa de crecimiento por
duración del fuego, así que lo controla $p$, **no $f/p$**.

Medido, con $f/p$ fijo en 0.01, la razón del tamaño medio de incendio entre los
dos métodos:

| $p$ | 0.02 | 0.01 | 0.005 | 0.002 |
|---|---|---|---|---|
| sincrónico / instantáneo | 7.0 | 2.1 | 1.9 | 1.0 |

Mantener $f/p$ constante y bajar solo $p$ los junta. Esa es la versión nítida de
una frase que normalmente se deja pasar sin más.

---

## 9. Formas cerradas que vale la pena memorizar

| Situación | Resultado |
|---|---|
| Umbral de percolación de sitios, red cuadrada | $p_c = 0.5927460$ |
| Por debajo de $p_c$ | sin clúster percolante, en el límite de red grande |
| Por encima de $p_c$ | percola con probabilidad que tiende a 1 |
| Impactos por paso | $f\rho L^2$ — crece con el área |
| Estado estacionario | área quemada por paso $=$ área crecida por paso |
| Método instantáneo | área quemada $=$ tamaño del clúster $\le L^2$ |
| Método sincrónico | el área quemada puede superar $L^2$ |
| Fuego endémico | por encima de $p \approx 0.1$ el fuego sincrónico nunca se apaga |
| Registros reales de incendios | frecuencia-área de ley de potencias, exponente de 1.3 a 1.5 |
| Longitud de correlación en $p_c$ | diverge — que es por lo que las redes finitas mienten |

**Un aviso sobre la fila del estado estacionario**, porque es la que decidió
[§10.2](#102-el-argumento-de-la-supresión-en-dos-direcciones). Es una ley de
conservación, no una aproximación: lo que crece tiene que arder tarde o
temprano, así que el área total quemada por unidad de tiempo la fijan $p$ y la
fracción vacía. Cualquier intervención que no cambie el *crecimiento* ni
*cuándo empiezan los fuegos* no puede cambiarla.

---

## 10. Lo que mostró la simulación

### 10.1 El umbral, medido

Predicción: el cruce está en $p_c$, y la transición se afila con la red.

![Fracción de redes aleatorias en las que los árboles percolan de un borde al
otro, frente a la densidad de árboles, para cuatro tamaños de red, con el umbral
de percolación marcado.](figures/percolation.png)

```
     L   p where spanning crosses 1/2   width of the crossing
    16                         0.5867                  0.1367
    32                         0.5900                  0.0896
    64                         0.5917                  0.0625
   128                         0.5926                  0.0467
```

**Qué concluir:** las dos mitades se sostuvieron. En $L = 128$ el cruce medido
es 0.5926 frente al verdadero 0.5927460, y la anchura se ha reducido a la mitad
dos veces. En una red infinita la curva sería un escalón; toda red finita lo
difumina, y ver encogerse el difuminado es lo que distingue una transición de
fase de un cambio gradual.

### 10.2 El argumento de la supresión, en dos direcciones

Predicción, escrita antes: **apaga todo incendio por debajo de un umbral de
tamaño, deja sus árboles en pie, y la densidad debería subir y el mayor incendio
crecer con ella.** Ese es el argumento estándar de acumulación de combustible.

```
 threshold   density    fires   largest  total burned
         0     0.398      953      7684       1385741
        10     0.397      643      7448       1388102
        50     0.396      484      7448       1388489
       200     0.395      402      7518       1391419
```

**Falso.** Nada se mueve — ni la densidad, ni el mayor incendio, ni el área
total quemada. La ley de conservación de §9 se interpone: lo que crece tiene que
arder, así que apagar un incendio no salva su combustible, se lo entrega al
siguiente.

Estaba listo para informar de que la paradoja no aparece en este modelo. Sí
aparece, en un mando que no había girado. El mecanismo es la **tasa de
ignición**:

![Izquierda: densidad de árboles frente a la tasa de rayos, con el umbral de
percolación marcado. Derecha: el mayor incendio como porcentaje del bosque,
frente al mismo eje.](figures/ignition.png)

```
      f      f/p  density   fires    mean  largest  of lattice
  2e-02  4.0e-01    0.244  242893     7.2      136        1.5%
  1e-03  2.0e-02    0.350   12689    88.6     2209       24.0%
  2e-04  4.0e-03    0.374    2640   409.8     5396       58.6%
  1e-05  2.0e-04    0.528     193  4224.5     9083       98.6%
```

**Qué concluir:** 2000× menos chispas lleva el mayor incendio del 1.5% del
bosque al 98.6%, y la densidad de 0.24 hasta pasar $p_c$ y llegar a 0.53. Menos
igniciones significa más tiempo entre incendios, significa un bosque más denso
cuando por fin llega uno.

*Respuesta a la pregunta 3, y son dos respuestas.* El área total quemada a lo
largo de un siglo apenas cambia — esa es la ley de conservación. **Lo que cambia
es cómo se entrega**: como muchos incendios pequeños, o como uno que se lo lleva
todo. Esos son la misma integral y siglos muy distintos.

Y también son intervenciones distintas en el mundo real. Prevenir igniciones no
es el mismo acto que combatir un fuego ya empezado, y solo el primero mueve este
modelo.

**Una salvedad dicha en vez de enterrada.** En la última fila el fuego cubre el
98.6% de la red: esa medida está limitada por la caja, no por la física. Es
también la grieta por la que §11 llega.

### 10.3 Cuándo coinciden los dos métodos

Cubierto en [§8.3](#83-y-la-separación-de-escalas-temporales-la-fija-p). La
predicción — que convergen conforme el bosque crece más despacio — se sostuvo, y
su forma nítida fue la sorpresa: el parámetro que controla es $p$ y no $f/p$.

De ahí salió una segunda cosa que no estaba predicha en absoluto. **Por encima
de una tasa de crecimiento de aproximadamente 0.1 el fuego sincrónico nunca se
apaga.** El rebrote alimenta el frente más rápido de lo que este lo atraviesa,
así que no hay ningún tamaño de incendio que informar:

| $p$ | 0.005 | 0.02 | 0.05 | 0.1 |
|---|---|---|---|---|
| anillos hasta que muere | 4 | 50 | 49 | sigue ardiendo en 3000 |

El método lanza una excepción en lugar de devolver un número, porque un fuego
que nunca termina no tiene tamaño. La versión instantánea no puede tener esa
transición en absoluto, ya que nada crece mientras algo arde — así que es una
propiedad del *método*, que es la demostración más nítida posible de que
«cuánto dura un fuego» nunca fue un detalle.

---

## 11. Dónde el modelo deja de ser cierto

### 11.1 Puede que no sea crítico en absoluto

El titular, y no es una salvedad pequeña.

Este modelo es el ejemplo estándar de criticalidad autoorganizada. Durante una
década se citó su distribución de tamaños de incendio como una ley de potencias.
Después Grassberger (2002) y Pruessner y Jensen (2002) fueron a redes grandes y
encontraron que el escalado está **roto**: no hay un único régimen de ley de
potencias, y los ajustes sobre todo el rango describen una mezcla de un cuerpo
que no escala y un corte que es el borde de la caja.

[`fire-percolation`](https://github.com/FullFran/fire-percolation) reproduce eso
de forma independiente — el exponente ajustado se mueve 7.3 frente a un error
estándar combinado de 0.54 a lo largo de los tamaños de red, y a $L$ grande el
ajustador abandona el cuerpo por completo y aterriza en el corte de tamaño
finito. Su `FINDINGS.md` vale la pena leerlo como relato de cómo un ajuste
plausible puede no significar nada.

La posición honesta: el *mecanismo* de aquí es real y vale la pena entenderlo —
crecimiento y quema se equilibran en un umbral que nadie fijó. La afirmación de
que esto produce un escalado crítico limpio no está establecida, y la versión
introductoria de la historia es más ordenada que la evidencia.

### 11.2 El resto de la lista

| Límite | Qué ocurre en realidad | Esta entrada |
|---|---|---|
| Redes grandes | Los impactos por paso crecen como $fL^2$; la separación de escalas temporales falla en silencio | guardado solo sobre $f<p$, y §8.2 dice por qué eso no basta |
| Crecimiento por encima de $p\approx0.1$, sincrónico | El fuego se vuelve endémico y nunca termina | lanza una excepción |
| $f$ no muy por debajo de $p$ | Los dos métodos discrepan por un factor de siete | medido |
| Mayor incendio cerca de $L^2$ | Limitado por la caja, no por la física | dicho |
| La supresión como política | El modelo sostiene la afirmación de la tasa de ignición y no la de apagarlos | medido, en las dos direcciones |
| Red cuadrada, cuatro vecinos | $p_c$ es una propiedad de la red; los paisajes reales no son redes | no modelado |
| Viento, pendiente, humedad, especies | Todo el comportamiento del fuego | no modelado |
| Ignición humana | Se agrupa cerca de las carreteras; no es uniforme | no modelado |

---

## 12. Lo esencial

- **Tamaños de ley de potencias significa que no hay tamaño típico.** «El
  incendio medio» es un número que puedes calcular y no puedes usar.
- **Ajustar un sistema a su punto crítico no explica nada.** El contenido está
  en un sistema que *llega* ahí, porque el crecimiento empuja hacia arriba y la
  quema empuja hacia abajo y el umbral es donde se equilibran.
- **$p_c = 0.5927460$**, sin forma cerrada, que es lo que la convierte en una
  comprobación externa real.
- **Un fuego quema un clúster, no un radio**, y un clúster es una línea de
  código aplicada hasta que nada nuevo se prende.
- **El estado estacionario es una ley de conservación**: lo que crece tiene que
  arder. Cualquier intervención que no cambie ni el crecimiento ni cuándo
  empiezan los fuegos no puede cambiar el total.
- **Suprimir incendios no acumula combustible. Prevenir igniciones sí.** La
  misma integral, una distribución muy distinta, y actos distintos en el mundo
  real.
- **La separación de escalas temporales la fija la tasa de crecimiento, no
  $f/p$** — lo que importa es cuánto bosque aparece durante un fuego.
- **Por encima de una tasa de crecimiento de ~0.1 el fuego nunca se apaga.** Una
  transición que pertenece al método, no a la red.
- **Los impactos por paso crecen con el área**, así que una comprobación de
  régimen sin $L$ dentro no puede ver el régimen fallando.
- **El ejemplo de manual de la criticalidad autoorganizada no es, con la
  evidencia actual, limpiamente crítico.** Eso lo hicieron redes más grandes, no
  un análisis más listo.

---

## 13. Preguntas abiertas

- **¿Por qué a $p_c$ no le importan los detalles?** Porque el engrosado de
  escala de la red hace fluir los parámetros hasta un punto fijo, y todo lo que
  no sobrevive al zoom nunca importó. Un bloque $2\times2$ da
  $R(p) = 2p^2 - p^4$, y $R(p^{\ast}) = p^{\ast}$ factoriza a
  $p^{\ast} = (\sqrt5-1)/2 = 0.618$ — la razón áurea, a un 4% de la verdad,
  salida de una cuártica. El exponente del mismo cálculo se desvía un 23%, y ver
  eso converger conforme crece el bloque es la siguiente entrada.
- **¿Es crítico o no?** Zanjar eso requiere escalado de tamaño finito hecho
  bien, que es para lo que está `fire-percolation` y lo que §11.1 dice que no
  está zanjado.
- **¿Qué hace el montón de arena que esto no hace?** Bak–Tang–Wiesenfeld es un
  modelo distinto con una ley de conservación que a este le falta, y se sospecha
  que la diferencia importa para si la criticalidad es genuina.
- **¿Siguen esto los incendios reales, o algo distinto que también da leyes de
  potencias?** Malamud dice que la estadística coincide; una distribución que
  coincide es evidencia débil de un mecanismo que coincide.
- **¿Qué hace añadir un cortafuegos?** Una intervención estructurada en vez de
  un umbral de tamaño, y es la única pregunta de política que esta entrada
  podría responder y no responde.

---

## 14. Referencias

**Criticalidad autoorganizada**

- **Bak, P., Tang, C. & Wiesenfeld, K.** *Self-organized criticality: an
  explanation of 1/f noise.* Physical Review Letters **59**, 381 (1987).
  [enlace](https://doi.org/10.1103/PhysRevLett.59.381)
- **Bak, P.** *How Nature Works* (1996). El alegato, a todo volumen.
- **Drossel, B. & Schwabl, F.** *Self-organized critical forest-fire model.*
  Physical Review Letters **69**, 1629 (1992).
  [enlace](https://link.aps.org/doi/10.1103/PhysRevLett.69.1629)

**Y el caso en contra**

- **Grassberger, P.** *Critical behaviour of the Drossel-Schwabl forest fire
  model.* New Journal of Physics **4**, 17 (2002).
  [enlace](https://arxiv.org/abs/cond-mat/0202022)
- **Pruessner, G. & Jensen, H. J.** *Broken scaling in the forest-fire model.*
  Physical Review E **65**, 056707 (2002).
  [enlace](https://arxiv.org/abs/cond-mat/0201306)

**Percolación**

- **Stauffer, D. & Aharony, A.** *Introduction to Percolation Theory*, 2ª ed.
  De donde salen $p_c$, los exponentes y la renormalización en espacio real.
- **Newman, M. E. J. & Ziff, R. M.** *Efficient Monte Carlo algorithm and
  high-precision results for percolation.* Physical Review Letters **85**, 4104
  (2000). [enlace](https://arxiv.org/abs/cond-mat/0005264)

**Incendios reales**

- **Malamud, B. D., Morein, G. & Turcotte, D. L.** *Forest fires: an example of
  self-organized critical behavior.* Science **281**, 1840–1842 (1998).
  [enlace](https://www.science.org/doi/10.1126/science.281.5384.1840)

---

*Código: [`../lattice.py`](../lattice.py) y [`../methods/`](../methods/) ·
Entrada: [`../README.md`](../README.md) · Arquitectura del repositorio:
[`docs/architecture.md`](../../docs/architecture.md)*
