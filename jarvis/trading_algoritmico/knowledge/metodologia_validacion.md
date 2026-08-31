# Metodología de validación: walk-forward optimization

Investigación de agosto de 2026. Esta es la pieza más importante de toda la carpeta — el gap que ya se identificó como crítico en `ANALISIS_ESTRATEGICO_IA_FINANCIERA.md`.

## El problema que ya tenemos documentado

El backtest de XAU/USD mostró win rate de 70,0% (07/06/2026) → 58,8% (22/06/2026) → 38,5% (01/07/2026) en tres corridas consecutivas **sin cambios de código**. Eso no es una estrategia que se degrada — es la firma clásica de un backtest optimizado sobre una ventana corta que no generaliza fuera de esa ventana (overfitting).

El paper FINSABER (arXiv 2505.07078, ya citado en el informe estratégico) confirma el patrón a escala grande: sobre 20 años y 100+ símbolos, las ventajas reportadas por estrategias en papers de ventana corta se diluyen o desaparecen — son demasiado conservadoras en mercados alcistas y demasiado agresivas en bajistas. Más del 90% de estrategias académicas fallan al pasar a capital real.

## Qué es walk-forward optimization (WFO)

Es el método reconocido como "estándar de oro" de validación de estrategias (popularizado por Robert Pardo). En vez de optimizar parámetros sobre todo el histórico y probar una sola vez sobre una porción separada (lo que da falsa confianza si esa porción resultó "fácil"), WFO repite el ciclo optimización→validación en múltiples ventanas móviles:

1. Tomar una ventana de datos (ej. las últimas 1.000 velas) y optimizar los parámetros de la estrategia ahí (**in-sample**).
2. Probar esos parámetros, sin volver a tocarlos, sobre la ventana siguiente que el modelo nunca vio (ej. las próximas 200 velas) (**out-of-sample**).
3. Correr la ventana entera 200 velas hacia adelante y repetir el ciclo.
4. La estrategia solo se considera robusta si funciona de manera consistente a través de múltiples ventanas out-of-sample, no solo en una.

Esto obliga a la estrategia a probarse repetidamente contra condiciones de mercado distintas, en vez de depender de que la única ventana de test haya sido favorable por azar.

## Por qué esto resuelve el problema de Jarvis específicamente

El patrón 70%→38,5% habría aparecido en las métricas de WFO como inestabilidad entre ventanas — es decir, se hubiera detectado **antes** de confiar en el 70% inicial, no después de perder confianza en tres corridas reales. Implementar WFO real en `backtest.py` (Fase 1 del roadmap del informe estratégico) sigue siendo el paso crítico antes de agregar cualquier funcionalidad nueva.

## Implementación de referencia

Hay una implementación abierta en Python con optimización Bayesiana que puede servir de punto de partida: [walk-forward-backtester (GitHub)](https://github.com/TonyMa1/walk-forward-backtester).

Sources: [QuantInsti — Walk-Forward Optimization](https://blog.quantinsti.com/walk-forward-optimization-introduction/) · [Interactive Brokers Campus — Walk Forward Analysis](https://www.interactivebrokers.com/campus/ibkr-quant-news/the-future-of-backtesting-a-deep-dive-into-walk-forward-analysis/) · [Wikipedia — Walk forward optimization](https://en.wikipedia.org/wiki/Walk_forward_optimization) · [walk-forward-backtester (GitHub)](https://github.com/TonyMa1/walk-forward-backtester) · [Walk-Forward Analysis: comparación de tres enfoques (Medium)](https://medium.com/@NFS303/walk-forward-analysis-a-production-ready-comparison-of-three-validation-approaches-69cd25fc9fc7)
