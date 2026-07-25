---
name: marketing-optimizar-meta-ads
description: Genera recomendaciones de targeting, copy, creativos y estructura de campaña para Meta Ads del consultorio. Usar cuando Diego pida optimizar/armar una campaña de Meta Ads o pregunte cómo mejorar el rendimiento de los anuncios.
---

# Optimización de Meta Ads

Equipo: Marketing/Contenido.

1. Ejecutar desde la raíz del repo: `python jarvis/marketing/run_marketing.py meta`
   (corre `meta_optimizer.py`).
2. Basar las recomendaciones en `jarvis/marketing/data/config.json` (budget, procedimientos, geo, keywords ya configurados) y en `jarvis/marketing/knowledge/optimizacion_campanas.md` + `copy_y_creatividades.md`.
3. Si Diego menciona un procedimiento específico (rinoplastia, lipo, mamoplastia, bichectomía), priorizar ese en la recomendación en vez de dar algo genérico.
4. Presupuesto de referencia: USD 500–2.000/mes (ver memoria de proyecto). No sugerir presupuestos fuera de ese rango sin que Diego lo pida.
