"""
Probabilidad de rentabilidad positiva operando Miercoles con riesgo alto
(15-20%), a pedido de Diego (02/09/2026). Metodologia: BLOCK BOOTSTRAP
por dia (el estandar de significancia de este proyecto) -- se remuestrea
con reemplazo, muchas veces, el conjunto de miercoles REALES (cada uno
con su secuencia real de operaciones intradia, no operaciones sueltas
mezcladas), simulando "universos alternativos" de la misma cantidad de
miercoles que los que realmente se operaron. Para cada universo se corre
el interes compuesto con el riesgo dado y se mide si termina en
ganancia.

Ademas, se calcula tambien el escenario semanal realista completo
(escala bajada: dias comunes en 2-3%, Miercoles en 15% o 20%) sobre la
serie cronologica real completa (no bootstrap, la serie real tal cual
paso).
"""
import pandas as pd
import numpy as np
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, curva_riesgo_variable, max_drawdown, DIAS_ORDEN

np.random.seed(7)
N_ITER = 5000
CAPITAL_INICIAL = 1000.0


def armar_dias_miercoles(df):
    mie = df[df['dia_semana'] == 'Miércoles'].sort_values(['Fecha_dt', 'orden_sesion', 'hora'])
    dias = [g['Beneficio_R'].values for _, g in mie.groupby('Fecha_dt')]
    return dias


def bootstrap_probabilidad(dias_reales, riesgo, n_iter=N_ITER, capital_inicial=1.0):
    n_dias = len(dias_reales)
    finales = np.empty(n_iter)
    drawdowns = np.empty(n_iter)
    for it in range(n_iter):
        idx = np.random.randint(0, n_dias, size=n_dias)
        capital = capital_inicial
        valores = [capital]
        for i in idx:
            for r in dias_reales[i]:
                capital += capital * riesgo * r
                valores.append(capital)
        finales[it] = capital
        s = pd.Series(valores)
        pico = s.cummax()
        drawdowns[it] = ((s - pico) / pico * 100).min()
    return finales, drawdowns


if __name__ == '__main__':
    df = cargar_todo_cronologico()
    dias_mie = armar_dias_miercoles(df)
    n_ops_mie = sum(len(d) for d in dias_mie)
    print(f"Miercoles reales: {len(dias_mie)} dias, {n_ops_mie} operaciones totales")
    print(f"Win rate real (a nivel de operacion, Miercoles): "
          f"{(np.concatenate(dias_mie) > 0).mean()*100:.1f}%")

    print(f"\n-- Probabilidad de terminar en ganancia neta, tras operar TODOS los miercoles "
          f"del periodo (bootstrap, {N_ITER} universos simulados) --")
    print(f"{'Riesgo':>8}{'P(positivo)':>14}{'Mediana retorno':>18}{'P5 retorno':>13}{'P95 retorno':>13}{'Mediana DD':>13}{'P5 DD (peor)':>14}")
    for riesgo_pct in [10, 15, 20]:
        riesgo = riesgo_pct / 100
        finales, drawdowns = bootstrap_probabilidad(dias_mie, riesgo, capital_inicial=1.0)
        p_positivo = (finales > 1.0).mean() * 100
        ret = (finales - 1) * 100
        print(f"{riesgo_pct:>7}%{p_positivo:>13.1f}%{np.median(ret):>+17.1f}%{np.percentile(ret,5):>+12.1f}%"
              f"{np.percentile(ret,95):>+12.1f}%{np.median(drawdowns):>+12.1f}%{np.percentile(drawdowns,5):>+13.1f}%")

    print(f"\n-- Comparacion: mismo bootstrap con riesgo PAREJO en dias NO miercoles (linea base) --")
    otros = df[df['dia_semana'] != 'Miércoles']
    dias_otros = [g.sort_values(['orden_sesion','hora'])['Beneficio_R'].values for _, g in otros.groupby('Fecha_dt')]
    for riesgo_pct in [3]:
        riesgo = riesgo_pct / 100
        finales, drawdowns = bootstrap_probabilidad(dias_otros, riesgo, capital_inicial=1.0)
        p_positivo = (finales > 1.0).mean() * 100
        print(f"Resto de dias a {riesgo_pct}%: P(positivo) = {p_positivo:.1f}% (referencia, no es lo que se pregunto)")

    # ---- Escenario semanal completo, escala bajada, serie real (no bootstrap) ----
    print(f"\n{'='*95}\nESCENARIOS REALISTAS -- serie cronologica real completa (no bootstrap), USD {CAPITAL_INICIAL:.0f} inicial")
    print(f"{'='*95}")
    combos = [
        ('Base 2% / Miercoles 15%', {**{d: 0.02 for d in DIAS_ORDEN}, 'Miércoles': 0.15}),
        ('Base 2% / Miercoles 20%', {**{d: 0.02 for d in DIAS_ORDEN}, 'Miércoles': 0.20}),
        ('Base 3% / Miercoles 15%', {**{d: 0.03 for d in DIAS_ORDEN}, 'Miércoles': 0.15}),
        ('Base 3% / Miercoles 20%', {**{d: 0.03 for d in DIAS_ORDEN}, 'Miércoles': 0.20}),
    ]
    resumen = []
    print(f"{'Escenario':<28}{'Capital final':>15}{'Retorno':>11}{'Drawdown max':>14}")
    for nombre, riesgo_dia in combos:
        valores = curva_riesgo_variable(df, riesgo_dia, capital_inicial=CAPITAL_INICIAL)
        final = valores[-1]
        ret = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        print(f"{nombre:<28}USD {final:>10,.0f}{ret:>+10.1f}%{dd:>+13.1f}%")
        resumen.append(dict(escenario=nombre, capital_final=round(final,2), retorno_pct=round(ret,1), drawdown_max_pct=round(dd,1)))
    pd.DataFrame(resumen).to_csv(os.path.join(os.path.dirname(__file__), 'escenarios_realistas_miercoles.csv'), index=False)
