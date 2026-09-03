<!-- translated-from: 56b468008210 -->

# Difusión

Destruye una distribución con ruido hasta que no quede nada, aprende por el
camino la pendiente del logaritmo de la densidad, y vuelve a subir por ella.
El proceso inverso necesita una cosa que el directo tira — la score — y la
pregunta honesta es cómo sabrías nunca si una score aprendida es correcta.
Así que el objetivo aquí es una mezcla de gaussianas, la única familia cuya
score con ruido sigue siendo exactamente calculable. 505 líneas de núcleo.

| | |
|---|---|
| **Nivel** | L1 derivar · L2 implementar · L3 experimentar |
| **Dominio** | [`process.py`](process.py) — 233 líneas, sin ningún muestreador dentro |
| **Métodos** | [`ancestral.py`](methods/ancestral.py) 34 · [`probability_flow.py`](methods/probability_flow.py) 44 |
| **Tests** | 96, repartidos entre dominio, contrato y dónde divergen los métodos |
| **Sigue a** | [`sampling/`](../sampling/), que es el mismo paseo con la energía dada en vez de aprendida |

## Disposición

```
docs/process.md       the derivation, from the phenomenon down
docs/figures/         the figures it argues from
process.py            the domain: noising, and the exact score it implies
methods/
  ancestral.py        sample the reverse transition
  probability_flow.py integrate the flow with the same marginals
solve.py              the schedule, the loop, and the verdict
experiments/
  collapse.py         what noising destroys, and what the score still knows
  step_budget.py      where the two methods separate, and where they stop
  trajectories.py     the flow is the quantile transport map
tests/
  test_process.py     the score, three independent ways
  test_methods.py     the contract: the samples are draws from the target
  test_methods_differ.py  the one term that separates them
```

## 1. Qué problema resuelve

Tienes muestras de una distribución y ninguna fórmula para ella. No hay
densidad para las fotografías, ni energía que nadie escribiera. Ese es el
espejo exacto de [`sampling/`](../sampling/), donde la energía está dada y el
normalizador es inalcanzable: aquí lo dado son las muestras y lo inalcanzable
es la densidad.

Ambos se resuelven con el mismo objeto. El muestreo necesita cocientes de
probabilidades; la difusión necesita el gradiente de un logaritmo de
probabilidad. Ninguno de los dos puede ver una constante de normalización,
porque una constante se cancela en un cociente y desaparece bajo una
derivada.

El truco consiste en hacer alcanzable la distribución difícil desde una
fácil. Añade ruido gaussiano hasta que lo que queda sea una normal estándar,
que sabes muestrear trivialmente, y luego recorre el proceso al revés.
Invertirlo necesita

$$\nabla_x \log q_t(x),$$

la score de la densidad *con ruido* en cada punto del camino. Aprende eso y
podrás llevar el ruido de vuelta a los datos.

Que es donde llega la pregunta por la que existe esta entrada: si la score es
la salida de una red, ¿contra qué se la está comparando?

## 2. Las ecuaciones

El proceso directo, en la forma que importa — no un paso, sino el salto desde
los datos a cualquier instante de una vez:

$$x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1 - \bar\alpha_t}\, \varepsilon,
\qquad \varepsilon \sim \mathcal{N}(0, I)$$

Un único escalar $\bar\alpha_t \in (0, 1]$ carga con todo el tiempo: la
fracción de señal que todavía queda. Nada de lo que sigue necesita $t$ en sí.

**La mezcla sigue siendo una mezcla.** Una gaussiana convolucionada con
una gaussiana es una gaussiana, así que
si $p_0 = \sum_k w_k \mathcal{N}(\mu_k, \Sigma_k)$ entonces

$$q_t = \sum_k w_k \mathcal{N}\!\left(\sqrt{\bar\alpha}\,\mu_k,\;
S_k\right), \qquad S_k = \bar\alpha \Sigma_k + (1 - \bar\alpha) I.$$

Las medias encogen hacia el origen, las covarianzas se inflan hacia la
identidad, y los pesos no se mueven nunca: el ruido no cambia de qué
componente vino una muestra, solo lo bien que puedes distinguirlo.

**La score, en forma cerrada.** Derivando el logaritmo de esa suma:

