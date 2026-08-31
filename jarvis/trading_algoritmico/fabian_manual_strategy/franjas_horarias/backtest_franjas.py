"""
Backtest real (con SL/TP, RR=0.9 -- mismos parametros que el resto del
proyecto) de las señales del motor calibrado a lo largo de las 24hs, sobre
la muestra de 40 dias ya descargada (27/10-19/12/2025). Sin el circuit
breaker diario de Fabian (1 TP o 2 SL) -- ese breaker fue diseñado para su
ventana angosta de 2hs, aplicarlo a 24hs cortaria la exploracion despues
del primer trade del dia. Una posicion a la vez (no solapadas).
"""
import pandas as pd
import numpy as np
import pytz
import sys
sys.path.append('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy')
from prueba_ventana_horaria import tipo_envolvente, es_start, MIN_BREAK_PCT, MAX_SL_PIPS, RR

NY = pytz.timezone('America/New_York')
UTC = pytz.UTC
INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/data/XAUUSD_M1_24h_fabian.csv'


def tramos_continuos(df, max_hueco=pd.Timedelta(hours=2)):
    diffs = df.index.to_series().diff()
    cortes = diffs[diffs > max_hueco].index
    limites = [df.index[0]] + list(cortes) + [df.index[-1] + pd.Timedelta(minutes=1)]
    tramos = []
    for i in range(len(limites) - 1):
        ini, fin = limites[i], limites[i + 1]
        tramo = df[(df.index >= ini) & (df.index < fin)]
        if len(tramo) >= 30:
            tramos.append(tramo)
    return tramos


def backtest_tramo_24h(g: pd.DataFrame):
    """Igual logica que backtest_dia() pero SIN circuit breaker diario --
    una posicion a la vez, se abre en cualquier hora."""
    m3 = g.resample('3min').agg(open=('open', 'first'), high=('high', 'max'),
                                 low=('low', 'min'), close=('close', 'last')).dropna()
    if len(m3) < 3:
        return []

    o_arr, h_arr, l_arr, c_arr = g['open'].values, g['high'].values, g['low'].values, g['close'].values
    m1_idx = list(g.index)

    alto_level, bajo_level = np.nan, np.nan
    alto_prev, bajo_prev = np.nan, np.nan
    tend_state = 0
    ultimo_quiebre = np.nan
    mec_fase_a, mec_extremo_a = 0, np.nan
    mec_fase_b, mec_extremo_b = 0, np.nan

    trades = []
    en_posicion = False
    direccion_pos = entrada_precio = sl_precio = tp_precio = t_entrada = None

    for i in range(2, len(g)):
        t = m1_idx[i]
        m3_cerradas = m3[m3.index + pd.Timedelta(minutes=3) <= t]
        if len(m3_cerradas) >= 2:
            v1, v2 = m3_cerradas.iloc[-1], m3_cerradas.iloc[-2]
            if v2['close'] > v2['open'] and v1['close'] < v1['open']:
                nivel = max(v2['high'], v1['high'])
                if np.isnan(alto_level) or nivel != alto_level:
                    alto_prev, alto_level = alto_level, nivel
            if v2['close'] < v2['open'] and v1['close'] > v1['open']:
                nivel = min(v2['low'], v1['low'])
                if np.isnan(bajo_level) or nivel != bajo_level:
                    bajo_prev, bajo_level = bajo_level, nivel

        close_i = c_arr[i]
        choc_alcista = choc_bajista = False
        if tend_state <= 0 and not np.isnan(alto_level) and h_arr[i] > alto_level * (1 + MIN_BREAK_PCT):
            choc_alcista, tend_state, ultimo_quiebre = True, 1, alto_level
        elif tend_state == 1 and not np.isnan(alto_level) and h_arr[i] > alto_level * (1 + MIN_BREAK_PCT):
            ultimo_quiebre = alto_level
        if tend_state >= 0 and not np.isnan(bajo_level) and l_arr[i] < bajo_level * (1 - MIN_BREAK_PCT):
            choc_bajista, tend_state, ultimo_quiebre = True, -1, bajo_level
        elif tend_state == -1 and not np.isnan(bajo_level) and l_arr[i] < bajo_level * (1 - MIN_BREAK_PCT):
            ultimo_quiebre = bajo_level

        if choc_alcista:
            mec_fase_a, mec_extremo_a = 1, h_arr[i]
        elif mec_fase_a == 1:
            if c_arr[i] < o_arr[i]:
                mec_fase_a = 2
            else:
                mec_extremo_a = max(mec_extremo_a, h_arr[i])
        if choc_bajista:
            mec_fase_b, mec_extremo_b = 1, l_arr[i]
        elif mec_fase_b == 1:
            if c_arr[i] > o_arr[i]:
                mec_fase_b = 2
            else:
                mec_extremo_b = min(mec_extremo_b, l_arr[i])

        env_alcista = tipo_envolvente(o_arr[i], h_arr[i], l_arr[i], c_arr[i], True)
        env_bajista = tipo_envolvente(o_arr[i], h_arr[i], l_arr[i], c_arr[i], False)
        patron_alcista = (env_alcista in (1, 2)) or es_start(o_arr, h_arr, l_arr, c_arr, i, 1)
        patron_bajista = (env_bajista in (1, 2)) or es_start(o_arr, h_arr, l_arr, c_arr, i, -1)

        if en_posicion:
            if direccion_pos == 1:
                if l_arr[i] <= sl_precio:
                    trades.append({'t_entrada': t_entrada, 'R': -1.0, 'direccion': 1})
                    en_posicion = False
                elif h_arr[i] >= tp_precio:
                    trades.append({'t_entrada': t_entrada, 'R': RR, 'direccion': 1})
                    en_posicion = False
            else:
                if h_arr[i] >= sl_precio:
                    trades.append({'t_entrada': t_entrada, 'R': -1.0, 'direccion': -1})
                    en_posicion = False
                elif l_arr[i] <= tp_precio:
                    trades.append({'t_entrada': t_entrada, 'R': RR, 'direccion': -1})
                    en_posicion = False

        if not en_posicion:
            mecA_long = tend_state == 1 and not np.isnan(ultimo_quiebre) and h_arr[i] > ultimo_quiebre * (1 + MIN_BREAK_PCT) and patron_alcista
            mecA_short = tend_state == -1 and not np.isnan(ultimo_quiebre) and l_arr[i] < ultimo_quiebre * (1 - MIN_BREAK_PCT) and patron_bajista
            mecB_long = mec_fase_a == 2 and h_arr[i] > mec_extremo_a * (1 + MIN_BREAK_PCT) and patron_alcista
            mecB_short = mec_fase_b == 2 and l_arr[i] < mec_extremo_b * (1 - MIN_BREAK_PCT) and patron_bajista
            mer_long = choc_alcista and env_alcista in (1, 2) and (np.isnan(alto_prev) or abs(alto_level - alto_prev) / alto_level <= MIN_BREAK_PCT)
            mer_short = choc_bajista and env_bajista in (1, 2) and (np.isnan(bajo_prev) or abs(bajo_level - bajo_prev) / bajo_level <= MIN_BREAK_PCT)

            if mecB_long or choc_bajista:
                mec_fase_a, mec_extremo_a = 0, np.nan
            if mecB_short or choc_alcista:
                mec_fase_b, mec_extremo_b = 0, np.nan

            entra_long = mecA_long or mecB_long or (mer_long and not (mecA_long or mecB_long))
            entra_short = mecA_short or mecB_short or (mer_short and not (mecA_short or mecB_short))

            if entra_long and not np.isnan(bajo_level):
                dist = close_i - bajo_level
                if dist * 100 > MAX_SL_PIPS:
                    dist *= 0.6
                if dist > 0:
                    en_posicion, direccion_pos = True, 1
                    entrada_precio, t_entrada = close_i, t
                    sl_precio, tp_precio = close_i - dist, close_i + dist * RR
            elif entra_short and not np.isnan(alto_level):
                dist = alto_level - close_i
                if dist * 100 > MAX_SL_PIPS:
                    dist *= 0.6
                if dist > 0:
                    en_posicion, direccion_pos = True, -1
                    entrada_precio, t_entrada = close_i, t
                    sl_precio, tp_precio = close_i + dist, close_i - dist * RR
    return trades


