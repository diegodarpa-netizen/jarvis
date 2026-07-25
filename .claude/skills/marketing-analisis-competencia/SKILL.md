---
name: marketing-analisis-competencia
description: Analiza qué están haciendo otras clínicas/consultorios de cirugía plástica en ads y redes (Meta Ad Library, competidores). Usar cuando Diego pida espiar/analizar competencia, o qué ads está corriendo otra clínica.
---

# Análisis de competencia

Equipo: Marketing/Contenido.

1. Ejecutar desde la raíz del repo: `python jarvis/marketing/run_marketing.py competidores`
   (corre `competitor_analyzer.py` + `ad_library_scraper.py`, que interpretan resultados reales de Meta Ad Library — no en `graph.facebook.com` con tokens propios, ver regla de seguridad en `CLAUDE.md`: nunca hardcodear tokens en comandos).
2. Si Diego pide algo más puntual (una clínica específica, no el barrido general), usar `ad_library_scraper.py` directamente para esa búsqueda.
3. Cruzar el resultado con `jarvis/marketing/knowledge/meta_ads_clinica.md` y `estrategia_completa.md` para dar recomendaciones accionables, no solo el dato crudo.