$$\nabla \log q_t(x) = -\sum_k r_k(x)\, S_k^{-1}\left(x - \sqrt{\bar\alpha}\,
\mu_k\right), \qquad r_k(x) = \operatorname{softmax}_k\big[\log w_k + \log
\mathcal{N}(x; \sqrt{\bar\alpha}\mu_k, S_k)\big].$$

Un promedio, ponderado por responsabilidades, de hacia dónde tiraría cada
componente. Cuando $\bar\alpha \to 0$ las responsabilidades se aplanan, todos
los tirones coinciden, y la score colapsa a $-x$: al final del proceso
directo no queda nada que invertir, que es precisamente por qué el proceso
inverso puede arrancar desde ruido puro.

**La fórmula de Tweedie**, que no va de mezclas en absoluto:

$$\mathbb{E}[x_0 \mid x_t] = \frac{x_t + (1 - \bar\alpha)\nabla \log
q_t(x_t)}{\sqrt{\bar\alpha}}, \qquad \nabla \log q_t(x_t) = -\frac{\mathbb{E}
[\varepsilon \mid x_t]}{\sqrt{1 - \bar\alpha}}.$$

Vale para cualquier $p_0$ bajo ruido gaussiano. Esa es la razón de que una
red entrenada para predecir el ruido de una imagen corrompida sea un
estimador de la score sin que nadie lo decidiera, y la razón de que quitar
ruido y generar resultaran ser un mismo asunto.

## 3. Qué implementé

Dos caminos de vuelta, que difieren en un término.

**Ancestral** muestrea la transición inversa. La $q(x_{t-1} \mid x_t)$ exacta
no es gaussiana — es una gaussiana mezclada sobre todo lo que $x_0$ podría
haber sido — pero para un paso suficientemente pequeño se le parece:

$$x_{t-1} = \frac{x_t + (1 - \alpha_t)\,\nabla \log q_t}{\sqrt{\alpha_t}} +
\sigma_t z, \qquad \alpha_t = \frac{\bar\alpha_t}{\bar\alpha_{t-1}}.$$

**Flujo de probabilidad** integra la pareja determinista de esa ecuación
estocástica: un proceso distinto con la misma densidad marginal en todo
instante, que es la única propiedad que se le pide a un muestreador:

$$x_{t-1} = \sqrt{\bar\alpha_{t-1}}\,\hat x_0 + \sqrt{1 - \bar\alpha_{t-1}}\,
\hat\varepsilon.$$

A ninguno de los dos métodos se le entrega el objetivo. Ambos reciben una
score ya evaluada en el punto actual, que es la costura sobre la que se
construye la entrada: `solve.sample` toma un `score_fn`, y cambiar la score
exacta por una aprendida no cambia ni una línea de `methods/`.

## 4. Qué verifiqué

| Afirmación | Dónde |
|---|---|
| **La score coincide con diferencias centradas del logaritmo de la densidad** — 15 combinaciones de objetivo y $\bar\alpha$, peor caso $1.7 \times 10^{-9}$ | dominio |
| **Tweedie coincide con el condicionamiento gaussiano** — una derivación no relacionada de $\mathbb{E}[x_0 \mid x_t]$, sin compartir una línea, peor caso $2.1\times10^{-14}$ | dominio |
| **$\nabla \log q_t = -\mathbb{E}[\varepsilon\mid x_t]/\sqrt{1-\bar\alpha}$** hasta precisión de máquina | dominio |
| **La score olvida el objetivo según muere la señal** — en $\bar\alpha = 10^{-6}$ vale $-x$ | dominio |
| **$q_t$ integra a 1** sobre una malla | dominio |
| **Las muestras son extracciones del objetivo** — MMD² insesgada dentro de un suelo medido, ambos métodos, los tres objetivos | contrato |
| **Se visitan las dos modas** — 50/50 en el objetivo simétrico, no 100/0 | contrato |
| **Una score equivocada da muestras equivocadas** — divídela por dos y la discrepancia sube | contrato |
| **El flujo es una función de su ruido inicial** — idéntico bit a bit, no con tolerancia | divergencia |
| **Ancestral sigue sorteando después del arranque** | divergencia |
| **Ninguno sobrevive a tres pasos** — un orden de magnitud fuera del suelo | divergencia |
| **El flujo va por delante a cinco pasos** — 0.6–0.9× en MMD², por encima del suelo | divergencia |

