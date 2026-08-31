# Evidencia real: traders algorítmicos rentables y fracasos documentados

Investigación de agosto de 2026, a pedido explícito de Diego (13/08/2026): *"quiero que investigues la mayor parte de información que podamos usar de traders rentables algorítmicos, todo... para no caminar sobre caminos que ya caminaron otros y se equivocaron."* Complementa `traders_referentes.md` (perfiles de los grandes nombres) con dos cosas que faltaban ahí: **casos documentados de fracaso** (qué rompió a quién y por qué) y **un caso real de alguien en nuestra escala** (no un fondo de miles de millones), con números auditables.

---

## 1. El benchmark realista — no el de Renaissance

Renaissance/Medallion (66% anual antes de comisiones) es la referencia que todos citan, pero no es alcanzable a nuestra escala — depende de ventajas institucionales (datos propietarios, cientos de PhDs, infraestructura) que no están disponibles para un trader individual. Cita textual de Simons sobre su criterio de selección de activos, de una entrevista pública de 2000: *"If it's publicly traded, liquid and amenable to modeling, we trade it"* — simple en apariencia, pero detrás hay decenas de investigadores full-time. Fuentes: [Nurp — Jim Simons & Medallion Fund](https://nurp.com/algorithmic-trading-blog/jim-simons-medallion-fund-quantitative-trading/) · [QuantVPS — Jim Simons Trading Strategy](https://www.quantvps.com/blog/jim-simons-trading-strategy)

**El benchmark que sí es relevante para nosotros** es un caso real, documentado con números verificables, de alguien que empezó como nosotros — sin trasfondo de finanzas/matemática, aprendiendo solo — y sostuvo el esfuerzo 7 años:

### Caso Josh Malizzi — 7 años de investigación en trading algorítmico (retail, sin trasfondo financiero)

- **Resultado final, después de 7 años**: sobre futuros ES (E-mini S&P 500), **563 operaciones en 19+ años de backtest, 58% de acierto, Sharpe ratio 0,98 out-of-sample**. Esto es lo que se consigue con disciplina real y años de trabajo — no una fantasía, un número modesto y honesto.
- **Los primeros 3 años fueron de errores clásicos**: "combatir el data-mining bias" y "combatir el curve-fitting" — señales individuales que andaban espectacular en el backtest y fallaban en vivo. Exactamente el mismo patrón que ya documentamos con el XAU viejo (70%→38,5% WR).
- **El "desvío" de 2021-2022 hacia machine learning puro fracasó**: la relación señal-ruido tan baja de los datos financieros hace que los modelos de ML aprendan del ruido, no de la señal — el mismo problema que ya identificamos en `machine_learning_financiero.md` (López de Prado dice lo mismo, desde otra fuente completamente distinta).
- **Lo que sí funcionó**: no una sola estrategia "perfecta", sino un **sistema de votación por ensamble** — combinar muchas señales técnicas simples y no correlacionadas entre sí (genera ~3.000 señales sobre 36 mercados de futuros, las filtra estadísticamente, y combina las mejores no correlacionadas). Cita clave: "combinar muchos predictores malos no da un buen sistema" — la diversidad real (señales que no se mueven juntas) es lo que importa, no la cantidad.

**Por qué este caso es más útil que Renaissance para nosotros:** confirma, con un ejemplo real a nuestra escala, exactamente el camino que ya veníamos armando por lógica propia — walk-forward, anti-overfitting, no ML puro todavía, portfolio de estrategias simples y no correlacionadas en vez de una sola "genial". No es una coincidencia — es la misma conclusión a la que llega cualquiera que investiga esto en serio, desde ángulos distintos.

Fuente: [Lessons from 7 Years of Algorithmic Trading R&D — Josh Malizzi (Medium)](https://medium.com/@josh.malizzi/lessons-from-7-years-of-algorithmic-trading-research-and-development-c63f1d319831)

---

## 2. Por qué fracasan la mayoría (evidencia estadística, no anécdota)

- **Más del 90% de las estrategias académicas fracasan al pasar a capital real** — la brecha entre backtest y resultado real es la norma, no la excepción.
- **Regla práctica de la industria**: recortar el resultado in-sample a la mitad como estimación conservadora de lo que se puede esperar out-of-sample.
- **Causa #1 documentada**: overfitting y data-snooping por optimización de parámetros in-sample — lo mismo que venimos evitando toda la sesión.
- **Los costos de transacción destruyen resultados que parecían buenos** sin fricción — coincide con lo que ya vimos nosotros mismos al agregar comisiones al backtest de XAU 1H.

Fuentes: [Systematic Testing of Systematic Trading Strategies (ResearchGate)](https://www.researchgate.net/publication/323927874_Systematic_Testing_of_Systematic_Trading_Strategies) · [Predictive ability of technical trading rules — Springer](https://link.springer.com/article/10.1007/s11408-023-00433-2)

## 3. Fracasos famosos — qué rompió a quién (para no repetirlo)

| Caso | Qué pasó | Lección aplicable a Jarvis |
|---|---|---|
| **LTCM (1998)** | Apalancamiento 1:27 (US$125.000M de exposición sobre US$4.500M de capital). El modelo asumía que las correlaciones históricas no se rompen y que los precios convergen a "valor justo" — nunca fue programado para un escenario tipo default de Rusia. Perdió US$4.600M en 4 meses. | Nunca asumir que un escenario "nunca antes visto" no puede pasar — el modelo de riesgo tiene que sobrevivir a lo que nunca entrenó, no solo a lo que ya vio. Apalancamiento extremo multiplica cualquier error de modelo. |
| **Knight Capital (2012)** | Un bug de software (no de estrategia) en un despliegue de código causó pérdida de US$440M en 45 minutos. | No es solo la lógica de la estrategia lo que hay que auditar — el riesgo de *implementación/despliegue* es tan real como el de mercado. Ya tenemos la regla de nunca automatizar ejecución sin supervisión directa (`brokers_ejecucion.md`) — este caso es la prueba de por qué. |
| **"Quant Meltdown" de agosto 2007** | Varios fondos cuantitativos con estrategias supuestamente no correlacionadas perdieron simultáneamente cuando uno grande empezó a liquidar posiciones forzosamente. | "No correlacionado en backtest" no significa "no correlacionado en una crisis real" — en eventos de estrés, todo tiende a correlacionarse (el mismo problema que ya identificamos con el 2008 GFC y el 2022 bear market en XAU). |
| **COVID-19, marzo 2020** | Varias estrategias sistemáticas tuvieron su peor drawdown de la historia en semanas, por volatilidad extrema fuera de rango histórico. | Reforzar por qué probamos siempre ventanas de crisis específicas (ya lo hicimos con 2008) — un backtest de "años normales" no prueba nada sobre cómo se comporta la estrategia en el peor momento. |

Fuentes: [Lessons from Algo Trading Failures — LuxAlgo](https://www.luxalgo.com/blog/lessons-from-algo-trading-failures/) · [What Traders Can Learn From LTCM — Medium](https://medium.com/algorithmic-trading/what-traders-can-learn-from-the-long-term-capital-management-hedge-fund-collapse-1b1e013073f9) · [Knight Capital — CIO.com](https://www.cio.com/article/286790/software-testing-lessons-learned-from-knight-capital-fiasco.html)

---

## Conclusión — qué cambia esto en lo que veníamos planeando

**Nada de lo ya decidido queda invalidado — todo lo contrario, queda confirmado por una fuente completamente independiente.** El caso de Malizzi (7 años, resultado real 0,98 Sharpe) valida en la práctica lo que veníamos armando por lógica propia: walk-forward real, anti-overfitting, portfolio de señales simples y no correlacionadas antes que ML sofisticado, expectativas modestas y realistas (no el "5%/semana" que ya descartamos, no el 66% de Renaissance).

**Lo que sí se ajusta:**
1. **Expectativa de resultado recalibrada con un número real de alguien en nuestra escala**: Sharpe ~0,9-1,0 después de años de trabajo disciplinado es un objetivo realista, no una decepción.
2. **El objetivo no es "encontrar LA estrategia"** — es construir un portfolio de varias señales simples genuinamente no correlacionadas entre sí (no solo distintos parámetros de la misma idea). Esto cambia cómo hay que pensar el próximo paso: no buscar una sola estrategia "ganadora" para XAU, sino empezar a pensar en términos de ensamble desde temprano.
3. **Testear siempre contra ventanas de crisis específicas** (ya lo hacíamos con 2008) — confirmado como práctica necesaria, no opcional, por 3 casos históricos distintos (LTCM, 2007, COVID).
