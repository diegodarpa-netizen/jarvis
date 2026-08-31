# Bitácora de activos — Algo Trading

Registro de cada vez que Diego pide revisar/analizar activos para el proyecto de backtesting algorítmico. Cada entrada nueva va arriba (más reciente primero). No borrar entradas viejas — es historial, no estado actual.

**Cómo se usa:** cuando Diego pida "revisemos los activos" o similar, agregar una entrada acá con fecha, qué se analizó y la conclusión. Así no se repite research ya hecho entre sesiones, sin depender de la memoria automática (que es específica de cada máquina — ver `project_infra_google_drive` en la memoria de usuario).

---

## 27/08/2026 — Historial real de Fabian (XAU scalping manual, MEC/MER): primera evidencia sólida de edge real en 10 meses de trading en vivo

Diego pasó el export de Notion (vía WhatsApp) con el registro completo de operaciones reales de Fabian, 27/10/2025 → 27/08/2026. Se analizó trade por trade, día por día (191 operaciones) — ver informe completo en `fabian_manual_strategy/INFORME_COMPLETO.md`.

**Resultado**: 65,45% win rate, +72,83R acumulado, drawdown máximo de solo -4R, mediana semanal exactamente en el objetivo declarado de 2R (60,5% de semanas lo alcanzan o superan). MEC (66,3% WR) supera a MER (64,4%); dentro de MEC, el patrón Envolvente (70,2% WR) es mucho más fuerte que START (47,4% WR, casi azar). Sell supera a Buy (69,1% vs 61,9%), coincidiendo con el sesgo bajista que ya veníamos observando en el propio análisis de 6 meses de oro. Se corrigió un error de tipeo de fecha en el CSV original (28/04/2026→28/10/2025, por secuencia cronológica). Se cruzaron 123 de las 191 operaciones contra nuestros propios datos M1 de 6 meses — consistentes visualmente (6 casos verificados a mano). Escenario $1.000 con supuesto de 1% de riesgo por operación (no confirmado, pendiente preguntarle a Diego el número real): $2.054 final con reinversión (+105,4%), drawdown máximo -3,97%.

**Por qué esto es distinto a todo lo probado antes en este proyecto**: a diferencia de EMA9/Fibonacci/ORB/VWAP/patrones de velas (todo nulo o no significativo en nuestros propios tests), acá hay muestra grande sostenida en tiempo real (no backtest retrospectivo), múltiples regímenes de mercado, sin dependencia de 1-2 operaciones grandes, y reglas objetivas y ya formalizables (estructura M3 + ChOC + Envolvente, documentadas en los PDFs base de `jarvis/trading/xau_strategy`).

**Recomendación registrada**: en vez de seguir probando ideas nuevas desde cero, el candidato con más chances de ser la primera estrategia algorítmica XAU real y validada es formalizar la regla exacta de Fabian (filtrando o revisando el patrón START, que es el eslabón débil) y correr walk-forward sobre eso — no inventar una nueva. Pendiente investigar por qué el código automatizado de `xau_strategy` no replica este resultado (inestabilidad 70%→38,5% ya documentada en `ANALISIS_ESTRATEGICO_IA_FINANCIERA.md`).

**Pendiente**: confirmar con Diego el % de riesgo real por operación (no está en el Plan Operativo, puede estar en el Plan Técnico de 2,4MB, no revisado entero todavía).

---

## 15/08/2026 — Distancia a EMA (9/20/50/200) multi-resolución: sin edge robusto, 1 de 34 celdas "significativa" (y esa 1 es lo que el azar solo predice)

A raíz de imágenes que compartió Diego (gráfico diario de XAU con 4 EMAs, marcando "momentos" donde el precio se aleja de la EMA9 y después vuelve), se armó una línea de análisis paralela y complementaria a la entrada de abajo (14/08, 2) sobre la misma idea de "surfear la EMA9":

