"""
Descarga datos diarios reales (yfinance) para el universo de equities swing
propuesto en PLAN_CONSTRUCCION.md (prioridad 3): CRM, WFC, SLB, ORCL, FSLR,
BSBR. Retoma el research que había quedado a mitad de camino (ver memoria
project_swing_trading_equities) — esta vez con walk-forward real, no un
solo backtest estático.

~5 años diarios: suficiente para varias ventanas de walk-forward con
muestra razonable de trades por ventana (a diferencia del backtest
original de 03/08, que solo cubría ~7 meses).
"""
import os
import time

import yfinance as yf

TICKERS = ["CRM", "WFC", "SLB", "ORCL", "FSLR", "BSBR"]
PERIODO = "5y"
OUT_DIR = os.path.join(os.path.dirname(__file__), "data")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for ticker in TICKERS:
        print(f"Descargando {ticker}...")
        df = yf.download(ticker, period=PERIODO, interval="1d", auto_adjust=True, progress=False)
        if df.empty:
            print(f"  [aviso] sin datos para {ticker}")
            continue
        if isinstance(df.columns, __import__("pandas").MultiIndex):
            df.columns = df.columns.get_level_values(0)
        out_path = os.path.join(OUT_DIR, f"swing_{ticker.lower()}_daily.csv")
        df.to_csv(out_path)
        print(f"  OK: {len(df)} barras, {df.index[0].date()} -> {df.index[-1].date()} -> {out_path}")
        time.sleep(1)  # no golpear la API muy rápido


if __name__ == "__main__":
    main()
