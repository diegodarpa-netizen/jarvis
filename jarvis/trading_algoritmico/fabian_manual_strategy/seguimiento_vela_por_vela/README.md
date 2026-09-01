# Seguimiento vela por vela — calibración contra Fabian (código base exitoso)

**Objetivo permanente**: hacer que el código replique EXACTAMENTE lo que hace
Fabian, operación por operación, día por día. Fabian (191 operaciones reales,
65,45% WR, bootstrap significativo — ver `../INFORME_COMPLETO.md`) es el
código base exitoso contra el que se calibra todo lo demás. No se avanza a la
siguiente operación hasta que la actual esté explicada o corregida.

## Estado del patrón START (el que faltaba)

**12/02/2026, 09:03, SELL — CALIBRADO Y CONFIRMADO (27/08/2026).**

Secuencia real de velas M1 (hora NY):
- 08:57-09:00: 4 velas bajistas (bloque previo, no forma parte del patrón en sí)
- **09:01: vela alcista (pullback, en contra de la dirección final)**
- **09:02: vela de indecisión (cuerpo 18,5% del rango, no es martillo)**
- **09:03: vela envolvente bajista (cuerpo 87,5%, mecha inferior 8,1% — clásica) → ENTRADA SELL**

Fórmula Python que reproduce esto exacto (`es_start()`):
1. Vela de entrada (i) debe ser Envolvente (cualquier variante) en la dirección buscada.
2. Vela anterior (i-1) debe ser indecisión (cuerpo ≤50%, y no cumplir los
   parámetros de envolvente martillo).
3. Vela anterior a esa (i-2) debe ir EN CONTRA de la dirección final (pullback).
4. Invalidación: si las 3 velas (i-2, i-1, i) son del mismo color, el patrón
   pierde validez (regla del Plan Técnico pág. 15).

**Resultado de la prueba**: con esta fórmula, el código dispara SELL exactamente
a las 09:03 — el mismo minuto que Fabian, no 16 minutos después como pasaba sin
START. Ver `dia1_codigo_con_start.png`.

## Cómo seguir usando esta carpeta

Cada operación nueva que se calibre (coincide o no coincide con la fórmula)
se agrega acá abajo, con fecha, para no perder el hilo entre sesiones.

## Bitácora de calibración (agregar entradas nuevas arriba)

### 31/08/2026 — RE-TEST completo, resultado confirmado (nada cambió)
A pedido explícito de Diego ("no quiero que me digas que ya está hecho...
quiero que hagamos un test y quiero ver el porcentaje de acierto otra
vez"): se corrió de nuevo, operación por operación, TODO el dataset de
191 operaciones reales -- no de memoria, un test real ejecutado ahora
(`retest_completo_31ago.py`, carga el CSV de precios una sola vez y
reusa `señales_del_dia()` de `validar_entrada_fabian.py`, sin cambiar
ninguna lógica).

**Resultado: 182/191 EXACTAS (95,3%), 0 sin dato -- idéntico al cierre
del 30/08/2026.** Las 9 que no coinciden son exactamente las mismas 9 ya
documentadas (ninguna nueva, ninguna dejó de fallar):
28/10 09:04 SELL, 26/11 09:35 BUY, 26/11 10:10 BUY, 07/04 10:01 SELL,
22/04 09:28 BUY, 30/04 09:34 SELL, 22/05 10:03 SELL (Regla N°5), 05/08
10:03 BUY, 25/08 10:19 SELL -- todas con causa ya conocida (8 diferencia
de precio OANDA/Dukascopy + 1 Regla N°5 de noticias confirmada por
Fabian). Confirma que el motor está estable: no hubo regresión desde el
cierre del 30/08. Resultado fila por fila guardado en
`retest_completo_31ago_resultado.csv`.

### 30/08/2026 — CIERRE DEFINITIVO: 182/191 (95,3%), 0 sin dato
Fabian confirmó las 2 fechas ambiguas: la operación anotada como
08/02/2026 (Martes) era en realidad **10/02/2026**, y la anotada como
10/02/2026 (Miércoles) era en realidad **11/02/2026** -- corregido en
`fabian_consolidado_limpio.csv`. Ambas ahora coinciden EXACTO.

Fabian también mandó una imagen de su gráfico real (OANDA) para el
26/11/2025 09:35 confirmando que esa vela SÍ es una envolvente válida --
en nuestro dato (Dukascopy) esa misma vela sale casi sin cuerpo (0,4%).
Se suma a la lista de casos por diferencia de broker.

**RESULTADO FINAL: 182/191 EXACTAS (95,3%), 0 sin dato, 0 casos
genuinamente sin explicar.** Los 9 restantes: 8 por diferencia de precio
OANDA/Dukascopy (incluye ahora el 26/11 09:35) + 1 de la misma familia
"patrón antes de la ruptura" (26/11 10:10, igual al 22/04).

### 30/08/2026 — CIERRE FINAL: las 191 operaciones completas
A pedido de Diego: *"quiero que hagas el backtesting de todas las
operaciones que nos paso fabian... que vuelvas ha hacer todo una por
una"*. Se completaron las 52 operaciones previas al 12/02/2026 (desde
27/10/2025), usando `data/XAUUSD_M1_gap_fabian.csv` fusionado al CSV
principal + parches puntuales de huecos reales encontrados en 27-29/10,
10/11, 12/11, 06/02 y 08/02/2026.

**Hallazgo de dato**: dos fechas del registro de Fabian son inconsistentes
con el calendario real -- 08/02/2026 dice "Día: Martes" pero el 08/02 real
es domingo (mercado cerrado esa mañana); 10/02/2026 dice "Miércoles" pero
el 10/02 real es martes. No se pudo inferir la fecha correcta con certeza
(el patrón de secuencia no es concluyente) -- quedan marcadas como
**pendientes de aclarar con Fabian**, no se adivinó.

