# Machine learning aplicado a trading — técnicas de López de Prado, verificadas en fuente primaria

Investigación de agosto de 2026. Diego compartió un resumen (generado por otra IA a partir de PDFs de origen no autorizado) de *Advances in Financial Machine Learning* con varios conceptos de peso. No guardamos ese resumen tal cual — cada técnica de acá se re-investigó y confirmó contra la fuente primaria real y gratuita (SSRN, Wikipedia, documentación de librerías open-source que implementan estas técnicas), no contra el resumen de segunda mano. López de Prado publica la mayoría de su trabajo académico gratis y legal en [SSRN](https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=434076) — ya estaba linkeado en `biblioteca/README.md`.

**Por qué importa esto para Jarvis:** son técnicas específicas para el problema que ya identificamos como el más peligroso de todo el proyecto — el overfitting (70%→38,5% WR del XAU viejo). No son solo teoría de ML genérica, atacan directamente ese problema con herramientas más finas que "walk-forward simple".

---

## 1. El método de la triple barrera (Triple-Barrier Method)

**El problema que resuelve:** cuando se etiqueta una operación como "ganadora" o "perdedora" para entrenar un modelo (o para evaluar una estrategia con reglas fijas), el método ingenuo es mirar el retorno a un horizonte de tiempo fijo (ej. "¿subió a los 60 minutos?"). Eso ignora que en el camino el precio pudo haber tocado un stop-loss mucho antes, o un take-profit — la etiqueta queda desconectada de cómo se opera en la realidad.

**Cómo funciona:** cada operación se etiqueta según cuál de tres barreras toca primero:
- Barrera superior — take-profit
- Barrera inferior — stop-loss
- Barrera vertical — límite de tiempo (si no tocó ninguna de las otras dos antes)

Es un etiquetado dinámico, no un retorno a horizonte fijo — refleja cómo se gestiona una posición real (con stop/target), no una ficción académica de "comprar y esperar N barras".

**Aplicable a Jarvis:** nuestras estrategias actuales (EMA cross, RSI, Bollinger+VWAP) usan señales de entrada/salida por cruce de indicador, no por barrera de precio explícita — este método daría una forma más realista de medir "cuánto tardó y por qué salió" cada operación en los backtests que ya corrimos.

