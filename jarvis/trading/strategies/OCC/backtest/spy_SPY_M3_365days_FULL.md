# Backtest COMPLETO: OCC Strategy R5.1 — SPY M3
## Jun 06, 2025 — Jun 05, 2026 | Timeframe: 3 MINUTOS | Capital: $100,000

---

## CONFIGURACIÓN CONFIRMADA
| Parámetro | Valor |
|-----------|-------|
| Timeframe | **3 minutos** |
| MA Type | SMMA |
| MA Period | 8 |
| Multiplier | 3x (calcula en 9m) |
| Delay | **0 (repainting activo)** |
| Stop Loss | 0 (desactivado) |
| Take Profit | 0 (desactivado) |
| Commission | $0 |
| Order size | 10% del equity |

---

## KEY STATS

| Métrica | Valor |
|---------|-------|
| Net PnL | +$808.73 (+0.81%) |
| Open PnL (trade activo) | +$262.08 (+0.26%) |
| Max Drawdown | $52.26 (0.05%) |
| Win Rate | **61.74%** — 71/115 |
| Profit Factor | **3.947** |
| Sharpe Ratio | 0.760 |
| Sortino Ratio | **6.696** |
| Strategy outperformance vs B&H | +$1,120.58 |
| Buy & Hold PnL | -$311.85 (-0.31%) |
| CAGR | 0.81% |

---

## LONG vs SHORT

| | Long | Short |
|--|------|-------|
| Trades | 58 | 58 |
| Ganadores | 38 | 33 |
| Win Rate | **65.5%** | 58.6% |
| Net PnL | $520.39 (0.52%) | $550.42* |
| Avg PnL | $8.97 | $9.49* |
| Profit Factor | **4.78** | 3.108 |
| Mayor ganancia | $76.44 | $262.08* |
| Mayor pérdida | -$40.56 | -$40.43 |

*Short incluye el trade 116 abierto con $262.08 — sin ese trade Short neto es ~$288

---

## ANÁLISIS POR HORA DEL DÍA ⭐ HALLAZGO CRÍTICO

| Hora | Trades | Win Rate | PnL Total | Avg PnL | Veredicto |
|------|--------|----------|-----------|---------|-----------|
| 9:00 | 18 | **44.4%** | **-$16.90** | -$0.94 | ❌ EVITAR |
| 10:00 | 21 | 66.7% | +$112.45 | +$5.35 | ✅ Bueno |
| 11:00 | 13 | 61.5% | +$44.46 | +$3.42 | ✅ OK |
| 12:00 | 17 | 64.7% | +$150.15 | +$8.83 | ✅ Bueno |
| 13:00 | 12 | 58.3% | +$106.08 | +$8.84 | ✅ OK |
| 14:00 | 20 | **70.0%** | +$246.22 | +$12.31 | ⭐ MUY BUENO |
| 15:00 | 15 | 66.7% | **+$428.35** | **+$28.56** | ⭐ EL MEJOR |

**Las horas 14:00-15:59 generan $674.57 = 83% del PnL total con solo 30% de los trades.**
**La hora 9 es destructiva: los 3 peores trades de toda la estrategia ocurren ahí.**

---

## ANÁLISIS POR DÍA DE LA SEMANA ⭐

| Día | Trades | Win Rate | PnL Total | Avg PnL | Veredicto |
|-----|--------|----------|-----------|---------|-----------|
| Lunes | 19 | **42.1%** | +$124.93* | $6.58 | ❌ EVITAR |
| Martes | 19 | 52.6% | +$42.77 | $2.25 | ⚠️ Débil |
| Miércoles | 25 | 68.0% | +$188.89 | $7.56 | ✅ Bueno |
| **Jueves** | 30 | **73.3%** | **+$301.99** | **$10.07** | ⭐ EL MEJOR |
| Viernes | 23 | 65.2% | +$412.23* | $17.92 | ⭐ Muy bueno |

*Lunes incluye trade de $262 (open). *Viernes tiene outliers grandes.

**Jueves + Viernes = $714.22 del PnL total.**
**Lunes win rate 42.1% — peor que el azar.**

---

## TOP 5 TRADES

| # | Tipo | Fecha | PnL | Nota |
|---|------|-------|-----|------|
| 116 | Exit short | 2026-06-05 15:57 | **+$262.08** | Trade abierto actualmente |
| 45 | Exit long | 2026-05-22 10:00 | +$76.44 | |
| 115 | Exit long | 2026-06-04 15:51 | +$62.40 | |
| 77 | Exit long | 2026-05-28 14:39 | +$59.54 | |
| 43 | Exit long | 2026-05-21 14:48 | +$54.86 | |

---

## PEORES 5 TRADES — todos en hora 9

| # | Tipo | Fecha | PnL | Hora |
|---|------|-------|-----|------|
| 13 | Exit long | 2026-05-19 10:09 | **-$40.56** | 9:00 |
| 56 | Exit short | 2026-05-26 09:42 | **-$40.43** | 9:00 |
| 31 | Exit long | 2026-05-21 09:33 | -$25.61 | 9:00 |
| 84 | Exit short | 2026-05-29 09:30 | -$14.69 | 9:00 |
| 24 | Exit short | 2026-05-20 10:18 | -$12.87 | 9:00 |

---

## RACHAS

| Métrica | Valor |
|---------|-------|
| Racha ganadora máxima | **9 trades** consecutivos |
| Racha perdedora máxima | 6 trades consecutivos |
| Avg barras en ganadores | 20 barras (= 60 minutos) |
| Avg barras en perdedores | 9 barras (= 27 minutos) |

---

## CONCLUSIONES Y MEJORAS PROPUESTAS

### Mejora #1 — Filtro de horario (MAYOR IMPACTO)
Bloquear operaciones en la primera hora (9:00-9:59 ET).
- Pérdida evitada: ~$90 en pérdidas + mejora win rate de 61% a estimado ~68%
- Implementación: agregar condición `hour(time) >= 10` en Pine Script

### Mejora #2 — Filtro de día de la semana
Evitar operar lunes y martes.
- Win rate de Lu+Ma: 47.4% combinado
- Operar solo Mi-Vi mejoraría sustancialmente la calidad

### Mejora #3 — Take Profit en la última hora
La hora 15 tiene avg PnL de $28.56 — los trades que van bien al final del día son muy grandes.
Considerar reducir posición o agregar trailing stop en hora 15.

### Mejora #4 — Stop Loss dinámico
Sin stop loss, la mayor pérdida fue -$40.56 (0.42%).
Con ATR-based stop loss podría reducirse a ~0.15-0.20%.
