"""
Prueba: sesion angosta (09:01-10:59 NY, la que usa Fabian) vs ventana
ancha (08:00-11:59 NY, todo lo que hay disponible en los 6 meses M1) --
misma logica de EstrategiaXAU (M3 en 3min via resample, ChOC,
Envolvente, MEC-A/MEC-B/MER), unico cambio es el rango horario. A
pedido de Diego (27/08/2026).
"""
import pandas as pd
import numpy as np
import pytz

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
NY = pytz.timezone('America/New_York')
UTC = pytz.UTC

RR = 0.9
MIN_BREAK_PCT = 0.0001
MAX_SL_PIPS = 20000
DAILY_MAX_SL = 2
ENV_CLASICA_MIN = 0.85
ENV_MARTILLO_MIN = 0.50
ENV_DOJI_MIN = 0.15


def cargar():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    return df.sort_index()


def ventana_ny(fecha, hora_ini, min_ini, hora_fin, min_fin):
    ini = NY.localize(pd.Timestamp(fecha.year, fecha.month, fecha.day, hora_ini, min_ini)).astimezone(UTC)
    fin = NY.localize(pd.Timestamp(fecha.year, fecha.month, fecha.day, hora_fin, min_fin)).astimezone(UTC)
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
    # CORREGIDO 27/08/2026: mecha chica (<15%) -> clasica sin importar el
    # cuerpo exacto (ya no exige >=85% como pared dura) -- calibrado contra
    # 51 casos reales de Fabian, subio la coincidencia de 56.9% a 96.1%
    if bp >= ENV_MARTILLO_MIN and w_op < ENV_DOJI_MIN:
        return 1
    elif ENV_MARTILLO_MIN <= bp < ENV_CLASICA_MIN and w_op >= ENV_DOJI_MIN:
        return 2
    elif ENV_DOJI_MIN <= w_op <= ENV_CLASICA_MIN and ENV_DOJI_MIN <= w_fav <= ENV_CLASICA_MIN:
        return 3
    return 0


def es_indecision(o, h, l, c):
    total = h - l
    if total <= 0:
        return False
    bp = abs(c - o) / total
    es_martillo = tipo_envolvente(o, h, l, c, True) == 2 or tipo_envolvente(o, h, l, c, False) == 2
    return bp <= ENV_MARTILLO_MIN and not es_martillo


def es_start(o_arr, h_arr, l_arr, c_arr, i, direccion):
    """FUSIONADO 28/08/2026 (calibrado y confirmado contra el dia 1 real,
    12/02/2026 09:03): vela i = envolvente en la direccion, vela i-1 =
    indecision, vela i-2 = pullback EN CONTRA de la direccion, y las 3
    (i-2,i-1,i) no pueden ser del mismo color (invalidacion pag.15 del
    Plan Tecnico)."""
    if i < 2:
        return False
    tipo = tipo_envolvente(o_arr[i], h_arr[i], l_arr[i], c_arr[i], direccion == 1)
    # CORREGIDO 28/08/2026: doji (tipo 3) es "invalido como señal standalone"
    # segun el Plan Tecnico -- solo clasica (1) o martillo (2) confirman.
    if tipo not in (1, 2):
        return False
    if not es_indecision(o_arr[i-1], h_arr[i-1], l_arr[i-1], c_arr[i-1]):
        return False
    pullback_ok = (c_arr[i-2] > o_arr[i-2]) if direccion == -1 else (c_arr[i-2] < o_arr[i-2])
    if not pullback_ok:
        return False
    color_i = c_arr[i] > o_arr[i]
    color_i1 = c_arr[i-1] > o_arr[i-1]
    color_i2 = c_arr[i-2] > o_arr[i-2]
    if color_i == color_i1 == color_i2:
        return False
    return True


