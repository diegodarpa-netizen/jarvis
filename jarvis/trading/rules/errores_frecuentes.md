# 🐛 Errores Frecuentes del Código — Historial

> Registro de bugs detectados, sus causas y fixes aplicados.
> Permite evitar regresar a errores ya resueltos.

---

## Error #6 — SL no se actualiza después de entrar (SL "congelado" al momento del fill)
**Detectado:** 04/07/2026 (comparativa screenshot trader humano vs código "XAU Scalp" en `scalping/XAU_Scalping_Strategy.pine`, causa confirmada leyendo `strategies/xau_v9.pine`)
**Síntoma:** El trade ganador se corta con pérdida/breakeven justo antes del tramo grande del movimiento, aunque la entrada fue en la dirección correcta.
**Causa:** `sl_p`/`tp_p` en el bloque `exec_long`/`exec_short` (BLOQUE 8) se calculan UNA SOLA VEZ, en la barra en que se llena la orden (`position_avg_price`), a partir de `gb_low`/`gb_high` en ese instante. `strategy.exit(...)` con ese stop/limit fijo no se vuelve a llamar mientras el trade sigue abierto, aunque `gb_low`/`gb_high` se sigan actualizando en sesión (vía la lógica de `gb_invalidated`, ya existente). Resultado: el SL queda "congelado" en el nivel M3 del momento de entrada y no sigue la estructura mientras el trade corre — viola la "REGLA FUNDAMENTAL — Niveles M3 dinámicos (10/06/2026)".
**Fix aplicado (04/07/2026):** Variables persistentes `active_sl_long/active_tp_long/active_sl_short/active_tp_short` que guardan el SL/TP vigente del trade abierto. Nuevo bloque después de `exec_long`/`exec_short` que, en CADA barra mientras `strategy.position_size != 0`, chequea si `gb_low`/`gb_high` mejoró (subió para BUY, bajó para SELL) respecto al SL activo, y si es así reemite `strategy.exit(...)` con el nuevo stop — **solo ajusta a favor, nunca afloja la protección**. Se resetean las variables a `na` cuando la posición se cierra.
**Versión:** `strategies/xau_v9.pine` (BLOQUE 8, después de línea ~709). **Pendiente:** portar el mismo fix a `codigo1/xau_v9.pine` y `strategies/xau_v9_codigo1.pine` (copias idénticas antes de este fix, ahora desactualizadas) y evaluar si aplica también a `scalping/XAU_Scalping_Strategy.pine` (arquitectura de SL distinta, ver comparativa 04/07/2026 en `strategy_notes.md`).
**Pendiente de probar:** este fix no se validó todavía contra backtest ni en vivo — falta correr `backtest.py` con esta versión antes de usarla con capital real.

---

