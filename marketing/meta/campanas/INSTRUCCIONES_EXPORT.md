# Cómo exportar datos de Meta Ads para Jarvis

## Paso a paso

1. Entrá al **Administrador de Anuncios** de Meta Business
2. Hacé clic en **"Informes"** (columna izquierda) o usá el botón de exportar en la vista de campañas
3. Configurá el informe:
   - **Rango de fechas**: el período que querés analizar
   - **Nivel**: Campaña / Conjunto de anuncios / Anuncios (podés exportar los tres por separado)
   - **Columnas recomendadas** (ver abajo)
4. Exportá como **CSV**
5. Guardá el archivo en esta carpeta: `marketing/meta/exports/`
6. Renombrá el archivo como: `meta_campanas_YYYYMM.csv` (ej: `meta_campanas_202605.csv`)
7. Decile a Jarvis: *"Analizá el export de Meta del mes pasado"*

---

## Columnas recomendadas para el export

Seleccioná estas columnas en el Administrador de Anuncios antes de exportar:

**Básicas:**
- Nombre de la campaña
- Estado
- Presupuesto
- Importe gastado
- Resultados
- Costo por resultado
- Alcance
- Impresiones
- Frecuencia

**Rendimiento:**
- Clics (todos)
- CTR (todos)
- CPC (todos)
- CPM (costo por 1.000 impresiones)
- Compras (si tenés pixel instalado)
- ROAS de compra (si tenés pixel)
- Valor de conversión de compras

**Público:**
- Inicio de sesión en la cuenta publicitaria
- Fecha de inicio
- Fecha de finalización

---

## Niveles de análisis

Exportá los tres niveles para un análisis completo:

| Nivel | Archivo | Para qué sirve |
|---|---|---|
| Campaña | `meta_campanas_YYYYMM.csv` | Ver performance por objetivo |
| Conjunto de anuncios | `meta_conjuntos_YYYYMM.csv` | Ver qué audiencia funciona mejor |
| Anuncio | `meta_anuncios_YYYYMM.csv` | Ver qué creatividad gana |
