# Selección de universo de activos — autocrítica y evidencia

Investigación de agosto de 2026, a raíz de que Diego preguntó en qué se basó la elección de XAU/EUR/BTC/SPY/QQQ — y si fue un error.

## Cómo se eligieron realmente (sin maquillar)

- **XAU y BTC**: porque ya eran proyectos existentes de Diego en Jarvis — continuidad, no criterio de selección.
- **EUR/USD**: propuesto por Jarvis para "completar" tres clases de activo (metales/forex/cripto) — el par más común por default, sin evidencia de que específicamente EUR/USD tuviera mejor edge que otro par.
- **SPY y QQQ**: pedidos por Diego sobre la marcha — los dos instrumentos de acciones de EE.UU. más conocidos/familiares.

**Ninguno pasó un filtro de universe selection real** (liquidez medida, estabilidad de Sharpe, correlación verificada antes de elegir, per `filtros_de_tendencia.md`/investigación de universe selection). Fue conveniencia y familiaridad — sesgo de disponibilidad.

## La referencia académica seria: Moskowitz, Ooi & Pedersen (2012) — "Time Series Momentum"

El paper más citado de la industria sobre si el trend-following funciona. Probaron **58 instrumentos líquidos** (índices bursátiles, monedas, commodities, bonos soberanos) con **>25 años de datos**. 52 de los 58 mostraron momentum estadísticamente significativo (5% de significancia).

## Comparación contra Turtle Traders y CTAs modernos

Las tres referencias (Moskowitz et al., Turtle Traders originales de Dennis/Eckhardt, CTAs modernos como Winton/AHL) coinciden en cubrir: metales, monedas, **bonos soberanos/renta fija**, commodities amplios (energía, agrícolas), e índices de acciones (típicamente uno por región, no varios superpuestos). CTAs modernos operan típicamente 50+ mercados.

## Dónde queda parado nuestro universo de 5

| Clase de activo | ¿En las referencias serias? | ¿La tenemos? |
|---|---|---|
| Metales (oro) | Sí | ✅ XAU |
| Monedas | Sí | ✅ EUR/USD |
| Bonos soberanos/renta fija | Sí, en las tres — históricamente de las clases más consistentes | ❌ No tenemos ninguna |
| Commodities amplios | Sí (energía, agrícolas) | ❌ Solo oro |
| Índices de acciones | Sí, uno por región típicamente | ⚠️ Tenemos SPY y QQQ — redundantes entre sí |
| Cripto | No aparece en ninguna referencia (sin 25+ años de historia para validar) | ⚠️ BTC sin el mismo respaldo histórico |

## Problemas concretos identificados

1. **SPY y QQQ no diversifican entre sí** — misma clase de activo, alta correlación, superposición de las mismas mega-empresas tecnológicas en ambos índices.
2. **Falta renta fija y commodities amplios** — las clases que las tres referencias coinciden en incluir siempre.
3. **Universo muy angosto**: 5 activos contra 58 del paper académico o 50+ de un CTA real — mayor riesgo de que el ruido domine sobre la señal.

## Herramientas de screening — Finviz vs. Yahoo Finance vs. Bloomberg (11/08/2026)

| | Finviz | Yahoo Finance | Bloomberg Terminal |
|---|---|---|---|
| Cobertura | Solo acciones/ETFs EE.UU. (+8.000 tickers), paneles básicos de futuros/forex/cripto sin screening profundo | Acciones, ETFs, fondos, futuros, índices — cobertura internacional | Todo: acciones, bonos, forex, commodities, derivados, cripto |
| Filtros | 67+ (descriptivos, fundamentales, técnicos) — el más profundo de los tres para acciones | ~95 métricas, criterios más básicos | Ilimitado, pensado para terminal profesional |
| Costo | Gratis (plan pago opcional) | Gratis (`yfinance`, ya integrado en el proyecto) | ~US$24.000/usuario/año |

**Decisión:** Yahoo Finance sigue siendo la fuente de datos históricos del proyecto (ya integrado). Finviz queda como herramienta complementaria gratuita para el Paso 1-2 (liquidez + capitalización) si se amplía la pata de acciones más allá de SPY. Bloomberg es la referencia de a qué apunta el proceso ideal, pero fuera de escala para este proyecto — la estrategia es replicar el **método** de los profesionales con herramientas gratuitas, no su presupuesto.

Sources: [Best Stock Screeners 2026 — Koyfin](https://www.koyfin.com/blog/best-stock-screeners/) · [FINVIZ vs Yahoo Finance — Find My Moat](https://www.findmymoat.com/vs/finviz-vs-yahoo-finance) · [Finviz Screener Hacks — LuxAlgo](https://www.luxalgo.com/blog/finviz-screener-hacks-save-hours-scanning/)

## Ajuste propuesto (pendiente de confirmación)

Sacar la redundancia SPY+QQQ (quedarse con uno, o tratarlos explícitamente como una sola apuesta no dos), y sumar al menos una clase de renta fija (ej. TLT — ETF de bonos largos del Tesoro de EE.UU., con décadas de datos vía yfinance) para acercar el universo a lo que la evidencia académica realmente respalda.

Sources: [Time Series Momentum — SSRN (Moskowitz, Ooi, Pedersen)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2089463) · [Time Series Momentum — NYU Stern (PDF)](https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf) · [Time Series Momentum — ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0304405X11002613) · [Turtle Trading Strategy — QuantifiedStrategies](https://www.quantifiedstrategies.com/turtle-trading-strategy/) · [The Original Turtle Trading Story and Rules — Forex Training Group](https://forextraininggroup.com/the-original-turtle-trading-story-and-rules/) · [Managed Futures Trend Following — Return Stacked](https://www.returnstacked.com/managed-futures-trend-following/)
