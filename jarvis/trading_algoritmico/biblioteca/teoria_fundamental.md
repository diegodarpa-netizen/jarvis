# Teoría fundamental del trading algorítmico — fuentes 100% gratuitas

Complementa `README.md` (los 5 libros de referencia). Esto cubre los pilares teóricos que no habíamos investigado a fondo en la sesión — todo de fuentes públicas y gratuitas (papers académicos, sitios educativos reconocidos).

---

## 1. Hipótesis de Mercados Eficientes (EMH) y por qué pueden existir "edges"

**La pregunta de fondo que hay que responder antes de programar cualquier estrategia: ¿por qué debería existir una ventaja explotable, para empezar?**

- La **Hipótesis de Mercados Eficientes** (Fama, 1970) dice que el precio ya refleja toda la información disponible — si fuera 100% cierta, ninguna estrategia sistemática debería funcionar de forma sostenida.
- **Las anomalías documentadas que contradicen la EMH pura**: efecto momentum, efecto "ganador-perdedor" (reversión de largo plazo), anomalías de calendario (efecto enero), la prima de riesgo accionario ("equity premium puzzle").
- **Las finanzas conductuales explican el "por qué"**: sesgos sistemáticos y repetibles en el comportamiento humano — exceso de confianza, comportamiento de manada, heurísticas de decisión — que generan los mismos patrones una y otra vez, no al azar.
- **La conclusión práctica, citada en la literatura**: la mayoría de estas anomalías se pueden explotar con estrategias relativamente simples — las ganancias no son "gratis" (hay riesgo), pero son rentables en relación a ese riesgo, incluso en horizontes largos.

**Por qué importa para nosotros:** cualquier estrategia que probemos debería poder explicar, en una frase, *qué sesgo humano o fricción de mercado está explotando*. Si no hay respuesta, es más señal de que estamos ante ruido sobreajustado (lo que ya vimos toda la sesión) que ante un edge real.

