# Registro completo — Calibración vela por vela (28-30/08/2026)

> Todo lo que dijo Fabian en este proceso es oro — este documento guarda
> el registro completo de la sesión, no solo un resumen. Complementa
> (no reemplaza) `seguimiento_vela_por_vela/README.md` (bitácora técnica
> día por día) y `base_conocimiento_NO_TOCAR/respuestas_fabian_30-08-2026.md`
> (las respuestas textuales de Fabian).

---

## 1. Punto de partida (28/08/2026)

Día anterior a esta sesión: el código replicaba el patrón START, pero
"Día 1" (12/02/2026, SELL 09:03 de Fabian) no coincidía — disparaba a las
09:19. Diego pidió resolverlo: *"resolvamos el día 1, por que no funciona,
por que no podes hacer y corroborar igualmente dependiendo a los pdf lo
que hizo fabian"*.

### Bugs reales encontrados y corregidos (28/08)
1. **M3 se reseteaba al abrir la ventana operable (09:01 NY)** — la
   estructura M3 no debe resetear, se arma continua desde antes (igual
   que `request.security` en el `.pine`, que nunca resetea).
2. **Doji (tipo 3 de envolvente) se usaba como señal válida** — el Plan
   Técnico dice que es "inválido como señal standalone"; corregido a solo
   clásica (1) o martillo (2).
3. Con ambos fixes + el patrón START ya fusionado: **Día 1 pasó a
   coincidir EXACTO (SELL 09:03)**.

### Cambio de método de validación
Diego corrigió el enfoque: no correr el motor de forma autónoma (con
circuit-breaker) y diffear la lista de operaciones — una señal extra que
nunca cierra puede tapar la señal real. Método correcto: por cada
operación REAL de Fabian, chequear si el código la reconoce en su horario
exacto, catalogando aparte (sin bloquear) las señales que el código
encuentra pero Fabian no tomó.

> *"quiero que hagas lo que hizo fabian, el filtro no toma otras cosas
> que nosotros sí... por ahora tenemos que tener coherencia entre lo que
> hace fabian operando cada día... lo extra lo vamos a ir encontrando"*

## 2. Recorrido día por día — primera pasada (28/08/2026)

