"""
Jarvis - Portfolio Tracker (CEDEAR Edition)
Obtiene precios de CEDEARs en ARS desde Yahoo Finance (.BA),
convierte a USD usando el tipo CCL del día y calcula P&L real.
Uso: python portfolio_tracker.py [--export] [--json]
"""

import argparse
import json
import os
import sys
from datetime import datetime

try:
    import yfinance as yf
    import requests
except ImportError as e:
    print(f"ERROR: Falta instalar dependencias. Ejecutá: pip install yfinance requests\n{e}")
    sys.exit(1)

# ── Rutas ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSITIONS_FILE = os.path.join(BASE_DIR, "Jarvis\\jarvis\\portfolio\\active_positions.json")

# Si el path con backslash no existe, intentar path normal (en caso de migración futura)
if not os.path.exists(POSITIONS_FILE):
    POSITIONS_FILE = os.path.join(BASE_DIR, "..", "portfolio", "active_positions.json")


# ── CCL ───────────────────────────────────────────────────────────────────────
def get_ccl() -> float:
    """Obtiene el tipo de cambio CCL (Contado con Liqui) del día."""
    fuentes = [
        ("dolarapi.com",     "https://dolarapi.com/v1/dolares/contadoconliqui", lambda r: r.get("venta")),
        ("dolarapi.com MEP", "https://dolarapi.com/v1/dolares/mep",             lambda r: r.get("venta")),
    ]
    for nombre, url, extractor in fuentes:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                valor = extractor(r.json())
                if valor:
                    return float(valor)
        except Exception:
            pass

    # Fallback: calcular CCL implícito usando SPY.BA vs SPY NYSE
    try:
        spy_ba = yf.Ticker("SPY.BA").info
        spy_us = yf.Ticker("SPY").info
        p_ba = spy_ba.get("currentPrice") or spy_ba.get("regularMarketPrice")
        p_us = spy_us.get("currentPrice") or spy_us.get("regularMarketPrice")
        # SPY CEDEAR ratio oficial BYMA = 5 (5 CEDEARs = 1 SPY)
        if p_ba and p_us:
            return round(p_ba / (p_us / 5), 2)
    except Exception:
        pass

    # Último recurso: tipo hardcodeado (actualizar si es necesario)
    return 1450.0


# ── Precios CEDEAR ────────────────────────────────────────────────────────────
def get_cedear_prices(tickers: list) -> dict:
    """
    Obtiene precios actuales de CEDEARs en ARS usando el sufijo .BA de Yahoo Finance.
    Devuelve dict {ticker: {price_ars, prev_close_ars, name, cambio_dia_pct}}
    """
    prices = {}
    for ticker in tickers:
        if ticker in ("EJEMPLO",):
            continue
        ba_ticker = f"{ticker}.BA"
        try:
            stock = yf.Ticker(ba_ticker)
            info = stock.info
            price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
            prev  = info.get("previousClose") or price
            name  = info.get("longName") or info.get("shortName") or ticker
            cambio = ((price - prev) / prev * 100) if (prev and prev != 0) else 0.0
            if price:
                prices[ticker] = {
                    "price_ars":      round(float(price), 2),
                    "prev_close_ars": round(float(prev), 2),
                    "cambio_dia_pct": round(cambio, 2),
                    "name":           name,
                    "ok":             True,
                }
                continue
        except Exception:
            pass

        # Fallback: intentar con el ticker directo en USD (menos preciso para CEDEARs)
        prices[ticker] = {"price_ars": None, "cambio_dia_pct": 0, "name": ticker, "ok": False}

    return prices


