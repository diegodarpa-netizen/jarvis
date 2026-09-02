"""
BACKTEST AUTONOMO COMPLETO (01/09/2026), a pedido de Diego: "quiero que
armemos un backtesting propio, lo mas completo que podamos... para
evaluar la estrategia para otro tipo de activos".

A diferencia de señales_del_dia() / validar() (que solo miden si el
codigo RECONOCE el patron de una entrada real de Fabian, sin abrir
posiciones -- metodo elegido para la calibracion porque una señal extra
que nunca cierra tapaba la validacion), este motor SI abre y cierra
posiciones solas, con la misma logica de EstrategiaXAU.pine:
  - SL/TP calculados con f_calcSL (distancia al nivel M3, tope de
    MAX_SL_PIPS)
  - RR = 0.9 (TP = 0.9x la distancia del SL)
  - Hedge: señal contraria con posicion abierta cierra y abre la nueva
    (el cierre por Hedge NO cuenta para el corte diario -- fix del
    01/09/2026)
  - Corte diario: 1 TP o 2 SL (reales, no Hedge) frena el dia
  - Ventana: 09:01-10:59 NY (la misma que se uso en TODA la calibracion
    historica contra las 191 operaciones reales -- OJO: el .pine en vivo
    ahora usa 09:02-11:00, confirmado con Fabian el 01/09, 1 minuto
    distinto a lo ya validado)

Simplificacion declarada: si en la misma vela el precio toca SL y TP a
la vez (raro, pero posible en velas grandes), se asume que se toco el SL
primero (supuesto conservador, no tenemos datos de tick).
"""
import pandas as pd
import numpy as np
import pytz
import sys
sys.path.insert(0, '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy')
from prueba_ventana_horaria import cargar, ventana_ny, tipo_envolvente, es_start, MIN_BREAK_PCT, RR, MAX_SL_PIPS

NY = pytz.timezone('America/New_York')
FABIAN_CSV = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
ALLOW_HEDGE = True


def f_calc_sl(dist):
    dist_pips = dist * 100
    return dist * 0.6 if dist_pips > MAX_SL_PIPS else dist


