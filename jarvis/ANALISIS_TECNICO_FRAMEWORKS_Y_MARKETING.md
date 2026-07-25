# Análisis técnico: Jarvis vs. frameworks de agentes + rediseño del agente de marketing

Fecha: 2026-07-04

---

## 1. Jarvis vs. cómo programan otros agentes financieros

| | Jarvis hoy | TradingAgents (LangGraph) | FinRobot (AutoGen) |
|---|---|---|---|
| Orquestación | Scripts Python secuenciales de ~500 líneas, ejecutados a mano | Grafo de estados con checkpoints persistentes | Conversación tipo chat entre agentes (GroupChat) |
| Memoria | Archivos `.md` editados a mano (`trading_analysis.md`, `strategy_notes.md`) | `~/.tradingagents/memory/trading_memory.md` — **casi idéntico al patrón que ya usa Jarvis** | Historial de conversación en RAM, sin persistencia nativa |
| Separación de código | Todo junto: patrones, riesgo e indicadores mezclados en `xau_v9.pine`/`backtest.py` | Config centralizado en `default_config.py` | Carpetas separadas: `agents/`, `data_source/` (un archivo por proveedor de datos), `functional/` (lógica pura) |

**Hallazgo validador**: el patrón de memoria en markdown que ya usás no es una improvisación rara — es literalmente lo que hace TradingAgents. No hace falta migrar eso.

**Paper más relevante — QuantAgent (arXiv 2509.09995)**: separa el trading en 4 agentes con roles fijos — `IndicatorAgent`, `PatternAgent`, `TrendAgent`, `RiskAgent`. Es casi un mapa 1:1 de lo que hoy hacés a mano y mezclado en un solo script Pine: detección de patrón de vela + estructura M3 (tendencia) + gestión de riesgo. La recomendación concreta: separar esa lógica en funciones/módulos independientes (ya estaba en el roadmap de la Fase 1, esto lo confirma con evidencia externa).

**Auditoría metodológica — Profit Mirage (arXiv 2510.07920)**: confirma que varios benchmarks de agentes financieros LLM tienen fuga de información temporal (look-ahead bias) que infla resultados — el mismo problema que ya identificamos en tu propio backtest (70%→38.5% WR sin cambios de código). Ni LangGraph ni CrewAI resuelven esto: es un problema de validación, no de framework.

### ¿Migrar a LangGraph / CrewAI / AutoGen?

**No.** Resuelven un problema que Jarvis no tiene (múltiples LLMs debatiendo en tiempo real con recuperación de fallos a media conversación). Tu uso es secuencial y episódico. El costo de mantenimiento de esos frameworks (versionado inestable, debugging de grafos/chats) no se paga para un usuario no-programador-profesional operando solo.

**Sí adoptar, gratis y sin dependencias nuevas:**
- Separar responsabilidades en archivos: `pattern_detector.py`, `risk_manager.py`, `indicators.py` dentro de `xau_strategy/` (patrón QuantAgent/FinRobot).
- Un solo `config.py` centralizado por módulo (API keys y parámetros sueltos hoy están dispersos en cada script).
- Mantener la memoria en `.md` — ya es el patrón correcto.

**Cuándo reconsiderar un framework**: si algún día querés que 2 modelos debatan una entrada (bull vs. bear) antes de operar. Hoy sería sobre-ingeniería.

---

## 2. Hallazgo crítico en el agente de marketing existente

Leyendo el código real de `jarvis/marketing/scripts/`:

- `market_daily.py`, `meta_optimizer.py`, `competitor_analyzer.py`, `viral_tracker.py` llaman a `client.messages.create()` con preguntas tipo *"tendencias marketing cirugía plástica Argentina 2026 qué está pasando ahora"* **sin ninguna herramienta de búsqueda real conectada**.
- Claude no tiene acceso a internet en vivo salvo que se le dé explícitamente la tool `web_search`. Estos scripts le piden al modelo "investigar" y "analizar competidores" sin datos reales — el resultado es contenido plausible pero **no verificado**, esencialmente alucinado con la fecha de corte del modelo, no información real de hoy.
- La única excepción parcial es `ad_library_scraper.py`, que sí intenta la Ad Library API real de Meta (requiere permiso especial) con fallback a generar la URL de búsqueda manual.

Esto es más grave que un gap de arquitectura — es un problema de **confiabilidad del output**: las "tendencias de hoy" y los "análisis de competidores" que lee Diego pueden estar inventados.

---

## 3. Qué agregar (orden de prioridad)

1. **Conectar `web_search` real** (tool de servidor de Anthropic) a los 4 scripts que hoy alucinan tendencias/competencia. Esto es el fix de mayor impacto del módulo de marketing.
2. Terminar la integración real de Meta Ad Library API (ya hay código parcial en `ad_library_scraper.py`) en vez de depender de que Diego revise URLs a mano.
3. Separar `marketing/scripts/` siguiendo el patrón `data_source/` (todo lo que trae datos externos: web_search, Meta API, WhatsApp API) vs. `functional/` (generación de copy, análisis, estrategia — lógica pura sobre datos ya obtenidos).
4. Aplicar el mismo criterio a trading: separar patrón/indicador/riesgo en módulos, como ya estaba planificado para la Fase 1.
