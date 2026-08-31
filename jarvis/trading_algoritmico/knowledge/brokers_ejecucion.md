# Brokers para ejecución algorítmica

Investigación de agosto de 2026. **Esto es solo mapeo de opciones para el futuro — no se está conectando ni ejecutando nada real todavía.** Ejecutar operaciones o mover fondos sigue siendo una acción que Diego tiene que hacer él mismo, nunca un script automático sin supervisión directa.

## Opciones evaluadas

| Bróker | Cobertura | Fortaleza | Límite |
|---|---|---|---|
| [Alpaca](https://alpaca.markets/algotrading) | Acciones, opciones, cripto (EE.UU.) | API REST/WebSocket bien documentada, paper trading ilimitado gratis, sin mínimo de cuenta, mejor punto de entrada para desarrolladores Python | Sin forex, sin futuros, sin mercados internacionales |
| [Interactive Brokers](https://www.interactivebrokers.com/) (TWS API / IBKR API / FIX API) | 150+ mercados en 34 países, 150+ tipos de orden | El más completo para trading serio — cubre forex (relevante para XAU/USD), futuros, acciones internacionales; latencia de ejecución <50ms | Curva de aprendizaje más alta que Alpaca, API más compleja |

## Algoritmos de ejecución — cómo minimizar el costo de entrar/salir de una posición grande

Agregado 13/08/2026, verificado contra fuente primaria (no contra el resumen de segunda mano que compartió Diego, generado a partir de PDFs de origen no autorizado). Relevante para cuando el capital operado sea grande respecto a la liquidez del instrumento — con el tamaño actual de Jarvis todavía no es el cuello de botella, pero conviene tenerlo documentado.

- **TWAP (Time-Weighted Average Price)**: divide la orden en partes iguales a lo largo del tiempo, sin importar el volumen real del mercado en cada momento. Útil en arbitraje/pares para mantener neutralidad de dólares entre las dos patas de una posición.
- **VWAP (Volume-Weighted Average Price)**: ajusta el ritmo de ejecución según la distribución histórica de volumen intradía del instrumento — ejecuta más rápido cuando históricamente hay más liquidez. Es el benchmark más común contra el que se mide la calidad de ejecución institucional.
- **Modelo Almgren-Chriss** (Almgren & Chriss, *Optimal Execution of Portfolio Transactions*, Journal of Risk 3(2), 2000): formaliza la ejecución como un trade-off matemático entre dos riesgos opuestos — ejecutar rápido reduce el riesgo de que el precio se mueva en contra mientras se espera (riesgo de volatilidad), pero aumenta el costo por impacto de mercado (la propia orden mueve el precio). Es el paper seminal detrás de casi todos los algoritmos de ejecución institucionales "de segunda generación".
- **Smart Order Routing (SOR)**: en mercados fragmentados (el mismo activo cotiza en varias bolsas/venues a la vez), el SOR decide automáticamente dónde enviar cada parte de la orden para minimizar precio pagado + comisiones de cada venue.

Fuentes: [Optimal Execution of Portfolio Transactions — Almgren & Chriss (paper original, Journal of Risk 2000)](https://www.smallake.kr/wp-content/uploads/2016/03/optliq.pdf) · [QuantInsti — blog de ejecución algorítmica](https://blog.quantinsti.com/)

## Cómo se ubica esto en el proyecto

El orden lógico es: **datos históricos → backtesting con walk-forward → paper trading → recién ahí, si todo se sostiene, ejecución real supervisada.** Ahora mismo el proyecto está en la primera etapa (conocimiento/datos), así que esto queda documentado para cuando se llegue a paper trading — no antes.

- **Alpaca** es el candidato natural para paper trading de equities/cripto (retoma el caso de swing CRM/WFC/SLB) por lo simple que es empezar.
- **Interactive Brokers** es el candidato para XAU/USD el día que se quiera pasar la estrategia de scalping de Pine Script/TradingView a ejecución automática real, porque es de los pocos con cobertura de forex/metales vía API.

Sources: [Best Broker APIs for Algorithmic Trading 2026 — TradeAlgo](https://www.tradealgo.com/trading-guides/tools/best-broker-apis-for-algorithmic-trading-in-2026) · [Alpaca — Algorithmic Trading API](https://alpaca.markets/algotrading) · [Best Brokers for Algorithmic Trading 2026 — BrokerChooser](https://brokerchooser.com/best-brokers/best-brokers-for-algo-trading)
