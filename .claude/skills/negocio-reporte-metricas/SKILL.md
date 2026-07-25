---
name: negocio-reporte-metricas
description: Arma un resumen ejecutivo cruzando portfolio, marketing y trading para que Diego tenga una foto general del negocio. Usar cuando Diego pida "cómo viene todo", un estado general, o un resumen tipo CEO.
---

# Reporte ejecutivo (vista CEO)

Equipo: Negocio/Ops. Este es el resumen que cruza los otros 3 equipos — pensado para cuando Diego pregunta algo amplio en vez de pedir un equipo puntual.

1. Portfolio/Finanzas: correr `finanzas-reporte-portfolio` (P&L actual).
2. Marketing: si hay algo reciente en `jarvis/marketing/reports/` o corriendo `marketing-briefing-diario`, resumir el foco de contenido/campaña de la semana.
3. Trading: estado de las estrategias activas según `jarvis/trading/memory/strategy_notes.md` (no hace falta correr backtests para esto, es un resumen de estado, no un análisis nuevo).
4. Armar un resumen corto (no un reporte de 10 páginas): 3-4 bullets por área, y un párrafo final con lo que más necesita la atención de Diego hoy.
