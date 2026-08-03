# Módulo de Publicidad y Marketing — Jarvis

## ¿Qué hace este módulo?

Centraliza el análisis de todas las campañas publicitarias, con foco en **Meta Business (Facebook + Instagram Ads)**.

El objetivo es tener visibilidad completa del rendimiento de cada peso invertido y maximizar el ROAS con análisis sistemático.

---

## Estructura

```
marketing/
├── meta/
│   ├── campanas/         ← CSVs exportados del Administrador de Anuncios
│   ├── audiencias/       ← Segmentaciones guardadas y análisis de público
│   ├── creatividades/    ← Registro de copies, imágenes y videos usados
│   ├── reportes/         ← Reportes HTML generados por Jarvis
│   └── exports/          ← Exports crudos de Meta sin procesar
├── analisis/
│   ├── metricas/         ← KPIs calculados y tracking histórico
│   ├── comparativas/     ← A/B tests y comparaciones entre campañas
│   └── embudos/          ← Análisis de conversión por etapa
├── scripts/              ← Scripts Python para procesar datos de Meta
├── recursos/
│   ├── plantillas/       ← Templates de análisis y reportes
│   └── benchmarks/       ← Referencias de industria para comparar
└── README.md             ← Este archivo
```

---

## Flujo de trabajo

### 1. Exportar datos de Meta
1. Ir al Administrador de Anuncios → Informes
2. Seleccionar el rango de fechas y el nivel (campaña / conjunto / anuncio)
3. Exportar como CSV → guardar en `meta/exports/`
4. Pedirle a Jarvis: *"Analizá el export de Meta en meta/exports/"*

### 2. Análisis automático
Jarvis procesa el CSV y genera:
- Ranking de campañas por ROAS
- CPM, CPC, CTR, CPA por campaña
- Detección de campañas con bajo rendimiento
- Sugerencias de optimización

### 3. Seguimiento
- Los reportes se guardan en `meta/reportes/` con fecha
- Las métricas acumuladas quedan en `analisis/metricas/`

---

## Métricas clave que analiza Jarvis

| Métrica | Qué mide | Objetivo |
|---|---|---|
| **ROAS** | Retorno sobre inversión publicitaria | > 3x |
| **CPM** | Costo por 1.000 impresiones | Benchmarks por industria |
| **CPC** | Costo por click | Lo más bajo posible |
| **CTR** | Click-through rate | > 1% (awareness), > 2% (retargeting) |
| **CPA** | Costo por adquisición/conversión | Depende del ticket |
| **Frecuencia** | Veces que vio el anuncio el mismo usuario | < 3 (evitar fatiga) |
| **Alcance** | Personas únicas impactadas | — |
| **Conversiones** | Acciones completadas | — |

---

## Cómo pedirle análisis a Jarvis

```
"Analizá mis campañas de Meta del último mes"
"¿Cuál es mi campaña con mejor ROAS?"
"Comparame el rendimiento de Mayo vs Abril en Meta"
"¿Qué audiencias están funcionando mejor?"
"Detectá campañas que debería pausar"
"Generá un reporte de performance de Meta"
```
