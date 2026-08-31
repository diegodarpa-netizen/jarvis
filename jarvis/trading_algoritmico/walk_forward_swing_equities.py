"""
Walk-forward real del setup de swing (momentum + RSI sano + cerca de
máximos + volumen) sobre el universo de equities propuesto en
PLAN_CONSTRUCCION.md: CRM, WFC, SLB, ORCL, FSLR, BSBR.

Retoma el research de 03/08/2026 (ver memoria project_swing_trading_equities)
que había quedado con un backtest estático flojo (40,4% aciertos, CRM en
duda, SLB con edge) y una segunda vuelta filtrada nunca completada. Esta vez:
walk-forward por ventanas (no un solo número agregado) + comparación contra
comprar-y-mantener en la MISMA ventana, siguiendo la disciplina ya
establecida en el resto de este proyecto (ver walk_forward_harness.py).

Parámetros de la estrategia: FIJOS de manual, no se tocan mirando el
resultado (ver strategy_swing_momentum.py).
"""
import os

import pandas as pd

from strategy_swing_momentum import strategy_swing_momentum
from walk_forward_harness import walk_forward

TICKERS = ["CRM", "WFC", "SLB", "ORCL", "FSLR", "BSBR"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
N_WINDOWS = 5


def load_ticker(ticker: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, f"swing_{ticker.lower()}_daily.csv")
    df = pd.read_csv(path, index_col=0, header=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(columns={"adj close": "close"})
    return df[["open", "high", "low", "close", "volume"]].sort_index()


def main():
    resumen_agregado = []

    for ticker in TICKERS:
        print(f"\n{'=' * 70}\n{ticker}\n{'=' * 70}")
        df = load_ticker(ticker)
        resultados = walk_forward(
            df, strategy_swing_momentum, n_windows=N_WINDOWS,
            strategy_name=f"swing_momentum_{ticker}", cost_bps=5.0, verbose=True,
        )
        for r in resultados:
            resumen_agregado.append({
                "ticker": ticker,
                "ventana": r["ventana"],
                "desde": r["desde"].date(), "hasta": r["hasta"].date(),
                "estrategia_%": r["estrategia"]["retorno_total_%"],
                "buy_hold_%": r["buy_hold"]["retorno_total_%"],
                "gano_vs_bh": r["estrategia_le_gano_a_bh"],
                "n_barras_en_posicion": r["estrategia"]["n_barras_con_movimiento"],
                "win_rate_%": r["estrategia"]["win_rate_%"],
            })

    resumen_df = pd.DataFrame(resumen_agregado)
    pd.set_option("display.width", 140)
    pd.set_option("display.max_rows", 200)
    print(f"\n\n{'#' * 70}\nRESUMEN COMPLETO — todas las ventanas, todos los tickers\n{'#' * 70}")
    print(resumen_df.to_string(index=False))

    print(f"\n{'#' * 70}\nAGREGADO POR TICKER (cuántas ventanas de {N_WINDOWS} le ganó a buy-and-hold)\n{'#' * 70}")
    por_ticker = resumen_df.groupby("ticker").agg(
        ventanas_ganadas=("gano_vs_bh", "sum"),
        ventanas_totales=("gano_vs_bh", "count"),
        retorno_estrategia_prom_pct=("estrategia_%", "mean"),
        retorno_bh_prom_pct=("buy_hold_%", "mean"),
    )
    print(por_ticker.to_string())

    out_path = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_path, exist_ok=True)
    resumen_df.to_csv(os.path.join(out_path, "walk_forward_swing_equities.csv"), index=False)
    print(f"\nGuardado detalle en results/walk_forward_swing_equities.csv")


if __name__ == "__main__":
    main()
