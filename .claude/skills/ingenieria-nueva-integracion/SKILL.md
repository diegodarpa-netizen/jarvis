---
name: ingenieria-nueva-integracion
description: Checklist para conectar una API/automatización nueva al proyecto (CRM, WhatsApp, alguna herramienta nueva). Usar cuando Diego pida conectar algo nuevo, agregar una integración, o automatizar un proceso manual.
---

# Agregar una integración nueva

Equipo: Ingeniería/Automatización.

1. **Credenciales van en `.env`** (raíz del repo, gitignoreado) — nunca en `.claude/settings.local.json`, nunca hardcodeadas en un comando de Bash ni pegadas directo en un script. Este es el motivo por el que hubo que limpiar un token filtrado el 2026-07-25 — no repetir el error.
2. Agregar la variable nueva también a `.env.example` (sin el valor real) para que quede documentado qué hace falta configurar.
3. Ubicar el código de la integración según a qué equipo sirve: si es de marketing (ej. otra red social, otro ad manager) va en `jarvis/marketing/scripts/`; si es de finanzas/trading va en `jarvis/scripts/` o `jarvis/trading/`; si es transversal (CRM, WhatsApp, automatización general) puede vivir suelta en `jarvis/` con su propio README corto.
4. Probar la integración de forma aislada antes de conectarla a un flujo existente (`run_marketing.py`, etc.) — no asumir que anda solo porque el código compila.
5. Si la integración expone datos sensibles (tokens, IDs de cuenta), correr `ingenieria-diagnostico-repo` después de conectarla para confirmar que no quedó nada filtrado.