El umbral está medido, no elegido. Dos conjuntos independientes de muestras
*exactas* discrepan en cierta cantidad; ese es el suelo, estimado sobre cinco
pares y tomado por arriba, y a un muestreador se le permite exactamente eso.

Ese detalle no es decoración. La primera versión estimaba el suelo a partir
de un solo par, y el test de contrato entonces pasaba a 100 pasos, fallaba a
200 y volvía a pasar a 400 en el mismo objetivo: una moneda al aire
disfrazada de umbral.

### El experimento

**[`step_budget.py`](experiments/step_budget.py)** — dónde se separan los dos
métodos. La afirmación recibida es que el muestreador determinista necesita
muchos menos pasos, y suele defenderse con una score aprendida y una métrica
perceptual. Sobrevive al cambio a una score exacta y una métrica
distribucional, pero solo dentro de una ventana:

```
=== arc (noise floor 8.8e-03) ===
 steps     ancestral     prob-flow    ratio  ahead
     5      3.09e-02      1.70e-02     0.6x  prob-flow
     8      1.12e-02      7.06e-03     0.6x  prob-flow
    12      4.35e-03      3.85e-03       --  both at floor
    50      2.59e-04      1.46e-03       --  both at floor
```

Pasados unos doce pasos no queda nada que ordenar. **Una versión anterior de
este fichero los ordenó igualmente** y reportó que ancestral iba por delante
hasta 5.6× a cincuenta pasos. Ambos números eran indistinguibles de cero, y
dividir uno por otro medía cuál de los dos ruidos era mayor. El suelo ahora
se imprime junto a la tabla y el cociente se retiene en cuanto los dos caen
por debajo.

## 5. Qué dejé fuera deliberadamente

**La score aprendida.** Esta es la omisión que importa, y es el sentido de la
costura más que un accidente de alcance. Todo lo de aquí corre sobre una
score derivada, así que lo que la entrada establece es el solucionario: un
objetivo con score exacta, una métrica con suelo medido, y un muestreador que
toma la score como argumento. Aprenderla es la entrada siguiente, y podrá
calificarse en vez de admirarse.

**Datos reales.** Una mezcla de gaussianas no es interesante. Es el caso que
tiene respuesta, y todo el diseño sale de querer una.

**Tiempo continuo.** La EDE y su EDO de flujo de probabilidad son el
enunciado general; esto es su discretización sobre una malla fija, que es lo
que son DDPM y DDIM.

**Guía sin clasificador, espacios latentes, condicionamiento, predicción de
$v$.** Todos son modificaciones de la score, y ninguno cambia lo que aquí se
verifica.

**Varianzas aprendidas.** $\sigma_t$ sale del calendario.

## Dónde deja de ser correcto

El núcleo son 505 líneas, justo por encima de la banda de 100–500 de la regla
4. Se declara en vez de redondearse a la baja.

$\bar\alpha$ se rechaza por debajo de $10^{-8}$: en cero exacto la mezcla ha
olvidado de qué componente vino, y el softmax es sobre logits idénticos. Los
calendarios paran en $10^{-4}$.

El suelo de la MMD es función del tamaño de muestra. Comparar ejecuciones con
distinto `draws` compara dos umbrales distintos, que es por qué el
experimento lo mantiene fijo.

`bimodal` es demasiado fácil para ordenar métodos: ambos se sientan en el
suelo desde unos ocho pasos, y la comparación allí reporta ruido. Los
objetivos anisótropos son los que separan algo.

## Ejecútalo

```bash
uv run pytest diffusion
uv run python diffusion/experiments/step_budget.py
```

```python
import solve
run = solve.sample(target="arc", method="probability-flow", steps=50)
run.within_noise          # is it a draw from the target, or only nearly
```

## Qué prepara esto

[`sampling/`](../sampling/) recorre una energía que alguien escribió. Esto
recorre una que no escribió nadie. El paso que queda es dejar de derivar la
score y aprenderla — los gradientes para eso son [`mlp/`](../mlp/) — momento
en el que cada número de la sección 4 se convierte en una nota en vez de una
comprobación.
