# Escenarios de riesgo — Estrategia de Fabian (referencia permanente)

**Última actualización: 27/08/2026. Leer esto ANTES de repetir cualquiera de estos análisis
en una sesión futura — ya está todo hecho y validado, no rehacer desde cero.**

Base de datos: `fabian_consolidado_limpio.csv` — 191 operaciones reales, 27/10/2025 → hoy.
Todos los escenarios de esta página parten de ese archivo, interés compuesto salvo que
se indique lo contrario.

---

## Regla de trabajo para este tema (importante)

Diego pidió explícitamente (27/08/2026) que en este tema **no se filtre por tolerancia
psicológica/comodidad emocional** — es frío y agresivo en la toma de decisiones. Mostrar
los números crudos de todos los niveles de riesgo (pasivo a agresivo) sin suavizar la
recomendación. Ver `feedback_fabian_frio_agresivo.md` en la memoria de usuario.

---

## 1. Qué significa "arriesgar X%" (concepto)

Fijás de antemano cuánto dinero real perdés si la operación toca el stop loss —
ajustás el tamaño de la posición para que una pérdida total (-1R) sea exactamente
X% del capital *en ese momento*. Como es interés compuesto, el monto en dólares de
ese 1R cambia operación a operación (crece si vas ganando, se achica si vas perdiendo).

## 2. Barrido completo 1%-10% (USD 10.000 iniciales)

| Riesgo | Capital final | Retorno | Drawdown máx. |
|---|---|---|---|
| 1% | $20.540 | +105,4% | -4,0% |
| 2% | $41.485 | +314,8% | -7,9% |
| 3% | $82.393 | +723,9% | -11,7% |
| 4% | $160.946 | +1.509,5% | -15,5% |
| 5% | $309.249 | +2.992,5% | -19,2% |
| 6% | $584.550 | +5.745,5% | -22,8% |
| 7% | $1.087.087 | +10.770,9% | -26,3% |
| 8% | $1.989.192 | +19.791,9% | -29,7% |
| 9% | $3.581.749 | +35.717,5% | -33,1% |
| 10% | $6.346.756 | +63.367,6% | -36,3% |

**Advertencia ya documentada**: de 5%-10% para arriba, el compuesto explota
matemáticamente pero es una fantasía práctica — la peor racha real observada fue
de 3 pérdidas seguidas (191 operaciones, no es garantía de que sea el peor caso
futuro), la ejecución real se degrada a esa escala de posición, y el drawdown en
dólares sobre una cuenta ya grande es brutal. Script: `barrido_riesgo_1_a_10.py`.
Gráfico: `graficos/barrido_riesgo_1_a_10.png`.

## 3. Franja razonable 1%-3% (la que se usa de base para todo lo demás)

| Riesgo | Capital final | Retorno | Drawdown máx. % | Peor caída en USD (puede ser otro momento distinto al peor %) |
|---|---|---|---|---|
| 1,0% | $20.540 | +105,4% | -4,0% | -$594 |
| 1,5% | $29.252 | +192,5% | -5,9% | -$1.272 |
| 2,0% | $41.485 | +314,8% | -7,9% | -$2.410 |
| 2,5% | $58.586 | +485,9% | -9,8% | -$4.265 |
| 3,0% | $82.393 | +723,9% | -11,7% | -$7.216 |

**Ojo con esto** (hallazgo real, no intuitivo): la peor caída en % y la peor caída
en USD **no siempre son el mismo momento**. La peor caída porcentual fue el
10/03/2026 (-11,7% al 3%, de $25.730 a $22.717 en 10 operaciones). La peor caída
en DÓLARES fue mucho después, el 26/08/2026 (-$7.216, "solo" -8,4% pero sobre una
cuenta ya más grande de $85.966). Cuanto más crece la cuenta, una caída % más chica
puede pesar más en plata real que una caída % más grande al principio.

