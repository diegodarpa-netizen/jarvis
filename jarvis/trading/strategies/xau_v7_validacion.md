# XAU/USD v7 — Log de Validación y Mejoras

## Estado actual del código
- Archivo: `xau_v7.pine`
- Timeframe: M1 con estructura M3
- Sesión: 09:01–10:59 NY

---

## Fixes aplicados (historial)

| # | Problema | Fix aplicado |
|---|----------|--------------|
| 1 | Solo 2 trades en 365 días | Cambio de `ta.pivothigh(5,5)` a detección por color M3 |
| 2 | `brk_up` nunca disparaba | `math.max(high[1],high[2],high[3])` en lugar de `ta.highest(high,5)` que incluía `high[0]` |
| 3 | Labels no aparecían | Mover label.new() DENTRO del bloque `if sig_bull and position_size == 0` |
| 4 | Labels duplicados | Cambio a chequeo `sig_bull` en lugar de `mec_bull or mer_bull` |
| 5 | `f_pat_env_bull` demasiado estricto | BUY solo necesita `high > mxH` (no `low < mnL`) |
| 6 | SL mal calculado | `close - dist * 0.60 * pip` (60% de distancia real, no hardcodeado 12.000) |
| 7 | Trend flippeaba durante caídas | 2 M3 consecutivas mismo color (v1 del fix) |
| 8 | Trend seguía ALCISTA en caída del 06/06 | **ACTUAL**: tendencia basada en highs/lows crecientes/decrecientes de M3 |

---

## Lógica de tendencia (Block 3) — versión actual

- **ALCISTA**: nuevo Alto M3 > Alto M3 anterior (highs crecientes)
- **BAJISTA**: nuevo Bajo M3 < Bajo M3 anterior (lows decrecientes)
- **ChOC**: primer quiebre en dirección contraria
- Solo actualiza cuando se forma un patrón M3 real → mucho más estable

---

## Fechas de validación

| Fecha | Señal esperada (PDF) | Señal código | Estado | Notas |
|-------|---------------------|--------------|--------|-------|
| 20/05/2026 | ? | ? | ⏳ pendiente | |
| 27/05/2026 | ? | ? | ⏳ pendiente | |
| 29/05/2026 | ? | ? | ⏳ pendiente | |
| 03/06/2026 | Sin señal | ? | ⏳ pendiente | |
| 06/06/2026 | SELL bajista | ⏳ fix en prueba | ⏳ pendiente | Trend mostraba ALCISTA durante caída |

---

## Backtest (actualizar al recibir capturas)

| Métrica | v5 | v6 | v7 (actual) |
|---------|----|----|-------------|
| Total trades | 2 | ? | ? |
| Win rate | ? | ? | ? |
| Profit factor | ? | ? | ? |
| Max drawdown | ? | ? | ? |

---

## Preguntas abiertas / cosas a confirmar

1. ¿El ChOC level para MER se mide desde el último Alto M3 antes del quiebre, o desde el High de la vela M1 que quiebra?
2. ¿El patrón START acepta Doji como vela de indecisión?
3. ¿El límite semanal -2R se resetea el lunes NY open o medianoche?
4. ¿El hedge cierra solo la posición actual o también cancela el exit order?

---

## Próximas mejoras planeadas

- [ ] Validar las 5 fechas con capturas
- [ ] Webhook TradingView → Jarvis para alertas en tiempo real
- [ ] Notificaciones Telegram/push al disparar señal
- [ ] Dashboard Jarvis con estado de estrategia
- [ ] Remover diagnósticos (bgcolor + plotshape) cuando el trend quede validado
