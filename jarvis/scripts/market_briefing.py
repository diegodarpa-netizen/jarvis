"""
Jarvis - Market Briefing
Genera un briefing completo del mercado: índices, sectores, macro, noticias.
Se ejecuta a diario o a demanda. Output JSON para que Claude lo analice.
Uso: python market_briefing.py [--full]
"""

import json
import sys
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance no instalado. Ejecutá: pip install yfinance")
    sys.exit(1)

# Índices y activos clave a monitorear siempre
INDICES = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",
    "VIX (Volatilidad)": "^VIX"
}

SECTORS_ETFS = {
    "Tecnología": "XLK",
    "Finanzas": "XLF",
    "Salud": "XLV",
    "Energía": "XLE",
    "Consumo Discrecional": "XLY",
    "Consumo Básico": "XLP",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Materiales": "XLB",
    "Industriales": "XLI",
    "Comunicaciones": "XLC"
}

MACRO_ASSETS = {
    "Oro": "GC=F",
    "Petróleo WTI": "CL=F",
    "Bono 10Y EEUU": "^TNX",
    "Bono 2Y EEUU": "^IRX",
    "DXY (Dólar Index)": "DX-Y.NYB",
    "Bitcoin": "BTC-USD",
    "Euro/USD": "EURUSD=X"
}


def get_ticker_snapshot(label: str, symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        if hist.empty:
            return {"label": label, "symbol": symbol, "error": "Sin datos"}

        closes = hist["Close"].tolist()
        current = closes[-1]
        prev = closes[-2] if len(closes) >= 2 else closes[0]
        change = current - prev
        change_pct = (change / prev * 100) if prev else 0

        week_start = closes[0]
        week_change_pct = (current - week_start) / week_start * 100

        return {
            "label": label,
            "symbol": symbol,
            "current": round(current, 4),
            "change_1d": round(change, 4),
            "change_1d_pct": round(change_pct, 2),
            "change_5d_pct": round(week_change_pct, 2),
            "direction": "up" if change >= 0 else "down"
        }
    except Exception as e:
        return {"label": label, "symbol": symbol, "error": str(e)}


def fetch_all_snapshots(items: dict) -> list:
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(get_ticker_snapshot, label, sym): label
                   for label, sym in items.items()}
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda x: list(items.keys()).index(x["label"]) if x["label"] in items else 999)
    return results


def get_top_movers(tickers: list, period: str = "1d") -> dict:
    gainers, losers = [], []
    for t in tickers:
        try:
            ticker = yf.Ticker(t)
            hist = ticker.history(period="2d")
            if len(hist) < 2:
                continue
            closes = hist["Close"].tolist()
            change_pct = (closes[-1] - closes[-2]) / closes[-2] * 100
            entry = {"ticker": t, "change_pct": round(change_pct, 2), "price": round(closes[-1], 2)}
            if change_pct > 0:
                gainers.append(entry)
            else:
                losers.append(entry)
        except Exception:
            pass

    gainers.sort(key=lambda x: x["change_pct"], reverse=True)
    losers.sort(key=lambda x: x["change_pct"])
    return {"top_gainers": gainers[:5], "top_losers": losers[:5]}


def get_market_sentiment(indices: list) -> str:
    if not indices:
        return "neutral"
    up = sum(1 for i in indices if i.get("direction") == "up")
    total = len([i for i in indices if "direction" in i])
    if total == 0:
        return "neutral"
    ratio = up / total
    if ratio >= 0.7:
        return "risk-on (mercado alcista)"
    elif ratio <= 0.3:
        return "risk-off (mercado bajista)"
    return "mixto"


def main():
    parser = argparse.ArgumentParser(description="Jarvis Market Briefing")
    parser.add_argument("--full", action="store_true", help="Incluir top movers de S&P")
    args = parser.parse_args()

    print("# Generando briefing del mercado...", file=sys.stderr)

    indices_data = fetch_all_snapshots(INDICES)
    sectors_data = fetch_all_snapshots(SECTORS_ETFS)
    macro_data = fetch_all_snapshots(MACRO_ASSETS)

    vix_entry = next((i for i in indices_data if "VIX" in i.get("label", "")), None)
    vix_level = vix_entry.get("current") if vix_entry else None
    vix_signal = "bajo" if vix_level and vix_level < 15 else ("elevado" if vix_level and vix_level > 25 else "moderado")

    sentiment = get_market_sentiment(indices_data)

    sectors_sorted = sorted(
        [s for s in sectors_data if "change_1d_pct" in s],
        key=lambda x: x["change_1d_pct"],
        reverse=True
    )
    best_sector = sectors_sorted[0] if sectors_sorted else None
    worst_sector = sectors_sorted[-1] if sectors_sorted else None

    bono_10y = next((m for m in macro_data if "10Y" in m.get("label", "")), None)
    bono_2y = next((m for m in macro_data if "2Y" in m.get("label", "")), None)
    yield_curve = None
    if bono_10y and bono_2y and bono_10y.get("current") and bono_2y.get("current"):
        spread = round(bono_10y["current"] - bono_2y["current"], 3)
        yield_curve = {"spread_10y_2y": spread, "inverted": spread < 0}

    movers = {}
    if args.full:
        sp500_tickers = [
            "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "BRK-B",
            "JPM", "JNJ", "V", "UNH", "XOM", "MA", "HD", "PG", "COST", "ABBV",
            "MRK", "CVX", "LLY", "AMD", "CRM", "ADBE", "NFLX"
        ]
        movers = get_top_movers(sp500_tickers)

    output = {
        "briefing_date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.utcnow().isoformat(),
        "market_sentiment": sentiment,
        "vix": {"level": vix_level, "signal": vix_signal},
        "yield_curve": yield_curve,
        "indices": indices_data,
        "sectors": {
            "all": sectors_data,
            "best_today": best_sector,
            "worst_today": worst_sector
        },
        "macro": macro_data,
        "movers": movers
    }

    print(json.dumps(output, indent=2, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