if __name__ == '__main__':
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df = df[~df.index.duplicated(keep='last')]

    tramos = tramos_continuos(df)
    todos_trades = []
    for tramo in tramos:
        todos_trades.extend(backtest_tramo_24h(tramo))

    tr = pd.DataFrame(todos_trades)
    tr['t_ny'] = tr['t_entrada'].apply(lambda x: x.tz_convert(NY))
    tr['hora_ny'] = tr['t_ny'].dt.hour

    print(f"TOTAL operaciones (40 dias, 24hs, sin circuit breaker): {len(tr)}")
    print(f"Win rate global: {(tr['R']>0).mean()*100:.1f}% | R total: {tr['R'].sum():.1f} | R promedio: {tr['R'].mean():.4f}")

    print("\n--- Por hora NY de entrada ---")
    for h in range(24):
        sub = tr[tr['hora_ny'] == h]
        if len(sub) == 0:
            continue
        wr = (sub['R'] > 0).mean() * 100
        marca = ' <-- ventana Fabian' if h in (9, 10) else ''
        print(f"  {h:02d}:00  n={len(sub):3d}  WR={wr:5.1f}%  R_total={sub['R'].sum():+7.2f}  R_prom={sub['R'].mean():+.3f}{marca}")

    print("\n--- Por franja de sesión ---")
    franjas = {
        'Asia (19:00-03:59)': list(range(19, 24)) + list(range(0, 4)),
        'Londres (04:00-07:59)': list(range(4, 8)),
        'NY apertura (08:00-11:59)': list(range(8, 12)),
        'NY tarde (12:00-16:59)': list(range(12, 17)),
        'Cierre/noche (17:00-18:59)': list(range(17, 19)),
    }
    for nombre, horas in franjas.items():
        sub = tr[tr['hora_ny'].isin(horas)]
        if len(sub) == 0:
            print(f"  {nombre}: sin operaciones")
            continue
        wr = (sub['R'] > 0).mean() * 100
        print(f"  {nombre}: n={len(sub)} ({len(sub)/40:.1f}/día)  WR={wr:.1f}%  R_total={sub['R'].sum():+.2f}  R_prom={sub['R'].mean():+.3f}")

    tr.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/franjas_horarias/backtest_24h_muestra.csv', index=False)
    print("\nGuardado: backtest_24h_muestra.csv")
