---
name: ingenieria-diagnostico-repo
description: Audita el repo por problemas estructurales (archivos con nombres rotos, secretos filtrados, permisos demasiado abiertos, colisiones de rutas). Usar cuando Diego pida revisar/limpiar/ordenar el repo, o si algo "no está andando" sin causa obvia.
---

# Diagnóstico de salud del repo

Equipo: Ingeniería/Automatización. Formaliza el chequeo que se hizo el 2026-07-25 al reparar el proyecto (ver `git log` de esa fecha para el precedente completo: token de Meta filtrado + archivos con nombre roto por una extracción de Windows).

Checklist a correr:

1. **Nombres de archivo rotos** — buscar archivos con `\` literal en el nombre (típico de una extracción/copiado mal hecho en Windows): `git ls-files | grep '\\\\'`. Si aparece algo, no está viviendo en la carpeta real que su nombre sugiere.
2. **Secretos filtrados** — buscar patrones de tokens/API keys en archivos trackeados:
   `git grep -ilE "access_token=[A-Za-z0-9]{20}|api[_-]?key['\"]?\s*[:=]\s*['\"][A-Za-z0-9]{15}|sk-[A-Za-z0-9]{20}|AIza[A-Za-z0-9]{30}" HEAD`.
   Si hay resultados: no arreglar solo el archivo actual, el token puede seguir en el historial de git (`git log -p --all | grep -i <patrón>`). Avisar a Diego antes de reescribir historial o forzar push — eso se confirma con él siempre.
3. **Permisos demasiado abiertos** — revisar `.claude/settings.local.json` por entradas tipo `Bash(*)` o `"allow": ["*"]` sin acotar.
4. **`.gitignore` desactualizado** — confirmar que `.env`, `.claude/settings.local.json` y carpetas de salida generada (reports/, charts/) están ignoradas.
5. Reportar en español, priorizado: qué es urgente (secretos) vs. qué es prolijidad (nombres, estructura).
