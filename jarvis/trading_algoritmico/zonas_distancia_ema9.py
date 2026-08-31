"""
Analisis por zonas de distancia a la EMA9 -- para cada zona (0-0.5%,
0.5-1%, 1-2%, etc.), que retorno dio el dia/periodo SIGUIENTE en promedio.
A pedido de Diego (15/08/2026): entender que zona de distancia conviene
para entrar y cual para salir, no solo mirar la racha completa.
"""
import pandas as pd
import numpy as np

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'

BANDAS = [0, 0.5, 1, 2, 4, np.inf]  # en % de distancia absoluta


def load_daily():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    daily = df.groupby('day')['close'].last()
    daily.index = pd.to_datetime(daily.index)
    return daily


def analizar_zonas(close: pd.Series, unidad: str, bandas=BANDAS):
    ema = close.ewm(span=9, adjust=False).mean()
    dist_pct = (close - ema) / ema * 100
    dist_abs = dist_pct.abs()
    signo = np.sign(dist_pct)

    # retorno del periodo SIGUIENTE (t+1 respecto a t), en la misma direccion del signo actual
    ret_siguiente = close.pct_change().shift(-1) * 100 * signo  # orientado: positivo = a favor de la direccion actual

    zona = pd.cut(dist_abs, bins=bandas, labels=[f"{bandas[i]}-{bandas[i+1]}%" for i in range(len(bandas)-1)])

    tabla = pd.DataFrame({'zona': zona, 'ret_siguiente_%': ret_siguiente, 'signo': signo}).dropna()

    print(f"\n--- Zonas de distancia a EMA9 ({unidad}) -- retorno del siguiente periodo, orientado a favor de la direccion actual ---")
    resumen = tabla.groupby('zona', observed=True).agg(
        n=('ret_siguiente_%', 'count'),
        retorno_medio=('ret_siguiente_%', 'mean'),
        retorno_mediana=('ret_siguiente_%', 'median'),
        win_rate=('ret_siguiente_%', lambda x: (x > 0).mean() * 100),
    )
    print(resumen.round(4).to_string())
    return resumen


if __name__ == '__main__':
    daily = load_daily()
    print("="*80)
    print("ZONAS DE DISTANCIA A EMA9 -- que pasa el PERIODO SIGUIENTE segun la zona")
    print("="*80)
    r_daily = analizar_zonas(daily, "diario")

    # Intradia: por sesion, para no cruzar el gap entre dias
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    tablas = []
    for day, g in df.groupby('day'):
        if len(g) < 15:
            continue
        ema = g['close'].ewm(span=9, adjust=False).mean()
        dist_pct = (g['close'] - ema) / ema * 100
        dist_abs = dist_pct.abs()
        signo = np.sign(dist_pct)
        ret_sig = g['close'].pct_change().shift(-1) * 100 * signo
        zona = pd.cut(dist_abs, bins=BANDAS, labels=[f"{BANDAS[i]}-{BANDAS[i+1]}%" for i in range(len(BANDAS)-1)])
        tablas.append(pd.DataFrame({'zona': zona, 'ret_siguiente_%': ret_sig}).dropna())
    tabla_m1 = pd.concat(tablas, ignore_index=True)
    print(f"\n--- Zonas de distancia a EMA9 (M1, todas las sesiones agrupadas) ---")
    resumen_m1 = tabla_m1.groupby('zona', observed=True).agg(
        n=('ret_siguiente_%', 'count'),
        retorno_medio=('ret_siguiente_%', 'mean'),
        retorno_mediana=('ret_siguiente_%', 'median'),
        win_rate=('ret_siguiente_%', lambda x: (x > 0).mean() * 100),
    )
    print(resumen_m1.round(5).to_string())

    print("\nLectura: retorno_medio positivo = a favor de que la tendencia actual CONTINUE.")
    print("retorno_medio negativo = a favor de que empiece a REVERTIR en esa zona.")
    print("n = cuantas observaciones hay en esa zona -- ojo con zonas con pocos datos.")
