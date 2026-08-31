# Filtros de tendencia — cómo distinguir mercado en tendencia de mercado en rango

Investigación de agosto de 2026, a raíz del portfolio de 5 activos: el cruce de EMA 20/50 le fue bien a XAU (tendencia limpia) y mal a QQQ/EUR (mercado en rango) — este archivo documenta cómo resuelve esto la industria, no eligiendo activos "de confianza" a mano (eso sería data snooping sobre la selección de activos, el mismo error que sobre parámetros).

## Los nombres y qué aportó cada uno

| Quién | Aporte | Año aprox. |
|---|---|---|
| Richard Donchian ("padre del trend-following") | Canal de Donchian (máximo/mínimo de N períodos) — sistema de breakout | Mediados s. XX |
| Richard Dennis y William Eckhardt (Turtle Traders) | Probaron que el trend-following se puede enseñar con reglas mecánicas — Donchian + ATR para sizing + regla de "saltar entrada si la señal anterior del mismo sistema ganó" (anti-whipsaw) | Años 80 — ganaron US$175M en 5 años |
| J. Welles Wilder | ADX (Average Directional Index) — fuerza de tendencia 0-100, independiente de la dirección. Umbral estándar: >25 tendencia fuerte, <20 sin tendencia | — |
| Bill Dreiss (trader australiano) | Choppiness Index — 0-100, <38 tendencia limpia, >62 mercado en rango, funciona en cualquier activo/timeframe | — |
| Perry Kaufman | Efficiency Ratio (parte de su Moving Average Adaptativo/KAMA) — % del movimiento de precio que es "señal" vs. "ruido" | — |
| Adam White | Vertical Horizontal Filter (VHF) — mismo propósito, otra fórmula | — |

## Cómo lo resuelven los fondos CTA institucionales (Winton, Man AHL, Aspect Capital)

No usan un filtro binario único — combinan: (1) escalado de posición por volatilidad (reducen tamaño cuando el mercado está ruidoso), (2) múltiples horizontes temporales promediados para suavizar ruido de corto plazo, (3) recalibración adaptativa continua del régimen de mercado.

## Disponibilidad en NautilusTrader (ya instalado, sin que haga falta programar desde cero)

- `nautilus_trader.indicators.volatility.DonchianChannel` — el canal original de Donchian.
- `nautilus_trader.indicators.trend.DirectionalMovement` — +DI/-DI, base del ADX.
- `nautilus_trader.indicators.volatility.VerticalHorizontalFilter` — VHF de Adam White.
- `nautilus_trader.indicators.momentum.EfficiencyRatio` — Efficiency Ratio de Kaufman.

## KAMA — el filtro de Kaufman en detalle (agregado 13/08/2026, verificado en fuente primaria)

Ya usamos el Efficiency Ratio de Kaufman como filtro (fila de arriba). KAMA es el paso siguiente: en vez de solo filtrar cuándo operar, usa el mismo Efficiency Ratio para hacer que **la propia media móvil cambie de velocidad** — se vuelve más rápida (reactiva) cuando el mercado tiende con fuerza, y más lenta (suave) cuando está en rango, en vez de tener un período fijo (20, 50) que es igual de rígido en cualquier condición.

Fórmula (3 pasos): 1) Efficiency Ratio (ER) — cambio de precio neto sobre movimiento total en N períodos, de 0 a 1. 2) Constante de suavizado `SC = [ER × (SC_rápida − SC_lenta) + SC_lenta]²`. 3) `KAMA_t = KAMA_t-1 + SC × (Precio_t − KAMA_t-1)`. Parámetros estándar: 10 períodos para el ER, 2 para la EMA más rápida, 30 para la más lenta.

**Aplicable a Jarvis:** es un candidato directo para reemplazar el EMA 20/50 fijo que venimos usando — en vez de agregar el filtro de tendencia como una capa aparte (lo que ya probamos y empeoró el resultado combinado, ver `bitacora_activos.md` 11/08), KAMA integra la misma lógica adentro de la media móvil misma.

Fuentes: [StockCharts ChartSchool — Kaufman's Adaptive Moving Average](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama) · [Wall Street Mojo — KAMA formula](https://www.wallstreetmojo.com/adaptive-moving-average/)

## MESA / análisis de ciclos (John Ehlers) — otra familia de filtro, no probada todavía

Distinta lógica a todo lo de arriba: en vez de medir "¿tiende o no?", MESA (Maximum Entropy Spectral Analysis) busca **ciclos de precio periódicos escondidos en el ruido** — técnica tomada de la exploración petrolera (lecturas sísmicas de pulso corto) que Ehlers adaptó a series de precios en los años 70-80. Su ventaja frente a un análisis espectral de Fourier clásico es que necesita muy pocos datos para identificar un ciclo estable, lo que la hace apta para trading de corto plazo/intradía — relevante para nuestro caso de XAU M1.

**No la agregamos como decisión, solo como familia a considerar** si el análisis exploratorio (Hurst/ADF) de XAU muestra evidencia de ciclicidad en vez de tendencia pura o reversión pura — sería una tercera lectura posible del mismo dato, ninguna de las dos que ya tenemos cubre esto.

Fuentes: [MESA Software — papers técnicos de Ehlers (gratis)](https://www.mesasoftware.com/213-2/) · [A Technical Description of Market Data for Traders — Ehlers (PDF gratis)](https://www.mesasoftware.com/papers/AMFM.pdf)

## Decisión pendiente

Agregar uno de estos como filtro al EMACross del portfolio (`backtest_portfolio.py`): la estrategia solo opera cuando el filtro indica mercado en tendencia, no en cualquier momento como está ahora. Candidatos: VHF o Efficiency Ratio (más modernos) vs. ADX clásico (más conocido/documentado). Pendiente de qué prefiere Diego.

Sources: [Richard Donchian — TurtleTrader](https://www.turtletrader.com/richard-donchian/) · [Donchian Channels — TradersUnion](https://tradersunion.com/interesting-articles/trading-strategies/donchian-channels/) · [ADX — StockCharts ChartSchool](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/average-directional-index-adx) · [ADX indicator — Equiti](https://www.equiti.com/sc-en/news/trading-ideas/adx-indicator-definition-use-and-characteristics/) · [Turtle Trading Strategy — QuantifiedStrategies](https://www.quantifiedstrategies.com/turtle-trading-strategy/) · [Trend-Following CTAs vs Alternative Risk-Premia — Hedge Fund Journal](https://thehedgefundjournal.com/trend-following-ctas-vs-alternative-risk-premia/) · [Choppiness Index — GoCharting](https://gocharting.com/docs/charting/technical-indicator/oscillators/choppines-index) · [Detecting Ranging/Trending Markets with Choppiness Index — EODHD](https://eodhd.com/financial-academy/backtesting-strategies-examples/detecting-ranging-and-trending-markets-with-choppiness-index-in-python)
