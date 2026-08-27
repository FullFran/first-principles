<!-- translated-from: 3212f9b8a42a -->

# Separar la física del cálculo numérico

> Las ecuaciones son el invariante. El algoritmo es una elección. Ponlos en
> archivos distintos y haz que la flecha apunte en un solo sentido.

Esta es la arquitectura que sigue cada entrada de este repositorio. Está
escrita porque sobrevivió al contacto con una reescritura real — y porque,
según resulta, no es original. La mitad de la ciencia computacional ya trabaja
así bajo otros nombres, y vale la pena leer el [trabajo previo](#trabajo-previo).

## La regla

```
methods/ imports the domain.        The domain imports nobody.
```

Una flecha, sin excepciones. Todo lo que sigue es una consecuencia.

## La forma

```
entry/
├── docs/            long-form derivation, when the entry earns one
├── physics.py       the domain: the equations and their invariants
├── methods/         one file per algorithm, each importing the domain
│   ├── method_a.py
│   └── method_b.py
├── solve.py         orchestration: validate, dispatch, convert
└── tests/
    ├── test_physics.py         domain laws, no solver involved
    ├── test_methods.py         the contract, run against every method
    └── test_methods_agree.py   the methods cross-checked
```

Un método recibe cantidades que el dominio ya calculó y devuelve el resultado
en bruto. Nunca vuelve a derivar física por su cuenta. Las entradas pequeñas
colapsan `methods/` en un solo archivo; lo que tiene que sobrevivir es la
flecha, no el número de carpetas.

## Por qué compensa: la prueba del intercambio

Reordenar archivos no compra nada por sí solo. Lo que sí compra algo es esto:

> **Intercambia el algoritmo. Toda ley física debe seguir cumpliéndose.**

Si se cumplen, has separado lo que hace la naturaleza de cómo elegiste
calcularlo. Si una se rompe, tenías física escondida dentro de tu cálculo
numérico y no lo sabías — que es el fallo real que esta arquitectura existe
para atrapar, y es invisible en un archivo monolítico.

El corolario es la prueba honesta de si entendiste el material siquiera.
Cualquiera puede implementar un algoritmo y reproducir una gráfica de
referencia. Conseguir que dos algoritmos sin relación coincidan hasta 1e-13
exige saber qué partes eran física.

## La frontera es una prueba, no una carpeta

Esta es la parte que la gente se salta. La estructura de directorios no impone
nada. Lo que hace real la frontera es que **todo método tiene que pasar la
misma suite**:

```python
# tests/test_methods.py
from methods import ALL as METHODS

pytestmark = pytest.mark.parametrize("method", sorted(METHODS))
```

Registra un algoritmo nuevo y hereda el contrato automáticamente. Un método
que asume en silencio algo físico fallará una ley que nunca mencionó.

Sin esto, `physics.py` y `methods/` son dos carpetas con una convención de
nombres entre ellas.

## Dónde va la línea

Los casos ambiguos son donde el patrón se gana el sueldo. La pregunta que
resuelve casi todos:

> **¿Cambiaría esto si eligiera otro algoritmo?** Si no, es dominio.

| Asunto | Lado | Por qué |
|---|---|---|
| Ecuaciones de gobierno, relaciones constitutivas | dominio | El enunciado sobre la naturaleza |
| Condiciones de contorno e iniciales | dominio | Parte del problema, no de la solución |
| Leyes de conservación, simetrías, invariantes | dominio | Ciertas sin importar cómo integres |
| Unidades y adimensionalización | dominio | Cambia las ecuaciones, no la aritmética |
| Cortes de rama fijados por causalidad o pasividad | dominio | Un requisito físico con ropa numérica |
| Validación de entradas admisibles | dominio | Pasividad, positividad, cotas termodinámicas |
| Discretización, esquema de integración, control de paso | método | Pura elección |
| Tolerancia de convergencia, topes de iteración | método | Presupuesto de aproximación |
| Guardas de desbordamiento, reordenación por estabilidad | método | Artefactos de la precisión finita |
| Distribución de propuesta en Monte Carlo | método | Cualquier propuesta ergódica funciona |
| Criterio de aceptación en Metropolis | dominio | *Es* la distribución de Boltzmann |
| Gráficas, barridos, salida a archivo | ninguno | Experimentos, fuera de ambos |

Ese último par es la ilustración más nítida. En Monte Carlo de Metropolis la
propuesta es libre y la razón de aceptación no — mover la regla de aceptación
dentro del muestreador es exactamente el error que esta disposición está
diseñada para hacer evidente.

### Ejemplos resueltos

| Entrada | Dominio | Métodos |
|---|---|---|
| Matriz de transferencia | Snell, Fresnel, fase, flujo de energía | producto de matrices · recursión de Rouard |
| Red de Hopfield | función de energía, regla de actualización | síncrono · asíncrono |
| DDPM | proceso directo/inverso, la pérdida | muestreador ancestral · DDIM |
| Modelo de Ising | hamiltoniano, peso de Boltzmann | Metropolis · clúster de Wolff |
| N cuerpos | fuerza gravitatoria, energía | velocity Verlet · RK4 · simpléctico |

La división es siempre la misma frase: **las ecuaciones, frente al algoritmo
que las discretiza.**

## Trabajo previo

La idea no es nueva, y fingir otra cosa sería justo lo contrario de aquello
para lo que existe este repositorio. Aparece en al menos cuatro literaturas
que en su mayoría no se citan entre sí.

**Separación de responsabilidades en computación científica.** El principio
general, enunciado del modo más directo en la literatura de traducción
teoría-software: el software debe separar la pregunta científica, las
ecuaciones, los métodos numéricos que las resuelven y la infraestructura de
debajo — y el modo de fallo habitual es que no lo hace.
([Theory-Software Translation, arXiv:1910.09902](https://arxiv.org/pdf/1910.09902) ·
[On the Role of Mathematical Abstractions for Scientific Computing](https://link.springer.com/chapter/10.1007/978-0-387-35407-1_9))

**FEniCS, Firedrake y UFL.** La versión de calidad industrial. UFL declara la
forma variacional en notación casi matemática — la física — mientras que un
compilador de formas y el runtime se encargan de la discretización y la
ejecución. El propio artículo de Firedrake presenta su contribución como «una
separación de responsabilidades más completa» entre analistas numéricos y
especialistas de la aplicación.
([Firedrake, arXiv:1501.01809](https://arxiv.org/abs/1501.01809) ·
[The FEniCS Project](https://www.siam.org/publications/siam-news/articles/the-fenics-project/))

**`scipy.integrate.solve_ivp`.** La versión que todo el mundo ya ha usado sin
ponerle nombre: le entregas la EDO (dominio) y eliges `method="RK45"`,
`"Radau"`, `"BDF"`, `"LSODA"` (algoritmo). `extensisq` lo extiende pasando un
`OdeSolver` propio — un puerto abierto en todo salvo en el vocabulario.
([SciPy docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) ·
[extensisq](https://pypi.org/project/extensisq/0.0.2/))

**Modelos de tiempo y clima.** LFRic separa el código científico de la capa de
paralelización y optimización para que la misma física sobreviva a un cambio
de hardware.
([LFRic, arXiv:1809.07267](https://arxiv.org/pdf/1809.07267))

Y la coincidencia más cercana, publicada en julio de 2026: un marco que
propone exactamente esta estratificación dominio-físico / método-numérico
**para la enseñanza de la física computacional**, con el argumento de que el
código monolítico esconde dónde termina el conocimiento del dominio y dónde
empieza la estrategia computacional.
([Physical Systems as Objects, arXiv:2607.03457](https://arxiv.org/pdf/2607.03457))

## La mitad de las pruebas también tiene nombre

La división no es solo estructural — es la epistemología estándar de la
ciencia computacional, donde las dos mitades se llaman verificación y
validación:

> **Verificación** — ¿estoy resolviendo bien las ecuaciones? (numérica)
> **Validación** — ¿estoy resolviendo las ecuaciones correctas? (física)

La formulación es de Roache, formalizada en ASME V&V 10 (mecánica de sólidos,
2006) y V&V 20 (CFD y transferencia de calor).
([Roache, *Verification and Validation in Computational Science and Engineering*](https://www.amazon.com/Verification-Validation-Computational-Science-Engineering/dp/0913478083) ·
[ASME V&V 10](https://www.asme.org/codes-standards/find-codes-standards/standard-for-verification-and-validation-in-computational-solid-mechanics) ·
[ASME V&V 20 overview](https://www.semanticscholar.org/paper/An-Overview-of-ASME-V&V-20:-Standard-for-and-in-and-Coleman/5a2b34af86de4fac220df0f697b1afbe8bc24340))

Que es todo el sentido de la división en archivos: `test_physics.py` y
`test_methods.py` son esa distinción convertida en estructura, de modo que un
fallo te dice cuál de las dos preguntas respondiste mal.

Otras dos técnicas de esa literatura encajan con lo que las entradas pequeñas
pueden permitirse de verdad:

- **Soluciones exactas y fabricadas.** MMS se describe como la técnica de
  verificación de código más rigurosa disponible; donde ya existe una forma
  cerrada, úsala directamente. En `tmm/` esas son los coeficientes de Fresnel,
  la fórmula de Airy para una sola capa y la transformación de admitancia de
  cuarto de onda.
  ([MMS for code verification](https://link.springer.com/chapter/10.1007/978-3-319-70766-2_12) ·
  [Exact solutions, in *Verification and Validation in Scientific Computing*](https://www.cambridge.org/core/books/abs/verification-and-validation-in-scientific-computing/exact-solutions/DFB030CD8A8334FA13DF3B2A627964E4))
- **Comparación código a código.** Contrastar implementaciones independientes —
  lo que hace `test_methods_agree.py`.

## Límites honestos

**Que dos métodos coincidan prueba consistencia, no corrección.** La
literatura de V&V es explícita en que una jerarquía estricta importa,
precisamente para no dejarse engañar por una coincidencia fortuita entre
implementaciones defectuosas. Los dos solvers de este repositorio importan el
mismo `physics.py`; una ecuación equivocada ahí sería reproducida
idénticamente por ambos, hasta 1e-13, con la suite entera en verde. Por eso
las pruebas del dominio contra formas cerradas pesan más que la prueba de
concordancia, y por eso la prueba de concordancia va la última y no la primera.

**Una abstracción con una sola implementación es especulación.** No construyas
`methods/` sobre la teoría de que quizá llegue un segundo algoritmo. En `tmm/`
el segundo se ganó con un defecto medido: la matriz de transferencia se
desborda a NaN pasadas unas 20 µm de metal y la recursión no. Hasta que
aparezca algo así, un solo archivo es la respuesta correcta.

**Las entradas autónomas no pueden compartir un proceso de pruebas.** Cada
entrada pone su propio directorio en `sys.path` para que `import solve`
funcione en cuanto copias la carpeta fuera — esa es la regla 6, y significa
que dos entradas definen los mismos nombres de módulo. En un mismo proceso
solo una de ellas puede ser `sys.modules["solve"]`, así que las pruebas de la
otra entrada importan a un desconocido. pytest se detiene en los *nombres de
archivo* de prueba duplicados con `import file mismatch`, que se lee como un
problema de caché obsoleta y no lo es; fuérzalo con `--import-mode=importlib`
y la recolección tiene éxito, fallan 184 pruebas, y la razón no aparece por
ninguna parte en la salida. Ningún modo de importación lo arregla, porque la
colisión está en `sys.path` y no en la recolección. El `conftest.py` raíz
rechaza una ejecución así y dice por qué, y `./run-tests` da a cada entrada su
propio proceso. Se cambió un comando por la propiedad de que una carpeta siga
funcionando después de copiarla a otro sitio, y para un repositorio que se lee
en lugar de instalarse ese intercambio está en el sentido correcto.

**La ceremonia es el modo de fallo.** Sin entidades, sin capa de casos de uso,
sin inyección de dependencias, sin un value object envolviendo un número
complejo. Este repositorio limita un núcleo a 500 líneas, y un mecanismo de
150 líneas repartido en doce archivos de interfaces ha perdido más de lo que
ganó. Toma la regla de dependencia; deja el aparato de astronauta de la
arquitectura.
