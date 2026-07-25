---
name: finanzas-scanner-oportunidades
description: Escanea y rankea oportunidades de inversión, o analiza una empresa/ticker puntual (precio, fundamentals, noticias). Usar cuando Diego pida buscar oportunidades, analizar una empresa, o comparar tickers.
---

# Scanner de oportunidades / análisis de empresa

Equipo: Trading/Finanzas.

1. Para un scan general: `python jarvis/scripts/scan_opportunities.py` (rankea una lista de tickers).
2. Para una empresa puntual: `python jarvis/scripts/analyze_company.py` (pipeline completo: precio + fundamentals + noticias → JSON).
3. Apoyarse en `jarvis/scripts/fetch_market.py` (datos de Yahoo Finance) y `jarvis/scripts/fetch_news.py` (Yahoo Finance → Alpha Vantage → NewsAPI, en ese orden de prioridad).
4. Si Diego pide un research más profundo antes de decidir, usar `jarvis/scripts/deep_research.py` para armar las queries y el WebSearch real — no inventar datos de mercado.
5. Watchlist dinámico basado en JPMorgan, Schwab, Reuters, Bloomberg, TradingView y analistas top (ver memoria de usuario) — priorizar coherencia con eso si Diego no da un ticker puntual.
