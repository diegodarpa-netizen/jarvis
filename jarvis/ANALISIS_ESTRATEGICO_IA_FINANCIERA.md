# Informe estratégico: cómo hacer de Jarvis el mejor analista financiero posible

Fecha: 2026-07-03

---

## 1. Qué tenés hoy (auditoría real de la carpeta)

### Trading XAU/USD — núcleo principal (avanzado, parcialmente automatizado)
Scalping intraday en oro. Dos capas: `xau_v9.pine` (Pine Script para TradingView) + `backtest.py` (motor Python sobre datos yfinance). Entrada por patrones de vela (Envolvente + START) sobre estructura M3. Objetivo del PDF base: 135 trades/24 semanas, 71% WR, 2.3R/semana.

**Resultados reales de los últimos 3 backtests:**

| Fecha | Trades | Win Rate | Total R | R/semana |
|---|---|---|---|---|
| 2026-06-07 | 20 | 70.0% | 6.6R | 1.65R |
| 2026-06-22 | 17 | 58.8% | 2.0R | 0.4R |
| 2026-07-01 | 13 | 38.5% | -3.5R | -1.17R |

El patrón START es fuerte (85.7% WR), el ENV es débil (33.3% WR) y arrastra el promedio. La caída de 70% a 38.5% WR en tres corridas sin cambios de código es la señal más importante del informe: el sistema **no está validado out-of-sample**, así que ese 70% no es confiable como expectativa futura.

### Estrategia OCC (abandonada a pesar de ser la más fuerte en papel)
Profit Factor 14.13, WR 79.2% sobre 33 años de histórico — pero con Delay=0 (repainting, resultados inflados). Con Delay=1 (real) el CAGR cae a 0.55%. Documentada en `rules.md`/`analysis.md` pero **nunca integrada** al código en vivo.

### Portfolio CEDEARs
`portfolio_tracker.py` + `active_positions.json`: 12 posiciones (~US$34.2k), conversión ARS→USD vía CCL con fallback. Funciona bajo demanda, sin rebalanceo ni alertas, y **totalmente desconectado** del riesgo de la mesa de XAU — podés tener drawdown simultáneo en ambos sin verlo.

### Marketing (clínica)
Agente Claude con tool use + knowledge base en markdown, uso episódico, sin feedback loop de resultados de campaña hacia la KB.

### Gaps concretos, priorizados

**Críticos (bloquean confiabilidad en vivo):**
1. Gray box dinámico no se recalcula durante impulsos fuertes → pierde entradas válidas.
2. ChOC no flipea a alcista tras impulsos alcistas → sesga el sistema a bajista todo el día.
3. Tolerancia de pullback ±5 pts vs. los ±3 que usa el trader humano de referencia (Fabian) → entradas prematuras.
4. Regla "primera vela de contacto / rechazo de cuerpo" (aprendida el 10/06) nunca se codificó.

**Altos:**
5. Sin walk-forward ni train/test split — el 70%→38.5% WR sin explicación lo confirma.
6. OCC con métricas superiores, cero integración.
7. Portfolio y trading XAU sin visión de riesgo unificada.
8. Datos históricos manuales (Dukascopy) desalineados con backtests en vivo (yfinance, 60 días).

---

## 2. Qué hacen otros "analistas financieros IA" (evidencia externa, 2024-2026)

| Proyecto | Arquitectura | Punto clave |
|---|---|---|
| **BloombergGPT** | Modelo monolítico 50B | Un solo LLM entrenado con datos propietarios; no toma decisiones, solo genera texto/análisis. |
| **FinGPT** (open source) | Modelo con fine-tuning liviano (LoRA) | Democratiza adaptar un LLM a finanzas, sigue siendo un modelo único. |
| **FinRobot** | Multi-agente en 4 capas | Agentes especializados por tarea, usa FinGPT como motor interno. |
| **TradingAgents** | Multi-agente (técnico, fundamental, sentiment, noticias → debate bull/bear → trader → risk manager → fund manager) | El más citado: mejoró retorno, Sharpe y drawdown vs. baselines, pero en ventana de backtest corta (ene-mar 2024). |
| **FinMem** | Agente único con memoria jerárquica | Superó a Buy&Hold y a modelos de RL en su propio benchmark. |
| **AI Hedge Fund (virattt, GitHub)** | Multi-agente con "personajes" (Buffett, Wood, Burry) + risk manager + portfolio manager | Educativo/experimental, sin auditoría de performance real. |
| **Numerai** | Miles de modelos ML independientes combinados en meta-modelo por ensamble | Evidencia de que ensamblar modelos diversos > un modelo único cerrado. Con capital institucional real detrás (JPMorgan). |
| **Danelfin** | Scoring de ~200 factores en 4 subscores | No es agéntico, es un score compuesto; resultados no auditados de forma independiente. |

