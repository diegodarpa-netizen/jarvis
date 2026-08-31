"""
Verificacion dia 1 y dia 2 con el motor UNIFICADO (M3 real OHLC + START
fusionado en MEC). Compara contra lo real de Fabian:
- Dia 1 (12/02/2026): Fabian SELL 09:03 (START), salida 09:16, +1.0R
- Dia 2 (17/02/2026): Fabian SELL 09:33 (MER), TP +1.0R
A pedido de Diego (28/08/2026): "resolvamos el dia 1".
"""
import pandas as pd
import pytz
from prueba_ventana_horaria import cargar, ventana_ny, backtest_dia

NY = pytz.timezone('America/New_York')

if __name__ == '__main__':
    df = cargar()
    df['day'] = df.index.date

    for fecha_str, real in [('2026-02-12', 'SELL 09:03 (START) -> salida 09:16, +1.0R'),
                             ('2026-02-17', 'SELL 09:33 (MER), TP +1.0R')]:
        dia = pd.Timestamp(fecha_str).date()
        g = df[df['day'] == dia]
        ini, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
        # M3 se arma con TODO el dato disponible antes del cierre de la
        # ventana (no resetea a las 09:01) -- las entradas solo se permiten
        # desde t_inicio_entradas=ini en adelante.
        g_amplia = g[g.index <= fin]
        trades = backtest_dia(g_amplia, t_inicio_entradas=ini)

        print("=" * 90)
        print(f"DIA {fecha_str} -- Fabian real: {real}")
        if not trades:
            print("  Codigo: SIN OPERACIONES")
            continue
        for t in trades:
            t_ny = t['t_entrada'].tz_convert(NY)
            dir_txt = 'BUY' if t['direccion'] == 1 else 'SELL'
            print(f"  Codigo: {dir_txt} {t_ny.strftime('%H:%M')} -> R={t['R']:+.2f}")
