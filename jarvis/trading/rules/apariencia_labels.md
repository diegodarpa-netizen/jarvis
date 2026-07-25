# 🎨 Apariencia de Labels — Estructura Visual del Código

> Esta estructura visual fue aprobada por Diego. MANTENER SIEMPRE.
> Base: Plan Apariencia PDF + sesiones reales.

---

## ✅ Formato aprobado de labels de operación

### Label de entrada (triángulo + tipo de patrón)
```
▲ MEC-A   → BUY  (label_up,   verde,  debajo de la vela)
▼ MEC-A   → SELL (label_down, rojo,   encima de la vela)
▲ START   → BUY  (mismo formato)
▼ MEC-B   → SELL (mismo formato)
▼ MER     → SELL (mismo formato)
```

### Label de detalle (tooltip gris al costado)
```
Estructura m3:    Alcista / Bajista
Posicionamiento:  Compra / Venta
Ejecucion:        MEC Patron / MEC START / MEC-B QPC / MER
Resultado:        --- (en entrada) → SL / TP (al cerrar)
Fecha:            DD/MM/YYYY
T. entrada:       HH:MM
T. salida:        --- (en entrada) → HH:MM (al cerrar)
```

### Colores
| Elemento | Color | Opacidad |
|---|---|---|
| Label BUY (triángulo) | Verde `color.green` | 10% |
| Label SELL (triángulo) | Rojo `color.red` | 10% |
| Label detalle | Gris `color.gray` | 30% |
| Texto todos | Blanco `color.white` | — |
| Círculo BUY bloqueado | Verde | 50% |
| Círculo SELL bloqueado | Rojo | 50% |

### Líneas M3
| Elemento | Color | Estilo |
|---|---|---|
| M3 Alto (pivot) | Rojo `color.red` 15% | Punteado, width=2 |
| M3 Bajo (pivot) | Teal `color.teal` 15% | Punteado, width=2 |
| ChOC ALCISTA | Lima `color.lime` 5% | Sólido, width=3 |
| ChOC BAJISTA | Rojo `color.red` 5% | Sólido, width=3 |

### Fondo de sesión
| Condición | Color |
|---|---|
| Sesión activa | Azul claro (opacity 92%) |
| Tendencia ALCISTA | Verde claro (opacity 88%) |
| Tendencia BAJISTA | Rojo claro (opacity 88%) |
| Bloqueo noticia | Naranja (opacity 75%) |

---

## 📋 Regla permanente

- El formato de los labels (Estructura / Posicionamiento / Ejecución / Resultado / Fecha / T. entrada / T. salida) **NO se cambia sin aprobación de Diego**
- Los triángulos ▲▼ deben aparecer en la **vela exacta de entrada**
- Los círculos muestran señales válidas que fueron **bloqueadas por límites**
- El resultado del label se actualiza automáticamente al cerrar la operación (--- → SL/TP)
- Máximo 4 líneas M3 por tipo (alto / bajo) para no saturar el chart

---

## 🗓️ Aprobado

- Fecha aprobación: 07/06/2026
- Screenshot referencia: Imagen 6 (Jun 4 sesión, 21:18 UTC-4)
- Comentario Diego: "me encanto como lo pusiste, con esa info y demas, mantenlo asi"
