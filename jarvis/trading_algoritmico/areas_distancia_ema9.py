"""
Estadística por ÁREAS de distancia a la EMA9 (no solo toca/surfea) -- a
pedido de Diego (14/08/2026): en vez de una sola línea, dividir el espacio
alrededor de la EMA9 en bandas (por default 0-0,5 / 0,5-1 / 1-1,5 / 1,5-2 /
2+ ATR, arriba y abajo) y medir qué pasa históricamente cuando el precio
está en cada una. Misma fórmula que envolvente_ema9_areas.pine, para que
lo que se ve en el gráfico coincida con lo que mide este script.

Para cada área se mide:
  - Cuántos días (de toda la historia) cayeron ahí, y qué % del total.
  - El retorno promedio de los siguientes 1, 3 y 5 días (cerrando desde el
    cierre del día en esa área) -- para ver si estar en un área particular
    anticipa algo sobre lo que viene, o es todo parecido.

Uso:
    python3 areas_distancia_ema9.py                          # bandas default
    python3 areas_distancia_ema9.py --bandas 0.5,1,1.5,2,3
    python3 areas_distancia_ema9.py --desde 2021-01-01
"""
import argparse
import os

import numpy as np
import pandas as pd

from strategy_ema9_surf import ema
from strategy_swing_momentum import atr

DATA_PATH = os.path.join(os.path.dirname(__file__), "data_xau_daily_15y.csv")


def clasificar_area(dist_atr: float, bandas: list) -> str:
    lado = "arriba" if dist_atr >= 0 else "abajo"
    d = abs(dist_atr)
    anterior = 0.0
    for b in bandas:
        if d <= b:
            return f"{lado}_{anterior}-{b}"
        anterior = b
    return f"{lado}_{bandas[-1]}+"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bandas", default="0.5,1,1.5,2", help="Límites de las bandas en ATR, separados por coma")
    parser.add_argument("--desde", default=None)
    parser.add_argument("--hasta", default=None)
    args = parser.parse_args()
    bandas = [float(x) for x in args.bandas.split(",")]

    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    df.columns = [c.lower() for c in df.columns]
    df = df.sort_index()

    df["ema9"] = ema(df["close"], 9)
    df["atr14"] = atr(df, 14)
    df["dist_atr"] = (df["close"] - df["ema9"]) / df["atr14"]
    df = df.dropna(subset=["ema9", "atr14"])

    df["area"] = df["dist_atr"].apply(lambda d: clasificar_area(d, bandas))

    # retornos futuros (desde el cierre del día en esa área)
    for n in (1, 3, 5):
        df[f"ret_fwd_{n}d"] = df["close"].shift(-n) / df["close"] - 1

    if args.desde:
        df = df[df.index >= args.desde]
    if args.hasta:
        df = df[df.index <= args.hasta]

    print("=" * 90)
    print(f"Estadística por área de distancia a EMA9 — {df.index[0].date()} a {df.index[-1].date()} ({len(df)} velas)")
    print("=" * 90)

    filas = []
    for area, grupo in df.groupby("area"):
        filas.append({
            "area": area,
            "dias": len(grupo),
            "%_del_total": round(len(grupo) / len(df) * 100, 1),
            "ret_fwd_1d_%": round(grupo["ret_fwd_1d"].mean() * 100, 3),
            "ret_fwd_3d_%": round(grupo["ret_fwd_3d"].mean() * 100, 3),
            "ret_fwd_5d_%": round(grupo["ret_fwd_5d"].mean() * 100, 3),
            "win_rate_fwd_1d_%": round((grupo["ret_fwd_1d"] > 0).mean() * 100, 1),
        })

    tabla = pd.DataFrame(filas)
    # ordenar: abajo de más lejos a más cerca, arriba de más cerca a más lejos
    orden_lado = tabla["area"].str.split("_").str[0]
    orden_num = tabla["area"].str.extract(r"_([\d.]+)")[0].astype(float)
    tabla["_orden"] = np.where(orden_lado == "abajo", -orden_num, orden_num)
    tabla = tabla.sort_values("_orden").drop(columns="_orden")

    pd.set_option("display.width", 140)
    print(tabla.to_string(index=False))

    out_path = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_path, exist_ok=True)
    tabla.to_csv(os.path.join(out_path, "areas_distancia_ema9.csv"), index=False)
    print(f"\nGuardado en results/areas_distancia_ema9.csv")


if __name__ == "__main__":
    main()