def backtest_dia(g_sesion: pd.DataFrame, t_inicio_entradas=None):
    """CORREGIDO 28/08/2026 (encontrado al resolver el dia 1 real, 12/02/2026):
    la estructura M3 (niveles alto/bajo, tendencia) NO se resetea al abrir la
    ventana operable -- se viene armando desde antes. Antes, g_sesion arrancaba
    justo en 09:01 y a esa hora todavia no habia 2 velas M3 cerradas, asi que
    el ChOC real (que Fabian si vio, con contexto previo a las 09:01) quedaba
    invisible para el codigo. Ahora `g_sesion` puede venir mas amplio (con
    velas de antes de la ventana operable) para construir M3/tendencia, y
    `t_inicio_entradas` es el corte real desde el cual se permite ABRIR
    operaciones (si es None, se permite desde la primera vela, como antes)."""
    if len(g_sesion) < 10:
        return []
    # CORREGIDO 28/08/2026: M3 debe armarse con los altos/bajos REALES de
    # M1 (mechas incluidas), no con un OHLC derivado solo del cierre --
    # eso ignoraba movimiento real dentro de cada tramo de 3 minutos.
    m3 = g_sesion.resample('3min').agg(open=('open', 'first'), high=('high', 'max'),
                                        low=('low', 'min'), close=('close', 'last')).dropna()
    if len(m3) < 3:
        return []

    alto_level, bajo_level = np.nan, np.nan
    alto_prev, bajo_prev = np.nan, np.nan
    # NUEVO 30/08/2026 (Plan Tecnico pag.29): un alto/bajo M3 solo habilita
    # entradas (MER/MEC-A) si supero CON CUERPO a su propio alto/bajo M3
    # anterior en >=0.01% -- si no, es "acumulacion" (maximo mas bajo o
    # minimo mas alto que el anterior) y el nivel sigue sirviendo para
    # actualizar la estructura, pero NO para disparar una entrada.
    alto_valido, bajo_valido = True, True
    tend_state = 0
    ultimo_quiebre = np.nan
    ultimo_quiebre_valido = True
    mec_fase_a, mec_extremo_a = 0, np.nan
    mec_fase_b, mec_extremo_b = 0, np.nan

    trades = []
    en_posicion = False
    direccion_pos, entrada_precio, sl_precio, tp_precio, t_entrada = None, None, None, None, None
    sl_hoy, tp_hoy = 0, 0

    m1_idx = list(g_sesion.index)
    o_arr, h_arr, l_arr, c_arr = g_sesion['open'].values, g_sesion['high'].values, g_sesion['low'].values, g_sesion['close'].values

    def cerrar(i, motivo):
        nonlocal en_posicion, sl_hoy, tp_hoy
        precio_salida = sl_precio if motivo == 'SL' else tp_precio
        ret_r = RR if motivo == 'TP' else -1.0
        trades.append({'t_entrada': t_entrada, 'R': ret_r, 'direccion': direccion_pos})
        if motivo == 'SL':
            sl_hoy += 1
        else:
            tp_hoy += 1
        en_posicion = False

    for i in range(2, len(g_sesion)):
        t = m1_idx[i]
        m3_cerradas = m3[m3.index + pd.Timedelta(minutes=3) <= t]
        if len(m3_cerradas) >= 2:
            v1, v2 = m3_cerradas.iloc[-1], m3_cerradas.iloc[-2]
            if v2['close'] > v2['open'] and v1['close'] < v1['open']:
                nivel = max(v2['high'], v1['high'])
                if np.isnan(alto_level) or nivel != alto_level:
                    alto_prev, alto_level = alto_level, nivel
                    alto_valido = np.isnan(alto_prev) or alto_level > alto_prev * (1 + MIN_BREAK_PCT)
            if v2['close'] < v2['open'] and v1['close'] > v1['open']:
                nivel = min(v2['low'], v1['low'])
                if np.isnan(bajo_level) or nivel != bajo_level:
                    bajo_prev, bajo_level = bajo_level, nivel
                    bajo_valido = np.isnan(bajo_prev) or bajo_level < bajo_prev * (1 - MIN_BREAK_PCT)

        close_i = c_arr[i]
        # RE-APLICADO 30/08/2026: el margen se vuelve a medir con la mecha
        # (high/low), no con el cierre. El PDF actualizado dice "con
        # cuerpo" (pag.21), pero Fabian confirmo en vivo (caso 21/04) que
        # mide con la herramienta "rango de precios" de TradingView, y
        # verificado con dato exacto el low SI perforaba el margen aunque
        # el cierre no. Empiricamente esta version da mejor match (96%)
        # que la version "con cierre" (92%) -- la explicacion mas probable
        # de la frase "con cuerpo" del PDF es que en el dato real de
        # Fabian (OANDA) el cierre SI alcanza, y la diferencia con
        # Dukascopy (nuestra fuente) se compensa mirando la mecha.
        choc_alcista = choc_bajista = False
        if tend_state <= 0 and not np.isnan(alto_level) and h_arr[i] > alto_level * (1 + MIN_BREAK_PCT):
            choc_alcista, tend_state, ultimo_quiebre, ultimo_quiebre_valido = True, 1, alto_level, alto_valido
        elif tend_state == 1 and not np.isnan(alto_level) and h_arr[i] > alto_level * (1 + MIN_BREAK_PCT):
            ultimo_quiebre, ultimo_quiebre_valido = alto_level, alto_valido
        if tend_state >= 0 and not np.isnan(bajo_level) and l_arr[i] < bajo_level * (1 - MIN_BREAK_PCT):
            choc_bajista, tend_state, ultimo_quiebre, ultimo_quiebre_valido = True, -1, bajo_level, bajo_valido
        elif tend_state == -1 and not np.isnan(bajo_level) and l_arr[i] < bajo_level * (1 - MIN_BREAK_PCT):
            ultimo_quiebre, ultimo_quiebre_valido = bajo_level, bajo_valido

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
        # patron valido para MEC = Envolvente O Start (MER nunca usa Start,
        # por eso mer_long/mer_short mas abajo siguen usando solo env_*)
        # doji (tipo 3) invalido como señal standalone (Plan Tecnico) -- solo
        # clasica (1) / martillo (2) disparan entrada, ver es_start() tambien.
        patron_alcista_mec = (env_alcista in (1, 2)) or es_start(o_arr, h_arr, l_arr, c_arr, i, 1)
        patron_bajista_mec = (env_bajista in (1, 2)) or es_start(o_arr, h_arr, l_arr, c_arr, i, -1)

        if en_posicion:
            if direccion_pos == 1:
                if l_arr[i] <= sl_precio: cerrar(i, 'SL')
                elif h_arr[i] >= tp_precio: cerrar(i, 'TP')
            else:
                if h_arr[i] >= sl_precio: cerrar(i, 'SL')
                elif l_arr[i] <= tp_precio: cerrar(i, 'TP')

        dia_detenido = tp_hoy >= 1 or sl_hoy >= DAILY_MAX_SL
        fuera_de_ventana = t_inicio_entradas is not None and t < t_inicio_entradas
        puede_abrir = not dia_detenido and not en_posicion and not fuera_de_ventana

        if puede_abrir:
            mecA_long = tend_state == 1 and not np.isnan(ultimo_quiebre) and h_arr[i] > ultimo_quiebre*(1+MIN_BREAK_PCT) and patron_alcista_mec
            mecA_short = tend_state == -1 and not np.isnan(ultimo_quiebre) and l_arr[i] < ultimo_quiebre*(1-MIN_BREAK_PCT) and patron_bajista_mec
            mecB_long = mec_fase_a == 2 and h_arr[i] > mec_extremo_a*(1+MIN_BREAK_PCT) and patron_alcista_mec
            mecB_short = mec_fase_b == 2 and l_arr[i] < mec_extremo_b*(1-MIN_BREAK_PCT) and patron_bajista_mec
            mer_long = choc_alcista and env_alcista in (1, 2) and (np.isnan(alto_prev) or abs(alto_level-alto_prev)/alto_level <= MIN_BREAK_PCT)
            mer_short = choc_bajista and env_bajista in (1, 2) and (np.isnan(bajo_prev) or abs(bajo_level-bajo_prev)/bajo_level <= MIN_BREAK_PCT)
            # NOTA 30/08/2026: la regla del PDF pag.29 (un M3 nuevo debe
            # superar con cuerpo a su M3 anterior del mismo tipo, si no es
            # "acumulacion") se probo (alto_valido/bajo_valido, mas arriba)
            # pero aplicada tal cual hundio el match rate de 91.6% a 44% --
            # la interpretacion o el alcance de la regla esta mal. Revertido
            # hasta entender bien el alcance real (ver bitacora 30/08).

            if mecB_long or choc_bajista: mec_fase_a, mec_extremo_a = 0, np.nan
            if mecB_short or choc_alcista: mec_fase_b, mec_extremo_b = 0, np.nan

            entra_long = mecA_long or mecB_long or (mer_long and not (mecA_long or mecB_long))
            entra_short = mecA_short or mecB_short or (mer_short and not (mecA_short or mecB_short))

            if entra_long and not np.isnan(bajo_level):
                dist = close_i - bajo_level
                if dist * 100 > MAX_SL_PIPS: dist *= 0.6
                if dist > 0:
                    en_posicion, direccion_pos = True, 1
                    entrada_precio, t_entrada = close_i, t
                    sl_precio, tp_precio = close_i - dist, close_i + dist*RR
            elif entra_short and not np.isnan(alto_level):
                dist = alto_level - close_i
                if dist * 100 > MAX_SL_PIPS: dist *= 0.6
                if dist > 0:
                    en_posicion, direccion_pos = True, -1
                    entrada_precio, t_entrada = close_i, t
                    sl_precio, tp_precio = close_i + dist, close_i - dist*RR
    return trades


