"""
Escalera de descenso de a 1 punto porcentual (02/09/2026), a pedido de
Diego: bajar Miercoles/Martes/Jueves de a 1% desde la combinacion
recomendada (7/6/4) hasta el piso (1/1/1 = parejo), para comparar mas
adelante en un informe (no armar el informe todavia, solo generar y
guardar los escenarios). Serie cronologica real completa, USD 1.000
inicial, interes compuesto + bootstrap de probabilidad en cada escalon.
"""
import pandas as pd
import numpy as np
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, curva_riesgo_variable, max_drawdown, peor_racha_perdedora_real, DIAS_ORDEN
from grilla_riesgo_por_dia import peor_dia_unico
from combinacion_final_7_6_4 import bootstrap_por_dias_reales

np.random.seed(11)
CAPITAL_INICIAL = 1000.0

ESCALONES = [
    (7, 6, 4), (6, 5, 3), (5, 4, 2), (4, 3, 1), (3, 2, 1), (2, 1, 1), (1, 1, 1),
]


def armar_riesgo(mie, mar, jue):
    return {'Lunes': 0.01, 'Martes': mar/100, 'Miércoles': mie/100, 'Jueves': jue/100,
            'Viernes': 0.01, 'Sábado': 0.0, 'Domingo': 0.01}


if __name__ == '__main__':
    df = cargar_todo_cronologico()
    filas = []
    print(f"{'Combinacion':<22}{'Capital final':>15}{'Retorno':>12}{'DD real':>9}{'Peor racha':>11}{'Peor dia':>10}{'P(positivo) boot':>18}{'DD mediana boot':>17}{'P(DD<-30%)':>12}")
    for mie, mar, jue in ESCALONES:
        riesgo = armar_riesgo(mie, mar, jue)
        valores = curva_riesgo_variable(df, riesgo, capital_inicial=CAPITAL_INICIAL)
        final = valores[-1]
        ret = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        racha = peor_racha_perdedora_real(df, riesgo)
        pd_unico, pd_fecha = peor_dia_unico(df, riesgo)

        finales_b, dd_b = bootstrap_por_dias_reales(df, riesgo, n_iter=3000)
        p_pos = (finales_b > 1.0).mean() * 100
        dd_med = np.median(dd_b)
        p_dd30 = (dd_b < -30).mean() * 100

        etiqueta = f"Mie{mie}/Mar{mar}/Jue{jue}"
        print(f"{etiqueta:<22}USD {final:>10,.0f}{ret:>+11.1f}%{dd:>+8.1f}%{racha:>+10.1f}%{pd_unico:>+9.1f}%{p_pos:>17.1f}%{dd_med:>+16.1f}%{p_dd30:>11.1f}%")
        filas.append(dict(combinacion=etiqueta, mie=mie, mar=mar, jue=jue,
                           capital_final=round(final, 2), retorno_pct=round(ret, 1), drawdown_real_pct=round(dd, 1),
                           peor_racha_3L_pct=round(racha, 1), peor_dia_unico_pct=round(pd_unico, 1),
                           p_positivo_bootstrap=round(p_pos, 2), dd_mediana_bootstrap=round(dd_med, 1),
                           p_dd_peor_30_bootstrap=round(p_dd30, 1)))

    out = pd.DataFrame(filas)
    out.to_csv(os.path.join(os.path.dirname(__file__), 'escalera_descenso_1pto_resumen.csv'), index=False)
    print(f"\nGuardado: escalera_descenso_1pto_resumen.csv ({len(out)} escalones)")