Sources: [Market efficiency, anomalies and behavioral finance — WJARR](https://wjarr.com/content/market-efficiency-anomalies-and-behavioral-finance-review-theories-and-empirical-evidence) · [Review on Efficiency and Anomalies in Stock Markets — MDPI](https://www.mdpi.com/2227-7099/8/1/20)

---

## 2. Microestructura de mercado — cómo funciona el "motor" por dentro

- **Spread bid-ask**: la diferencia entre el precio de compra y venta — refleja liquidez y es el costo de transacción real que ya modelamos hoy con comisiones.
- **Order book (libro de órdenes)**: las bolsas organizan las órdenes de compra y venta ranqueadas por precio — es la estructura de datos real detrás de cada "precio" que vemos.
- **Impacto de mercado**: una orden de mercado grande consume liquidez del libro y mueve el precio en contra de quien la ejecuta — el spread se ensancha momentáneamente y se recupera de a poco.
- **Desequilibrio de flujo de órdenes**: cuando hay más compradores activos que vendedores, el precio tiende a subir para atraer vendedores nuevos (y viceversa) — es la base de por qué el volumen/flujo predice movimientos de muy corto plazo.
- **El porqué teórico del spread — Glosten-Milgrom (paper seminal)**: el spread existe porque el que hace mercado (market maker) enfrenta traders informados con mejor información, y necesita ensanchar el spread para compensar esas pérdidas esperadas — es una prima de "selección adversa", no un capricho.

**Por qué importa:** explica por qué agregar comisión/fricción realista (lo que hicimos con XAU 1H) es tan importante — el spread y el impacto de mercado no son un detalle menor, son la razón estructural por la que estrategias de alta frecuencia son mucho más difíciles de lo que parecen en un backtest sin fricción.

Sources: [Market Microstructure — Hans R. Stoll](https://www.acsu.buffalo.edu/~keechung/MGF743/Readings/Hans%20Stoll,%202003,%20Market%20microstructure.pdf) · [Market Microstructure: Order Books & Execution — Brenndoerfer](https://mbrenndoerfer.com/writing/market-microstructure-order-book-mechanics)

---

## 3. Estadística de series de tiempo — el lenguaje matemático detrás de "tendencia" vs. "rango"

Esto es, literalmente, el **paso 1 (explorar los datos crudos)** del que hablamos ayer — las herramientas exactas para hacerlo con rigor, no a ojo.

- **Test de Dickey-Fuller Aumentado (ADF)**: mide si una serie tiene "raíz unitaria" — si la tiene, es un camino aleatorio (random walk) y NO revierte a la media. Si lo rechaza con un p-valor bajo, la serie es estacionaria (oscila alrededor de un promedio estable).
- **Exponente de Hurst**: mide la "memoria de largo plazo" de una serie —
  - H > 0,5 → la serie **tiende** (momentum, un movimiento persiste)
  - H = 0,5 → camino aleatorio puro (ninguna estrategia sistemática debería funcionar)
  - H < 0,5 → la serie **revierte a la media** (mean-reversion)
- **Cointegración**: dos activos individualmente pueden ser random walks, pero si están cointegrados, la *diferencia* entre ambos sí revierte a la media de forma estable — es la base matemática del stat-arb/pairs trading (la 4ª familia de estrategias que nunca llegamos a testear con código).
- **Vida media (half-life) de reversión**: una vez confirmado que una serie revierte, esto estima cuánto tarda en volver a su promedio — clave para calibrar el horizonte de una estrategia de mean-reversion.

**Por qué importa — conexión directa con el plan de ayer:** antes de tirarle a nuestro dataset de XAU (los 6 meses M1 que bajamos) cualquier estrategia prestada de un libro, correr ADF + Hurst sobre la serie real nos dice objetivamente si conviene buscar tendencia o reversión ahí — es exactamente el análisis exploratorio que quedó pendiente.

Sources: [Basics of Statistical Mean Reversion Testing — QuantStart](https://www.quantstart.com/articles/Basics-of-Statistical-Mean-Reversion-Testing/) · [Detecting trends and mean reversion with the Hurst exponent — Macrosynergy](https://macrosynergy.com/research/detecting-trends-and-mean-reversion-with-the-hurst-exponent/) · [Hurst: Mean Reversion of Time Series Data — Medium](https://medium.com/@jlabs/hurst-mean-reversion-of-time-series-data-08b608479656)

---

## 4. Criterio de Kelly y teoría de portfolio — cuánto apostar, no solo cuándo

- **Fórmula de Kelly**: `f* = (bp − q) / b` — calcula matemáticamente qué fracción del capital asignar a cada apuesta, dado el retorno esperado y la probabilidad de éxito. Maximiza el crecimiento de largo plazo *minimizando* el riesgo de ruina.
- **Apostar MÁS que Kelly garantiza la ruina eventual, casi con certeza matemática.** Apostar menos es más seguro cuando las probabilidades estimadas son inciertas (que siempre lo son en trading real) — por eso la práctica estándar es usar "medio Kelly" o menos.
- **Kelly vs. Markowitz (Teoría Moderna de Portafolio)**: Kelly dice cuánto apostarle a una sola apuesta para crecer óptimamente en el largo plazo; Markowitz dice cómo repartir capital ENTRE varios activos para el mejor retorno ajustado por riesgo, sin apalancamiento. Son complementarios, no competidores — y los portfolios de Kelly puros suelen quedar muy concentrados (más riesgosos en el corto plazo) que los de Markowitz.
- **El resultado de Samuelson**: un portfolio de Kelly es óptimo en el límite (muy largo plazo), pero NO en horizontes finitos — el apalancamiento alto que sugiere puede generar drawdowns grandes en el camino.

**Por qué importa:** es la matemática exacta detrás de la advertencia del "5%/semana" que ya dimos — apostar de más para llegar a un objetivo alto no es optimizar, es maximizar la probabilidad de arruinarse.

Sources: [Kelly Criterion Position Sizing — Astute Investors Calculus](https://astuteinvestorscalculus.com/the-kelly-criterion/) · [Portfolio Construction: Kelly vs Markowitz — Adrian Riv](https://www.adrianriv.com/blog/2024/01/15/kelly_vs_markowitz/)

---

## 5. Dónde seguir gratis, de forma continua — no solo esta sesión

| Recurso | Qué ofrece |
|---|---|
| **[QuantStart](https://www.quantstart.com/)** (Michael Halls-Moore) | Artículos técnicos gratuitos, de nivel serio, sobre estadística aplicada a trading — la fuente de varios de los conceptos de arriba |
| **[Quantra / QuantInsti](https://github.com/QuantInsti/Quantra-Courses)** | +50 cursos gratuitos, +700 Jupyter Notebooks, +1.000 ejercicios de código — el recurso estructurado más completo que encontramos |
| **[arXiv — sección q-fin](https://arxiv.org/list/q-fin/recent)** | Papers académicos de finanzas cuantitativas, de acceso abierto — la fuente primaria (no resúmenes de blog) |
| **[Zipline (código abierto)](https://github.com/quantopian/zipline)** | Motor de backtesting gratuito — ya evaluamos alternativas a esto en `frameworks_backtesting.md`, pero sigue siendo una referencia de código legible |

---

## Cómo se conecta esto con lo que ya hicimos

Todo lo de arriba es la explicación teórica de por qué funcionaron (o no) las cosas que ya probamos:
- El **walk-forward** que usamos todo el día = aplicación práctica de por qué la EMH y el sobreajuste importan.
- El **filtro de tendencia (Efficiency Ratio)** = versión práctica del Hurst exponent (ambos miden lo mismo: ¿tiende o revierte?).
- El **problema de SPY vs. buy-and-hold** = la teoría de Kelly explica por qué forzar apuestas simétricas (largo Y corto) contra un activo con deriva estructural fuerte es subóptimo.
- **Lo que todavía no probamos con código**: cointegración/pairs trading (stat-arb) — es la pieza que falta de las 4 familias del Módulo 3.