1. **Conteo de rachas** (cruces de EMA9) en M1/M5/M15/M30/diario, sobre los 6 meses de datos M1 intradía ya descargados (ventana 08:00-11:30 NY): ~25-30% de las rachas son "extendidas" en todas las resoluciones (patrón consistente en escala), pero sin sesgo direccional (≈50/50 alza/baja) — coincide con el Hurst≈0,5 ya calculado en el análisis exploratorio del 13-14/08.
2. **Regla naive** (entrar al cruce, salir al próximo cruce) aplicada a 32 episodios diarios: 19 ganadores/3 perdedores/+46% sumado — pero se identificó que es **casi tautológica** (una racha "ALZA" se define retrospectivamente como que terminó arriba, así que "operarla a favor" no es una predicción real, solo confirma la propia definición).
3. **Regla pulida** (confirmar entrada recién a los 3 días, salir por retroceso de 50% de la distancia máxima dentro de la racha): 14 de 32 episodios confirmados, 6 ganadores/3 perdedores, win rate 42,9% (consistente con el rango de industria de trend-following 35-45%), +16,87% sumado.
4. **Zonas de distancia → retorno del período siguiente**: ninguna zona diaria ni intradía mostró continuación clara — la zona 2-4% diaria incluso dio win rate 35,7% (peor que azar).
5. **Grilla final**: 4 EMAs (9/20/50/200, las mismas del gráfico de Diego) × 5 resoluciones × zonas de distancia, con bootstrap de 5.000 iteraciones por celda para intervalo de confianza 95%. **Solo 1 de 34 celdas válidas fue significativa** (EMA50 diario, zona 2-4%, +0,65% medio, IC[0,07%, 1,24%]) — pero con 34 pruebas a 95% de confianza se esperan ~1,7 "significativas" por puro azar (mismo fenómeno que el estudio de QuantPedia de 4.000 estrategias sobre oro, `knowledge/estrategias_oro_encontradas.md`), así que esa única celda no se puede tomar como edge real todavía.

**Conclusión: en 6 meses de XAU M1, no se encontró un patrón estadísticamente robusto de "distancia a una media móvil → continuación esperable" en ninguna de las 4 EMAs, en ninguna resolución.** Complementa (no contradice) el resultado en dólares de la entrada de abajo: mismo veredicto de fondo (sin edge consistente), visto desde dos ángulos distintos — conteo estadístico de zonas acá, backtest en dólares con reglas de entrada/salida concretas abajo.

**Nota operativa:** este archivo se modificó en paralelo por otra sesión mientras se trabajaba esta entrada (ver 14/08 (2) debajo, que apareció sin que esta sesión la escribiera) — señal de que hay más de una sesión de Jarvis corriendo sobre este proyecto al mismo tiempo. Vale la pena que Diego lo tenga presente para evitar que una sesión pise el trabajo de la otra.

**Próxima entrada:** cruzar esta línea de análisis con el hallazgo de abajo (falta de stop-loss como causa concreta de la pérdida) — probar si agregar un stop (ej. 1,5×ATR, ya usado en `strategy_swing_momentum.py`) cambia el resultado de la zona 2-4% de EMA50 que salió "significativa" (con la salvedad de multiple comparisons ya anotada).

## 14/08/2026 (2) — Estrategia propia de Diego: "surfear" la EMA 9 en oro diario — pierde contra buy-and-hold, sin stop-loss es el sospechoso principal

Diego propuso su propia idea (no de manual): comprar/vender cuando el oro "surfea" la EMA 9 (vela entera arriba o abajo, sin tocarla) tras una vela que la tocó, mantener mientras siga surfeando del mismo lado, salir en cuanto una vela la toca. La había probado a mano en oro diario desde enero 2026. Se formalizó en `strategy_ema9_surf.py` y se backtesteó en `backtest_ema9_surf_xau.py`.

**Bug encontrado y corregido en el camino:** la primera versión solo salía por "toque" — no contemplaba que con velas diarias el precio puede pasar de surfear un lado al otro sin que ninguna vela puntual la toque en el medio (la EMA también se mueve día a día). Eso la dejó vendida un mes entero mientras el oro subía fuerte (31/12→30/01, sin ningún toque que la sacara). Se corrigió: un salto limpio al lado contrario también cierra la posición.

