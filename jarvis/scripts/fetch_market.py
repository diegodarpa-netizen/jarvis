"""
Jarvis - Market Data Fetcher
Fuente: Yahoo Finance (yfinance)
Uso: python fetch_market.py TICKER [--period 6mo] [--info] [--full]
"""

import argparse
import json
import sys
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance no instalado. Ejecutá: pip install yfinance")
    sys.exit(1)

PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]


def fetch_price_history(ticker: str, period: str = "6mo") -> dict:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    if hist.empty:
        return {"error": f"No se encontraron datos para {ticker}"}

    records = []
    for date, row in hist.iterrows():
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(row["Open"], 4),
            "high": round(row["High"], 4),
            "low": round(row["Low"], 4),
            "close": round(row["Close"], 4),
            "volume": int(row["Volume"])
        })

    latest = records[-1]
    first = records[0]
    price_change = latest["close"] - first["close"]
    pct_change = (price_change / first["close"]) * 100

    return {
        "ticker": ticker.upper(),
        "period": period,
        "current_price": latest["close"],
        "price_change": round(price_change, 4),
        "pct_change": round(pct_change, 2),
        "period_high": round(max(r["high"] for r in records), 4),
        "period_low": round(min(r["low"] for r in records), 4),
        "data_points": len(records),
        "history": records,
        "fetched_at": datetime.utcnow().isoformat()
    }


def fetch_info(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    info = stock.info

    fields = [
        "longName", "sector", "industry", "country", "website",
        "marketCap", "enterpriseValue", "trailingPE", "forwardPE",
        "priceToBook", "priceToSalesTrailing12Months",
        "profitMargins", "operatingMargins", "returnOnEquity",
        "revenueGrowth", "earningsGrowth",
        "totalRevenue", "grossProfits", "ebitda", "netIncomeToCommon",
        "totalDebt", "totalCash", "freeCashflow",
        "dividendYield", "payoutRatio",
        "52WeekHigh", "52WeekLow",
        "fiftyDayAverage", "twoHundredDayAverage",
        "shortRatio", "sharesShort",
        "beta", "averageVolume", "averageVolume10days",
        "longBusinessSummary", "fullTimeEmployees",
        "recommendationKey", "targetMeanPrice", "numberOfAnalystOpinions"
    ]

    result = {"ticker": ticker.upper()}
    for f in fields:
        val = info.get(f)
        if val is not None:
            result[f] = val

    result["fetched_at"] = datetime.utcnow().isoformat()
    return result


def fetch_financials(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    result = {"ticker": ticker.upper()}

    try:
        income = stock.income_stmt
        if income is not None and not income.empty:
            result["income_statement"] = income.to_dict()
    except Exception:
        pass

    try:
        balance = stock.balance_sheet
        if balance is not None and not balance.empty:
            result["balance_sheet"] = balance.to_dict()
    except Exception:
        pass

    try:
        cashflow = stock.cashflow
        if cashflow is not None and not cashflow.empty:
            result["cashflow"] = cashflow.to_dict()
    except Exception:
        pass

    result["fetched_at"] = datetime.utcnow().isoformat()
    return result


def main():
    parser = argparse.ArgumentParser(description="Jarvis Market Data Fetcher")
    parser.add_argument("ticker", help="Ticker del activo (ej: AAPL, MSFT, SPY)")
    parser.add_argument("--period", default="6mo", choices=PERIODS, help="Período histórico")
    parser.add_argument("--info", action="store_true", help="Incluir info fundamental de la empresa")
    parser.add_argument("--financials", action="store_true", help="Incluir estados financieros")
    parser.add_argument("--full", action="store_true", help="Todo: precio + info + financials")
    parser.add_argument("--no-history", action="store_true", help="Solo métricas, sin historial de precios")

    args = parser.parse_args()
    ticker = args.ticker.upper()

    result = {}

    price_data = fetch_price_history(ticker, args.period)
    if args.no_history and "history" in price_data:
        del price_data["history"]
    result["market"] = price_data

    if args.info or args.full:
        result["info"] = fetch_info(ticker)

    if args.financials or args.full:
        result["financials"] = fetch_financials(ticker)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