def backtest_dia_autonomo(g_amplia, ventana_ini_ny, ventana_fin_ny):
    """Simula un dia completo: estructura M3 continua (desde el arranque
    del dia disponible), entradas/cierres reales solo dentro de la
    ventana operable [ventana_ini_ny, ventana_fin_ny] (hora NY)."""
    m3 = g_amplia.resample('3min').agg(open=('open', 'first'), high=('high', 'max'),
                                        low=('low', 'min'), close=('close', 'last')).dropna()
    o_arr, h_arr, l_arr, c_arr = g_amplia['open'].values, g_amplia['high'].values, g_amplia['low'].values, g_amplia['close'].values
    m1_idx = list(g_amplia.index)

    alto_level, bajo_level = np.nan, np.nan
    tend_state = 0
    ultimo_quiebre = np.nan
    mec_fase_a, mec_extremo_a = 0, np.nan
    mec_fase_b, mec_extremo_b = 0, np.nan

    en_posicion = None  # None / 'long' / 'short'
    entry_price = entry_time = sl_price = tp_price = modelo_actual = None

    sl_hoy, tp_hoy, dia_detenido = 0, 0, False
    trades = []

    for i in range(2, len(g_amplia)):
        t = m1_idx[i]
        t_ny = t.tz_convert(NY)
        o_i, h_i, l_i, c_i = o_arr[i], h_arr[i], l_arr[i], c_arr[i]
        en_ventana = ventana_ini_ny <= t_ny.time() <= ventana_fin_ny

        # 1) chequear cierre de posicion abierta (SL/TP), ANTES de evaluar
        # nuevas señales en esta misma vela
        if en_posicion == 'long':
            if l_i <= sl_price:
                trades.append(dict(t_entry=entry_time, t_exit=t, dir='BUY', modelo=modelo_actual,
                                    entry=entry_price, exit=sl_price, motivo='SL', r=-1.0))
                sl_hoy += 1
                if sl_hoy >= 2 or tp_hoy >= 1:
                    dia_detenido = True
                en_posicion = None
            elif h_i >= tp_price:
                trades.append(dict(t_entry=entry_time, t_exit=t, dir='BUY', modelo=modelo_actual,
                                    entry=entry_price, exit=tp_price, motivo='TP', r=RR))
                tp_hoy += 1
                if sl_hoy >= 2 or tp_hoy >= 1:
                    dia_detenido = True
                en_posicion = None
        elif en_posicion == 'short':
            if h_i >= sl_price:
                trades.append(dict(t_entry=entry_time, t_exit=t, dir='SELL', modelo=modelo_actual,
                                    entry=entry_price, exit=sl_price, motivo='SL', r=-1.0))
                sl_hoy += 1
                if sl_hoy >= 2 or tp_hoy >= 1:
                    dia_detenido = True
                en_posicion = None
            elif l_i <= tp_price:
                trades.append(dict(t_entry=entry_time, t_exit=t, dir='SELL', modelo=modelo_actual,
                                    entry=entry_price, exit=tp_price, motivo='TP', r=RR))
                tp_hoy += 1
                if sl_hoy >= 2 or tp_hoy >= 1:
                    dia_detenido = True
                en_posicion = None

        # 2) estructura M3 (continua, sin resetear, igual que señales_del_dia)
        m3c = m3[m3.index + pd.Timedelta(minutes=3) <= t]
        if len(m3c) >= 2:
            v1, v2 = m3c.iloc[-1], m3c.iloc[-2]
            if v2['close'] > v2['open'] and v1['close'] < v1['open']:
                nivel = max(v2['high'], v1['high'])
                if np.isnan(alto_level) or nivel != alto_level:
                    alto_level = nivel
            if v2['close'] < v2['open'] and v1['close'] > v1['open']:
                nivel = min(v2['low'], v1['low'])
                if np.isnan(bajo_level) or nivel != bajo_level:
                    bajo_level = nivel

        choc_alcista = choc_bajista = False
        if tend_state <= 0 and not np.isnan(alto_level) and h_i > alto_level * (1 + MIN_BREAK_PCT):
            choc_alcista, tend_state, ultimo_quiebre = True, 1, alto_level
        elif tend_state == 1 and not np.isnan(alto_level) and h_i > alto_level * (1 + MIN_BREAK_PCT):
            ultimo_quiebre = alto_level
        if tend_state >= 0 and not np.isnan(bajo_level) and l_i < bajo_level * (1 - MIN_BREAK_PCT):
            choc_bajista, tend_state, ultimo_quiebre = True, -1, bajo_level
        elif tend_state == -1 and not np.isnan(bajo_level) and l_i < bajo_level * (1 - MIN_BREAK_PCT):
            ultimo_quiebre = bajo_level

        if choc_alcista:
            mec_fase_a, mec_extremo_a = 1, h_i
        elif mec_fase_a == 1:
            if c_i < o_i:
                mec_fase_a = 2
            else:
                mec_extremo_a = max(mec_extremo_a, h_i)
        if choc_bajista:
            mec_fase_b, mec_extremo_b = 1, l_i
        elif mec_fase_b == 1:
            if c_i > o_i:
                mec_fase_b = 2
            else:
                mec_extremo_b = min(mec_extremo_b, l_i)

        env_alcista = tipo_envolvente(o_i, h_i, l_i, c_i, True)
        env_bajista = tipo_envolvente(o_i, h_i, l_i, c_i, False)
        patron_alcista = (env_alcista in (1, 2)) or es_start(o_arr, h_arr, l_arr, c_arr, i, 1)
        patron_bajista = (env_bajista in (1, 2)) or es_start(o_arr, h_arr, l_arr, c_arr, i, -1)

        mecA_long = tend_state == 1 and not np.isnan(ultimo_quiebre) and h_i > ultimo_quiebre * (1 + MIN_BREAK_PCT) and patron_alcista
        mecA_short = tend_state == -1 and not np.isnan(ultimo_quiebre) and l_i < ultimo_quiebre * (1 - MIN_BREAK_PCT) and patron_bajista
        mecB_long = mec_fase_a == 2 and not np.isnan(mec_extremo_a) and h_i > mec_extremo_a * (1 + MIN_BREAK_PCT) and patron_alcista
        mecB_short = mec_fase_b == 2 and not np.isnan(mec_extremo_b) and l_i < mec_extremo_b * (1 - MIN_BREAK_PCT) and patron_bajista
        mer_long = choc_alcista and env_alcista in (1, 2)
        mer_short = choc_bajista and env_bajista in (1, 2)

        if mecB_long or choc_bajista:
            mec_fase_a, mec_extremo_a = 0, np.nan
        if mecB_short or choc_alcista:
            mec_fase_b, mec_extremo_b = 0, np.nan

        long_ok = mecA_long or mecB_long or mer_long
        short_ok = mecA_short or mecB_short or mer_short

        # 3) ejecucion -- solo dentro de la ventana operable.
        # FIX 01/09/2026 (a pedido de Diego, tras encontrar 1.481 cierres
        # por Hedge de los cuales 81% eran re-disparos en la MISMA
        # direccion, sin ningun freno): una señal nueva solo puede abrir
        # posicion si no hay nada abierto, o si hay una posicion abierta
        # en la direccion OPUESTA (flip real). Una señal repetida en la
        # misma direccion mientras ya se esta en esa posicion se ignora.
        can_trade = en_ventana and not dia_detenido
        puede_abrir_long  = can_trade and (en_posicion is None or (ALLOW_HEDGE and en_posicion == 'short'))
        puede_abrir_short = can_trade and (en_posicion is None or (ALLOW_HEDGE and en_posicion == 'long'))

        if puede_abrir_long and long_ok:
            if en_posicion is not None:
                trades.append(dict(t_entry=entry_time, t_exit=t, dir=en_posicion.upper(), modelo=modelo_actual,
                                    entry=entry_price, exit=c_i, motivo='Hedge',
                                    r=(c_i - entry_price) / (entry_price - sl_price) if en_posicion == 'long' else (entry_price - c_i) / (sl_price - entry_price)))
            dist = f_calc_sl(c_i - bajo_level)
            en_posicion = 'long'
            entry_price, entry_time = c_i, t
            sl_price = c_i - dist
            tp_price = c_i + dist * RR
            modelo_actual = 'MEC-A' if mecA_long else ('MEC-B' if mecB_long else 'MER')
        elif puede_abrir_short and short_ok:
            if en_posicion is not None:
                trades.append(dict(t_entry=entry_time, t_exit=t, dir=en_posicion.upper(), modelo=modelo_actual,
                                    entry=entry_price, exit=c_i, motivo='Hedge',
                                    r=(c_i - entry_price) / (entry_price - sl_price) if en_posicion == 'long' else (entry_price - c_i) / (sl_price - entry_price)))
            dist = f_calc_sl(alto_level - c_i)
            en_posicion = 'short'
            entry_price, entry_time = c_i, t
            sl_price = c_i + dist
            tp_price = c_i - dist * RR
            modelo_actual = 'MEC-A' if mecA_short else ('MEC-B' if mecB_short else 'MER')

    # cierre forzado a fin de sesion si quedo posicion abierta (simplificacion)
    if en_posicion is not None:
        c_last = c_arr[-1]
        r = (c_last - entry_price) / (entry_price - sl_price) if en_posicion == 'long' else (entry_price - c_last) / (sl_price - entry_price)
        trades.append(dict(t_entry=entry_time, t_exit=m1_idx[-1], dir=en_posicion.upper(), modelo=modelo_actual,
                            entry=entry_price, exit=c_last, motivo='EOD', r=r))

    return trades


