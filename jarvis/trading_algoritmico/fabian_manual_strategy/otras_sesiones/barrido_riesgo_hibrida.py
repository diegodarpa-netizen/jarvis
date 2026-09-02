"""
Barrido de riesgo (3%, 5%, 10%, 15%, 20%), interes compuesto, $10.000
iniciales, sobre la "gestion hibrida" Pre-NY + Asia (dias operativos
limitados + tope semanal +3R + corte diario 1TP/2SL) -- misma formula de
`barrido_riesgo_1_a_5.py` (capital += capital * riesgo_pct * r).
"""
import pandas as pd
import os

CARPETA = os.path.dirname(__file__)
CAPITAL_INICIAL = 10000.0
NIVELES = [3, 5, 10, 15, 20]


def curva_compuesta(r_serie, riesgo_pct, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    valores = [capital]
    for r in r_serie:
        capital += capital * riesgo_pct * r
        valores.append(capital)
    return valores


def max_drawdown(valores):
    s = pd.Series(valores)
    pico = s.cummax()
    dd = (s - pico) / pico * 100
    return dd.min()


def peor_racha_perdedora(r_serie, n=3):
    """Busca la peor racha real de n perdidas SEGUIDAS en la serie (no
    supone -1R fijo, usa el R real de cada perdida de la racha)."""
    peor_suma = 0.0
    racha_actual = []
    for r in r_serie:
        if r < 0:
            racha_actual.append(r)
        else:
            racha_actual = []
        if len(racha_actual) >= n:
            suma = sum(racha_actual[-n:])
            peor_suma = min(peor_suma, suma)
    return peor_suma


if __name__ == '__main__':
    df = pd.read_csv(os.path.join(CARPETA, 'gestion_hibrida_resultado.csv'))
    df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
    df = df.sort_values(['Fecha_dt', 'Hora apertura (NY)'])
    r_serie = df['Beneficio_R'].values
    ini_fecha = df['Fecha_dt'].min().strftime('%d/%m/%Y')
    fin_fecha = df['Fecha_dt'].max().strftime('%d/%m/%Y')
    peor_racha_r = peor_racha_perdedora(r_serie, 3)

    print(f"Base: {len(r_serie)} operaciones ({ini_fecha} -> {fin_fecha}), gestion hibrida Pre-NY+Asia")
    print(f"Peor racha real de 3 perdidas seguidas: {peor_racha_r:+.2f}R")
    print()
    print(f"{'Riesgo':>7} | {'Capital final':>15} | {'Retorno':>10} | {'Drawdown max':>13} | {'Impacto peor racha 3L':>22}")
    print("-" * 80)
    resumen = []
    for pct in NIVELES:
        riesgo = pct / 100
        valores = curva_compuesta(r_serie, riesgo)
        final = valores[-1]
        ret_pct = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        impacto_racha = ((1 + riesgo * peor_racha_r / 3) ** 3 - 1) * 100 if False else None
        # impacto real: aplicar la racha real (suma de R) de una sola vez
        impacto_racha_pct = riesgo * peor_racha_r * 100
        print(f"{pct:>6}% | USD {final:>11,.0f} | {ret_pct:>+8.1f}% | {dd:>+11.1f}% | {impacto_racha_pct:>+20.1f}%")
        resumen.append(dict(riesgo_pct=pct, capital_final=round(final, 2), retorno_pct=round(ret_pct, 1),
                             drawdown_max_pct=round(dd, 1), impacto_peor_racha_pct=round(impacto_racha_pct, 1)))

    pd.DataFrame(resumen).to_csv(os.path.join(CARPETA, 'barrido_riesgo_hibrida_resumen.csv'), index=False)
