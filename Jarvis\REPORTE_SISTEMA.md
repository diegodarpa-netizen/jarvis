# Jarvis — Reporte del Sistema
**Versión MVP · Mayo 2026**
*Documento interno — Nahuel Divano*

---

## 1. Qué es Jarvis

Jarvis es un asistente financiero personal construido sobre Claude Code Desktop. No es una aplicación web ni una app móvil — es un entorno de trabajo inteligente donde el usuario opera en lenguaje natural y Jarvis ejecuta análisis, scripts y búsquedas de forma autónoma en el fondo.

La interfaz es Claude Code. El cerebro es Claude. Los datos vienen de Yahoo Finance + Alpha Vantage + NewsAPI. La automatización (reportes automáticos por email) puede integrarse con n8n en una fase posterior.

---

## 2. Arquitectura del sistema

```
Usuario habla con Claude Code Desktop
         │
         ▼
   CLAUDE.md (cargado automáticamente al abrir la carpeta)
   Define identidad, flujos, scripts disponibles y reglas de comportamiento
         │
         ▼
┌─────────────────────────────────────────┐
│              JARVIS (Claude)            │
│  Interpreta el pedido del usuario,      │
│  decide qué scripts ejecutar y en       │
│  qué orden, sintetiza los resultados    │
│  y presenta el análisis final           │
└────────────┬────────────────────────────┘
             │ ejecuta vía bash
    ┌────────┴────────┐
    │  SCRIPTS PYTHON  │
    └────────┬────────┘
             │ consultan
    ┌────────┴──────────────────────────────────┐
    │              FUENTES DE DATOS             │
    │  Yahoo Finance (yfinance)  — principal    │
    │  Alpha Vantage News API    — histórico    │
    │  NewsAPI                   — opcional     │
    │  Web Search (Claude nativo)— research     │
    └───────────────────────────────────────────┘
             │ guarda en
    ┌────────┴──────────────────┐
    │        ARCHIVOS LOCALES   │
    │  jarvis/portfolio/        │
    │  jarvis/charts/           │
    │  jarvis/reports/          │
    └───────────────────────────┘
```

---

## 3. Componentes del sistema

### 3.1 Scripts Python

#### `fetch_market.py` — Datos de mercado
**Fuente**: Yahoo Finance (sin API key)

- Precio actual y variación diaria
- Histórico OHLCV para cualquier período (1d a max)
- Fundamentals: PE, PB, PS, ROE, márgenes, deuda, FCF
- Analistas: target price, consenso, número de analistas
- Info de empresa: sector, industria, empleados, descripción
- Estados financieros: income statement, balance sheet, cashflow

```bash
python jarvis/scripts/fetch_market.py AAPL --period 1y --info
python jarvis/scripts/fetch_market.py SPY --period 5d --no-history
```

---

#### `fetch_news.py` — Noticias financieras con tres capas
**Fuentes**: Yahoo Finance (base) + Alpha Vantage (histórico + sentimiento) + NewsAPI (opcional)

| Fuente | Cobertura | Key requerida |
|---|---|---|
| Yahoo Finance | Últimas 2-4 semanas | No |
| Alpha Vantage | Hasta 12 meses + sentimiento por artículo | Sí (gratuita) |
| NewsAPI | Últimos 30 días | Sí (gratuita) |

Parámetro `--days` para extender la búsqueda histórica (solo aplica con Alpha Vantage activo).

Cada artículo de Alpha Vantage incluye:
- `sentiment`: Alcista / Levemente alcista / Neutral / Levemente bajista / Bajista
- `sentiment_score`: float entre -1.0 (muy bajista) y 1.0 (muy alcista)

```bash
python jarvis/scripts/fetch_news.py NVDA --limit 20 --days 180
python jarvis/scripts/fetch_news.py MARKET --limit 15
```

---

