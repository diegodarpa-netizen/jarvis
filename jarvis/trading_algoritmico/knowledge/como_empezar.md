# Cómo empezar — el camino ordenado, no la biblioteca de referencia

Investigación de agosto de 2026, a pedido explícito de Diego (13/08/2026): *"antes de eso [analizar datos] es saber sobre trading algorítmico... si no te pido que hagas estos análisis vos ya querés arrancar con la estrategia sin siquiera saber qué vamos a encontrar."*

**Por qué existe este archivo aparte de todo lo demás en `knowledge/` y `biblioteca/`:** el resto de la carpeta es una biblioteca de referencia — se consulta cuando aparece una duda puntual. Esto es distinto: es el **orden** en el que hay que atravesar esa biblioteca, sintetizado de fuentes gratuitas y legales (no hace falta ningún libro pirateado para tener esto resuelto). Cuando Diego pregunte "¿por dónde seguimos?", la respuesta se busca acá primero.

---

## Las 4 etapas (consenso entre QuantStart, EPAT/QuantInsti y AlgoTrading101)

Tres fuentes independientes coinciden en el mismo esqueleto de fondo, con matices:

| Etapa | QuantStart (gratis, artículos) | EPAT/QuantInsti (currícula de curso pago) | AlgoTrading101 (roadmap práctico) |
|---|---|---|---|
| 1 | Identificación de estrategia | Fundamentos (Python, estadística) → microestructura | Elegir estrategia según el propio trader |
| 2 | Backtesting (con eliminación de sesgos) | Familias de estrategia (momentum/mean-reversion/stat-arb) | Entorno técnico + datos |
| 3 | Sistema de ejecución | Riesgo y ejecución (módulo separado) | Backtesting in/out-of-sample |
| 4 | Gestión de riesgo | Machine learning (opcional, avanzado) | Producción/paper trading |

Fuentes: [QuantStart — Beginner's Guide to Quantitative Trading](https://www.quantstart.com/articles/beginners-guide-to-quantitative-trading/) · [QuantInsti — EPAT](https://www.quantinsti.com/epat) · [AlgoTrading101 — Quantitative Trader's Roadmap](https://algotrading101.com/learn/quantitative-trader-guide/)

**Lo que las tres tienen en común y que nosotros nos saltamos:** la Etapa 1 real no es "elegir un indicador" — es **clasificar el mercado/activo** (¿tiende o revierte?) y **definir el perfil del trader** antes de mirar un solo dato. Fuimos directo a la Etapa 3 (backtesting) varias veces esta semana sin cerrar la 1.

---

## El hueco que encontramos: Chan tiene un libro específico para la Etapa 1, y no era el que teníamos

Ya estaba en la biblioteca *Algorithmic Trading: Winning Strategies and Their Rationale* (técnico, de estrategias concretas). El que faltaba es su otro libro, *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* — el Capítulo 2 se llama **"Fishing for Ideas"** y arranca preguntando, antes de tocar datos: cuántas horas por semana tenés disponibles, tu nivel de programación, tu capital, tu objetivo. Agregado a `biblioteca/README.md` (13/08/2026) — sin el texto, con la estructura y fuentes públicas.

**Consejos concretos de Chan, de entrevistas gratuitas y públicas (no del libro):**
- **Clasificar el mercado primero**: ¿mean-reverting o momentum-driven? Esto determina qué familia de estrategia probar — evita testear a ciegas. Es exactamente lo mismo que ya sabíamos hacer con Hurst/ADF, pero como *paso 1*, no como algo que se corre en paralelo a todo lo demás. [Fuente: traders.com — entrevista con Chan]
- **Empezar simple**: literalmente con Excel antes que Python, con la estrategia más básica posible — porque un trader independiente no puede competir en complejidad con un banco grande, y en su propia experiencia lo más simple fue lo rentable.
- **Evitar complejidad excesiva**: sistemas complejos generan más puntos de falla — coincide con nuestra propia regla de no ajustar parámetros hasta que "se vea bien" (data snooping).
- **Priorizar el drawdown tanto como la ganancia**: es lo que separa el trading personal del institucional — y es literalmente la misma lección que ya sacamos de Ivan Scherman (`traders_referentes.md`): "solo la buena gestión de riesgo permite ganancias sostenidas".
- **Validación rigurosa fuera de muestra**: nada nuevo — es el walk-forward que ya tenemos documentado en `metodologia_validacion.md`, confirmado por una tercera fuente independiente.

[Fuente: Better System Trader — Ep. 012, entrevista con Ernest Chan](https://bettersystemtrader.com/012-ernest-chan/)

---

## El camino aplicado a Jarvis, en orden — desde donde estamos parados hoy

1. **Perfil del trader (Diego) — pendiente, es la Etapa 1 real.** No lo resolvimos todavía porque Diego priorizó primero cerrar la base teórica (este documento). Cuando se retome: tiempo disponible por semana, nivel de involucramiento en código/matemática, objetivo del proyecto (aprender / sistema propio / eventual automatización real), capital de referencia. Determina todo lo que sigue.
2. **Clasificar el activo (XAU, en la ventana que se decida) — mean-reverting vs. momentum**, con ADF/Hurst/autocorrelación tratando los gaps de sesión correctamente (ya resuelto metodológicamente, ver conversación del 13/08 sobre el problema de gaps de Chan/epchan.blogspot.com). Esto es la Etapa 1 de QuantStart/AlgoTrading101 — recién acá se decide qué familia de estrategia probar primero, no antes.
3. **Backtesting de la estrategia que indique el resultado del paso 2**, con separación in-sample/out-of-sample real — no las ventanas de parámetros fijos que veníamos corriendo (que prueban robustez, pero no son walk-forward optimization estricto).
4. **Gestión de riesgo como módulo separado de la señal** — el patrón que confirman Scherman, Chan y la propia EPAT: no se mezcla con la lógica de entrada, se audita aparte (drawdown máximo, tamaño de posición, Kelly fraccionado).
5. **Recién ahí, sistema de ejecución / paper trading** — no antes. Ya mapeado en `brokers_ejecucion.md`, pero es el último paso, no algo para resolver ahora.

## Qué NO cambia de lo ya investigado

Este documento no reemplaza nada de `knowledge/` ni `biblioteca/` — los reordena. Todo lo que ya está (walk-forward, filtros de tendencia, selección de universo, plataforma NautilusTrader) sigue siendo válido y se usa en el momento del camino que le corresponde, no todo junto desde el principio.
