# Informe completo v2 — Estrategia manual de Fabian (XAU/USD scalping)

**Fecha: 27/08/2026 (reescrito, versión con gráficos + auditoría trade por trade contra velas reales)**
**Fuente: historial real de Fabian, 27/10/2025 → hoy. 191 operaciones, procesadas al 100%.**
**Base leída línea por línea: Plan Técnico XAU.pdf (31 páginas completas) + Plan Operativo XAU.pdf.**

---

## 0. Qué cambió respecto a la v1 de este informe

Diego pidió: gráficos (tortas, comparaciones), volver a revisar las estrategias, y **cruzar el 100% de las operaciones contra las velas reales**, no solo una muestra. Esto agrega:

1. Dashboard visual completo (9 gráficos en 1 imagen — ver `graficos/fabian_dashboard_completo.png`).
2. Auditoría trade por trade: para cada operación con patrón "Envolvente" declarado, se reconstruyó la vela real de entrada y se le aplicaron las **mismas fórmulas matemáticas exactas** que quedaron en `EstrategiaXAU.pine` (cuerpo ≥85% = clásica, 50-85% con mecha opuesta = martillo, ambas mechas 15-85% = doji), para ver si el código reconocería lo mismo que Fabian marcó a mano.
3. **Cobertura de datos**: teníamos M1 real desde 12/02/2026, pero Fabian arranca 27/10/2025 — un hueco de 68 operaciones sin vela real para verificar. En vez de conformarnos con el 64% de cobertura, se lanzó una descarga puntual de Dukascopy acotada exactamente a ese tramo (27/10/2025 → 12/02/2026) — corriendo en background, se actualiza este informe cuando termine.

---

## 1. Métricas generales — sin cambios respecto a v1 (esto ya usaba el 100% de los datos)

| Métrica | Valor |
|---|---|
| Operaciones totales | 191 |
| Ganadoras / Perdedoras / Breakeven | 125 / 59 / 7 |
| **Win rate** | **65,45%** |
| **Total R acumulado** | **+72,83R** |
| Racha ganadora / perdedora máxima | 11 / 3 |
| Drawdown máximo (en R) | -4,00R |
| Semanas que cumplieron el objetivo de 2R | 23 de 38 (60,5%) |

## 2. Comparación visual por categoría (ver dashboard)

| Categoría | n | Win rate |
|---|---|---|
| MEC | 104 | 66,3% |
| MER | 87 | 64,4% |
| **Envolvente** | 84 | **70,2%** |
| **START** | 19 | **47,4%** ⚠️ |
| Buy | 97 | 61,9% |
| Sell | 94 | 69,1% |

**Lectura reforzada con el gráfico de barras**: el patrón START está prácticamente en la línea de 50% (azar) — es visualmente el único que cruza por debajo de esa línea de referencia en el dashboard. Envolvente es, con claridad, el motor real del sistema.

**R por día de semana** (nuevo, gráfico de barras): miércoles es el día más fuerte en R acumulado, jueves el más flojo — pero ningún día es negativo, la estrategia no depende de un solo día bueno.

**R semanal** (gráfico de barras, código de color verde=cumplió objetivo/naranja=positivo pero bajo el objetivo/rojo=negativo): de 38 semanas, solo **4 cerraron en rojo**, y ninguna con una caída severa (la peor fue -2R). El patrón visual confirma lo que ya sabíamos: consistencia, no un resultado de pocas operaciones grandes.

## 3. Auditoría trade por trade contra velas reales — el hallazgo más importante de esta versión

Sobre las 123 operaciones dentro de nuestra ventana M1 (12/02/2026 en adelante), se reconstruyó la vela exacta de entrada y se aplicaron las fórmulas matemáticas del Plan Técnico (idénticas a las de `EstrategiaXAU.pine`).

**De las 51 operaciones con patrón "Envolvente" declarado por Fabian, el código reconoce el mismo patrón en 29 (56,9%).**

Esto **no** significa que Fabian se equivoque en 22 operaciones — significa una de estas cosas, y hay que investigarlo antes de confiar ciegamente en el código automático:

1. **La hora registrada no es exacta al minuto de la vela de entrada real** (el CSV trae "09:18", pero la vela real pudo haber sido 09:17 o 09:19 — usamos la más cercana). Varios casos "no coincide" tienen cuerpo 80-85%, es decir, están *al borde* del umbral — un desfasaje de 1 minuto podría explicar buena parte del 43,1% de discordancia.
2. **Fabian, como trader humano, puede estar aplicando más criterio visual/contextual** del que capturan los 3 umbrales rígidos (85%/50%/15%) — el plan tiene excepciones documentadas (ej. página 11: "si el cuerpo supera 50% por 0.01%, igual cuenta como indecisión").
3. Posibilidad real de que **el código necesite ajuste fino** en los umbrales antes de confiar en que replique el criterio humano.

**Casos concretos que hay que revisar a mano** (todos con cuerpo entre 65-85%, justo en el borde): 16/03, 20/03, 23/03, 25/03, 01/05, 06/05, 19/05, 20/05, 29/05, 02/06, 23/06, 24/06, 26/06, 30/06, 09/07, 21/07, 22/07, 23/07, 03/08, 11/08. Lista completa en `validacion_trade_por_trade.csv`.

**Esto es exactamente el tipo de brecha que ya sabíamos que existía** (el código viejo de `xau_strategy` mostraba inestabilidad de win rate 70%→38,5%) — ahora tenemos, por primera vez, el dato cuantitativo de **dónde** está la brecha: no es la lógica de MEC/MER/M3, es la **calibración fina del reconocimiento de vela**.

## 4. Plan concreto para cerrar la brecha (próximos pasos)

1. Esperar la descarga del tramo 27/10/2025-12/02/2026 (en curso) y correr la auditoría sobre el 100% de las 191 operaciones, no solo 123.
2. Revisar a mano (con capturas de TradingView) los ~20 casos "al borde" para ver si el desfasaje de 1 minuto explica la discordancia.
3. Si no la explica, recalibrar los umbrales de `EstrategiaXAU.pine` con los datos reales de Fabian como "ground truth" — es decir, ajustar el código para que aprenda de sus 84 operaciones Envolvente reales, en vez de solo copiar el número del PDF (85%) a ciegas.

## 5. Archivos de esta versión

- `dashboard_completo.py` / `graficos/fabian_dashboard_completo.png` — las 9 visualizaciones
- `validacion_trade_por_trade.py` / `validacion_trade_por_trade.csv` — auditoría contra velas reales
- `data/download_gap_fabian.py` — descarga del tramo faltante (en curso)
- Ver también `INFORME_COMPLETO_v1_respaldo` (contenido de la versión anterior, preservado más abajo en el historial de bitácora)
