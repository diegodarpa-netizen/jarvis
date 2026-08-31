"""
Analisis de "momentos de extension" (precio alejado de EMA9) en varias
resoluciones -- M1, M5, M15, M30, diario. A pedido de Diego (15/08/2026):
ver si el patron de extension sostenida se repite en distintas escalas de
tiempo, para una posible estrategia de entrada por distancia + salida
dinamica (mientras se mantenga alejado, la operacion sigue abierta).

NO se arma "4hs" -- cada sesion dura ~3.5hs (208 min), una barra de 4hs
cruzaria el gap entre sesiones (mismo problema de contaminacion ya
identificado con el consejo de Ernie Chan sobre gaps). Se deja pendiente
hasta ampliar la ventana horaria de los datos.
"""
import pandas as pd
import numpy as np

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'


def load():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    return df


def resample_within_session(df, rule):
    """Resamplea a `rule` (ej. '5min', '15min', '30min') PERO solo dentro
    de cada sesion -- devuelve una lista de Series, una por dia, para que
    el calculo de EMA/rachas tampoco cruce el gap entre sesiones despues."""
    out = []
    for day, g in df.groupby('day'):
        r = g['close'].resample(rule).last().dropna()
        if len(r) > 3:
            out.append(r)
    return out


def resample_daily(df):
    daily = df.groupby('day')['close'].last()
    daily.index = pd.to_datetime(daily.index)
    return daily


def ema9_streaks_single(close: pd.Series, span=9):
    """EMA9 y rachas sobre UNA sola serie continua (sin cortes)."""
    ema = close.ewm(span=span, adjust=False).mean()
    dist_pct = (close - ema) / ema * 100
    sign = np.sign(dist_pct)
    change = sign.diff().fillna(1) != 0
    group_id = change.cumsum()
    streaks = sign.groupby(group_id).agg(['first', 'count'])
    streaks.columns = ['signo', 'duracion']
    return streaks, dist_pct


def ema9_streaks(series_o_lista, span=9):
    """Si recibe una lista de series (una por sesion), calcula EMA/rachas
    POR SEPARADO en cada una y las agrupa -- nunca deja que una racha
    cruce de una sesion a la siguiente. Si recibe una sola serie continua
    (uso para diario, donde no hay gaps intra-dia), la trata directo."""
    if isinstance(series_o_lista, list):
        all_streaks, all_dist = [], []
        for s in series_o_lista:
            streaks, dist_pct = ema9_streaks_single(s, span=span)
            all_streaks.append(streaks)
            all_dist.append(dist_pct)
        return pd.concat(all_streaks, ignore_index=True), pd.concat(all_dist)
    else:
        return ema9_streaks_single(series_o_lista, span=span)


def analizar_resolucion(close: pd.Series, nombre: str, minutos_por_barra: float):
    streaks, dist_pct = ema9_streaks(close)
    total = len(streaks)
    p75 = streaks['duracion'].quantile(0.75)
    extendidas = streaks[streaks['duracion'] >= p75]
    n_extendidas = len(extendidas)
    dur_media_ext_barras = extendidas['duracion'].mean()
    dur_media_ext_minutos = dur_media_ext_barras * minutos_por_barra if minutos_por_barra else None
    ruido = (streaks['duracion'] <= 2).sum()
    n_arriba_ext = (extendidas['signo'] > 0).sum()
    n_abajo_ext = (extendidas['signo'] < 0).sum()
    return {
        'resolucion': nombre,
        'total_rachas': total,
        'pct_ruido': round(ruido / total * 100, 1) if total else None,
        'n_momentos_extension': n_extendidas,
        'pct_momentos_extension': round(n_extendidas / total * 100, 1) if total else None,
        'dur_media_ext_barras': round(dur_media_ext_barras, 2) if n_extendidas else None,
        'dur_media_ext_en_minutos_reales': round(dur_media_ext_minutos, 1) if (n_extendidas and dur_media_ext_minutos is not None) else None,
        'momentos_alza_ext': int(n_arriba_ext), 'momentos_baja_ext': int(n_abajo_ext),
        'distancia_media_abs_%': round(dist_pct.abs().mean(), 4),
    }


if __name__ == '__main__':
    df = load()
    print("="*90)
    print("MOMENTOS DE EXTENSION vs EMA9 -- multi-resolucion, XAU/USD 6 meses")
    print("="*90)

    resultados = []

    m1 = [g['close'] for day, g in df.groupby('day') if len(g) > 3]
    resultados.append(analizar_resolucion(m1, 'M1', 1))

    m5 = resample_within_session(df, '5min')
    resultados.append(analizar_resolucion(m5, 'M5', 5))

    m15 = resample_within_session(df, '15min')
    resultados.append(analizar_resolucion(m15, 'M15', 15))

    m30 = resample_within_session(df, '30min')
    resultados.append(analizar_resolucion(m30, 'M30', 30))

    daily = resample_daily(df)
    # para diario, "minutos por barra" no aplica -- se reporta en dias directamente
    r_daily = analizar_resolucion(daily, 'Diario', None)
    resultados.append(r_daily)

    tabla = pd.DataFrame(resultados)
    print("\n", tabla.to_string(index=False))

    print("\n--- Lectura por columna ---")
    print("total_rachas: cuantas veces cruzo la EMA9 en total en los 6 meses")
    print("pct_ruido: % de esas rachas que duraron <=2 barras (cruzo y volvio ya)")
    print("n_momentos_extension / pct_momentos_extension: cuantas rachas fueron 'extendidas' (percentil 75 de duracion para esa resolucion)")
    print("dur_media_ext_barras: duracion promedio de una racha extendida, en barras de esa resolucion")
    print("dur_media_ext_en_minutos_reales: lo mismo pero convertido a minutos reales, para comparar resoluciones entre si (no aplica a diario)")
    print("momentos_alza_ext / momentos_baja_ext: de las rachas extendidas, cuantas fueron al alza vs a la baja")
    print("distancia_media_abs_%: que tan lejos, en promedio, se aleja el precio de la EMA9 en esa resolucion")

    print("\nNota: sigue siendo descriptivo. La proxima pieza (pendiente, no corrida")
    print("todavia) es simular la regla real -- entrar cuando arranca una racha,")
    print("mantener mientras dure la extension, salir cuando empieza a revertir --")
    print("y medir el resultado en $ con walk-forward, no solo contar momentos.")