Fuentes: [Wikipedia — Purged cross-validation (menciona el contexto del método)](https://en.wikipedia.org/wiki/Purged_cross-validation) · [Hudson & Thames — Does Meta Labeling Add to Signal Efficacy? (triple-barrier + meta-labeling)](https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy-triple-barrier-method/) · [mlfinpy — Data Labelling docs (implementación open-source)](https://mlfinpy.readthedocs.io/en/latest/Labelling.html)

## 2. Meta-labeling — separar "hacia dónde" de "cuánto apostar"

**La idea central:** un modelo primario (puede ser tan simple como nuestro cruce de EMA actual) decide la *dirección* (largo/corto). Un segundo modelo separado — el meta-etiquetador — no vuelve a decidir la dirección, decide si **actuar o no** sobre esa señal y con qué tamaño.

**Por qué es relevante para Jarvis específicamente:** es la misma arquitectura que ya veníamos armando por otro camino — el "módulo de riesgo separado de la señal" que propone `ANALISIS_ESTRATEGICO_IA_FINANCIERA.md` y que confirma Ivan Scherman en `traders_referentes.md`. Meta-labeling es, en el fondo, una formalización estadística de exactamente esa idea: la señal técnica decide la dirección, un segundo juicio (humano o modelo) decide si vale la pena tomarla.

Fuente: [Hudson & Thames — Meta Labeling](https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy-triple-barrier-method/)

## 3. Diferenciación fraccional — el dilema estacionariedad vs. memoria

**El problema:** para que cualquier análisis estadístico riguroso funcione (incluido el ADF que planeamos correr sobre XAU), la serie necesita ser estacionaria. La forma estándar de lograrlo es diferenciar (tomar retornos en vez de precio: `precio_t − precio_t-1`) — pero diferenciar con un entero completo (d=1) **borra toda la memoria de largo plazo** de la serie, y esa memoria es justamente lo que un modelo predictivo necesita para tener algo que aprender.

**La solución:** diferenciar con un parámetro fraccional (d entre 0 y 1, no necesariamente 1 entero) — el mínimo grado de diferenciación necesario para lograr estacionariedad, preservando la mayor memoria histórica posible. Es un punto intermedio entre "serie cruda con memoria pero no estacionaria" y "retornos estacionarios pero sin memoria".

**Aplicable a Jarvis:** directamente relevante para el análisis exploratorio pendiente de XAU — en vez de solo correr ADF sobre precio crudo vs. retornos (todo o nada), esto da un método para encontrar el punto óptimo entre ambos extremos.

Fuentes: [Hudson & Thames — Fractional Differentiation](https://hudsonthames.org/fractional-differentiation/) · [mlfinlab — Fractionally Differentiated Features (docs)](https://www.mlfinlab.com/en/latest/feature_engineering/frac_diff.html)

## 4. Validación cruzada purgada (Purged K-Fold CV) con embargo

**El problema:** el K-fold cruzado estándar de ML asume que las observaciones son independientes entre sí. En series financieras no lo son — las etiquetas de operaciones cercanas en el tiempo se solapan (ej. dos operaciones que abrieron con una hora de diferencia comparten buena parte de su horizonte de evaluación), lo que filtra información del set de entrenamiento al de test y produce resultados artificialmente buenos.

**La solución (desarrollada por López de Prado en 2017, en Guggenheim Partners y Cornell):**
- **Purga (purging)**: eliminar del set de entrenamiento cualquier observación cuya etiqueta se solape en el tiempo con las del set de test.
- **Embargo**: además de purgar, excluir un margen de observaciones inmediatamente posteriores al set de test, para prevenir fuga por autocorrelación remanente.

**Aplicable a Jarvis:** es una versión más rigurosa que el walk-forward simple que venimos usando (ventanas fijas consecutivas) — el walk-forward evita mirar al futuro, pero no necesariamente maneja el solapamiento de etiquetas dentro de cada ventana. Para cuando pasemos a probar algo con ML real (no solo reglas fijas), esto reemplaza al walk-forward básico.

Fuente: [Wikipedia — Purged cross-validation](https://en.wikipedia.org/wiki/Purged_cross-validation)

## 5. Hierarchical Risk Parity (HRP) — la alternativa a Markowitz

**El problema con Markowitz (optimización media-varianza clásica):** necesita invertir una matriz de covarianza estimada con datos históricos — cuando los activos están muy correlacionados (matriz casi singular) o hay pocos datos relativos a la cantidad de activos, esa inversión se vuelve inestable: pequeños errores de estimación in-sample generan carteras muy distintas y con desempeño desastroso out-of-sample. Se lo conoce como "la maldición de Markowitz": más correlación → más necesidad teórica de diversificar, pero también más inestabilidad numérica del optimizador.

**La solución (López de Prado, 2016, *Building Diversified Portfolios that Perform Well Out-of-Sample*):** HRP usa teoría de grafos y clustering jerárquico sobre la matriz de covarianza en vez de invertirla directamente — no requiere que la matriz sea invertible, y en pruebas de Monte Carlo da menor varianza out-of-sample que los optimizadores cuadráticos clásicos, incluso cuando esos optimizadores tienen la varianza mínima como objetivo explícito.

**Aplicable a Jarvis:** es la respuesta directa al gap de "sizing sin normalizar por volatilidad" que ya identificamos en la auditoría del 13/08 — en vez de normalizar posición por posición a mano, HRP da un método formal para asignar capital entre los activos del portfolio (XAU/EUR/BTC/SPY/TLT) basado en su estructura de correlación real, sin el problema de inestabilidad de Markowitz.

Fuentes: [SSRN — Building Diversified Portfolios that Perform Well Out-of-Sample (López de Prado, 2016)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2708678) · [Wikipedia — Hierarchical Risk Parity](https://en.wikipedia.org/wiki/Hierarchical_Risk_Parity)

## 6. El paradigma de la Meta-Estrategia (por qué el ML financiero individual fracasa)

**El problema (el "paradigma de Sísifo", como lo llama López de Prado):** las firmas tradicionales contratan investigadores para que, cada uno por su cuenta, produzcan una estrategia ganadora en pocos meses. Casi siempre termina en un backtest sobreajustado — es pedirle a una sola persona que descubra sola algo que en la práctica requiere un equipo grande trabajando en conjunto.

**La alternativa (paradigma de Meta-Estrategia):** estructurar la investigación como una línea de producción con roles separados y auditados de forma independiente — curación de datos, extracción de features, formulación de la estrategia, backtesting (con cálculo independiente de probabilidad de sobreajuste), despliegue, y supervisión del ciclo de vida del modelo en producción. Cada eslabón se mide por separado, no solo el resultado final.

**Aplicable a Jarvis:** no vamos a replicar una estructura de firma institucional, pero el principio de fondo aplica igual — es la misma razón por la que separamos "clasificar el activo" (Etapa 1) de "elegir estrategia" (Etapa 2) de "validar" (Etapa 3) de "gestionar riesgo" (Etapa 4) en `como_empezar.md`, en vez de que una sola persona (o un solo backtest) decida todo de una.

Fuentes: [The 10 Reasons Most Machine Learning Funds Fail — López de Prado (Journal of Portfolio Management, versión pública en SlideShare)](https://www.slideshare.net/MehdiMeraiMSc/3-the-7-reasons-most-machine-learning-funds-fail-marcos-lopez-de-prado) · [The Myth and Reality of Financial Machine Learning — SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3120557)

## 7. Barras de información — otra forma de muestrear precio, no solo por tiempo

**El problema con las barras de tiempo (M1, M5, diarias — lo que usamos hoy):** el mercado no procesa información al mismo ritmo todo el día. Una barra de tiempo fija sobre-muestrea las horas tranquilas y sub-muestrea los momentos de alta actividad — la serie resultante tiene peores propiedades estadísticas (autocorrelación, heterocedasticidad, retornos lejos de la normalidad) que dificultan cualquier análisis riguroso encima.

**La alternativa:** muestrear una barra nueva cada vez que se cumple un umbral de *actividad de mercado*, no de tiempo — barras de ticks (cada N operaciones), barras de volumen, barras de dólares (cada vez que se intercambia cierto monto), o barras de desequilibrio (imbalance — cuando el flujo comprador/vendedor se desvía de lo esperado, detectando un cambio de régimen más temprano). Producen series con propiedades estadísticas más cercanas a lo que los modelos y tests estadísticos asumen.

**Aplicable a Jarvis:** es una alternativa real a nuestro dataset M1 actual — no reemplaza lo ya descargado, pero es una forma legítima de re-muestrear los mismos ticks crudos que ya bajamos de Dukascopy (tenemos el tick a tick, solo lo agregamos a M1 por convención) si el análisis exploratorio muestra que M1 tiene demasiado ruido en horas tranquilas.

Fuentes: [mlfinlab/mlfinpy — documentación de barras de información (open-source)](https://mlfinpy.readthedocs.io/en/doc-staging/_modules/mlfinpy/data_structure/imbalance_bars.html) · [Alpaca — Alternative Bars, Parte I](https://alpaca.markets/learn/alternative-bars-01)

## 8. La Primera Ley del Backtesting + importancia de features (MDA/MDI)

**La frase, confirmada en la cuenta pública real del propio López de Prado** (no en el resumen de segunda mano — la fuente es su propio posteo): *"Backtesting is not a research tool. Feature importance is."* — el backtest no debe usarse para buscar una estrategia probando variantes hasta que "se vea bien" (es exactamente el data snooping que venimos evitando toda la sesión); debe usarse solo como control de sanidad al final, después de construir una teoría con evidencia de importancia de variables.

**Dos formas de medir esa importancia:**
- **MDI (Mean Decrease Impurity)**: rápida, específica de modelos de árbol (random forest) — mide cuánto reduce cada variable la "impureza" de los nodos. Rápida pero in-sample (optimista) y sesgada hacia variables con muchas categorías posibles.
- **MDA (Mean Decrease Accuracy)**: aplicable a cualquier modelo — se mide el desempeño out-of-sample, se desordena (shuffle) una variable a la vez, y se ve cuánto cae el desempeño. Más lenta pero más honesta porque es out-of-sample.

**Aplicable a Jarvis:** confirma por qué insistimos tanto en walk-forward en vez de solo mirar el resultado del backtest — es literalmente la misma filosofía que López de Prado formaliza con esta "primera ley", desde una fuente completamente distinta a la nuestra.

Fuentes: [López de Prado — posteo público original de la frase (X/Twitter, cuenta verificada del autor)](https://x.com/lopezdeprado/status/1138716396248915968) · [mlfinlab — Feature Importance docs](https://random-docs.readthedocs.io/en/latest/implementations/feature_importance.html)

## 9. Aprendizaje por refuerzo (RL) aplicado a ejecución — territorio distinto al resto

Todo lo de arriba es sobre *qué operar y cuándo*. El aprendizaje por refuerzo entra en un problema distinto: *cómo ejecutar* una orden grande dividiéndola de forma óptima contra el libro de órdenes en vivo — un agente aprende, por prueba y error contra un simulador del mercado, a fraccionar órdenes para minimizar el costo contra un benchmark (ej. VWAP) sin tener que modelar a mano cada situación posible del libro.

**Aplicable a Jarvis:** es la versión moderna/ML del problema que ya documentamos con Almgren-Chriss en `brokers_ejecucion.md` (mismo problema — minimizar costo de ejecución — dos enfoques distintos, uno matemático clásico de 2000, este basado en RL). No es territorio urgente — aplica recién en la etapa de ejecución real, muy lejos todavía.

Fuentes: [Reinforcement Learning for Trade Execution with Market and Limit Orders — arXiv 2507.06345](https://arxiv.org/pdf/2507.06345) · [Optimal Execution with Reinforcement Learning — arXiv 2411.06389](https://arxiv.org/abs/2411.06389)

---

## Dónde encaja todo esto en el camino ya definido (`como_empezar.md`)

Ninguna de estas técnicas es para usar ahora — son para la Etapa 3-4 del roadmap (backtesting riguroso + gestión de riesgo), después de clasificar XAU y elegir familia de estrategia. Quedan documentadas acá para no tener que reinvestigarlas cuando lleguemos a esa etapa. La única que sí tiene aplicación inmediata es la diferenciación fraccional, porque es una herramienta directamente del "explorar los datos crudos" que es el próximo paso pendiente.