**Resultado de las 52 (27/10/2025-11/02/2026): 46/52 EXACTAS.** 5
NO_EXACTO + 1 SIN_DATO (este último es 08/02, la fecha ambigua). De los 5
NO_EXACTO, 4 son casos NUEVOS sin explicar todavía (28/10 09:04 SELL,
17/11 09:06 BUY, 26/11 09:35 BUY, 26/11 10:10 BUY -- este último día
falla en las DOS operaciones, con dato completo, raro) y 1 es la fecha
ambigua del 10/02.

**RESULTADO FINAL CONSOLIDADO -- las 191 operaciones reales de Fabian:**
- **EXACTAS: 175/191 (91,6%)**
- 10 ya explicadas (8 diferencia de broker OANDA/Dukascopy + 1 Regla N°5
  de noticias + 1 contradicho por Fabian en 22/04).
- **4 casos NUEVOS sin explicar** (28/10, 17/11, 26/11 ×2) -- pendiente
  de análisis vela por vela como se hizo con los 5 anteriores.
- 2 con fecha ambigua en el registro, no evaluables sin aclaración.

### 30/08/2026 — REVERTIDO: margen vuelve a medirse con cierre (cuerpo)
Fabian respondió los 5 casos pendientes por WhatsApp y mandó los PDFs
actualizados (guardados en `base_conocimiento_NO_TOCAR/`, ver
`respuestas_fabian_30-08-2026.md`). El PDF actualizado (pág.21) dice
explícitamente: "el precio debe superar CON CUERPO... con un volumen de
0.01% o más" -- CUERPO = cierre, no mecha. Esto contradice el fix del
28/08 (que se basó en una interpretación del caso 21/04). Revertido en
`prueba_ventana_horaria.py` y `validar_entrada_fabian.py`.

**Hallazgo clave**: Fabian opera con datos de OANDA (Plan Técnico pág.31:
"instrumento XAUUSD... commodity CFD OANDA visto en TradingView"),
nosotros usamos Dukascopy. La hipótesis más probable para los casos límite
(21/04, 07/04, 30/04, 25/08, 23/02) es una diferencia de precio entre
brokers para el mismo minuto -- no un error de fórmula. No es corregible
sin cambiar de fuente de dato.

