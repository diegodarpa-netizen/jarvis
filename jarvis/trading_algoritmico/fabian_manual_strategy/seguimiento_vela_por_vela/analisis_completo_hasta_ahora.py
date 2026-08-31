"""
Analisis de cero (a pedido de Diego, 28/08/2026): correr el codigo TAL COMO
ESTA CALIBRADO HOY (M3 continuo sin reset, doji excluido como señal
standalone, patron START fusionado a MEC) contra TODAS las entradas reales
de Fabian que caen dentro del rango de dato M1 disponible (desde 12/02/2026),
y reportar, sin sacar conclusiones prematuras, cuantas coinciden exacto,
cuantas coinciden con desfase de pocos minutos, y cuantas no se reconocen
en absoluto. Solo lectura -- no se toca el codigo en este script.
"""
import pandas as pd
import numpy as np
import pytz
import sys
sys.path.append('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy')
from validar_entrada_fabian import señales_del_dia
from prueba_ventana_horaria import cargar, ventana_ny

NY = pytz.timezone('America/New_York')


def cargar_fabian():
    fab = pd.read_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv')
    fab['Fecha_dt'] = pd.to_datetime(fab['Fecha_dt'])
    fab = fab[fab['Fecha_dt'] >= pd.Timestamp('2026-02-12')].sort_values('Fecha_dt')
    return fab


if __name__ == '__main__':
    df = cargar()
    df['day'] = df.index.date
    fab = cargar_fabian()

    resultados = []
    cache_señales = {}

    for _, row in fab.iterrows():
        fecha = row['Fecha_dt'].date()
        hora_txt = str(row['Hora apertura (NY)']).strip()
        if not hora_txt or hora_txt.lower() == 'nan' or ':' not in hora_txt:
            continue
        h, m = map(int, hora_txt.split(':')[:2])
        direccion = 'BUY' if str(row['Buy / Sell']).strip().lower().startswith('b') else 'SELL'

        if fecha not in cache_señales:
            g = df[df['day'] == fecha]
            if len(g) < 30:
                cache_señales[fecha] = None  # sin dato ese dia
            else:
                _, fin = ventana_ny(pd.Timestamp(fecha), 9, 1, 10, 59)
                g_amplia = g[g.index <= fin]
                if len(g_amplia) < 30:
                    cache_señales[fecha] = None
                else:
                    s = señales_del_dia(g_amplia)
                    s['t_ny'] = s['t'].apply(lambda x: x.tz_convert(NY))
                    cache_señales[fecha] = s

        señales = cache_señales[fecha]
        if señales is None:
            resultados.append({'fecha': fecha, 'hora': hora_txt, 'direccion': direccion, 'estado': 'SIN_DATO'})
            continue

        exacto = señales[(señales['t_ny'].dt.hour == h) & (señales['t_ny'].dt.minute == m) & (señales['direccion'] == direccion)]
        if len(exacto):
            resultados.append({'fecha': fecha, 'hora': hora_txt, 'direccion': direccion, 'estado': 'EXACTO', 'modelo': exacto.iloc[0]['modelo']})
            continue

        # buscar la señal del mismo lado (direccion) mas cercana en el tiempo, +/- 15 min
        minutos_obj = h * 60 + m
        mismas_dir = señales[señales['direccion'] == direccion].copy()
        if len(mismas_dir):
            mismas_dir['delta'] = mismas_dir['t_ny'].apply(lambda x: x.hour * 60 + x.minute - minutos_obj)
            cercana = mismas_dir.iloc[mismas_dir['delta'].abs().argsort()[:1]]
            delta = int(cercana.iloc[0]['delta'])
            if abs(delta) <= 15:
                resultados.append({'fecha': fecha, 'hora': hora_txt, 'direccion': direccion, 'estado': 'DESFASE',
                                    'delta_min': delta, 'modelo': cercana.iloc[0]['modelo']})
                continue
        resultados.append({'fecha': fecha, 'hora': hora_txt, 'direccion': direccion, 'estado': 'NO_RECONOCIDA'})

    res = pd.DataFrame(resultados)
    res.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/seguimiento_vela_por_vela/analisis_completo_resultado.csv', index=False)

    print("=" * 90)
    print(f"TOTAL operaciones reales de Fabian evaluadas (desde 12/02/2026): {len(res)}")
    for estado in ['EXACTO', 'DESFASE', 'NO_RECONOCIDA', 'SIN_DATO']:
        sub = res[res['estado'] == estado]
        print(f"  {estado}: {len(sub)} ({len(sub)/len(res)*100:.1f}%)")

    print("\n--- Detalle DESFASE (coincide el lado, pero no el minuto exacto) ---")
    for _, r in res[res['estado'] == 'DESFASE'].iterrows():
        print(f"  {r['fecha']} {r['hora']} {r['direccion']} -- código {int(r['delta_min']):+d} min (modelo {r['modelo']})")

    print("\n--- Detalle NO_RECONOCIDA (el código no encuentra nada de ese lado en +/-15 min) ---")
    for _, r in res[res['estado'] == 'NO_RECONOCIDA'].iterrows():
        print(f"  {r['fecha']} {r['hora']} {r['direccion']}")

    print("\n--- Detalle SIN_DATO (menos de 30 velas M1 disponibles ese día en la ventana) ---")
    for _, r in res[res['estado'] == 'SIN_DATO'].iterrows():
        print(f"  {r['fecha']} {r['hora']} {r['direccion']}")
