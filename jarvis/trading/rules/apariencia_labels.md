# 🎨 Apariencia de Labels — Estructura Visual del Código

> Esta estructura visual fue aprobada por Diego. MANTENER SIEMPRE.
> Versión vigente: 31/08/2026 (reemplaza la de 07/06/2026 — ver historial
> al final). Base: Plan Apariencia PDF + sesiones reales + referencia de
> una captura de una versión anterior del script que a Diego le gustaba.

---

## ✅ Formato aprobado — versión vigente (31/08/2026)

### Cambio de Estructura (ChoC) — marca SOLO esa vela
- Franja de fondo angosta (`bgcolor`) únicamente en la vela donde ocurre
  el ChoC — verde si es alcista, roja si es bajista. **No** hay franja de
  fondo continua durante toda la tendencia (se sacó a pedido de Diego,
  reemplazada por esto).
- Cartel de texto "CAMBIO DE ESTRUCTURA ALCISTA" / "... BAJISTA" pegado a
  esa misma vela (`label.style_label_up`/`_down`, fondo verde/rojo 15%,
  texto blanco, `size.small`).

### Label de entrada (tag gris + modelo)
- Tag chico gris "BUY"/"SELL" (no verde/rojo), más lejos de la vela.
- Debajo (más cerca de la vela), el nombre del modelo que disparó la
  entrada, en texto blanco sin caja: `"MER BUY"`, `"MER SELL"`, `"MEC ENV
  BUY"`, `"MEC ENV SELL"`, `"MEC START BUY"`, `"MEC START SELL"` (MER
  nunca lleva patrón porque solo usa Envolvente, por regla del PDF).
- Sin triángulos ▲▼, sin tooltip de detalle al costado, sin cartel de
  precio — se sacaron en el rediseño del 30/08/2026 y siguen sin usarse.

### Colores
| Elemento | Color | Opacidad |
|---|---|---|
| Tag BUY/SELL | Gris `color.gray` | 10% |
| Texto del modelo | Blanco `color.white`, sin caja | — |
| Cartel ChoC alcista | Verde `color.green` | 15% |
| Cartel ChoC bajista | Rojo `color.red` | 15% |
| Franja ChoC (1 vela) alcista | Verde `color.green` | 55% |
| Franja ChoC (1 vela) bajista | Rojo `color.red` | 55% |

### Líneas M3
| Elemento | Color | Estilo |
|---|---|---|
| M3 Alto (pivot) | Rojo `color.red` 25% | Punteado, rayita corta (12 barras) |
| M3 Bajo (pivot) | Verde `color.green` 25% | Punteado, rayita corta (12 barras) |
| ChOC ALCISTA (línea que cambia a sólida) | Lima `color.lime` 5% | Sólido, width=2 |
| ChOC BAJISTA (línea que cambia a sólida) | Rojo `color.red` 5% | Sólido, width=2 |

### Fondo de sesión
| Condición | Color |
|---|---|
| Sesión activa | Azul claro (opacity 95%) |
| Vela del Cambio de Estructura | Ver tabla de arriba (solo 1 vela, no toda la tendencia) |

### Líneas de operación activa
- Entrada (blanco), SL (rojo punteado), TP (verde punteado) — se estiran
  mientras la posición sigue abierta, se borran y redibujan en la
  siguiente entrada.

---

## 📋 Regla permanente

- Este formato **NO se cambia sin aprobación de Diego**.
- El cartel de Cambio de Estructura y el tag de entrada aparecen en la
  **vela exacta** del evento (ChoC o entrada), nunca desplazados.
- Máximo 500 labels/lines en total (`max_labels_count`/`max_lines_count`
  de la estrategia) — las rayitas de nivel M3 más viejas se van
  descartando solas al llegar al límite.

---

## 🗓️ Historial de aprobaciones

- **31/08/2026** (vigente): se sacó la franja de fondo continua por
  tendencia, se agregó el cartel de 1 vela para el ChoC, y el tag de
  entrada volvió a gris + texto de modelo debajo ("MER SELL", "MEC ENV
  SELL", etc.), en vez del tag verde/rojo simple sin modelo del
  30/08/2026. Diego mandó una captura de una versión anterior del script
  como referencia: "mira para el cambio de estructura solo marcabas la
  vela, me gusta... mira como marcabas las entradas, si era por MER SELL
  por ejemplo, asi me gustaba la estetica" — confirmado con mockup antes
  de tocar el código real.
- 30/08/2026 (superada): triángulos y tooltip de detalle reemplazados por
  líneas de entrada/SL/TP + tag simple BUY/SELL (verde/rojo, sin nombre
  de modelo) + rayitas cortas de nivel M3 (en vez de líneas que se
  estiraban todo el gráfico).
- 07/06/2026 (superada): formato original con triángulos ▲▼ + tooltip de
  detalle al costado. Screenshot referencia: Imagen 6 (Jun 4 sesión,
  21:18 UTC-4). Comentario Diego en su momento: "me encanto como lo
  pusiste, con esa info y demas, mantenlo asi" — reemplazado más
  adelante, no usar como referencia actual.
