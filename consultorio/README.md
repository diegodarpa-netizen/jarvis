# Módulo Consultorio — Gestión integral de la práctica

Centraliza todo lo que no es inversión personal: redes sociales, contenido, competencia, equipo, agenda y publicidad del consultorio de cirugía plástica.

Se integra con:
- `../marketing/` → publicidad paga (Meta Ads), ya armado — ver `publicidad/README.md`
- `../jarvis/` → finanzas personales de Diego, módulo separado

---

## Estructura

```
consultorio/
├── data/
│   └── perfil_consultorio.json     ← identidad del consultorio, redes, equipo, contacto
├── equipo/
│   └── equipo.json                 ← las 4 personas del equipo, roles y áreas
├── redes/
│   ├── instagram/
│   │   ├── metricas/               ← snapshots históricos (seguidores, alcance, engagement)
│   │   ├── contenido/              ← guiones, ideas, copies
│   │   └── reels/                  ← registro específico de reels
│   ├── tiktok/
│   │   ├── metricas/
│   │   └── contenido/
│   ├── youtube/
│   │   ├── metricas/
│   │   └── contenido/
│   └── calendario/
│       └── calendario_contenido.json  ← planificación de posteos en las 3 plataformas
├── competencia/
│   ├── perfiles/
│   │   └── cuentas_monitoreadas.json  ← colegas/competencia a seguir
│   └── analisis/                   ← comparativas de formato, frecuencia, engagement
├── agenda/
│   └── turnos.json                 ← turnos de pacientes (en pausa por ahora)
├── publicidad/
│   └── README.md                   ← apunta a ../marketing/ (ya armado)
├── reportes/                       ← reportes HTML generados por Jarvis
└── scripts/                        ← scripts Python del módulo (se van sumando)
```

---

## Equipo

| Persona | Rol | Área |
|---|---|---|
| Diego Rodríguez Pabón | Titular / Cirujano | Consultorio, contenido on-camera |
| Saira | Secretaría / CM Instagram | Redes, responde mensajes |
| Pilar | CM TikTok | Redes, controla mensajes de Instagram |
| Vanina | Redes multicuenta / Asistencia quirúrgica | Redes, cirugía |

Además hay un **agente de respuesta automática** que contesta mensajes (canal exacto a confirmar), supervisado por Saira. Detalle completo en `equipo/equipo.json`.

**Canal de YouTube:** Diego Rodríguez Pabón

## Estado actual (25/07/2026)

Esqueleto armado, equipo y redes ya cargados. Falta completar:
- Datos de contacto y ubicación del consultorio (`data/perfil_consultorio.json`)
- Confirmar sobre qué canal opera el agente de respuesta automática
- Cuentas de competencia a monitorear (`competencia/perfiles/cuentas_monitoreadas.json`)
- Primer snapshot de métricas de Instagram, TikTok y YouTube

## Cómo pedirle cosas a Jarvis sobre el consultorio

```
"Cargá los datos del equipo del consultorio"
"Agregá esta cuenta a la competencia: @fulano.cirugia"
"Planificá el contenido de la semana que viene"
"Analizá este reel: [link de Instagram]"
"Compará mi Instagram contra [competencia]"
"¿Cómo venimos en redes este mes?"
"Reporte semanal de redes y publicidad"
```

Sobre analizar contenido puntual (reels, tiktoks, posts de competencia): Jarvis puede abrir el link y analizar el copy, formato, tono y engagement visible, pero **no puede scrapear métricas privadas de Instagram/TikTok/YouTube sin conectar sus APIs**. Para métricas propias precisas (alcance, impresiones, retención), en algún momento conviene conectar:
- Meta Graph API (Instagram Business) — reusa credenciales de `../marketing/.env` si ya están cargadas
- TikTok Business API
- YouTube Data API

Hasta entonces, los snapshots de métricas se cargan a mano en `redes/*/metricas/metricas_historicas.json` (una vez por semana alcanza para ver tendencia).

---

## Reporte diario de mensajes, comentarios y contenido

Cuando Diego pida "armá el reporte de hoy" (o similar), el flujo es:

1. **Mensajes por canal** — Filtrar en ManyChat (`app.manychat.com` → Contactos → Filtro → [Instagram/TikTok/WhatsApp] → Última interacción → after [hoy 00:00]) y anotar el total de cada uno.
2. **Facebook Messenger** — No pasa por ManyChat. Pedirle a Diego que revise la bandeja de Meta Business Suite (página "Clínica Estética Darpa", mismo Instagram @drdiegorop.cirugiaplastica) y confirme cuántos mensajes nuevos hay.
3. **Comentarios** — Ídem, contador "Comentarios" en el panel de Meta Business Suite (pedirle a Diego captura o el número).
4. **Anuncios/leads de Meta** — Ver sección de Publicidad más abajo.
5. **Contenido del día** — Revisar posteos/reels/tiktoks recientes (propios y de la competencia prioritaria) para detectar qué está funcionando y sugerir ideas. Requiere navegación manual o capturas de Diego si la cuenta de Instagram está con restricciones activas (ver nota de seguridad abajo).
6. Guardar todo en `reportes/mensajes_YYYY-MM-DD.md` con el mismo formato que `reportes/mensajes_2026-07-27.md`.

**Nota de seguridad:** evitar navegar de forma automatizada (browser tool) por Instagram, Facebook o WhatsApp Business logueados con la cuenta real de Diego — Meta puede interpretarlo como actividad sospechosa y activar checkpoints de verificación de identidad (ya pasó una vez, el 27/07/2026). Para esas plataformas, preferir que Diego navegue manualmente y comparta capturas. TikTok no tiene este riesgo.

**API de mensajería:** `MANYCHAT_API_KEY` está en `.env`, pero la API pública de ManyChat no expone historial de conversaciones (limitación confirmada de la plataforma) — el filtro de "Última interacción" en la interfaz web es, por ahora, la única forma de contar mensajes nuevos por canal.
