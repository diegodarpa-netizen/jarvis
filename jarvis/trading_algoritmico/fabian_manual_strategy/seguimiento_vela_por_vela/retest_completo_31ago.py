"""
RE-TEST completo (31/08/2026), a pedido explicito de Diego: "no quiero que
me digas que ya esta hecho... quiero que hagamos un test y quiero ver el
porcentaje de acierto otra vez". Corre la validacion operacion por
operacion (misma logica de validar_entrada_fabian.señales_del_dia, sin
autonomia/circuit-breaker) sobre las 191 operaciones reales de Fabian,
cargando el CSV de precios UNA sola vez (no 191 veces como validar()) para
que sea rapido, y muestra el resultado real, no una cifra recordada.
"""
import pandas as pd
import numpy as np
import pytz
import sys
sys.path.insert(0, '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy')
from prueba_ventana_horaria import cargar, ventana_ny
from seguimiento_vela_por_vela.validar_entrada_fabian import señales_del_dia

NY = pytz.timezone('America/New_York')

FABIAN_CSV = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'

# Lista DEFINITIVA de los 9 casos NO_EXACTO del cierre 30/08/2026
# (182/191, 0 sin explicar) -- confirmada cruzando README.md +
# INFORME_CALIBRACION_30AGO2026.md, no la version parcial de un intento
# anterior de este mismo script.
CASOS_PREVIOS_NO_EXACTO = {
    ('2025-10-28', '09:04'),   # broker: la vela cambia de color entero entre feeds
    ('2025-11-26', '09:35'),   # broker: cuerpo de la envolvente difiere (0,4% vs valida en OANDA)
    ('2025-11-26', '10:10'),   # familia "patron antes de la ruptura", igual al 22/04
    ('2026-04-07', '10:01'),   # broker: envolvente martillo, cuerpo 44-48% vs 50-85% esperado
    ('2026-04-22', '09:28'),   # broker: Fabian dice que rompe el alto M3, nuestro dato no
    ('2026-04-30', '09:34'),   # broker: mismo tipo que 07/04
    ('2026-05-22', '10:03'),   # Regla N5 de noticias (CONFIRMADO), no automatizada todavia
    ('2026-08-05', '10:03'),   # broker
    ('2026-08-25', '10:19'),   # broker: caso limite del margen, faltan USD 0,13
}


def main():
    fab = pd.read_csv(FABIAN_CSV)
    fab['Fecha_dt'] = pd.to_datetime(fab['Fecha_dt']).dt.date
    precios = cargar()
    precios = precios.copy()
    precios['day'] = precios.index.date

    resultados = []
    dias_unicos = sorted(fab['Fecha_dt'].unique())
    cache_señales = {}

    for dia in dias_unicos:
        g = precios[precios['day'] == dia]
        if len(g) == 0:
            trades_dia = fab[fab['Fecha_dt'] == dia]
            for _, row in trades_dia.iterrows():
                resultados.append({'fecha': dia, 'hora': row['Hora apertura (NY)'],
                                    'dir': row['Buy / Sell'], 'estado': 'SIN_DATO'})
            continue
        _, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
        g_amplia = g[g.index <= fin]
        señales = señales_del_dia(g_amplia)
        if len(señales):
            señales['t_ny'] = señales['t'].apply(lambda x: x.tz_convert(NY))
        cache_señales[dia] = señales

        trades_dia = fab[fab['Fecha_dt'] == dia]
        for _, row in trades_dia.iterrows():
            hora = row['Hora apertura (NY)']
            direccion_raw = row['Buy / Sell']
            direccion = 'BUY' if str(direccion_raw).strip().lower() == 'buy' else 'SELL'
            if pd.isna(hora) or not isinstance(hora, str) or ':' not in hora:
                resultados.append({'fecha': dia, 'hora': hora, 'dir': direccion, 'estado': 'SIN_DATO'})
                continue
            h, m = map(int, hora.split(':'))
            if len(señales):
                match = señales[(señales['t_ny'].dt.hour == h) & (señales['t_ny'].dt.minute == m) & (señales['direccion'] == direccion)]
            else:
                match = pd.DataFrame()
            estado = 'EXACTO' if len(match) else 'NO_EXACTO'
            modelo = match.iloc[0]['modelo'] if len(match) else None
            resultados.append({'fecha': dia, 'hora': hora, 'dir': direccion, 'estado': estado, 'modelo': modelo})

    res = pd.DataFrame(resultados)
    total = len(res)
    exactas = (res['estado'] == 'EXACTO').sum()
    no_exactas = (res['estado'] == 'NO_EXACTO').sum()
    sin_dato = (res['estado'] == 'SIN_DATO').sum()

    print("=" * 90)
    print(f"RE-TEST COMPLETO -- {total} operaciones reales de Fabian (27/10/2025-27/08/2026)")
    print("=" * 90)
    print(f"EXACTAS:    {exactas}/{total}  ({exactas/total*100:.1f}%)")
    print(f"NO_EXACTO:  {no_exactas}/{total}  ({no_exactas/total*100:.1f}%)")
    print(f"SIN_DATO:   {sin_dato}/{total}")
    print()

    if no_exactas:
        print("-- Detalle de las que NO coincidieron en este re-test --")
        for _, r in res[res['estado'] == 'NO_EXACTO'].iterrows():
            clave = (str(r['fecha']), str(r['hora']).strip())
            marca = " [ya conocido, cierre 30/08]" if clave in CASOS_PREVIOS_NO_EXACTO else " [** NUEVO, no estaba en la lista del 30/08 **]"
            print(f"  {r['fecha']} {r['hora']} {r['dir']}{marca}")

    if sin_dato:
        print("-- SIN_DATO (revisar por que) --")
        for _, r in res[res['estado'] == 'SIN_DATO'].iterrows():
            print(f"  {r['fecha']} {r['hora']} {r['dir']}")

    res.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/seguimiento_vela_por_vela/retest_completo_31ago_resultado.csv', index=False)
    print()
    print("Guardado: retest_completo_31ago_resultado.csv")


if __name__ == '__main__':
    main()
