"""
Backtest de la estrategia de Fabian (misma logica que EstrategiaXAU.pine)
sobre el año calendario 2022 completo, usando datos reales M1 de Dukascopy
ya descargados. A pedido de Diego (27/08/2026).

Simplificacion declarada: se implementa MEC-A (tendencia), MEC-B
(Quiebre-Pullback-Continuacion) y MER (primera vela de contacto), todos
con patron Envolvente (3 variantes: clasica/martillo/doji). El patron
START se deja fuera de esta v1 -- en los datos reales de Fabian ya
mostro win rate cercano al azar (47.4%, 19 de 191 operaciones), asi que
omitirlo no cambia la lectura de fondo, y evita meter un state-machine
extra sin validar todavia.

Sesion: 09:01-10:59 NY (igual que el Plan Operativo). M3 se resamplea a
3min DENTRO de la sesion (no usa datos pre-sesion, siguiendo la regla ya
aprendida en jarvis/trading/rules/estructura_m3.md: la estructura debe
confirmarse dentro de la sesion, no heredar tendencia overnight).
"""
import pandas as pd
import numpy as np
import pytz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/data/XAUUSD_M1_5y.csv'
NY = pytz.timezone('America/New_York')
UTC = pytz.UTC

RR = 0.9
MIN_BREAK_PCT = 0.0001  # 0.01%
MAX_SL_PIPS = 20000
DAILY_MAX_SL = 2

ENV_CLASICA_MIN = 0.85
ENV_MARTILLO_MIN = 0.50
ENV_DOJI_MIN = 0.15


def cargar():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    return df


def sesion_ny(fecha):
    ini = NY.localize(pd.Timestamp(fecha.year, fecha.month, fecha.day, 9, 1)).astimezone(UTC)
    fin = NY.localize(pd.Timestamp(fecha.year, fecha.month, fecha.day, 10, 59)).astimezone(UTC)
    return ini, fin


def tipo_envolvente(o, h, l, c, es_compra):
    total = h - l
    if total <= 0:
        return 0
    body = abs(c - o)
    bp = body / total
    if es_compra:
        if c <= o:
            return 0
        w_op = (h - max(o, c)) / total
        w_fav = (min(o, c) - l) / total
    else:
        if c >= o:
            return 0
        w_op = (min(o, c) - l) / total
        w_fav = (h - max(o, c)) / total

    if bp >= ENV_CLASICA_MIN and w_op < ENV_DOJI_MIN:
        return 1
    elif ENV_MARTILLO_MIN <= bp < ENV_CLASICA_MIN and w_op >= ENV_DOJI_MIN:
        return 2
    elif ENV_DOJI_MIN <= w_op <= ENV_CLASICA_MIN and ENV_DOJI_MIN <= w_fav <= ENV_CLASICA_MIN:
        return 3
    return 0