# ── Carga posiciones ──────────────────────────────────────────────────────────
def load_positions() -> list:
    if not os.path.exists(POSITIONS_FILE):
        print(f"ERROR: No se encontró {POSITIONS_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("positions", [])


# ── Cálculo P&L ───────────────────────────────────────────────────────────────
def calculate_portfolio(positions: list, cedear_prices: dict, ccl: float) -> dict:
    total_costo_usd   = 0.0
    total_valor_usd   = 0.0
    total_valor_ars   = 0.0
    rows = []

    for pos in positions:
        ticker  = pos["ticker"]
        if ticker == "EJEMPLO":
            continue
        qty     = pos.get("quantity", 0)
        buy_usd = pos.get("avg_buy_price", 0)   # USD por CEDEAR al momento de compra
        costo_usd = qty * buy_usd

        pdata = cedear_prices.get(ticker, {})
        price_ars = pdata.get("price_ars")

        if price_ars:
            valor_ars = qty * price_ars
            valor_usd = valor_ars / ccl
            pnl_usd   = valor_usd - costo_usd
            pnl_pct   = (pnl_usd / costo_usd * 100) if costo_usd else 0
        else:
            valor_ars = None
            valor_usd = None
            pnl_usd   = None
            pnl_pct   = None

        total_costo_usd += costo_usd
        if valor_usd:
            total_valor_usd += valor_usd
        if valor_ars:
            total_valor_ars += valor_ars

        rows.append({
            "ticker":          ticker,
            "name":            pdata.get("name", ticker),
            "quantity":        qty,
            "avg_buy_usd":     round(buy_usd, 4),
            "price_ars":       round(price_ars, 2) if price_ars else None,
            "price_usd":       round(price_ars / ccl, 4) if price_ars else None,
            "cambio_dia_pct":  pdata.get("cambio_dia_pct", 0),
            "costo_usd":       round(costo_usd, 2),
            "valor_usd":       round(valor_usd, 2) if valor_usd else None,
            "valor_ars":       round(valor_ars, 2) if valor_ars else None,
            "pnl_usd":         round(pnl_usd, 2) if pnl_usd is not None else None,
            "pnl_pct":         round(pnl_pct, 2) if pnl_pct is not None else None,
        })

    rows.sort(key=lambda x: (x["pnl_usd"] or 0), reverse=True)

    total_pnl_usd = total_valor_usd - total_costo_usd
    total_pnl_pct = (total_pnl_usd / total_costo_usd * 100) if total_costo_usd else 0

    return {
        "ccl_usado": ccl,
        "summary": {
            "total_costo_usd":  round(total_costo_usd, 2),
            "total_valor_usd":  round(total_valor_usd, 2),
            "total_valor_ars":  round(total_valor_ars, 2),
            "total_pnl_usd":    round(total_pnl_usd, 2),
            "total_pnl_pct":    round(total_pnl_pct, 2),
            "num_positions":    len(rows),
        },
        "positions":  rows,
        "fetched_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }


# ── Impresión ─────────────────────────────────────────────────────────────────
def print_table(portfolio: dict):
    s   = portfolio["summary"]
    ccl = portfolio["ccl_usado"]
    pos = portfolio["positions"]
    ts  = portfolio["fetched_at"]

    print()
    print("=" * 80)
    print(f"  JARVIS — PORTFOLIO DIEGO  |  {ts}  |  CCL: ${ccl:,.2f}")
    print("=" * 80)
    print(f"  {'TICKER':<7} {'CANT':>5}  {'P.COMPRA':>9}  {'P.ACTUAL ARS':>13}  {'HOY':>7}  {'COSTO USD':>10}  {'VALOR USD':>10}  {'P&L USD':>10}  {'P&L%':>7}")
    print("-" * 80)

    for r in pos:
        if r["price_ars"] is None:
            print(f"  {r['ticker']:<7} {r['quantity']:>5}  {'S/D':>9}  {'S/D':>13}  {'S/D':>7}  ${r['costo_usd']:>9,.0f}  {'S/D':>10}  {'S/D':>10}  {'S/D':>7}")
            continue

        hoy  = f"{r['cambio_dia_pct']:+.2f}%"
        pnl  = f"{'+'if r['pnl_usd']>=0 else ''}{r['pnl_usd']:,.0f}" if r["pnl_usd"] is not None else "S/D"
        ppct = f"{'+'if r['pnl_pct']>=0 else ''}{r['pnl_pct']:.1f}%" if r["pnl_pct"] is not None else "S/D"
        print(
            f"  {r['ticker']:<7} {r['quantity']:>5}"
            f"  ${r['avg_buy_usd']:>8.2f}"
            f"  ${r['price_ars']:>12,.2f}"
            f"  {hoy:>7}"
            f"  ${r['costo_usd']:>9,.0f}"
            f"  ${r['valor_usd']:>9,.0f}"
            f"  {pnl:>10}"
            f"  {ppct:>7}"
        )

    print("=" * 80)
    pnl_t = s["total_pnl_usd"]
    sgn   = "+" if pnl_t >= 0 else ""
    print(f"  CAPITAL INVERTIDO:  u$s {s['total_costo_usd']:>10,.2f}")
    print(f"  VALOR ACTUAL:       u$s {s['total_valor_usd']:>10,.2f}   ($ {s['total_valor_ars']:>14,.0f} ARS)")
    print(f"  GANANCIA / PÉRDIDA: u$s {sgn}{abs(pnl_t):>9,.2f}   ({sgn}{s['total_pnl_pct']:.2f}%)")
    print("=" * 80)
    print()

    # Mejor y peor posición
    con_datos = [r for r in pos if r["pnl_usd"] is not None]
    if con_datos:
        mejor = max(con_datos, key=lambda x: x["pnl_usd"])
        peor  = min(con_datos, key=lambda x: x["pnl_usd"])
        print(f"  🏆  Mejor posición:  {mejor['ticker']} ({'+' if mejor['pnl_usd']>=0 else ''}u$s {mejor['pnl_usd']:,.0f} / {'+' if mejor['pnl_pct']>=0 else ''}{mejor['pnl_pct']:.1f}%)")
        print(f"  ⚠️   Peor posición:   {peor['ticker']}  ({'+'if peor['pnl_usd']>=0 else ''}u$s {peor['pnl_usd']:,.0f} / {'+'if peor['pnl_pct']>=0 else ''}{peor['pnl_pct']:.1f}%)")
        print()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Jarvis Portfolio Tracker — CEDEARs")
    parser.add_argument("--export", action="store_true", help="Exportar resultado como JSON")
    parser.add_argument("--json",   action="store_true", help="Output en JSON")
    args = parser.parse_args()

    print("Obteniendo tipo de cambio CCL...")
    ccl = get_ccl()

    positions = load_positions()
    tickers   = [p["ticker"] for p in positions if p["ticker"] != "EJEMPLO"]

    print(f"Consultando precios CEDEAR en BYMA para {len(tickers)} posiciones...")
    cedear_prices = get_cedear_prices(tickers)

    portfolio = calculate_portfolio(positions, cedear_prices, ccl)

    if args.json or args.export:
        print(json.dumps(portfolio, indent=2, ensure_ascii=False))
    else:
        print_table(portfolio)


if __name__ == "__main__":
    main()
