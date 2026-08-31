# Traders y firmas de referencia en trading sistemático

Investigación de agosto de 2026. El objetivo de este archivo no es imitar la escala de estas firmas (son fondos institucionales con equipos de decenas de PhDs) sino extraer los **principios** que se repiten entre los que sostuvieron rentabilidad en el tiempo — y contrastarlos contra lo que ya sabemos que le falta a Jarvis (walk-forward, gestión de riesgo unificada).

## Ivan Scherman — SciTech Investments

El más directamente comparable a la escala de Jarvis: es un individuo (portfolio manager y CIO), no un fondo con cientos de empleados.

- **Track record:** ganó el World Cup Championship of Futures Trading® 2023 con ~500% de retorno en un año y un drawdown máximo de solo 26%. En 17 años liderando SciTech (hedge fund 100% algorítmico) logró un promedio de 23% anual neto para sus clientes, con 16 años positivos y solo 1 negativo. Reconocido por la SEC como Large Trader desde 2014.
- **Metodología:** sistemas algorítmicos que detectan patrones históricos y generan señales automáticas cuando esos patrones reaparecen. Corre **múltiples sistemas en paralelo sobre distintos marcos temporales** (ej. trend-following semanal combinado con posiciones cortas diarias para neutralizar movimientos en contra).
- **Gestión de riesgo:** la pieza que él mismo señala como la clave real — "únicamente la buena gestión del riesgo permite ganancias sostenidas". El 26% de drawdown máximo con ~500% de retorno es la prueba.
- **Por qué automatiza:** para eliminar la psicología del trading y los errores humanos, no por velocidad de ejecución pura.
- **Aplicable a Jarvis:** el patrón de "múltiples sistemas en distintos timeframes que se validan entre sí" es exactamente el tipo de arquitectura modular con veto de riesgo que ya proponía `ANALISIS_ESTRATEGICO_IA_FINANCIERA.md` (agente técnico + agente de riesgo separado).

## Jim Simons — Renaissance Technologies (Medallion Fund)

- Retornos promedio de 66% anual (37% neto de comisiones) entre 1988-2021 — el track record más citado de la industria cuantitativa.
- 150.000 a 300.000 operaciones diarias, ejecutadas por algoritmos sobre patrones estadísticos, no por tesis discrecionales.
- Contrató matemáticos, físicos y criptógrafos en lugar de perfiles tradicionales de Wall Street.
- **Aplicable a Jarvis:** confirma que la ventaja está en la disciplina estadística y la escala de datos procesados, no en una "corazonada" mejor — reforzando por qué el walk-forward (validación estadística rigurosa) importa más que ajustar manualmente reglas de entrada.

## Ed Seykota — pionero del trend-following sistemático

- Convirtió US$5.000 en más de US$15.000.000 en 12 años (retorno anual ~60%). Una cuenta que tomó en 1972 con US$5.000 creció más de 250.000% para 1988.
- Uno de los primeros en pasar de trading manual a sistemas computarizados, específicamente para eliminar el sesgo emocional.
- Filosofía: simplicidad de reglas + disciplina de ejecución por encima de complejidad de modelo.

## Otras firmas de trading sistemático (referencia de escala institucional)

- **Two Sigma** — IA, machine learning y computación distribuida aplicados a señales de trading.
- **Citadel Securities, Jump Trading, Hudson River Trading (HRT)** — firmas de HFT (high-frequency trading) con infraestructura de ejecución propia.
- **Virtu Financial** — market-making electrónico de ultra baja latencia.

Estas últimas no son un modelo replicable a la escala de Jarvis (compiten en microsegundos con infraestructura de decenas de millones de dólares), pero confirman el mismo patrón de fondo: sistematización + gestión de riesgo explícita + validación estadística, no "una IA más grande".

## Reporte verificado — World Cup Championship of Futures Trading 2023 (agregado 13/08/2026)

Diego compartió el reporte final oficial (World Cup Advisor / Emerge Funds Investments) de la cuenta de Scherman en el campeonato 2023. Datos verificados (matemática de composición mensual chequeada — cierra: 492,02% calculado vs. 491,95% reportado):