## Error #7 — Reset de sesión/día usa `dayofmonth(time)` en vez de fecha completa
**Detectado:** 04/07/2026 (Diego pegó `xau_v9.pine` en TradingView el 04/07 y el chart de la sesión 09:00-10:30 NY no mostró NINGUNA entrada, línea M3 ni gray box, a pesar de que el dashboard mostraba "Tendencia M3: BAJISTA" y contadores de trades no-cero — señal de que el estado interno no correspondía a la sesión visible)
**Síntoma:** Chart sin entradas visibles, sin líneas M3, sin gray box — pero el dashboard indica que sí hubo trades ("SL hoy 2/2", "TP hoy 4/2") y una tendencia definida. Contradicción entre lo que muestra el dashboard (estado interno) y lo que se ve en las velas de hoy.
**Causa:** Los 4 resets de sesión/día del archivo (`m3_sess_day`, `gb_day`, `mer_sess_day`, `last_day`/`curr_day` para day_sl/day_tp) comparaban contra `dayofmonth(time)` — que devuelve SOLO el número de día (1-31), sin mes ni año. En un chart con más de ~1 mes de historia cargada, dos sesiones de MESES distintos que caen en el mismo día del mes (ej. 4 de junio y 4 de julio) comparten ese número, y la condición `dayofmonth(time) != <var>` nunca se dispara entre esas dos fechas — el reset de sesión se salta, y `m3_trend`, `gb_high/gb_low`, `m3h1/m3l1`, contadores de MER, y `day_sl/day_tp` pueden arrastrar estado de un mes anterior sin que el trader lo note. Es el mismo problema de "Error #1c" (contaminación de estructura) pero a escala mensual en vez de overnight.
**Nota importante:** `scalping/XAU_Scalping_Strategy.pine` NO tiene este bug — ya usaba correctamente `day_id = year * 10000 + month * 100 + dayofmonth` para su reset diario. Solo afectaba a `xau_v9.pine` (y por herencia, a las copias `codigo1/xau_v9.pine` y `strategies/xau_v9_codigo1.pine`, todavía sin este fix).
**Fix aplicado (04/07/2026):** Nueva variable `day_key = year(time) * 10000 + month(time) * 100 + dayofmonth(time)` calculada una vez en BLOQUE 3, reutilizada en los 4 puntos de reset (reemplaza los 4 usos de `dayofmonth(time)` como clave de comparación). El uso de `dayofmonth(t)` dentro de `f_ddmm()` (formateo de fecha para los labels, no lógica de reset) se dejó sin cambios — ese es correcto tal cual está.
**Versión:** `strategies/xau_v9.pine` (BLOQUE 3, BLOQUE 7/MER, BLOQUE 8).
**Confianza del diagnóstico:** ALTA en que es un bug real y objetivamente incorrecto (confirmado leyendo el código, no solo inferido del screenshot). MEDIA en que sea la ÚNICA causa de "cero entradas visibles" en la sesión que Diego mostró — pendiente confirmar re-pegando el código corregido en TradingView y viendo si aparecen las entradas/líneas M3 en la sesión de hoy.

---

## Error #1 — Entradas prematuras por tendencia overnight
**Detectado:** 04/06/2026
**Síntoma:** 2 entradas en primeros 10 min de sesión antes de que el trader manual entrara
**Causa:** `m3_trend` persiste desde pre-sesión → entra con primera ENV sin esperar estructura
**Fix:** `m3_pivots_sess >= 2` — requiere 2 pivots M3 dentro de sesión antes de operar
**Versión:** XAU v9 (bloque 3)

---

## Error #1g — choc_down/choc_up NO detectaba transición 0→±1 (ROOT CAUSE del BUY incorrecto)
**Detectado:** 07/06/2026 (imagen 9 — comparativa trader humano vs código)
**Síntoma:** Código entra BUY a 09:15 aunque el trader humano vendió @ 4,502.985 (SELL). Misma vela, misma hora, dirección opuesta.
**Causa:** `choc_down = prev_trend == 1 and m3_trend == -1`. En Jun 4, la secuencia fue high(1)→0, low(1)→0, low(2)<low(1)→trend=-1 (prev=0). Como prev_trend==0 y no ==1, choc_down=FALSE. El ChOC real (quiebre bajo del gray box) fue IGNORADO. Luego un HIGH rompió hacia arriba → choc_up (prev=-1→+1) → BUY ❌
**Fix:** Cambiar a `prev_trend != ±1` (acepta transición desde 0 O desde opuesto), + requerir referencia del tipo contrario en sesión:
```pine
choc_up   = prev_trend != 1  and m3_trend == 1  and m3_low_sess
choc_down = prev_trend != -1 and m3_trend == -1 and m3_high_sess
```
**Lógica:** el ChOC del gray box = primera vez que trend alcanza ±1, siempre que ya exista al menos UN pivot del tipo opuesto (= gray box tiene ambos lados). La transición 0→-1 CON high en sesión = quiebre bajista del gray box = SELL.
**Versión:** XAU v9 (bloque 3)

---

