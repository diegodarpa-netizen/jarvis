# ⚠️ BASE DE CONOCIMIENTO — NO TOCAR

Esta carpeta es la fuente original de la estrategia manual de Fabian para
XAU/USD. Es la base de todo lo que se construyó en `EstrategiaXAU.pine` y
en el análisis de `fabian_manual_strategy/INFORME_COMPLETO.md`.

**No editar, no borrar, no mover estos archivos.** Si hace falta releer el
plan técnico o el histórico original, se hace desde acá.

## Contenido

- `Plan técnico XAU.pdf` (31 páginas) — la regla completa: estructura M3,
  línea punteada (tendencia) vs línea continua (cambio de estructura/ChOC),
  patrón Envolvente (3 variantes: clásica/martillo/doji), patrón START
  (morning/evening star), modelos MEC y MER, Hedge Position, stop loss y
  take profit (RR 1:0.9).
- `Plan operativo XAU.pdf` — horario de sesión (09:01-10:59 NY), reglas de
  noticias (Forex Factory, ventanas de no-operativa), límite diario (3
  escenarios: 1 TP solo / 1 SL+1 TP / 2 SL detienen el día).
- `Apariencia del indicador XAU.pdf` — formato visual aprobado (ver también
  `jarvis/trading/rules/apariencia_labels.md`, que ya lo resume).
- `fabian_export_whatsapp_original.zip` — el export original de Notion vía
  WhatsApp con el historial real de 191 operaciones (27/10/2025-27/08/2026),
  sin procesar. La versión limpia y analizada está en
  `fabian_manual_strategy/fabian_consolidado_limpio.csv`.

## Actualización 30/08/2026 — PDFs revisados por Fabian

Fabian mandó versiones actualizadas de ambos PDFs (respondiendo dudas de la
calibración vela por vela) — **usar estas como la versión vigente**, los
originales del 27/08 quedan solo como historial:

- `Plan tecnico XAU (actualizado 30-08-2026).pdf`
- `Plan operativo XAU (actualizado 30-08-2026).pdf`
- `respuestas_fabian_30-08-2026.md` — sus explicaciones textuales sobre 5
  casos puntuales (07/04, 22/04, 30/04, 22/05, 25/08/2026) que no coincidían
  entre el código y sus operaciones reales, LEER ANTES de retomar la
  calibración.

Cambios grandes en esta versión: el Plan Operativo ahora define 3 sesiones
habilitadas (Pre New York 07:00-09:00, New York 09:02-11:00, Asia
20:02-22:00 NY) en vez de solo 1; noticias no-operables ahora incluyen
CNY/JPY además de USD; hay un receso de fin de año (3ra sem. dic. a 3ra
sem. ene.); el Plan Técnico agrega una regla de flexibilidad del 0,01% para
la envolvente clásica (condicionada a resultado semanal positivo y primera
operación del día) y confirma que el margen de ruptura se mide "con
cuerpo" (cierre), no con la mecha.

## Por qué se guarda así

Fecha de consolidación: 27/08/2026. A pedido de Diego — es la base de
conocimiento más completa que existe del sistema de Fabian, y de acá salió
`EstrategiaXAU.pine` (el primer intento fiel al Plan Técnico completo,
corrigiendo huecos del `XAU_Strategy.pine` anterior que no tenía patrón
START, ni las 3 variantes de envolvente, ni la lógica de Hedge Position).
