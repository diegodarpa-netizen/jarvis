"""
Grilla de riesgo de a 1% (02/09/2026), a pedido de Diego: bajar Miercoles
de a 1 punto porcentual hasta encontrar el mejor balance, y despues
probar si conviene subir Martes/Jueves tambien de a 1%. Serie
cronologica real completa (482 operaciones, NY+Pre-NY+Asia), USD 1.000
inicial, interes compuesto.

Precauciones que se miden en cada combinacion (no solo capital final):
- Drawdown maximo real (la caida de pico a valle mas dura del camino).
- Peor racha real de 3 perdidas seguidas (golpe puntual).
- PEOR DIA UNICO (una sola vela/operacion mala en el dia de riesgo alto
  puede pegar fuerte de una sola vez -- se mide aparte, es distinto al
  drawdown acumulado).
"""
import pandas as pd
import numpy as np
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, curva_riesgo_variable, max_drawdown, DIAS_ORDEN, peor_racha_perdedora_real

CARPETA = os.path.dirname(__file__)
CAPITAL_INICIAL = 1000.0


def peor_dia_unico(df, riesgo_por_dia):
    """Peor golpe de UN SOLO dia (suma de R de ese dia * riesgo de ese
    dia), en % de capital -- para detectar el riesgo de "un solo dia
    malo" en la franja de riesgo alto."""
    peor = 0.0
    peor_fecha = None
    for fecha, g in df.groupby('Fecha_dt'):
        dia = g['dia_semana'].iloc[0]
        riesgo = riesgo_por_dia.get(dia, 0.0)
        golpe = 1.0
        for r in g['Beneficio_R'].values:
            golpe *= (1 + riesgo * r)
        golpe_pct = (golpe - 1) * 100
        if golpe_pct < peor:
            peor = golpe_pct
            peor_fecha = fecha
    return peor, peor_fecha


def correr_grilla(df, base, variable_dia, valores, otros_fijos=None):
    filas = []
    for v in valores:
        riesgo_dia = {d: base for d in DIAS_ORDEN}
        if otros_fijos:
            riesgo_dia.update(otros_fijos)
        riesgo_dia[variable_dia] = v / 100
        valores_capital = curva_riesgo_variable(df, riesgo_dia, capital_inicial=CAPITAL_INICIAL)
        final = valores_capital[-1]
        ret = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores_capital)
        racha = peor_racha_perdedora_real(df, riesgo_dia)
        peor_dia, peor_fecha = peor_dia_unico(df, riesgo_dia)
        filas.append(dict(variable=f"{variable_dia}={v}%", capital_final=round(final, 2), retorno_pct=round(ret, 1),
                           drawdown_max_pct=round(dd, 1), peor_racha_3L_pct=round(racha, 1),
                           peor_dia_unico_pct=round(peor_dia, 1), fecha_peor_dia=str(peor_fecha.date()) if peor_fecha is not None else None))
    return pd.DataFrame(filas)


if __name__ == '__main__':
    df = cargar_todo_cronologico()
    BASE = 0.01  # 1% en los demas dias, segun lo que pidio Diego

    print(f"{'='*100}\nTRAMO 1 -- Miercoles de 15% a 5%, de a 1 punto (base {BASE*100:.0f}% el resto de dias)\n{'='*100}")
    g1 = correr_grilla(df, BASE, 'Miércoles', list(range(15, 4, -1)))
    print(g1.to_string(index=False))
    g1.to_csv(os.path.join(CARPETA, 'grilla_miercoles.csv'), index=False)

    print(f"\n{'='*100}\nTRAMO 2 -- Martes de 1% a 8% (Miercoles fijo en el mejor balance del tramo 1, base 1% el resto)\n{'='*100}")
    # eleccion del mejor balance del tramo 1: la penultima antes de que el
    # drawdown supere el -35% (umbral de "todavia tolerable"), se define
    # abajo tras ver g1 -- por ahora se deja como parametro explicito
    MEJOR_MIE = 7  # drawdown <30% y peor dia unico <15%, el punto donde
    # ambas precauciones todavia se sostienen (ver tramo 1)
    g2 = correr_grilla(df, BASE, 'Martes', list(range(1, 9)), otros_fijos={'Miércoles': MEJOR_MIE / 100})
    print(g2.to_string(index=False))
    g2.to_csv(os.path.join(CARPETA, 'grilla_martes.csv'), index=False)

    print(f"\n{'='*100}\nTRAMO 3 -- Jueves de 1% a 8% (Miercoles fijo, base 1% el resto)\n{'='*100}")
    g3 = correr_grilla(df, BASE, 'Jueves', list(range(1, 9)), otros_fijos={'Miércoles': MEJOR_MIE / 100})
    print(g3.to_string(index=False))
    g3.to_csv(os.path.join(CARPETA, 'grilla_jueves.csv'), index=False)
