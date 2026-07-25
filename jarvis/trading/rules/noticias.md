# ⛔ Reglas de Noticias Económicas

> BASE PDF: Plan Operativo XAU.pdf — sección "Noticias"
> Fuente de horarios: https://www.forexfactory.com/ (solo USD)

---

## Reglas del PDF (inamovibles)

### Noticias de ALTO impacto (carpeta roja)
- Ventana de NO operación: **-10 min antes hasta +3 min después**
- No abrir NI cerrar operaciones en esa ventana

### Noticias de MEDIANO impacto (carpeta naranja)
- Ventana de NO apertura: **-3 min antes hasta +3 min después**
- Si hay operación abierta → se puede mantener
- Se puede entrar DESPUÉS de la noticia si el precio confirma

### Días completamente NO operables (PDF explícito)
| Noticia | Moneda | Frecuencia |
|---------|--------|------------|
| Federal Funds Rate & Statement | USD | ~8 veces/año |
| **NFP (Non-Farm Payrolls)** | USD | Primer viernes de cada mes |
| CPI y/y | USD | Mensual |
| FOMC Meeting Minutes | USD | ~8 veces/año |
| Advance GDP q/q | USD | Trimestral |
| Bank Holidays USD | USD | Variable |

> Para estos 5 eventos: NO mantener orden abierta durante la publicación.

---

## ⚡ Aprendizajes de sesiones reales

### Aprendizaje #1 — 05/06/2026 (NFP day)
**Situación:** NFP 172k vs 88k esperado (muy fuerte). Código tomó 2 BUY en sesión 09:01-10:59. Ambos hit SL. -2R.
**Lección:** El NFP se publica a las 8:30 AM ET (antes de la sesión). La sesión 9:01 empieza técnicamente fuera de la ventana (-10/+3). PERO el mercado queda dominado por el impulso del news todo el día. La estructura M3 que detecta el código en la primera hora es FALSA (producto del rebote post-news, no de tendencia real).
**Fix aplicado:** Toggle `⛔ Día de noticia roja` en el código → bloquea toda la sesión ese día.
**Regla nueva:** En días de NFP/FOMC/CPI/GDP → activar el toggle. No operar aunque técnicamente la ventana ya pasó.

---

## 📋 Checklist pre-sesión (cada día)

Antes de las 09:00 AM NY, verificar en Forex Factory:

- [ ] ¿Hay noticias rojas USD hoy? → Si sí → ¿cuál?
  - NFP / FOMC / CPI / GDP / Fed Rate → **NO operar en todo el día**
  - Otra roja (ej: ISM, Retail Sales) → activar ventana -10/+3
- [ ] ¿Hay noticias naranjas USD entre 09:00 y 11:00? → Activar ventana -3/+3
- [ ] ¿Es feriado bancario USD? → NO operar
- [ ] ¿Hay speakers de mediano impacto con hora exacta? → Tratar como alto impacto

---

## Implementación en código (XAU v9)

```pine
// Toggle manual en TradingView Settings
no_news = input.bool(false, "⛔ Día de noticia roja (NFP/FOMC/CPI/GDP)")

// Ventana configurable (default: NFP a las 8:30 → ventana 8:20-8:33)
news_time   = input.session("0820-0833", "Ventana de noticia (NY time)")
in_news_win = not na(time("1", news_time, "America/New_York"))

news_block  = no_news or in_news_win
can_trade   = ... and not news_block
```
