"""
Barrido de umbrales de distancia (entrada) x días de salida, para encontrar
la mejor combinación de "cuán lejos hay que estar de la EMA9 para entrar" y
"cuántos días conviene quedarse" -- a pedido de Diego (14/08/2026):
"entre más lejos se encuentre, el siguiente acompaña, hay una oportunidad
ahí".

OJO -- esto es un barrido de MUCHOS parámetros a la vez, que es
textualmente la definición de data snooping si el resultado "mejor" del
barrido se toma como validado sin más. Por eso el script:
  1. Muestra el barrido completo (para ver la forma general, no un
     número aislado).
  2. Separa arriba de abajo -- ya sabemos que no se comportan igual
     (ver bitácora 14/08: arriba acompaña, abajo tiende a rebotar).
  3. Al final, toma el candidato más razonable (no el pico más alto
     aislado, que suele ser ruido de muestra chica) y lo corre en
     walk-forward -- recién ahí se sabe si es real o si fue el mejor
     de muchos intentos por casualidad.

Uso:
    python3 sweep_areas_ema9.py
"""
import os

import numpy as np
import pandas as pd

from strategy_ema9_surf import ema
from strategy_swing_momentum import atr

DATA_PATH = os.path.join(os.path.dirname(__file__), "data_xau_daily_15y.csv")
UMBRALES = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
DIAS_SALIDA = [1, 3, 5, 10, 15]
MIN_MUESTRA = 30  # menos de esto, no se reporta -- muy poca muestra para significar algo


def preparar_datos(desde=None, hasta=None) -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    df.columns = [c.lower() for c in df.columns]
    df = df.sort_index()
    df["ema9"] = ema(df["close"], 9)
    df["atr14"] = atr(df, 14)
    df["dist_atr"] = (df["close"] - df["ema9"]) / df["atr14"]
    df = df.dropna(subset=["ema9", "atr14"])
    for n in DIAS_SALIDA:
        df[f"ret_fwd_{n}d"] = df["close"].shift(-n) / df["close"] - 1
    if desde:
        df = df[df.index >= desde]
    if hasta:
        df = df[df.index <= hasta]
    return df


def barrer(df: pd.DataFrame, lado: str) -> pd.DataFrame:
    """lado='arriba' -> comprar cuando dist_atr > umbral (apostando a que
    sigue subiendo). lado='abajo' -> comprar cuando dist_atr < -umbral
    (apostando al rebote, no a que siga cayendo -- así se comportó en la
    estadística por área)."""
    filas = []
    for umbral in UMBRALES:
        if lado == "arriba":
            mascara = df["dist_atr"] > umbral
        else:
            mascara = df["dist_atr"] < -umbral
        subset = df[mascara]
        if len(subset) < MIN_MUESTRA:
            continue
        fila = {"umbral_atr": umbral, "muestra": len(subset)}
        for n in DIAS_SALIDA:
            rets = subset[f"ret_fwd_{n}d"].dropna()
            fila[f"ret_{n}d_%"] = round(rets.mean() * 100, 3)
            fila[f"win_{n}d_%"] = round((rets > 0).mean() * 100, 1)
        filas.append(fila)
    return pd.DataFrame(filas)


def main():
    df = preparar_datos()
    print(f"Datos: {df.index[0].date()} a {df.index[-1].date()} ({len(df)} velas)\n")

    for lado, hipotesis in [("arriba", "comprar apostando a que sigue subiendo"),
                             ("abajo", "comprar apostando a que rebota")]:
        print("=" * 100)
        print(f"LADO: {lado.upper()} -- {hipotesis}")
        print("=" * 100)
        tabla = barrer(df, lado)
        if tabla.empty:
            print("Sin combinaciones con muestra suficiente.")
            continue
        pd.set_option("display.width", 160)
        print(tabla.to_string(index=False))
        print()

        # mejor combinación por win rate a 5 días, con muestra decente
        candidatos = tabla[tabla["muestra"] >= 50]
        if not candidatos.empty:
            mejor = candidatos.loc[candidatos["win_5d_%"].idxmax()]
            print(f"Mejor combinación (win rate 5d, muestra >= 50): umbral {mejor['umbral_atr']} ATR "
                  f"-> win rate {mejor['win_5d_%']}%, retorno prom. {mejor['ret_5d_%']}%, muestra {int(mejor['muestra'])}")
        print()


if __name__ == "__main__":
    main()
