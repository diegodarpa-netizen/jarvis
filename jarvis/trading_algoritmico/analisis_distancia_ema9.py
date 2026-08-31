"""
Analisis de distancia del precio a la EMA9 -- cuantas veces se mantiene
afuera, cuanto ruido hay, oportunidades en alza/baja, tanto intradia (M1)
como diario. A pedido de Diego (15/08/2026), a raiz de la imagen que
comparto de TradingView (precio vs EMA9/20/50/200 diario).
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


def resample_daily(df):
    """Un cierre por dia -- ultimo precio de la ventana de sesion de cada dia."""
    daily = df.groupby('day')['close'].last()
    daily.index = pd.to_datetime(daily.index)
    return daily.to_frame('close')


def ema9_and_streaks(close: pd.Series, span=9):
    """EMA9, signo (arriba/abajo), y duracion de rachas consecutivas del
    mismo signo (= band walk / cuanto se mantiene afuera)."""
    ema = close.ewm(span=span, adjust=False).mean()
    dist_pct = (close - ema) / ema * 100
    sign = np.sign(dist_pct)
    # identificar rachas consecutivas del mismo signo
    change = sign.diff().fillna(1) != 0
    group_id = change.cumsum()
    streaks = sign.groupby(group_id).agg(['first', 'count'])
    streaks.columns = ['signo', 'duracion']
    return ema, dist_pct, sign, streaks


def resumen(streaks: pd.DataFrame, unidad: str):
    n_arriba = (streaks['signo'] > 0).sum()
    n_abajo = (streaks['signo'] < 0).sum()
    total = len(streaks)
    dur_arriba = streaks.loc[streaks['signo'] > 0, 'duracion']
    dur_abajo = streaks.loc[streaks['signo'] < 0, 'duracion']
    print(f"\n--- Rachas de distancia a EMA9 ({unidad}) ---")
    print(f"  Total de rachas (cruces de EMA9): {total}")
    print(f"  Rachas en ALZA (precio arriba de EMA9): {n_arriba} ({n_arriba/total*100:.1f}%)")
    print(f"  Rachas en BAJA (precio abajo de EMA9): {n_abajo} ({n_abajo/total*100:.1f}%)")
    print(f"  Duracion promedio racha alza: {dur_arriba.mean():.2f} {unidad} | mediana: {dur_arriba.median():.1f} | max: {dur_arriba.max():.0f}")
    print(f"  Duracion promedio racha baja: {dur_abajo.mean():.2f} {unidad} | mediana: {dur_abajo.median():.1f} | max: {dur_abajo.max():.0f}")
    # "ruido" = rachas muy cortas (1-2 unidades) -- cruzo y volvio enseguida
    ruido = (streaks['duracion'] <= 2).sum()
    print(f"  Rachas de 'ruido' (duro <=2 {unidad}, cruzo y volvio ya): {ruido} ({ruido/total*100:.1f}% de todas las rachas)")
    extendidas = (streaks['duracion'] >= streaks['duracion'].quantile(0.75)).sum()
    p75 = streaks['duracion'].quantile(0.75)
    print(f"  Rachas 'extendidas' (>= percentil 75, {p75:.1f} {unidad}): {extendidas} ({extendidas/total*100:.1f}%)")
    return {'total': total, 'n_arriba': n_arriba, 'n_abajo': n_abajo,
            'dur_arriba_media': dur_arriba.mean(), 'dur_abajo_media': dur_abajo.mean(),
            'pct_ruido': ruido/total*100, 'p75_duracion': p75}


if __name__ == '__main__':
    df = load()
    print("="*70)
    print("DISTANCIA A EMA9 -- XAU/USD, 6 meses, ventana 08:00-11:30 NY")
    print("="*70)
    print(f"Velas M1: {len(df)} | Dias: {df['day'].nunique()}")

    # --- INTRADIA (M1), respetando sesiones por separado para no mezclar dias ---
    print("\n" + "#"*70)
    print("# NIVEL INTRADIA (M1) -- EMA9 recalculada AL INICIO de cada sesion")
    print("#"*70)
    all_streaks_intraday = []
    all_dist = []
    for day, g in df.groupby('day'):
        if len(g) < 15:
            continue
        ema, dist_pct, sign, streaks = ema9_and_streaks(g['close'])
        all_streaks_intraday.append(streaks)
        all_dist.append(dist_pct)
    streaks_intra = pd.concat(all_streaks_intraday, ignore_index=True)
    dist_intra = pd.concat(all_dist)
    r_intra = resumen(streaks_intra, "velas M1")
    print(f"\n  Distancia promedio absoluta (micro %, intradia): {dist_intra.abs().mean():.4f}%")
    print(f"  Distancia maxima observada (intradia): {dist_intra.abs().max():.3f}%")
    print(f"  Desvio estandar de la distancia (intradia): {dist_intra.std():.4f}%")

    # --- DIARIO ---
    print("\n" + "#"*70)
    print("# NIVEL DIARIO -- un cierre por dia, EMA9 sobre esa serie")
    print("#"*70)
    daily = resample_daily(df)
    ema_d, dist_d, sign_d, streaks_d = ema9_and_streaks(daily['close'])
    r_daily = resumen(streaks_d, "dias")
    print(f"\n  Distancia promedio absoluta (%, diario): {dist_d.abs().mean():.3f}%")
    print(f"  Distancia maxima observada (diario): {dist_d.abs().max():.3f}%")
    print(f"  Desvio estandar de la distancia (diario): {dist_d.std():.3f}%")

    print("\n" + "="*70)
    print("RESUMEN COMPARATIVO")
    print("="*70)
    print(f"{'Nivel':<12}{'% ruido (racha<=2)':<22}{'% arriba':<12}{'% abajo':<10}{'dur.media alza':<16}{'dur.media baja'}")
    print(f"{'Intradia':<12}{r_intra['pct_ruido']:<22.1f}{r_intra['n_arriba']/r_intra['total']*100:<12.1f}{r_intra['n_abajo']/r_intra['total']*100:<10.1f}{r_intra['dur_arriba_media']:<16.2f}{r_intra['dur_abajo_media']:.2f}")
    print(f"{'Diario':<12}{r_daily['pct_ruido']:<22.1f}{r_daily['n_arriba']/r_daily['total']*100:<12.1f}{r_daily['n_abajo']/r_daily['total']*100:<10.1f}{r_daily['dur_arriba_media']:<16.2f}{r_daily['dur_abajo_media']:.2f}")

    print("\nNota: esto es descriptivo (cuenta lo que paso), todavia NO es una")
    print("estrategia validada -- falta pasar por walk-forward antes de operar nada.")
