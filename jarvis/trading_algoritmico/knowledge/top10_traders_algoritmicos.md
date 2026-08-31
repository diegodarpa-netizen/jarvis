# Los 10 mejores traders/firmas algorítmicas del mundo — método y fracasos documentados

Investigación de agosto de 2026, a pedido explícito de Diego (13/08/2026): *"investigá a cada uno de ellos por separado, quiero saber todo... y qué cosas fueron las que fallaron."* Completa `traders_referentes.md` (perfiles generales) y `evidencia_traders_rentables_y_fracasos.md` (fracasos famosos por evento) con un tratamiento individual — método + track record + fracaso específico, uno por uno.

---

## 1. Jim Simons — Renaissance Technologies (Medallion)

**Método:** patrones estadísticos en datos masivos, ejecutado sin discreción humana, con matemáticos/físicos/criptógrafos en vez de perfiles tradicionales de Wall Street. Criterio de selección de activos, textual de una entrevista de 2000: *"If it's publicly traded, liquid and amenable to modeling, we trade it."*

**Track record:** Medallion, ~66% anual antes de comisiones (1988-2021) — el mejor track record sostenido de la industria cuantitativa. Pero es un fondo **cerrado a inversores externos desde 2005** — solo opera con capital de empleados.

**Lo que falló — y es la lección más importante de todo este archivo:** los fondos *públicos* de Renaissance (RIEF, RIDA, RIDGE, abiertos a inversores externos) tuvieron años terribles — en un año, RIEF y RIDA perdieron 19,9% y 31,9% **el mismo año que Medallion cerró +76%**. Los activos bajo gestión de esos fondos públicos cayeron de US$35.800M a menos de US$20.000M. **La estrategia que funciona a la perfección en un contexto (capital propio, cerrado, sin presión de rescates) no se traslada automáticamente a otro (capital de terceros, abierto, con salidas de inversores en pánico).**