**Resultado del revert**: 129/139 exactas (92,8%), bajando desde el
96,4% que daba el fix de la mecha (que empíricamente ayudaba, aunque
contradecía el texto literal del PDF). Se prioriza fidelidad al PDF sobre
el número más alto -- decisión explícita de Diego ("estos datos son el
corazón de la estrategia").

**Otros hallazgos de las respuestas de Fabian** (ver `respuestas_fabian_30-08-2026.md`
para el detalle completo):
- 22/05 (SELL 10:03): CONFIRMADO -- Regla N°5 del Plan Operativo (bloqueo
  de 3 min antes/después de noticias de mediano impacto), la entrada real
  fue la vela de las 10:00 pero se ejecutó recién a las 10:03 por una
  noticia de impacto medio publicándose justo en ese momento.
- 22/04 (BUY 09:28): Fabian dice que esa vela SÍ rompe el alto M3 -- no
  coincide con nuestro cálculo (Dukascopy), misma hipótesis de diferencia
  de broker.
- 07/04 y 30/04: Fabian dice que son "Vela Envolvente Martillo" válidas
  (cuerpo 50-85%) -- nuestro cálculo dio 44-48%, mismo tipo de diferencia.
- El Plan Operativo actualizado ahora define 3 sesiones (no solo NY):
  Pre New York (07:00-09:00), New York (09:02-11:00), Asia (20:02-22:00
  NY) -- pendiente de incorporar esto a la exploración de franjas horarias.

### 30/08/2026 — Re-recorrido día por día con el motor corregido
A pedido de Diego: "vamos a hacer otra vez día por día el backtesting...
empezamos por bloques de 10". Con el margen revertido a cierre:
- Bloque 1 (12/02-10/03, 16 op.): 15/16 -- falla 23/02 (broker).
- Bloque 2 (05/03-25/03, 16 op.): 15/16 -- falla 05/03 09:04 (broker).
- Bloque 3 (26/03-09/04, 13 op.): 12/13 -- falla 07/04 10:01 (envolvente
  martillo, ya explicado por Fabian, diferencia de broker).
- Bloque 4 (13/04-27/04, 17 op.): 15/17 -- fallan 21/04 y 22/04 (broker).
- Bloque 5 (29/04-14/05, 17 op.): 16/17 -- falla 30/04 (envolvente
  martillo, mismo tipo que 07/04).
- Bloque 6 (15/05-02/06, 13 op.): 12/13 -- falla 22/05 (Regla N°5 de
  noticias, CONFIRMADO por Fabian, no automatizado todavía).
- Bloque 7 (03/06-23/06, 12 op.): 12/12 perfecto.
- Bloque 8 (24/06-13/07, 14 op.): 13/14 -- falla 25/06 (broker).
- Bloque 9 (16/07-31/07, 13 op.): 13/13 perfecto.
- Bloque 10 (03/08-21/08, 14 op.): 13/14 -- falla 05/08 (broker).
- Bloque 11 (24/08-27/08, 8 op.): 7/8 -- falla 25/08 (broker, ya visto en
  detalle con imagen).

**RESULTADO FINAL del re-recorrido completo (139 operaciones, 12/02 al
27/08/2026): 129/139 EXACTAS (92,8%).** Los 10 fallos son exactamente los
mismos 10 casos ya identificados y explicados en la corrida anterior (8
desfase + 2 no reconocida), todos con causa conocida: 8 de 10 son
diferencia de precio OANDA (Fabian) vs Dukascopy (nuestro dato) en el
mismo minuto -- no corregible sin cambiar de fuente; 1 es la Regla N°5 de
noticias de mediano impacto (CONFIRMADA, mecanismo entendido, falta
automatizar); 1 (22/04) Fabian dice que sí rompe el nivel, contradice
nuestro cálculo, misma hipótesis de broker. Cero casos sin explicación.

### 28/08/2026 — CIERRE 2: tramo 14/08-27/08 completo, dataset 100% procesado
Tramo final descargado y validado (14/08, 24/08, 25/08, 26/08 necesitaron
reintento por publicación tardía de Dukascopy para fechas muy recientes,
resuelto). Las 15 operaciones restantes de Fabian, día por día:
- 14/08 09:34 BUY + 09:46 SELL (Hedge/MER): ✓ ambas
- 18/08 09:51 SELL (MER, TP): ✓
- 19/08 09:35 SELL + 09:43 BUY (Hedge/MER): ✓ ambas
- 20/08 10:45 BUY (MEC/Envolvente, TP): ✓
- 21/08 09:37 BUY (MER, TP): ✓
- 24/08 10:20 BUY + 10:42 SELL (MEC/Envolvente): ✓ ambas
- 25/08 10:19 SELL (MER, SL): **✗ -- caso límite del margen**. Hay una
  envolvente clásica perfecta justo ahí (env=1), pero ni siquiera el low
  de la vela perfora el margen 0,01% (le falta USD 0,13).
  25/08 10:24 BUY (Hedge/MER, SL): ✓
- 26/08 09:59 BUY + 10:59 SELL (MER): ✓ ambas
- 27/08 09:34 SELL + 10:20 BUY (MER): ✓ ambas

**CORRECCIÓN (mismo día):** el 23/02 (09:12 BUY) había quedado mal anotado
como "sin resolver ni con mecha" -- reverificado y en realidad SÍ está
EXACTO desde que se aplicó el fix de la mecha (confirmado con
`validar_entrada_fabian.py` en vivo). Error de anotación, no de código.

**RESULTADO FINAL — dataset completo de Fabian (12/02 al 27/08/2026, 139
operaciones, 100% procesado, cero pendiente de dato):**
- **EXACTO: 134/139 (96,4%)**
- Desfase/no reconocida: 5 -- 4 de la familia "patrón en vela separada"
  (07/04, 22/04, 30/04, 05/08), 1 de "nivel recién nacido ya roto" (22/05),
  1 de "caso límite del margen, ni con mecha" (25/08).
- Sin dato: 0.

Ya no queda dato de Fabian por evaluar. Próximo paso (pedido por Diego):
abrir el análisis a otras franjas horarias (sesión asiática, etc.) para
buscar oportunidades del mismo patrón mecánico fuera de la ventana
09:01-10:59 NY.

### 28/08/2026 — Días 89-92 parcial (18/08 a 21/08/2026): 5/5 exactas
Tramo 14/08-27/08 descargado; 14/08, 24/08, 25/08 y 26/08 salieron
incompletos o vacíos (raro para días hábiles, probablemente rezago de
Dukascopy en publicar dato de los últimos días) -- reintento en curso.
Mientras tanto, validados los días que sí bajaron completos:
- 18/08 09:51 SELL (MER, TP): ✓
- 19/08 09:35 SELL (MER, SL) y 09:43 BUY (Hedge/MER, TP): ✓ ambas
- 20/08 10:45 BUY (MEC/Envolvente, TP): ✓
- 21/08 09:37 BUY (MER, TP): ✓

### 28/08/2026 — Descargando tramo 14/08-27/08/2026 + próximo paso: otras sesiones
Corriendo `data/descargar_tramo_14ago_27ago.py` en background para completar
las 15 operaciones de Fabian que faltan evaluar (14/08 en adelante).

Diego adelantó el siguiente tema para cuando esto termine: **abrir el
análisis a otras franjas horarias** (sesión asiática y demás, fuera de la
ventana 09:01-10:59 NY que usa Fabian) para ver si el mismo patrón
mecánico (MEC-A/MEC-B/MER, Envolvente, START) encuentra oportunidades en
otros horarios. Retoma la idea original de "ventana angosta vs ventana
ancha" de `prueba_ventana_horaria.py` (27/08/2026), pero ahora con el motor
ya calibrado al 96% contra Fabian, no con la versión inicial sin corregir.

### 28/08/2026 — CIERRE: todo el rango disponible procesado, 96,0% exacto
Recorridas las 124 operaciones evaluables de Fabian (12/02 al 11/08/2026,
todo el rango con dato M1 disponible), día por día, sin saltear ninguna:

- **EXACTO: 119 (96,0%)**
- **DESFASE: 5 (4,0%)** -- 4 de la familia "patrón en vela separada de la
  ruptura" (07/04, 22/04, 30/04, 05/08) y 1 de la familia "nivel recién
  nacido ya roto" (22/05, único caso donde el código va ANTES que Fabian).
- **NO_RECONOCIDA: 0** -- cero casos sin explicación.
- Sin dato: 15 operaciones del 14/08/2026 en adelante (fuera del rango
  descargado hasta ahora).

Pendiente decisión de Diego: ¿profundizar en alguna de las 2 familias de
desfase restantes, o seguir acumulando evidencia de más operaciones (falta
descargar 14/08 en adelante) antes de tocar algo más?

### 28/08/2026 — Días 84-88 (03/08 a 11/08/2026): 6/7 exactas
- 03/08 09:25 SELL, 06/08 09:19 BUY, 10/08 09:02 SELL + 09:46 SELL, 11/08
  10:41 BUY: ✓ todas.
- 05/08 10:03 BUY: ✗ -- código reconoce a las 10:04 (1 min después), mismo
  tipo de caso ya conocido (patrón en vela adyacente a la de ruptura), no
  es un hallazgo nuevo.

**Del 14/08/2026 en adelante no hay dato M1 todavía** (el archivo base
llega hasta el 13/08/2026) -- quedan sin evaluar las operaciones de esas
fechas hasta que se descargue ese tramo.

### 28/08/2026 — Días 74-83 (16/07 a 31/07/2026): 13/13 EXACTAS, sin fallos
16/07, 20/07, 21/07 (x2), 22/07, 23/07 (x2), 24/07, 28/07, 29/07, 30/07,
31/07 -- las 13 operaciones exactas, sin excepción.

### 28/08/2026 — Días 64-73 (24/06 a 13/07/2026): 14/14 EXACTAS, sin fallos
- 24/06 09:41 BUY, 25/06 09:18 SELL (antes desfase +6min, ahora exacto con
  el fix de la mecha), 26/06 10:15 BUY, 30/06 09:07 BUY, 01/07 09:22 BUY,
  06/07 09:14 SELL + 10:24 SELL (Hedge/START), 07/07 09:24 SELL + 10:35
  SELL, 09/07 09:13 BUY, 10/07 09:26 SELL, 13/07 09:39 SELL. Todas exactas.

### 28/08/2026 — Días 54-63 (03/06 a 23/06/2026): 12/12 EXACTAS, sin fallos
- 03/06 09:20 SELL (MEC/Envolvente, TP): ✓
- 04/06 09:53 SELL (MER, TP): ✓
- 09/06 09:40 SELL (MEC/Envolvente, SL) y 09:46 BUY (MER, TP): ✓ ambas
- 11/06 09:59 SELL (MER, TP): ✓
- 12/06 09:07 BUY (MER, SL) y 09:40 SELL (MER, SL): ✓ ambas
- 15/06 10:05 BUY (MER, SL): ✓
- 16/06 09:16 SELL (MER, TP): ✓
- 18/06 09:40 SELL (MER, TP): ✓
- 22/06 10:02 SELL (MEC/Envolvente, SL): ✓
- 23/06 09:40 BUY (MEC/Envolvente, TP): ✓

### 28/08/2026 — Días 44-53 (15/05 a 02/06/2026): 12/13 exactas, hallazgo #3
Bloque de 10 días (13 operaciones) validado con el motor ya corregido
(mecha + patrón fusionado):
- 15/05 09:37 SELL (MER, TP): ✓
- 18/05 09:23 BUY (MEC/Envolvente, TP): ✓
- 19/05 09:02 SELL (MEC/Envolvente, TP): ✓
- 20/05 09:13 BUY (MER, SL) y 09:24 SELL (MEC/Envolvente, TP): ✓ ambas
- 21/05 09:33 SELL (MEC/Envolvente, SL) y 09:48 BUY (MER, TP): ✓ ambas
- 22/05 10:03 SELL (MEC/Envolvente, TP): **✗ -- hallazgo NUEVO, tercer tipo.**
  El código dispara a las 10:00, 3 minutos ANTES que Fabian (los otros
  hallazgos siempre fueron el código llegando DESPUÉS). A las 10:00 aparece
  un nivel M3 bajo nuevo (4511,77) que YA viene roto por el precio en ese
  mismo instante -- el código lo toma como ruptura válida apenas se conoce
  el nivel, sin exigir una vela fresca de ruptura posterior a que el nivel
  exista. Sin confirmar todavía si Fabian descarta este tipo de nivel
  "recién nacido y ya roto" a propósito, o si es timing/anotación. Pendiente
  acumular más casos de este tercer tipo antes de proponer algo -- no se
  toca el código.
- 27/05 09:18 SELL (MEC/START, SL) y 09:32 BUY (MER, TP): ✓ ambas
- 28/05 10:08 BUY (MER, TP): ✓
- 29/05 09:40 BUY (MEC/Envolvente, TP): ✓
- 02/06 09:21 SELL (MEC/Envolvente, TP): ✓

### 28/08/2026 — CORREGIDO: el quiebre se mide con la mecha, no con el cierre
Diego le mandó a Fabian la comparación visual del caso 21/04 y Fabian
confirmó: "la vela sí superó ese 0.01% luego de quebrar el bajo, por eso la
tomé, sino no la hubiese ejecutado, el mide con el rango de precios,
herramienta de TradingView". Verificado con el dato exacto: el CIERRE de
la vela de las 09:05 (4775,93) no llegaba al umbral, pero el LOW de esa
misma vela (4775,824) sí lo perforaba por muy poco. El código medía el
quiebre del nivel M3 con el precio de cierre; Fabian lo mide con la mecha
completa de la vela (como la herramienta de rango de precios de TradingView).

**Corregido en `prueba_ventana_horaria.py` y `validar_entrada_fabian.py`**:
las 6 condiciones de ruptura (ChOC alcista/bajista, mecA_long/short,
mecB_long/short) ahora usan `h_arr[i]`/`l_arr[i]` en vez de `close_i`.

**Verificación cruzada de los 4 casos previos marcados como "margen 0,01%"**:
- 23/02 (09:12 BUY): ahora EXACTO.
- 05/03 (09:04 y 10:01 BUY): ambos ahora EXACTOS.
- 21/04 (09:05 SELL): ahora EXACTO (el caso que confirmó Fabian).
- 07/04 (10:01 SELL): sigue sin coincidir exacto -- pero por una razón
  DISTINTA ahora: con la mecha, la ruptura sí se detecta a las 10:01, pero
  esa vela no tiene el patrón envolvente (aparece recién en la vela
  siguiente, 10:02) -- es el mismo tipo de caso que el 22/04 (ruptura y
  patrón en velas separadas), no el margen. Antes ambos problemas se
  compensaban por casualidad y parecía "solo 1 minuto de diferencia" por
  el motivo equivocado.

**Chequeo de regresión sobre las 55 operaciones ya procesadas (12/02 a
27/04/2026): 53/55 EXACTAS** (antes del fix: 51/55 exactas con 4 casos de
margen). Sin retrocesos -- todo lo que ya coincidía sigue coincidiendo, y
se ganaron 4 coincidencias nuevas. Quedan 2 pendientes (07/04, 22/04),
ambos de la misma familia: "ruptura y patrón en velas separadas" -- se
sigue acumulando evidencia antes de proponer un cambio para ese caso.

### 28/08/2026 — Días 34-43 (13/04 a 27/04/2026): 15/17 exactas, 1 hallazgo nuevo
- 13/04 09:47 SELL (SL) y 10:17 SELL (TP), ambas MEC/Envolvente: ✓ ambas
- 14/04 09:19 BUY (MEC/Envolvente, TP): ✓
- 15/04 09:57 BUY (MEC/START, SL) y 10:30 SELL (MEC/Envolvente, TP): ✓ ambas
- 16/04 09:34 BUY (MER, SL): ✓
- 17/04 09:06 BUY (MEC/Envolvente, TP): ✓
- 21/04 09:05 SELL (MER, TP): ✗ -- mismo patrón del margen 0,01% ya aceptado
  (rompe a las 09:06 por solo USD 0,10). Quinto caso del mismo fenómeno.
- **22/04 09:28 BUY (MER, TP): ✗ -- hallazgo NUEVO, distinto al margen.**
  A las 09:28 hay una envolvente clásica perfecta (env=1) justo cuando el
  precio toca el nivel M3 (a solo USD 0,22 del margen). Pero la vela que
  rompe el nivel es la de las 09:29, y esa vela NO tiene ningún patrón
  (env=0) -- el código exige ruptura + patrón en la MISMA vela, así que
  sigue esperando hasta que otra vela junte las dos cosas: recién pasa a
  los 9 minutos (09:37). Hipótesis (sin confirmar, no se toca el código):
  Fabian podría estar usando el patrón que se forma AL TOCAR el nivel como
  confirmación visual suficiente, sin exigir que la ruptura numérica caiga
  en esa misma vela -- coincide con el punto de Diego sobre percepción
  visual de niveles. Pendiente: buscar más casos de este tipo (ruptura y
  patrón en velas separadas) antes de proponer nada.
- 23/04 09:16 BUY (MER, TP): ✓
- 24/04 09:21 SELL (MER, TP): ✓
- 27/04 09:16 BUY (MER, SL) y 10:26 SELL (MER, SL): ✓ ambas

### 28/08/2026 — Días 24-33 (26/03 a 09/04/2026): 12/13 exactas
- 26/03 09:44 BUY (MER, SL): ✓
- 27/03 09:09 SELL (MEC/Envolvente, TP): ✓
- 30/03 09:05 SELL (MER, TP): ✓
- 31/03 09:09 BUY (MER, SL) y 09:25 SELL (Hedge/MER, TP): ✓ ambas
- 01/04 10:45 BUY (MEC/START, TP): ✓
- 02/04 09:41 BUY (MER, TP): ✓
- 06/04 09:24 BUY (MER, TP): ✓
- 07/04 09:54 BUY (MER, SL): ✓ -- **10:01 SELL (Hedge/MER, TP): ✗** mismo
  patrón del margen 0,01% ya aceptado (cierre a solo USD 0,08 del umbral,
  código dispara a las 10:02). Cuarto caso del mismo fenómeno (23/02, 05/03,
  07/04) -- no se toca, ya confirmado por Diego que el margen queda como está.
- 08/04 09:10 SELL (MER, TP): ✓
- 09/04 09:33 BUY (MER, TP): ✓

### 28/08/2026 — Diego pide reportes de a 10 días, sin saltear ninguno
"no quiero que te apures... si me puedes dar reportes de a 10 para hacerlo
lo mas eficiente, pero sin saltearse nada, lo primero es que todos tienen
que coincidir". De acá en más se procesa y valida cada día en orden
cronológico (sin saltos), reportando en bloques de 10 días.

### 28/08/2026 — Días 14-23 (05/03 a 25/03/2026): 15/16 exactas
- 05/03 09:04 BUY: ✗ (caso ya conocido, margen 0,01%, aceptado -- no se toca)
- 05/03 10:01 BUY (MEC/START, SL): ✓
- 12/03 09:15 SELL (MEC/Envolvente, TP): ✓
- 13/03 09:25 SELL (MEC, TP): ✓
- 16/03 09:28 SELL (MER, SL) y 10:19 SELL (MEC/Envolvente, TP): ✓ ambas
- 17/03 09:01 BUY (MER, TP): ✓
- 18/03 10:05 BUY (MER, SL), 10:20 SELL (Hedge/MER, TP), 10:45 BUY
  (Hedge/MER, TP): ✓ las 3
- 20/03 09:10 SELL (MEC/Envolvente, TP): ✓
- 23/03 10:15 BUY (MEC/Envolvente, TP): ✓
- 24/03 10:10 BUY (MEC/START, TP): ✓
- 25/03 09:45 SELL (MEC/Envolvente, TP): ✓

### 28/08/2026 — Días 11, 12, 13 (03/03, 09/03, 10/03/2026): CONFIRMADOS
- Día 11 (03/03): BUY 10:37, MER, TP +1.0R. **✓ exacto**.
- Día 12 (09/03, 2 operaciones): BUY 09:30 (MER, SL -1R) y SELL 09:41
  (Hedge Position/MER, TP +1.0R). **✓ ambas exactas**.
- Día 13 (10/03, 2 operaciones): BUY 09:21 (MEC/Envolvente, SL -1R) y SELL
  10:07 (MEC/START, SL -1R). **✓ ambas exactas**.

Racha de 13 días seguidos sin ningún fallo real de reconocimiento (día 6 y
el caso 05/03 siguen con el desfase/no-match del margen 0,01%, ya aceptado
por Diego como no-problema).

### 28/08/2026 — Día 10 (02/03/2026): CONFIRMADO
Fabian: SELL 09:04→(TP), modelo MEC, patrón START, TP +1.0R. **✓ exacto** (MEC-A).

### 28/08/2026 — Día 9 (26/02/2026): CONFIRMADO (2 operaciones)
Fabian: BUY 09:22 (MER, SL -1R) y SELL 10:27 (MEC, Envolvente, SL -1R).
**✓ ambas exactas** (MEC-A). Diego confirmó que el margen del 0,01% queda
como está -- no hay problema con ese número, se descarta tocarlo por ahora.

### 28/08/2026 — Diego corrige el criterio de "coincide": exacto, no tolerancia
Diego rechazó la idea de usar una ventana de ±15 min como métrica de éxito:
"la idea es que coincida lo que hace fabi con nuestro algoritmo... quiero
que cada cosa me vayas preguntando... tenemos que lograr que el código tome
todo en tiempo y forma". Se descarta la métrica de tolerancia -- el estándar
sigue siendo minuto exacto + mismo lado, como se venía haciendo día por día.
También planteó una hipótesis importante: un trader humano percibe niveles
de forma VISUAL, no numérica exacta -- por eso el margen del 0,01% (que en
estos precios representa apenas USD 0,49-0,52) podría estar exigiendo una
precisión que Fabian no aplica en la práctica. Investigado con evidencia
externa: incluso el copy-trading 100% automático (broker a broker, sin
humano) tolera 20-100ms de latencia como normal, nunca "el mismo instante"
-- reforzando que no hay que buscar precisión perfecta, pero el criterio de
"coincide" en ESTE proyecto igual exige el minuto exacto, no una ventana.
El ajuste del margen del 0,01% queda pendiente de confirmación de Diego
antes de tocar el código (2 casos reales lo señalan: 23/02 y 05/03/2026).

### 28/08/2026 — Día 8 (25/02/2026): CONFIRMADO
Fabian: SELL 09:23→09:35, modelo MEC, patrón Envolvente, TP +1.0R.
**✓ exacto** (MEC-A).

### 28/08/2026 — Caso 16/06/2026 resuelto: era hueco de dato, no lógica
Al parchear los 4 días que arrancaban a las 09:00 NY en vez de las 08:00 NY
(03/06, 27/04, 04/06, 16/06/2026 -- mismo tipo de problema que el día 4),
el caso 16/06/2026 09:16 SELL pasó de "no reconocida" a **EXACTO**. El caso
05/03/2026 09:04 BUY sigue sin resolver -- es el del margen 0,01%, no dato.

### 28/08/2026 — Día 7 (24/02/2026): CONFIRMADO
Fabian: BUY 09:38→10:45, modelo MEC, patrón Envolvente, TP +1.0R.
**✓ reconocida** (MEC-A).

### 28/08/2026 — Día 6 (23/02/2026): NO reconciliado -- desfase de 2 min por margen ChOC
Fabian: BUY 09:12→09:24, modelo MEC, patrón START, TP +1.0R.

**✗ NO reconocida a las 09:12** -- el código recién reconoce BUY a las 09:14.
Diagnóstico exacto (no es un caso de "señal extra", es un desfase real de
la entrada de Fabian):
- El patrón START (pullback + indecisión + envolvente) se completa EXACTO
  en la vela de las 09:12 (`start_alc=True`).
- Pero el ChOC (quiebre del nivel M3 opuesto) todavía no confirma: a las
  09:12 el cierre (5153,165) está a solo **USD 0,18 del umbral** requerido
  por el margen del 0,01% (5153,345) -- rompe recién a las 09:14 (cierre
  5157,05, muy por encima).

Fabian entró apenas el precio cerró por encima del nivel M3 (ruptura visual
de ~0,0065%), sin exigir el margen completo de 0,01% que el código aplica
como umbral duro. Es la primera vez que aparece este tipo de desfase --
no se toca el umbral con un solo caso (es literal del PDF), pero queda
marcado como candidato a revisar si se repite en más días: ¿el margen del
0,01% es correcto tal cual está escrito, o Fabian lo aplica con más
tolerancia visual en la práctica?

**Pendiente**: acumular más casos de este tipo (entrada real de Fabian a 1-2
minutos de una ruptura de nivel M3 que el código todavía no confirma por el
margen) antes de decidir si se ajusta el 0,01%.

### 28/08/2026 — Día 5 (20/02/2026): CONFIRMADO
Fabian: SELL 10:02→10:05, modelo MER, TP +1.0R. **✓ reconocida** (MEC-A/MER).

Se encontraron y quedaron en cola de parcheo 12 huecos intra-día más (1-2
horas cada uno) repartidos entre 25/02/2026 y 11/08/2026 -- mismo tipo de
problema que el día 4 (fallo puntual de descarga, no de lógica). Corriendo
`data/parchear_huecos_intradia.py` en background para no repetir el susto
en los próximos días de la bitácora.

### 28/08/2026 — Día 4 (19/02/2026): CONFIRMADO (con parche de dato)
Fabian: SELL 09:07→09:34, modelo MEC, patrón START, TP +1.0R.

Primera pasada: **✗ NO reconocida** -- pero no era un problema de reglas.
`XAUUSD_M1.csv` tenía un hueco real de una hora completa (14:00-14:59 UTC =
09:00-09:59 NY) ese día -- salta de 08:59 directo a 10:00, producto de un
fallo de descarga anterior. Se parcheó con una descarga puntual de esa sola
hora vía Dukascopy (`data/parchear_hueco_19feb.py`, mismo motor validado que
los downloaders de fondo) e insertada en el CSV base (29.576 → 29.636 filas).

**Con el dato completo: 09:07 SELL ✓ reconocida** (MEC-A / START).

**Aprendizaje del día**: antes de asumir que un día no calibra por lógica,
chequear que el dato M1 esté completo para esa ventana -- un hueco de una
hora en medio de la sesión operable puede simular un "no reconocido" que en
realidad es un problema de datos, no de reglas. Vale la pena correr un
chequeo de huecos sobre todo el rango antes de seguir día por día para no
repetir este mismo susto.

### 28/08/2026 — Día 3 (18/02/2026): CONFIRMADO
Fabian: BUY 09:31→09:36, modelo MEC, patrón Envolvente, TP +1.0R (no hubo
trades entre el 12/02 y el 17/02 -- Fabian no operó esos días, por eso el
orden cronológico salta directo del día 1 al día 2 al día 3 así).

**09:31 BUY: ✓ reconocida** (MEC-A).

Este día deja ~35 señales extra en la ventana 09:01-10:59 (casi todas BUY,
consistente con una tendencia alcista sostenida donde cada vela con patrón
Envolvente/START dentro de la continuación ya establecida cumple MEC-A por
definición del PDF). Confirma en la práctica lo que Diego señaló: "él no
toma muchas entradas... en el futuro cuando tengamos el código bien
fabricado, vamos a tomar esas entradas" -- el filtro de Fabian es
selectividad discrecional por ENCIMA del mínimo mecánico del PDF, no un
error del código. Catalogado, no se toca ahora.

**Aprendizaje del día**: confirma que la definición de MEC-A ("tendencia ya
establecida, dispara con cada patrón nuevo que aparece dentro de la
continuación") es literal y va a producir muchas señales en tendencias
largas y limpias -- es información valiosa para la fase de expansión
("¿cuáles de esas 35 señales extra habría convenido tomar? ¿hay alguna
característica que las distinga de la que Fabian sí tomó, más allá de que
fue la primera del día?").

### 28/08/2026 — Cambio de método de validación: coherencia con Fabian primero
Diego marcó una prioridad clara: "quiero que hagas lo que hizo Fabian... el
filtro [de Fabian] no toma otras cosas que nosotros sí... por ahora tenemos
que tener coherencia entre lo que hace Fabian operando cada día... lo extra
lo vamos a ir encontrando" -- es decir, la calibración día a día no es
"correr el motor solo y ver qué operaciones salen", sino: ¿el código
RECONOCE cada entrada real de Fabian en su horario exacto? Las señales que
el código encuentra pero Fabian no tomó se catalogan aparte (para expandir
el código más adelante), sin bloquear ni contaminar la validación del día.

Esto corrige el método usado más arriba (motor autónomo con circuit-breaker):
la señal extra de las 09:01 del día 2 nunca cerraba (SL/TP) y por eso
"tapaba" la señal real de las 09:33 en la simulación -- no era necesariamente
un bug de reglas, era un problema de cómo se estaba comparando. Con el nuevo
método (`validar_entrada_fabian.py`), se evalúa en cada vela si mecA/mecB/mer
reconoce una entrada, sin tomar posición ni aplicar circuit-breaker, y se
chequea puntualmente si la hora real de Fabian aparece reconocida.

**Resultado con el nuevo método -- AMBOS DÍAS CONFIRMADOS:**
- Día 1 (12/02/2026) 09:03 SELL: ✓ reconocida (MEC-A / patrón START).
- Día 2 (17/02/2026) 09:33 SELL: ✓ reconocida (MEC-A/MER, envolvente clásica).

La entrada de las 09:01 del día 2 (SL ~USD 66, sobre el desplome previo a
sesión) queda catalogada como "señal extra no tomada por Fabian" -- no se
investiga ni se filtra ahora, es candidato para la fase de expansión futura
("lo extra lo vamos a ir encontrando"). Cada día trae varias señales extra
de este tipo (ver salida completa de `validar_entrada_fabian.py`) -- normal,
esperado, y no bloqueante mientras el foco sea coherencia con Fabian.

**Regla de método para lo que sigue**: seguir día por día con
`validar_entrada_fabian.py` (reconocimiento puntual del horario real de
Fabian), no con el motor autónomo de `backtest_dia()` -- ese motor autónomo
se retoma recién cuando se pase a la fase de "expandir el código" con las
señales extra.

### 28/08/2026 — DÍA 1 RESUELTO Y CONFIRMADO (motor unificado)
Diego pidió expresamente "resolvamos el día 1". Se encontraron y corrigieron
2 bugs reales más (además del M3-close-only del punto anterior), y se fusionó
el detector de START ya calibrado dentro de `backtest_dia()`:

1. **`backtest_dia()` reseteaba el M3/tendencia al abrir la ventana operable
   (09:01 NY).** A las 09:03 real todavía no había 2 velas M3 cerradas dentro
   de la ventana, así que el ChOC que sí vio Fabian (con contexto de antes de
   las 09:01) era invisible para el código. Se confirmó con Diego que el M3
   NO debe resetear -- se arma continuo, igual que en `EstrategiaXAU.pine`
   (que usa `request.security` sin reset, esto ya estaba bien en el Pine,
   el bug era solo del replica Python). Ahora `backtest_dia(g_sesion,
   t_inicio_entradas)` arma M3/tendencia con TODO el dato disponible y solo
   permite ABRIR operaciones desde `t_inicio_entradas` en adelante. Diego
   además pidió ampliar el alcance: estudiar las 24hs del mercado, día por
   día, para buscar oportunidades en otros horarios además de la ventana
   09:01-10:59 ya validada -- pendiente de datos (ver downloads en curso).

2. **Doji (tipo 3 de `tipo_envolvente`) se estaba usando como señal válida
   de entrada** en `patron_alcista_mec`/`patron_bajista_mec`, `mer_long`,
   `mer_short` -- el propio Plan Técnico dice que el doji es "inválido como
   señal standalone". Corregido: ahora solo tipo 1 (clásica) o 2 (martillo)
   disparan entrada (`env_x in (1, 2)`), tanto en MEC como en MER como en la
   vela de confirmación de `es_start()`.

**Resultado día 1 (12/02/2026): SELL 09:03 exacto, mismo minuto que Fabian.**
Antes disparaba a las 09:19 (sin M3 corregido ni START), después a las 09:14
(con M3 corregido, sin START), ahora 09:03 con las 3 correcciones juntas.
Ver `comparacion_dia1_motor_unificado.py` / `dia1_motor_unificado_confirmado.png`.

**Día 2 (17/02/2026): nuevo hallazgo, no resuelto todavía.** Con el M3
continuo, el código ahora ve un desplome fuerte entre 08:45-09:00 (~USD 80 en
15 min) que Fabian no operó (empieza recién a las 09:01). Eso deja una fase
de continuación bajista (`mecFaseB=2`) ya activa al abrir la ventana, y a las
09:01 dispara un SELL con un SL de ~USD 66 (nivel M3 opuesto muy lejano,
producto del desplome) -- Fabian no tomó esta operación. Esa posición nunca
toca ni SL ni TP durante el resto de la sesión, así que queda abierta todo
el día y el código **nunca llega** a la señal real de las 09:33. Esto es el
mismo tipo de hallazgo que ya estaba pendiente ("filtro de fuerza de señal",
ver entrada de abajo) pero ahora con un caso concreto y medible: una entrada
con SL desproporcionado (USD 66) que monta un movimiento previo a la sesión.
**Pendiente para la próxima sesión**: revisar más casos como este (¿Fabian
descarta continuaciones cuyo SL es muy grande respecto al SL típico de sus
operaciones reales? ¿hay un techo de distancia razonable?) antes de proponer
un número — no inventar un filtro con un solo caso.

### 28/08/2026 — BUG REAL encontrado y corregido: M3 se armaba mal
Diego marcó el error de fondo: el M3 se estaba resampleando SOLO del precio
de cierre (`close.resample('3min').ohlc()`), lo que genera un OHLC de 3min
sintético a partir de una serie de cierres -- ignora las mechas reales que
tocó el precio en M1 dentro de cada tramo de 3 minutos. Corregido a
`g_sesion.resample('3min').agg(open='first', high='max', low='min', close='last')`
sobre las columnas REALES de M1.

**Resultado al re-correr los días 1 y 2 con el M3 corregido:**
- **Día 2 (17/02/2026): AHORA SÍ coincide con Fabian.** El código dispara
  SELL a las 09:33 -- el mismo minuto exacto. Antes (con el M3 roto) disparaba
  a las 09:16 con una señal débil. El código también toma una operación extra
  a las 09:31 (BUY, continuación del rally, pierde -1R) antes de la señal real
  -- es una operación legítima por las reglas (no un bug), coincide con el
  "escenario 2" del Plan Operativo (1 SL + 1 TP detiene el día). Fabian no la
  tomó -- pendiente entender por qué (¿descarta visualmente el tope del rally?
  ¿alguna regla de "único nivel M3 opuesto" que todavía no estamos aplicando
  ahí?).
- **Día 1 (12/02/2026): mejora parcial.** Sin M3 roto, el MEC-A/MER pasa de
  disparar a las 09:19 a las 09:14 -- más cerca pero todavía no en el 09:03
  real. Día 1 sigue necesitando el patrón START (ya calibrado por separado,
  ver más abajo) fusionado al motor principal para calzar exacto.

**Pendiente inmediato**: fusionar el detector de START (ya validado) dentro
de `backtest_dia()` como una tercera vía de entrada para MEC, y volver a
correr los días 1 y 2 juntos con el M3 corregido + START incluido.

### 28/08/2026 — Día 2 (17/02/2026): problema nuevo, distinto al del día 1
Fabian: SELL 09:33, MER, TP +1R — entrada en la punta de un rally limpio y
sostenido (4843→4905), lectura de agotamiento de impulso.
Código (con fórmula ya corregida): BUY 09:16, +0,9R — entra en una zona
lateral/chica (cuerpo 25,7%), técnicamente válida pero visualmente débil,
DENTRO del mismo rally que Fabian esperó a que termine. Gana por casualidad
y activa el límite diario (1 TP = se detiene el día), así que el código
**nunca llega** a la señal real de las 09:33.

**Hallazgo**: no es un problema de fórmula de vela (ya corregida). El código
no distingue señal fuerte de señal débil — dispara con cualquier cosa que
cumpla el mínimo matemático, sin filtrar por si el contexto previo (fuerza
del quiebre, claridad de la estructura M3) es suficiente. Fabian aplica ese
filtro aunque no esté escrito explícitamente en el plan como una regla numérica.

**Pendiente para la próxima sesión**: definir un filtro de "fuerza de señal"
objetivo (candidatos: exigir que el quiebre del nivel M3 sea más amplio que
el 0.01% mínimo: por volumen de velas en la ruptura, o por la distancia
recorrida en el "Quiebre" de MEC-B antes de la Continuación) y probarlo
contra más días para ver si reduce este tipo de falso positivo sin perderse
señales reales.



### 27/08/2026 — Patrón START calibrado y confirmado (día 1: 12/02/2026)
Ver detalle arriba. Pendiente: correr esta fórmula de START sobre las 19
operaciones reales con patrón START (igual que se hizo con Envolvente,
56,9%→96,1%) para medir el % de coincidencia real, no solo este caso 1.
