# Análisis Semanal XAU/USD — Historial

Este archivo persiste entre sesiones. Cada análisis de screenshot se guarda acá.

---

### Sesión EN VIVO | 10/06/2026 — IMG 10:07–10:08 NY — COMPARATIVA v9 vs En Vivo 🔥

**RESULTADO SORPRESA: XAU v9 (código VIEJO) = 0 SL / 2 TP = +1.8R hoy**

#### Dashboard v9 a las 10:08:
- Tendencia M3: BAJISTA
- SL hoy: **0 / 2**
- TP hoy: **2 / 2** ← DOS TPs!
- R semanal: **1.8R**
- Opera hoy: SI
- Posición: SHORT (trade nuevo abierto ~10:05)
- Alto/Bajo M3: 4186.42 / 4173.85

#### Lo que se ve en el chart:
- **Punto VERDE** en la vela envolvente alcista ~09:42 = código detectó el BUY ✅
- **Punto ROJO** en el techo ~09:50 = TP alcanzado ~4,185–4,186 ✅
- Caja TEAL arriba = zona TP del trade BUY
- Caja BURDEOS abajo = zona SL (nunca tocada)
- **Ahora en SHORT** ~10:05 con SL en 4,185.882

#### Comparativa FINAL del día — 10/06/2026:
| | **XAU VIVO (nuevo)** | **XAU v9 (viejo)** | **Diego manual** | **Fabian** |
|---|---|---|---|---|
| Trade 1 (SELL) | ❌ SL -1R | ✅ TP (evitó el SL?) | — | ❌ SL |
| Trade 2 (BUY) | ❌ FLAT | ✅ **TP +0.9R** | ✅ TP +0.9R | ✅ TP +0.9R |
| **Total** | **-1R** | **+1.8R 🏆** | **+0.9R** | **~0R** |

#### 🔑 CONCLUSIÓN CLAVE:
El código v9 viejo DETECTÓ la envolvente alcista a ~09:42 con el punto verde.
El código EN VIVO no la detectó por el gray box estático y ChOC no actualizado.
**El v9 terminó siendo más preciso hoy — pero por razones que hay que entender mejor.**

---

### Sesión EN VIVO | 10/06/2026 — IMG 10:30 NY — ERROR código v2: entradas en lugar equivocado ❌

**Lo que hizo el código v2:**
- ~09:35: SELL ENV → TP ✅ (correcto, tendencia bajista)
- ~09:55: SELL ENV → SL ❌ (INCORRECTO — mercado ya había revertido)
- ~10:00-10:05: CONTACTO SELL × 2 ❌ (nivel equivocado)
- BUY a 09:42: **NUNCA detectado** ❌

**Lo que hizo Fabian:**
- ~09:42: BUY — DOJI BAJISTA + ENVOLVENTE ALCISTA en pullback desde 4,184 → TP ✅

**EL ERROR RAÍZ:**
El código detecta ChOC BAJISTA todo el tiempo (dashboard = BAJISTA).
Nunca flippeó a ALCISTA cuando M3 cerró arriba de 4,184.
→ Nunca buscó BUY patterns.
→ El DOJI + ENVOLVENTE ALCISTA a 09:42 fue ignorado completamente.

**Gray Box actual:** 4186.42 / 4176.2 (sí se actualizó - dinámico funciona ✅)
**ChOC M3:** BAJISTA (el flip a ALCISTA nunca ocurrió durante el impulso - BUG)

**Fix necesario:** revisar condición de ChOC flip — cuándo M3 debe detectar ALCISTA
cuando precio sube de 4,132 → 4,184 (+52 pts en impulso fuerte)

---

### Sesión EN VIVO | 10/06/2026 — IMG 09:51 NY — Dashboard código vs patrón de entrada ⭐

**Screenshot:** sesion_10jun_0951_codigo_dashboard_buy_pattern.png
**Hora:** 09:51 NY | Precio: 4,180.340

#### 🔍 LO QUE SE VE EN EL CÓDIGO (dashboard):
- **ChOC M3:** BAJISTA ❌ (SIGUE DESACTUALIZADO — precio está +24 pts arriba del GB High)
- **Gray Box:** 4156.535 / 4145.085 ❌ (estático — el viejo pivot)
- **Posición:** FLAT (el código no entró en la compra)
- **Pullback:** No

#### 🎯 PATRÓN DE ENTRADA QUE EL CÓDIGO DEBERÍA HABER DETECTADO:

**Zona:** ~09:40–09:44 NY | Nivel: 4,169.745

**Secuencia de velas en M1:**
```
Vela [2]: pullback bajista (precio baja desde 4,175 al área 4,169)
Vela [1]: DOJI / indecisión — cuerpo pequeño, mechas simétricas → NADIE manda
Vela [0]: ENVOLVENTE ALCISTA — cuerpo grande, engulfa la vela anterior → BUY
```
→ Esto es exactamente el **patrón START** (pullback + doji + envolvente)
→ O bien patrón **ENV** si solo se toman las últimas 2 velas (doji + envolvente)

**¿Por qué el código NO entró?**
1. Gray box viejo (4156/4145) → el nivel de pullback que busca es ~4,156, no 4,169
2. ChOC sigue diciendo BAJISTA → código no busca BUY
3. El nuevo nivel M3 (~4,169) nunca fue registrado → código "ciego"

#### Comparativa LEFT (código) vs RIGHT (Fabian):
| | Código XAU VIVO | Fabian |
|---|---|---|
| Entrada | ❌ FLAT (no detectó) | ✅ BUY 4,169.685 |
| Patrón | No reconoció START/ENV | DOJI + Envolvente alcista |
| Motivo | Gray box estático + ChOC no flipped | Dinámica correcta |
| Precio ahora | 4,180 (perdió +10 pts) | +10 pts ganando |

#### 🔑 LECCIÓN CLAVE:
El patrón DOJI + ENVOLVENTE es el START pattern que YA ESTÁ CODED en v2.
El único problema: el nivel de referencia M3 no se actualizó.
**Si el gray box hubiera sido dinámico → el código habría entrado CORRECTAMENTE.**

---

### Sesión EN VIVO | 10/06/2026 — IMG 09:47 NY — BUY MEC ENVOLVENTE ⭐

**Screenshot:** sesion_10jun_0947_fabian_buy_mec.png
**Hora:** 09:47 NY (UTC-4)
**Precio actual:** 4,178.350 (en trade abierto)

#### 🔑 ENTRADA DE FABIAN — BUY MEC a 4,169.685

**Patrón detectado:** Envolvente ALCISTA (bullish engulfing) en M1
**Zona de entrada:** ~09:44–09:45 NY
**Precio de entrada:** 4,169.685

**Estructura del trade:**
- **TP:** ~4,184.685 (+15 pts / 15,000 pips) → RR 0.9
- **SL original:** 27.675 pips (4,141-ish) → MÁS DE 20,000 PIPS → SE REDUCE
- **SL reducido:** 16.582 pips → 4,153.103 (reducción del 40%)
- **Caja azul (upside):** 15,000 pips × 0.9 = zona TP ~4,184
- **Caja gris (downside/SL):** 16,582 pips → 4,153.103

#### 🆕 REGLA NUEVA CRÍTICA — Reducción de SL cuando > 20,000 pips

Texto de Fabian en el chart:
> "SL de 27.675 pips, por lo tanto se reduce. Recordar que todo SL mayor a 20.000 pips se debe reducir en un 40%"
> "Nuevo SL reducido en un 40%. Quedó en 16.582 pips"

**Fórmula:**
```
Si dist_SL > 20,000 pips → SL_real = dist_SL × 0.60 (reducir 40%)
Ejemplo: 27.675 × 0.60 = 16.605 ≈ 16.582 pips
```

#### Comparativa LEFT (código) vs RIGHT (Fabian)

| | Código en vivo v2 | Fabian (humano) |
|---|---|---|
| Detección BUY | ✅ buscaba BUY en pullback desde 4,184 | ✅ entró BUY a 4,169.685 |
| Patrón | ENV / CONTACTO / START | **Envolvente (ENV)** |
| SL | gb_low fijo | gb_low **REDUCIDO 40%** si > 20k pips |
| TP | 0.9R fijo | 0.9R ✅ |
| Resultado | NO ESTABA PEGADO (v2 nuevo) | 🔄 trade abierto, precio en 4,178 |

#### ⚠️ LO QUE EL CÓDIGO NO TENÍA:
1. **Reducción de SL**: cuando SL > 20,000 pips → reducir 40% — **REGLA NUEVA** que falta en el código
2. **Gray box dinámico**: el nuevo GB high era ~4,169 (nivel donde entró) no el viejo 4,156
3. **El pullback fue exacto**: desde 4,184 bajó a ~4,169 → envolvente alcista → BUY

**Estado del trade:** ✅ **TP ALCANZADO ~4,184.811** — Diego replicó manualmente el trade de Fabian y ganó +0.9R

---

## Formato de entrada

```
### Semana YYYY-WXX | Fecha: DD/MM/YYYY
**Screenshot:** nombre_archivo.png
**Análisis:**
- Tendencia M3 detectada: ALCISTA / BAJISTA / NEUTRAL
- Señales generadas: X BUY, Y SELL
- Comparación con estrategia PDF: OK / DESVÍO
- Notas: ...
**Resultado:** X TP, Y SL | WR semana: XX%
```

---

<!-- Los análisis se agregan abajo cronológicamente -->

---

### Semana 2026-W23 | Fecha: 04/06/2026 — ANÁLISIS COMPARATIVO TRADER HUMANO vs CÓDIGO
**Screenshot:** imagen enviada por Diego — chart de Fabian Uade (trader humano)
**Sesión:** NY 08:15–10:15 aprox | Jue 04 Jun 2026

---

#### TRADER HUMANO (Fabian) — lo que hizo:
- **Gray Box** (zona gris): HIGH = **4,515.515** | LOW = **4,504** ← rango del último M3 alcista significativo
- **Señal / Envolvente**: La primera vela bajista (negra) grande que ABRE por debajo de 4,504
  - La vela envolvente es la que INICIA la zona rosa
  - El trader decide entrar al OPEN de esa vela