def main():
    fab = pd.read_csv(FABIAN_CSV)
    fab['Fecha_dt'] = pd.to_datetime(fab['Fecha_dt']).dt.date
    precios = cargar()
    precios = precios.copy()
    precios['day'] = precios.index.date

    VENTANA_INI = pd.Timestamp('09:01').time()
    VENTANA_FIN = pd.Timestamp('10:59').time()

    dias_unicos = sorted(fab['Fecha_dt'].unique())
    todos_trades = []

    for dia in dias_unicos:
        g = precios[precios['day'] == dia]
        if len(g) == 0:
            continue
        _, fin = ventana_ny(pd.Timestamp(dia), 10, 59, 10, 59)
        g_amplia = g[g.index <= fin]
        if len(g_amplia) < 5:
            continue
        trades = backtest_dia_autonomo(g_amplia, VENTANA_INI, VENTANA_FIN)
        for tr in trades:
            tr['fecha'] = dia
        todos_trades.extend(trades)

    tdf = pd.DataFrame(todos_trades)
    tdf.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/backtest_autonomo_completo_resultado.csv', index=False)

    reales = tdf[tdf['motivo'].isin(['SL', 'TP'])]
    hedge = tdf[tdf['motivo'] == 'Hedge']
    eod = tdf[tdf['motivo'] == 'EOD']

    print("=" * 90)
    print(f"BACKTEST AUTONOMO COMPLETO -- {len(dias_unicos)} dias (mismas fechas que las 191 de Fabian)")
    print("=" * 90)
    print(f"Total operaciones simuladas: {len(tdf)}")
    print(f"  -- Cierres reales (SL/TP): {len(reales)}")
    print(f"  -- Cierres por Hedge:      {len(hedge)}")
    print(f"  -- Cierres forzados EOD:   {len(eod)}")
    print()
    if len(reales):
        wins = (reales['motivo'] == 'TP').sum()
        losses = (reales['motivo'] == 'SL').sum()
        wr = wins / len(reales) * 100
        r_total_reales = reales['r'].sum()
        print(f"SOLO cierres reales (SL/TP): {len(reales)} operaciones")
        print(f"  Win Rate: {wr:.1f}%  ({wins}W / {losses}L)")
        print(f"  R total:  {r_total_reales:+.1f}R")
        print(f"  R promedio por operacion: {reales['r'].mean():+.3f}R")
    print()
    r_total_con_hedge = tdf['r'].sum()
    print(f"TODO incluido (SL+TP+Hedge+EOD), R total: {r_total_con_hedge:+.1f}R  ({len(tdf)} operaciones)")
    print()
    print(f"-- Comparacion contra Fabian real --")
    print(f"Fabian real:      191 operaciones, +72.8R, 65.4% Win Rate")
    print(f"Codigo autonomo:  {len(reales)} operaciones reales (+ {len(hedge)} hedge, {len(eod)} EOD)")


if __name__ == '__main__':
    main()
