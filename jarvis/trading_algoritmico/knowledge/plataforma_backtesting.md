# Plataforma de backtesting — decisión

Investigación de agosto de 2026. Este archivo responde puntualmente "sobre qué plataforma vamos a hacer el backtesting y cómo juntamos todo" — es la pieza que faltaba después de `frameworks_backtesting.md` (que comparaba librerías sueltas por activo).

## El problema de armar todo por separado

En `frameworks_backtesting.md` se evaluó un framework distinto por tipo de activo (Zipline para equities, NautilusTrader/Backtrader para XAU/BTC). Eso funciona, pero reproduce el mismo problema que ya tenemos hoy: **fuentes de datos y motores desalineados entre instrumentos** — es literalmente la causa raíz documentada en `ANALISIS_ESTRATEGICO_IA_FINANCIERA.md` (Dukascopy manual vs. yfinance). Sumar un tercer framework para equities no resuelve el problema, lo triplica.

## Recomendación: LEAN (motor de QuantConnect), self-hosted

[LEAN](https://github.com/QuantConnect/Lean) es un motor de backtesting/ejecución de código abierto (Apache 2.0, ~17.800 estrellas en GitHub) que resuelve las tres preguntas — datos, backtesting, cómo juntar todo — con una sola pieza de infraestructura:

- **Multi-activo nativo:** un mismo motor y un mismo portfolio central manejan Equities, Forex (incluye XAU/USD), Futuros, Cripto (6 exchanges), Opciones e Índices al mismo tiempo. No hace falta un motor por activo.
- **Datos incluidos:** librería de +400 TB — equities de EE.UU. desde 1998, forex con spreads interbancarios, futuros, miles de pares cripto. Elimina el problema de andar juntando fuentes sueltas (HistData, CCXT, yfinance) a mano por cada instrumento — siguen siendo útiles como respaldo/cross-check, pero dejan de ser la fuente primaria.
- **Backtesting event-driven real:** cada vela dispara el algoritmo exactamente como lo haría en vivo (no vectorizado). Esto es clave porque **el mismo código corre en backtest y en ejecución en vivo** — reduce el riesgo de que una estrategia pase el backtest y falle en vivo por diferencias de motor, que es el problema #1 que reportan las plataformas retail en 2026 según la comparativa de la industria.
- **Python nativo.**
- **Cómo se conecta con lo que ya identificamos:** LEAN corre backtests ilimitados gratis en el plan free (sin tarjeta, sin límite de tiempo). El paso a ejecución en vivo en la nube de QuantConnect cuesta desde US$60/mes — pero **al ser open source, se puede self-hostear con LEAN CLI** en la propia máquina, corriendo backtests y hasta ejecución en vivo conectado directo a un bróker (Interactive Brokers, Alpaca, OANDA, Binance) sin pagar ese plan. Coincide con la regla de no sumar gastos recurrentes innecesarios (misma lógica que ya aplicamos en marketing con la API key de Anthropic).

## Comparación rápida contra lo evaluado antes

| | LEAN (self-hosted) | Stack separado (Zipline + Backtrader/NautilusTrader) | MetaTrader 5 |
|---|---|---|---|
| Datos | Incluidos, multi-activo | Hay que armar el pipeline por fuente | Incluidos pero solo forex/CFD/futuros |
| Un solo motor para todos los activos | Sí | No (uno por tipo de activo) | Sí, pero sin equities/cripto reales |
| Backtest = mismo código que en vivo | Sí (event-driven) | Depende del framework elegido | Parcial — conocido por repaint en Pine/MQL5 (ya lo sufrimos con la estrategia OCC) |
| Costo | Gratis self-hosted | Gratis | Gratis |
| Curva de aprendizaje | Media-alta (hay que aprender la API de LEAN) | Media (cada framework por separado) | Baja, pero ya se evidenció el problema de repainting |

## Decisión

**LEAN self-hosted vía LEAN CLI** como motor único del proyecto. Reemplaza la idea de elegir un framework distinto por activo — un solo repo de estrategias, un solo motor, walk-forward implementado una vez y reutilizado para XAU, BTC y equities. Los frameworks vectorizados (VectorBT) siguen teniendo un lugar como herramienta de exploración rápida de parámetros antes de formalizar una estrategia en LEAN, pero no como motor de validación final.

Sources: [LEAN — QuantConnect (GitHub)](https://github.com/QuantConnect/Lean) · [lean.io](https://www.lean.io/) · [QuantConnect Review 2026 — QuantVPS](https://www.quantvps.com/blog/quantconnect-review) · [QuantConnect Review 2026 — AI Trading Camp](https://aitradingcamp.com/reviews/quantconnect) · [Best Backtesting Platforms 2026 — TradeAlgo](https://www.tradealgo.com/trading-guides/tools/best-backtesting-platforms-2026)

## Corrección importante (11/08/2026) — antes de instalar se profundizó más

La primera pasada de esta investigación subestimó el costo real de los datos en local. Lo que se confirmó después, antes de instalar:

- **Forex/CFD (OANDA/FXCM) — gratis y completo por LEAN CLI**, tick a diario, sin cuenta paga. Cubre **XAU/USD** sin costo — es la vía fácil para la prioridad #1 del proyecto.
- **Cripto y equities — NO son gratis por LEAN CLI.** Por licencias de exchange/bolsa, QuantConnect no puede regalar esos datos: hay que comprarlos (ej. ~US$600/año el "US Equity Security Master") **o traer los datos gratuitos ya identificados en `fuentes_datos_historicos.md`** (CryptoDataDownload/CCXT para BTC, Tiingo/yfinance para equities) y convertirlos a formato LEAN nosotros mismos — más trabajo de ingeniería, costo $0.
- **Self-hosting no ahorra tanto como parece**: si se quieren los datos curados de QuantConnect, se paga igual. Lo que sí se evita self-hosteando es el plan de trading en vivo en la nube (US$60/mes).
- **Requiere Docker** para correr backtests en local (el motor corre en contenedor) — no estaba instalado en la máquina de Diego al momento de instalar la CLI, es un paso pendiente y separado.
- **Requiere una cuenta de QuantConnect** (gratis) para el login de la CLI — la tiene que crear Diego, no Jarvis (regla de seguridad: no se crean cuentas ni se cargan API keys/tokens de terceros).
- Framework opinado (`QCAlgorithm`), curva de aprendizaje media-alta — no es Python libre, hay convenciones propias que aprender.

Sources adicionales: [LEAN CLI (GitHub)](https://github.com/QuantConnect/lean-cli) · [FOREX Data — QuantConnect Docs](https://www.quantconnect.com/docs/v2/lean-cli/datasets/quantconnect/download-in-bulk/forex-data) · [Costs — LEAN CLI Datasets](https://www.quantconnect.com/docs/v2/lean-cli/datasets/costs) · [Avoiding Vendor Lock-In — QuantConnect forum](https://www.quantconnect.com/forum/discussion/2400/avoiding-vendor-lock-in-running-lean-on-your-server/) · [Installing LEAN CLI — Docs](https://www.lean.io/docs/v2/lean-cli/installation/installing-lean-cli)

## Segunda corrección (11/08/2026) — LEAN CLI descartado, cambio a NautilusTrader

Al intentar generar el API token real en la cuenta de QuantConnect de Diego, la plataforma devolvió: **"To request an access token, you must belong to a paid organization"**. Se confirmó con la página oficial de precios: el plan gratis de QuantConnect **no incluye LEAN CLI local ni acceso a la API** — eso empieza en el plan **Researcher, US$84/mes**. El plan gratis solo sirve para el editor web en la nube de QuantConnect (sin instalar nada localmente, sin Docker, sin self-hosting real).

Esto invalida la recomendación anterior de "LEAN self-hosted = gratis". Se re-evaluaron alternativas 100% gratuitas y activamente mantenidas:

| Framework | Licencia | Mantenimiento | Veredicto |
|---|---|---|---|
| **NautilusTrader** | LGPL, open source | Activo, motor Rust+Python de alto rendimiento | **Elegido — reemplaza a LEAN** |
| Zipline-reloaded | Open source | Activo (último release jul/2025) | Especializado en equities, candidato secundario |
| VectorBT (open source, no confundir con VectorBT PRO que es pago US$20/mes) | Apache 2.0 + Commons Clause | Activo | Herramienta de exploración rápida de parámetros |
| Freqtrade | Open source | Activo | Solo si se busca un bot de cripto en vivo específicamente |
| Backtrader | Open source pero **proyecto muerto** — el propio creador lo dio por terminado, sin releases en años | Abandonado | Descartado |

**Decisión final: NautilusTrader** como motor único — es el que más se parece a la propuesta de valor que buscábamos en LEAN (event-driven, multi-activo, mismo código en backtest y en vivo, alta fidelidad de ejecución), sin ningún paywall.

**Bloqueo nuevo detectado (común a los 4 candidatos activos, no solo a NautilusTrader):** todos requieren Python ≥3.10 (VectorBT y Freqtrade piden ≥3.11). La Mac de Diego solo tenía Python 3.9.6 (Command Line Tools) y sin Homebrew — hace falta instalar Python 3.12 antes de seguir.

**Docker no quedó desperdiciado:** NautilusTrader no lo necesita para el backtesting local (solo lo usa opcionalmente para el adaptador de Interactive Brokers), así que el Docker Desktop que ya instalamos sigue siendo útil para cuando se conecte IB en `brokers_ejecucion.md`.

Sources: [QuantConnect Pricing](https://www.quantconnect.com/pricing/) · [NautilusTrader — Open Source Licensing](https://nautilustrader.io/legal/open-source-licensing/) · [NautilusTrader Installation Docs](https://nautilustrader.io/docs/latest/getting_started/installation/) · [Is Backtrader dead? — Backtrader Community](https://community.backtrader.com/topic/3702/is-backtrader-dead) · [vectorbt (GitHub)](https://github.com/polakowo/vectorbt) · [zipline-reloaded (GitHub)](https://github.com/stefan-jansen/zipline-reloaded) · [freqtrade (GitHub)](https://github.com/freqtrade/freqtrade)