## Error #1f — sess_choc_done se activa ANTES de que el gray box esté completo
**Detectado:** 07/06/2026 (imagen 8 — BUY 09:15 en vez de SELL 09:15)
**Síntoma:** BUY a 09:15 aunque estructura final era BAJISTA. La secuencia M3 formó un ChOC ALCISTA (-1→+1) justo cuando sess_both_ok se volvió true → sess_choc_done=true + m3_trend=+1 → BUY disparado. El trader humano esperaba el gray box COMPLETO antes de tomar el quiebre como ChOC real.
**Causa:** `sess_choc_done` se activaba cuando ANY ChOC ocurría en sesión, incluso si el gray box (sess_both_ok) no estaba formado todavía o se formó justo en ese momento.
**Fix:** Agregar `sess_both_ok` como requisito para activar sess_choc_done. Solo cuenta el ChOC que ocurre DESPUÉS de que ambas referencias M3 (alto y bajo) ya existen en la sesión.
```pine
// Antes:
if in_session and (choc_up or choc_down)
    sess_choc_done := true
// Después:
if in_session and sess_both_ok and (choc_up or choc_down)
    sess_choc_done := true
```
**Versión:** XAU v9 (bloque 3)

---

## Error #1e — ENV pattern usa vela PRE-SESIÓN como setup (ROOT CAUSE del 09:01)
**Detectado:** 07/06/2026 (observación del trader: "la decisión es al comienzo de la nueva vela")
**Síntoma:** BUY disparado a las 09:01 (primera vela de sesión) usando la vela 09:00 (pre-sesión) como setup del patrón ENV. El trader humano NUNCA usa una vela pre-sesión como setup.
**Causa:** `pat_env_bull = close[1] < open[1] and f_engulf_bull(...)` — el [1] era la vela 09:00, fuera de sesión. Cumplía la condición pero era inválida.
**Fix:** Agregar `in_session[1]` a ENV y `in_session[1] and in_session[2]` a START. Garantiza que TODAS las velas del patrón son de sesión NY.
**Versión:** XAU v9 (bloque 5)

---

## Error #1d — Primera transición 0→+1 no es ChOC real (FIX DEFINITIVO)
**Detectado:** 07/06/2026 (tercera imagen, con session reset)
**Síntoma:** Con session reset (m3_trend=0 al inicio), la primera transición 0→+1 NO es un ChOC (choc_up requiere prev=-1). Pero sess_both_ok=true se activaba rápido (09:09-09:12) → BUY prematuro seguía disparando → 2 SLs antes de 09:15 → SELL correcto bloqueado.
**Fix definitivo:** `sess_choc_done` — solo se activa cuando hay un ChOC REAL (+1→-1 o -1→+1). La secuencia para Jun 4: trend 0→+1 (09:12, no cuenta) → trend +1→-1 (09:15, ChOC real!) → sess_choc_done=true → SELL permitido a las 09:15.
**Versión:** XAU v9 (bloque 3 y 5 y 7)

---

## Error #1c — M3 overnight contamina estructura de sesión (RAÍZ DEFINITIVA)
**Detectado:** 07/06/2026 (segunda imagen con sess_both_ok)
**Síntoma:** Fondo del chart verde (ALCISTA) a las 09:15 aunque el trader manual ve BAJISTA. El lower low de 09:15 (~4502) era MÁS ALTO que los lows overnight → código no lo vio como lower low → m3_trend nunca flippeó a -1 → SELL nunca disparó.
**Causa raíz:** m3h1/m3l1/m3_trend NO se reseteaban al inicio de sesión. El overnight M3 contaminaba los valores de referencia. El trader manual solo mira la estructura de LA SESIÓN (el gray box = 09:01 en adelante).
**Fix:** Reset total al primer bar de sesión (in_session AND nuevo día): `m3_trend:=0`, `m3h1:=na`, `m3h2:=na`, `m3l1:=na`, `m3l2:=na`. Así los pivots de referencia son SOLO de la sesión actual.
**Versión:** XAU v9 (bloque 3)

---

## Error #1b — BUY prematuro en pullback bajista (Jun 4)
**Detectado:** 07/06/2026 (análisis retrospectivo de Jun 4)
**Síntoma:** Código tomó BUY a ~09:09-09:12 en lo que era un pullback alcista dentro de tendencia BAJISTA general. El trader manual esperó hasta 09:15 y tomó SELL.
**Causa:** `m3_high_sess` se activa al PRIMER M3 high en sesión. El primer pullback alcista (09:00-09:12) formó un higher high → `m3_trend=1`, `m3_high_sess=true` → BUY disparado. Era el pullback del contexto overnight bajista, no una nueva tendencia.
**Fix:** `sess_both_ok = m3_high_sess AND m3_low_sess` → solo permite entradas cuando la sesión formó AMBAS referencias (alto Y bajo M3). El "gray box" del trader manual = estructura completa. Recién al break del rango (ChOC con sess_both_ok=true) se permite entrar.
**Versión:** XAU v9 (bloque 3 y 5 y 7)