**Resultado — enero a agosto 2026 (réplica de la prueba de Diego), corregido el bug:** 21 operaciones, 40% de aciertos, retorno acumulado (suma simple, sin componer) **−26,55%** contra **comprar y mantener +3,69%** en el mismo período. El mayor lastre: una sola operación (COMPRA 11/03→30/03) perdió **−12,41%** — la regla no tiene stop-loss, solo sale cuando toca la EMA, y en esa operación el precio corrió mucho en contra antes de que eso pasara.

**Walk-forward 2021-2026 (5 ventanas ~1 año):** ganó 1 de 5 ventanas contra buy-and-hold — mismo patrón que ya venimos viendo con todo lo probado hasta ahora en este proyecto (EMA-cross, RSI, momentum swing): sin edge consistente.

**Pendiente de confirmar con Diego:** si estos números no coinciden con lo que él vio a mano, es señal de que hay un detalle de la regla interpretado distinto (documentado en el docstring de `strategy_ema9_surf.py`) — no necesariamente un error de cálculo. Sospecha principal a probar después: la regla tal como está no tiene protección de stop — agregar uno (ej. el 1,5×ATR que ya se usa en otras estrategias del proyecto) podría cambiar el resultado bastante, especialmente por la operación de −12,41%.

## 14/08/2026 — Retomado el swing de equities (prioridad 3): CRM se da vuelta con el filtro técnico, el resto no muestra edge consistente

Diego pidió retomar el proyecto de swing trading de equities (memoria `project_swing_trading_equities`, 09/08) que había quedado con un backtest estático flojo (40,4% aciertos agregado, CRM el peor del lote) y una segunda vuelta filtrada nunca completada — los scripts de esa sesión vivían en scratchpad efímero y se perdieron. Esta vez se rehizo desde cero, ya integrado al proyecto (`strategy_swing_momentum.py` + `walk_forward_swing_equities.py`, reutilizando `walk_forward_harness.py`), con walk-forward real en vez de un solo número.

**Datos:** CRM, WFC, SLB, ORCL, FSLR, BSBR — 5 años diarios reales (yfinance, 16/08/2021→14/08/2026), partidos en 5 ventanas de ~1 año cada una.

**Estrategia (parámetros fijos de manual, no ajustados mirando el resultado):** largo únicamente cuando momentum(10d) > 0, RSI(14) en zona sana 50-70, precio a ≤5% del máximo de 20 ruedas, volumen relativo ≥1,2× el promedio de 20 ruedas. Salida: stop 1,5×ATR(14), target 2,5R — mismo money management ya validado con Diego en la sesión original (riesgo 1%/trade, tope 10% concentración — eso se aplica en el sizing real, no en este backtest de señal). Costo de transacción: 5 bps por cambio de posición.

**Resultado agregado: 13 de 30 ventanas (6 tickers × 5 ventanas) le ganaron a comprar-y-mantener — 43,3%, por debajo de la mitad.** Mismo patrón que ya se documentó con SPY y el portfolio EMA-cross: en ventanas de mercado fuertemente alcista (ORCL +82,5%, SLB +69,5%/+67,4%, FSLR +78,8%, WFC +51,3%), estar afuera de mercado la mayor parte del tiempo (la estrategia solo estuvo en posición 20-40% de las barras) cuesta caro frente a estar siempre adentro.

**Hallazgo específico — CRM se dio vuelta:** en el backtest original sin filtro, CRM era el peor del lote (26,9% aciertos, −US$2.732, arrastraba todo el agregado negativo). Con este filtro técnico, CRM ganó 4 de 5 ventanas a buy-and-hold (retorno promedio estrategia +1,95% vs. buy-hold −3,39%) — el único ticker de los 6 con resultado consistente. **Ojo: es 1 de 6 tickers — con 6 comparaciones independientes, un resultado así puede ser azar (multiple comparisons), no todavía evidencia sólida de edge específico en CRM.** No se debe concentrar capital en CRM solo por este resultado sin más validación (ej. repetir en otro período, otro universo de comparables del mismo sector).

Detalle completo por ventana en `results/walk_forward_swing_equities.csv`.

