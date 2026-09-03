"""
Frontera v2 (02/09/2026), a pedido de Diego: agrega a la comparacion
parejo/ponderado ya hecha (frontera_riesgo_retorno.py) 2 combos nuevos
(base 3% constante, Miercoles a 4% y a 5%) + la gestion hibrida
(Pre-NY+Asia, dias limitados + tope semanal +3R + corte diario 1TP/2SL,
160 operaciones) como una TERCERA familia, evaluada a los mismos niveles
de riesgo (3% y 5%) para que sea comparable de igual a igual.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, curva_riesgo_variable, max_drawdown, peor_racha_perdedora_real, DIAS_ORDEN
from grilla_riesgo_por_dia import peor_dia_unico
from combinacion_final_7_6_4 import bootstrap_por_dias_reales

np.random.seed(31)
CARPETA = os.path.dirname(__file__)
CAPITAL_INICIAL = 1000.0


def curva_uniforme(r_serie, riesgo, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    valores = [capital]
    for r in r_serie:
        capital += capital * riesgo * r
        valores.append(capital)
    return valores


def bootstrap_hibrida(df_hib, riesgo, n_iter=3000):
    dias = [g.sort_values('Hora apertura (NY)')['Beneficio_R'].values for _, g in df_hib.groupby('Fecha_dt')]
    n_dias = len(dias)
    finales = np.empty(n_iter)
    drawdowns = np.empty(n_iter)
    for it in range(n_iter):
        idx = np.random.randint(0, n_dias, size=n_dias)
        capital = 1.0
        valores = [capital]
        for i in idx:
            for r in dias[i]:
                capital += capital * riesgo * r
                valores.append(capital)
        finales[it] = capital
        s = pd.Series(valores)
        pico = s.cummax()
        drawdowns[it] = ((s - pico) / pico * 100).min()
    return finales, drawdowns


if __name__ == '__main__':
    df = cargar_todo_cronologico()
    filas = []

    # -- Ponderado nuevo: base 3% constante, Miercoles a 4% y 5% --
    print("=" * 100)
    print("PONDERADO v2 -- base 3% TODOS los dias, Miercoles mas alto")
    print("=" * 100)
    print(f"{'Combo':>20}{'Retorno':>13}{'Drawdown':>11}{'Peor racha':>12}{'Peor dia':>10}{'P(DD<-20%)':>12}{'P(DD<-30%)':>12}")
    for mie in [3, 4, 5]:
        riesgo_dia = {d: 0.03 for d in DIAS_ORDEN}
        riesgo_dia['Miércoles'] = mie / 100
        valores = curva_riesgo_variable(df, riesgo_dia, capital_inicial=CAPITAL_INICIAL)
        final = valores[-1]
        ret = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        racha = peor_racha_perdedora_real(df, riesgo_dia)
        pdu, pdf = peor_dia_unico(df, riesgo_dia)
        finales_b, dd_b = bootstrap_por_dias_reales(df, riesgo_dia, n_iter=3000)
        p_dd20 = (dd_b < -20).mean() * 100
        p_dd30 = (dd_b < -30).mean() * 100
        etiqueta = f"Base3/Mié{mie}"
        print(f"{etiqueta:>20}{ret:>+12.1f}%{dd:>+10.1f}%{racha:>+11.1f}%{pdu:>+9.1f}%{p_dd20:>11.1f}%{p_dd30:>11.1f}%")
        filas.append(dict(tipo='Base3+Mié', etiqueta=etiqueta, capital_final=round(final, 2), retorno_pct=round(ret, 1),
                           drawdown_pct=round(dd, 1), peor_racha_pct=round(racha, 1), peor_dia_pct=round(pdu, 1),
                           p_dd_peor_20=round(p_dd20, 1), p_dd_peor_30=round(p_dd30, 1)))

    # -- Gestion hibrida, a 3% y 5% --
    print(f"\n{'=' * 100}\nGESTION HIBRIDA (Pre-NY+Asia, dias limitados + tope +3R + corte 1TP/2SL) -- 160 operaciones\n{'=' * 100}")
    df_hib = pd.read_csv(os.path.join(CARPETA, 'gestion_hibrida_resultado.csv'))
    df_hib['Fecha_dt'] = pd.to_datetime(df_hib['Fecha_dt'])
    r_hib = df_hib.sort_values(['Fecha_dt', 'Hora apertura (NY)'])['Beneficio_R'].values
    print(f"{'Riesgo':>8}{'Retorno':>13}{'Drawdown':>11}{'P(DD<-20%)':>12}{'P(DD<-30%)':>12}")
    for pct in [3, 5]:
        riesgo = pct / 100
        valores = curva_uniforme(r_hib, riesgo)
        final = valores[-1]
        ret = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        finales_b, dd_b = bootstrap_hibrida(df_hib, riesgo, n_iter=3000)
        p_dd20 = (dd_b < -20).mean() * 100
        p_dd30 = (dd_b < -30).mean() * 100
        etiqueta = f"Híbrida {pct}%"
        print(f"{pct:>7}%{ret:>+12.1f}%{dd:>+10.1f}%{p_dd20:>11.1f}%{p_dd30:>11.1f}%")
        filas.append(dict(tipo='Híbrida', etiqueta=etiqueta, capital_final=round(final, 2), retorno_pct=round(ret, 1),
                           drawdown_pct=round(dd, 1), peor_racha_pct=None, peor_dia_pct=None,
                           p_dd_peor_20=round(p_dd20, 1), p_dd_peor_30=round(p_dd30, 1)))

    # -- traer los puntos de referencia ya conocidos (3% y 5% parejo) --
    for pct in [3, 5]:
        riesgo_dia = {d: pct / 100 for d in DIAS_ORDEN}
        valores = curva_riesgo_variable(df, riesgo_dia, capital_inicial=CAPITAL_INICIAL)
        final = valores[-1]
        ret = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        finales_b, dd_b = bootstrap_por_dias_reales(df, riesgo_dia, n_iter=3000)
        p_dd20 = (dd_b < -20).mean() * 100
        p_dd30 = (dd_b < -30).mean() * 100
        filas.append(dict(tipo='Parejo', etiqueta=f"{pct}% parejo", capital_final=round(final, 2), retorno_pct=round(ret, 1),
                           drawdown_pct=round(dd, 1), peor_racha_pct=None, peor_dia_pct=None,
                           p_dd_peor_20=round(p_dd20, 1), p_dd_peor_30=round(p_dd30, 1)))

    tabla = pd.DataFrame(filas)
    tabla.to_csv(os.path.join(CARPETA, 'frontera_v2_tabla.csv'), index=False)

    # -- scatter con las 3 familias --
    fig, ax = plt.subplots(figsize=(11, 7), facecolor='#131722')
    ax.set_facecolor('#131722')
    GRID, WHITE = '#2a2e39', '#d1d4dc'
    colores = {'Parejo': '#448aff', 'Base3+Mié': '#ff9800', 'Híbrida': '#26a69a'}
    marcadores = {'Parejo': 'o', 'Base3+Mié': '^', 'Híbrida': 's'}
    for tipo, g in tabla.groupby('tipo'):
        ax.scatter(g['drawdown_pct'].abs(), g['retorno_pct'], color=colores[tipo], marker=marcadores[tipo],
                   s=80, label=tipo, zorder=3)
        for _, r in g.iterrows():
            ax.annotate(r['etiqueta'], (abs(r['drawdown_pct']), r['retorno_pct']), fontsize=7, color=WHITE,
                        xytext=(4, 4), textcoords='offset points')
    ax.set_yscale('log')
    ax.set_xlabel('Drawdown máximo (%, valor absoluto)', color=WHITE)
    ax.set_ylabel('Retorno total (%, escala log)', color=WHITE)
    ax.set_title('Frontera riesgo/retorno v2 -- Parejo vs Base3+Miércoles vs Gestión Híbrida', color=WHITE, fontsize=11)
    ax.grid(color=GRID, linewidth=0.5, alpha=0.5)
    ax.tick_params(colors=WHITE)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, loc='upper left')
    plt.tight_layout()
    out_png = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/frontera_v2_hibrida.png'
    plt.savefig(out_png, dpi=150, facecolor='#131722')
    print(f"\nGuardado: {out_png}")