---

## Error #2 — Operar en días de alto impacto (NFP)
**Detectado:** 05/06/2026
**Síntoma:** 2 BUY en día de NFP → mercado dominado por impulso del news → 2 SL
**Causa:** Código no tenía conciencia de noticias económicas
**Fix:** Toggle `⛔ Día de noticia roja` + ventana configurable -10/+3 min
**Versión:** XAU v9 (bloque 0)

---

## Error #3 — Pine Script: multi-línea con + en funciones
**Detectado:** Durante desarrollo
**Síntoma:** "end of line without line continuation"
**Causa:** Pine v5 no permite cortar string concatenation con + al final de línea dentro de función
**Fix:** Asignar a variables intermedias (line1, line2...) y concatenar al final
**Versión:** XAU v9 (función f_det)

---

## Error #4 — label.new multi-línea con := dentro de if block
**Detectado:** Durante desarrollo
**Síntoma:** "end of line without line continuation" en label.new con múltiples parámetros
**Causa:** Pine tiene problemas con `:=` + función multi-línea dentro de if block
**Fix:** Calcular args en variables intermedias (det_y, det_txt) y pasar en una sola línea
**Versión:** XAU v9 (bloque 9)

---

## Error #1h — ChOC por PIVOTS M3 NO replica el gray box del trader (FIX DEFINITIVO)
**Detectado:** 07/06/2026 (sesión continua — 6+ iteraciones fallidas con pivot-based ChOC)
**Síntoma:** BUY persistente @ 09:15 en Jun 4 a pesar de todos los fixes previos (session reset, sess_both_ok, sess_choc_done, in_session[1], prev_trend != ±1, in_sess_m3_valid=0909). El código no pudo detectar el ChOC BAJISTA correcto.
**Causa raíz:** La detección de ChOC por pivot M3 (HIGH_2 > HIGH_1 = ALCISTA, LOW_2 < LOW_1 = BAJISTA) NO equivale a lo que el trader humano ve. En Jun 4:
  1. M3 09:06-08: UP (pico a 4514)
  2. M3 09:09-11: DOWN (pullback bajista)
  3. M3 09:12-14: DOWN (continuación bajista) ← trader ve 2 barras DOWN = BAJISTA
  El pivot-based ChOC necesita un "segundo low < primer low". Pero el segundo low puede dispararse DESPUÉS de que un segundo high ya creó un ChOC ALCISTA. La secuencia de pivots no garantiza el orden correcto.
**Fix definitivo:** Reemplazar detección de ChOC por DIRECCIÓN DE CIERRE de barras M3:
  - Rastrear si se vio al menos 1 barra M3 alcista Y 1 bajista en sesión (= gray box)
  - ChOC = 2 barras M3 CONSECUTIVAS en misma dirección DESPUÉS del gray box completo
  - 2 DOWN consecutivas = ChOC BAJISTA; 2 UP consecutivas = ChOC ALCISTA
  - m3_high_sess/m3_low_sess ahora se setean por DIRECCIÓN de barra M3 (no solo por pivot)
**Resultado en Jun 4:**
  09:09: M3[0]=UP, M3[1]=UP → 2UP, falta DOWN → sin ChOC (gray box incompleto)
  09:12: M3[0]=DOWN, M3[1]=UP → 1+1, gray box completo → sin ChOC (distinto)
  09:15: M3[0]=DOWN, M3[1]=DOWN → 2 DOWN + gray box → ChOC BAJISTA ✅ → SELL ✅
**Implementación:** 4 nuevas llamadas request.security (m3_c_cur, m3_o_cur, m3_c_prv, m3_o_prv) + variables saw_m3_bull/saw_m3_bear + gray_box_ready + m3_2bull/m3_2bear
**Versión:** XAU v9 (BLOQUE 2 + BLOQUE 3)

---

