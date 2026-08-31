# Software generador/optimizador de estrategias — panorama completo (pago vs. gratis)

Investigación de agosto de 2026, a pedido de Diego: mapear todo lo que existe para "probar millones de combinaciones y filtrar" — sin comprar nada todavía, solo para tener el panorama completo cuando haga falta decidir.

---

## Pagos — generadores por fuerza bruta / programación genética

| Software | Qué hace | Precio | Corre en Mac | Ejecuta en |
|---|---|---|---|---|
| **[StrategyQuant X](https://strategyquant.com/)** | Programación genética — combina millones de condiciones de entrada/salida, filtra por tus criterios (Sharpe, drawdown, etc.), miles de backtests por segundo | US$1.290 (Starter) / US$1.490 (Professional) / US$2.900 (Ultimate) — licencia única | **Sí, nativo** (.dmg para ARM) | MetaTrader 4/5, NinjaTrader |
| **[Build Alpha](https://www.buildalpha.com/)** | Motor propio, 6.000-7.000 señales predefinidas, tests de robustez para detectar "backtests mentirosos" (su propio término para overfitting) | US$1.497 — licencia única | No confirmado | Varias plataformas, sin código |
| **[Adaptrade Builder](https://www.adaptradebuilder.com/)** | Programación genética más simple, incluye estrategias bonus ya armadas | US$895-995 — licencia única | Probablemente no (pensado para TradeStation/MultiCharts/NinjaTrader, todo Windows) | TradeStation, MultiCharts, NinjaTrader, MetaTrader, AmiBroker |

## Pagos — plataformas de trading con optimizador integrado (no exclusivamente generadores)

| Software | Qué ofrece | Costo |
|---|---|---|
| **AmiBroker** | Motor de optimización muy rápido en su propio lenguaje (AFL), fuerte para comparar cientos de símbolos a la vez | Pago, licencia propia |
| **MultiCharts** | Backtesting a nivel portfolio, optimización genética integrada, multi-símbolo | Pago |
| **NinjaTrader** | Backtesting real con datos de mercado, **tiene capa gratuita real** (no todo pago) | Freemium |
| **MetaTrader 5** | Strategy Tester integrado con MQL5, optimización de parámetros | Gratis (bróker lo provee) |
| **TradingView (Pine Script)** | Backtesting/forward-testing de una idea por vez, liviano, no genera estrategias por fuerza bruta | Freemium |

## Gratis — lo que YA tenemos disponible y no lo habíamos usado para esto

Esto es lo más importante del hallazgo de hoy: **ya teníamos, sin saberlo, el equivalente funcional gratuito** de lo que hacen StrategyQuant/Build Alpha, documentado desde hace días en `frameworks_backtesting.md` pero nunca usado con este propósito específico:

- **[Freqtrade + Hyperopt](https://www.freqtrade.io/en/stable/hyperopt/)**: Freqtrade (ya en nuestra lista de frameworks) tiene un optimizador integrado que usa el paquete `optuna` — arranca con combinaciones aleatorias y después usa un algoritmo de muestreo (NSGAIII) para converger rápido hacia la mejor combinación de parámetros dentro del espacio de búsqueda que definas. Es, en esencia, lo mismo que hace StrategyQuant (búsqueda inteligente sobre un espacio enorme de combinaciones), gratis y open-source.
- **[VectorBT (edición comunitaria, gratis)](https://github.com/polakowo/vectorbt)**: en vez de recorrer las barras una por una para cada estrategia, empaqueta miles de configuraciones en arrays de NumPy y las corre todas *a la vez*, acelerado con Numba/Rust — literalmente su descripción es "corré miles de ideas de trading antes de que otros terminen una". Convierte horas de grid search en segundos.

**La diferencia real con las opciones pagas no es la capacidad técnica — es la interfaz.** StrategyQuant/Build Alpha son "apuntar y hacer clic, sin código". Freqtrade+Hyperopt y VectorBT requieren escribir código Python (que ya venimos haciendo todo el proyecto). Si el objetivo es aprender el proceso a fondo (que es lo que Diego planteó desde el arranque del proyecto), la opción gratuita además **enseña más**, porque no queda una caja negra de por medio.

## Otras plataformas cloud relevadas (para completar el panorama)

- **[QuantConnect](https://www.quantconnect.com/)**: ya evaluado y descartado en `plataforma_backtesting.md` — el uso local/API requiere plan pago Researcher (US$84/mes).
- **[Quantiacs](https://quantiacs.com/)**: plataforma gratuita de investigación cuantitativa en Python, con datos históricos de acciones/futuros incluidos — no evaluada en profundidad todavía, candidato a revisar si se necesita otra fuente de datos/cómputo.
- **Numerai**: plataforma de estrategias crowdsourceadas con API en Python — modelo similar al de WorldQuant BRAIN (ver `top10_traders_algoritmicos.md`), pero para inversores retail que compiten con modelos de ML.

---

## Conclusión — no hay que gastar nada para tener esta capacidad

**Ya tenemos acceso gratuito a la misma capacidad técnica que ofrecen los US$900-2.900 de las herramientas pagas** — vía Freqtrade+Hyperopt o VectorBT, ambos Python, ambos ya identificados en nuestro propio stack. La ventaja de pagar sería únicamente velocidad de desarrollo (no escribir código) — no capacidad nueva.

**La misma advertencia aplica para cualquiera de las dos vías, pago o gratis:** generar/probar miles o millones de combinaciones sin la disciplina de walk-forward que ya tenemos como regla, es la forma más rápida de producir overfitting a escala industrial — no importa cuán buena sea la herramienta, el riesgo de "encontrar algo que se ve ganador por puro azar estadístico" crece con la cantidad de combinaciones probadas (ver `metodologia_validacion.md` y `machine_learning_financiero.md`, la Primera Ley de Backtesting de López de Prado).
