# Backtest: OCC Strategy R5.1 — Oro (XAU/USD)
## Período: Jan 28, 1993 — Jun 5, 2026 (DEEP)

---

## KEY STATS

| Métrica | Valor |
|---------|-------|
| Total PnL | +$3,200.51 USD (+3.20%) |
| Max Drawdown | $19.81 USD (0.02%) |
| Profitable Trades | 79.23% — 328/414 |
| Profit Factor | **14.129** |
| Open PnL | +$22.69 USD (+0.02%) |
| Expected Payoff | $7.68 USD por trade |
| Strategy Outperformance vs Buy&Hold | +$7,455.22 USD |
| Sharpe Ratio | **2.294** |

---

## COMPARACIÓN vs BUY & HOLD

| | Buy & Hold | Estrategia |
|-|------------|-----------|
| PnL Máximo | +$485.98 (+0.49%) | +3.18% |
| PnL Actual | -$4,490 (-4.49%) | +3.18% |
| PnL Mínimo | -$4,490 (-4.49%) | 0.00% |

**Conclusión:** La estrategia aplasta al buy & hold. Mientras B&H está en -4.49%, OCC está en +3.18%.

---

## ANÁLISIS DE TRADES

| Métrica | All | Long | Short |
|---------|-----|------|-------|
| Total trades | 414 | 207 | 207 |
| Trades abiertos | 1 | 1 | 0 |
| Ganadores | 328 | 160 | 168 |
| Perdedores | 85 | 46 | 39 |
| % Rentable | **79.23%** | 77.29% | **81.16%** |
| PnL Promedio | $7.68 / 0.08% | $6.56 / 0.06% | $8.79 / 0.09% |
| Ganancia Promedio | $10.43 / 0.10% | $9.29 / 0.09% | $11.51 / 0.11% |
| Pérdida Promedio | $2.85 / 0.03% | $2.78 / 0.03% | $2.93 / 0.03% |
| Ratio Ganancia/Pérdida | **3.661** | 3.339 | **3.935** |
| Mayor ganancia | $234.40 (2.29%) | $91.50 (0.91%) | $234.40 (2.29%) |
| Mayor pérdida | $12.82 (0.13%) | $12.82 (0.13%) | $9.26 (0.09%) |
| Mayor gan. % del bruto | 6.85% | 6.16% | 12.12% |
| Mayor perd. % del bruto | 5.30% | 10.02% | 8.11% |
| Outliers (operaciones excepcionales) | 11 | 6 | 5 |
| PnL de Outliers | $910.83 (0.91%) | $349.43 (0.35%) | $561.40 (0.56%) |
| Barras promedio por trade | 18 | 17 | 18 |
| Barras promedio en ganadores | 20 | 19 | 21 |
| Barras promedio en perdedores | 8 | 8 | 7 |

---

## CAPITAL EFFICIENCY

| Métrica | All | Long | Short |
|---------|-----|------|-------|
| CAGR (retorno anualizado) | 0.55% | 0.24% | 0.32% |
| Retorno sobre capital inicial | 3.18% | 1.36% | 1.82% |
| Capital requerido | $19.81 USD | | |
| Retorno sobre capital requerido | **16,039.20%** | 6,856.16% | 9,183.04% |
| PnL neto % de la mayor pérdida | 24,780.22% | 10,592.62% | 19,654.93% |

---

## RUN-UP & DRAWDOWN

| Métrica | Valor |
|---------|-------|
| Run-up promedio | 0.15% |
| Run-up actual | 0.42% |
| Drawdown máximo | 0.02% |
| Drawdown promedio | 0.01% |

---

## DATOS CONFIRMADOS (fotos adicionales)

### Capital y Retornos
| Métrica | Valor |
|---------|-------|
| Capital inicial | **$100,000 USD** (confirmado) |
| Net PnL total | +$3,177.82 USD (+3.18%) |
| Net PnL Long | +$1,358.40 USD (+1.36%) |
| Net PnL Short | +$1,819.42 USD (+1.82%) |
| Gross profit | $3,419.86 USD (3.42%) |
| Gross loss | $242.05 USD (0.24%) |
| Profit Factor Long | 11.615 |
| Profit Factor Short | **16.949** |
| Commission paid | **$0 USD** — sin comisiones en este backtest |
| Expected payoff Long | $6.56 USD |
| Expected payoff Short | $8.79 USD |

### Run-Ups (detalle)
| Métrica | Valor |
|---------|-------|
| Avg run-up duration | 5 horas |
| Avg run-up (close-to-close) | $150.25 / 0.15% |
| Max run-up (close-to-close) | $430.06 / 0.43% |
| Max run-up (intrabar) | **$3,207.42 / 3.11%** |
| Max run-up % inicial capital | 3.21% |

### Drawdowns (detalle)
| Métrica | Valor |
|---------|-------|
| Avg drawdown duration | **17 minutos** |
| Avg drawdown (close-to-close) | $8.15 / 0.01% |
| Max drawdown (close-to-close) | $17.23 / 0.02% |
| Max drawdown (intrabar) | $19.81 / 0.02% |
| Return of max drawdown | $161.54 USD |

### Benchmarking vs Buy & Hold
| Métrica | Valor |
|---------|-------|
| Buy & Hold PnL actual | **-$4,277.40 (-4.28%)** |
| Buy & Hold % gain | -4.28% |
| Strategy outperformance | **+$7,455.22 USD** |

### Risk-Adjusted Performance
| Métrica | Valor |
|---------|-------|
| Sharpe Ratio | **2.294** |
| Sortino Ratio | N/D (no disponible en este backtest) |

### Distribución de Trades (ROI)
- Pico de trades ganadores concentrado entre 0% y 0.1%
- Average loss: **-0.03%** / Average profit: **0.08%**
- Breakevens: 1 trade (0.24%)
- Winners: 328 (79.23%) / Losers: 85 (20.53%)

## NOTAS IMPORTANTES
- **Comisiones:** $0 — los resultados NO incluyen comisiones reales. En vivo esto cambia el PnL.
- **Capital inicial:** $100,000 USD confirmado
- **Delay setting:** No confirmado aún — si fue 0, repainting puede inflar resultados
- **Timeframe del chart:** El eje muestra horas (08:04, 11:04) — parece intraday (1h o similar)
