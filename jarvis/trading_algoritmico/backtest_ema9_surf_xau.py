"""
Backtest de la estrategia propia de Diego (surfear la EMA 9) sobre XAU/USD
diario. Dos partes:

1. Réplica exacta de lo que Diego probó a mano: oro diario desde enero 2026.
   Acá se listan las operaciones una por una para que se puedan comparar
   contra lo que él vio en el gráfico — si algo no coincide, seguramente
   sea la interpretación de una regla puntual (ver docstring de
   strategy_ema9_surf.py), no un error de cálculo.

2. Walk-forward sobre más historia (2021-2026, con walk_forward_harness.py)
   — porque enero-agosto 2026 son ~7 meses, muestra chica para sacar
   conclusiones fuertes (misma lección que ya aplicamos con XAU: 4
   operaciones no alcanzan para juzgar nada).
"""
import os

import pandas as pd

from strategy_ema9_surf import strategy_ema9_surf, ema
from walk_forward_harness import walk_forward

DATA_PATH = os.path.join(os.path.dirname(__file__), "data_xau_daily_15y.csv")
COST_BPS = 2.0  # costo de transacción aproximado por cambio de posición


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    df.columns = [c.lower() for c in df.columns]
    return df.sort_index()


def extraer_operaciones(df: pd.DataFrame, positions: pd.Series, ema_vals: pd.Series, touches: pd.Series) -> pd.DataFrame:
    """Convierte la serie de posiciones {-1,0,1} en una lista de operaciones
    discretas. Precio de salida: si la salida fue por TOQUE de la EMA (el
    stop-loss real, según lo que aclaró Diego el 14/08 — la distancia a la
    EMA9 ES el stop), se usa el valor de la EMA9 en esa vela, no el cierre
    — el cierre puede quedar mucho peor que el nivel real del stop en una
    vela que se mueve fuerte ese día. Si la salida fue por "salto limpio"
    al lado contrario (sin toque) o quedó abierta al final, se usa el
    cierre porque ahí no hay un nivel de stop definido."""
    trades = []
    dir_actual = 0
    entrada_idx = None
    entrada_precio = None

    for i in range(len(positions)):
        pos = positions.iloc[i]
        if dir_actual == 0 and pos != 0:
            dir_actual = pos
            entrada_idx = positions.index[i]
            entrada_precio = df["close"].iloc[i]
        elif dir_actual != 0 and pos == 0:
            salida_idx = positions.index[i]
            fue_por_toque = bool(touches.iloc[i])
            salida_precio = ema_vals.iloc[i] if fue_por_toque else df["close"].iloc[i]
            ret_pct = (salida_precio / entrada_precio - 1) * 100 * dir_actual
            trades.append({
                "direccion": "COMPRA" if dir_actual == 1 else "VENTA",
                "entrada_fecha": entrada_idx.date(), "entrada_precio": round(entrada_precio, 2),
                "salida_fecha": salida_idx.date(), "salida_precio": round(salida_precio, 2),
                "motivo_salida": "toque EMA9 (stop)" if fue_por_toque else "salto limpio al lado contrario",
                "retorno_%": round(ret_pct, 2),
                "resultado": "GANADORA" if ret_pct > 0 else "PERDEDORA",
            })
            dir_actual = 0

    # si quedó una posición abierta al final del período
    if dir_actual != 0:
        salida_idx = positions.index[-1]
        salida_precio = df["close"].iloc[-1]
        ret_pct = (salida_precio / entrada_precio - 1) * 100 * dir_actual
        trades.append({
            "direccion": "COMPRA" if dir_actual == 1 else "VENTA",
            "entrada_fecha": entrada_idx.date(), "entrada_precio": round(entrada_precio, 2),
            "salida_fecha": salida_idx.date(), "salida_precio": round(salida_precio, 2),
            "motivo_salida": "-",
            "retorno_%": round(ret_pct, 2),
            "resultado": "ABIERTA al final del período",
        })
    return pd.DataFrame(trades)


def main():
    df = load_data()

    # --- Parte 1: réplica exacta, oro diario desde enero 2026 ---
    # OJO: las operaciones se extraen sobre la SERIE COMPLETA (no recortada
    # a enero) para no perder el precio real de entrada de una operación que
    # ya venía abierta de diciembre -- después se filtra la tabla a lo que
    # cae dentro de la ventana, marcando si la entrada fue anterior a ella.
    ema_vals = ema(df["close"], 9)
    touches = (df["low"] <= ema_vals) & (ema_vals <= df["high"])
    positions_full = strategy_ema9_surf(df, ema_period=9)
    trades_full = extraer_operaciones(df, positions_full, ema_vals, touches)

    print("=" * 70)
    print("PARTE 1 — Oro diario desde enero 2026 (réplica de la prueba de Diego)")
    print("=" * 70)
    ventana_inicio = pd.Timestamp("2026-01-01")
    en_ventana = trades_full[
        (pd.to_datetime(trades_full["salida_fecha"]) >= ventana_inicio)
    ].copy()
    en_ventana["entrada_previa_a_la_ventana"] = pd.to_datetime(en_ventana["entrada_fecha"]) < ventana_inicio
    trades = en_ventana
    if trades.empty:
        print("La regla no generó ninguna operación en este período.")
    else:
        print(trades.to_string(index=False))
        ganadoras = (trades["resultado"] == "GANADORA").sum()
        cerradas = trades[trades["resultado"] != "ABIERTA al final del período"]
        win_rate = (cerradas["resultado"] == "GANADORA").mean() * 100 if len(cerradas) else float("nan")
        retorno_total = trades["retorno_%"].sum()
        print(f"\nOperaciones: {len(trades)} | Ganadoras: {ganadoras} | Win rate: {win_rate:.1f}%")
        print(f"Retorno acumulado (suma simple de %, sin compuesto): {retorno_total:.2f}%")

    df_2026 = df[df.index >= ventana_inicio]
    precio_inicio = df_2026["close"].iloc[0]
    precio_fin = df_2026["close"].iloc[-1]
    bh_ret = (precio_fin / precio_inicio - 1) * 100
    print(f"\nComprar y mantener en el mismo período: {bh_ret:.2f}% "
          f"(${precio_inicio:.2f} -> ${precio_fin:.2f})")

    # --- Parte 2: walk-forward con más historia ---
    print("\n" + "=" * 70)
    print("PARTE 2 — Walk-forward 2021-2026 (5 ventanas ~1 año, más muestra)")
    print("=" * 70)
    df_wf = df[df.index >= "2021-01-01"].copy()
    resultados = walk_forward(
        df_wf, lambda w: strategy_ema9_surf(w, ema_period=9),
        n_windows=5, strategy_name="ema9_surf_XAU", cost_bps=COST_BPS, verbose=True,
    )
    ventanas_ganadas = sum(r["estrategia_le_gano_a_bh"] for r in resultados)
    print(f"\nVentanas ganadas vs. buy-and-hold: {ventanas_ganadas} de {len(resultados)}")


if __name__ == "__main__":
    main()
