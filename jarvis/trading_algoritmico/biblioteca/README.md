# Biblioteca de referencia — los 6 libros más influyentes de trading algorítmico

Carpeta para consultar cuando tengamos dudas de base — antes de probar algo nuevo, mirar acá primero si ya está respondido.

**No contiene los PDFs de los libros** — son textos comerciales con copyright activo (Jarvis tiene prohibido bajar de fuentes no autorizadas, sin excepción). Contiene: la ficha de cada libro para comprarlo legal si Diego quiere el texto completo, y una síntesis propia de los conceptos centrales de cada uno — la parte que realmente se usa día a día para resolver dudas.

Elegidos cruzando dos búsquedas independientes (no la lista de un solo blog) — los que se repiten en fuentes serias como los más recomendados por practicantes reales, no marketers.

**Actualización 13/08/2026:** se agregó un 6º libro (`0. Ernest Chan — Quantitative Trading`) que faltaba — es la guía de *arranque* (cómo definir tu perfil de trader y elegir estrategia), distinta del libro de Chan que ya estaba (el técnico, de estrategias concretas). Ver `../knowledge/como_empezar.md` para el roadmap completo armado a partir de este hueco.

---

## 0. Ernest Chan — *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2ª ed., 2021)

**ISBN:** 978-1119800064 | **Editorial:** Wiley | [Amazon](https://www.amazon.com/Quantitative-Trading-Build-Algorithmic-Business/dp/1119800064) · [Wiley](https://www.wiley.com/en-us/Quantitative+Trading:+How+to+Build+Your+Own+Algorithmic+Trading+Business,+2nd+Edition-p-9781119800064)

**Por qué es el 0 y no el 1:** no es un libro de estrategias — es la guía de **cómo arrancar**, organizada capítulo a capítulo alrededor de los pasos a seguir, no de la técnica. Es el libro que nos faltaba y que motivó esta actualización (13/08/2026, a pedido de Diego: *"antes de eso [analizar datos] es saber sobre trading algorítmico"*).

**Qué enseña (estructura, vía catálogo de biblioteca — no el texto):**
- Cap. 1 — "The Whats, Whos, and Whys of Quantitative Trading": quién puede ser trader cuantitativo, el caso de negocio (escalabilidad, demanda de tiempo, no hace falta marketing).
- Cap. 2 — "Fishing for Ideas": cómo identificar una estrategia que **te quede bien a vos** — según horas disponibles, nivel de programación, capital, objetivo. Este es el capítulo que estábamos saltando.
- El resto del libro sigue el orden: backtesting → automatización de ejecución → gestión de riesgo/capital, con foco en trader independiente (no institucional).

**Consejo del propio Chan, de entrevistas públicas gratuitas** (no del libro): empezar simple — literalmente con Excel antes que Python — y con la estrategia más básica posible, porque como trader independiente no podés competir en complejidad con un banco grande; en su propia experiencia, quedarse con lo más simple fue lo rentable. También insiste en clasificar primero si el mercado/activo es *mean-reverting* o *momentum-driven* antes de probar nada — evita testear a ciegas. [Fuente: Better System Trader — entrevista Ep. 012](https://bettersystemtrader.com/012-ernest-chan/)

---

## 1. Ernest Chan — *Algorithmic Trading: Winning Strategies and Their Rationale* (2013)

**ISBN:** 978-1118460146 | **Editorial:** Wiley | [Amazon](https://www.amazon.com/Algorithmic-Trading-Winning-Strategies-Rationale/dp/1118460146) · [Goodreads](https://www.goodreads.com/book/show/16144886-algorithmic-trading)

**La frase que resume su aporte central:** *"La mayoría de los traders gasta 90% del tiempo optimizando estrategias y 10% generándolas. Debería ser al revés."*

**Qué enseña:**
- El proceso completo de armar una estrategia, de punta a punta, con ejemplos de código reales (mean-reversion, momentum, pares cointegrados).
- La importancia de partir de una **hipótesis con lógica económica** — no minar datos hasta que aparezca un patrón (data mining puro), sino tener una razón de por qué algo debería funcionar antes de testearlo.
- Cómo evaluar si una estrategia es viable en la práctica (costos de transacción, capacidad, apalancamiento) — no solo si el backtest da bien.

**Por qué lo elegimos:** es el punto de entrada más práctico y menos académico de los 5 — el que mejor conecta con lo que ya venimos haciendo en `jarvis/trading_algoritmico/`.

---

## 2. Marcos López de Prado — *Advances in Financial Machine Learning* (2018)

**ISBN:** 978-1119482086 | **Editorial:** Wiley | [Amazon](https://www.amazon.com/Advances-Financial-Machine-Learning-Marcos/dp/1119482089) · [Sitio del autor](https://www.quantresearch.org/)

**Quién es:** el mismo autor del paper (con Bailey, Borwein y Zhu) sobre sobreajuste de backtests que ya citamos en la sesión de hoy — la referencia de "pasados los ~50 tests sobre el mismo dato, el riesgo de sobreajuste se dispara".

**Qué enseña:**
- Metodología rigurosa para no engañarse a uno mismo con un backtest — validación cruzada específica para series de tiempo financieras (el método estándar de ML no aplica directo, porque los datos financieros están correlacionados en el tiempo).
- Cómo etiquetar datos financieros correctamente para entrenar modelos (el "triple-barrier method").
- Gran parte de su trabajo académico (papers, no el libro) está publicado gratis y legal en [SSRN](https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=434076) — recurso real y gratuito si se necesita profundizar sin comprar el libro.

**Por qué lo elegimos:** es la base teórica de todo lo que hicimos hoy sobre walk-forward y sobreajuste — no lo inventamos nosotros, viene de acá.

---

## 3. Perry Kaufman — *Trading Systems and Methods* (múltiples ediciones, ~1.200 páginas)

**ISBN (última edición):** 978-1119606090 | **Editorial:** Wiley | [Amazon](https://www.amazon.com/Trading-Systems-Methods-Wiley/dp/1119606098)

**Quién es:** el mismo autor del **Efficiency Ratio** que ya usamos hoy como filtro de tendencia (`knowledge/filtros_de_tendencia.md`) — no es una referencia lejana, es una herramienta que ya está en nuestro código.

**Qué enseña:**
- Es la "enciclopedia" — cataloga y explica prácticamente todos los tipos de sistemas técnicos que existen (tendencia, reversión, volatilidad, estacionalidad), con la matemática de cada uno.
- Sirve como diccionario de referencia más que como lectura de principio a fin — ideal para cuando aparece un indicador nuevo y hay que entender qué es y de dónde viene.

**Por qué lo elegimos:** es la fuente primaria de gran parte del vocabulario técnico que ya venimos usando.

---

## 4. David Aronson — *Evidence-Based Technical Analysis* (2006)

**ISBN:** 978-0470008744 | **Editorial:** Wiley | [Amazon](https://www.amazon.com/Evidence-Based-Technical-Analysis-Scientific-Statistical/dp/0470008741) · [Resumen — Synapse Trading](https://synapsetrading.com/evidence-based-technical-analysis-david-aronson/)

**Qué enseña:**
- Aplicar el método científico y la inferencia estadística a señales de trading — separar objetivamente **habilidad de suerte**, en vez de "esto se parece a un patrón que funcionó antes".
- Reglas objetivas y cuantificables en vez de patrones subjetivos de manual (el problema clásico del análisis técnico tradicional: dos personas miran el mismo gráfico y ven cosas distintas).

**Por qué lo elegimos:** es el fundamento filosófico/metodológico de por qué insistimos tanto hoy en no elegir "lo que se ve bien" — viene directo de acá.

---

## 5. Rishi Narang — *Inside the Black Box: A Simple Guide to Quantitative and High-Frequency Trading* (3ª edición, 2013)

**ISBN:** 978-1118416824 | **Editorial:** Wiley | [Amazon](https://www.amazon.com/Inside-Black-Box-Quantitative-Trading/dp/1118416823)

**Qué enseña:**
- Cómo funciona un fondo cuantitativo real por dentro — no solo la estrategia, sino la arquitectura completa: generación de señal, gestión de riesgo (con veto independiente, el mismo patrón que ya investigamos con Ivan Scherman), construcción de portfolio, ejecución.
- Es el único de los 5 escrito para explicar el **negocio** completo, no solo la técnica — conecta con la pregunta de "cómo eligen los activos los profesionales" que ya investigamos.

**Por qué lo elegimos:** completa a los otros 4 (todos más técnicos) con la vista de negocio/estructura — el "por qué" institucional detrás de las reglas técnicas.

---

## Cómo usar esta carpeta

Cuando tengamos una duda de base (¿por qué walk-forward? ¿qué es esto que estoy viendo en el gráfico? ¿cómo se llama esta técnica?) — mirar acá primero antes de investigar de cero. Si la síntesis no alcanza y Diego quiere el texto completo de alguno, están los links de compra legal arriba.
