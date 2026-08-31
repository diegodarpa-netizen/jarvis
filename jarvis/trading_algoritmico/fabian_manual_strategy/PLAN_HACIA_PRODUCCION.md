# Plan hacia producción — EstrategiaXAU

A partir de la calibración cerrada al 30/08/2026 (180/191 exacto, 94,2%).
Objetivo: llegar a una decisión informada sobre operar con capital real,
sin asumir nada que no esté validado.

---

## Fase 0 — Cerrar lo que quedó abierto (esta semana)

1. **Caso 26/11/2025 (único sin explicar)**: análisis vela por vela más a
   fondo de las 2 operaciones BUY de ese día, ya con imágenes armadas —
   falta mandárselas a Fabian si no se resuelve solo con el PDF.
2. **2 fechas ambiguas (08/02 y 10/02/2026)**: preguntarle directo a
   Fabian cuál es la fecha real de esas 2 operaciones (el día de la
   semana anotado no coincide con el calendario).
3. Con esto, el dataset de 191 queda 100% revisado, sin cabos sueltos.

**Responsable**: yo. **Bloqueante**: necesito que le mandes las preguntas
a Fabian (no tengo forma de escribirle directo).

---

## Fase 1 — Actualizar el `.pine` real con todo lo aprendido

El `EstrategiaXAU.pine` de TradingView **todavía no tiene ninguna de las
correcciones de esta sesión** — todo el trabajo de calibración se hizo en
Python, en paralelo, sin tocarlo (como pediste en su momento). Ahora hay
que volcarlo:

- M3 continuo sin reset, doji excluido, patrón START fusionado a MEC,
  margen de ruptura medido con la mecha.
- Estética nueva: líneas de entrada/SL/TP (sin etiquetas de precio),
  franjas de fondo por tendencia, marca de dirección chica del color de
  la operación (el diseño que fuimos afinando juntos).

**Responsable**: yo. **Bloqueante**: ninguno, puedo arrancar apenas lo
confirmes.

---

## Fase 2 — Validar con datos reales de OANDA (el test más importante)

8 de los 11 casos que no coinciden hoy son diferencia de precio entre
Dukascopy (mi fuente) y OANDA (la de Fabian). Esto se prueba una sola vez:

- Correr el `.pine` actualizado directo en TradingView, sobre el gráfico
  real OANDA:XAUUSD (no Dukascopy), en el mismo período histórico
  (27/10/2025-27/08/2026).
- Comparar contra las mismas 191 operaciones reales.
- Si el % sube (es lo esperable, ya que se elimina la causa principal de
  error), ese es el número de fidelidad "real" del sistema — no el 94,2%
  medido con datos de un broker distinto al que usa Fabian.

**Responsable**: esto lo tenés que correr vos en TradingView (yo no tengo
acceso a la plataforma) — yo preparo el Pine Script listo para pegar y te
guío en la lectura de resultados si hace falta.

---

## Fase 3 — Forward testing (paper trading, tiempo real)

Antes de capital real, correr el sistema en vivo sin plata, comparando
cada señal contra lo que Fabian hace ese mismo día — mismo método vela
por vela que usamos con el histórico, pero hacia adelante.

**Preguntas que necesito que definas vos antes de armar esto** (no las
asumo):
- ¿Cuánto tiempo querés que dure el forward test antes de evaluar
  resultados (2 semanas, 1 mes, hasta N operaciones)?
- ¿Lo corremos con alertas de TradingView, o preferís que armemos algo
  que te avise a vos directo (WhatsApp, mail) cada vez que dispara?

---

## Fase 4 — Decisión de capital real

Con el forward test hecho, ahí se evalúa si tiene sentido operar en real
(probablemente arrancando en demo o con riesgo bajo). Esta decisión es
tuya — yo te doy los números, no la tomo por vos.

---

## En paralelo (no bloquea nada de arriba)

- **Franjas horarias** (Pre-NY 07:00-09:00, Asia 20:02-22:00 NY): ya
  confirmadas como reales en el Plan Operativo actualizado, exploración
  inicial hecha (40 días de muestra, nada significativo todavía) — se
  retoma cuando quieras.
- **Señales "extra"** que el código encuentra pero Fabian no toma: quedan
  catalogadas en cada día de la bitácora, para cuando pasemos a la fase
  de expansión del sistema que ya habías planteado.

---

## Orden sugerido

**Fase 0 y Fase 1 las puedo arrancar ya, en paralelo, sin que hagas nada.**
Fase 2 necesita que vos corras algo en TradingView. Fase 3 necesita 2
decisiones tuyas (duración, forma de aviso). Fase 4 es tu decisión final.

¿Arranco con la Fase 0 y la Fase 1 ahora?
