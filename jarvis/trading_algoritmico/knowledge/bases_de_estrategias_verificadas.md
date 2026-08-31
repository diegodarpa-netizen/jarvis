# Bases de datos de estrategias algorítmicas con backtest real

Investigación de agosto de 2026, a pedido de Diego: dónde encontrar estrategias que "hayan funcionado de verdad", no solo teoría.

## QuantPedia — la referencia principal

**[QuantPedia](https://quantpedia.com/)**, "The Encyclopedia of Algorithmic and Quantitative Trading Strategies". Lo que hace: lee papers académicos, extrae la regla de trading en lenguaje simple, y le agrega estadísticas de riesgo/retorno reales.

- **~70 estrategias gratis**, **900+ en el plan Premium** (pago).
- Premium incluye **400+ backtests out-of-sample con curva de equity, estadísticas y código completo** — no solo la idea, la prueba.
- Se actualiza cada 2 semanas con estrategias nuevas.
- Parte de sus estrategias están implementadas directamente en QuantConnect (el motor que ya evaluamos y descartamos por el costo del plan de ejecución en vivo, pero acá solo se usaría para consultar, no para correr).

## Otras dos, complementarias

- **[Papers With Backtest](https://paperswithbacktest.com/strategies)** — mantenido por gente que corre backtests de oficio; combina estrategias descriptas por académicos e institucionales con resultados reales (Sharpe, etc.). Su lista curada de librerías (`awesome-systematic-trading`) ya la teníamos en `frameworks_backtesting.md`.
- **[QuantifiedStrategies.com](https://www.quantifiedstrategies.com/trading-strategies-free/)** — **200+ estrategias gratis, backtesteadas con los parámetros mostrados**. Ya la venimos usando como fuente todo el proyecto (Ed Seykota, Jim Simons, etc.) sin darnos cuenta de que también tiene esta base de estrategias.

## La advertencia que hay que sostener siempre, incluso con estas fuentes

La misma búsqueda trajo el dato que ya veníamos citando varias veces: **más del 90% de las estrategias académicas fracasan al pasar a capital real** — el problema no es que estas bases mientan, es que un backtest de otro (aunque sea riguroso) no reemplaza correr **nuestro propio walk-forward** sobre nuestros datos, con nuestros costos de transacción. Encontrar una estrategia acá es el punto de partida (la hipótesis con lógica económica del paso 1 de `proceso_prueba_estrategias.md`), no el resultado final — igual hay que pasarla por los 4 pasos ya documentados ahí.
