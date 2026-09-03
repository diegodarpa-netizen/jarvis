"""
Frontera riesgo/retorno (02/09/2026), a pedido de Diego: comparar
"parejo" (mismo riesgo todos los dias) vs. "ponderado por dia"
(Miercoles/Martes/Jueves mas alto), con dispersión (scatter) de
retorno vs drawdown, para encontrar el mejor punto de la curva antes de
converger al rango profesional agresivo (medio/cuarto-Kelly, ~2.5%-5%
segun la literatura ya citada).

Cada punto = una configuracion de riesgo (uniforme o ponderada), corrida
sobre la serie cronologica real completa (482 operaciones) + bootstrap
(3000 universos) para la probabilidad de superar distintos umbrales de
drawdown.
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

np.random.seed(23)
CARPETA = os.path.dirname(__file__)
CAPITAL_INICIAL = 1000.0

NIVELES_PAREJOS = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 10]
COMBOS_PONDERADOS = [(1, 1, 1), (2, 1, 1), (3, 2, 1), (4, 3, 1), (5, 4, 2), (6, 5, 3), (7, 6, 4)]


def evaluar(riesgo_por_dia, etiqueta, tipo):
    valores = curva_riesgo_variable(cargar_todo_cronologico(), riesgo_por_dia, capital_inicial=CAPITAL_INICIAL) \
        if False else None  # placeholder, se recalcula abajo con df cacheado
    return None


if __name__ == '__main__':
    df = cargar_todo_cronologico()
    filas = []

    print("=" * 100)
    print("PAREJO -- mismo riesgo todos los dias")
    print("=" * 100)
    print(f"{'Riesgo':>7}{'Retorno':>13}{'Drawdown':>11}{'Peor racha':>12}{'Peor dia':>10}{'P(DD<-20%)':>12}{'P(DD<-30%)':>12}")
    for pct in NIVELES_PAREJOS:
        riesgo_dia = {d: pct / 100 for d in DIAS_ORDEN}
        valores = curva_riesgo_variable(df, riesgo_dia, capital_inicial=CAPITAL_INICIAL)
        final = valores[-1]
        ret = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        racha = peor_racha_perdedora_real(df, riesgo_dia)
        pdu, pdf = peor_dia_unico(df, riesgo_dia)
        finales_b, dd_b = bootstrap_por_dias_reales(df, riesgo_dia, n_iter=3000)
        p_dd20 = (dd_b < -20).mean() * 100
        p_dd30 = (dd_b < -30).mean() * 100
        print(f"{pct:>6}%{ret:>+12.1f}%{dd:>+10.1f}%{racha:>+11.1f}%{pdu:>+9.1f}%{p_dd20:>11.1f}%{p_dd30:>11.1f}%")
        filas.append(dict(tipo='Parejo', etiqueta=f"{pct}% parejo", riesgo_prom=pct, capital_final=round(final, 2),
                           retorno_pct=round(ret, 1), drawdown_pct=round(dd, 1), peor_racha_pct=round(racha, 1),
                           peor_dia_pct=round(pdu, 1), p_dd_peor_20=round(p_dd20, 1), p_dd_peor_30=round(p_dd30, 1)))

    print(f"\n{'=' * 100}\nPONDERADO -- Miercoles/Martes/Jueves mas alto, resto 1%\n{'=' * 100}")
    print(f"{'Combo':>16}{'Retorno':>13}{'Drawdown':>11}{'Peor racha':>12}{'Peor dia':>10}{'P(DD<-20%)':>12}{'P(DD<-30%)':>12}")
    for mie, mar, jue in COMBOS_PONDERADOS:
        riesgo_dia = {'Lunes': 0.01, 'Martes': mar/100, 'Miércoles': mie/100, 'Jueves': jue/100,
                      'Viernes': 0.01, 'Sábado': 0.0, 'Domingo': 0.01}
        valores = curva_riesgo_variable(df, riesgo_dia, capital_inicial=CAPITAL_INICIAL)
        final = valores[-1]
        ret = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        racha = peor_racha_perdedora_real(df, riesgo_dia)
        pdu, pdf = peor_dia_unico(df, riesgo_dia)
        finales_b, dd_b = bootstrap_por_dias_reales(df, riesgo_dia, n_iter=3000)
        p_dd20 = (dd_b < -20).mean() * 100
        p_dd30 = (dd_b < -30).mean() * 100
        # riesgo promedio ponderado por cantidad real de operaciones de cada dia
        n_por_dia = df.groupby('dia_semana').size()
        riesgo_prom = sum(riesgo_dia.get(d, 0) * n_por_dia.get(d, 0) for d in DIAS_ORDEN) / n_por_dia.sum() * 100
        etiqueta = f"Mié{mie}/Mar{mar}/Jue{jue}"
        print(f"{etiqueta:>16}{ret:>+12.1f}%{dd:>+10.1f}%{racha:>+11.1f}%{pdu:>+9.1f}%{p_dd20:>11.1f}%{p_dd30:>11.1f}%")
        filas.append(dict(tipo='Ponderado', etiqueta=etiqueta, riesgo_prom=round(riesgo_prom, 2), capital_final=round(final, 2),
                           retorno_pct=round(ret, 1), drawdown_pct=round(dd, 1), peor_racha_pct=round(racha, 1),
                           peor_dia_pct=round(pdu, 1), p_dd_peor_20=round(p_dd20, 1), p_dd_peor_30=round(p_dd30, 1)))

    tabla = pd.DataFrame(filas)
    tabla.to_csv(os.path.join(CARPETA, 'frontera_riesgo_retorno_tabla.csv'), index=False)

    # ---- Scatter: drawdown vs retorno (log), parejo vs ponderado ----
    fig, ax = plt.subplots(figsize=(11, 7), facecolor='#131722')
    ax.set_facecolor('#131722')
    GRID = '#2a2e39'
    WHITE = '#d1d4dc'

    parejo = tabla[tabla['tipo'] == 'Parejo']
    pond = tabla[tabla['tipo'] == 'Ponderado']

    ax.scatter(parejo['drawdown_pct'].abs(), parejo['retorno_pct'], color='#448aff', s=70, label='Parejo (mismo % todos los días)', zorder=3)
    for _, r in parejo.iterrows():
        ax.annotate(r['etiqueta'], (abs(r['drawdown_pct']), r['retorno_pct']), fontsize=7, color=WHITE,
                    xytext=(4, 4), textcoords='offset points')

    ax.scatter(pond['drawdown_pct'].abs(), pond['retorno_pct'], color='#ff9800', s=70, marker='^', label='Ponderado (Mié/Mar/Jue más alto)', zorder=3)
    for _, r in pond.iterrows():
        ax.annotate(r['etiqueta'], (abs(r['drawdown_pct']), r['retorno_pct']), fontsize=7, color=WHITE,
                    xytext=(4, -10), textcoords='offset points')

    # zona profesional agresiva (drawdown que suele acompañar 2.5%-5% medio-Kelly)
    ax.axvspan(15, 25, color='#26a69a', alpha=0.08, zorder=1)
    ax.text(20, ax.get_ylim()[1] if False else 1, '', color=WHITE)  # placeholder, se ajusta con yscale log abajo

    ax.set_yscale('log')
    ax.set_xlabel('Drawdown máximo (%, valor absoluto)', color=WHITE)
    ax.set_ylabel('Retorno total (%, escala log)', color=WHITE)
    ax.set_title('Frontera riesgo/retorno -- Parejo vs. Ponderado por día\n(zona sombreada = drawdown típico del rango profesional agresivo, medio/cuarto-Kelly)', color=WHITE, fontsize=11)
    ax.grid(color=GRID, linewidth=0.5, alpha=0.5)
    ax.tick_params(colors=WHITE)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    legend = ax.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, loc='upper left')

    plt.tight_layout()
    out_png = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/frontera_riesgo_retorno.png'
    plt.savefig(out_png, dpi=150, facecolor='#131722')
    print(f"\nGuardado grafico: {out_png}")
    print(f"Guardado tabla: frontera_riesgo_retorno_tabla.csv")
