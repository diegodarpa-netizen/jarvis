"""
Estadística de la distancia precio-EMA9 en oro diario (15 años) — a pedido
de Diego (14/08/2026): antes de definir el stop como "toca = sale", medir
si la distancia a la EMA9 se achica de forma detectable ANTES de un toque
real, y sobre todo, si esa "bajada" se puede distinguir estadísticamente
de una bajada que después sigue de largo (falsa alarma / ruido normal).

Distancia normalizada en unidades de ATR(14) -- no en dólares ni en %,
porque la volatilidad del oro cambió mucho en 15 años (no es lo mismo un
movimiento de US$20 en 2015 que en 2026) y en unidades de ATR sí es
comparable entre épocas.

Metodología:
  1. Se identifican "corridas" (runs): tramos de velas consecutivas
     surfeando el mismo lado de la EMA9, terminan cuando una vela la toca.
  2. Cada corrida que termina en toque se clasifica según lo que pasa
     DESPUÉS: si la próxima corrida "limpia" (2+ velas seguidas surfeando)
     es del MISMO lado -> "continuación" (el toque fue ruido/sacudida).
     Si es del lado CONTRARIO -> "reversión" (el toque anticipó un cambio
     de tendencia real).
  3. Se compara la distancia (en ATR) 1, 2 y 3 velas antes del toque entre
     ambos grupos -- si continuación y reversión no se distinguen ahí, la
     distancia sola no alcanza como señal de salida anticipada.
"""
import os

import numpy as np
import pandas as pd

from strategy_ema9_surf import ema
from strategy_swing_momentum import atr

DATA_PATH = os.path.join(os.path.dirname(__file__), "data_xau_daily_15y.csv")


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    df.columns = [c.lower() for c in df.columns]
    return df.sort_index()


def main():
    df = load_data()
    df["ema9"] = ema(df["close"], 9)
    df["atr14"] = atr(df, 14)
    df["dist_atr"] = (df["close"] - df["ema9"]) / df["atr14"]  # positivo = arriba, negativo = abajo

    df["touches"] = (df["low"] <= df["ema9"]) & (df["ema9"] <= df["high"])
    df["surf_bull"] = df["low"] > df["ema9"]
    df["surf_bear"] = df["high"] < df["ema9"]

    df = df.dropna(subset=["ema9", "atr14"]).reset_index()

    # --- 1) Distribución general de la distancia mientras se surfea ---
    surfing = df[df["surf_bull"] | df["surf_bear"]]
    print("=" * 70)
    print("Distribución de |distancia a EMA9| en unidades de ATR14, mientras se surfea")
    print("=" * 70)
    print(surfing["dist_atr"].abs().describe(percentiles=[.1, .25, .5, .75, .9]).round(2).to_string())

    # --- 2) Identificar corridas (runs) ---
    runs = []
    dir_actual = 0
    inicio_idx = None
    distancias_run = []

    for i in range(len(df)):
        if df["surf_bull"].iloc[i]:
            lado = 1
        elif df["surf_bear"].iloc[i]:
            lado = -1
        else:
            lado = 0  # toque

        if lado != 0 and lado == dir_actual:
            distancias_run.append(df["dist_atr"].iloc[i])
        elif lado != 0 and lado != dir_actual:
            if dir_actual != 0 and len(distancias_run) >= 1:
                runs.append({"dir": dir_actual, "fin_idx": i - 1, "distancias": distancias_run})
            dir_actual = lado
            distancias_run = [df["dist_atr"].iloc[i]]
        elif lado == 0 and dir_actual != 0:
            runs.append({"dir": dir_actual, "fin_idx": i - 1, "distancias": distancias_run})
            dir_actual = 0
            distancias_run = []

    # --- 3) Clasificar cada corrida: continuación vs reversión ---
    def proxima_corrida_limpia(desde_idx: int):
        """Busca hacia adelante la próxima corrida de 2+ velas seguidas
        surfeando el mismo lado -- devuelve su dirección, o None si no
        hay ninguna clara en los siguientes 30 días."""
        lado_actual, racha = 0, 0
        for j in range(desde_idx, min(desde_idx + 30, len(df))):
            if df["surf_bull"].iloc[j]:
                lado = 1
            elif df["surf_bear"].iloc[j]:
                lado = -1
            else:
                lado = 0
            if lado != 0 and lado == lado_actual:
                racha += 1
                if racha >= 2:
                    return lado
            elif lado != 0:
                lado_actual, racha = lado, 1
            else:
                lado_actual, racha = 0, 0
        return None

    for r in runs:
        siguiente = proxima_corrida_limpia(r["fin_idx"] + 1)
        if siguiente is None:
            r["resultado"] = "indeterminado"
        elif siguiente == r["dir"]:
            r["resultado"] = "continuacion"
        else:
            r["resultado"] = "reversion"
        d = r["distancias"]
        r["dist_1_antes"] = abs(d[-1]) if len(d) >= 1 else np.nan
        r["dist_2_antes"] = abs(d[-2]) if len(d) >= 2 else np.nan
        r["dist_3_antes"] = abs(d[-3]) if len(d) >= 3 else np.nan
        r["dist_max"] = max(abs(x) for x in d)
        r["largo"] = len(d)

    runs_df = pd.DataFrame(runs)
    print(f"\nTotal de corridas identificadas: {len(runs_df)}")
    print(runs_df["resultado"].value_counts().to_string())

    print("\n" + "=" * 70)
    print("¿La distancia justo antes del toque distingue continuación de reversión?")
    print("=" * 70)
    comparables = runs_df[runs_df["resultado"].isin(["continuacion", "reversion"])]
    for col in ["dist_1_antes", "dist_2_antes", "dist_3_antes", "dist_max", "largo"]:
        print(f"\n--- {col} ---")
        print(comparables.groupby("resultado")[col].describe(percentiles=[.25, .5, .75]).round(2).to_string())

    out_path = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_path, exist_ok=True)
    runs_df.drop(columns=["distancias"]).to_csv(os.path.join(out_path, "estadistica_distancia_ema9_runs.csv"), index=False)
    print(f"\nGuardado detalle de corridas en results/estadistica_distancia_ema9_runs.csv")


if __name__ == "__main__":
    main()
