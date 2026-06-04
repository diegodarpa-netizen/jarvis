"""
Jarvis - Portfolio Tracker
Lee positions.json y calcula P&L en tiempo real contra Yahoo Finance
Uso: python portfolio_tracker.py [--export]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance no instalado. Ejecutá: pip install yfinance")
    sys.exit(1)

POSITIONS_FILE = Path(__file__).parent.parent / "portfolio" / "active_positions.json"


def load_positions() -> list:
    if not POSITIONS_FILE.exists():
        print(f"ERROR: No se encontró {POSITIONS_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("positions", [])


def get_current_prices(tickers: list) -> dict:
    prices = {}
    for ticker in tickers:
        if ticker == "EJEMPLO":
            continue
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
            name = info.get("longName") or info.get("shortName") or ticker
            prices[ticker] = {
                "current_price": price,
                "name": name,
                "currency": info.get("currency", "USD")
            }
        except Exception as e:
            prices[ticker] = {"current_price": None, "name": ticker, "error": str(e)}

    return prices


def calculate_portfolio(positions: list, current_prices: dict) -> dict:
    total_invested = 0
    total_current_value = 0
    rows = []

    for pos in positions:
        ticker = pos["ticker"]
        if ticker == "EJEMPLO":
            continue

        qty = pos.get("quantity", 0)
        avg_buy = pos.get("avg_buy_price", 0)
        invested = qty * avg_buy

        price_data = current_prices.get(ticker, {})
        current_price = price_data.get("current_price")

        if current_price:
            current_value = qty * current_price
            pnl_usd = current_value - invested
            pnl_pct = (pnl_usd / invested * 100) if invested > 0 else 0
        else:
            current_value = None
            pnl_usd = None
            pnl_pct = None

        total_invested += invested
        if current_value:
            total_current_value += current_value

        rows.append({
            "ticker": ticker,
            "name": price_data.get("name", ticker),
            "type": pos.get("type", "stock"),
            "quantity": qty,
            "avg_buy_price": avg_buy,
            "current_price": current_price,
            "invested_usd": round(invested, 2),
            "current_value_usd": round(current_value, 2) if current_value else None,
            "pnl_usd": round(pnl_usd, 2) if pnl_usd is not None else None,
            "pnl_pct": round(pnl_pct, 2) if pnl_pct is not None else None,
            "buy_date": pos.get("buy_date"),
            "notes": pos.get("notes", "")
        })

    total_pnl = total_current_value - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0

    rows.sort(key=lambda x: (x["pnl_pct"] or 0), reverse=True)

    return {
        "summary": {
            "total_invested_usd": round(total_invested, 2),
            "total_current_value_usd": round(total_current_value, 2),
            "total_pnl_usd": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "num_positions": len(rows)
        },
        "positions": rows,
        "fetched_at": datetime.utcnow().isoformat()
    }


def print_table(portfolio: dict):
    summary = portfolio["summary"]
    positions = portfolio["positions"]

    print("\n" + "=" * 70)
    print("  JARVIS — PORTFOLIO DE DIEGO RODRIGUEZ")
    print("=" * 70)
    print(f"  {'TICKER':<8} {'NOMBRE':<25} {'CANT':>6} {'P.COMPRA':>10} {'P.ACTUAL':>10} {'G/P USD':>10} {'G/P %':>8}")
    print("-" * 70)

    for pos in positions:
        pnl_usd = f"${pos['pnl_usd']:+.2f}" if pos['pnl_usd'] is not None else "S/D"
        pnl_pct = f"{pos['pnl_pct']:+.2f}%" if pos['pnl_pct'] is not None else "S/D"
        current = f"${pos['current_price']:.2f}" if pos['current_price'] else "S/D"
        name_short = pos['name'][:24]
        print(f"  {pos['ticker']:<8} {name_short:<25} {pos['quantity']:>6} ${pos['avg_buy_price']:>9.2f} {current:>10} {pnl_usd:>10} {pnl_pct:>8}")

    print("=" * 70)
    pnl_sign = "+" if summary["total_pnl_usd"] >= 0 else ""
    print(f"  CAPITAL INVERTIDO:  ${summary['total_invested_usd']:,.2f}")
    print(f"  VALOR ACTUAL:       ${summary['total_current_value_usd']:,.2f}")
    print(f"  GANANCIA / PÉRDIDA: {pnl_sign}${summary['total_pnl_usd']:,.2f} ({pnl_sign}{summary['total_pnl_pct']:.2f}%)")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Jarvis Portfolio Tracker")
    parser.add_argument("--export", action="store_true", help="Exportar resultado como JSON")
    parser.add_argument("--json", action="store_true", help="Output en JSON (para Jarvis/Claude)")
    args = parser.parse_args()

    positions = load_positions()
    tickers = [p["ticker"] for p in positions]
    current_prices = get_current_prices(tickers)
    portfolio = calculate_portfolio(positions, current_prices)

    if args.json or args.export:
        print(json.dumps(portfolio, indent=2))
    else:
        print_table(portfolio)
        print(json.dumps(portfolio["summary"], indent=2))


if __name__ == "__main__":
    main()