- **18 instrumentos de futuros operados**: ES/YM/RTY/VX (índices), ZB/ZT (tasas), 6J (yen), GC/SI/PL/HG (metales), CL/NG (energía), ZC/ZS/ZW/SB/OJ (agrícolas) — las 6 categorías completas que coinciden con el universo de Moskowitz-Ooi-Pedersen y las Turtle Traders (`seleccion_de_universo.md`). Confirma con un caso real que la diversificación amplia entre clases de activo es lo que usan los que ganan competencias serias, no solo teoría académica.
- **Patrón mensual 2023**: ago (−6,18%) y sep (−21,30%) negativos (~−28% combinado); **octubre solo (+116,73%) es más de dos tercios de la ganancia anual** — firma clásica de trend-following (muchos meses de ruido, uno o dos que capturan un movimiento sostenido grande y hacen todo el año). Mismo patrón que se encontró en el backtest propio de SPY 2008.
- **Aclaración crítica del propio reporte**: es una **cuenta propietaria de competencia** ("not available for AutoTrade Subscribers"), no su fondo real para clientes (~23% anual en 17 años, ya documentado arriba). Las competencias premian riesgo extremo por diseño — no es comparable a gestión sostenible de capital de terceros. Misma distinción que la lección del "5%/semana" (jarvis/trading_algoritmico, sesión 12/08/2026): lo alcanzable con riesgo extremo en una buena racha no es lo sostenible.

## Otros nombres de referencia (agregado 11/08/2026)

- **David E. Shaw** (D.E. Shaw) — PhD en Ciencias de la Computación de Stanford, no venía de finanzas. Uno de los fondos quant más grandes y longevos del mundo.
- **Ken Griffin** (Citadel / Citadel Securities) — de los mayores en market making algorítmico a escala global.
- **John Overdeck y David Siegel** (Two Sigma) — IA + machine learning aplicado a señales de trading.
- **Cliff Asness** (AQR Capital) — PhD en finanzas de la Universidad de Chicago, popularizó el "momentum" y "value" sistemático a escala institucional.
- **Peter Muller** (Morgan Stanley PDT) — matemática teórica en Princeton, pionero del arbitraje estadístico en los años 90.
- **Thomas Peterffy** (Interactive Brokers) — pionero histórico de la ejecución electrónica automatizada, desde los años 80, antes de que "algo trading" existiera como categoría.

## Países donde el trading algorítmico es más fuerte

| País/región | Por qué |
|---|---|
| Estados Unidos | Domina el share global (~38-40%). Chicago (futuros/commodities: Jump Trading, DRW, Citadel Securities) y Nueva York (equities/derivados: Jane Street, Two Sigma, D.E. Shaw, Renaissance) son los dos polos históricos. ~60-75% del volumen en mercados de acciones de EE.UU. ya es algorítmico. |
| Reino Unido (Londres) | Segundo polo histórico — ahí tiene base XTX Markets, uno de los mayores market makers del mundo. |
| India | Crecimiento explosivo en volumen retail algorítmico + cantera enorme de talento técnico (ingenieros de los IIT) hacia fondos quant globales. |
| China | Enorme volumen doméstico, acceso restringido para extranjeros. |
| Países Bajos (Ámsterdam) | Hub de market making — Optiver, IMC, Flow Traders. |
| Singapur / Hong Kong | Hubs asiáticos para fondos quant que operan la región. |
| Europa del Este (Ucrania, Polonia, Rumania) | No son mercados grandes en sí, pero son fuente de talento técnico que contratan las firmas de HFT para código de baja latencia. |

## Camino de carrera hacia trading algorítmico

1. Base formal: matemática, física, ingeniería, ciencias de la computación o estadística.
2. Programación (Python es el estándar de facto).
3. Estadística y series de tiempo — el corazón técnico real del trabajo.
4. Portfolio propio de estrategias backtesteadas y documentadas (lo que se está armando en `jarvis/trading_algoritmico/`).
5. Entrada vía roles junior (analista cuantitativo, "trading assistant") antes de operar capital propio o de un fondo.

## Por qué dominan los matemáticos — la razón que da Jim Simons

