# Fuentes de datos históricos

Investigación de agosto de 2026. Objetivo: reemplazar la mezcla actual de Dukascopy manual (XAU) + yfinance (equities/otros) por una fuente consistente por instrumento.

## Oro / XAU-USD (forex)

| Fuente | Qué ofrece | Costo |
|---|---|---|
| [HistData.com](https://www.histdata.com/download-free-forex-historical-data/) | Datos M1 (barras de 1 minuto) y tick con resolución de 1 segundo, descarga directa | Gratis |
| [GoldAPI.io](https://www.goldapi.io/) | API REST/JSON de precio spot de oro y plata, histórico incluido | Gratis (con límites) |
| [UniRateAPI](https://unirateapi.com/gold-price-api) | 58 años de histórico LBMA, consultas por rango de fechas | Gratis (tier limitado; ticks sub-minuto requieren feed de bróker) |
| [Barchart.com](https://www.barchart.com/forex/quotes/%5EXAUUSD/price-history/historical) | Intradía hasta 1 minuto, ~10 años hacia atrás | Gratis con registro |
| [EODHD](https://eodhd.com/financial-summary/XAUUSD.FOREX) | Histórico + fundamentals vía API | Pago |

**Recomendación:** HistData.com para reconstruir el histórico base (M1/tick, gratis, sin límite de descarga) + GoldAPI.io o UniRateAPI si se necesita actualización incremental vía API. Evita depender de un solo proveedor no versionado como hoy con Dukascopy manual.

**Verificación real (14/08/2026), a raíz de que la descarga de Dukascopy resultó mucho más lenta de lo estimado (~3 semanas al ritmo real, no días):**

- **Confirmado**: XAUUSD disponible en HistData.com de 2009 a 2026, con **M1 directo** (no hace falta agregar desde tick como con Dukascopy) y también tick si se necesita.
- **Ventaja estructural real sobre Dukascopy**: la descarga es por **archivo mensual/anual en bloque (zip)**, no una request por hora como el endpoint de Dukascopy — estructuralmente debería ser mucho más rápido para bajar rangos largos.
- **Contra a tener en cuenta**: la descarga gratuita manual por navegador de HistData pide **resolver un captcha por cada archivo** — no es un endpoint directo scrapeable sin más. Existen herramientas de la comunidad que automatizan esto (`histdatacom` en PyPI, `hddl`, `HistDataScraper` en GitHub), pero agregan una capa de dependencia de terceros no oficial.
- **Decisión pendiente, no tomada todavía**: no se cambió la fuente activa — la descarga de 5 años por Dukascopy sigue corriendo en background a pedido explícito de Diego. Esto queda documentado para la próxima vez que se evalúe una fuente de datos (para XAU o para sumar otro instrumento), no para reemplazar lo que ya está en curso.

## Criptomonedas

| Fuente | Qué ofrece | Costo |
|---|---|---|
| [CCXT](https://github.com/ccxt/ccxt) (librería) | OHLCV histórico de 100+ exchanges (Binance incluido), Python/JS/PHP, sin suscripción | Gratis |
| [CryptoDataDownload](https://www.cryptodatadownload.com/data/) | CSVs OHLCV diarios/horarios/1-min desde 2017, Binance/Bitstamp/Gemini/Bitfinex, sin login ni rate limit | Gratis |
| [CoinAPI](https://docs.coinapi.io/market-data/how-to-guides/get-historical-ohlcv-data-using-coinapi) | OHLCV histórico multi-exchange vía API | Freemium |

**Recomendación:** CCXT para automatizar la descarga (ya sería consistente con el ecosistema Python del resto del proyecto) o CryptoDataDownload si se prefiere no escribir código de ingesta todavía.

## Equities (para retomar el backtest de swing CRM/WFC/SLB)

| Fuente | Qué ofrece | Costo |
|---|---|---|
| [yfinance](https://github.com/ranaroussi/yfinance) | Wrapper no oficial de Yahoo Finance, sin API key, lo que ya se usa en `scan_opportunities.py` | Gratis, pero inestable (Yahoo cambia el backend seguido) |
| [Tiingo](https://www.tiingo.com/) | Free tier generoso, datos de cierre diario limpios y bien documentados, algunos fundamentals | Freemium |
| [Alpha Vantage](https://www.alphavantage.co/) | 20+ años de histórico, cubre equities/forex/cripto | Freemium — free tier muy ajustado (25 llamadas/día) |
| [Polygon.io](https://polygon.io/) | Datos institucionales, tiempo real | Pago para tiempo real |

**Recomendación:** mantener yfinance para prototipado rápido (ya integrado), pero migrar a Tiingo si se necesita corridas de backtest reproducibles sin que un cambio de Yahoo rompa el pipeline a mitad de camino — es lo que le pasó al backtest filtrado de swing que se perdió en scratchpad.

Sources: [HistData.com](https://www.histdata.com/download-free-forex-historical-data/) · [GoldAPI.io](https://www.goldapi.io/) · [UniRateAPI](https://unirateapi.com/gold-price-api) · [Barchart](https://www.barchart.com/forex/quotes/%5EXAUUSD/price-history/historical) · [EODHD](https://eodhd.com/financial-summary/XAUUSD.FOREX) · [CryptoDataDownload](https://www.cryptodatadownload.com/data/) · [CoinAPI](https://docs.coinapi.io/market-data/how-to-guides/get-historical-ohlcv-data-using-coinapi) · [Financial Data APIs Compared 2026](https://www.ksred.com/the-complete-guide-to-financial-data-apis-building-your-own-stock-market-data-pipeline-in-2025/)
