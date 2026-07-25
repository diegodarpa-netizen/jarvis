"""
Jarvis - News Fetcher
Fuentes (en orden de prioridad):
  1. Yahoo Finance   — siempre activo, últimas 2-4 semanas
  2. Alpha Vantage   — hasta 1 año de historia + sentimiento (ALPHA_VANTAGE_KEY en .env)
  3. NewsAPI         — últimos 30 días adicionales (NEWSAPI_KEY en .env)

Uso:
  python fetch_news.py TICKER [--limit 10] [--days 180]
  python fetch_news.py MARKET --limit 15
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance no instalado. Ejecutá: pip install yfinance", file=sys.stderr)
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests no instalado. Ejecutá: pip install requests", file=sys.stderr)
    sys.exit(1)

ENV_FILE = Path(__file__).parent.parent.parent / ".env"
MARKET_PROXIES = ["SPY", "QQQ", "^GSPC"]

# Etiquetas de sentimiento Alpha Vantage → español
SENTIMENT_LABELS = {
    "Bullish": "Alcista",
    "Somewhat-Bullish": "Levemente alcista",
    "Somewhat Bullish": "Levemente alcista",
    "Neutral": "Neutral",
    "Somewhat-Bearish": "Levemente bajista",
    "Somewhat Bearish": "Levemente bajista",
    "Bearish": "Bajista",
}


def load_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    env.update(os.environ)
    return env


# ── Yahoo Finance ─────────────────────────────────────────────────────────────

def parse_yf_item(item: dict, ticker: str) -> dict:
    content = item.get("content", {})
    title = content.get("title") or item.get("title", "")
    summary = content.get("summary") or item.get("summary", "")
    pub_date = content.get("pubDate") or item.get("providerPublishTime", "")
    if isinstance(pub_date, (int, float)):
        try:
            pub_date = datetime.utcfromtimestamp(pub_date).strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            pub_date = str(pub_date)
    source = ""
    if "provider" in content:
        source = content["provider"].get("displayName", "")
    elif "publisher" in item:
        source = item["publisher"]
    url = (content.get("canonicalUrl", {}) or {}).get("url") or item.get("link", "")
    return {
        "title": title, "summary": summary, "published_at": pub_date,
        "source": source, "url": url, "ticker": ticker.upper(),
        "sentiment": None, "sentiment_score": None, "via": "yahoo_finance"
    }


def fetch_yf_news(ticker: str, limit: int) -> list:
    try:
        raw = yf.Ticker(ticker).news or []
        return [parse_yf_item(i, ticker) for i in raw[:limit]]
    except Exception:
        return []


# ── Alpha Vantage News & Sentiment ────────────────────────────────────────────

def fetch_alpha_vantage_news(ticker: str, api_key: str, limit: int, days: int) -> list:
    """
    Consulta Alpha Vantage NEWS_SENTIMENT API.
    Cubre hasta 1 año de historia. Incluye score de sentimiento por artículo.
    Free plan: 25 requests/día — cada request puede traer hasta 1000 artículos.
    """
    time_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y%m%dT%H%M")

    # Para noticias de mercado general usamos topics en lugar de ticker
    if ticker == "MARKET":
        params = {
            "function": "NEWS_SENTIMENT",
            "topics": "financial_markets,economy_macro,economy_monetary",
            "time_from": time_from,
            "limit": min(limit * 2, 200),
            "sort": "LATEST",
            "apikey": api_key,
        }
    else:
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "time_from": time_from,
            "limit": min(limit * 2, 200),
            "sort": "LATEST",
            "apikey": api_key,
        }

    try:
        resp = requests.get(
            "https://www.alphavantage.co/query",
            params=params,
            timeout=15
        )
        data = resp.json()

        # La API devuelve {"Information": "..."} si se superó el límite
        if "Information" in data or "Note" in data:
            return []

        feed = data.get("feed", [])
        results = []
        for article in feed[:limit]:
            # Convertir fecha: "20260515T143000" → "2026-05-15 14:30 UTC"
            raw_date = article.get("time_published", "")
            try:
                dt = datetime.strptime(raw_date, "%Y%m%dT%H%M%S")
                pub_date = dt.strftime("%Y-%m-%d %H:%M UTC")
            except Exception:
                pub_date = raw_date

            # Sentimiento global del artículo
            sentiment_label = article.get("overall_sentiment_label", "")
            sentiment_score = article.get("overall_sentiment_score", None)
            sentiment_es = SENTIMENT_LABELS.get(sentiment_label, sentiment_label)

            # Si es un ticker específico, usar el sentimiento específico para ese ticker
            if ticker != "MARKET":
                for ts in article.get("ticker_sentiment", []):
                    if ts.get("ticker", "").upper() == ticker.upper():
                        tsl = ts.get("ticker_sentiment_label", sentiment_label)
                        sentiment_es = SENTIMENT_LABELS.get(tsl, tsl)
                        try:
                            sentiment_score = float(ts.get("ticker_sentiment_score", sentiment_score))
                        except Exception:
                            pass
                        break

            results.append({
                "title": article.get("title", ""),
                "summary": article.get("summary", ""),
                "published_at": pub_date,
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "ticker": ticker.upper(),
                "sentiment": sentiment_es or None,
                "sentiment_score": round(float(sentiment_score), 3) if sentiment_score is not None else None,
                "via": "alpha_vantage"
            })
        return results
    except Exception:
        return []


# ── NewsAPI ───────────────────────────────────────────────────────────────────

def fetch_newsapi(query: str, api_key: str, limit: int, ticker: str) -> list:
    from_date = (datetime.utcnow() - timedelta(days=29)).strftime("%Y-%m-%d")
    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={"q": query, "language": "en", "sortBy": "publishedAt",
                    "pageSize": min(limit, 20), "from": from_date, "apiKey": api_key},
            timeout=10
        )
        articles = resp.json().get("articles", [])
        return [{
            "title": a.get("title", ""),
            "summary": a.get("description", ""),
            "published_at": a.get("publishedAt", ""),
            "source": a.get("source", {}).get("name", ""),
            "url": a.get("url", ""),
            "ticker": ticker.upper(),
            "sentiment": None,
            "sentiment_score": None,
            "via": "newsapi"
        } for a in articles]
    except Exception:
        return []


# ── Agregadores ───────────────────────────────────────────────────────────────

def fetch_market_news(limit: int, av_key: str, newsapi_key: str, days: int) -> list:
    seen, all_news = set(), []

    for proxy in MARKET_PROXIES:
        for item in fetch_yf_news(proxy, limit):
            if item["title"] and item["title"] not in seen:
                seen.add(item["title"])
                item["ticker"] = "MARKET"
                all_news.append(item)
        if len(all_news) >= limit:
            break

    if av_key and len(all_news) < limit:
        for item in fetch_alpha_vantage_news("MARKET", av_key, limit - len(all_news), days):
            if item["title"] not in seen:
                seen.add(item["title"])
                all_news.append(item)

    if newsapi_key and len(all_news) < limit:
        extra = fetch_newsapi(
            '"stock market" OR "S&P 500" OR "Federal Reserve" OR "earnings"',
            newsapi_key, limit - len(all_news), "MARKET"
        )
        for item in extra:
            if item["title"] not in seen:
                seen.add(item["title"])
                all_news.append(item)

    return all_news[:limit]


def fetch_ticker_news(ticker: str, limit: int, av_key: str, newsapi_key: str, days: int) -> list:
    seen, all_news = set(), []

    for item in fetch_yf_news(ticker, limit):
        if item["title"] and item["title"] not in seen:
            seen.add(item["title"])
            all_news.append(item)

    if av_key:
        for item in fetch_alpha_vantage_news(ticker, av_key, limit, days):
            if item["title"] not in seen:
                seen.add(item["title"])
                all_news.append(item)

    if newsapi_key and len(all_news) < limit:
        info = {}
        try:
            info = yf.Ticker(ticker).info
        except Exception:
            pass
        company = info.get("longName") or info.get("shortName") or ticker
        query = f'"{company}" OR "{ticker}" stock'
        for item in fetch_newsapi(query, newsapi_key, limit - len(all_news), ticker):
            if item["title"] not in seen:
                seen.add(item["title"])
                all_news.append(item)

    return all_news[:limit]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Jarvis News Fetcher")
    parser.add_argument("ticker", nargs="?", default="MARKET",
                        help="Ticker (ej: AAPL) o MARKET para noticias generales")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--days", type=int, default=30,
                        help="Días de historia a cubrir (Alpha Vantage, default: 30, max: 365)")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    env = load_env()
    av_key = env.get("ALPHA_VANTAGE_KEY", "")
    newsapi_key = env.get("NEWSAPI_KEY", "")

    if ticker == "MARKET":
        news = fetch_market_news(args.limit, av_key, newsapi_key, args.days)
    else:
        news = fetch_ticker_news(ticker, args.limit, av_key, newsapi_key, args.days)

    sources = list({n["via"] for n in news})
    print(json.dumps({
        "ticker": ticker,
        "count": len(news),
        "sources": sources,
        "alpha_vantage_active": bool(av_key),
        "newsapi_active": bool(newsapi_key),
        "days_covered": args.days,
        "fetched_at": datetime.utcnow().isoformat(),
        "news": news
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
