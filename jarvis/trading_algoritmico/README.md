# Algo Trading — proyecto de backtesting unificado

**Estado: plan armado, sin código todavía.** Investigación completa + plan de construcción (`PLAN_CONSTRUCCION.md`) + bitácora activa (`bitacora_activos.md`). El código arranca cuando Diego lo pida — ver "Próximo paso concreto" en el plan.

## Por qué existe esta carpeta

El informe [`ANALISIS_ESTRATEGICO_IA_FINANCIERA.md`](../ANALISIS_ESTRATEGICO_IA_FINANCIERA.md) (03/07/2026) ya había detectado el problema de fondo en lo que existe hoy:

- **XAU/USD** (`jarvis/trading/`): `backtest.py` sin walk-forward real. Win rate cayó de 70,0% a 38,5% en corridas consecutivas sin tocar el código — señal clara de overfitting de ventana corta, no de una estrategia validada.
- **BTC scalping** (`jarvis/btc_scalping/`): carpeta `backtest/` existe pero vacía.
- **Swing equities** (CRM/WFC/SLB, análisis del 09/08/2026): backtest mecánico corrido una vez (40,4% de aciertos, flojo), pero los scripts vivían en un scratchpad efímero y se perdieron.
- Fuentes de datos **desalineadas entre sí**: Dukascopy manual para unos casos, yfinance para otros.

En resumen: tres backtests sueltos, sin metodología de validación común, sin fuente de datos consistente. Esta carpeta junta la investigación necesaria para resolver eso antes de escribir una línea de motor nuevo.

## Contenido

| Archivo | Qué cubre |
|---|---|
| [`PLAN_CONSTRUCCION.md`](PLAN_CONSTRUCCION.md) | **Empezar por acá** — qué debemos tener, universo de activos propuesto, estructura de carpetas, próximo paso concreto |
| [`bitacora_activos.md`](bitacora_activos.md) | Log de cada revisión de activos — se actualiza cada vez que Diego pide analizar algo acá |
| [`knowledge/fuentes_datos_historicos.md`](knowledge/fuentes_datos_historicos.md) | APIs y datasets de precio histórico para XAU/forex, cripto y equities — gratis y pagos |
| [`knowledge/frameworks_backtesting.md`](knowledge/frameworks_backtesting.md) | Librerías Python de backtesting (vectorizadas vs. event-driven) evaluadas por separado |
| [`knowledge/plataforma_backtesting.md`](knowledge/plataforma_backtesting.md) | **Decisión de plataforma**: LEAN (motor de QuantConnect) self-hosted, como motor único multi-activo |
| [`knowledge/metodologia_validacion.md`](knowledge/metodologia_validacion.md) | Walk-forward optimization — el estándar para no repetir el problema del 70%→38,5% WR |
| [`knowledge/brokers_ejecucion.md`](knowledge/brokers_ejecucion.md) | APIs de brokers para eventual ejecución algorítmica (mapeo de opciones, no ejecución real) |
| [`knowledge/traders_referentes.md`](knowledge/traders_referentes.md) | Traders y firmas de trading sistemático de referencia mundial (Ivan Scherman, Jim Simons, Ed Seykota, y otros) |

## Cómo seguir sin perder el hilo

Este proyecto está registrado en el `CLAUDE.md` raíz del repo (equipo Trading/Finanzas) — eso significa que **cualquier sesión, en cualquier máquina donde esté clonado Jarvis, lo va a encontrar**, a diferencia de la memoria automática que es específica de cada computadora. Cuando Diego pida revisar activos, la entrada va en `bitacora_activos.md`.