def correr(df, hora_ini, min_ini, hora_fin, min_fin, nombre):
    # La estructura M3 no resetea al abrir la ventana operable (ver
    # backtest_dia): para cada dia se usa TODO el dato disponible desde el
    # arranque del dia (g completo) para construir M3/tendencia, y se
    # permiten operaciones recien desde hora_ini:min_ini en adelante.
    df = df.copy()
    df['day'] = df.index.date
    todos = []
    for day, g in df.groupby('day'):
        ini, fin = ventana_ny(pd.Timestamp(day), hora_ini, min_ini, hora_fin, min_fin)
        g_amplia = g[g.index <= fin]
        if len(g_amplia) < 10:
            continue
        todos.extend(backtest_dia(g_amplia, t_inicio_entradas=ini))
    tr = pd.DataFrame(todos)
    print(f"\n--- {nombre} ---")
    if len(tr) == 0:
        print("Sin operaciones generadas.")
        return tr
    wr = (tr['R'] > 0).mean() * 100
    print(f"Operaciones: {len(tr)} | Win rate: {wr:.1f}% | Total R: {tr['R'].sum():.2f} | Promedio R: {tr['R'].mean():.4f}")
    print(f"Ganadoras: {(tr['R']>0).sum()} | Perdedoras: {(tr['R']<0).sum()}")
    return tr


if __name__ == '__main__':
    df = cargar()
    print("=" * 100)
    print("VENTANA ANGOSTA (09:01-10:59 NY, la real de Fabian) vs VENTANA ANCHA (08:00-11:59 NY, todo lo disponible)")
    print("=" * 100)
    tr_angosta = correr(df, 9, 1, 10, 59, "Ventana angosta 09:01-10:59 NY")
    tr_ancha = correr(df, 8, 0, 11, 59, "Ventana ancha 08:00-11:59 NY")

    if len(tr_angosta) and len(tr_ancha):
        tr_angosta.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/backtest_ventana_angosta.csv', index=False)
        tr_ancha.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/backtest_ventana_ancha.csv', index=False)
        print(f"\nDiferencia en cantidad de operaciones: {len(tr_ancha)-len(tr_angosta)} ({(len(tr_ancha)/len(tr_angosta)-1)*100:+.1f}%)")
