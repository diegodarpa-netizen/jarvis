# Plataformas y recursos gratuitos — barrido amplio

Investigación de agosto de 2026, a pedido explícito de Diego (13/08/2026): *"quiero que aprendas todo lo que puedas en trading algorítmico, que busques en todas las plataformas que puedas."* Complementa `biblioteca/README.md` (los 6 libros) y `biblioteca/teoria_fundamental.md` (teoría de fondo) — esto es el mapa de **dónde seguir aprendiendo de forma continua**, no solo lo investigado puntualmente hoy.

Todo lo de acá es gratis y legal — cero excepciones a la regla de copyright.

---

## 1. Cursos estructurados gratuitos

| Recurso | Qué ofrece | Nivel |
|---|---|---|
| **[freeCodeCamp — Algorithmic Trading Using Python](https://www.freecodecamp.org/news/algorithmic-trading-using-python-course/)** (Nick McCullum) | Curso completo de 4 horas, gratis en YouTube + repo de código en GitHub. Cubre fundamentos + 3 proyectos reales: fondo indexado S&P 500 equal-weight, estrategia de momentum cuantitativo, estrategia de value cuantitativo. Usa datos de prueba (no arriesga capital ni paga API) | Principiante-intermedio, hands-on |
| **[Class Central — Quantitative Finance](https://www.classcentral.com/subject/quantitative-finance)** | Agregador de 100+ cursos gratuitos de Coursera/edX/universidades, filtrable y rankeado por reseñas reales | Todos los niveles |
| **Coursera (previsualización gratis)** | "Fundamentals of Quantitative Modeling" (UPenn), "Financial Engineering and Risk Management" (Columbia), "Machine Learning for Trading" (Google Cloud/NYIF) — el primer módulo de cada uno se puede cursar gratis sin certificado | Intermedio-avanzado |
| **[QuantInsti — EPAT](https://www.quantinsti.com/epat)** | Ya documentado en `biblioteca/README.md` como referencia de estructura curricular (pago, 6 meses) — no se paga, pero QuantInsti también publica gratis buena parte de su blog técnico (`blog.quantinsti.com`), ya citado varias veces en `knowledge/` | Referencia de orden, no de contenido pago |

## 2. Comunidades y foros activos

| Recurso | Qué ofrece |
|---|---|
| **[r/algotrading](https://reddit.com/r/algotrading)** | La comunidad más grande en inglés — discusiones reales de traders retail (no solo teoría de marketing de curso pago), hilos de "qué me falló" tan valiosos como los de éxito |
| **Foro de la comunidad de QuantConnect** | Estrategias compartidas, debugging de LEAN/backtests, aunque nosotros ya migramos a NautilusTrader |
| **Substacks de practicantes individuales** (ej. Quant Journey, Algomatic Trading, Young and Calculated) | Menos autoridad institucional que un libro, pero terreno real de "cómo piensa alguien que lo hace todos los días" — hay que leerlos con más escepticismo que a un paper académico |

## 3. Librerías de código abierto — lo que faltaba adicionar a `frameworks_backtesting.md`

Ya teníamos Zipline, Backtrader, VectorBT, Freqtrade, NautilusTrader, CCXT documentados. Lo nuevo que encontramos en esta barrida (lista curada [paperswithbacktest/awesome-systematic-trading](https://github.com/paperswithbacktest/awesome-systematic-trading), 97 librerías catalogadas):

| Librería | Para qué sirve | Por qué la sumamos |
|---|---|---|
| **TA-Lib** | Indicadores técnicos clásicos (RSI, MACD, Bollinger, etc.) ya implementados y optimizados | Evita reimplementar indicadores a mano — más confiable que código propio |
| **pandas-ta** | +130 indicadores sobre DataFrames de pandas directamente | Alternativa más "pythonica" a TA-Lib, más fácil de integrar con nuestro stack actual |
| **PyPortfolioOpt** | Optimización de portafolio (frontera eficiente, Markowitz) ya implementada | Directamente relevante para cuando se implemente el sizing normalizado por volatilidad (gap ya identificado en la auditoría del 13/08) |
| **quantstats** | Analítica y reportes de performance de portfolio (Sharpe, drawdown, tearsheets) | Mejor que armar métricas a mano cada vez — estándar de facto para reportar resultados de backtest |
| **OpenBB Terminal** | Terminal de investigación de inversión open-source — la alternativa gratuita más cercana a un Bloomberg Terminal que existe | Útil para research exploratorio manual, no para backtesting en sí |

## 4. Canales de YouTube recomendados por la comunidad (no verificados por nosotros, para ver con criterio propio)

- **Kevin Davey** — trading algorítmico generalista, veterano de campeonatos de trading real
- **sentdex** — programación en Python aplicada a finanzas y trading (más técnico/software)
- **Part Time Larry** — algo trading con enfoque en IA/ML aplicado

## 5. Educación específica de forex (relevante porque XAU/USD cotiza como par de forex)

**[BabyPips — School of Pipsology](https://www.babypips.com/learn/forex)**: programa gratuito estructurado en niveles (Preschool → básico → intermedio → avanzado), cubre mecánica de forex, análisis técnico/fundamental, gestión de riesgo y psicología de trading. Módulos cortos (1-6 horas cada uno). La mayoría del contenido educativo es gratis — solo las "trading ideas" (señales) requieren suscripción paga, que no necesitamos.

## 6. Enciclopedia de referencia rápida

**[Investopedia — sección de Algorithmic Trading](https://www.investopedia.com/)**: no reemplaza a ningún libro ni paper, pero es la fuente más rápida para resolver "¿qué es X término?" sin tener que rastrear un paper académico — market making, arbitraje, scalping, todas las estrategias base explicadas en una página.

## 7. Meta-recurso: listas curadas de GitHub ("awesome lists")

Para no tener que rehacer este barrido cada vez que aparece una duda de "¿existe una librería para esto?":
- [paperswithbacktest/awesome-systematic-trading](https://github.com/paperswithbacktest/awesome-systematic-trading) — la más completa y prolija de las que encontramos, 97 librerías + libros + blogs + videos, categorizada
- [wangzhe3224/awesome-systematic-trading](https://github.com/wangzhe3224/awesome-systematic-trading) — cobertura similar, buena para cripto/futuros/opciones específicamente
- [merovinh/best-of-algorithmic-trading](https://github.com/merovinh/best-of-algorithmic-trading) — rankeada automáticamente por calidad/actividad del proyecto (actualizada semanalmente), útil para no elegir una librería abandonada

---

## Cómo se conecta esto con lo que ya hicimos

No cambia ninguna decisión ya tomada — NautilusTrader sigue siendo el motor elegido (`plataforma_backtesting.md`), Dukascopy/HistData siguen siendo las fuentes de datos (`fuentes_datos_historicos.md`). Esto es **superficie de aprendizaje adicional**: dónde seguir leyendo/mirando por fuera de este chat, y qué librerías puntuales usar cuando lleguemos a necesitar sizing por volatilidad (PyPortfolioOpt) o reportes de performance (quantstats) — ambos ya identificados como gaps pendientes en la auditoría del 13/08.