**Lo que dice la evidencia sobre monolítico vs. modular:**
Meter precio + fundamentales + noticias + sentiment en un solo prompt/modelo degrada la precisión a medida que crece el contexto ("contaminación de contexto" — mismo fenómeno que describe Anthropic en su guía de context engineering). Separar en agentes especializados con contexto acotado por tarea evita ese degradado y permite auditar cada señal por separado. La contrapartida: la comunicación entre agentes en lenguaje natural puede perder información si el protocolo de debate/consenso está mal diseñado.

**El hallazgo más importante para vos — FINSABER (arxiv 2505.07078):**
Sobre 20 años y 100+ símbolos, las ventajas de estrategias LLM reportadas en papers de ventana corta **se diluyen o desaparecen**: son demasiado conservadoras en mercados alcistas y demasiado agresivas en bajistas. Esto es exactamente el patrón que ya viste en tus propios backtests (70% → 38.5% WR en semanas consecutivas). Más del 90% de estrategias académicas fallan al pasar a capital real.

**Datos alternativos que usan los sistemas serios más allá del precio:** sentiment de noticias/redes vía NLP, put/call ratio y actividad de opciones, datos macro, on-chain (para cripto). JPMorgan (2024): fondos que incorporan datos alternativos ganan ~3% más de retorno anual; 67% de gestores ya los usan.

---

## 3. La pregunta central: ¿toda la info en un solo cerebro, o partes especializadas?

**Respuesta corta: partes especializadas que se combinan con reglas simples de votación/veto — no un cerebro único.** Tres razones, con evidencia:

1. **La arquitectura ganadora en la literatura reciente es modular** (TradingAgents, FinRobot). Separar técnico/sentiment/riesgo reduce la contaminación de contexto y te permite auditar cada señal — algo que ya necesitás hoy, porque tu Pine Script tiene reglas propias que hay que poder inspeccionar, no una caja negra.
2. **Tu problema real no es "falta de inteligencia", es overfitting de ventana corta** — lo prueba FINSABER con datos duros y lo confirma tu propio 70%→38.5% WR. Un módulo de risk management separado, que vote/filtre independiente de la señal de entrada, es el control estructural contra ese sesgo (igual que ya hace, en parte, tu estructura M3).
3. **Con recursos limitados no hace falta replicar Numerai ni entrenar un BloombergGPT propio.** El patrón de mejor costo-beneficio es imitar TradingAgents/FinRobot a escala chica: 2-3 agentes especializados que ya tenés la mitad construidos.

---

## 4. Roadmap concreto para Jarvis (orden de prioridad)

**Fase 1 — Arreglar antes de agregar nada (crítico):**
- Corregir gray box dinámico y ChOC flip en `xau_v9.pine`.
- Bajar tolerancia de pullback a ±3 pts.
- Codificar la regla de "vela de rechazo" aprendida el 10/06.
- Implementar walk-forward real (train/test split) en `backtest.py` antes de confiar en cualquier % de WR.

**Fase 2 — Arquitectura modular (adoptar el patrón TradingAgents/FinRobot a escala chica):**
- **Agente técnico**: lo que ya tenés en Pine/backtest.py (estructura M3, patrones de vela).
- **Agente de riesgo**: separado del agente técnico, con veto — no ejecuta si el portfolio de CEDEARs ya está en drawdown, o si hay eventos de noticias de alto impacto (`rules/noticias.md` ya existe, falta conectarlo).
- **Agente de sentiment/noticias**: liviano, vía LLM, para XAU (oro reacciona fuerte a Fed/DXY/geopolítica) — no hace falta entrenar nada, un prompt bien armado sobre noticias recientes alcanza.
- Reglas de consenso simples (ej: el agente técnico propone, el de riesgo puede vetar, el de sentiment ajusta el tamaño de posición) — no necesitás un debate bull/bear completo como TradingAgents, es overkill para tu escala.

**Fase 3 — Unificar el riesgo del portfolio completo:**
- Dashboard único que combine exposición XAU + CEDEARs, para evitar drawdown simultáneo invisible.
- Reactivar OCC con Delay=1 real como estrategia complementaria (no reemplazo) en otro instrumento/timeframe, ya que su edge es distinto al de xau_v9.

**Fase 4 — Aprendizaje continuo real:**
- Versionar los archivos de memoria (`strategy_notes.md`, `trading_analysis.md`) con timestamp y diff de qué regla se probó cuándo, en vez de edición manual sin historial.
- Cerrar el loop: cada sesión en vivo que genere un aprendizaje nuevo (como el del 10/06) debe traducirse en un test automático que verifique que el código lo implementa, no solo quedar en un `.md`.

---

## 5. Conclusión

No es cuestión de "meter toda la información posible" en un solo lugar — la evidencia (propia y externa) dice lo contrario: la contaminación de contexto y el overfitting de ventana corta son justamente los dos problemas que ya tenés. La mejora de mayor impacto no es agregar más datos o una IA más grande, es (a) arreglar los bugs de estructura que ya identificaste en vivo, (b) validar con walk-forward antes de confiar en un backtest, y (c) modularizar en 2-3 agentes especializados con veto de riesgo — el mismo patrón que usan los sistemas más citados de 2024-2026, adaptado a tu escala de usuario individual.
