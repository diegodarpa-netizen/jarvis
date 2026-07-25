---
name: marketing-seguimiento-leads
description: Gestiona el seguimiento de leads por WhatsApp del consultorio (recordatorios, respuestas). Usar cuando Diego pida hacer seguimiento a un paciente/lead, o algo de WhatsApp Business.
---

# Seguimiento de leads por WhatsApp

Equipo: Marketing/Contenido (frontera con Negocio — si lo que pide es más "cerrar la venta" que "responder un lead", ver también `.claude/skills/negocio-reporte-metricas`).

1. Ejecutar desde la raíz del repo: `python jarvis/marketing/run_marketing.py whatsapp [subcomando]` (por defecto `info` si no se pasa subcomando).
   Esto corre `jarvis/marketing/scripts/whatsapp_leads.py`, integración con WhatsApp Business.
2. Las credenciales de la integración van en `.env` en la raíz — nunca pedirle a Diego el token/API key por chat, y nunca hardcodearlo en un comando de Bash (ver regla de seguridad en `CLAUDE.md`).
