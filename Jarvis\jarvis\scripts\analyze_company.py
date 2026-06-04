"""
Jarvis - Company Analysis Pipeline
Análisis completo de una empresa: precios, fundamentals, noticias, métricas clave.
Diseñado para ser ejecutado por Jarvis/Claude y obtener todo en un solo JSON.
Uso: python analyze_company.py TICKER [--period 1y] [--full]
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance no instalado. Ejecutá: pip install yfinance")
    sys.exit(1)


def run_script(name: str, args_list: list) -> dict:
    cmd = [sys.executable, str(SCRIPTS_DIR / name)] + args_list
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}
    return {}


def compute_technicals(history: list) -> dict:
    if len(history) < 2:
        return {}

    closes = [r["close"] for r in history]
    highs = [r["high"] for r in history]
    lows = [r["low"] for r in history]

    def sma(data, window):
        if len(data) < window:
            return None
        return round(sum(data[-window:]) / window, 4)

    def rsi(closes, period=14):
        if len(closes) < period + 1:
            return None
        gains, losses = [], []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i - 1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 2)

    current = closes[-1]
    ma20 = sma(closes, 20)
    ma50 = sma(closes, 50)
    ma200 = sma(closes, 200)
    rsi14 = rsi(closes)

    high_52w = max(highs[-252:]) if len(highs) >= 252 else max(highs)
    low_52w = min(lows[-252:]) if len(lows) >= 252 else min(lows)
    pct_from_52w_high = round((current - high_52w) / high_52w * 100, 2)
    pct_from_52w_low = round((current - low_52w) / low_52w * 100, 2)

    trend = "neutral"
    if ma20 and ma50:
        if current > ma20 > ma50:
            trend = "alcista"
        elif current < ma20 < ma50:
            trend = "bajista"

    rsi_signal = "neutral"
    if rsi14:
        if rsi14 > 70:
            rsi_signal = "sobrecomprado"
        elif rsi14 < 30:
            rsi_signal = "sobrevendido"

    return {
        "current_price": current,
        "ma20": ma20,
        "ma50": ma50,
        "ma200": ma200,
        "rsi_14": rsi14,
        "rsi_signal": rsi_signal,
        "trend": trend,
        "52w_high": round(high_52w, 4),
        "52w_low": round(low_52w, 4),
        "pct_from_52w_high": pct_from_52w_high,
        "pct_from_52w_low": pct_from_52w_low
    }


def compute_valuation_summary(info: dict) -> dict:
    pe = info.get("trailingPE")
    fpe = info.get("forwardPE")
    pb = info.get("priceToBook")
    ps = info.get("priceToSalesTrailing12Months")
    peg = info.get("pegRatio")
    ev_ebitda = None

    ev = info.get("enterpriseValue")
    ebitda = info.get("ebitda")
    if ev and ebitda and ebitda != 0:
        ev_ebitda = round(ev / ebitda, 2)

    signals = []
    if pe:
        if pe < 15:
            signals.append("PE bajo (posiblemente subvaluada)")
        elif pe > 40:
            signals.append("PE alto (valuación exigente)")
    if fpe and pe:
        if fpe < pe:
            signals.append("Earnings creciendo (forward PE menor que trailing)")
    if pb and pb < 1.5:
        signals.append("Price/Book bajo (posible oportunidad de valor)")
    if peg and peg < 1:
        signals.append("PEG < 1 (crecimiento a precio razonable)")

    return {
        "trailing_pe": pe,
        "forward_pe": fpe,
        "price_to_book": pb,
        "price_to_sales": ps,
        "peg_ratio": peg,
        "ev_ebitda": ev_ebitda,
        "analyst_target": info.get("targetMeanPrice"),
        "analyst_recommendation": info.get("recommendationKey"),
        "num_analysts": info.get("numberOfAnalystOpinions"),
        "signals": signals
    }


def compute_financial_health(info: dict) -> dict:
    total_debt = info.get("totalDebt", 0) or 0
    total_cash = info.get("totalCash", 0) or 0
    ebitda = info.get("ebitda", 0) or 0
    revenue = info.get("totalRevenue", 0) or 0
    net_income = info.get("netIncomeToCommon", 0) or 0
    fcf = info.get("freeCashflow", 0) or 0

    net_debt = total_debt - total_cash
    debt_to_ebitda = round(net_debt / ebitda, 2) if ebitda else None
    profit_margin = info.get("profitMargins")
    roe = info.get("returnOnEquity")
    revenue_growth = info.get("revenueGrowth")
    earnings_growth = info.get("earningsGrowth")

    signals = []
    if debt_to_ebitda is not None:
        if debt_to_ebitda < 1:
            signals.append("Deuda muy baja respecto al EBITDA")
        elif debt_to_ebitda > 4:
            signals.append("Deuda elevada — riesgo financiero")
    if profit_margin and profit_margin > 0.20:
        signals.append(f"Margen neto alto ({profit_margin*100:.1f}%)")
    if roe and roe > 0.15:
        signals.append(f"ROE sólido ({roe*100:.1f}%)")
    if revenue_growth and revenue_growth > 0.15:
        signals.append(f"Crecimiento de ingresos fuerte ({revenue_growth*100:.1f}% YoY)")
    if fcf and fcf > 0:
        signals.append("Genera Free Cash Flow positivo")

    return {
        "total_revenue": revenue,
        "net_income": net_income,
        "free_cashflow": fcf,
        "total_debt": total_debt,
        "total_cash": total_cash,
        "net_debt": net_debt,
        "debt_to_ebitda": debt_to_ebitda,
        "profit_margin_pct": round(profit_margin * 100, 2) if profit_margin else None,
        "roe_pct": round(roe * 100, 2) if roe else None,
        "revenue_growth_pct": round(revenue_growth * 100, 2) if revenue_growth else None,
        "earnings_growth_pct": round(earnings_growth * 100, 2) if earnings_growth else None,
        "signals": signals
    }


def main():
    parser = argparse.ArgumentParser(description="Jarvis Company Analysis Pipeline")
    parser.add_argument("ticker", help="Ticker de la empresa (ej: AAPL, MSFT, NVDA)")
    parser.add_argument("--period", default="1y", help="Período histórico de precios")
    parser.add_argument("--full", action="store_true", help="Incluir estados financieros completos")
    parser.add_argument("--no-chart", action="store_true", help="No generar gráfico")
    parser.add_argument("--news-limit", type=int, default=10)

    args = parser.parse_args()
    ticker = args.ticker.upper()

    result = {"ticker": ticker, "analyzed_at": datetime.utcnow().isoformat()}

    # 1. Precio e histórico
    market_data = run_script("fetch_market.py", [ticker, "--period", args.period, "--info"])
    history = market_data.get("market", {}).get("history", [])
    info = market_data.get("info", {})

    result["price_data"] = {k: v for k, v in market_data.get("market", {}).items() if k != "history"}
    result["company_info"] = {
        "name": info.get("longName") or info.get("shortName", ticker),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "country": info.get("country"),
        "employees": info.get("fullTimeEmployees"),
        "market_cap": info.get("marketCap"),
        "beta": info.get("beta"),
        "description": (info.get("longBusinessSummary") or "")[:600]
    }

    # 2. Análisis técnico
    result["technicals"] = compute_technicals(history)

    # 3. Valuación
    result["valuation"] = compute_valuation_summary(info)

    # 4. Salud financiera
    result["financial_health"] = compute_financial_health(info)

    # 5. Noticias
    news_data = run_script("fetch_news.py", [ticker, "--limit", str(args.news_limit)])
    result["news"] = news_data.get("news", [])

    # 6. Gráfico
    if not args.no_chart:
        chart_result = run_script("chart_generator.py", [ticker, "--period", args.period, "--type", "candlestick"])
        result["chart"] = chart_result

    # 7. Resumen ejecutivo para Claude
    all_signals = (
        result["technicals"].get("trend", ""),
        result["technicals"].get("rsi_signal", ""),
        *result["valuation"].get("signals", []),
        *result["financial_health"].get("signals", [])
    )
    result["executive_summary"] = {
        "ticker": ticker,
        "name": result["company_info"]["name"],
        "current_price": result["technicals"].get("current_price"),
        "trend": result["technicals"].get("trend"),
        "rsi": result["technicals"].get("rsi_14"),
        "analyst_recommendation": result["valuation"].get("analyst_recommendation"),
        "analyst_target": result["valuation"].get("analyst_target"),
        "key_signals": [s for s in all_signals if s]
    }

    print(json.dumps(result, indent=2, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