#### `analyze_company.py` — Pipeline completo de análisis
En un solo llamado ejecuta en secuencia:
1. Precio e histórico
2. Fundamentals completos
3. Análisis técnico: MA20/50/200, RSI-14, tendencia, señales
4. Valuación: PE trailing/forward, PB, PS, PEG, EV/EBITDA, upside de analistas
5. Salud financiera: deuda/EBITDA, márgenes, ROE, crecimiento, FCF
6. Noticias recientes
7. Gráfico candlestick
8. Resumen ejecutivo JSON

```bash
python jarvis/scripts/analyze_company.py NVDA --period 1y
python jarvis/scripts/analyze_company.py TSLA --period 6mo --no-chart
```

---

#### `market_briefing.py` — Briefing diario del mercado
Fetch paralelo (multithreading) de todos los activos:

- **Índices**: S&P 500, NASDAQ, Dow Jones, Russell 2000, VIX
- **Sectores S&P (11)**: XLK, XLF, XLV, XLE, XLY, XLP, XLU, XLRE, XLB, XLI, XLC
- **Macro**: Oro, Petróleo WTI, Bono 10Y, Bono 2Y, DXY, Bitcoin, EUR/USD

Cálculos propios:
- Sentimiento del mercado (risk-on / risk-off / mixto)
- Señal VIX (bajo / moderado / elevado / pánico)
- Yield curve (spread 10Y-2Y, si está invertida)

`--full`: agrega top 5 gainers y losers del día.

---

#### `scan_opportunities.py` — Scanner con scoring (0-100)
Lee `jarvis/portfolio/watchlist.json` y puntúa cada ticker:

- **Técnico (30%)**: precio vs MAs, RSI, performance del período
- **Fundamental (40%)**: forward PE, ROE, crecimiento de ingresos, márgenes, P/B
- **Analistas (30%)**: consenso buy/hold/sell, upside al target

Sectores: `tech`, `finance`, `etfs`, `latam`, `custom`

```bash
python jarvis/scripts/scan_opportunities.py --list tech --top 10
python jarvis/scripts/scan_opportunities.py --tickers MELI NU GLOB --top 3
```

---

#### `portfolio_tracker.py` — Tracker del portfolio
Lee `jarvis/portfolio/active_positions.json`, trae precios actuales y calcula:
- P&L por posición (USD y %)
- Totales del portfolio
- Ordenado por mejor performance

```bash
python jarvis/scripts/portfolio_tracker.py
python jarvis/scripts/portfolio_tracker.py --json
```

---

#### `chart_generator.py` — Gráficos interactivos HTML
Plotly dark theme con:
- Candlestick / línea / área
- MA20, MA50, MA200 superpuestas
- Volumen en subplot inferior
- Tooltip OHLCV en hover, zoom y pan

Guardados en `jarvis/charts/`.

```bash
python jarvis/scripts/chart_generator.py AAPL --period 1y --type candlestick
python jarvis/scripts/chart_generator.py MSFT --period 6mo --type area --open
```

---

#### `deep_research.py` — Research web estructurado
Genera queries optimizados para que Claude los ejecute con su herramienta de búsqueda web nativa.

Tipos: `company`, `macro`, `sector`, `news`

```bash
python jarvis/scripts/deep_research.py --ticker NVDA --type company
python jarvis/scripts/deep_research.py --topic "inflación EEUU" --type macro
```

---

#### `report_builder.py` — Reportes HTML
4 tipos con gráficos Plotly embebidos, dark theme, todo en español:
- `portfolio` — posiciones, P&L, distribución
- `market` — índices, sectores, macro
- `company` — análisis completo con candlestick
- `opportunities` — ranking por sector con scores

Guardados en `jarvis/reports/` con timestamp.

---

#### `send_email.py` — Envío de reportes
Gmail SMTP (App Password) o Resend API. Configurado en `.env`.

---

### 3.2 Archivos de datos

| Archivo | Contenido | Quién lo edita |
|---|---|---|
| `jarvis/data/profile.json` | Perfil del usuario: broker, riesgo, horizonte, preferencias | Jarvis (onboarding conversacional) |
| `jarvis/portfolio/active_positions.json` | Cartera actual con tickers, cantidad y precio promedio | Jarvis (por pedido del usuario) |
| `jarvis/portfolio/watchlist.json` | Listas de seguimiento por sector | Jarvis (por pedido del usuario) |

