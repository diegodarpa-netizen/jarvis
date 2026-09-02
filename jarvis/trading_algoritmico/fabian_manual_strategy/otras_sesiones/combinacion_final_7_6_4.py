"""
Combinacion final recomendada (02/09/2026): Miercoles 7% / Martes 6% /
Jueves 4% / resto (Lunes, Viernes, Sabado, Domingo) 1%. Serie
cronologica real completa (482 operaciones), USD 1.000 inicial, interes
compuesto -- mas bootstrap de probabilidad (5000 universos, remuestreo
por dia completo, preservando el dia de semana real de cada dia
remuestreado) para saber la probabilidad de terminar en ganancia con
esta combinacion especifica.
"""
import pandas as pd
import numpy as np
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, curva_riesgo_variable, max_drawdown, peor_racha_perdedora_real, DIAS_ORDEN
from grilla_riesgo_por_dia import peor_dia_unico

np.random.seed(11)
CAPITAL_INICIAL = 1000.0
N_ITER = 5000

RIESGO_COMBO = {
    'Lunes': 0.01, 'Martes': 0.06, 'Miércoles': 0.07, 'Jueves': 0.04,
    'Viernes': 0.01, 'Sábado': 0.0, 'Domingo': 0.01,
}


def bootstrap_por_dias_reales(df, riesgo_por_dia, n_iter=N_ITER):
    dias = [(fecha, g['dia_semana'].iloc[0], g.sort_values(['orden_sesion', 'hora'])['Beneficio_R'].values)
            for fecha, g in df.groupby('Fecha_dt')]
    n_dias = len(dias)
    finales = np.empty(n_iter)
    drawdowns = np.empty(n_iter)
    for it in range(n_iter):
        idx = np.random.randint(0, n_dias, size=n_dias)
        capital = 1.0
        valores = [capital]
        for i in idx:
            _, dia_semana, r_vals = dias[i]
            riesgo = riesgo_por_dia.get(dia_semana, 0.0)
            for r in r_vals:
                capital += capital * riesgo * r
                valores.append(capital)
        finales[it] = capital
        s = pd.Series(valores)
        pico = s.cummax()
        drawdowns[it] = ((s - pico) / pico * 100).min()
    return finales, drawdowns


if __name__ == '__main__':
    df = cargar_todo_cronologico()

    print("Combinacion: " + ", ".join(f"{d}={v*100:.0f}%" for d, v in RIESGO_COMBO.items() if v > 0) + ", resto 0%")
    print()

    # -- serie real (no bootstrap) --
    valores = curva_riesgo_variable(df, RIESGO_COMBO, capital_inicial=CAPITAL_INICIAL)
    final = valores[-1]
    ret = (final / CAPITAL_INICIAL - 1) * 100
    dd = max_drawdown(valores)
    racha = peor_racha_perdedora_real(df, RIESGO_COMBO)
    peor_dia, peor_fecha = peor_dia_unico(df, RIESGO_COMBO)

    print("=" * 80)
    print("SERIE REAL COMPLETA (lo que realmente paso, no un promedio)")
    print("=" * 80)
    print(f"Capital final (desde USD {CAPITAL_INICIAL:.0f}): USD {final:,.0f}")
    print(f"Retorno: {ret:+.1f}%")
    print(f"Drawdown maximo: {dd:+.1f}%")
    print(f"Peor racha real de 3 perdidas seguidas: {racha:+.1f}%")
    print(f"Peor dia unico: {peor_dia:+.1f}%  ({peor_fecha.date() if peor_fecha is not None else '-'})")

    # -- bootstrap --
    finales, drawdowns = bootstrap_por_dias_reales(df, RIESGO_COMBO)
    ret_boot = (finales - 1) * 100
    p_positivo = (finales > 1.0).mean() * 100
    print()
    print("=" * 80)
    print(f"BOOTSTRAP -- {N_ITER} universos alternativos (remuestreo de dias reales completos)")
    print("=" * 80)
    print(f"P(termina en ganancia neta): {p_positivo:.2f}%")
    print(f"Retorno -- mediana: {np.median(ret_boot):+.1f}%   P5 (mal escenario): {np.percentile(ret_boot,5):+.1f}%   P95 (buen escenario): {np.percentile(ret_boot,95):+.1f}%")
    print(f"Drawdown -- mediana: {np.median(drawdowns):+.1f}%   P5 (peor 5%): {np.percentile(drawdowns,5):+.1f}%   P95 (mejor 5%): {np.percentile(drawdowns,95):+.1f}%")
    print(f"Probabilidad de drawdown peor que -40%: {(drawdowns < -40).mean()*100:.1f}%")
    print(f"Probabilidad de drawdown peor que -30%: {(drawdowns < -30).mean()*100:.1f}%")

    pd.DataFrame([dict(
        combinacion="Mie7/Mar6/Jue4/resto1",
        capital_final=round(final, 2), retorno_pct=round(ret, 1), drawdown_max_pct=round(dd, 1),
        peor_racha_3L_pct=round(racha, 1), peor_dia_unico_pct=round(peor_dia, 1),
        p_positivo_bootstrap=round(p_positivo, 2),
        dd_mediana_bootstrap=round(np.median(drawdowns), 1),
        dd_p5_bootstrap=round(np.percentile(drawdowns, 5), 1),
        prob_dd_peor_30=round((drawdowns < -30).mean()*100, 1),
        prob_dd_peor_40=round((drawdowns < -40).mean()*100, 1),
    )]).to_csv(os.path.join(os.path.dirname(__file__), 'combinacion_final_7_6_4_resumen.csv'), index=False)
