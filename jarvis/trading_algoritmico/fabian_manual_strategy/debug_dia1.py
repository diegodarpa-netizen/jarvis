"""Debug vela por vela del dia 1 (12/02/2026) para ver por que a las 09:03
el patron START no dispara la entrada aunque este.py"""
import pandas as pd
import numpy as np
import pytz
from prueba_ventana_horaria import cargar, ventana_ny, tipo_envolvente, es_indecision, es_start, MIN_BREAK_PCT, MAX_SL_PIPS

NY = pytz.timezone('America/New_York')

df = cargar()
df['day'] = df.index.date
dia = pd.Timestamp('2026-02-12').date()
g = df[df['day'] == dia]
ini, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
g_sesion = g[(g.index >= ini) & (g.index <= fin)]

m3 = g_sesion.resample('3min').agg(open=('open', 'first'), high=('high', 'max'),
                                    low=('low', 'min'), close=('close', 'last')).dropna()
print("M3 candles:")
for t, row in m3.iterrows():
    print(f"  {t.tz_convert(NY).strftime('%H:%M')} O={row['open']:.2f} H={row['high']:.2f} L={row['low']:.2f} C={row['close']:.2f} {'ALCISTA' if row['close']>row['open'] else 'BAJISTA'}")

alto_level, bajo_level = np.nan, np.nan
alto_prev, bajo_prev = np.nan, np.nan
tend_state = 0
ultimo_quiebre = np.nan
mec_fase_a, mec_extremo_a = 0, np.nan
mec_fase_b, mec_extremo_b = 0, np.nan

m1_idx = list(g_sesion.index)
o_arr, h_arr, l_arr, c_arr = g_sesion['open'].values, g_sesion['high'].values, g_sesion['low'].values, g_sesion['close'].values

print("\nVela por vela (09:01-09:20):")
for i in range(2, len(g_sesion)):
    t = m1_idx[i]
    t_ny = t.tz_convert(NY)
    if t_ny.hour == 9 and t_ny.minute > 20:
        break
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
    if tend_state <= 0 and not np.isnan(alto_level) and close_i > alto_level * (1 + MIN_BREAK_PCT):
        choc_alcista, tend_state, ultimo_quiebre = True, 1, alto_level
    elif tend_state == 1 and not np.isnan(alto_level) and close_i > alto_level * (1 + MIN_BREAK_PCT):
        ultimo_quiebre = alto_level
    if tend_state >= 0 and not np.isnan(bajo_level) and close_i < bajo_level * (1 - MIN_BREAK_PCT):
        choc_bajista, tend_state, ultimo_quiebre = True, -1, bajo_level
    elif tend_state == -1 and not np.isnan(bajo_level) and close_i < bajo_level * (1 - MIN_BREAK_PCT):
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
    start_alcista = es_start(o_arr, h_arr, l_arr, c_arr, i, 1)
    start_bajista = es_start(o_arr, h_arr, l_arr, c_arr, i, -1)
    patron_alcista_mec = (env_alcista > 0) or start_alcista
    patron_bajista_mec = (env_bajista > 0) or start_bajista

    mecA_long = tend_state == 1 and not np.isnan(ultimo_quiebre) and close_i > ultimo_quiebre*(1+MIN_BREAK_PCT) and patron_alcista_mec
    mecA_short = tend_state == -1 and not np.isnan(ultimo_quiebre) and close_i < ultimo_quiebre*(1-MIN_BREAK_PCT) and patron_bajista_mec
    mecB_long = mec_fase_a == 2 and close_i > mec_extremo_a*(1+MIN_BREAK_PCT) and patron_alcista_mec
    mecB_short = mec_fase_b == 2 and close_i < mec_extremo_b*(1-MIN_BREAK_PCT) and patron_bajista_mec
    mer_long = choc_alcista and env_alcista > 0
    mer_short = choc_bajista and env_bajista > 0

    print(f"{t_ny.strftime('%H:%M')} O={o_arr[i]:.2f} H={h_arr[i]:.2f} L={l_arr[i]:.2f} C={c_arr[i]:.2f} | "
          f"alto_lvl={alto_level:.2f} bajo_lvl={bajo_level:.2f} tend={tend_state} quiebre={ultimo_quiebre:.2f} | "
          f"faseA={mec_fase_a} extA={mec_extremo_a if not np.isnan(mec_extremo_a) else float('nan'):.2f} "
          f"faseB={mec_fase_b} extB={mec_extremo_b if not np.isnan(mec_extremo_b) else float('nan'):.2f} | "
          f"env_alc={env_alcista} env_baj={env_bajista} start_alc={start_alcista} start_baj={start_bajista} | "
          f"choc_alc={choc_alcista} choc_baj={choc_bajista} | "
          f"mecA_L={mecA_long} mecA_S={mecA_short} mecB_L={mecB_long} mecB_S={mecB_short} mer_L={mer_long} mer_S={mer_short}")

    if mecB_long or choc_bajista: mec_fase_a, mec_extremo_a = 0, np.nan
    if mecB_short or choc_alcista: mec_fase_b, mec_extremo_b = 0, np.nan