**Conclusión:** el filtro técnico (momentum+RSI+cerca de máximos+volumen) **no muestra un edge consistente y estable en el universo probado** — mismo veredicto que ya se vio con EMA-cross en XAU/EUR/BTC/SPY/TLT. No se recomienda operar esto con plata real todavía. CRM es la única señal interesante para seguir investigando, con la salvedad de la muestra chica de comparación.

**Próximo paso propuesto:** decidir si (a) se profundiza específicamente en CRM (más historia, comparables del mismo sector — otros SaaS enterprise), (b) se prueba la misma familia de estrategia (momentum swing) en el universo más amplio de 13 candidatos ya validados el 12/08 (SHOP, NET, BLK, NVDA, GLD, JPM, SCHW, BAC) en vez de insistir con estos 6 puntuales, o (c) se pausa equities y se vuelve a XAU/BTC (prioridades 1 y 2, todavía sin walk-forward real con datos de HistData) — pendiente de que Diego priorice.

## 12/08/2026 — Scanner + validación de probabilidad + 7 activos sumados: mismo patrón que SPY, confirmado a mayor escala

Se corrió la skill `finanzas-scanner-oportunidades` (`scan_opportunities.py`) sobre 44 tickers (tech/finanzas/latam/ETFs) para buscar candidatos. Top scores: NVDA, CRM, ORCL, NU, META (score 96-100).

**Validación histórica (1sem/1mes/1año/3años/5años) reveló que el score del scanner no capturaba la trayectoria completa:** CRM (score 100) viene negativo en 1, 3 y 5 años; ORCL (score 98) tiene −41,8% en el último año. Se amplió a 50 tickers (watchlist completa + commodities) con el mismo check.

**Se calculó probabilidad histórica real de ganancia** (retornos rolling sobre toda la historia disponible, no un solo dato puntual) para los 13 que habían dado positivo en las 5 ventanas simples. Resultado: USO, CPER, DBC, SLV y SNOW cayeron a ~46-55% (básicamente azar) con la medición correcta — el filtro simple anterior los sobrestimaba. Quedaron como sólidos: SHOP (83,6% prob. anual+), NET (80,4%), BLK (76,6%), NVDA (74,6%), GLD (69,5%), JPM (68,1%), SCHW (67,9%), BAC (66,0%).

**Se sumaron 7 al universo sistemático** (`backtest_portfolio.py`): JPM, BAC, BLK, NVDA, SHOP, NET, SCHW. GLD quedó afuera a propósito — redundante con XAU (mismo activo, misma lógica que ya corrigió SPY+QQQ).

**Resultado al correr el portfolio de 12 con la estrategia activa (EMA 20/50, largo+corto): EMPEORÓ el agregado** (Sharpe de +0,59 a −0,02, PnL de +US$2.401,97 a −US$284,71). Solo BAC (+US$1.327) y JPM (+US$560) dieron positivo; BLK, NVDA, SCHW, NET y SHOP dieron negativo pese a su alta probabilidad de ganancia en buy-and-hold.

**Confirma y generaliza el hallazgo de SPY (entrada anterior):** activos con tendencia secular fuerte (NVDA, SHOP, NET, BLK, SCHW) pierden con una estrategia simétrica larga+corta — cada entrada corta apuesta contra su propia tendencia de fondo. Solo los más cíclicos (JPM, BAC) toleraron bien la operativa en ambas direcciones.

**Próximo paso concreto:** probar versión SOLO-LARGA de la estrategia sobre SPY, NVDA, SHOP, NET, BLK, SCHW contra comprar-y-mantener — pendiente de ejecutar.

## 11/08/2026 (noche, 7) — SPY 15 años: comprar-y-mantener le gana a la estrategia en las 6 ventanas

Diego cuestionó el descarte de SPY: "sube casi todos los años, depende del timeframe". Correcto en el dato de fondo, pero conflacionaba comprar-y-mantener con la estrategia activa (dos cosas distintas). Se resolvió consiguiendo la muestra real que faltaba: 15 años de SPY diario (2011-2026, 3.770 barras — balance entre suficiente historia para cruzar regímenes distintos y no irse a un mercado ya irreconocible; 10-15 años es el estándar práctico de la industria para esto).