### 3.3 Configuración

| Archivo | Contenido |
|---|---|
| `.env` | Keys de API, credenciales de email, zona horaria |
| `.env.example` | Template documentado para configurar un nuevo deployment |
| `CLAUDE.md` | Prompt principal de Jarvis — cargado automáticamente por Claude Code |
| `setup.ps1` | Instalación automática de dependencias Python |

---

## 4. Fuentes de datos

| Fuente | Qué provee | Cobertura | Costo | Key |
|---|---|---|---|---|
| Yahoo Finance (yfinance) | Precios, histórico, fundamentals, noticias, earnings, analistas | Últimas semanas | Gratis | No |
| Alpha Vantage News API | Noticias financieras + sentimiento por artículo | Hasta 12 meses | Gratis (25 req/día) | Sí |
| NewsAPI | Noticias de medios internacionales | Últimos 30 días | Gratis (500 req/día) | Sí |
| Web Search (Claude nativo) | Research en tiempo real, SEC, Fed, medios | Actual | Incluido en Claude Pro | No |

---

## 5. Capacidades del MVP

| Capacidad | Script | Estado |
|---|---|---|
| Onboarding conversacional | CLAUDE.md (flujo nativo en Claude) | ✅ Operativo |
| Precio y métricas de cualquier ticker | fetch_market.py | ✅ Operativo |
| Histórico de precios cualquier período | fetch_market.py | ✅ Operativo |
| Fundamentals completos | fetch_market.py --info | ✅ Operativo |
| Noticias recientes (Yahoo Finance) | fetch_news.py | ✅ Operativo |
| Noticias históricas hasta 12 meses | fetch_news.py --days (Alpha Vantage) | ✅ Operativo |
| Sentimiento de noticias | fetch_news.py (Alpha Vantage) | ✅ Operativo |
| Análisis técnico (MA, RSI, tendencia) | analyze_company.py | ✅ Operativo |
| Análisis de valuación | analyze_company.py | ✅ Operativo |
| Análisis de salud financiera | analyze_company.py | ✅ Operativo |
| Gráficos candlestick interactivos | chart_generator.py | ✅ Operativo |
| Briefing completo del mercado | market_briefing.py | ✅ Operativo |
| Portfolio con P&L en tiempo real | portfolio_tracker.py | ✅ Operativo |
| Scanner de oportunidades | scan_opportunities.py | ✅ Operativo |
| Reportes HTML dark-theme | report_builder.py | ✅ Operativo |
| Envío de reportes por email | send_email.py | ✅ Operativo |
| Deep research web estructurado | deep_research.py + WebSearch | ✅ Operativo |
| Fechas obligatorias en toda la info | CLAUDE.md (regla) | ✅ Configurado |
| Sentimiento agregado en análisis | CLAUDE.md (regla) | ✅ Configurado |

---

## 6. Onboarding

El onboarding es **completamente conversacional** dentro de Claude Code. Cuando el usuario abre la carpeta por primera vez, Jarvis detecta `onboarding_completed: false` en `profile.json` y lanza el flujo de preguntas directamente en el chat.

Al confirmar, Jarvis edita los archivos JSON directamente sin intervención manual.

---

## 7. Roadmap — Fase 2

| Capacidad | Herramienta sugerida | Esfuerzo |
|---|---|---|
| Reporte diario automático (sin intervención) | n8n cron → script → email | Bajo |
| Alertas de precio vía Telegram o WhatsApp | n8n + Telegram Bot API | Medio |
| Comparación multi-ticker en un solo gráfico | Extensión de chart_generator | Bajo |
| Análisis de cadena de opciones | yfinance options chain | Medio |
| Módulo académico (Fase 2 del proyecto) | Nuevos scripts + CLAUDE.md | Alto |

---

*Jarvis MVP — Mayo 2026 | Desarrollado por Nahuel Divano*
