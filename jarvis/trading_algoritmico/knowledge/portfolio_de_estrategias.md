# Portfolio de estrategias — correr muchas a la vez

Investigación de agosto de 2026, a raíz de una pregunta de Diego sobre un amigo que dice correr "200 o 2000 estrategias" y cuántas corre Ivan Scherman.

## La matemática de por qué funciona

Con **N estrategias no correlacionadas**, cada una con Sharpe individual `S`, el Sharpe del conjunto combinado escala aproximadamente como `S × √N`. Lo que importa no es la cantidad — es cuán no-correlacionadas están entre sí. Muchas estrategias que ganan/pierden todas juntas (dependen del mismo régimen de mercado) no diversifican nada.

## Qué es realmente "una estrategia" cuando alguien dice "corro 200"

Casi nunca son 200 ideas originales. De menos a más diversificación real:

1. La misma lógica aplicada a muchos instrumentos (ej. un cruce de medias en 200 pares) — diversifica por activo, poco por idea.
2. La misma lógica con distintos parámetros/timeframes — diversifica poco, siguen correlacionadas entre sí.
3. Familias de lógica genuinamente distintas (trend-following + mean-reversion + stat-arb + market-making) — esto sí diversifica de verdad, y es mucho más difícil de construir.

**Modelo "plataforma"** (Citadel, Millennium, Balyasny): no es una lista central de N estrategias — son cientos de portfolio managers independientes, cada uno con su propio libro, y un sistema de riesgo central que asigna/retira capital dinámicamente según desempeño de cada uno. Es diversificación organizacional, no solo algorítmica.

## Cuántas estrategias corre Ivan Scherman

No publica un número exacto. La única cifra en su material oficial: **"decenas de algoritmos que escanean miles de activos en simultáneo"** (Fairvalue, sci.tech). O sea: decenas de estrategias (~10-90), no cientos ni miles — lo que sí son miles es la cantidad de **activos monitoreados**, no de estrategias distintas. Es una distinción clave: la cifra de "miles" que a veces se escucha en charlas informales probablemente mezcla "estrategias" con "instrumentos escaneados".

## La trampa: data snooping bias / comparaciones múltiples

Cuantas más estrategias se testean sobre el mismo histórico, más alta la probabilidad de que alguna parezca buena solo por azar estadístico. Es el mismo problema de overfitting ya documentado en el XAU de Jarvis (70%→38,5% WR), pero **multiplicado por la cantidad de estrategias probadas**. Correr muchas estrategias sin walk-forward real (`metodologia_validacion.md`) es la forma más rápida de autoengañarse, no de diversificar. Cuantas más estrategias, MÁS necesaria es la validación rigurosa, no menos.

## Decisión tomada (11/08/2026)

Antes de migrar la lógica custom de XAU (todavía no validada), se arranca con un sistema de reglas **públicas y probadas por décadas** (tipo Ed Seykota / turtle-trading: cruce de medias o breakout de canal), corriendo en paralelo sobre varios instrumentos/timeframes en NautilusTrader. Esto da una base de comparación honesta y la infraestructura real de portfolio-de-estrategias, sin todavía comparar contra la lógica propia de Jarvis (eso queda para después, a pedido explícito de Diego).

Sources: [Ivan Scherman — Fairvalue](https://www.fairvalue.es/blog-newsletter/iv%C3%A1n-scherman-el-trader-argentino-que-conquist%C3%B3-el-mundo-con-la-ia-y-el-an%C3%A1lisis-t%C3%A9cnico) · [Ivan Scherman — SciTech Investments](https://sci.tech/our-founder/) · [Multi-Strategy Hedge Funds Explained — CAIS](https://www.caisgroup.com/articles/an-introduction-to-multi-strategy-hedge-funds) · [The Structure of Modern Trading Firms — Young and Calculated](https://youngandcalculated.substack.com/p/the-structure-of-modern-trading-firms) · [Uncorrelated Assets and Strategies — Paperswithbacktest](https://paperswithbacktest.com/course/uncorrelated-assets-and-strategies)