Calmar (retorno÷drawdown) dentro de esta franja: **mejora con el riesgo** (26,4 a
1% hasta 61,9 a 3%) — matemáticamente 3% es "mejor" por esta métrica sola, pero eso
no filtra por lo que Diego realmente puede sostener operando (ver regla de arriba:
no se filtra, se muestran los números crudos y decide él).

Scripts: `franja_1_3_y_rachas.py` (parte 1), `ganancia_vs_perdida_1_3.py` (gráfico
de ganancia arriba / pérdida en USD abajo, mismo eje temporal — el más completo
visualmente). Gráficos: `graficos/franja_1_3.png`, `graficos/ganancia_vs_perdida_1_3.png`.

## 4. Proyección a 1 año completo (365 días), mismo ritmo observado

Los 191 trades cubren 304 días de calendario (≈10 meses). Se anualizó el retorno
compuesto real (técnica estándar, NO se inventaron operaciones) para proyectar
los ~61 días que faltan para completar 1 año, al mismo ritmo demostrado.

| Riesgo | Real hoy (304d) | Proyectado a 365d | Retorno anualizado |
|---|---|---|---|
| 1,0% | $20.540 | $23.732 | +137,3% |
| 1,5% | $29.252 | $36.283 | +262,8% |
| 2,0% | $41.485 | $55.191 | +451,9% |
| 2,5% | $58.586 | $83.533 | +735,3% |
| 3,0% | $82.393 | $125.797 | +1.158,0% |

La brecha entre el escenario pasivo y el agresivo CRECE con el tiempo (4x a los 10
meses → 5,3x proyectado a 1 año) — efecto compuesto sobre más tiempo, no achica la
diferencia. Script: `panorama_1_anio.py`. Gráfico: `graficos/panorama_1_anio.png`.

## 5. Análisis de rachas (¿hay momentum entre operaciones?)

Después de N resultados IGUALES seguidos (sin importar signo), ¿cambia el win rate
de la operación siguiente respecto al promedio general (65,45%)?

| Racha previa | n | Win rate del siguiente | ¿Distinto del promedio? |
|---|---|---|---|
| 1 | 73 | 72,6% | No |
| 2 | 41 | 56,2% | No |
| 3 | 21 | 61,6% | No |
| 4 | 12 | 50,2% | No (muestra chica) |

**Conclusión: no hay racha caliente ni fría — cada operación es estadísticamente
independiente.** No se puede predecir la próxima por lo que vino antes. Script:
`franja_1_3_y_rachas.py` (parte 2). Resultado: `analisis_rachas.csv`.

## 6. Otros hallazgos de esta línea de trabajo (de sesiones previas, ya documentados)

- Bootstrap del resultado global: IC 95% [0,25R, 0,50R] — **significativo**, primera
  vez en todo el proyecto que una hipótesis pasa este filtro (ver `analisis_profundo.py`).
- Primeros 30 min de sesión (09:01-09:30): 72,9% WR vs 59-60% el resto — la ventana
  de apertura rinde casi el doble.
- Hedge Position: días con hedge rinden peor en promedio por día (+0,119R vs
  +0,537R), PERO sacar el hedge del cálculo total empeora el resultado acumulado
  (+84,1% vs +105,4% a 1%) — quitarlo elimina recuperaciones junto con las pérdidas
  que compensaba. No es una conclusión simple.
- Nunca hubo un mes completo en rojo en los 11 meses de historial (oct-25 a ago-26).
- Últimos 2 meses (jul-ago 2026) son los más flojos del historial (50% y 57% WR,
  contra 65-82% en meses previos) — vigilar, muestra todavía chica para alarmarse.

## 7. Pendiente

- Descarga puntual del gap de datos (27/10/2025-12/02/2026) en curso en background
  (`data/download_gap_fabian.py`) — cuando termine, se puede repetir el backtest
  mecánico (Python, no el Pine Script) sobre el período EXACTO de Fabian, no sobre
  2022 como se hizo de prueba.
- % de riesgo real que usa Fabian: todavía no confirmado — todo lo de esta página
  usa 1%-10% como supuesto exploratorio, no el dato real de él.
