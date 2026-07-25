---
name: marketing-briefing-diario
description: Genera el briefing diario de marketing del consultorio (tendencias, noticias, idea de contenido del día). Usar cuando Diego pida el briefing/resumen diario de marketing, o "qué publico hoy".
---

# Briefing diario de marketing

Equipo: Marketing/Contenido.

1. Ejecutar desde la raíz del repo: `python jarvis/marketing/run_marketing.py daily`
   (esto corre `jarvis/marketing/scripts/market_daily.py`, que usa `jarvis/marketing/scripts/web_research.py` como fuente de datos real — no inventes tendencias, ese script existe justo para evitar que se alucinen).
2. El resultado se apoya en el conocimiento de `jarvis/marketing/knowledge/` (estrategia, copy, TikTok/redes, psicología del paciente) — si el briefing necesita contexto adicional, leer los `.md` relevantes ahí antes de responder.
3. Presentar el resultado en español, con la idea de contenido del día bien remarcada arriba.

No usar una API key de Anthropic propia para esto — correr todo en este chat (ver regla de seguridad en `CLAUDE.md`).
