# Estrategias de oro (XAU/GLD) encontradas en bases públicas — con reglas y stats reales

Investigación de agosto de 2026, a pedido de Diego: relevar estrategias de oro concretas de QuantifiedStrategies.com (fuente gratuita, 200+ estrategias con parámetros). **Nota técnica:** el sitio bloquea el acceso directo de herramientas automatizadas (verificación anti-bot), así que esto sale de los resúmenes de búsqueda, no de haber leído la página completa — si se quiere el detalle completo (código, gráficos), hay que entrar manualmente a los links.

Ninguna de estas se declara "buena" todavía — son la hipótesis (paso 1 de `proceso_prueba_estrategias.md`), falta correrles nuestro propio walk-forward.

---

## 1. Gold Momentum Strategy (oro + bonos del Tesoro a 10 años)

**Regla:** mide el retorno total de 12 meses del oro (GLD) y de los bonos del Tesoro a 10 años (IEF). Si **ambos** son positivos, posición larga en oro. Si cualquiera de los dos es negativo, se pasa a cash hasta la próxima evaluación de fin de mes.

**Resultado del backtest:** ~6% anual (mensual) / 6,2% anual (semanal) — **contra 10,5% anual de comprar-y-mantener**. La estrategia rinde MENOS en retorno absoluto, pero redujo la exposición al mercado un 19% (menos tiempo invertido, cortando meses malos). Recomendación del propio sitio: no usar como única estrategia de portfolio, es volátil — funciona mejor como overlay de otra estrategia de oro, no de forma aislada.

**Lectura honesta:** es exactamente el patrón que ya documentamos con SPY — reducir exposición no siempre gana en retorno absoluto, aunque mejore el perfil de riesgo. Hay que medir Sharpe, no solo retorno, antes de descartarla o aceptarla.