Fuentes: [Nurp — Jim Simons & Medallion Fund](https://nurp.com/algorithmic-trading-blog/jim-simons-medallion-fund-quantitative-trading/) · [Renaissance Technologies' External Hedge Funds Shrink — Rebellion Research](https://www.rebellionresearch.com/renaissance-technologies-external-hedge-funds-shrink)

---

## 2. Ed Seykota — pionero del trend-following sistemático

**Método:** sistemas de reglas simples, cortar pérdidas rápido, dejar correr ganancias, apostar 1-2% del capital por operación para sobrevivir rachas perdedoras sin drawdowns catastróficos.

**Track record:** convirtió US$5.000 en más de US$15.000.000 en 12 años (~60% anual).

**Lo que falló:** el propio Seykota reportó drawdowns de 30-40% en algunos períodos — su sistema **funcionaba matemáticamente pero muchos de sus clientes no toleraron psicológicamente sostener esas caídas, y se retiraron justo antes de la recuperación.** Su conclusión, textual en espíritu: el fracaso de un sistema tiene más que ver con la incompatibilidad psicológica del trader con lo que el sistema exige, que con fallas del sistema en sí. Por eso fundó en 1992 el "Trading Tribe Process" — un espacio específico para trabajar el componente psicológico de sostener un sistema ganador durante sus peores rachas.

**Aplicable a Jarvis:** confirma por qué la disciplina de no tocar la estrategia en medio de un drawdown (que ya tenemos como regla) es tan crítica — el sistema no falla por matemática, falla por abandono humano en el peor momento.

Fuentes: [Ed Seykota — QuantifiedStrategies](https://www.quantifiedstrategies.com/ed-seykota-trading-strategies/) · [Ed Seykota — Trends and Breakouts](https://trendsandbreakouts.com/ed-seykota)

---

## 3. David E. Shaw — D.E. Shaw & Co.

**Método:** computación paralela sofisticada para explotar ineficiencias de microestructura de mercado, desde 1988.

**Track record:** 18% anual promedio 1988-1996 con baja volatilidad; recuperado después de su crisis a 12,7% anualizado en 23 años.

**Lo que falló — con números concretos:** en la crisis de 1998 (colapso de LTCM + default ruso), **la operación de arbitraje estadístico de Shaw perdió el 73% de su capital ese año**, con ~US$200M de pérdidas propias y US$372M reportados por BankAmerica en el joint venture conjunto. La firma despidió al 25% de su plantilla (264 personas) y vendió unidades de negocio no centrales. Volvió a ser golpeado (aunque menos que otros) en el "quant quake" de agosto 2007, con su fondo compuesto cayendo un récord de 5% en un mes.

**Aplicable a Jarvis:** el mismo patrón que LTCM (ya documentado en `evidencia_traders_rentables_y_fracasos.md`) — un modelo de arbitraje que asume que las relaciones históricas se mantienen, se rompe exactamente cuando hay un shock de liquidez sistémico sin precedente en los datos de entrenamiento.

Fuentes: [D.E. Shaw's 1998 Crisis — Medium](https://medium.com/@navnoorbawa/d-e-shaw-s-1998-crisis-how-a-372-million-loss-built-a-65-billion-quant-giant-b15c6bac91cd) · [D. E. Shaw & Co. — Wikipedia](https://en.wikipedia.org/wiki/D._E._Shaw_%26_Co.)

---

## 4. Ken Griffin — Citadel

**Método:** múltiples estrategias (crédito, acciones, commodities) corriendo en paralelo, con apalancamiento significativo.

**Track record:** una de las plataformas multiestrategia más grandes y longevas del mundo.

**Lo que falló:** en 2008, **los fondos insignia de Citadel cayeron 55%** — la exposición pesada a bonos convertibles se derrumbó tras la caída de Lehman Brothers, agravada por el apalancamiento alto. Griffin admitió después que estuvieron a un pelo de cerrar del todo. Inversores pidieron retirar US$1.500M de los fondos insignia.

**La corrección posterior es la parte más valiosa:** antes de 2008, Griffin y su equipo se dieron cuenta de que **no podían distinguir habilidad de suerte** en sus resultados de stock-picking — la solución fue una construcción de portafolio más estructurada (mezcla deliberada de empresas de distinto tamaño/momentum para maximizar riesgo idiosincrático, no concentrado). Hoy Griffin sostiene explícitamente que la IA pura no puede reemplazar el juicio humano en mercados, y aboga por combinar "algoritmos basados en datos" con criterio humano experimentado.

**Aplicable a Jarvis:** la lección de "no podíamos distinguir habilidad de suerte" es exactamente el problema de overfitting que perseguimos evitar todo el proyecto — y la corrección (estructura de portafolio deliberada, no concentración) es la misma línea que venimos siguiendo con diversificación entre activos no correlacionados.

Fuentes: [Ken Griffin Navigates A Flock Of Black Swans — Forbes](https://www.forbes.com/sites/maneetahuja/2022/04/01/billionaire-trader-ken-griffin-navigates-a-flock-of-black-swans/) · [Citadel's struggle to survive — Fortune 2008](https://archive.fortune.com/2008/12/08/news/companies/citadel_vickers.boyd.fortune/index.htm)

---

## 5. Peter Muller — PDT Partners (ex Morgan Stanley)

**Método:** arbitraje estadístico con modelos propietarios ("caja negra", poco se sabe públicamente de los detalles), asignando capital dinámicamente entre distintas sub-estrategias.

**Track record:** el fondo PDT Partners **nunca tuvo un año negativo** desde su spin-out de Morgan Stanley en 2012 (según reportes hasta 2016) — 18,5% anualizado neto desde el inicio, +21,5% en los primeros 11 meses de 2015.

**Lo que falló:** acá hay que ser honesto con la limitación de la investigación — **no encontré ningún fracaso o pérdida grande documentada públicamente para PDT específicamente.** Esto puede significar dos cosas: (a) genuinamente no tuvieron un evento de pérdida grave reportable, o (b) al ser un fondo muy cerrado (poco se sabe de sus modelos), la información simplemente no es pública. No asumir que "nunca falló" es lo mismo que "es infalible" — es más honesto decir que no tenemos evidencia de fracaso, no que no exista.

Fuentes: [The New Quant Hedge Fund Master — Forbes](https://www.forbes.com/sites/nathanvardi/2016/01/04/the-new-quant-hedge-fund-master/) · [PDT Partners — Wikipedia](https://en.wikipedia.org/wiki/PDT_Partners)

---

## 6. Cliff Asness — AQR Capital Management

**Método:** factor investing sistemático a escala institucional (momentum, value) — popularizó estos factores como estrategias replicables, no solo teoría académica.

**Track record:** uno de los gestores cuantitativos más influyentes en popularizar factor investing; llegó a gestionar US$226.000M en activos (pico 2018).

**Lo que falló — con números concretos, año por año:** el llamado **"quant winter" de 2018-2021**. El fondo Absolute Return perdió ~12% en 2018, más de 5% en 2019, y **22% en 2020 (su peor año)**. Los activos bajo gestión cayeron de US$226.000M a US$137.000M (~40% de caída), con despidos del 5-10% de la plantilla dos años seguidos. Un reporte de la competencia (Man Numeric) criticó a los quants del sector por **no adaptarse a cambios estructurales** (cambio climático, cambios demográficos, integración tecnológica) y depender de patrones históricos que dejaron de repetirse.

**Aplicable a Jarvis:** es la prueba más clara de que **ningún factor/patrón es permanente** — lo que funcionó 10-15 años puede dejar de funcionar sin aviso, y el tamaño de la firma no protege contra esto. Refuerza por qué monitoreamos walk-forward de forma continua, no una sola vez.

Fuentes: [Cliff Asness Has Steered AQR Through Three Quant Crises — Institutional Investor](https://www.institutionalinvestor.com/article/2dqsr456gmu55p19gxiio/corner-office/cliff-asness-has-steered-hedge-fund-aqr-through-not-one-not-two-but-three-quant-crises) · [AQR Cuts Jobs After Assets Decline — Bloomberg](https://www.bloomberg.com/news/articles/2020-01-08/aqr-capital-cuts-jobs-after-quant-firm-sees-assets-decline)

---

## 7. John Overdeck y David Siegel — Two Sigma

**Método:** IA, machine learning y computación distribuida para generar señales de trading a escala.

**Track record:** uno de los quant funds más grandes del mundo, gestión multi-modelo sofisticada.

**Lo que falló — este es distinto a todos los anteriores, es una falla de gobernanza, no de mercado:** en 2023 se descubrió que **un solo investigador había estado modificando modelos de trading sin autorización durante casi 2 años**, para inflar su propia compensación (llegó a cobrar US$23M). El resultado fue un impacto asimétrico: algunos fondos de clientes ganaron de más (US$400M) mientras otros perdieron (US$165M) — **todo por la misma falla de gobernanza**. Two Sigma pagó US$90M en multas regulatorias y devolvió US$165M a clientes afectados. Una vulnerabilidad identificada ya en 2019 quedó sin resolver más de 4 años, permitiendo modificaciones no autorizadas en 14 modelos distintos. Además, la pelea entre los propios fundadores llegó a citarse como "riesgo material" en una presentación regulatoria.

**Aplicable a Jarvis:** ningún modelo, por sofisticado que sea, sirve sin **control de cambios y auditoría** — quién puede tocar qué parámetro, cuándo, y por qué. Es un tipo de riesgo completamente distinto al de mercado (riesgo operacional/de gobernanza) y tan real como cualquier otro.

Fuentes: [The $400M Gain, $165M Loss — Two Sigma's Model Governance Failures (Medium)](https://medium.com/@navnoorbawa/the-400m-gain-165m-loss-how-two-sigmas-model-governance-failures-created-asymmetric-p-l-impact-5f78edc8ebf8) · [Two Sigma cofounders material risk — Fortune](https://fortune.com/2023/06/20/two-sigma-cofounders-hedge-fund-material-risk)

---

## 8. Ivan Scherman — SciTech Investments

Ya cubierto en profundidad en `traders_referentes.md` — track record real de 23% anual/17 años (fondo de clientes) vs. ~500% en la competencia World Cup 2023 (cuenta propietaria de riesgo extremo, no comparable). Lección clave ya documentada: "solo la buena gestión del riesgo permite ganancias sostenidas."

---

## 9. Thomas Peterffy — pionero histórico, fundador de Interactive Brokers

**Método:** fue el primero en aplicar un modelo matemático computarizado para valuar opciones en tiempo real (1977), y **construyó el primer sistema de trading algorítmico totalmente automatizado en 1987** (una computadora conectada a una terminal de Nasdaq que colocaba órdenes más rápido que cualquier humano).

**Anécdota histórica que vale la pena guardar** (no es una falla, es ingenio regulatorio): cuando Nasdaq le exigió que las órdenes se tipearan manualmente, Peterffy construyó **un robot con dedos de goma que tipeaba tan rápido que sonaba como ametralladora** — cumplía la regla al pie de la letra ("hay que tipear") sin perder la velocidad.

**Lo que falló:** su propia operación de market-making automatizado terminó siendo **exprimida por competidores de alta frecuencia más rápidos que él mismo** — en marzo de 2017 anunció el cierre parcial de esa operación, ya insostenible frente a la competencia de HFT. Se reinventó pasando al negocio de bróker de descuento (Interactive Brokers), que sigue siendo su negocio principal hoy.

**Aplicable a Jarvis:** hasta el pionero histórico de la velocidad terminó superado en velocidad — es la prueba de que competir por latencia pura (HFT) no es sostenible para nadie que no invierta a escala industrial en infraestructura; confirma nuestra decisión de no ir por ese camino.

Fuentes: [Father of Algorithmic Trading Seeks Speed Controls — Traders Magazine](https://www.tradersmagazine.com/news/father-of-algorithmic-trading-seeks-speed-controls/) · [Thomas Peterffy — Forbes](https://www.forbes.com/profile/thomas-peterffy/)

---

## 10. Nunzio Tartaglia — el origen histórico del stat-arb (Morgan Stanley, años 80)

**Quién era:** ex sacerdote jesuita con PhD en física — el "abuelo" de todos los nombres de esta lista que hacen arbitraje estadístico.

**Método:** a mediados de los 80, armó en Morgan Stanley el primer equipo de físicos, matemáticos e informáticos de Wall Street para buscar arbitraje en acciones — inventaron el **pairs trading** (encontrar dos acciones históricamente correlacionadas, apostar cuando su precio diverge de esa relación).

**Track record:** su equipo generó ~US$50M de ganancia para Morgan Stanley en 1987 con esta técnica, entonces completamente nueva.

**Por qué importa para esta lista, más allá de él mismo:** su equipo formó a **Peter Muller (#5 de esta lista) y David Shaw (#3 de esta lista)** — ambos empezaron ahí antes de fundar sus propias firmas. Es el nodo histórico que conecta directamente a 3 de los 10 nombres de esta lista — la disciplina de stat-arb que hoy es estándar en toda la industria nació literalmente de este único grupo.

Fuentes: [The History and Evolution of Quantitative Finance — Medium](https://medium.com/the-financial-journal/the-history-and-evolution-of-quantitative-finance-1980s-2a4eb1f49b52) · [Comprehensive Introduction to Pairs Trading — Hudson & Thames](https://hudsonthames.org/definitive-guide-to-pairs-trading/)

---

## Bonus — un modelo distinto que vale la pena conocer: Igor Tulchinsky (WorldQuant)

No es de los "10 mejores" por track record público, pero es un **modelo de organización completamente distinto** a los otros 9: en vez de un equipo cerrado de PhDs, WorldQuant creó una plataforma de investigación **crowdsourceada** (BRAIN) donde miles de personas en todo el mundo (14.000+ en un solo concurso) compiten armando señales ("alphas") por premios en dinero. Tulchinsky fundó además una universidad online gratuita y acreditada (WorldQuant University) para formar talento cuantitativo sin costo. Filosofía textual: "el talento está distribuido parejo en el mundo, la oportunidad no." Es el modelo opuesto al "equipo secreto y cerrado" de Renaissance o PDT.

Fuente: [WorldQuant — Wikipedia](https://en.wikipedia.org/wiki/WorldQuant) · [Igor Tulchinsky — Grokipedia](https://grokipedia.com/page/Igor_Tulchinsky)

---

## Síntesis — patrones que se repiten en los fracasos (no en los aciertos)

Cruzando los 10 casos, los fracasos NO vienen del lado de "la estrategia matemática estaba mal" — vienen de:

1. **Apalancamiento excesivo amplificando un shock no visto en el entrenamiento** (Shaw 1998, Citadel 2008, LTCM ya documentado aparte).
2. **Un producto/contexto distinto al que validó la estrategia** (Medallion vs. fondos públicos de Renaissance — la misma "receta" no sobrevive el traslado a otro tipo de capital).
3. **Psicología humana abandonando el sistema en el peor momento**, no el sistema fallando matemáticamente (Seykota).
4. **Falta de control/gobernanza sobre quién puede tocar el modelo**, un riesgo completamente aparte del riesgo de mercado (Two Sigma 2023).
5. **El mercado cambiando de régimen de forma permanente**, no cíclica (AQR, "quant winter").
6. **Ser superado en velocidad por quien invierte más en infraestructura** — nadie es inmune, ni el pionero histórico (Peterffy).

Ninguno de estos 6 patrones es "la matemática estaba mal" — todos son de **gestión de riesgo, gobernanza, psicología o contexto**. Confirma, por sexta vez distinta en esta sesión, la misma conclusión de fondo: la ventaja no está en encontrar una fórmula secreta, está en sobrevivir el tiempo suficiente sin quebrar por alguno de estos 6 motivos.
