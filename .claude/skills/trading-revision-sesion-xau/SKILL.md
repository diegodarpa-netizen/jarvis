---
name: trading-revision-sesion-xau
description: Analiza screenshots de trading XAU/USD (o BTC) comparando la señal del código contra la decisión del trader humano, y revisa/ajusta la estrategia. Usar cuando Diego mande una captura de una sesión de trading, o pida revisar/tocar el código de la estrategia.
---

# Revisión de sesión de trading XAU/USD

Equipo: Trading/Finanzas.

**Antes de tocar código de estrategia:** consultar los PDFs base en `/Users/diegorodriguez/Downloads/scalping/` — son la fuente de verdad, todo lo demás es adicional.

**Reglas aprendidas** (no reemplazan los PDFs, las complementan) en `jarvis/trading/rules/` — leer `README.md` de esa carpeta primero, después `noticias.md`, `estructura_m3.md`, `errores_frecuentes.md` y `apariencia_labels.md` (estructura visual aprobada — no modificar sin aprobación explícita de Diego).

**Cada vez que Diego mande una imagen:**
1. Analizarla de inmediato, sin esperar a que lo pida.
2. Guardar el análisis en `jarvis/trading/memory/trading_analysis.md`.
3. Hacer comparativa lado izquierdo (código) vs. lado derecho (trader humano), con foco en la **decisión** de entrada (▲▼), no solo en los niveles marcados.
4. Identificar TODAS las oportunidades que tomó el trader humano en la imagen, no solo la primera.

**Después de cualquier `Write`/`Edit` a un `.pine`:** copiarlo al portapapeles automáticamente — `cat archivo.pine | pbcopy`.

Estado de las estrategias y versión actual: `jarvis/trading/memory/strategy_notes.md`. Para BTC scalping, la misma lógica aplica en `jarvis/btc_scalping/` (memory/rules propios).
