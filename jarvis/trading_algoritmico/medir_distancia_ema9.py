"""
Herramienta para medir la distancia entre la vela y la EMA9 — en dólares,
en % y en unidades de ATR14 (la unidad comparable entre épocas, ver
estadistica_distancia_ema9.py). Reutiliza las mismas funciones ema()/atr()
que ya usa el resto del proyecto, para que el número sea siempre el mismo
diga lo que diga cualquier otro script.

Uso:
    python3 medir_distancia_ema9.py                    # últimas 10 velas
    python3 medir_distancia_ema9.py --n 30              # últimas 30 velas
    python3 medir_distancia_ema9.py --fecha 2026-01-30   # una vela puntual
"""
import argparse
import os

import pandas as pd

from strategy_ema9_surf import ema
from strategy_swing_momentum import atr

DATA_PATH = os.path.join(os.path.dirname(__file__), "data_xau_daily_15y.csv")


def calcular_distancia(df: pd.DataFrame, ema_period: int = 9, atr_period: int = 14) -> pd.DataFrame:
    """Devuelve el mismo df con columnas nuevas: ema9, atr14, dist_dolares,
    dist_pct, dist_atr (signo: positivo = vela arriba de la EMA, negativo =
    abajo) y estado (surfea_arriba / surfea_abajo / toca)."""
    out = df.copy()
    out["ema9"] = ema(out["close"], ema_period)
    out["atr14"] = atr(out, atr_period)
    out["dist_dolares"] = out["close"] - out["ema9"]
    out["dist_pct"] = out["dist_dolares"] / out["ema9"] * 100
    out["dist_atr"] = out["dist_dolares"] / out["atr14"]

    toca = (out["low"] <= out["ema9"]) & (out["ema9"] <= out["high"])
    surf_arriba = out["low"] > out["ema9"]
    out["estado"] = "toca"
    out.loc[surf_arriba, "estado"] = "surfea_arriba"
    out.loc[~toca & ~surf_arriba, "estado"] = "surfea_abajo"
    return out


def main():
    parser = argparse.ArgumentParser(description="Mide la distancia vela-EMA9 en oro diario")
    parser.add_argument("--n", type=int, default=10, help="Cuántas últimas velas mostrar (default 10)")
    parser.add_argument("--fecha", type=str, default=None, help="Ver una fecha puntual (YYYY-MM-DD) en vez de las últimas N")
    args = parser.parse_args()

    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    df.columns = [c.lower() for c in df.columns]
    df = df.sort_index()

    resultado = calcular_distancia(df)
    cols = ["close", "ema9", "dist_dolares", "dist_pct", "dist_atr", "estado"]

    if args.fecha:
        fila = resultado.loc[resultado.index.date.astype(str) == args.fecha]
        if fila.empty:
            print(f"No hay vela para {args.fecha} (¿es fin de semana/feriado, o está fuera del rango de datos?)")
            return
        print(fila[cols].round(2).to_string())
    else:
        print(resultado[cols].tail(args.n).round(2).to_string())


if __name__ == "__main__":
    main()
