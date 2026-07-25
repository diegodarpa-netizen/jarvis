# XAU/USD Estrategia — Estado Actual

## Versión activa
- **Archivo:** `/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/strategies/xau_v9.pine` — **confirmado 04/07/2026 como la mejor versión disponible** (ver comparativa abajo). Copias idénticas (byte a byte) en `codigo1/xau_v9.pine` y `strategies/xau_v9_codigo1.pine` — son el mismo archivo, no versiones distintas.
- **Backtest engine:** `/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/backtest.py`

## ⚠️ Comparativa de versiones .pine existentes (04/07/2026)

Diego pidió comparar todas las versiones de XAU para saber cuál es la mejor/la que hay que usar en vivo. Se comparó presencia de los fixes documentados en `errores_frecuentes.md`:

| Archivo | Líneas | `sess_both_ok` | `in_session[1]` | `sess_choc_done` | SL reduc. >20k pips | Veredicto |
|---|---|---|---|---|---|---|
| `strategies/xau_v9.pine` | 798 | ✅ (5) | ✅ (6) | ✅ (10) | ✅ | **Mejor — usar esta** |
| `codigo_en_vivo/codigo_en_vivo_v2.pine` | 383 | ❌ | ✅ (6) | ❌ | ✅ | Rama más simple, sin protección de ChoC de sesión |
| `codigo_en_vivo/codigo_en_vivo.pine` | 305 | ❌ | parcial (2) | ❌ | ❌ | Más vieja, descartar |
| `scalping/XAU_Scalping_Strategy.pine` | 443 | ❌ | ❌ | ❌ | parcial | La que estaba corriendo en vivo en la sesión analizada — es la MENOS desarrollada de las 4. SL/TP estáticos calculados una sola vez al entrar (nunca se actualizan con nuevos pivots M3) |

**Conclusión:** `codigo_en_vivo_v2.pine` es cronológicamente el archivo modificado más reciente (10/06 13:53 vs 10/06 09:46 de xau_v9.pine), pero **"más reciente por fecha" no es lo mismo que "más completo"** — es una rama aparte que no heredó los fixes críticos de sesión/ChoC de xau_v9.pine. `xau_v9.pine` es la versión con más bugs reales resueltos y la que hay que cargar en TradingView reemplazando lo que esté corriendo ahora.