`spy_15y_walk_forward.py`: walk-forward en 6 ventanas de ~2,5 años, EMA 20/50 sin ajustar, comparado contra comprar-y-mantener en la misma ventana exacta.

**Resultado:** la estrategia ganó 5/6 ventanas individualmente, pero **comprar-y-mantener le ganó a la estrategia en las 6 ventanas, sin excepción, por 14 a 37 puntos porcentuales cada vez.** 15 años de solo comprar y mantener: +749,4%.

**Causa identificada:** la estrategia opera larga Y corta por igual. SPY tiene una deriva estructural alcista fuerte — cada vez que el sistema se pone corto, apuesta contra esa tendencia de fondo. El trend-following simétrico tiene sentido en commodities/divisas sin deriva estructural marcada, no en un índice de acciones con crecimiento secular.

**Próximo paso propuesto:** probar una versión SOLO-LARGA de la estrategia en SPY (comprar en señal alcista, quedar en cash en la bajista, nunca corto) contra el mismo benchmark de comprar-y-mantener.

## 11/08/2026 (noche, 6) — Barrida de timeframes + walk-forward sobre candidatos: BTC 4H es el menos malo

`timeframe_sweep.py`: EMA 20/50 fijo sobre 5 activos × 3 timeframes (1H/4H/1D), 15 combinaciones, cada una corrida AISLADA (un instrumento a la vez, no en portfolio compartido — nota: esto da resultados distintos a correr todo junto, ej. XAU 1H solo = 51,8% vs. 41,1% en portfolio de 5; causa exacta no diagnosticada, pendiente).

Los retornos más altos (BTC 1D +69,8%, XAU 1D +47,9%) vienen de 5-12 operaciones — descartados por muestra insuficiente. Los únicos con muestra decente sin validar: BTC 4H (84 ops, +38,6%) y SPY 4H (28 ops, +35,6%).

`walk_forward_candidates.py`: walk-forward (4 ventanas) sobre esos dos.
- **SPY 4H: descartado** — 2/4 ventanas ganadas, pero 3-13 operaciones por ventana, sin significado estadístico.
- **BTC 4H: el más consistente de toda la sesión — 3/4 ventanas ganadas** (+9,0% / +15,9% / +2,3% / **−3,7%**), muestra razonable (18-25 ops/ventana). **Pero la tendencia es decreciente ventana a ventana y la más reciente es negativa** — mismo patrón de debilitamiento que XAU. No es un edge fuerte y estable, es "el menos malo" de 15 combinaciones probadas.

**Conclusión de la sesión:** el cruce de EMA clásico sin ajustar no mostró edge fuerte y estable en ningún activo/timeframe probado hasta ahora. BTC 4H queda como el candidato más prometedor para seguir investigando (filtro de tendencia, sizing por volatilidad), pero no como una estrategia lista para usar.

**Próxima entrada:** pendiente decidir si se refina BTC 4H (filtro de tendencia + sizing) o se prueba una familia de estrategia distinta (mean-reversion, stat-arb) en vez de seguir iterando sobre trend-following.

## 11/08/2026 (noche, 5) — Walk-forward por ventanas: ningún activo tiene edge consistente

`walk_forward_portfolio.py`: se partió el período común a los 5 instrumentos (13/08/2024 → 11/08/2026, limitado por BTC) en 4 ventanas de ~6 meses, corriendo la misma estrategia (EMA 20/50, parámetros fijos, sin re-optimizar por ventana) en cada una por separado.

**Hallazgo central (probablemente el más importante de la sesión):** el "ranking de ganadores" del agregado de 2 años **no se sostiene ventana a ventana**.
- **TLT** "ganó" el agregado (+12,2%) pero en realidad ganó **1 de 4 ventanas** — todo el track record viene de la Ventana 1 (13/08/24-11/02/25), perdió las otras tres.
- **XAU** ganó 3 de 4 ventanas, pero la más reciente (Ventana 4, 10/02/26-11/08/26) dio **−6,5%** — el "ganador" se dio vuelta justo en el tramo más actual.
- **BTC y EUR**, que parecían "los perdedores" del agregado, en realidad **ganaron 3 de 4 ventanas cada uno** — el agregado negativo lo arrastraba una sola ventana mala (V2 para BTC: −14,7%).
- SPY: 2 de 4, el más parejo/mediocre de los cinco.