- **Entrada**: SELL @ **4,502.985** (open de la vela envolvente bajista)
- **SL**: **4,515.515** (techo del gray box = alto M3)
- **TP**: **4,491.655** (0.9R debajo de entrada)
- **Distancia SL**: 12.53 pts | **TP**: 11.27 pts (0.9R)
- **Resultado**: TP alcanzado (~4,491.655)
- **Timing**: Entrada ~10:00 | Salida ~10:09 aprox

#### CÓDIGO XAU v9 — lo que hace (Jun 4, 2026):
- **Entrada**: SELL @ **4,502.985** ← PRECIO CORRECTO ✅
- **Timing fill**: 10:00 open ← CORRECTO ✅  
- **SL**: 4,515.515 ← CORRECTO ✅
- **Label**: "MEC Patron" ← INCORRECTO ❌ (debería ser "ChOC")
- **SL hoy**: 2/2 mostrado → el código tomó trades previos que SL'd antes de la entrada correcta

#### COMPARACIÓN DETALLADA:
| | Trader Humano | Código |
|---|---|---|
| Gray box | 4,504 – 4,515.515 | Igual ✅ |
| Señal | Envolvente bajista a 10:00 | MEC Patron a 09:59 |
| Entrada fill | 4,502.985 @ 10:00 | 4,502.985 @ 10:00 ✅ |
| SL | 4,515.515 | 4,515.515 ✅ |
| TP | 4,491.655 (0.9R) | 4,491.655 (0.9R) ✅ |
| Tipo señal | ChOC directo | MEC Patron ❌ |
| Trades extra | 0 | 2 SL previos ❌ |

#### DIAGNÓSTICO:
- **Precio y timing de la entrada correcta**: MATCH EXACTO ✅
- **Problema 1**: El código toma 2 trades extras antes de la entrada correcta (2 SLs)
  - Causa: gray box pequeño temprano → ChOC early → SL → invalidación → nuevo ChOC → SL → MEC
- **Problema 2**: La entrada se clasifica como "MEC Patron" en vez de "ChOC"
  - Causa: cuando la entrada correcta dispara, m3_trend ya es -1 (de un ChOC previo que no se invalidó a tiempo), entonces choc_down no re-dispara y solo MEC-A satisface

#### CONCLUSIÓN TP:
- TP = 0.9R es lo que usa el trader humano en Jun 4 ← confirma que NO siempre es M3 opposite level
- Usar 0.9R por ahora (comportamiento actual del código ✅)

#### PENDIENTE:
- Verificar que con el nuevo fix (barra M3 directa) el código entre en ChOC en Jun 4
- Comparar Jun 3 con código

---

### Semana 2026-W23 | Fecha: 03/06/2026 — ANÁLISIS TRADER HUMANO
**Screenshot:** imagen enviada por Diego — chart de Fabian Uade (trader humano)
**Sesión:** NY | Mié 03 Jun 2026

#### TRADER HUMANO (Jun 3):
- **Gray Box**: HIGH = **4,466.205** | LOW = **4,453.905** ← rango del último M3 alcista
- **Tipo señal**: **MEC con patrón envolvente** (ChOC + pullback + envolvente bajista)
- **Secuencia**:
  1. Gray box formado: 4,453.905 – 4,466.205
  2. ChOC DOWN → precio cierra bajo 4,453.905
  3. Pullback al nivel roto (~4,453.905)
  4. Envolvente bajista en el pullback → entrada SELL
- **Entrada**: ~**4,453.905** (al nivel del gray box low roto)
- **SL**: 4,466.205 → distancia = 12.3 pts
- **TP**: 4,442.797 → 0.9R = 11.108 pts ✅
- **Resultado**: **TP** ✅

#### PENDIENTE COMPARAR:
- Navegar a Jun 3 en TradingView y capturar screenshot del código
- Verificar que código detecte: gray box 4,453.905-4,466.205, MEC-A, entrada ~4,453.905, TP ~4,442.797

---

### Semana 2026-W24 | Fecha: 10/06/2026 — SESIÓN EN VIVO + COMPARATIVA FABIAN
**Sesión:** NY 09:01–10:59 | Mié 10 Jun 2026

#### FABIAN (trader humano) — 09:10 NY:
- **Gray box**: HIGH = **4,175** | LOW = **4,144** (M3 pivot del rebote 08:30)
- **Posición a las 09:10**: **FLAT** — no entró
- **Plan explícito** (texto en su chart):
  - "Si el precio TRASPASA este bajo (4,144) → VENTAS por MEC"
  - "El precio no supera el alto M3 (4,175) → COMPRAS por MEC"
- **Confirmación**: Fabian espera M3 cierre FUERA del gray box → busca MEC en M1

#### CÓDIGO XAU v9 — 09:10 NY:
- **Posición**: SHORT abierto ~09:06 ❌
- **Causa**: ChOC directo en M1 (vela M1 cerró bajo ~4,148) sin esperar M3 confirmation
- **SL**: ~4,156 | **TP**: ~4,148
- **El código se apuró** — entró antes de que Fabian viera una señal válida

#### COMPARACIÓN:
| | Fabian | Código |
|---|---|---|
| Gray box | 4,144 – 4,175 ✅ | Similar (4,148-4,172?) |
| Posición 09:10 | **FLAT** ✅ | SHORT ❌ |
| Condición entrada | M3 cierra < 4,144 | M1 cierra < ~4,148 |
| Tipo entrada | MEC (espera envolvente) | ChOC directo |

#### REGLA #2 APRENDIDA HOY — Primera vela de contacto:
**Texto Fabian:** "La primera vela que entra en contacto con el alto M3 no lo supera con cuerpo"
- Pullback toca el nivel M3 roto con MECHA pero CUERPO no cierra sobre él = rechazo = SELL
- Diferente a envolvente clásica — solo requiere contacto + rechazo de cuerpo

#### REGLA #1 APRENDIDA HOY (crítica):
**El ChOC directo solo es válido si el M3 ya cerró fuera del gray box.**
Una vela M1 que cruza momentáneamente el nivel NO es señal suficiente.
Fabian SIEMPRE espera el M3 para confirmar, y LUEGO busca el MEC en M1.

---

### Semana 2026-W24 | Fecha: 09/06/2026 — M3 LIVE JUN 9
**Screenshot:** imagen enviada por Diego — M3 chart Jun 9 2026 (12:26 UTC-4)
**Sesión:** NY | Mar 09 Jun 2026

#### OBSERVACIONES M3 JUN 9:
- **Tendencia**: Bajista clara desde 09:00 (~4,420) hasta 4,353 al momento del screenshot
- **Señal detectada**: SELL → TP hit ✅ (label "▼ TP +0.02" visible ~10:15-10:20)
- **Precio TP hit**: ~4,355 aprox
- **Profit mostrado**: "+0.02" — muy pequeño (posible bug de cálculo TP o qty muy pequeña)
- **Dashboard (lado derecho)**: no visible en este screenshot
- **PENDIENTE**: Verificar por qué el profit es "+0.02" (¿qty_type mal configurada? ¿TP demasiado cercano?)
- **Dots visibles**: múltiples envolventes bajistas (rojo/naranja/violeta) y alcistas (verde/teal) marcados correctamente

#### ANÁLISIS LEFT (código) vs RIGHT (trader humano):
- No hay imagen del trader humano para Jun 9 para comparar
- El código SÍ entró SELL y llegó a TP — lógica de entrada funcionando ✅
- Issue: "+0.02" profit es sospechosamente pequeño

---

### Semana 2026-W23 | Fecha: 07/06/2026 (Hoy - Domingo, chart del día)
**Screenshot:** chat — XAU v9 con fix m3_pivots_sess >= 2
**Sesión:** NY 09:01–10:59 | Jun 07, 2026

**Código XAU v9 — resultado:**
- Tendencia M3 detectada: **ALCISTA** (verde) ← PROBLEMA CLAVE
- SL hoy: 2/2 | TP hoy: 0/1 | R semanal: -2/-2R | Opera hoy: NO
- Entradas visibles: 2 BUY alrededor de 09:35 (~4503) y 10:15 (~4494)
- Ambas entraron BUY basadas en M3 ALCISTA → ambas hit SL

**Movimiento real del mercado:**
- 08:45–09:45: rango alcista, precio sube de ~4500 a ~4515 → M3 detectó ALCISTA ✅ (correcto en ese momento)
- 10:00 en adelante: caída brutal, precio cae de ~4515 a ~4472 (-43 puntos = -4300 pips)
- La "estructura ALCISTA" de la primera hora fue una trampa / distribución

**Comparación con fix aplicado:**
- ✅ MEJORA: el filtro m3_pivots_sess >= 2 funcionó → entradas se movieron de 09:00-09:10 a 09:30-09:45
- ❌ AÚN INSUFICIENTE: las 2 entradas siguen siendo BUY en dirección equivocada

**Diagnóstico raíz:**
- El mercado tuvo estructura M3 ALCISTA legítima en primera hora → el código la leyó CORRECTAMENTE
- Pero fue una estructura falsa (distribución antes de caída) → ambos BUY hit SL
- NO es un bug de detección: el código hizo lo correcto según las reglas del PDF
- ES una limitación natural: la estrategia acepta hasta 2SL/día (Escenario 3)

**Verificación en PDF — Plan Operativo:**
✅ CONFIRMADO: "No está permitido mantener una orden abierta durante NFP (USD)"
✅ "En noticias de alto impacto (rojo), no abrir/cerrar en ventana -10min a +3min de publicación"
✅ NFP del 5 Jun: 172k vs 88k esperado → USD muy fuerte → oro cayó 43 puntos
✅ El Plan Operativo dice Forex Factory como única fuente de horarios de noticias
→ CONCLUSIÓN: El código tomó 2 BUY en un día de NFP dominado por el news. BUG A CORREGIR.

**Comparación vs Jun 4:**
- Jun 4: 2 SL prematuros → código entró ANTES de estructura → BUG corregido
- Jun 7: 2 SL con estructura ALCISTA legítima → mercado revirtió → limitación normal de estrategia