Se recorrieron las 139 operaciones de Fabian con dato disponible (12/02 al
27/08/2026), en bloques de 10 días (a pedido explícito: *"no quiero que te
apures, pero si me puedes dar reportes de a 10 para hacerlo lo mas
eficiente, pero sin saltearse nada, lo primero es que todos tienen que
coincidir"*).

Se descubrió y corrigió un hallazgo mayor: **el quiebre del nivel M3
medido con la mecha (high/low) en vez del cierre**, después de que Diego
le mandara a Fabian una imagen del caso 21/04 y Fabian confirmara: *"la
vela sí superó ese 0.01% luego de quebrar el bajo, por eso la tomé, sino
no la hubiese ejecutado, el mide con el rango de precios, herramienta de
tradingview"*. Verificado con dato exacto: el low de la vela SÍ perforaba
el margen aunque el cierre no.

**Resultado de la primera pasada completa: 134/139 exactas (96,4%)**,
0 sin explicar, quedaron 5 casos límite documentados con imágenes
(comparación Fabian vs código lado a lado, generadas y enviadas a Diego):
- 07/04 (SELL 10:01): patrón y ruptura en velas separadas.
- 22/04 (BUY 09:28): patrón antes de que el nivel se rompa.
- 30/04 (SELL 09:34): mismo tipo que 07/04.
- 22/05 (SELL 10:03): código dispara ANTES (10:00) -- único caso al revés.
- 25/08 (SELL 10:19): margen a USD 0,13 del umbral, ni con mecha.

Diego pidió mandarle estas 5 imágenes a Fabian por WhatsApp para que las
revise (no había herramienta de WhatsApp disponible en la sesión --
Diego las reenvió él mismo).

## 3. Exploración de franjas horarias (28/08/2026, en paralelo)

A pedido de Diego: *"quiero abrirlo, para ver si en otras sesiones, asia
o demás, hay oportunidades con este tipo de estrategia"*. Se usó una
muestra de 40 días de dato 24hs (27/10-19/12/2025) para correr el motor
mecánico (sin el filtro discrecional de Fabian) en TODAS las horas del
día, no solo 09:01-10:59 NY.

**Resultado**: 803 operaciones, WR 52,3%, R total -5,0 (neutro, esperado
sin el criterio humano de Fabian). Por franja, Asia se veía mejor (+29,2R)
pero el bootstrap (mismo test de todo el proyecto) mostró que NINGUNA
franja era significativa con 40 días de muestra -- el intervalo de Asia
cruzaba cero por muy poco.

Se descargó después una semana completa (18-22/08/2026, 24hs) a pedido de
Diego para un análisis más chico y controlado -- quedó pendiente de
correr el backtest sobre esa semana (interrumpido por el rediseño visual
del Pine y la respuesta de Fabian).

## 4. Rediseño visual del `.pine` (28/08/2026)

Diego pidió armar el código con todo lo aprendido, pero con estética
nueva ("que se vea similar a las fotos con la cual contrastábamos con
fabian, así lo subo al pine script"). Proceso iterativo con mockups
simulados (matplotlib, estilo TradingView):
1. Rechazó el formato triángulo aprobado anteriormente Y el cartel tipo
   "nube" -- pidió líneas (entrada sólida, SL/TP punteadas) sin
   etiquetas de precio, con franjas verticales de fondo por tendencia
   (ya aprobado en `apariencia_labels.md`) y marca de dirección BUY/SELL.
2. Iteró la etiqueta de dirección: capsula grande horizontal → vertical
   azul/gris → vertical roja/verde chica (esta última, la más reciente,
   fue la mejor recibida).
3. Se probó una galería de 3 estilos alternativos (cápsula oval,
   diamante, banderín) -- **rechazados todos** ("no me gusta ninguno...
   es la forma").
4. Segunda galería con formas más simples (punto+texto, solo texto,
   flecha) -- quedó sin definir un ganador claro antes de que llegara la
   respuesta de Fabian y el foco cambiara.
5. Se mostró también el formato ACTUAL del `.pine` (sin tocar) para
   comparar. **El `.pine` real (`EstrategiaXAU.pine`) todavía NO fue
   modificado** -- todo esto quedó en mockups de exploración
   (`fabian_manual_strategy/mockup_estilo_pine*.py`,
   `galeria_etiquetas*.py`, `estilo_actual_pine.py`).

## 5. Respuesta de Fabian y PDFs actualizados (30/08/2026)

Diego mandó por WhatsApp las 5 imágenes de casos sin resolver. Fabian
respondió con explicaciones detalladas y mandó versiones actualizadas de
ambos PDFs base. **Texto completo y verbatim de sus respuestas guardado
en** `base_conocimiento_NO_TOCAR/respuestas_fabian_30-08-2026.md` -- acá
solo el resumen:

- **07/04 y 30/04**: son "Vela Envolvente Martillo" válida según el PDF
  (Sección Entrada > Patrón envolvente > punto ii).
- **25/08**: usa la herramienta "Rango de precios" de TradingView para
  medir el 0,01% -- coincide con el PDF (pág.21-22), que además aclara
  que el margen se mide "CON CUERPO" (cierre), no con la mecha.
- **22/04**: dice que la vela de entrada SÍ rompe el alto M3, validando
  MER -- contradice nuestro cálculo con dato Dukascopy.
- **22/05**: CONFIRMADO -- Regla N°5 del Plan Operativo (noticias de
  mediano impacto, ventana ±3 min). La señal real fue la vela de las
  10:00, pero se ejecutó a las 10:03 porque en el medio se publicaba
  "Revised UoM Consumer Sentiment" (impacto medio). Regla completa:
  no abrir en la ventana ±3 min; si hay operación abierta, se puede
  mantener; se puede entrar después de la publicación al MISMO precio de
  la vela original, solo si el precio no tocó el SL durante el bloqueo.

### PDFs actualizados -- cambios grandes, no "ajustes pequeños"
Guardados en `base_conocimiento_NO_TOCAR/`:
`Plan tecnico XAU (actualizado 30-08-2026).pdf` y
`Plan operativo XAU (actualizado 30-08-2026).pdf` (los originales del
27/08 quedan como historial, no se borraron).

- **Plan Operativo**: ahora define 3 sesiones (antes 1 sola): Pre New
  York (07:00-09:00 NY), New York (09:02-11:00 NY), Asia (20:02-22:00 NY).
  Noticias no-operables ahora incluyen CNY y JPY además de USD. Nuevo
  receso de fin de año (3ra semana de diciembre a 3ra semana de enero).
  Regla N°5 de noticias de mediano impacto detallada completa.
- **Plan Técnico**: nueva regla de flexibilidad para la envolvente
  clásica (cuerpo a menos de 0,01% del 85% se puede validar, PERO solo si
  el resultado semanal acumulado es positivo Y es la primera operación de
  la sesión). Confirma que el margen de ruptura se mide "con cuerpo"
  (cierre) usando la herramienta "Rango de precios".

## 6. Revert del margen y segunda pasada completa (30/08/2026)

Dado que el PDF actualizado contradecía el fix de la mecha aplicado el
28/08, se revirtió (`prueba_ventana_horaria.py` y
`validar_entrada_fabian.py` vueltos a medir el quiebre con el cierre).

**Hallazgo clave**: Fabian opera con datos de **OANDA** (Plan Técnico
pág.31: "instrumento XAUUSD... commodity CFD OANDA visto en TradingView"),
nosotros usamos **Dukascopy**. La hipótesis mejor sustentada para casi
todos los casos límite es una diferencia de precio entre brokers para el
mismo minuto -- no un bug de fórmula. No es corregible sin cambiar de
fuente de dato.

Diego priorizó fidelidad al PDF sobre el número más alto: *"estos datos
son el corazón de la estrategia"*.

**Resultado del re-recorrido completo (mismas 139 operaciones, bloques de
10-13 días, reportado en vivo): 129/139 exactas (92,8%)**, bajando desde
el 96,4% del fix de la mecha. Los 10 fallos son EXACTAMENTE los mismos 10
casos ya identificados (8 por diferencia de broker, 1 por Regla N°5 de
noticias, 1 -- 22/04 -- contradicho por Fabian). Cero casos nuevos sin
explicar.

## 7. En curso: completar las 191 operaciones (30/08/2026)

Diego pidió expandir el alcance a TODAS las operaciones de Fabian (191
totales, no solo las 139 con dato ya disponible desde 12/02/2026) --
*"quiero que hagas el backtesting de todas las operaciones que nos paso
fabian... que vuelvas ha hacer todo una por una, para que no tengamos
ninguna duda"*.

Las 52 operaciones restantes van del 27/10/2025 (inicio real del
historial) al 11/02/2026. Se usó el dato ya descargado
(`data/XAUUSD_M1_gap_fabian.csv`, ventana 03:00-17:00 NY) fusionado al
CSV principal. Se encontraron y parcharon huecos de datos reales en
27-29/10/2025, 10/11, 12/11, 06/02 y 08/02/2026 (algunos completamente
vacíos) -- descargas puntuales vía Dukascopy, mismo motor validado.

**Estado al momento de escribir este registro**: parche de datos en
curso, validación día por día de las 52 operaciones restantes pendiente
de arrancar (bloques de 10, mismo método que las 139 ya hechas).

---

## Archivos clave de esta sesión (todos dentro de `jarvis/trading_algoritmico/`)

- `fabian_manual_strategy/seguimiento_vela_por_vela/README.md` --
  bitácora técnica día por día, con fecha, la más detallada.
- `fabian_manual_strategy/seguimiento_vela_por_vela/validar_entrada_fabian.py`
  -- función `señales_del_dia()`, el motor de validación actual.
- `fabian_manual_strategy/prueba_ventana_horaria.py` -- motor base
  (`backtest_dia`, `tipo_envolvente`, `es_start`).
- `fabian_manual_strategy/base_conocimiento_NO_TOCAR/` -- PDFs (original y
  actualizado 30/08) + respuestas de Fabian, la fuente de verdad.
- `fabian_manual_strategy/franjas_horarias/` -- exploración de otras
  sesiones (Pre-NY, Asia), en curso.
- `fabian_manual_strategy/mockup_estilo_pine*.py`, `galeria_etiquetas*.py`
  -- exploración visual del `.pine` nuevo, sin decisión final todavía.
- `jarvis/trading/xau_strategy/EstrategiaXAU.pine` -- el `.pine` real,
  **todavía sin las correcciones de esta sesión aplicadas**.
