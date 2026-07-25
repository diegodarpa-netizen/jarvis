# Backtest M3 ebar=0 — SPY COMPLETO
## Mar 09, 2026 — Jun 05, 2026 | 63 días de trading | 437 trades

---

## KEY STATS (datos reales, 3 meses)

| Métrica | Valor |
|---------|-------|
| Net PnL | **+$5,854 (+5.85%)** |
| CAGR anualizado | **26.52%** |
| Max Drawdown | $119 (0.11%) |
| Win Rate | **72.48%** |
| Profit Factor | **5.622** |
| Sharpe | 0.785 |
| Sortino | **7.59** |
| Buy & Hold mismo período | +$10,297 (+10.3%) |
| Strategy outperformance | +$3,059 |

---

## ANÁLISIS POR HORA (437 trades, 3 meses)

| Hora | Trades | Win Rate | PnL Total | Avg PnL | Veredicto |
|------|--------|----------|-----------|---------|-----------|
| 9:00 | 58 | **51.7%** | +$27 | +$0.47 | ❌ EVITAR |
| 10:00 | 71 | 71.8% | +$1,226 | +$17.27 | ✅ Muy bueno |
| 11:00 | 53 | 75.5% | +$764 | +$14.42 | ✅ Bueno |
| 12:00 | 55 | **81.8%** | +$851 | +$15.48 | ⭐ Excelente |
| 13:00 | 75 | 74.7% | +$1,308 | +$17.44 | ⭐ El mejor PnL |
| 14:00 | 71 | 73.2% | +$1,083 | +$15.25 | ✅ Muy bueno |
| 15:00 | 54 | 79.6% | +$855 | +$15.84 | ✅ Muy bueno |

---

## ANÁLISIS POR DÍA

| Día | Trades | Win Rate | PnL Total | Avg PnL | Veredicto |
|-----|--------|----------|-----------|---------|-----------|
| Lunes | 82 | 63.4% | +$684 | $8.34 | ⚠️ Débil |
| Martes | 72 | 68.1% | +$1,043 | $14.49 | ✅ OK |
| **Miércoles** | 92 | **77.2%** | +$1,364 | $14.83 | ⭐ |
| **Jueves** | 106 | **79.2%** | **+$1,597** | $15.07 | ⭐ El mejor |
| Viernes | 85 | 71.8% | +$1,427 | $16.79 | ✅ Muy bueno |

---

## ANÁLISIS POR MES

| Mes | Trades | Win Rate | PnL | Avg PnL |
|-----|--------|----------|-----|---------|
| Mar 2026 | 119 | 73.9% | +$1,615 | $13.57 |
| **Abr 2026** | 134 | **78.4%** | **+$2,455** | $18.33 |
| May 2026 | 162 | 67.3% | +$1,522 | $9.40 |
| Jun 2026 | 22 | 68.2% | +$524 | $23.81 |

---

## VERSIONES FILTRADAS — RESULTADOS ESTRELLA

| Versión | Trades | Win Rate | PnL | Profit Factor |
|---------|--------|----------|-----|---------------|
| Original | 437 | 72.5% | $5,854 | 5.622 |
| Sin hora 9 | 379 | **75.7%** | **$6,089** | **14.165** |
| Mi-Ju-Vi + sin hora 9 | 248 | **78.6%** | $4,117 | **18.427** |

**Sin hora 9: más PnL con menos trades. Profit Factor sube de 5.6 → 14.2**

---

## ⚠️ PROBLEMA CRÍTICO: $10,000 CON IBKR

### Por qué $10k no es suficiente para SPY en M3

| Concepto | Valor |
|---------|-------|
| Capital | $10,000 |
| 10% por trade | $1,000 |
| Acciones SPY (~$750) | **1 acción** |
| PnL diario escalado (1 acc) | $7.43/día |
| PnL anual bruto (1 acc) | $1,873 |
| Comisiones IBKR (~$2 RT × 1,512 trades) | **-$3,032** |
| **PnL neto real** | **-$1,158** ❌ |

### Solución: cambiar el instrumento

| Instrumento | Notional | Comisión RT | PnL viable con $10k |
|------------|----------|-------------|---------------------|
| SPY (1 acc) | $750 | $2.00 | ❌ Negativo |
| SPY (5 acc) | $3,750 | $0.50 | ⚠️ Justo |
| **MES Futures** | $18,750 | **$0.50** | ✅ **Ideal** |
| QQQ (1 acc) | $500 | $2.00 | ❌ Negativo |

**MES (Micro E-mini S&P 500) es la solución para $10k:**
- Margen requerido: ~$1,500/contrato
- Con $10k podés operar 2-3 contratos
- Comisión IBKR: ~$0.25-$0.50 por contrato
- Cada punto del S&P = $5 por contrato MES

---

## RACHAS

| Métrica | Valor |
|---------|-------|
| Racha ganadora máxima | **17 trades** consecutivos |
| Racha perdedora máxima | 7 trades consecutivos |