def backtest_dia(g_sesion: pd.DataFrame):
    """g_sesion: velas M1 de UNA sesion (09:01-10:59 NY de un dia)."""
    if len(g_sesion) < 10:
        return []

    m3 = g_sesion['close'].resample('3min').ohlc()
    m3 = m3.dropna()
    if len(m3) < 3:
        return []

    alto_level, bajo_level = np.nan, np.nan
    alto_prev, bajo_prev = np.nan, np.nan
    tend_state = 0
    ultimo_quiebre = np.nan

    mec_fase_a, mec_extremo_a = 0, np.nan
    mec_fase_b, mec_extremo_b = 0, np.nan

    trades = []
    en_posicion = False
    direccion_pos, entrada_precio, sl_precio, tp_precio, t_entrada = None, None, None, None, None
    sl_hoy, tp_hoy = 0, 0
    modelo_actual = [None]

    m1_idx = list(g_sesion.index)
    o_arr, h_arr, l_arr, c_arr = g_sesion['open'].values, g_sesion['high'].values, g_sesion['low'].values, g_sesion['close'].values

    def cerrar(i, motivo):
        nonlocal en_posicion, sl_hoy, tp_hoy
        precio_salida = sl_precio if motivo == 'SL' else tp_precio
        ret_r = RR if motivo == 'TP' else -1.0
        trades.append({'t_entrada': t_entrada, 't_salida': m1_idx[i], 'direccion': direccion_pos,
                        'motivo': motivo, 'R': ret_r, 'precio_entrada': entrada_precio, 'precio_salida': precio_salida,
                        'modelo': modelo_actual[0]})
        if motivo == 'SL':
            sl_hoy += 1
        else:
            tp_hoy += 1
        en_posicion = False

    for i in range(2, len(g_sesion)):
        t = m1_idx[i]

        # actualizar M3: buscar las ultimas 2 velas de 3min ya cerradas antes de t
        m3_cerradas = m3[m3.index + pd.Timedelta(minutes=3) <= t]
        if len(m3_cerradas) >= 2:
            v1, v2 = m3_cerradas.iloc[-1], m3_cerradas.iloc[-2]  # v1=mas reciente, v2=anterior
            alto_cand_ok = v2['close'] > v2['open'] and v1['close'] < v1['open']
            bajo_cand_ok = v2['close'] < v2['open'] and v1['close'] > v1['open']
            if alto_cand_ok:
                nivel = max(v2['high'], v1['high'])
                if np.isnan(alto_level) or nivel != alto_level:
                    alto_prev = alto_level
                    alto_level = nivel
            if bajo_cand_ok:
                nivel = min(v2['low'], v1['low'])
                if np.isnan(bajo_level) or nivel != bajo_level:
                    bajo_prev = bajo_level
                    bajo_level = nivel

        close_i = c_arr[i]
        choc_alcista = False
        choc_bajista = False
        tend_state_prev = tend_state  # el estado ANTES de esta vela -- clave para no confundir
        # una entrada MEC-A (continuacion de tendencia YA vigente) con la vela
        # misma del ChOC (que es territorio de MER, no de MEC-A)

        if tend_state <= 0 and not np.isnan(alto_level) and close_i > alto_level * (1 + MIN_BREAK_PCT):
            choc_alcista = True
            tend_state = 1
            ultimo_quiebre = alto_level
        elif tend_state == 1 and not np.isnan(alto_level) and close_i > alto_level * (1 + MIN_BREAK_PCT):
            ultimo_quiebre = alto_level

        if tend_state >= 0 and not np.isnan(bajo_level) and close_i < bajo_level * (1 - MIN_BREAK_PCT):
            choc_bajista = True
            tend_state = -1
            ultimo_quiebre = bajo_level
        elif tend_state == -1 and not np.isnan(bajo_level) and close_i < bajo_level * (1 - MIN_BREAK_PCT):
            ultimo_quiebre = bajo_level

        # MEC-B estado
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

        # gestion de posicion abierta
        if en_posicion:
            if direccion_pos == 1:
                if l_arr[i] <= sl_precio:
                    cerrar(i, 'SL')
                elif h_arr[i] >= tp_precio:
                    cerrar(i, 'TP')
            else:
                if h_arr[i] >= sl_precio:
                    cerrar(i, 'SL')
                elif l_arr[i] <= tp_precio:
                    cerrar(i, 'TP')

        dia_detenido = tp_hoy >= 1 or sl_hoy >= DAILY_MAX_SL
        puede_abrir = not dia_detenido and (not en_posicion)  # sin hedge en esta v1 (simplificacion)

        if puede_abrir:
            # MEC-A exige que la tendencia YA estuviera vigente ANTES de esta
            # vela -- si tend_state recien paso a 1/-1 en esta misma vela, eso
            # es el ChOC (territorio MER), no continuacion de tendencia
            mecA_long = tend_state_prev == 1 and not np.isnan(ultimo_quiebre) and close_i > ultimo_quiebre * (1 + MIN_BREAK_PCT) and env_alcista > 0
            mecA_short = tend_state_prev == -1 and not np.isnan(ultimo_quiebre) and close_i < ultimo_quiebre * (1 - MIN_BREAK_PCT) and env_bajista > 0
            mecB_long = mec_fase_a == 2 and close_i > mec_extremo_a * (1 + MIN_BREAK_PCT) and env_alcista > 0
            mecB_short = mec_fase_b == 2 and close_i < mec_extremo_b * (1 - MIN_BREAK_PCT) and env_bajista > 0
            mer_long = choc_alcista and env_alcista > 0 and (np.isnan(alto_prev) or abs(alto_level - alto_prev) / alto_level <= MIN_BREAK_PCT)
            mer_short = choc_bajista and env_bajista > 0 and (np.isnan(bajo_prev) or abs(bajo_level - bajo_prev) / bajo_level <= MIN_BREAK_PCT)

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
                    sl_precio = close_i - dist
                    tp_precio = close_i + dist * RR
                    modelo_actual[0] = 'MEC-A' if mecA_long else ('MEC-B' if mecB_long else 'MER')
            elif entra_short and not np.isnan(alto_level):
                dist = alto_level - close_i
                if dist * 100 > MAX_SL_PIPS:
                    dist *= 0.6
                if dist > 0:
                    en_posicion, direccion_pos = True, -1
                    entrada_precio, t_entrada = close_i, t
                    sl_precio = close_i + dist
                    tp_precio = close_i - dist * RR
                    modelo_actual[0] = 'MEC-A' if mecA_short else ('MEC-B' if mecB_short else 'MER')

    return trades


if __name__ == '__main__':
    df = cargar()
    df['day'] = df.index.date

    todos_trades = []
    dias_procesados = 0
    for day, g in df.groupby('day'):
        if day < pd.Timestamp('2022-01-01').date() or day > pd.Timestamp('2022-12-31').date():
            continue
        ini, fin = sesion_ny(pd.Timestamp(day))
        g_sesion = g[(g.index >= ini) & (g.index <= fin)]
        if len(g_sesion) < 10:
            continue
        trades = backtest_dia(g_sesion)
        todos_trades.extend(trades)
        dias_procesados += 1

    tr = pd.DataFrame(todos_trades)
    print(f"Dias con sesion procesados en 2022: {dias_procesados}")
    print(f"Operaciones generadas por el backtest: {len(tr)}")
    if len(tr) > 0:
        wr = (tr['R'] > 0).mean() * 100
        print(f"Win rate: {wr:.1f}% | Total R: {tr['R'].sum():.2f} | Promedio R: {tr['R'].mean():.3f}")
        print(f"Ganadoras: {(tr['R']>0).sum()} | Perdedoras: {(tr['R']<0).sum()}")
        tr.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/backtest_2022_resultados.csv', index=False)
        print("Guardado en backtest_2022_resultados.csv")
    else:
        print("No se generaron operaciones -- revisar logica antes de seguir.")