**Próximos pasos código:**
- [x] Triángulos ▲▼ en vela de entrada → implementado
- [x] Círculos para señales potenciales bloqueadas → implementado
- [x] Líneas M3 extendidas con extend.right → implementado (luego ajustado a +60 fijo)
- [x] Líneas limpias sin saturación → implementado (max 4 por tipo)
- [ ] PENDIENTE CRÍTICO: Dirección de entrada incorrecta — código toma BUY, trader manual toma SELL a las 09:15

### 📸 IMAGEN 7 — Jun 4 2026 (21:28 UTC-4) — OBSERVACIÓN CLAVE DEL TRADER
**Observación:** "la toma de decisión es al comienzo de la nueva vela, por qué lo tomás antes?"

**RESPUESTA — Root cause del BUY 09:01:**
El patrón ENV usa close[1] y open[1] (vela anterior). A las 09:01:
- close[1] = la vela de las 09:00 (PRE-SESIÓN) → era alcista ✅ (cumple condición)
- La vela 09:01 = envolvente alcista ✅
- El código usa la vela PRE-SESIÓN como setup → ENTRY inválida

El trader humano NUNCA usaría una vela pre-sesión como setup.
Entra al COMIENZO de la nueva vela porque el patrón completo (setup + envolvente)
ocurrió DENTRO de la sesión.

**FIX:** Agregar `in_session[1]` a todos los patrones ENV y START.
- `pat_env_bull = close[1] > open[1] AND in_session[1] AND f_engulf_bull(...)`
- Esto garantiza que la vela [1] (setup) también estaba dentro de la sesión.
- A las 09:01: in_session[1] = FALSE (09:00 era pre-sesión) → NO ENTRA ✅
- A las 09:15: in_session[1] = TRUE (09:14 era en sesión) → ENTRA cuando el patrón se forma ✅

### 📸 IMAGEN 6 — Jun 4 2026 (21:18 UTC-4) — PRIMER TP ✅ CON DESDE FIX
**PROGRESO SIGNIFICATIVO — Comparativa vs Trader Humano**

| | Trader Humano (referencia) | Código XAU v9 |
|---|---|---|
| Dirección | SELL ✅ BAJISTA | BUY ❌ → SL + SELL ✅ → TP |
| Entrada 1 | SELL 09:15 @ ~4502.50 | BUY 09:01 @ ~4500 → SL a 09:54 ❌ |
| Entrada 2 | — | SELL 10:24 @ ~4490 → TP a 10:42 ✅ |
| Resultado | +0.9R | -1R + 0.9R = **-0.1R neto** |
| Tendencia | BAJISTA ✅ | BAJISTA ✅ (corregido!) |
| Patrón | MEC-A BAJISTA | MEC-A BAJISTA ✅ (mismo!) |

**SIMILITUDES con trader humano:**
- Ambos usan MEC-A Patron ✅
- Ambos detectan estructura BAJISTA ✅  
- Ambos cierran con TP ✅
- Niveles M3: verde 4512, rojo 4502/4495 ✅ (idénticos al manual)

**DIFERENCIAS a corregir:**
1. BUY prematuro a las 09:01 — NO debería disparar (sess_choc_done debería bloquearlo)
2. SELL a las 10:24 vs manual a las 09:15 — delay de ~1:10hs
3. El trader humano tomó LA PRIMERA oportunidad BAJISTA (09:15 gray box break)
   El código la perdió y tomó la segunda válida (10:24 continuación bajista)

**Dashboard:**
- Tendencia M3: BAJISTA ✅
- SL hoy: 1/2 | TP hoy: 1/1 | R semanal: -0.1R (mejora de -2R a -0.1R!)
- El formato de labels (Estructura/Posicionamiento/Ejecución/Resultado/Fecha/Tiempo) ✅ MANTENER

**PRÓXIMAS CORRECCIONES:**
1. Fix BUY 09:01 — investigar por qué sess_choc_done no bloquea esa entrada
2. Acercar SELL a las 09:15 (el ChOC +1→-1 debería ocurrir antes)

### 📸 IMAGEN 5 — Jun 4 2026 (21:12 UTC-4) — TENDENCIA BAJISTA ✅
**PROGRESO:** Tendencia M3 ahora muestra **BAJISTA** ← session reset funcionando correctamente
- SL hoy: 2/2 | R semanal: -2/-2R (Jun 7 data)
- Alto/Bajo M3: 4345.38/4331.16 (Jun 7)
- Círculos verdes en 09:15-09:40 → señales BUY potenciales bloqueadas
- UN círculo naranja en ~10:30 → SELL potencial bloqueado
- Fondo BAJISTA (rojo) visible desde ~09:40-11:00 ← correcto
- SIN ▼ SELL → sigue bloqueado por weekly limit de días anteriores

**DIAGNÓSTICO:**
Session reset funciona (trend = BAJISTA). El único obstáculo: week_r ya viene en -2R
de sesiones anteriores (Jun 1-3) → can_trade=FALSE desde las 09:01 de Jun 4.
FIX: agregar parámetro `desde` en el código para resetear week_r desde esa fecha.

### 📸 IMAGEN 4 — Jun 4 2026 con sess_choc_done aplicado (20:40 UTC-4)
**Dashboard (Jun 7 data, siempre muestra el último bar):**
- Tendencia M3: ALCISTA (Jun 7 tendencia)
- SL hoy: 2/2 | R semanal: -2/-2R | Opera hoy: NO (Jun 7)

**Chart visible = Jun 4 sesión (precios ~4500-4515):**
- Círculos verdes en 09:05, 09:15, 09:25, 09:30 → BUY potenciales bloqueados
- Círculo rojo en ~10:30 → SELL potencial bloqueado
- SIN triángulos ▲▼ → código NO operó en toda la sesión Jun 4
- Fondo ALCISTA (verde) visible desde ~09:30

**DIAGNÓSTICO DEFINITIVO:**
El código NO operó en Jun 4 por `week_r <= -2.0` — la semana ya tenía -2R acumulado
de las sesiones del Lun Jun 1 + Mar Jun 2 + Mié Jun 3 ANTES de que llegara el Jue Jun 4.
Por eso `can_trade = false` desde las 09:01 → todas las señales aparecen como círculos.

Las sesiones previas (Jun 1-3) siguen tomando entradas incorrectas con el código antiguo
→ acumulan pérdidas → el weekly limit bloquea Jun 4 completamente.

**PRÓXIMO PASO CRÍTICO:**
Para verificar que el fix funciona en Jun 4:
→ Cambiar fecha inicio del backtest a Jun 4 (o Jun 2) en TradingView
→ Esto resetea week_r a 0 y permite ver si el SELL ▼ dispara a las 09:15
→ Si dispara: el fix de sess_choc_done funciona ✅
→ Si no: seguir ajustando

### 📸 IMAGEN 3 — Jun 4 2026 con session reset aplicado (20:24:50 UTC-4)
**Estado:** Código con session reset + sess_both_ok

**Comparativa:**
- Círculos verdes 09:15-09:45 → BUY bloqueados (can_trade=FALSE)
- TODAVÍA SIN ▼ SELL a las 09:15
- CAUSA RAÍZ FINAL: el primer cambio de tendencia en sesión (0→+1) NO es un ChOC real
  → m3_trend va 0→+1 (ALCISTA) antes de ir +1→-1 (BAJISTA real)
  → En el momento 0→+1: sess_both_ok=TRUE, ENV bull posible → BUY prematuro → SL
  → A las 09:15 ya hay 2 SLs → can_trade=FALSE → SELL bloqueado (círculo verde)

**FIX DEFINITIVO:** `sess_choc_done`
- La primera transición 0→+1 NO es un ChOC real (no hubo tendencia opuesta previa)
- El ChOC REAL ocurre cuando el trend ya establecido CAMBIA: +1→-1 o -1→+1
- Solo DESPUÉS del primer ChOC real en sesión → permitir entradas
- Para Jun 4: choc_down a las 09:15 (+1→-1) → sess_choc_done=true → SELL ✅

### 📸 NUEVA IMAGEN — Jun 4 2026 con sess_both_ok aplicado (20:24:50 UTC-4)
**Estado:** Código con fix `sess_both_ok` ya aplicado

**Chart izquierdo (nuevo código):**
- Líneas M3: verde ~4512.50, rojo ~4502.50 / ~4495 / ~4491.50 ✅
- Círculos verdes en 09:15-09:25 → BUY potenciales bloqueados (can_trade=FALSE)
- UN círculo rojo en ~10:30 (SELL potencial bloqueado más tarde)
- **SIN triángulo ▼ SELL a las 09:15 → EL CÓDIGO SIGUE SIN TOMAR LA DECISIÓN**
- Los 2 SLs se tomaron ANTES de 09:15 (no visibles, fuera del rango del chart)
- El fondo del chart en la zona de sesión es VERDE (m3_trend=ALCISTA) → PROBLEMA RAÍZ

**Root cause identificado (DEFINITIVO):**
- El código NO resetea m3h1/m3l1/m3_trend al inicio de sesión
- Entre 00:00 y 09:00, el M3 overnight sigue actualizando m3h1/m3l1
- A las 09:01 ya hay valores overnight → m3_trend podría ser +1 desde antes
- La primera ENV bull en sesión → BUY prematuro (incluso con sess_both_ok)
- El lower low a las 09:15 (~4502) es MÁS ALTO que los lows overnight → NO flip a BAJISTA
- Por eso el fondo sigue VERDE (ALCISTA) a las 09:15 mientras el manual ve BAJISTA

**FIX NECESARIO:** Reset total al inicio de sesión (09:01):
- `m3_trend := 0`, `m3h1 := na`, `m3h2 := na`, `m3l1 := na`, `m3l2 := na`
- Solo estructura DENTRO DE SESIÓN determina dirección
- Previene que la tendencia overnight contamine la lectura de sesión

### 📸 REFERENCIA GUARDADA — Jun 4 2026 (imagen de comparación permanente)
**Timestamp foto:** 20:16:42 UTC-4

