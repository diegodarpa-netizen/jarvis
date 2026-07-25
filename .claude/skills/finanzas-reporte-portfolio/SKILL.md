---
name: finanzas-reporte-portfolio
description: Muestra o envía el estado del portfolio de CEDEARs de Diego (P&L en tiempo real, reporte HTML por email). Usar cuando Diego pida ver su portfolio, cómo van sus posiciones, o que le mande el reporte.
---

# Reporte de portfolio (CEDEARs)

Equipo: Trading/Finanzas.

1. Datos en vivo: `jarvis/portfolio/active_positions.json` y `jarvis/portfolio/watchlist.json`.
2. Para P&L actualizado (convierte ARS→USD vía CCL): `python jarvis/scripts/portfolio_tracker.py`.
3. Si Diego pide el reporte completo/HTML: encadenar con `jarvis/scripts/report_builder.py` (arma el HTML en español) y, si pide que se lo mandes, `jarvis/scripts/send_email.py`.
4. Formato de números: punto de miles, coma decimal (ver `CLAUDE.md`). Perfil de riesgo de Diego: moderado-agresivo a agresivo — no suavices recomendaciones por defecto.