La gente formada en finanzas tradicional ya viene "contaminada" — anclada a narrativas, creencias institucionales y reacciones emocionales al mercado. Es más fácil enseñarle mercados a un matemático que enseñarle matemática y programación a alguien que ya "sabe" de mercados con sesgos incorporados. Los matemáticos/físicos están entrenados para trabajar con incertidumbre, ruido y sistemas complejos — exactamente las condiciones de un mercado financiero.

## Algorítmico vs. discrecional/análisis técnico — no hay ganador absoluto

- El algorítmico rinde mejor en condiciones normales, con mucha información y patrones estables.
- El discrecional (un trader humano bueno) rinde mejor en incertidumbre extrema — crisis, crashes, eventos sin precedente — donde el patrón pasado no sirve.
- Ventaja real del algorítmico: reglas backtesteadas, sin sesgo emocional, ejecución consistente.
- Debilidad real del algorítmico: overfitting — el mismo problema ya documentado en el XAU de Jarvis (70%→38,5% WR).
- Tendencia de la industria: los límites se están difuminando — cada vez más fondos usan un híbrido (señal algorítmica + veto/ajuste humano), coincide con la recomendación de arquitectura modular de `ANALISIS_ESTRATEGICO_IA_FINANCIERA.md`.

## De dónde sale la ganancia real (por categoría de estrategia)

| Categoría | Fuente del edge | Nota |
|---|---|---|
| Arbitraje estadístico | Ineficiencias de precio temporales entre activos correlacionados, posiciones largas/cortas balanceadas | Funciona bien en mercados estables |
| Trend following | Gana solo 35-45% de las operaciones, pero los ganadores son mucho más grandes que los perdedores | Prospera en mercados volátiles/con tendencia — la lógica de Ivan Scherman |
| Market making | Cobra el spread miles de veces por día, se retira rápido cuando sube la volatilidad | Requiere infraestructura de baja latencia, no replicable a escala individual |
| Mean reversion | Asume reversión al promedio (RSI, Bandas de Bollinger) | Falla fuerte en rupturas de tendencia genuinas |

**Patrón común entre los que ganaron sostenidamente (Simons, Scherman, Seykota):** no fue una señal mágica — fue la gestión de riesgo y la disciplina de ejecución sistemática sostenida durante años.

Sources: [Algorithmic Trading Market Report — Research and Markets](https://www.researchandmarkets.com/reports/5939167/algorithmic-trading-market-report) · [Algorithmic Trading Statistics 2026 — Paper Trading Journal](https://papertradingjournal.com/2026/03/12/algorithmic-trading-statistics/) · [Greatest Quant Traders of All Time — Quantt](https://www.quantt.co.uk/resources/greatest-quant-traders-of-all-time) · [How a Mathematician Generated 66% Annual Returns — Medium](https://medium.com/@barronqasem/how-a-mathematician-generated-66-annual-returns-for-30-years-and-why-wall-street-hated-him-676a96acb393) · [How to Become an Algorithmic Trader — QuantInsti](https://www.quantinsti.com/articles/making-a-career-in-algorithmic-trading-roadmap-jobs-skills-and-more/) · [Algorithmic Trading vs. Discretionary Trading — QuantInsti](https://blog.quantinsti.com/algorithmic-trading-vs-discretionary-trading/) · [Algorithmic Trading Strategies — QuantVPS](https://www.quantvps.com/blog/algorithmic-trading-strategies)

Sources: [Ivan Scherman — Forbes Australia](https://www.forbes.com.au/brand-voice/uncategorized/ivan-scherman-man-behind-the-money/) · [Ivan Scherman — CMT Association](https://cmtassociation.org/presenter/ivan-scherman/) · [Jim Simons Trading Strategy — QuantVPS](https://www.quantvps.com/blog/jim-simons-trading-strategy) · [Jim Simons — Medallion Fund — QuantifiedStrategies](https://www.quantifiedstrategies.com/jim-simons/) · [Ed Seykota — Trend-Following Strategy](https://www.quantifiedstrategies.com/ed-seykotas-trend-following-strategy/) · [Ed Seykota — cómo convirtió $5.000 en $15M](https://www.quantifiedstrategies.com/how-ed-seykota-turned-5000-into-15-million/) · [Top 100 Quantitative Trading Firms 2026 — Quant Blueprint](https://www.quantblueprint.com/blog/top-100-quantitative-trading-firms-to-know-in-2025)