**CHART DERECHO (trader manual) — REFERENCIA EXACTA:**
- Día: Jueves 04 Jun 2026
- Entrada: SELL a las **09:15** at **~4502.50**
- Gray box: rango 09:00-09:15, techo ~4513, piso ~4502.50
- SL: ~4513 (techo del gray box) → distancia ~10.50 pts
- TP: ~4491.46 → hit ✅ (RR 0.9 × 10.5 = ~9.45 pts abajo)
- RR: 0.9
- La entrada es exactamente cuando el precio ROMPE el piso del gray box
- El pink area (SELL zona) va desde 09:15 hasta TP hit ~10:00

**CHART IZQUIERDO (código XAU v9) — ESTADO PRE-FIX:**
- SL hoy: 2/2 | TP hoy: 0/1 | R semanal: -2/-2R
- Líneas M3: verde ~4512.50, rojo ~4502.50 / ~4495 / ~4492.50 ✅ coinciden con manual
- Círculos verdes en 09:15-09:25 y 09:40-09:45 → señales BUY bloqueadas por can_trade=FALSE
- Los 2 SLs se tomaron ANTES de 09:15 (probablemente 09:01-09:12)
- La dirección de las 2 entradas perdedoras era BUY (tendencia ALCISTA detectada por código)

**DIFERENCIAS CRÍTICAS:**
| Punto | Manual ✅ | Código ❌ |
|-------|-----------|-----------|
| Dirección | SELL a las 09:15 | BUY a las 09:01-09:12 |
| Timing | Espera gray box completo | Entra al primer pivot |
| Resultado | TP ✅ | 2 SL → límite activado |

**FIX APLICADO POST-IMAGEN:** `sess_both_ok = m3_high_sess AND m3_low_sess`
→ Requiere AMBAS referencias (alto Y bajo M3 en sesión) antes de permitir cualquier entrada
→ Imita el gray box del trader manual

### Comparativa detallada 07/06/2026 (screenshot código vs manual Jun 4)
**Izquierda (código):**
- Líneas M3: verde ~4512 (alto), rojo ~4502 / ~4494 / ~4492 (bajos) ✅ match con manual
- Círculos verdes en 09:15-09:25 → señales SELL potenciales detectadas pero bloqueadas
- BUY entries en 09:30-09:45 (m3_trend ALCISTA) → ambas hit SL → 2/2
- El código detectó la estructura ALCISTA por los higher highs de 09:00-09:45

**Derecha (trader manual):**
- SELL entry en 09:15 a ~4502
- Gray box = rango de consolidación M3 (09:00-09:15) entre ~4502-4508
- Break BAJISTA debajo del box → ENV pattern → SELL
- TP hit ~4491

**Root cause del desvío:**
Los círculos en 09:15-09:25 CONFIRMAN que el código detectó señales SELL válidas pero las bloqueó.
El bloqueo fue porque can_trade=FALSE en ese momento → el código ya había tomado 2 BUY SLs
antes de las 09:15 (probablemente a 09:01-09:12 con tendencia pre-sesión).
→ La secuencia fue: 2 SLs rápidos al inicio → límite activado → SELL correcto bloqueado

**PRÓXIMA FIX:**
Los 2 BUY prematuros a 09:01-09:12 son la causa raíz. Aunque m3_high_sess requiere HIGH
en sesión, la detección puede estar usando datos de la primera M3 vela que arranca exactamente
a las 09:00 (disponible en 09:01). Necesito investigar con backtest exacto qué vela activó
los primeros 2 BUY.


---

### Semana 2026-W23 | Fecha: 04/06/2026 (Jueves)
**Screenshots:** chat — izquierda: código XAU v9 | derecha: decisión manual misma sesión
**Sesión:** NY 09:01–10:59 | Timeframe: M1 + M3

**Código XAU v9 — resultado:**
- Tendencia M3: BAJISTA (fondo rojo en chart)
- Alto/Bajo M3: 4330.79 / 4322.01
- Señales generadas: 2 entradas → 2 SL, 0 TP
- Límite diario: Escenario 3 activado (2SL) → Opera hoy: NO
- R semanal: -2R / -2R → límite semanal alcanzado → dejó de operar

**Decisión manual — resultado:**
- SELL entrada ~4502, RR 0.9 (correcto según PDF)
- Dirección: bajista ✅
- Resultado: TP alcanzado ~4491-4492 ✅
- Operación ganadora

**Diagnóstico del desvío — CRÍTICO:**
- El código entró 2 veces ANTES de que la estructura bajista fuera clara
- Tomó 2 SL consecutivos → activó límite diario
- Cuando apareció el SELL correcto (el que tomó el trader manual) el código ya estaba bloqueado por límites
- El problema NO es la detección de la señal final — es que entra anticipado en estructuras incompletas

**Hipótesis de causa:**
- Las 2 primeras entradas probablemente fueron ENV o MER prematuros, sin confirmación suficiente de estructura M3
- El Patrón START (que requiere indecisión[1]) probablemente habría evitado esas entradas anticipadas
- Posible mejora: aumentar el filtro de confirmación de estructura antes de permitir MER/ENV en primeras barras de sesión

**Acción pendiente para el código:**
- [ ] Revisar en backtest cuáles fueron las 2 entradas perdedoras de ese día (hora exacta)
- [ ] Verificar si eran MER o ENV sin estructura suficiente
- [ ] Evaluar agregar filtro: mínimo N barras de sesión antes de permitir MER
- [ ] Comparar con reglas del Plan Técnico PDF — ¿hay condición de estructura mínima para MER?


---

### Semana 2026-W23 | Fecha: 04/06/2026 (Jueves) — IMAGEN 8 — BUY 09:15 TP + SELL BLOQUEADO
**Screenshot:** chat — Jun 07, 2026 21:34 UTC-4 — XAU v9 con fix sess_choc_done + in_session[1]
**Sesión:** NY 09:01–10:59

**Código XAU v9 — resultado:**
- Tendencia M3 al cierre: BAJISTA ▼ (dashboard confirma)
- SL hoy: 0/2 | TP hoy: 1/1 | R semanal: 0.9/-2R | Opera hoy: NO
- Entrada: BUY ▲ MEC-A a las 09:15 → TP a las 09:37
- Label detalle visible: Estructura: Alcista | Posicionamiento: Compra | Ejecucion: MEC Patron | Resultado: TP | Fecha: 04/06/2026 | T. entrada: 09:15 | T. salida: 09:37
- Señal SELL visible (~09:30) → BLOQUEADA por límite diario (TP 1/1 ya alcanzado)
- Gran caída de 10:00 a 10:45 (~-30 pts) → todas las oportunidades SELL bloqueadas por límite

**Comparación con trader humano:**
- Trader humano: SELL 09:15 @ ~4502.50 → TP ~4491 (+0.9R) ✅
- Código: BUY 09:15 @ ~4502 → TP 09:37 (+0.9R) ✅ (mismo timing, DIRECCIÓN OPUESTA ❌)

**Diagnóstico ROOT CAUSE — NUEVO:**
El código entra BUY a las 09:15 porque la PRIMERA secuencia M3 en sesión fue:
  1. M3 alto(1) se forma → m3h1 = X
  2. M3 bajo(1) se forma → m3l1 = Y  
  3. M3 alto(2) > M3 alto(1) → m3_trend = +1 (0→+1, NO es ChOC todavía)
  4. M3 bajo(2) < M3 bajo(1) → m3_trend = -1 (ChOC!: +1→-1) → sess_choc_done = true
  
  PERO: si la secuencia fue alternada (bajo primero, alto encima = ChOC ALCISTA):
  1. M3 bajo(1) → m3l1 = Y
  2. M3 bajo(2) < M3 bajo(1) → m3_trend = -1 (0→-1)
  3. M3 alto(1) → m3h1 = X; m3_high_sess = true → sess_both_ok = TRUE
  4. M3 alto(2) > M3 alto(1) → m3_trend = +1 → choc_up (-1→+1) → sess_choc_done = TRUE + ALCISTA!
  → BUY habilitado AUNQUE la dirección final es bajista
  
**FIX IDENTIFICADO:**
`sess_choc_done` debe activarse SOLO cuando `sess_both_ok` YA ES TRUE al momento del ChOC.
Si el ChOC ocurre ANTES de que se forme el gray box completo (ambos M3 high y low), NO cuenta.
  
  Código actual:
  ```if in_session and (choc_up or choc_down)```
  
  Fix propuesto:
  ```if in_session and sess_both_ok and (choc_up or choc_down)```
  
  Lógica: el trader humano espera que el RANGO de la sesión esté formado (gray box = ambas referencias).
  Solo DESPUÉS de eso, el primer quiebre de ese rango = ChOC real que habilita entradas.
  Si el ChOC ocurre mientras el rango aún no está completo → no es el ChOC del gray box.

**Otras oportunidades visibles en sesión:**
1. SELL ~09:30 — bloqueado por límite diario (TP ya tomado) → señal válida pero no ejecutada
2. SELL ~09:45-10:00 — caída grande, ~20 pts potencial → bloqueado por límite
3. SELL continuación 10:00-10:45 — caída brutal, múltiples señales → todas bloqueadas
4. El día tenía al menos 3-4 oportunidades de SELL post gray-box, todas en dirección correcta

**Resultado del día si hubiera entrado SELL correcto a 09:15:**
- +0.9R (como el trader humano)
- Opera hoy: NO post-TP (límite Escenario 1) → solo 1 operación, la correcta


---

### Semana 2026-W23 | Fecha: 04/06/2026 — IMAGEN 9 — Comparativa trader humano vs código
**Screenshot:** chat — Jun 07, 2026 21:44 UTC-4 — comparativa lado a lado
**Izquierda:** XAU v9 código | **Derecha:** Trader humano

**Código (izquierda):**
- BUY ▲ MEC-A a las 09:15 → TP 09:37
- Label: Estructura Alcista / Compra / MEC Patron / TP / 04/06/2026 / entrada 09:15 / salida 09:37
- Dashboard: SL 0/2, TP 1/1, R 0.9/-2R, Opera hoy: NO
- Alto/Bajo M3: 4318.12 / 4310.64

