# 📐 Estructura M3 — Lecciones de Sesiones Reales

> BASE PDF: Plan Técnico XAU.pdf — detección de highs/lows M3

---

## Reglas del PDF (inamovibles)

- Alto M3: vela alcista[2] + vela bajista[1] → `math.max(high[1], high[2])`
- Bajo M3: vela bajista[2] + vela alcista[1] → `math.min(low[1], low[2])`
- Tendencia ALCISTA: nuevo alto M3 > alto M3 anterior (higher highs)
- Tendencia BAJISTA: nuevo bajo M3 < bajo M3 anterior (lower lows)
- ChOC: primer quiebre en dirección contraria al trend actual

---

## ⚡ Aprendizajes de sesiones reales

### Aprendizaje #1 — 04/06/2026
**Situación:** Código entró 2 veces en los primeros 10 min de sesión (09:00-09:10) con tendencia overnight ya seteada. Trader manual esperó ~15 min y tomó el SELL correcto.
**Causa:** `m3_trend` persiste desde pre-sesión. Si había estructura bajista overnight, el código entraba en la primera vela ENV de sesión sin esperar estructura en sesión.
**Fix aplicado v1:** `m3_session_ok` = al menos 1 pivot M3 dentro de sesión. → Insuficiente (pivot de 09:00-09:03 ya contaba).
**Fix aplicado v2:** `m3_pivots_sess >= 2` = al menos 2 pivots M3 dentro de sesión → espera ~12-18 min → más alineado con trader manual.
**Regla nueva:** La estructura M3 debe confirmarse DENTRO de la sesión NY (mínimo 2 pivots) antes de permitir cualquier entrada.

### Aprendizaje #2 — 07/06/2026 (análisis retrospectivo Jun 4)
**Situación:** Jun 4 09:00-09:12: precio subió (pullback en contexto BAJISTA overnight). Código detectó higher high, activó `m3_high_sess=true` y `m3_trend=1` → BUY incorrecto. Trader manual vio el pullback como parte del rango de estructura (gray box ~09:00-09:15) y esperó el break BAJISTA a las 09:15 para entrar SELL.
**Insight clave:** El gray box del trader manual = período donde la sesión forma AMBAS referencias M3 (un alto Y un bajo). El break de ese rango es el ChOC real. No se entra durante la formación del rango.
**Fix aplicado:** `sess_both_ok = m3_high_sess and m3_low_sess` — requiere ambas referencias antes de cualquier entrada. Agregado a MEC-a (bull y bear) y MER (bull y bear).
**Regla nueva:** La sesión debe mostrar estructura completa (alto + bajo M3 confirmados) antes de permitir entradas. El primer pivot en sesión siempre es parte del rango, no la dirección final.

---

## 📋 Lo que Jarvis verifica en cada análisis de chart

Al recibir un screenshot de sesión:
1. ¿Cuándo se formó el primer pivot M3 dentro de sesión?
2. ¿La tendencia detectada coincide con la dirección del movimiento real?
3. ¿Hubo ChOC dentro de sesión o el código usó tendencia overnight?
4. ¿La entrada del código fue antes o después del 2do pivot M3?

---

## ⚡ REGLA FUNDAMENTAL — Niveles M3 dinámicos (10/06/2026)

**Los niveles M3 NO son estáticos durante la sesión.**

Durante la sesión 09:01–10:59, el M3 sigue formando nuevos pivots (altos y bajos).
Cada nuevo pivot M3 REEMPLAZA al anterior como referencia operativa.

### Regla operativa:
1. Ver M3 y M1 SIMULTÁNEAMENTE — siempre
2. Cada vez que M3 forma un nuevo HIGH → actualizar nivel de SELL (nuevo SL y zona de entrada)
3. Cada vez que M3 forma un nuevo LOW → actualizar nivel de BUY (nuevo SL y zona de entrada)
4. Las entradas en M1 son SIEMPRE contra el ÚLTIMO nivel M3 marcado

### Flujo correcto:
```
M3: nuevo pivot HIGH/LOW creado → marcar y actualizar nivel
M1: precio hace pullback al último nivel M3 → buscar ENV o START → entrar
```

### Implicación para el código:
El gray box debe ACTUALIZARSE con cada nuevo pivot M3 durante la sesión.
No solo fijarse con el primer pivot al inicio de sesión.
El código en vivo debe rastrear el ÚLTIMO alto M3 y el ÚLTIMO bajo M3
y usarlos como referencia dinámica para las entradas.

---

## ⚡ REGLA ENTRADA — "Primera vela de contacto" (10/06/2026)

**Aprendida en sesión en vivo. Texto de Fabian:**
> "La primera vela que entra en contacto con el alto M3 no lo supera con cuerpo"

### La regla:
Después de un ChOC M3 bajista:
1. El precio hace pullback hacia el nivel M3 roto (alto o bajo)
2. La PRIMERA vela que TOCA ese nivel M3...
   - Si el CUERPO **no cierra sobre el nivel** = RECHAZO = señal SELL válida
   - Si el cuerpo SÍ cierra sobre el nivel = nivel superado = NO entrar todavía
3. Esta vela de rechazo ES la señal de entrada (o la siguiente vela confirma)

### Diferencia con envolvente clásica:
- No necesita engulfar la vela anterior
- Solo necesita TOCAR el nivel M3 y que el CUERPO NO lo supere
- La mecha puede perforar el nivel, pero el CUERPO decide

### Ejemplo del 10/06/2026:
- Alto M3: ~4,154
- Pullback: precio sube hasta ~4,156 (mecha toca el nivel)
- Cuerpo de la vela cierra en ~4,142 (muy por debajo) = RECHAZO TOTAL
- Señal: SELL en esa vela

### Implicación para el código:
Agregar esta condición de entrada al código en vivo:
- near_level = precio está en zona del nivel M3 roto (±tolerancia)
- body_reject = close del cuerpo NO supera el nivel (para SELL: close < nivel)
- → sig_sell = choc_M3_bear AND near_gb_low AND body_reject
