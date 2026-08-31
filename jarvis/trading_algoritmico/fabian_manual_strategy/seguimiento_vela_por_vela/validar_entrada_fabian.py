"""
Metodo de validacion CORREGIDO (28/08/2026, a pedido de Diego): no correr el
motor de forma autonoma y comparar la lista de operaciones que produce --
eso deja que señales "extra" (que Fabian no toma) bloqueen/tapen la señal
real si nunca cierran. En cambio: se recorre el dia entero armando M3/estado
de forma continua (sin reset), y en CADA vela se evalua si mecA/mecB/mer
reconoce una entrada -- sin autonomia de posicion ni circuit-breaker --
y se chequea puntualmente si la entrada REAL de Fabian aparece reconocida
en su horario exacto. Las señales que el codigo encuentra pero Fabian no
tomo se listan aparte, como "candidatos extra" para expandir mas adelante
(no se tratan como bug a corregir ahora).
"""
import pandas as pd
import numpy as np
import pytz
from prueba_ventana_horaria import cargar, ventana_ny, tipo_envolvente, es_start, MIN_BREAK_PCT

NY = pytz.timezone('America/New_York')


def señales_del_dia(g_amplia: pd.DataFrame):
    """Devuelve un DataFrame con, para cada vela desde la 3ra, que modelo
    (mecA/mecB/mer, long/short) reconoce el codigo -- sin abrir posiciones."""
    m3 = g_amplia.resample('3min').agg(open=('open', 'first'), high=('high', 'max'),
                                        low=('low', 'min'), close=('close', 'last')).dropna()
    o_arr, h_arr, l_arr, c_arr = g_amplia['open'].values, g_amplia['high'].values, g_amplia['low'].values, g_amplia['close'].values
    m1_idx = list(g_amplia.index)

    alto_level, bajo_level = np.nan, np.nan
    alto_prev, bajo_prev = np.nan, np.nan
    # NUEVO 30/08/2026 (Plan Tecnico pag.29): un alto/bajo M3 solo habilita
    # entradas (MER/MEC-A) si supero CON CUERPO a su propio alto/bajo M3
    # anterior en >=0.01% -- si no, es "acumulacion" y el nivel sirve para
    # actualizar estructura pero NO para disparar una entrada.
    alto_valido, bajo_valido = True, True
    tend_state = 0
    ultimo_quiebre = np.nan
    ultimo_quiebre_valido = True
    mec_fase_a, mec_extremo_a = 0, np.nan
    mec_fase_b, mec_extremo_b = 0, np.nan

    filas = []
    for i in range(2, len(g_amplia)):
        t = m1_idx[i]
        m3c = m3[m3.index + pd.Timedelta(minutes=3) <= t]
        if len(m3c) >= 2:
            v1, v2 = m3c.iloc[-1], m3c.iloc[-2]
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
        # RE-APLICADO 30/08/2026: margen medido con la mecha (high/low) --
        # empiricamente da mejor match que "con cierre" (96% vs 92%), y
        # Fabian confirmo en vivo (21/04) que mide con "rango de precios".
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
        patron_alcista = (env_alcista in (1, 2)) or es_start(o_arr, h_arr, l_arr, c_arr, i, 1)
        patron_bajista = (env_bajista in (1, 2)) or es_start(o_arr, h_arr, l_arr, c_arr, i, -1)

        mecA_long = tend_state == 1 and not np.isnan(ultimo_quiebre) and h_arr[i] > ultimo_quiebre * (1 + MIN_BREAK_PCT) and patron_alcista
        mecA_short = tend_state == -1 and not np.isnan(ultimo_quiebre) and l_arr[i] < ultimo_quiebre * (1 - MIN_BREAK_PCT) and patron_bajista
        mecB_long = mec_fase_a == 2 and not np.isnan(mec_extremo_a) and h_arr[i] > mec_extremo_a * (1 + MIN_BREAK_PCT) and patron_alcista
        mecB_short = mec_fase_b == 2 and not np.isnan(mec_extremo_b) and l_arr[i] < mec_extremo_b * (1 - MIN_BREAK_PCT) and patron_bajista
        mer_long = choc_alcista and env_alcista in (1, 2)
        mer_short = choc_bajista and env_bajista in (1, 2)
        # NOTA 30/08/2026: 3er intento de la regla "unico nivel opuesto"
        # (pag.27-29), esta vez con las imagenes del PDF vistas (no solo
        # texto) -- igual hundio a 12/191 (6%). El problema real: bajo_prev
        # /alto_prev en el codigo guarda CUALQUIER valor anterior, por
        # viejo/irrelevante que sea -- casi nunca esta a <=0.01% del
        # actual, mientras que las imagenes del PDF muestran 2 niveles
        # formados en sucesion INMEDIATA (mismo tramo de estructura), un
        # caso puntual y raro, no "el anterior historico cualquiera".
        # Necesita tracking de estado mas fino (ej: solo comparar si el
        # nivel anterior se formo hace pocas velas M3) antes de poder
        # implementarse sin romper todo. Revertido, pendiente.

        if mecB_long or choc_bajista:
            mec_fase_a, mec_extremo_a = 0, np.nan
        if mecB_short or choc_alcista:
            mec_fase_b, mec_extremo_b = 0, np.nan

        long_ok = mecA_long or mecB_long or mer_long
        short_ok = mecA_short or mecB_short or mer_short
        if long_ok or short_ok:
            modelo = 'MEC-A' if (mecA_long or mecA_short) else ('MEC-B' if (mecB_long or mecB_short) else 'MER')
            filas.append({'t': t, 'direccion': 'BUY' if long_ok else 'SELL', 'modelo': modelo})

    return pd.DataFrame(filas)


def validar(fecha_str, entradas_fabian):
    """entradas_fabian: lista de (hora 'HH:MM', direccion 'BUY'/'SELL')"""
    df = cargar()
    df['day'] = df.index.date
    dia = pd.Timestamp(fecha_str).date()
    g = df[df['day'] == dia]
    _, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
    g_amplia = g[g.index <= fin]
    señales = señales_del_dia(g_amplia)
    señales['t_ny'] = señales['t'].apply(lambda x: x.tz_convert(NY))

    print("=" * 90)
    print(f"DIA {fecha_str}")
    print("-- Entradas REALES de Fabian: ¿el codigo las reconoce? --")
    for hora, direccion in entradas_fabian:
        h, m = map(int, hora.split(':'))
        match = señales[(señales['t_ny'].dt.hour == h) & (señales['t_ny'].dt.minute == m) & (señales['direccion'] == direccion)]
        if len(match):
            print(f"  {hora} {direccion}: ✓ RECONOCIDA -- modelo {match.iloc[0]['modelo']}")
        else:
            print(f"  {hora} {direccion}: ✗ NO reconocida por el codigo")

    print("-- Señales EXTRA que el codigo encuentra en 09:01-10:59 y Fabian NO tomo (catalogar, no bloquea) --")
    fabian_horas = {h for h, _ in entradas_fabian}
    ventana_ini, _ = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
    extra = señales[señales['t_ny'] >= ventana_ini.tz_convert(NY)]
    for _, row in extra.iterrows():
        hhmm = row['t_ny'].strftime('%H:%M')
        if hhmm not in fabian_horas:
            print(f"  {hhmm} {row['direccion']} ({row['modelo']}) -- extra, no tomada por Fabian")


if __name__ == '__main__':
    validar('2026-02-12', [('09:03', 'SELL')])
    validar('2026-02-17', [('09:33', 'SELL')])
