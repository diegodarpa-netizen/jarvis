"""
Jarvis - Opportunity Scanner
Escanea una lista de tickers y rankea oportunidades según métricas clave.
Pensado para que Jarvis detecte candidatos de inversión para Diego.
Uso: python scan_opportunities.py [--list sp500|tech|custom] [--tickers AAPL MSFT NVDA]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance no instalado. Ejecutá: pip install yfinance")
    sys.exit(1)

WATCHLIST_FILE = Path(__file__).parent.parent / "portfolio" / "watchlist.json"


def load_watchlists() -> dict:
    if WATCHLIST_FILE.exists():
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        sectors = data.get("sectors", {})
        return {k: v.get("tickers", []) for k, v in sectors.items()}
    # fallback si no existe el archivo
    return {
        "tech": ["AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN", "AMD", "TSLA",
                 "CRM", "ADBE", "NET", "PLTR", "SNOW", "DDOG", "SHOP"],
        "finance": ["JPM", "BAC", "GS", "MS", "V", "MA", "AXP", "BRK-B"],
        "etfs": ["SPY", "QQQ", "VGT", "VTI", "VOO", "IWM", "GLD", "TLT"],
        "latam": ["MELI", "NU", "GLOB", "YPF", "PBR", "ITUB"],
        "custom": []
    }


def score_ticker(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="6mo")

        if hist.empty or not info:
            return {"ticker": ticker, "error": "Sin datos"}

        closes = hist["Close"].tolist()
        if len(closes) < 20:
            return {"ticker": ticker, "error": "Historial insuficiente"}

        current = closes[-1]
        ma20 = sum(closes[-20:]) / 20
        ma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
        high_6m = max(closes)
        low_6m = min(closes)
        pct_from_high = round((current - high_6m) / high_6m * 100, 2)
        period_return = round((current - closes[0]) / closes[0] * 100, 2)

        # RSI 14
        gains, losses = [], []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i - 1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        ag = sum(gains[-14:]) / 14 if len(gains) >= 14 else 0
        al = sum(losses[-14:]) / 14 if len(losses) >= 14 else 0
        rsi = round(100 - (100 / (1 + ag / al)), 2) if al != 0 else 100

        # Métricas fundamentales
        pe = info.get("trailingPE")
        fpe = info.get("forwardPE")
        pb = info.get("priceToBook")
        roe = info.get("returnOnEquity", 0) or 0
        revenue_growth = info.get("revenueGrowth", 0) or 0
        profit_margin = info.get("profitMargins", 0) or 0
        market_cap = info.get("marketCap", 0) or 0
        analyst_rec = info.get("recommendationKey", "")
        target = info.get("targetMeanPrice")
        upside = round((target - current) / current * 100, 2) if target else None

        # Scoring (0-100)
        score = 50  # base

        # Trend signals
        if current > ma20:
            score += 5
        if ma50 and current > ma50:
            score += 5

        # RSI signals
        if 40 <= rsi <= 60:
            score += 8  # zona neutra sana
        elif rsi < 35:
            score += 12  # sobrevendido — posible oportunidad
        elif rsi > 75:
            score -= 10  # sobrecomprado

        # Fundamental signals
        if fpe and 10 < fpe < 25:
            score += 8
        if roe > 0.15:
            score += 5
        if revenue_growth > 0.10:
            score += 5
        if profit_margin > 0.15:
            score += 5
        if pb and 0.5 < pb < 3:
            score += 3

        # Analyst consensus
        rec_scores = {"strongBuy": 15, "buy": 10, "hold": 0, "sell": -10, "strongSell": -15}
        score += rec_scores.get(analyst_rec, 0)

        # Upside desde target de analistas
        if upside and upside > 20:
            score += 10
        elif upside and upside < 0:
            score -= 5

        # Performance reciente como señal negativa si cayó mucho
        if period_return < -20:
            score += 5  # puede ser oportunidad si fundamentals ok
        elif period_return > 50:
            score -= 5  # puede estar sobreextendida

        score = max(0, min(100, score))

        # Señales legibles
        signals = []
        if rsi < 35:
            signals.append(f"RSI sobrevendido ({rsi})")
        if rsi > 70:
            signals.append(f"RSI sobrecomprado ({rsi})")
        if upside and upside > 20:
            signals.append(f"Upside analistas: +{upside}%")
        if revenue_growth > 0.15:
            signals.append(f"Crecimiento ingresos: {revenue_growth*100:.1f}%")
        if roe > 0.20:
            signals.append(f"ROE alto: {roe*100:.1f}%")
        if analyst_rec in ("strongBuy", "buy"):
            signals.append(f"Consenso analistas: {analyst_rec}")

        return {
            "ticker": ticker,
            "name": info.get("longName") or info.get("shortName", ticker),
            "sector": info.get("sector", ""),
            "market_cap_b": round(market_cap / 1e9, 1) if market_cap else None,
            "current_price": round(current, 2),
            "period_return_pct": period_return,
            "pct_from_6m_high": pct_from_high,
            "rsi_14": rsi,
            "pe_trailing": pe,
            "pe_forward": fpe,
            "analyst_recommendation": analyst_rec,
            "analyst_target": target,
            "upside_to_target_pct": upside,
            "revenue_growth_pct": round(revenue_growth * 100, 2) if revenue_growth else None,
            "roe_pct": round(roe * 100, 2) if roe else None,
            "score": score,
            "signals": signals,
            "error": None
        }

    except Exception as e:
        return {"ticker": ticker, "error": str(e), "score": 0}


def main():
    parser = argparse.ArgumentParser(description="Jarvis Opportunity Scanner")
    WATCHLISTS = load_watchlists()

    parser.add_argument("--list", choices=list(WATCHLISTS.keys()), default="tech",
                        help="Watchlist predefinida a escanear")
    parser.add_argument("--tickers", nargs="+", help="Tickers custom (override de --list)")
    parser.add_argument("--top", type=int, default=10, help="Cuántos resultados mostrar")
    parser.add_argument("--min-score", type=int, default=50, help="Score mínimo para incluir")
    parser.add_argument("--workers", type=int, default=5, help="Threads paralelos")

    args = parser.parse_args()

    tickers = args.tickers if args.tickers else WATCHLISTS.get(args.list, [])
    if not tickers:
        print(json.dumps({"error": "No hay tickers para escanear"}))
        sys.exit(1)

    print(f"# Escaneando {len(tickers)} tickers...", file=sys.stderr)

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(score_ticker, t): t for t in tickers}
        for future in as_completed(futures):
            res = future.result()
            if not res.get("error"):
                results.append(res)
            print(f"# {res['ticker']} — score: {res.get('score', 'N/A')}", file=sys.stderr)

    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    filtered = [r for r in results if r.get("score", 0) >= args.min_score]
    top = filtered[:args.top]

    output = {
        "scanned_at": datetime.utcnow().isoformat(),
        "list": args.list,
        "total_scanned": len(tickers),
        "total_results": len(filtered),
        "top_opportunities": top
    }

    print(json.dumps(output, indent=2, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