Fuente: [Gold Momentum Strategy — QuantifiedStrategies](https://www.quantifiedstrategies.com/gold-momentum-strategy/)

## 2. Gold Moving Average Strategy (trend-following clásico)

**Regla:** cuando el precio del oro está por encima de su media móvil de 12 meses (250 días), la estrategia está larga. Es la versión más simple posible de trend-following — un solo filtro, sin cruce de dos medias.

**Aplicable a Jarvis:** más simple todavía que nuestro EMA 20/50 — vale la pena probarla como punto de comparación mínimo ("¿le gana algo más simple todavía a lo que ya probamos?").

Fuente: [Gold Moving Average Strategy — QuantifiedStrategies](https://www.quantifiedstrategies.com/gold-moving-average-strategy/)

## 3. Estrategia de ruptura (breakout) sobre GLD

**Regla:** entra al cierre cuando se confirma una ruptura, sale unos días después.

**Resultado del backtest:** 509 operaciones, drawdown máximo de -13%, backtesteado **incluyendo comisiones y slippage** (a diferencia de muchos backtests "limpios" que no lo hacen — punto a favor de que este número sea más realista).

Fuente: [Top Gold Trading Strategies — QuantifiedStrategies](https://www.quantifiedstrategies.com/gold-trading-strategies/)

## 4. Gold Overnight Strategy — hallazgo más interesante de toda la lista

**Regla:** mantener la posición solo durante la noche (de cierre a apertura), no durante el día.

**Resultado:** la ganancia promedio es **prácticamente cero**, a pesar de que GLD subió 317% en todo el período analizado. **Esto significa que casi toda la suba histórica del oro ocurrió durante el horario de operación diurno, no de un cierre a la apertura siguiente.**

**Por qué esto es relevante para nuestra franja horaria actual:** nuestra ventana de datos (08:00-11:30 NY, ahora ampliada a 03:00-17:00) es horario diurno de operación — este hallazgo sugiere que estamos mirando exactamente la parte del día donde históricamente se concentró el movimiento real del oro, no la parte "muerta". Es una validación indirecta más de la franja horaria elegida.

Fuente: [Gold Overnight Strategy — QuantifiedStrategies](https://www.quantifiedstrategies.com/gold-overnight-trading-strategy/)

## 5. Gold-Silver Chart Ratio Strategy

**Regla:** opera la relación relativa de precio entre oro y plata (cuando la ratio se desvía de su comportamiento histórico) — es un stat-arb simplificado entre dos metales, no una estrategia direccional pura sobre XAU solo.

**Aplicable a Jarvis:** es la primera pista concreta de una estrategia de la familia stat-arb/pairs trading (la 4ª familia que nunca probamos con código, mencionada en `teoria_fundamental.md`) aplicada específicamente a metales — vale la pena investigarla en más detalle cuando lleguemos a esa etapa.

Fuente: [Gold Silver Chart Ratio Strategy — QuantifiedStrategies](https://www.quantifiedstrategies.com/gold-silver-chart-ratio-strategy/)

---

## 6. Estacionalidad de oro por mes (con la advertencia de rigor incluida)

**El patrón más citado:** el "efecto septiembre" es el mes más fuerte del oro — positivo en el 64% de los años, sobre 50 años de historia. Enero también tiene respaldo estadístico (p=0,02). Retornos promedio por mes: septiembre +2,1%, enero +1,8%, noviembre +1,4% — más débiles: marzo -0,6%, junio -0,4%, abril -0,3%.

**La honestidad que trae la propia fuente, y que hay que sostener:** *"todos los meses excepto enero y junio tienen resultados demasiado inconsistentes — no hay patrón confiable."* O sea: de 12 meses "estacionales", **solo 2 pasan un chequeo de significancia real**. Es el ejemplo perfecto de por qué no alcanza con mirar un promedio bonito — hay que pedir el p-valor, no solo el número.

Fuentes: [How Seasonality Impacts the Gold Price](https://www.goldpriceforecast.com/explanations/how-seasonality-impacts-the-gold-price/) · [Seasonality in gold — The Invest Log](https://theinvestlog.com/p/seasonality-in-gold-do-some-months)

## 7. Posicionamiento COT (Commitment of Traders) — indicador contrarian

**Regla:** el reporte semanal de la CFTC (viernes 15:30 ET) separa a los operadores de futuros de oro en Comerciales (productores/consumidores que cubren riesgo) y No-Comerciales (grandes especuladores). **Posicionamiento corto extremo de Comerciales** suele señalar pisos de precio; **posicionamiento largo extremo de especuladores** suele señalar techos — se usa como indicador contrario (cuando todos están del mismo lado, se acerca un giro).

**Advertencia de la propia fuente:** el trend-following puro puede seguir siendo rentable incluso en niveles de posicionamiento extremos si los fundamentals siguen apoyando el movimiento — no usar el COT solo, combinar con otra señal.

**Aplicable a Jarvis:** es un dato **semanal**, no intradía — no sirve para M1 directo, pero podría ser un filtro de "régimen" macro que habilite/inhiba una estrategia intradía (la misma lógica que ya usamos con el filtro de tendencia Efficiency Ratio, aplicado a otra dimensión).

Fuente: [COT Report for Gold — Metalorix](https://metalorix.com/en/learn/markets-trading/cot-report-for-gold) · [Gold COT Report — COT Dashboard](https://www.cotdata.net/blog/cot-data-gold)

## 8. Opening Range Breakout (ORB) — la más directamente aplicable a nuestra franja horaria

**Regla:** marcar el máximo/mínimo de los primeros minutos de la sesión, entrar en la ruptura de ese rango (a favor si rompe arriba, en contra si rompe abajo), usar el tamaño del rango para el stop, salir al cierre de la sesión.

**Estadísticas encontradas:** win rate típico de 40-60% (no necesita ser alto porque busca "días de tendencia" donde el ganador corre varias veces el riesgo inicial — mismo patrón asimétrico de siempre). Un estudio de 2023 (Zarattini y Aziz) encontró que una versión disciplinada da buen retorno ajustado por riesgo; otro backtest reportó 74,56% de operaciones ganadoras con profit factor 2,512 (con reglas específicas, no genérico).

**Reglas de filtro encontradas para oro específicamente:** funciona mejor cuando el rango del día es menor al promedio de los últimos 2 meses (mercado comprimido, no ya volátil) y cuando el oro está por encima de su media móvil de 5 días.

**La advertencia más importante de todo este archivo, textual de la fuente:** *"probar docenas de ventanas de apertura (5, 7, 10, 12, 15, 20, 25, 30 minutos...) garantiza que vas a encontrar una que se ve espectacular en el histórico — pero esto es minería de parámetros, la 'mejor' ventana probablemente va a fallar hacia adelante."* Es exactamente el error de data-snooping que venimos evitando toda la sesión, dicho por la misma fuente que documenta la estrategia — hay que elegir UNA ventana por lógica (ej. los primeros 15-30 min de la sesión de Londres-NY) y no tocarla después de ver el resultado.

**Por qué esta es la más relevante para nosotros:** es intradía, aplica directo a nuestra ventana horaria (08:00-11:30 / 03:00-17:00 NY) y a nuestros datos M1 ya descargados — es la primera de todas las hipótesis de hoy que se puede probar sin esperar más datos.

Fuentes: [Opening Range Breakout Strategy — QuantifiedStrategies](https://www.quantifiedstrategies.com/opening-range-breakout-strategy/) · [Opening Range Breakout — TapeScript](https://tapescript.io/blog/opening-range-breakout)

## 9. Momentum + estructura de plazos (carry) combinados, en commodities en general

**Momentum:** comprar los futuros de commodities que más subieron recientemente, vender los que más bajaron, manteniendo hasta 12 meses. Según Quantpedia: robusto a costos de transacción y a la elección de parámetros, se sostiene incluso en crisis financieras, sin correlación significativa con los factores de riesgo tradicionales — una de las anomalías más respaldadas de toda la literatura cuantitativa.

**Carry (term structure):** menos bueno como diversificador que el momentum solo, pero está ligado a la volatilidad del mercado de acciones global — rinde poco cuando la volatilidad de acciones sube, y viceversa.

**La advertencia clave, específica y accionable:** **ambos factores rinden mejor en mercados de commodities con "baja financiarización"** (poca participación de inversores financieros, no solo productores/consumidores) — **y generan poca ganancia en mercados con participación financiera significativa.** El oro es de los commodities MÁS financiarizados que existen (ETFs, futuros muy líquidos, gran participación especulativa) — esto es una razón concreta para sospechar que estos dos efectos, aunque probados en commodities en general, pueden estar diluidos específicamente en oro. Hay que medirlo, no asumir que se traslada igual.

Fuentes: [Momentum Effect in Commodities — Quantpedia](https://quantpedia.com/strategies/momentum-effect-in-commodities) · [Term Structure Effect in Commodities — Quantpedia](http://quantpedia.com/screener/Details/22)

## 10. El hallazgo más importante de todo el archivo — 4.000 estrategias probadas sobre oro, casi todas ruido

QuantPedia publicó un estudio ("An Extensive Test of Market Timing Strategies in the Gold Market") que probó **más de 4.000 estrategias de timing** sobre oro — estacionales, técnicas y fundamentales combinadas. Resultado: aparecieron "grandes ganancias" en varias de ellas, **pero al aplicar un control riguroso de sobreajuste, la robustez se sostuvo solo en un subconjunto chico de estrategias técnicas** — la enorme mayoría de esas "grandes ganancias" eran ruido estadístico, no edge real.

**Por qué esto es el hallazgo más importante de todo el archivo:** es la confirmación empírica, a escala de 4.000 pruebas, de exactamente lo que venimos sosteniendo toda la sesión con el paper de Bailey/Borwein/López de Prado/Zhu (más de ~50 tests sobre el mismo dato dispara el riesgo de overfitting). Acá no son 50, son 4.000 — y la conclusión es la misma: **probar muchas estrategias sin control de sobreajuste garantiza encontrar "ganadoras" falsas.** Cualquier estrategia de las 9 que ya documentamos tiene que pasar por walk-forward real antes de creerle el número, sin excepción — este estudio es la prueba de que ni siquiera un análisis profesional/académico está exento de esto si no se controla explícitamente.

Fuente: [An Extensive Test of Market Timing Strategies in the Gold Market — QuantPedia](https://quantpedia.com/an-extensive-test-of-market-timing-strategies-in-the-gold-market/)

## 11. Time Series Momentum (Quantpedia #118) — con sizing por volatilidad incluido

**Regla:** cada mes, se mide el retorno en exceso de los últimos 12 meses de cada activo — si es positivo, posición larga; si es negativo, posición corta. **El tamaño de la posición es inversamente proporcional a la volatilidad del activo** (no un tamaño fijo por unidad, que es justo el gap que ya identificamos en nuestro propio portfolio).

**Resultado:** un portafolio diversificado de time-series momentum across muchos activos es "notablemente estable" — Sharpe alto, poca correlación con benchmarks pasivos. Es la misma idea de fondo del paper de Moskowitz-Ooi-Pedersen que ya teníamos en `seleccion_de_universo.md`, confirmada acá desde una fuente independiente.

**Aplicable a Jarvis:** el sizing por volatilidad es exactamente lo que nos falta implementar (ya lo señalamos con PyPortfolioOpt en `plataformas_y_recursos_gratuitos.md`) — esta es una tercera fuente, distinta, que confirma que es la pieza que falta, no solo una idea nuestra.

Fuente: [Time Series Momentum Effect — Quantpedia](https://quantpedia.com/strategies/time-series-momentum-effect)

## 12. Oro condicionado por régimen de inflación (cruzando con bonos)

**Hallazgo:** los retornos futuros del oro están sistemáticamente condicionados por el momentum conjunto del propio oro **y** de bonos del Tesoro de larga duración — mismo patrón que la estrategia de momentum+bonos ya documentada (#1), confirmado ahora desde el ángulo de régimen de inflación, no solo de momentum cruzado. El dataset de referencia arranca en 1981.

**Complementaria — ratio oro/plata como indicador de inflación**: un ratio más alto (hace falta más plata para comprar la misma onza de oro) tiende a asociarse con expectativas de mayor inflación — la gente prefiere oro sobre plata en esos regímenes. Refuerza la hipótesis #5 (ratio oro-plata) con una razón macro de fondo, no solo estadística.

Fuente: [Using Inflation Data for Systematic Gold and Treasury Investment Strategies — QuantPedia](https://quantpedia.com/using-inflation-data-for-systematic-gold-and-treasury-investment-strategies/)

---

## Pendiente — QuantPedia (fuente más rigurosa, no relevada en detalle todavía)

QuantPedia tiene específicamente una "Gold Momentum Trading Strategy" (investigación de Cyril Dujava) con la misma lógica de momentum de oro+bonos de arriba, pero con el respaldo de paper académico y backtest out-of-sample completo (en la parte paga). También tiene una categoría de "commodity trend following" y "front-running de estacionalidad de commodities" que incluye metales — no se relevó en detalle todavía, queda para la próxima sesión de investigación si Diego quiere profundizar ahí.
