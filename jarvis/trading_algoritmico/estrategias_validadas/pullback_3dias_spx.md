# Pullback 3 días — S&P 500 (primera estrategia validada del proyecto)

**Estado: VALIDADA en diario y semanal, 26 años, múltiples regímenes. NO significativa en oro (probado 25/08/2026, bootstrap cruza cero). Pendiente: costos de operación, intradía.**
**Fecha de validación inicial: 25/08/2026**
**Clasificación confirmada por Diego (25/08/2026): SWING TRADING (~4-9 días por operación). Alcance de estilo del proyecto confirmado como swing trading — day trading/scalping quedan fuera de prioridad por ahora.**

## Origen y atribución — corregido

Diego la trajo como "estrategia de Ivan Scherman, ganador del World Cup Championship
of Futures Trading 2023 (+491,4%)". Se verificó:

- El resultado de Scherman **es real**: argentino, CIO de SciTech Investments, convirtió
  US$241.360 en US$1.428.728 en 10,85 meses (drawdown 26,2%), primer latinoamericano en
  ganar el campeonato. Confirmado por World Cup Trading Championships, CMT Association,
  Forbes Australia.
- Su resultado real vino de un **fondo diversificado y apalancado** operando varios
  activos no correlacionados (E-mini S&P 500, gas natural, soja, oro, jugo de naranja).
- **La regla exacta que se probó acá NO está documentada como suya.** Coincide,
  prácticamente calcada, con la **"3-Day Pullback" de Larry Connors** (de su libro
  *Short-Term Trading Strategies That Work*), un autor y sistema completamente distintos,
  bastante anteriores. Probablemente hubo una mezcla de fuentes en el camino hasta Diego.
- Conclusión: la regla se prueba **por mérito propio**, no como reproducción de la
  hazaña de Scherman — esa cifra no es alcanzable con esta única regla, sin apalancamiento,
  en un solo instrumento.

## Regla

- **Activo probado**: S&P 500 índice (^GSPC, Yahoo Finance) — no oro, para no desvirtuar
  el test de un activo pensado para acciones/índices.
- **Filtro de tendencia**: cierre diario > SMA200
- **Señal de entrada**: 3 cierres diarios consecutivos, cada uno menor al anterior,
  mientras el filtro de tendencia sigue activo (pullback dentro de una tendencia alcista)
- **Entrada**: compra al cierre del día que completa el 3er cierre a la baja
- **Salida**: al cierre del primer día en que el precio supera la SMA5
- Solo largos, sin piramidar (no se abre una 2da posición si ya hay una abierta)

## Resultado (diario, 2000-2026, sin costos de operación)

| Métrica | Valor |
|---|---|
| Operaciones totales | 194 |
| Win rate | 77,3% (150G / 44P) |
| Resultado promedio por operación | +0,458% |
| Promedio ganadoras / perdedoras | +0,95% / -1,22% |
| Días promedio en posición | 4,4 |
| Bootstrap 95% CI del promedio (5000 iter.) | **[0,255%, 0,635%] — significativo, no cruza cero** |
| Retorno compuesto de la estrategia | +138,2% |
| Retorno compuesto buy&hold mismo período | +427,0% |
| Drawdown máximo estimado (solo entre cierres de operación, subestima el real) | ~-10,1% |

**Por régimen** (todas positivas, sin excepción):
- 2000-2007: 82,5% acierto, +22,3%
- 2008-2009 (crisis financiera): **100% acierto, +8,8%**, mientras buy&hold perdía -22,9%
- 2010-2019 (bull market largo): 72,2%, +20,5%
- 2020 (COVID): 57,1% (la más floja — recuperación demasiado violenta para un pullback de 3 días)
- 2021-2026: 82,4%, +37,1%

## Por qué pierde en $ totales contra buy&hold (y por qué no es un problema)

Está fuera del mercado ~87% del tiempo (solo entra en pullbacks puntuales dentro de
tendencias). En un mercado que sube casi sin parar (2010-2024), eso le cuesta retorno
bruto. Su fortaleza no es maximizar retorno, es **baja exposición + buen comportamiento
en crisis** (drawdown muy inferior al de buy&hold, que cayó >50% en 2008-2009).

## Costos de operación — CERRADO (26/08/2026)

Probado de 0 a 10 puntos base (0,10%) de costo por operación (entrada+salida) —
supuesto generoso para ES/SPY, de los instrumentos más líquidos y baratos del
mundo. Sobrevive cómodo en todos los escenarios: incluso con 0,10% de costo,
sigue siendo estadísticamente significativo (bootstrap 95% CI [0,16%, 0,54%],
WR 75,8%). No es un problema de este edge.

## Limitaciones pendientes de cerrar

1. ~~Sin comisión ni slippage~~ — cerrado, ver arriba.
2. Entrada al mismo cierre que confirma la señal (no al día/apertura siguiente) — testear
   la versión más realista de entrar al open del día siguiente.
3. No probada en semanal/mensual/intradía todavía (ver bitácora para el estado de esto).
4. No probada en otro instrumento (oro, Nasdaq, Dow, acciones individuales) para ver si
   el edge es específico de SPX o generalizable.
5. Drawdown reportado es una subestimación (solo mide entre cierres de operaciones, no
   el equity marcado a mercado día a día mientras una posición está abierta).

## Archivos

- Backtest: `jarvis/trading_algoritmico/estrategia_pullback_3dias_spx.py`
- Resultados operación por operación: `jarvis/trading_algoritmico/resultados_pullback_3dias_spx.csv`
- Gráficos: `jarvis/trading_algoritmico/graficos/pullback_3dias_equity_spx.png`,
  `jarvis/trading_algoritmico/graficos/pullback_3dias_zoom_2023.png`