## Error #5 — ChOC directo M1 sin confirmación M3 (SESIÓN EN VIVO Jun 10)
**Detectado:** 10/06/2026 — sesión en vivo 09:00-09:15 NY
**Síntoma:** Código entró SHORT ~09:06 mientras Fabian estaba FLAT. Posicion: SHORT abierta prematuramente.
**Causa:** El código detecta ChOC cuando UNA vela M1 cierra fuera del gray box. Eso es demasiado temprano. Fabian espera que el **M3 CIERRE** fuera del gray box para confirmar.
**Evidencia visual (Fabian, 09:10 NY):**
- Gray box: HIGH=4,175 | LOW=4,144
- Precio en 4,151 = DENTRO del box
- Texto de Fabian: "Si el precio TRASPASA este bajo (4,144) → VENTAS por MEC"
- Texto de Fabian: "El precio NO SUPERA el alto M3 (4,175) → COMPRAS por MEC"
- Fabian posicion: FLAT — esperando MEC después de ChOC M3 real
**Regla confirmada:**
1. El ChOC válido = M3 bar cierra FUERA del gray box (no solo M1)
2. Después del ChOC M3 → buscar MEC en M1 (pullback + envolvente)
3. ChOC directo (entrada inmediata al next open) es válido SOLO si el M3 ya cerró afuera
4. Una vela M1 que cierra momentáneamente fuera NO es ChOC real
**Fix necesario:** Antes de disparar choc_direct_bear/bull, verificar que al menos 1 barra M3 YA cerró fuera del gray box en la misma dirección.
**Versión afectada:** XAU v9 (bloque 6/7 — choc_direct logic)

---

## Regla visual — Colores de velas en chart del TRADER HUMANO
**Confirmado:** 08/06/2026
**CRÍTICO para análisis de imágenes:**
- Velas NEGRAS (black body) = ALCISTAS (bullish, close > open)
- Velas BLANCAS (white body) = BAJISTAS (bearish, close < open)
→ Esta es la configuración del tema de TradingView del trader humano
→ Es lo OPUESTO al esquema tradicional (verde=alcista, rojo=bajista)
→ NO afecta la lógica del código (Pine Script usa close/open, no colores)
→ SÍ afecta el análisis visual de los screenshots: al ver una vela BLANCA = bajista ↓

---

## Regla aprendida — TP calculation (09/06/2026)

**El TP NO es 0.9R del SL distance.**

El trader humano usa el **nivel M3 opuesto** como TP:
- SELL → TP = gb_low (piso del gray box) = m3l1
- BUY  → TP = gb_high (techo del gray box) = m3h1

Evidencia del 09/06/2026:
- BUY entrada 4,335.45 | SL 4,329.05 | TP 4,345.55 (= M3 high de sesión, no 0.9R)
- Con 0.9R el TP hubiera sido ~4,341 — incorrecto

**Pendiente:** actualizar cálculo de TP en el código cuando se confirme esta regla en más sesiones.

---

## 🆕 REGLA NUEVA — Reducción de SL cuando dist > 20,000 pips (10/06/2026)

**Detectado:** sesión en vivo 10/06/2026, trade BUY de Fabian a 4,169.685

**Texto exacto de Fabian:**
> "SL de 27.675 pips, por lo tanto se reduce. Recordar que todo SL mayor a 20.000 pips se debe reducir en un 40%"

### Regla:
```
Si dist_SL > 20,000 pips → usar dist_SL × 0.60 (recortar 40%)
Si dist_SL ≤ 20,000 pips → usar dist_SL completo
```

### Ejemplo del 10/06:
- GB low = ~4,142 | Entry BUY = 4,169.685
- Dist original = 27.675 pips (> 20,000 → se reduce)
- Dist reducida = 27.675 × 0.60 = 16.605 → Fabian usó 16.582 pips
- SL real = 4,169.685 - 16.582 = **4,153.103** ✅

### Fix para el código:
```pine
sl_dist_raw = choc_dir == 1 ? entry_price - gb_low : gb_high - entry_price
sl_dist = sl_dist_raw > 20.0 ? sl_dist_raw * 0.60 : sl_dist_raw
sl_price = choc_dir == 1 ? entry_price - sl_dist : entry_price + sl_dist
```

