# OCC Strategy R5.1 — Reglas y Lógica Detallada

## Concepto Central
La estrategia detecta cruces entre dos MAs: una calculada sobre el **precio de cierre** y otra sobre el **precio de apertura**. Cuando la MA del cierre cruza por encima de la MA de apertura → señal LONG. Lo inverso → señal SHORT.

---

## Lógica de Señales

### Entrada LONG
- `closeSeriesAlt` cruza hacia ARRIBA `openSeriesAlt`
- Es decir: MA(close) > MA(open) en el timeframe alternativo

### Entrada SHORT
- `closeSeriesAlt` cruza hacia ABAJO `openSeriesAlt`
- Es decir: MA(close) < MA(open) en el timeframe alternativo

### Salida
- La posición long se cierra cuando aparece señal short (y viceversa)
- Sin trailing stop (fue removido en R3)
- Stop Loss y Take Profit opcionales en puntos fijos

---

## Parámetros Configurables

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| Use Alternate Resolution | true | Activa el TF alternativo |
| Multiplier | 3x | TF del chart × 3 = TF de cálculo |
| MA Type | SMMA | Tipo de media móvil |
| MA Period | 8 | Longitud de la MA |
| Offset LSMA/Sigma ALMA | 6 | Solo para LSMA y ALMA |
| Offset ALMA | 0.85 | Solo para ALMA |
| Delay Open/Close MA | 0 | 0 = puede repintar / ≥1 = no repinta |
| Trade Type | BOTH | LONG / SHORT / BOTH / NONE |
| Stop Loss Points | 0 | 0 = desactivado |
| Target Profit Points | 0 | 0 = desactivado |
| Bars for Backtesting | 10000 | Límite de barras históricas |

---

## MAs Disponibles y Sus Características

| MA | Velocidad | Suavidad | Mejor para |
|----|-----------|----------|------------|
| SMA | Lenta | Alta | Swing |
| EMA | Media | Media | Intraday |
| DEMA | Rápida | Baja | Intraday/Scalping |
| TEMA | Muy rápida | Muy baja | Scalping |
| WMA | Media | Media | Intraday |
| VWMA | Media | Media | Cuando el volumen importa |
| **SMMA** | **Lenta** | **Muy alta** | **Default — Swing/Intraday** |
| HullMA | Rápida | Alta | Intraday |
| LSMA | Media | Alta | Swing |
| ALMA | Configurable | Alta | Versátil |
| SSMA | Muy lenta | Máxima | Swing largo |
| TMA | Muy lenta | Máxima | Swing largo |

**Nota del autor:** DEMA da los mejores resultados históricos.

---

## El Timeframe Alternativo (clave de la estrategia)

La estrategia calcula las MAs en un TF **3x mayor** al del chart:

| Chart | TF de cálculo (×3) |
|-------|--------------------|
| 1m | 3m |
| 5m | 15m |
| 15m | 45m |
| 1h | 3h |
| 4h | 12h |
| 1D | 3D |

**Por qué 3x:** reduce el ruido del TF base, genera menos señales falsas pero sigue siendo reactivo.

---

## Advertencia: Repainting

- **Delay = 0 (default):** puede repintar. Los resultados de backtesting se ven mejores de lo real.
- **Delay ≥ 1:** NO repinta. Los resultados caen drásticamente pero son reales.
- Para trading en vivo: **siempre usar Delay = 1**.

---

## Gestión de Posición

- `pyramiding = 0` → Solo 1 posición abierta a la vez
- `default_qty_value = 10` → 10% del capital por operación
- Cierre siempre por señal contraria (no hay trailing stop)
