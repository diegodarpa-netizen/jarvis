# Comparación M1 vs M3 vs DAILY — OCC Strategy R5.1 SPY
## Período de referencia: Jun 06, 2025 — Jun 05, 2026

---

## ⚠️ ADVERTENCIA CRÍTICA: LÍMITE DE BARRAS

El código tiene `ebar = 10,000 barras` configurado.

| Timeframe | 10,000 barras = | Datos reales disponibles |
|-----------|-----------------|--------------------------|
| M1 | ~3.3 semanas | Solo Jun 1–5, 2026 |
| M3 | ~10 semanas | Solo May 18 – Jun 5, 2026 |
| Daily | ~40 años | Año completo ✅ |

**El M1 tiene solo 3 semanas de datos reales, no un año.**
**El M3 tiene solo 10 semanas de datos reales.**
Para tener un año completo en M1 necesitás ebar = 100,000+ o ponerlo en 0.

---

## COMPARACIÓN GENERAL

| Métrica | M1 (3 sem) | M3 (10 sem) | Daily (1 año) |
|---------|------------|-------------|---------------|
| Trades | 107 | 115 | 6 |
| Win Rate | **75.7%** | 61.7% | 80.0% |
| Profit Factor | **13.801** | 3.947 | 2.249 |
| Sharpe | **1.518** | 0.760 | 0.085 |
| Sortino | — | **6.696** | — |
| Net PnL | $753 | $808 | $420 |
| CAGR | 0.76% | 0.81% | 0.42% |
| Max DD | 0.02% | **0.05%** | — |
| Racha perd. | **2** | 6 | 1 |

---

## ANÁLISIS M1 — POR HORA

| Hora | Trades | Win Rate | PnL Total | Avg PnL |
|------|--------|----------|-----------|---------|
| 9:00 | 8 | 75.0% | +$98.80 | +$12.35 |
| 10:00 | 25 | 76.0% | +$187.72 | +$7.51 |
| 11:00 | 16 | 75.0% | +$80.08 | +$5.00 |
| 12:00 | 12 | 75.0% | +$114.14 | +$9.51 |
| 13:00 | 13 | 61.5% | +$29.64 | +$2.28 |
| 14:00 | 15 | 80.0% | +$99.06 | +$6.60 |
| **15:00** | 19 | **84.2%** | **+$157.69** | **+$8.30** |

**En M1 la hora 9 NO es problemática (75% win rate).** Totalmente opuesto a M3.

---

## ANÁLISIS M1 — POR DÍA

| Día | Trades | Win Rate | PnL | Avg PnL |
|-----|--------|----------|-----|---------|
| **Lunes** | 25 | **84.0%** | +$109 | $4.37 |
| Martes | 23 | 73.9% | +$81 | $3.53 |
| Miércoles | 19 | 73.7% | +$89 | $4.73 |
| Jueves | 18 | 72.2% | +$142 | $7.92 |
| **Viernes** | 23 | 73.9% | **+$344** | **$14.97** |

**En M1 el Lunes es el MEJOR día (84%).** Opuesto a M3.

---

## ANÁLISIS M3 — POR HORA

| Hora | Trades | Win Rate | PnL Total | Veredicto |
|------|--------|----------|-----------|-----------|
| 9:00 | 18 | **44.4%** | **-$16.90** | ❌ EVITAR |
| 10:00 | 21 | 66.7% | +$112 | ✅ |
| 11:00 | 13 | 61.5% | +$44 | ✅ |
| 12:00 | 17 | 64.7% | +$150 | ✅ |
| 13:00 | 12 | 58.3% | +$106 | ✅ |
| 14:00 | 20 | 70.0% | +$246 | ⭐ |
| **15:00** | 15 | 66.7% | **+$428** | ⭐ |

---

## M3 FILTRADO (sin hora 9, sin Lunes/Martes) — RESULTADO ESTRELLA

| Métrica | M3 Original | M3 Filtrado | Mejora |
|---------|-------------|-------------|--------|
| Trades | 116 | 65 | -44% |
| Win Rate | 61.7% | **72.3%** | +10.6pp |
| Net PnL | $808 | **$888** | +10% más PnL |
| Profit Factor | 3.947 | **15.091** | +282% |
| Avg PnL/trade | $7.03 | **$13.67** | +94% |

**Con solo filtrar horario y día: mismo dinero, la mitad de trades, profit factor 15.**

---

## DAILY — LOS 6 TRADES DEL AÑO

| # | Tipo | Fecha | PnL | % |
|---|------|-------|-----|---|
| 1 | Short | 2025-11-26 | **-$336.75** | -3.45% |
| 2 | Long | 2026-01-16 | +$251.72 | +2.67% |
| 3 | Short | 2026-01-22 | +$53.20 | +0.55% |
| 4 | Long | 2026-02-04 | +$7.00 | +0.07% |
| 5 | Short | 2026-04-07 | +$445.48 | +4.62% |
| 6 | Long | 2026-06-05 | +$1,213.50 | +12.32% |

Solo 6 trades en 1 año. Trade 6 (abierto, +12.32%) inflando el resultado.
Sin trade 6: Net PnL = +$420 | 4/5 wins = 80%

---

## VEREDICTO FINAL

### ¿M1 o M3?

**M3 filtrado es la respuesta.**

- M1 tiene excelentes métricas PERO solo 3 semanas de datos — no es confiable estadísticamente
- M3 tiene 10 semanas y con filtros su profit factor sube a 15.091
- La clave no es el timeframe, es **cuándo operás**

### Recomendación operativa
| | Configuración |
|--|--|
| Timeframe | M3 |
| Operar | Miércoles, Jueves, Viernes |
| Horario | 10:00 — 15:59 ET |
| Stop Loss | ATR-based (agregar al Pine Script) |
| Take Profit | Trailing en hora 15 |

### Próximo paso: modificar el Pine Script
Agregar al código:
1. `hour(time) >= 10` — filtro horario
2. `dayofweek != 2 and dayofweek != 3` — sin Lunes ni Martes
3. Stop Loss dinámico con ATR
4. Take Profit opcional