**Motivo del ejercicio:** Diego propuso "aumentar exposición a los que ganaron" (XAU/TLT/SPY) — este walk-forward muestra que hacerlo hubiera sido apostar fuerte a TLT (que en realidad solo ganó una vez de cuatro) y a XAU justo antes de su peor ventana. Confirma la razón de ser del walk-forward: el agregado esconde inestabilidad real.

**Conclusión: ningún instrumento mostró edge consistente y estable ventana tras ventana con esta estrategia (EMA 20/50 sin filtro).** No se recomienda concentrar capital en ninguno basándose en este resultado.

**Próxima entrada:** pendiente definir próximo paso — posible foco en mejorar la estrategia base (no solo el universo) antes de seguir iterando sobre selección de activos.

## 11/08/2026 (noche, 4) — Universo corregido (QQQ → TLT): mejora real, no p-hacking

Se aplicó la corrección propuesta en `seleccion_de_universo.md`: se sacó QQQ (redundante con SPY) y se sumó TLT (renta fija, categoría que faltaba) — **decidido antes de correr el número**, basado en evidencia externa (Moskowitz-Ooi-Pedersen, KMLM, DBMF), no mirando qué combinación mejoraba el resultado.

**Resultado normalizado ($100 c/u):** combinado pasó de US$520,64 (+4,1%) a **US$557,41 (+11,5%).** TLT aportó +12,2% (255 operaciones→97 operaciones, 35,1% win rate), reemplazando el −24,6% que arrastraba QQQ. Volatilidad del combinado (0,462%) sigue siendo casi la mitad del promedio individual (0,877%) — la diversificación se sostiene.

**Importante — no confundir con éxito validado:** sigue siendo muestra chica (1.085 operaciones, 5 activos, 2 años) comparado con el estándar académico (58 instrumentos, 25+ años en Moskowitz et al.). Todavía no pasó walk-forward. El filtro de tendencia (Efficiency Ratio) probado antes con QQQ había empeorado el resultado — pendiente re-probarlo con este universo corregido, aparte.

Universo actual: XAU, EUR/USD, BTC, SPY, TLT. Argentina (GD30) queda evaluándose aparte, día a día, sin sumarse todavía al portfolio sistemático.

**Próxima entrada:** cuando se corra el walk-forward real sobre este universo.

## 11/08/2026 (noche, 3) — Filtro de tendencia (Efficiency Ratio): empeoró el resultado combinado

`strategy_ema_cross_filtered.py` + `backtest_portfolio_filtered.py`: mismo EMA 20/50, mismos 5 activos, sumando un filtro de tendencia (Efficiency Ratio de Kaufman, umbral 0,30, período 20 — valores de referencia de la literatura, no ajustados a este resultado) — la estrategia solo opera si el mercado está "tendiendo" según ese indicador.

**Resultado normalizado ($100 en cada uno, comparación justa con el backtest anterior):** combinado pasó de +4,1% (US$520,64) a **+1,4% (US$506,96) — peor con filtro que sin filtro.** Por instrumento: mejoró QQQ (−24,6%→−16,7%) y EUR/USD (−2,8%→−0,5%), pero empeoró BTC (−0,9%→−13,5%), SPY (+7,9%→+0,5%) y XAU (+41,1%→+37,2%).

**Conclusión:** un filtro "de manual" no es garantía de mejora — un solo umbral fijo para 5 activos con perfiles de volatilidad/eficiencia muy distintos (cripto vs. forex vs. equities) probablemente no es apropiado igual para todos. Se decidió explícitamente **no** iterar el umbral hasta que mejore (sería data snooping sobre el parámetro del filtro, el mismo error de siempre) — el camino correcto pendiente es walk-forward real para calibrar y validar el filtro por instrumento.

**Próxima entrada:** cuando se implemente walk-forward real (Módulo 4 del curso, todavía pendiente de hacer en código).

