# Publicidad — este módulo usa la infraestructura ya existente

Toda la gestión de campañas pagas (Meta Ads / Instagram Ads / Facebook Ads) **ya está armada** en `../marketing/`. No se duplica acá.

- Campañas exportadas: `../marketing/meta/campanas/`
- Audiencias: `../marketing/meta/audiencias/`
- Creatividades: `../marketing/meta/creatividades/`
- Reportes de performance: `../marketing/meta/reportes/`
- Scripts de análisis: `../marketing/scripts/`

Ver `../marketing/README.md` para el flujo completo de trabajo con Meta Ads.

Cuando pidas algo como *"comparame el gasto en ads vs los leads que generó el consultorio este mes"*, Jarvis va a cruzar datos de `../marketing/` (inversión y performance de campañas) con `../consultorio/agenda/` (turnos generados) para calcular el costo real por paciente.