**Gaps pendientes incluso en xau_v9.pine (ninguna versión los tiene):**
- `saw_m3_bull`/`saw_m3_bear` — el fix definitivo de ChoC por 2 barras M3 consecutivas (Error #1h) no está implementado en ningún archivo.
- Regla "primera vela de contacto" / rechazo de cuerpo (10/06/2026) — tampoco implementada en ninguno.
Estos dos siguen siendo parte de la Fase 1 pendiente para la sesión en vivo de esta semana.

## Métricas objetivo (PDF)
| Métrica | Target PDF | Actual (backtest) |
|---------|-----------|-------------------|
| Trades/semana | 5.6 | ~5 |
| Win Rate | 71% | 70% |
| R/semana | 2.3R | 1.65R |
| Total 24 semanas | 135 trades / 55.98R | — |

## ⚡ REGLA FUNDAMENTAL — M1 + M3 SIMULTÁNEO (aprendida 10/06/2026)
**Siempre se ven M1 y M3 al mismo tiempo. Sin excepción.**

### M3 — Estructura dinámica (NO estática)
- En M3 se van creando highs y lows CONSTANTEMENTE durante la sesión
- Cada nuevo pivot M3 (alto o bajo) debe marcarse y actualizarse
- El gray box NO es fijo — se actualiza con cada nuevo pivot M3 relevante
- El ÚLTIMO alto M3 = referencia para SELL (SL y nivel de entrada)
- El ÚLTIMO bajo M3 = referencia para BUY (SL y nivel de entrada)

### M1 — Ejecución
- Las entradas en M1 son SIEMPRE en base al ÚLTIMO alto o bajo M3 creado
- Pullback al último nivel M3 → buscar envolvente/START en M1 → entrar
- El nivel de referencia cambia durante la sesión si M3 forma nuevos pivots

### Flujo correcto
```
M3: nuevo pivot → actualizar nivel de referencia
M1: precio llega al nivel → buscar ENV o START → entrada
```

---

## Reglas clave
- **Sesión:** 09:01–10:59 NY time (M1 chart)
- **Tendencia M3:** estructural — nuevo high > prev high = alcista; nuevo low < prev low = bajista
- **Modelos:** MEC-a (ENV + START), MEC-b (QPC), MER (ChOC touch)
- **SL:** último low M3 (BUY) / high M3 (SELL). Si dist > 20.000 pips → 60%
- **TP:** RR 1:0.9
- **Límites diarios:** Esc1=1TP stop, Esc2=1SL+1TP stop, Esc3=2SL stop
- **Límite semanal:** -2R acumulado

## Patrones
- **Patrón ENV:** pullback[1] + envolvente[0] (body ≥85%, opp wick <15%)
- **Patrón START:** pullback[2] + indecisión[1] (body ≤50%) + envolvente[0]
- **Martillo:** body 50-85%, mecha extrema > cuerpo
- **Doji:** body ≤50%, ambas mechas ≥15%, simétrica ≤30%

## Hallazgos del backtest
- Patrón START: 85.7% WR ✅
- Patrón ENV: 33.3% WR ⚠️ (candidato a filtrar)
- Gap de R/semana puede cerrarse con más datos o filtrando ENV

## PDFs BASE (siempre consultar antes de cualquier cambio)
- Plan Técnico: `/Users/diegorodriguez/Downloads/scalping/Plan técnico XAU.pdf`
- Plan Operativo: `/Users/diegorodriguez/Downloads/scalping/Plan operativo XAU.pdf`
- Apariencia: `/Users/diegorodriguez/Downloads/scalping/Aparienciadel indicador XAU.pdf`

## Carpetas de screenshots
- `/semanas/` → chart semanal completo → evaluar WR y R
- `/señales/` → cada señal individual → verificar patrón vs PDF
- `/estructura_m3/` → highs/lows/ChOC → comparar detección automática vs manual
- `/errores/` → señales incorrectas → detectar bugs y mejorar código

## Estado de desarrollo — XAU v9 (07/06/2026)

### Fixes aplicados (en orden)
1. `m3_pivots_sess` → requiere pivots dentro de sesión
2. `news_block` → filtro NFP/FOMC/CPI/GDP
3. `m3_high_sess / m3_low_sess` → confirmación direccional en sesión
4. `sess_both_ok` → ambas referencias (alto Y bajo) antes de entrar
5. **Session reset** → m3_trend/m3h1/m3l1 se resetean al inicio de sesión NY (solo estructura de sesión)
6. **sess_choc_done** → primer ChOC REAL en sesión (+1→-1 o -1→+1) habilita entradas
7. **desde_fecha** → parámetro para resetear contadores desde una fecha (testing aislado)

### Resultado actual en Jun 4 (sesión aislada)
- Tendencia detectada: BAJISTA ✅
- Operaciones: BUY 09:01 → SL ❌ | SELL 10:24 → TP ✅
- R neto: -0.1R (vs manual trader: +0.9R)
- Pendiente: fix BUY prematuro 09:01 + adelantar SELL de 10:24 a ~09:15

### Estructura visual APROBADA (ver apariencia_labels.md)
- Labels con: Estructura m3 / Posicionamiento / Ejecución / Resultado / Fecha / T. entrada / T. salida
- Triángulos ▲▼ en vela exacta de entrada
- Círculos para señales bloqueadas
- Líneas M3 punteadas, max 4 por tipo

## REGLA PARA JARVIS
Cuando Diego envíe una imagen/screenshot en el chat:
1. Analizar inmediatamente
2. Guardar análisis completo en `/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/memory/trading_analysis.md`
3. Confirmar que quedó guardado
