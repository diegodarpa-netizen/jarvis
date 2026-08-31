# Frameworks de backtesting (Python)

Investigación de agosto de 2026. Objetivo: evaluar reemplazos para el `backtest.py` actual (ad hoc, sin walk-forward), que ya usa Python + yfinance.

## Las dos arquitecturas

- **Vectorizado**: toda la serie de precios se convierte en arrays de NumPy y las señales se calculan como operaciones sobre esos arrays. Muy rápido para barrer miles de combinaciones de parámetros, pero por defecto no simula bien fills parciales, slippage ni cola de órdenes — hay que tener cuidado si se quiere fidelidad al trading en vivo.
- **Event-driven**: avanza vela por vela simulando el mercado real (orden por orden). Más lento, pero más fiel a cómo se ejecutaría en vivo.

## Opciones evaluadas

| Framework | Tipo | Fortaleza | Cuándo conviene |
|---|---|---|---|
| **VectorBT** | Vectorizado | 10.000 combinaciones de parámetros de RSI en segundos | Barrido masivo de parámetros / optimización — pero validar fills/slippage aparte |
| **Backtrader** | Event-driven | Librería extensible, se programa como si fuera código de producción | Cuando se prioriza control fino sobre la lógica de ejecución |
| **Zipline-reloaded** | Event-driven, factor-based | API de Pipeline para selección dinámica de universo + rebalanceo | Backtesting de portfolio/equities con research de factores (relevante para el caso de swing CRM/WFC/SLB) |
| **Freqtrade** | Event-driven | Backtesting + hyperopt + trading en vivo integrados, pensado para cripto | Si se quiere pasar de backtest a bot de cripto en vivo sin reescribir todo |
| **NautilusTrader** | Event-driven, alto rendimiento | Combina velocidad con fills realistas y paridad backtest↔vivo | Si el objetivo final es ejecución algorítmica real, no solo research |

## Recomendación

- **Para XAU/BTC (scalping intradía)**: NautilusTrader o Backtrader — la fidelidad de ejecución (fills, slippage) importa más que la velocidad de barrido, porque el problema actual (70%→38,5% WR) es de validación, no de falta de velocidad de cómputo.
- **Para swing equities (CRM/WFC/SLB y similares)**: Zipline-reloaded + pyfolio — es el camino más establecido para research de factores y rebalanceo, y encaja con el enfoque de filtro técnico que ya se estaba probando en el backtest filtrado perdido.
- **Para exploración rápida de ideas nuevas** (antes de comprometerse a un framework): VectorBT, por la velocidad de iteración — pero cualquier resultado prometedor ahí debe re-validarse en un motor event-driven antes de confiar en él.

Sources: [Python Backtesting Libraries 2026](https://rmbell09-lang.github.io/tradesight/blog/python-backtesting-libraries-2026.html) · [Best Python Backtest Engines 2026 — BullAlert](https://bullalert.ai/blog/best-python-backtest-engines-2026/) · [Python Backtesting Frameworks — 7 Compared](https://quanttradingtools.com/python-backtesting-frameworks/)