## 11/08/2026 (noche, 2) — Portfolio de 5 activos, EMA 20/50 sin ajustar

`backtest_portfolio.py`: misma estrategia EMA 20/50 (parámetros fijos, sin optimizar) sobre XAU, EUR/USD, BTC, SPY y QQQ — datos reales por hora (~2 años, vía yfinance). 1.088 operaciones combinadas.

**Resultado: mediocre, no rentable de forma robusta.** PnL portfolio +US$916,19 (+0,46% en 2 años sobre US$200.000), Sharpe combinado 0,15. XAU (+$1.778) y SPY (+$497) positivos; BTC prácticamente plano; EUR/USD y sobre todo QQQ (−$1.345) negativos. El oro sostiene todo el resultado agregado.

**Causa identificada:** tamaño de posición fijo en unidades (no ajustado por volatilidad) por instrumento — rompe el supuesto de "apuestas de riesgo comparable" que necesita la matemática de `Sharpe_portfolio ≈ Sharpe_individual × √N` para cumplirse. Se decidió explícitamente **no** ajustar los parámetros de la estrategia (20/50) para mejorar el número — eso sería data snooping. La corrección legítima pendiente es normalizar el tamaño de cada posición por volatilidad (risk parity), no tocar la señal.

**Próxima entrada:** cuando se implemente sizing normalizado por volatilidad y se vea si el Sharpe combinado mejora.

## 11/08/2026 (noche) — Primer backtest con datos reales: EMA Cross sobre XAU

Se corrió `backtest_xau_ema_cross.py`: estrategia de referencia de NautilusTrader (cruce de EMA 20/50, trend-following clásico) sobre XAU/USD, con datos reales diarios de `GC=F` (futuros de oro vía yfinance, proxy de XAU/USD spot) — últimos 2 años, 503 barras.

**Resultado:** 4 operaciones, 25% win rate, PnL +US$1.499,20 (+1,5% en 2 años sobre US$100.000), Profit Factor 8,13, Sharpe 0,51. **Muestra demasiado chica para significar nada** — 4 operaciones no alcanza para juzgar si hay edge real, es solo la prueba de que el pipeline completo (datos reales → estrategia → ejecución → métricas) funciona de punta a punta. Pendiente: más operaciones (timeframe más chico o más instrumentos) antes de sacar cualquier conclusión.

Nota técnica: el instrumento tiene que construirse como `Commodity` (lote mínimo 1 unidad), no como `TestInstrumentProvider.default_fx_ccy` (que exige lote mínimo de 1000, como un lote estándar de forex) — con eso todas las órdenes se rechazaban.

**Próxima entrada:** cuando se corra la misma estrategia en más instrumentos/timeframes, o se avance a walk-forward.

## 11/08/2026 (tarde) — Entorno validado end-to-end

Se instaló y probó todo el stack técnico: Docker Desktop, Python 3.12.10, NautilusTrader 1.230.0 (venv en `jarvis/trading_algoritmico/venv/`). Se descartó LEAN/QuantConnect (requiere plan pago Researcher US$84/mes para CLI local, no estaba claro hasta intentar generar el token real). Se corrió `smoke_test.py`: backtest completo con datos sintéticos, 4 órdenes, 2 posiciones — confirma que el entorno funciona. Todavía no se cargó ningún dato histórico real ni se corrió ninguna estrategia real de Jarvis.

**Próxima entrada:** cuando se migre la estrategia de XAU con datos reales de HistData.com.

## 11/08/2026 — Arranque del proyecto

Se armó la carpeta de conocimiento (`knowledge/`) y el plan de construcción (`PLAN_CONSTRUCCION.md`). Todavía no se analizó ningún activo puntual con datos reales — es el punto de partida.

**Universo propuesto para arrancar** (ver `PLAN_CONSTRUCCION.md`): XAU/USD (prioridad 1), BTC/USD (prioridad 2), equities swing CRM/WFC/SLB/ORCL/FSLR/BSBR (prioridad 3). Pendiente de confirmación/ajuste por parte de Diego.

**Próxima entrada:** cuando Diego pida la primera revisión real de un activo.
