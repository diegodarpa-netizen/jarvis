# Geopolítica y selección de activos — cómo hacerlo sin volverse discrecional

Investigación de agosto de 2026, a raíz de la pregunta de Diego sobre usar contexto geopolítico para elegir en qué activos enfocar la estrategia.

## La tensión de fondo

Elegir activos porque "creemos que la geopolítica va a hacer que suban" es una predicción nuestra — reintroduce la "contaminación narrativa" que Jim Simons evitaba explícitamente (ver `traders_referentes.md`). La alternativa sistemática: usar un **índice medible** de riesgo geopolítico como input del sistema, no nuestra opinión sobre el futuro.

## La herramienta: Geopolitical Risk Index (GPR)

De **Dario Caldara y Matteo Iacoviello** (economistas de la Reserva Federal de EE.UU.). Se construye contando automáticamente artículos sobre guerras, tensión militar, terrorismo y conflictos internacionales en 10 diarios grandes (NYT, WSJ, FT, The Guardian, Chicago Tribune, Daily Telegraph, The Globe and Mail, LA Times, USA Today, Washington Post). **Gratis, público, actualizado semanalmente** — descargable directo del sitio de la Fed.

## Evidencia empírica por activo

### Oro — refugio confiable y consistente
- Correlación positiva significativa con GPR y VIX; negativa con DXY (dólar) e índices bursátiles.
- Confirmado en estudios sobre Irak-Kuwait (1990), 11-S (2001), invasión a Ucrania (2022), ataques Irán-Israel (2024/2025).
- Coincide con el resultado que ya vimos en el backtest del portfolio: XAU fue el único activo que realmente funcionó con la estrategia EMA 20/50.

### Bitcoin — la narrativa de "oro digital" no aguanta el dato
- Doble personalidad: en tiempos tranquilos se comporta como activo de riesgo correlacionado con el Nasdaq, no como refugio.
- **Problema serio:** en el estrés macro real, la correlación de BTC con activos de riesgo tiende a *subir* — se derrumba junto con las acciones justo cuando más se necesitaría que actuara como cobertura.
- Consenso académico: dividido, pero mayoritariamente apunta a que BTC **no** es un refugio geopolítico confiable, pese a la fama popular de "oro digital".

## Cómo lo hacen los fondos quant reales

No predicen el próximo conflicto — construyen proxies medibles (índices basados en texto, detección de régimen de volatilidad, cambios de correlación entre clases de activo) y ajustan exposición dinámicamente: reducen riesgo cuando el índice sube, rotan hacia los activos que la evidencia histórica confirma que responden bien en ese régimen. Mismo patrón que el filtro de tendencia (Efficiency Ratio) ya implementado, aplicado a otra dimensión (régimen geopolítico en vez de régimen de tendencia).

## Decisión pendiente

Incorporar el índice GPR real como señal del sistema — cuando el GPR está alto, aumentar sistemáticamente el peso en XAU; cuando está bajo, operar más parejo entre los 5 activos. Pendiente de implementación.

Sources: [Measuring Geopolitical Risk — Caldara & Iacoviello (Fed)](https://www.federalreserve.gov/econres/ifdp/files/ifdp1222.pdf) · [Geopolitical Risk Index — policyuncertainty.com](https://www.policyuncertainty.com/gpr.html) · [The Gold market as a safe haven against stock market uncertainty — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S030142072030903X) · [Safe Havens in Turbulent Times: Gold and USD — MDPI](https://www.mdpi.com/1911-8074/19/5/308) · [Examining safe-haven capabilities of gold and cryptocurrencies — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11616563/) · [Is Bitcoin the best safe haven against geopolitical risk? — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1544612324015721) · [Decoded: Integrating Geopolitical Risk into Algorithmic Trading Models — QuantArtisan](https://quantartisan.com/blog/quantifying-geopolitical-risk-a-framework-for-integrating-macro-and-sentiment-si-kv62)