**Trader humano (derecha):**
- SELL a las 09:15 @ **4,502.985** (precio exacto de entrada)
- Gray box visible: dashed rectangle ~09:01-09:12 rango ~4503-4514
- Trade en rojo/rosa descendente → TP alcanzado ~4490-4491
- R: 0.9R

**Diferencia crítica:**
- Mismo timing (09:15), misma vela, DIRECCIÓN OPUESTA
- Código: BUY | Trader humano: SELL @ 4,502.985

**Root cause identificado (Error #1g):**
La transición m3_trend 0→-1 NO era detectada como ChOC por el código.
choc_down requería prev_trend==+1, pero prev_trend era 0 en esa transición.
Secuencia real Jun 4:
  HIGH(1) → m3h1=4514, trend=0
  LOW(1)  → m3l1=4503, trend=0
  LOW(2) < 4503 → trend=-1, prev=0 → choc_down=FALSE (0!=1) → ¡ChOC NO detectado!
  Luego: HIGH(2) > 4514 → trend=+1, prev=-1 → choc_up=TRUE → BUY ❌

**Fix aplicado (Error #1g):**
choc_up   = prev_trend != 1  and m3_trend == 1  and m3_low_sess
choc_down = prev_trend != -1 and m3_trend == -1 and m3_high_sess
→ Ahora LOW(2) < gray box bottom con m3_high_sess=true → choc_down=TRUE → SELL ✅
→ Entrada esperada: SELL a 09:15 @ open de vela = ~4,502.985

**Otras oportunidades en sesión:**
1. 09:30-09:37 área: posible MEC-A SELL continuación (bloqueado por límite tras TP)
2. 09:45-10:00: inicio caída grande → MEC-A o MEC-B BAJISTA
3. 10:00-10:15: continuación bajista, señales múltiples
4. 10:30-10:45: caída final a ~4482
→ El día completo era BAJISTA con 3-4 oportunidades SELL post gray-box


---

### Semana 2026-W23 | Fecha: 04/06/2026 — IMAGEN 10 — Referencia entrada exacta trader humano
**Screenshot:** chat — Jun 07, 2026 — comparativa con dashboard parcial
**Izquierda:** XAU v9 (TODAVÍA con BUY 09:15 → TP — fix anterior, no el último)
**Derecha:** Trader humano — "Fabiancarreroa creado con TradingView.com, el Jun 04, 2026 10:09 UTC-4"

**Punto exacto que Diego quiere replicar:**
- SELL entrada: 09:15 | precio: ~4,502.985
- Gray box derecha: zona gris rectangular arriba (~09:12-09:15), rango ~4503-4514
- Trade rosa/rojo descendente desde 09:15 hasta ~09:37-09:45
- TP visible en la parte baja del rectángulo rosa
- Resultado: +0.9R

**Estado del código en esta imagen:**
- SIGUE con BUY en vez de SELL → fix choc_down (Error #1g) todavía NO fue aplicado/pegado
- El dashboard está cortado (no muestra valores completos)

**Acción pendiente:**
El código en portapapeles tiene el fix correcto (Error #1g). Pegar en TradingView.
Resultado esperado:
- NO BUY a las 09:15
- SELL a las 09:15 @ ~4,502.985
- TP a las ~09:37 (como la imagen del trader humano)
- Estructura bajista confirmada, gray box visible en código


---

### Semana 2026-W23 | Fecha: 04/06/2026 — IMAGEN 11 — BUY sigue en 09:15 (fix choc insuficiente)
**Screenshot:** chat — Jun 07, 2026 21:55 UTC-4 — Fix choc aplicado pero SIGUE BUY
**Código (izquierda):** BUY ▲ MEC-A 09:15 → TP 09:37 → SIGUE IGUAL ❌

**Diagnóstico ampliado — Root Cause REAL:**
Los pivots M3 detectados en los PRIMEROS MINUTOS de sesión (09:01-09:08) usan datos pre-sesión.

Cómo funciona request.security con M3:
  - M1 bar 09:01-09:02: last M3 bar confirmado = 08:57-08:59 (PRE-SESIÓN)
  - M1 bar 09:03-09:05: last M3 bar confirmado = 09:00-09:02 (MIX pre/sesión)
  - M1 bar 09:06-09:08: last M3 bar confirmado = 09:03-09:05 (incluye 09:03 inicio sesión)
  - M1 bar 09:09+: last M3 bar confirmado = 09:06-09:08 (TOTALMENTE en sesión)

Los pivots detectados a 09:03 y 09:06 incluyen barras M3 pre-sesión (08:57-08:59 y 09:00-09:02).
Aunque m3h1/m3l1 se resetean a na a las 09:01, los primeros valores que se asignan son de pivots
contaminados → gray box mal construido → ChOC dispara en dirección incorrecta.

**Secuencia real con contaminación pre-sesión:**
  09:03: m3_low_raw (pre-sesión) → m3l1 = 4499 (low pre-sesión), m3_low_sess=true
  09:06: m3_high_raw (sesión inicial) → m3h1 = 4514, m3_high_sess=true
  09:09: m3_high_raw(2) > 4514 → trend=+1, prev=0, m3_low_sess=true → choc_up=TRUE → BUY ❌

**Fix aplicado (bloque 3 completo):**
- Agregar `in_sess_m3_valid = 0909-1059` para procesar M3 solo desde 09:09
- A 09:09, ambas M3 reference bars (09:03-05 y 09:06-08) son de sesión → datos limpios
- Timeline resultante Jun 4:
  09:09: HIGH(1)=4514 → m3h1=4514, m3_high_sess=true
  09:12: LOW(1)=4503  → m3l1=4503, m3_low_sess=true, sess_both_ok=true
  09:15: LOW(2)=4502.985 < 4503 → trend=-1, prev=0 → choc_down TRUE → SELL ✅


---

### Semana 2026-W23 | Fecha: 04/06/2026 — IMAGEN 12 — Hand pointer en el punto exacto de entrada
**Screenshots:** chat 22:05 UTC-4 (código) + IMG_7434.heic 22:06 UTC-4 (hand pointer en TradingView)
**Estado código en imagen:** BUY 09:15 → SL 10:25 + HEDGE SELL ~10:15 → TP

**Punto exacto señalado por Diego (manito):**
- Hora: 09:14-09:15 (la vela exacta donde el trader humano tomó la decisión)
- Precio: ~4,502.985 (open de 09:15)
- Acción: SELL ▼ MEC-A BAJISTA
- El cursor + en el HEIC apunta a la vela 09:14 (la vela de setup) o 09:15 (la vela de entrada)

**Lo que ve el trader humano en ese punto:**
1. Gray box formado (zona gris rectangular): HIGH ~4514, LOW ~4503
2. Vela 09:14: pullback ALCISTA dentro del gray box (setup de patrón)
3. Vela 09:15: bearish engulf que rompe por DEBAJO del gray box low (4503) → ChOC BAJISTA
4. SELL al open de 09:15 = 4,502.985 → TP a ~4491

**Estado del código en imagen 12:**
- Sigue con BUY (código con fix choc_up/choc_down pero SIN in_sess_m3_valid)
- El fix in_sess_m3_valid=0909 está listo en clipboard, todavía no aplicado en TradingView

**Timeline esperado con fix completo (in_sess_m3_valid + new choc):**
  09:12: HIGH(1)=4514 detectado (primer M3 high limpio de sesión)
  09:15: LOW(1)=4503  detectado → sess_both_ok=true
  09:18: LOW(2)=4502.985 < 4503 → trend=-1 → choc_down → SELL at 09:18 entry
  
  OR si el ChOC+patrón coinciden a 09:15 → SELL at 09:15 ✅

**Próxima acción:** Diego pega el código del portapapeles (fix in_sess_m3_valid=0909)


---

### Semana 2026-W23 | Fecha: 04/06/2026 — IMAGEN 13 — Fix definitivo: M3 close direction
**Screenshot:** 22:21 UTC-4 — BUY persiste (mismo resultado que 22:05)
**Root cause DEFINITIVO:** La detección por pivot M3 (high/low) NO puede replicar el gray box del trader.

**Por qué todos los fixes previos fallaron:**
El trader humano usa las BARRAS M3 completas (dirección close vs open) para ver el gray box.
Los pivots M3 (turn pattern: bar[2] UP + bar[1] DOWN) son DISTINTOS a lo que el trader ve.
Para Jun 4:
  M3 09:06-08: UP (precio subiendo a 4514)
  M3 09:09-11: DOWN (precio bajando de 4514)
  M3 09:12-14: DOWN (precio continuando a la baja)
  → Dos barras M3 consecutivas DOWN = estructura BAJISTA → SELL a las 09:15

**Fix aplicado (definitivo):**
Reemplazar detección ChOC con "2 barras M3 consecutivas en misma dirección":
  choc_up   = 2 M3 bars consecutivas BULLISH + gray box completo (UP y DOWN vistos)
  choc_down = 2 M3 bars consecutivas BEARISH + gray box completo

Timeline Jun 4:
  09:09: M3[0]=09:06-08 UP, M3[1]=09:03-05 UP → 2 UP → saw_bull=true, pero no DOWN aún → NO ChOC
  09:12: M3[0]=09:09-11 DOWN, M3[1]=09:06-08 UP → distinto → saw_bear=true → gray_box=ready, NO ChOC
  09:15: M3[0]=09:12-14 DOWN, M3[1]=09:09-11 DOWN → 2 DOWN + gray_box=ready → ChOC BAJISTA ✅
  → SELL @ open 09:15 = ~4502.985 ✅


---

### Semana 2026-W23 | Fecha: 04/06/2026 — IMAGEN 14 — BUY @ 09:17 (fix M3 direction NO resuelve)
**Screenshot:** 23:35 UTC-4 — BUY @ 09:17 → SL @ 09:26 | SELL @ 09:30 → SL @ 09:35
**Dashboard:** SL 2/2 🔴, TP 0/1, R semanal -2/-2R, Opera: NO, Tendencia: ALCISTA

**LEFT (código XAU v9):**
- Trade 1: BUY ▲ MEC-A @ 09:17, T.salida: 09:26, Resultado: SL, Estructura: Alcista
- Trade 2: SELL ▼ START @ 09:30, T.salida: 09:35, Resultado: SL, Estructura: Bajista
- Líneas ChOC ALCISTA (verde) visibles al nivel ~4508 y ~4506
- Múltiples señales bloqueadas (círculos purple) entre 09:20-09:30

**RIGHT (trader humano — referencia):** SELL @ 09:15 @ 4502.985, TP ~4491, +0.9R

**Análisis del nuevo bug:**
El fix de "2 barras M3 consecutivas" mejoró (ahora detecta SELL eventualmente) pero la dirección del ChOC sigue siendo incorrecta para 09:15. El código detecta ChOC ALCISTA antes de la entrada correcta.

**Root cause definitivo identificado:**
En Jun 4, la secuencia real de barras M3 es:
  M3 09:06-08: DOWN (primera barra bajista al abrir sesión)
  M3 09:09-11: UP (rebote)
  M3 09:12-14: UP (continuación rebote, precio vuelve a ~4514)
  → Al 09:15: M3[0]=UP (09:12-14) + M3[1]=UP (09:09-11) = 2 UP → ChOC ALCISTA ❌

El código nunca puede saber que M3 09:15-17 sería DOWN (ya que solo ve barras completadas).
La solución de "2 barras M3" requiere esperar HASTA que ambas barras DOWN estén completas = 09:21.

**FIX REAL:** El trader humano NO usa 2 barras M3 consecutivas. Usa el RANGO DE PRECIO (gray box M1):
  1. Observa el rango de los primeros 12 minutos de sesión (09:01-09:12)
  2. gb_HIGH = max(highs de 09:01-09:12) ≈ 4514
  3. gb_LOW = min(lows de 09:01-09:12) ≈ 4506-4508
  4. Primera vela M1 que CIERRA por debajo de gb_LOW = ChOC BAJISTA
  5. A las 09:15: close ≈ 4502.985 < gb_LOW ≈ 4506 → ChOC BAJISTA ✅ → SELL ✅


---

### Semana 2026-W23 | Fecha: 04/06/2026 — IMAGEN 15 — Chart del trader humano (zoom Jun 4)
**Screenshot:** 23:35+ UTC-4 — Imagen del trader humano mostrando el punto exacto de entrada

**Análisis del chart del trader humano:**
- **Gray box visible:** área gris sombreada en la parte superior — consolida entre ~4,504 y ~4,516
- **Primera vela:** la vela que ROMPE el piso del gray box (~4,504) cerrando abajo → ChOC detectado
- **SEGUNDA VELA:** la siguiente vela = la vela envolvente bajista donde se TOMA LA DECISIÓN
  - Esta vela ABRE en 4,502.985 (open de la vela de ejecución)
  - Esta es la "segunda vela" que Diego señala como momento de la decisión
  - El trader ve el ChOC y en la SIGUIENTE vela ejecuta la entrada
- **Resultado:** Trade SELL desde 4,502.985 → TP ~4,491.655, +0.9R (visible en el box rosado)
- **Labels rojos en chart:** "11,330 - 19 0,9" y "11,330 (0,252%) 1,133,0 122,06" = métricas de la operación

**Concepto confirmado por Diego:**
En Pine Script con calc_on_every_tick=false:
  - Barra N (señal): el patrón ENV/START completa → signal_bear = true → strategy.entry() llamado
  - Barra N+1 (segunda vela): la orden se LLENA al OPEN = 4,502.985
  → La "segunda vela" ES la barra de ejecución real (bar N+1)
  → El ▼ triángulo y punto de decisión DEBEN aparecer en la barra N+1

**Cambios solicitados por Diego:**
1. Agregar un PUNTO visible en la segunda vela (barra de ejecución real)
2. Mostrar el gray box en el chart (líneas de los niveles gb_HIGH / gb_LOW)
3. Dejar todo lo demás igual (lógica gray box M1, labels, estructura visual)

---

### Semana 2026-W23 | Fecha: 04/06/2026 — IMAGEN 17 — Chart trader humano Jun 4 (comparación completa)
**Screenshot:** imagen nueva — trader humano Jun 4, 2026 completo con gray box y trade

**Análisis del chart del trader humano — IMAGEN 17:**

**ESTRUCTURA DEL CHART:**
- **Rectángulo gris grande (izquierda):** zona de distribución / acumulación previa a sesión NY (~08:45-09:40)
  - Rango: ~4,500 – 4,513 aprox
  - Dotted dashed lines = niveles estructurales previos
- **Gray box sombreado (gris relleno, derecha):** rango de los PRIMEROS minutos de sesión activa
  - HIGH ≈ 4,516 | LOW ≈ 4,504 (visible en el sombreado)
  - Se forma aproximadamente entre 09:45-10:00 en el chart visible
  - Label superior gris: "12,530 (0,278%) 1.253,0 750" = tamaño del gray box en puntos
- **Zona rosada (trade activo):** SELL desde 4,502.985 hacia abajo
  - Label rojo: "11,330 - 19 / 0,9" = entrada SELL, 19 puntos de SL, 0.9R riesgo
  - Label rojo inferior: "11,330 (0,252%) 1.133,0 122x.06" = resultado TP alcanzado

**PRECIOS CLAVE:**
| Nivel | Precio |
|-------|--------|
| Gray box HIGH | ≈ 4,516.000 |
| Gray box LOW  | ≈ 4,504.000 |
| Entry SELL    | 4,502.985 |
| Exit TP       | ≈ 4,491.655 |
| Recorrido     | ≈ 11.33 puntos (~0.9R) |

**PUNTO DE DECISIÓN (según PDFs):**
Siguiendo la guía del Plan Técnico y Plan Operativo:
1. **Gray box formado** → rango inicial de sesión definido (HIGH ~4,516 / LOW ~4,504)
2. **ChOC DOWN** → primera vela M1 que CIERRA por debajo de 4,504 (el piso del gray box)
3. **Patron ENV/START bajista** en la primera vela de ejecución → confirma la dirección
4. **Segunda vela** = la vela donde se ABRE la orden en 4,502.985
   → El trader toma la decisión AL FINALIZAR la primera vela de ruptura / INICIO de la segunda vela
   → Exactamente como Diego describió en sesiones anteriores

**COMPARACIÓN CÓDIGO (Fix v4 — m3l1/m3h1) vs TRADER HUMANO:**
| Aspecto | Trader Humano | Código Fix v4 |
|---------|--------------|---------------|
| Dirección | SELL (BAJISTA) ✅ | SELL (BAJISTA) ✅ |
| Entrada | 4,502.985 | Pendiente verificación |
| ChOC boundary | LOW del gray box ≈ 4,504 | m3l1 (primer pivot LOW M3 sesión) |
| TP | ~4,491.655 | Calculado por reglas PDF |
| Resultado | ~0.9R TP ✅ | Pendiente verificación |

**FIX v4 aplicado en esta sesión:**
Reemplazamos `gb_low`/`gb_high` (mínimo/máximo M1 de 09:01-09:12) por `m3l1`/`m3h1` (pivots M3 estructurales).
- m3l1 ≈ 4,507 (primer pivot LOW M3 de sesión, detectado ~09:09-09:12)
- Cuando la vela M1 de 09:14 cierra bajo 4,507 → ChOC → SELL @ 09:15 OPEN = 4,502.985 ✅ (esperado)
- Pendiente: confirmar con screenshot del código actualizado

**⚠️ REGLA VISUAL CONFIRMADA (08/06/2026):**
En el chart del trader humano: NEGRO = alcista ▲ | BLANCO = bajista ▼
Re-análisis del patrón de entrada Jun 4 con colores correctos:
- Gray box: velas NEGRAS (alcistas) empujan precio hasta HIGH ~4,516
- ChOC DOWN: primera vela BLANCA (bajista) que cierra bajo LOW ~4,504
- Zona rosada: secuencia de velas BLANCAS (bajistas) confirmando la tendencia SELL
- Segunda vela (ejecución @ 4,502.985): vela BLANCA bajista = patrón ENV/START bajista
  → Coherente con f_std_bear/f_hmr_bear del código (close < open, cuerpo ≥ 85%)
- El patrón que DISPARA la señal es la primera vela BLANCA que rompe el gray box

---

### Semana 2026-W23 | Fecha: 04/06/2026 — IMAGEN 18 — Código XAU v9 Fix v5 + comparación trader humano

**Comparación Imagen 18 (código) vs Imagen 17 (trader humano):**

| | Código (Fix v5) | Trader Humano |
|--|--|--|
| Dirección | SELL BAJISTA ✅ | SELL BAJISTA ✅ |
| T. entrada | 09:21 | ~10:00-10:05 |
| Precio entrada | ~4,501 (aprox) | 4,502.985 |
| Tipo | MEC START | MER (retest gray box) |
| Resultado | TP ✅ | TP ✅ |

**Observaciones:**
- El código toma una entrada START a las 09:21 (correcta en dirección)
- El trader humano toma una entrada MER a las ~10:00-10:05 (retest del gray box low)
- Diego señala con línea blanca: ~10:10 @ 4,502.5 = "aca es la entrada"
- La línea azul horizontal = MER level (gb_low) ≈ 4,502.5 → precio retoca ese nivel a las 10:10

**Bug MER identificado:**
- `mer_used_bear` se consumía en el PRIMER toque del nivel (aunque sin patrón bajista)
- En Jun 4: precio bota de regreso a ~4,505 múltiples veces durante 09:25-09:50 (rally)
- En esos bars, el precio toca el nivel (high >= threshold) → mer_used_bear = TRUE
- A las 10:10 cuando hay el retest REAL con patrón → mer_used_bear ya es TRUE → MER no dispara ❌

**Fix MER v1 (aplicado):**
1. `mer_touch_bear` ahora requiere `close[1] < mer_lvl_bear` → solo válido si bar anterior cerró DEBAJO
   = precio viene de abajo y retoca = retest real desde debajo del nivel
2. Eliminado el consumo standalone (`if mer_touch: mer_used := true`)
3. MER se consume SOLO cuando la entrada dispara (`if mer_bear: mer_used_bear := true`)
4. Eliminado `one_high_ok` y `one_low_ok` de las condiciones MER (bloqueaban por múltiples pivots M3)

**Esperado después del fix:**
- 09:21: SELL MEC START @ ~4,501 (entrada early, correcta)
- ~10:10: SELL MER @ ~4,502.985 (retest del nivel, segunda entrada = la del trader humano) ✅

---

### Semana 2026-W24 | Fecha: 09/06/2026 — Imagen 21 (comparativa código vs trader humano)
**Screenshot:** imagen recibida en sesión — código + chat WhatsApp con trader humano Jun 4

**Análisis comparativo — IZQUIERDA (código) vs DERECHA (trader humano):**

**Trader humano (derecha):**
- Gray box: HIGH ~4,515.515 | LOW ~4,504
- ChOC DOWN: primera vela que cierra < 4,504 (aprox 09:57-09:58)
- ENTRADA: 4,502.985 @ ~10:00 open
- SL: 4,515.515 (m3h1) | TP: 4,491.655
- Tipo de entrada: MER — primera vela bajista que retestea gb_low (~4,504) desde abajo
- La vela de entrada NO necesita ser envolvente — solo necesita ser BAJISTA (close < open)

**Código (izquierda):**
- Entry marcado ~6 velas tarde (entrada a ~10:08 en vez de ~10:00)
- Tooltip: T.entrada 09:59, Ejecución: MEC Patron
- Flecha azul señala la vela correcta ~09:57-09:59

**Root cause confirmado del delay de 6 velas:**
MER bear requiere `f_engulf_bear()` que exige `close < low[1]` (close por DEBAJO del low anterior).
En la vela de entrada real (~10:00), el precio retestea 4,504 desde abajo y cierra bajista,
pero NO cierra por debajo del low de la vela anterior (ChOC bar) → `f_engulf_bear` falla.
El código espera 4-6 velas más hasta que aparece una vela que sí engulfa.

**Fix a aplicar (Fix v7):**
Para MER solamente, reemplazar `f_engulf_bear` con `close < open` (vela bajista simple).
El retest del nivel ChOC YA es la confirmación suficiente según PDFs.
MEC-a mantiene el requisito de envolvente (para ese modelo sí aplica).

**Flecha verde (TP):**
- Diego marcó con flecha verde el final del TP en el chart izquierdo
- El TP alcanza ~4,491.655 ✅ (zona verde = la zona rosa del trader humano)
- La dirección y magnitud son correctas, solo el TIMING de la entrada está mal


---

### Semana 2026-W24 | Fecha: 09/06/2026 — Imagen 22 (línea vertical azul = 09:54)
**Screenshot:** Jun 4, 2026 — código XAU v9, Diego marcó con línea vertical azul

**Análisis:**
- Diego marcó con línea vertical azul la vela de las **09:54** en Jun 4
- Esa vela es la GRANDE ROJA que cae desde ~4,514 hasta ~4,502 (rompe gb_low = 4,504)
- = La vela del ChOC correcto
- El código sigue entrando en **MEC-A a las 09:59** (5 barras después)

**Por qué el código no entra en 09:54:**
1. Pivot M3 pequeño al inicio de sesión (~09:15-09:21) → ChOC early → SL → m3_trend = -1 (SL hoy = 1/2)
2. Rally grande 09:41-09:54 crea nuevo pivot M3 más alto (m3h1 = 4,515.515)
3. El gray box NO se actualiza porque requería m3_trend == 0
4. A las 09:54: choc_down no puede disparar porque m3_trend ya era -1
5. MEC-A dispara a las 09:59 (5 velas tarde)

**Fix aplicado: Gray Box Invalidation**
- Cuando m3h1 nuevo > gb_high anterior (pivot más alto) → resetear m3_trend = 0
- Esto permite que ChOC vuelva a disparar desde el NUEVO gray box correcto
- A las 09:54: invalidación activa → m3_trend = 0 → ChOC dispara → entry a las 09:55 open

**Timing coincide:** El M3 pivot (bar[2] alcista + bar[1] bajista) cierra exactamente a las 09:54
→ m3_high_raw disponible a las 09:54 → invalidación + ChOC en el MISMO bar de 09:54


---

### Semana 2026-W24 | Fecha: 09/06/2026 — SESIÓN EN VIVO 09:15 NY
**Screenshot:** M1 + M3 overlay, 09:15 UTC-4

**Estado del dashboard:**
- Tendencia M3: BAJISTA ✅ (ChOC DOWN ya disparó)
- Sesión NY: ACTIVA
- SL hoy: 1/2 | TP hoy: 2/2 → Opera hoy: **NO** ⛔
- R semanal: 0.8 / -2R (en positivo)
- Alto M3: 4,344.48 | Bajo M3: 4,317.12
- Precio actual: 4,341.58

**Estructura visible:**
- Red dotted ~4,345.5 y ~4,344.48 = niveles M3 altos (resistencias)
- Teal dotted ~4,341.5, ~4,338.0, ~4,337.0 = niveles M3 bajos (soportes/gb_low)
- El ChOC DOWN ya ocurrió (Tendencia BAJISTA confirmada)
- Precio consolidando entre ~4,338-4,344

**Límite diario alcanzado:** day_tp = 2/2 → no más operaciones por regla del Plan Operativo


---

### Semana 2026-W24 | Fecha: 09/06/2026 — SESIÓN EN VIVO 09:37 NY
**Screenshot:** M1 izquierda + M3 derecha, 09:37:54 UTC-4

**Estado M1 (izquierda):**
- SL hoy: 1/2 | Opera hoy: NO | Posición: FLAT
- Alto/Bajo M3: 4335.59 / 4329.02
- Red dotted: ~4,337.77 y ~4,336 (resistencias)
- Teal soporte: ~4,327.99
- Precio: 4,332.40

**Estado M3 (derecha):**
- SL hoy: 0/2 | TP hoy: 2/2 | Opera hoy: NO
- Alto/Bajo M3: 4335.59 / 4331.69
- Big drop: desde ~4,344 hasta ~4,330 (ChOC DOWN correcto ✅)
- Precio rebotando en ~4,332-4,333

**Análisis:**
- El movimiento SELL fue correcto — bajó ~12 puntos desde gray box high
- El código perdió la entrada óptima (entró tarde o con stops incorrectos)
- Opera hoy = NO en ambos charts (TP hoy 2/2 y posible week_r)
- Código nuevo con TP limit desactivado AÚN NO FUE PEGADO


---

### Semana 2026-W24 | Fecha: 09/06/2026 — SESIÓN EN VIVO 09:53 NY
**Screenshots:** M1+M3 código + M1 trader humano (Fabian Uade)

**Lo que pasó (trader humano):**
1. SELL entry ~09:44 (dentro del gray box, MEC)
2. SELL hit SL al spike arriba ~09:45-09:47
3. **EN LA MISMA VELA que tocó el SL del SELL → entrada BUY por MER** ✅
4. El BUY funcionó (precio subió hacia la zona azul)

**Patrón clave aprendido: "SL candle = MER inverso"**
- Cuando el precio toca el SL de una SELL (= rompe gb_high = ChOC UP)
- Esa misma vela ES la señal de BUY (choc_direct_bull = choc_up)
- Segunda vela = entrada BUY al open siguiente

**Por qué el código lo perdió:**
- M1: SL hoy = 2/2 → day_sl = 2 → `day_sl < 2` falla → can_trade = false → BUY bloqueado
- El límite de SLs también hay que desactivar mientras se calibra

**Estado del código M3:**
- MEC START SELL @ 09:39 → SL @ 09:45 (correcto detectar pero timing/SL price incorrecto)
- TP hoy: 4/2 (límite TP desactivado funcionando)
- Opera hoy: SI en M3

**Fix pendiente:** igual que el TP limit → hacer el SL limit configurable (off por defecto)


---

### Semana 2026-W24 | Fecha: 09/06/2026 — TRADES REALES (tabla de operaciones)

**Operación 1 — SELL:**
- Entrada: 4,329.05
- SL: 4,335.71 | TP: 4,322.68
- Cierre: 4,335.79 → **SL hit**
- Resultado: **-94.36**
- Distancia SL: 4,335.71 - 4,329.05 = **6.66 puntos**
- Distancia TP: 4,329.05 - 4,322.68 = **6.37 puntos** ≈ 0.96R (casi 1:1, no 0.9R)

**Operación 2 — BUY (mismo candle que tocó SL del SELL):**
- Entrada: ~4,335.45 (open de la vela siguiente al ChOC UP)
- SL: 4,329.05 = precio de entrada del SELL anterior (simétrico)
- TP: 4,345.55 = ~10 puntos arriba (gray box high / M3 high de sesión)
- Resultado: **+90.00** (TP hit)
- Distancia SL: 4,335.45 - 4,329.05 = 6.40 pts
- Distancia TP: 4,345.55 - 4,335.45 = 10.10 pts → RR = 1.58R

**Net: -94.36 + 90.00 = -4.36 (casi breakeven)**

**Reglas aprendidas de este trade:**
1. SL del SELL = mismo candle → ChOC UP → BUY directo (choc_direct_bull)
2. SL del BUY = precio de entrada del SELL (el nivel de M3 low que activó el SELL)
3. TP del BUY = M3 high de la sesión (no 0.9R — llega al techo del gray box)
4. La distancia SL del SELL (~6.66 pts) no es m3h1 completo — es un SL ajustado

**Discrepancias vs código actual:**
- Código usa TP = 0.9R (multiplica distancia SL por 0.9)
- Trader humano usa TP = nivel M3 opuesto (techo del gray box para BUY)
- Código usa SL = m3h1 exacto (puede ser más lejos)
- Trader humano usa SL ajustado al contexto

---

### Sesión | Fecha: 04/07/2026 — Comparativa trader humano (izq) vs código "XAU Scalp" (der)

**Screenshot:** imagen pegada en chat, sin archivo guardado en /screenshots (Diego la pegó directo).
**Chart derecho:** TradingView, Gold Spot/USD OANDA, M1, script "XAU Scalp" (parámetros en título: 0901-1059 0.9 0.85 0.75 0.5 200 0.4 0.0001 10 15 5), ventana 09:00–09:40 NY.
**Chart izquierdo:** vista del trader humano (recorte más simple, sin panel de indicador visible), mismo rango horario aprox. 09:00–09:45, con una caja gris/celeste que marca la zona de rango (gray box) y una flecha diagonal marcando el tramo impulsivo que capturó.

✅ **Archivo identificado:** `/Users/diegorodriguez/Desktop/Jarvis/jarvis/scalping/XAU_Scalping_Strategy.pine` — shorttitle `"XAU Scalp"` y parámetro de sesión `"0901-1059:23456"` coinciden exactamente con el título del chart. Es un script `strategy()` (no `indicator()`), por eso muestra los marcadores automáticos +2.48/-2.48 de P&L de TradingView en vez de los labels custom de `apariencia_labels.md`.

**Cómo se generan los labels (confirmado leyendo el código):**
- `strategy.entry("BUY", ...)` / `strategy.entry("SELL", ...)` → entradas. El archivo del repo usa IDs simples "BUY"/"SELL"; el screenshot muestra "MEC ENV BUY/SELL" — sugiere que la copia que corre en vivo en TradingView tiene el ID renombrado ahí mismo (no sincronizado de vuelta al repo).
- `strategy.exit("BUY_X", "BUY", stop=sl_b, limit=tp_b)` / `strategy.exit("SELL_X", "SELL", stop=sl_s, limit=tp_s)` → el sufijo `_X` es exactamente lo que se ve como "Long X" / "Short X": es el cierre de la posición al tocar el SL o el TP fijados en el momento de la entrada.
- Lógica de hedge: si aparece una señal contraria mientras hay posición abierta, el código hace `strategy.close(..., comment="Hedge")` y abre en la dirección nueva (pyramiding=1, siempre 1 posición neta).

**Causa raíz confirmada en el código (líneas 319-324):**
```
sld_b = close - m3l1          // distancia SL en el momento de la entrada
sl_b  = close - f_adj(sld_b)
tp_b  = close + f_adj(sld_b) * i_rr   // i_rr = 0.9 por defecto
```
El SL y el TP se calculan **una sola vez, en la vela de entrada**, a partir del `m3l1` (bajo M3) vigente en ese instante — y ya NO se actualizan mientras la operación sigue abierta, aunque se formen nuevos pivots M3 durante el trade. Esto es exactamente la "REGLA FUNDAMENTAL — Niveles M3 dinámicos (10/06/2026)" que ya identificamos como pendiente de implementar: el nivel de referencia debe seguir moviéndose con la estructura, pero en este archivo se congela al entrar.

#### Lectura cronológica con esto en mente
1. **~09:00–09:02** — `SELL` (mostrado como "MEC ENV SELL" en vivo) se dispara casi en la apertura, antes de que la sesión tenga ambas referencias M3 (alto y bajo) — mismo patrón de "Error #1b".
2. **09:10–09:15** — `SELL_X` ("Short X +2.48") cierra esa posición corta con ganancia (tocó su TP o se cerró por hedge) justo en el piso del rango.
3. **~09:18–09:20** — `BUY` ("MEC ENV BUY +2.48" acumulado) — misma zona y dirección que identificó el trader humano en su caja.
4. **~09:25–09:27** — `BUY_X` ("Long X -2.48") — el SL fijado AL MOMENTO DE ENTRAR (basado en el `m3l1` de ese instante) se tocó por un pullback menor, cerrando la posición justo antes de que arrancara el tramo grande (de ~4,160 a más de 4,200 hacia las 09:40). Nótese además que `i_rr = 0.9`: el TP del sistema está deliberadamente fijado a solo 0.9x la distancia del SL — es un sistema de scalping de objetivo corto, no de "dejar correr" la tendencia, lo cual también limita cuánto del movimiento se puede capturar aunque el SL no se hubiera tocado.

#### Comparativa con el trader humano (izq.)
- La caja del trader marca la misma zona de rango que el código tardó en confirmar.
- El trader captura el tramo completo porque recalcula el nivel M3 en vivo y no tiene un SL/TP congelado al momento de entrar.
- El código entró bien (dirección correcta) pero el SL fijo + TP corto (0.9R) lo sacan de la jugada antes de la parte más grande del movimiento.

#### Diagnóstico y acción concreta para el código
- **Entrada SELL inicial prematura** = "Error #1b" (falta esperar `sess_both_ok` real).
- **Salida temprana de la posición ganadora** = el SL/TP en `sl_b`/`tp_b` (líneas 319-324) se calculan una vez en la entrada y nunca se recalculan con nuevos pivots M3 — hay que hacerlos dinámicos (recalcular `m3l1`/`m3h1` vigente en cada barra mientras la posición está abierta, no solo al entrar).
- El parámetro `i_rr = 0.9` (TP = 0.9x SL) es una decisión de diseño explícita, no un bug — pero vale la pena revisar si conviene subirlo dado que en este ejemplo dejó la mayoría del movimiento sin capturar.

**Pendiente para la sesión en vivo de esta semana:** aplicar el fix de niveles M3 dinámicos también a `XAU_Scalping_Strategy.pine` (no solo a `xau_v9.pine`), y decidir si ajustar `i_rr` por encima de 0.9.

---

### Sesión EN VIVO | 01/09/2026 16:02 UTC-4 — Comparativa código (izq/EstrategiaXAU) vs Fabian real (der) — Pre-NY 07:00-08:15

**Chart izquierdo (código):** `diegodarpa`, TradingView, Gold Spot/USD OANDA M1,
`EstrategiaXAU v3` recién actualizado con las 3 sesiones. Ventana visible
07:00-08:15 NY (sesión Pre New York). Tabla: Total Trades 19, Win Rate
52.6%, Wins/Losses 10/9, Net Profit 113.95, **SL hoy/TP hoy: 3/0**, R
semana -3.1R.

**Chart derecho (Fabian real):** `Fabiancarreroa`, TradingView, Gold
Spot/USD OANDA M1, chart propio (sin nuestro indicador) con dibujos
manuales (rectángulos gris/rosa de rango, línea diagonal de medición),
ventana 06:15-09:15 NY. **No tiene un label explícito de BUY/SELL visible
en la captura** — solo cajas de medición de rango, así que no puedo leer
con certeza el minuto y la dirección exacta de su entrada real de las
~08:00 solo de la imagen. Pendiente: pedirle a Diego/Fabian el horario y
dirección exacta de esa entrada para poder chequearla puntualmente contra
el código (igual que se hizo con las 191 operaciones históricas).

#### Decisión de entrada — lo que hizo el código
En los primeros ~15 minutos de la sesión Pre-NY (07:00-07:15) el código
tomó varias entradas seguidas con flips de Hedge ("MEC ENV SELL", "MEC
ENV BUY" x2, cierres "Cierre por Hedge" -1/-1) — luego **ninguna entrada
más en toda la ventana 07:15-08:15**, a pesar de un Cambio de Estructura
Bajista claro cerca de las 07:52 con una vela roja grande y continuación
bajista fuerte hasta las 08:15 (justo la zona donde, según Diego, Fabian
sí encontró una entrada real).

#### CAUSA RAÍZ ENCONTRADA (no es un problema de reconocimiento de patrón)
La tabla mostraba **SL hoy: 3**, pero `DAILY_MAX_SL = 2` (regla fija del
Plan Operativo: 2 SL detiene el día) debería haber permitido como máximo
2 antes de frenar el día. Revisando el código de tracking
(`strategy.closedtrades`), el bug es que **un cierre por Hedge (flip de
posición cuando aparece una señal contraria con posición abierta) se
contaba igual que un SL real** si ese cierre daba en pérdida. Con varios
flips de Hedge seguidos en los primeros minutos de Pre-NY (una sesión más
"picada" que la ventana NY angosta que se calibró históricamente), el
contador de "2 SL detiene el día" se gastó casi de entrada — silenciando
el resto del día, incluida la zona de las ~08:00 donde Fabian entró.

**Por qué la calibración histórica (182/191, 95,3%) nunca detectó esto:**
el método de validación (`señales_del_dia()` en Python) nunca simuló
posiciones abiertas, hedge ni el corte diario — solo evaluaba si el
patrón se reconocía en cada vela, sin autonomía. El corte diario y la
lógica de Hedge solo existen en el `.pine` real de estrategia, que recién
se está probando en vivo por primera vez en esta Fase 2. Es un hallazgo
nuevo, no una regresión de lo ya validado.

**Fix aplicado (`EstrategiaXAU.pine`, 01/09/2026):** los cierres por
Hedge ahora se excluyen del conteo de SL/TP del día
(`str.contains(strategy.closedtrades.exit_comment(...), "Hedge")`) —
antes de este fix, un flip de posición podía contar como si el precio
hubiera tocado el stop loss real, que no es lo que dice el Plan
Operativo.

#### Otros cambios de estética aplicados en la misma sesión
- Sacado el cartel de texto "CAMBIO DE ESTRUCTURA ALCISTA/BAJISTA"
  (Diego: "veo mucho ruido") — se mantienen los colores de fondo en la
  vela del ChoC, sin el texto.
- Acortado el comentario de cierre por Hedge de "Cierre por Hedge" a
  "Hedge" (sigue siendo necesario como texto interno para el fix de
  arriba; para sacar TODOS los carteles automáticos de operaciones,
  Diego puede desactivarlo desde la config de estilo del indicador en
  TradingView, no es algo que dependa del código).

#### Pendiente
- Confirmar con Fabian el horario/dirección exacto de la entrada de las
  ~08:00 para chequearla puntualmente (igual que el resto de las 191).
- Volver a correr la sesión completa con el fix del contador aplicado y
  ver si el código ahora sí opera en la zona 07:50-08:15.

