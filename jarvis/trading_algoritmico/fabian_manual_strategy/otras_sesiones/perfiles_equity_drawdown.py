"""
Curvas de equity + drawdown ("underwater plot") en el tiempo, para los 3
perfiles de inversor (02/09/2026): Conservador (Gestion Hibrida 3%),
Moderado (3% parejo), Agresivo (5% parejo). Con fechas reales en el eje
X -- para ver CUANDO ocurrieron los peores momentos y cuanto duraron, no
solo el numero final.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, DIAS_ORDEN

CARPETA = os.path.dirname(__file__)
CAPITAL_INICIAL = 1000.0
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'
GREEN, RED = '#26a69a', '#ef5350'


def curva_con_fechas(fechas, r_serie, riesgo, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    fechas_out = [fechas[0]]
    valores = [capital]
    for f, r in zip(fechas, r_serie):
        capital += capital * riesgo * r
        fechas_out.append(f)
        valores.append(capital)
    return fechas_out, valores


def drawdown_curva(valores):
    s = pd.Series(valores)
    pico = s.cummax()
    dd = (s - pico) / pico * 100
    return dd.values


def peor_tramo_drawdown(fechas, dd):
    """Encuentra el tramo (inicio del pico, fecha del valle) del peor
    drawdown, para poder sombrearlo y anotar cuanto duro."""
    idx_valle = int(np.argmin(dd))
    # buscar hacia atras el ultimo punto en 0 (el pico previo al valle)
    idx_pico = idx_valle
    while idx_pico > 0 and dd[idx_pico] < 0:
        idx_pico -= 1
    return fechas[idx_pico], fechas[idx_valle], dd[idx_valle]


def graficar_perfil(ax_eq, ax_dd, fechas, valores, nombre, color):
    dd = drawdown_curva(valores)
    ax_eq.plot(fechas, valores, color=color, linewidth=1.3)
    ax_eq.set_yscale('log')
    ax_eq.set_facecolor(BG)
    ax_eq.set_title(nombre, color=WHITE, fontsize=11, fontweight='bold', loc='left')
    ax_eq.grid(color=GRID, linewidth=0.4, alpha=0.5)
    ax_eq.tick_params(colors=WHITE, labelsize=8)
    for s in ax_eq.spines.values():
        s.set_color(GRID)
    ax_eq.set_ylabel('Capital (USD, log)', color=WHITE, fontsize=8)

    ax_dd.fill_between(fechas, dd, 0, color=RED, alpha=0.35)
    ax_dd.plot(fechas, dd, color=RED, linewidth=0.8)
    ax_dd.set_facecolor(BG)
    ax_dd.grid(color=GRID, linewidth=0.4, alpha=0.5)
    ax_dd.tick_params(colors=WHITE, labelsize=8)
    for s in ax_dd.spines.values():
        s.set_color(GRID)
    ax_dd.set_ylabel('Drawdown %', color=WHITE, fontsize=8)

    f_pico, f_valle, peor = peor_tramo_drawdown(fechas, dd)
    dias_tramo = (f_valle - f_pico).days
    ax_dd.axvspan(f_pico, f_valle, color='white', alpha=0.08)
    ax_dd.annotate(f"peor tramo: {peor:.1f}%\n{dias_tramo} días ({f_pico.strftime('%d/%m/%y')} → {f_valle.strftime('%d/%m/%y')})",
                    xy=(f_valle, peor), xytext=(10, -25), textcoords='offset points',
                    color=WHITE, fontsize=7.5, arrowprops=dict(arrowstyle='->', color=WHITE, lw=0.8))
    return f_pico, f_valle, peor, dias_tramo


if __name__ == '__main__':
    df = cargar_todo_cronologico()
    fechas_full = df['Fecha_dt'].tolist()
    r_full = df['Beneficio_R'].values

    df_hib = pd.read_csv(os.path.join(CARPETA, 'gestion_hibrida_resultado.csv'))
    df_hib['Fecha_dt'] = pd.to_datetime(df_hib['Fecha_dt'])
    df_hib = df_hib.sort_values(['Fecha_dt', 'Hora apertura (NY)'])
    fechas_hib = df_hib['Fecha_dt'].tolist()
    r_hib = df_hib['Beneficio_R'].values

    perfiles = [
        ('CONSERVADOR -- Gestión Híbrida, riesgo 3%', fechas_hib, r_hib, 0.03, '#42a5f5'),
        ('MODERADO -- Riesgo parejo 3% (todos los días)', fechas_full, r_full, 0.03, '#ffb300'),
        ('AGRESIVO -- Riesgo parejo 5% (todos los días)', fechas_full, r_full, 0.05, '#ef5350'),
    ]

    fig, axes = plt.subplots(3, 2, figsize=(15, 12), facecolor=BG,
                              gridspec_kw={'height_ratios': [1, 1, 1], 'width_ratios': [2.2, 1]})

    resumen = []
    for i, (nombre, fechas, r_serie, riesgo, color) in enumerate(perfiles):
        f_out, valores = curva_con_fechas(fechas, r_serie, riesgo)
        ax_eq = axes[i][0]
        # panel de drawdown como sub-eje debajo, pero para simplificar usamos 2 columnas:
        # columna 0 = equity ancho, columna 1 = zoom del peor tramo (drawdown)
        dd = drawdown_curva(valores)
        ax_eq.plot(f_out, valores, color=color, linewidth=1.2)
        ax_eq.set_yscale('log')
        ax_eq.set_facecolor(BG)
        ax_eq.set_title(nombre, color=WHITE, fontsize=10.5, fontweight='bold', loc='left')
        ax_eq.grid(color=GRID, linewidth=0.4, alpha=0.5)
        ax_eq.tick_params(colors=WHITE, labelsize=7.5)
        for s in ax_eq.spines.values():
            s.set_color(GRID)
        ax_eq.set_ylabel('Capital USD (log)', color=WHITE, fontsize=8)
        ax_eq.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))

        ax_dd = axes[i][1]
        ax_dd.fill_between(f_out, dd, 0, color=RED, alpha=0.4)
        ax_dd.plot(f_out, dd, color=RED, linewidth=0.9)
        ax_dd.set_facecolor(BG)
        ax_dd.grid(color=GRID, linewidth=0.4, alpha=0.5)
        ax_dd.tick_params(colors=WHITE, labelsize=7.5)
        for s in ax_dd.spines.values():
            s.set_color(GRID)
        ax_dd.set_ylabel('Drawdown %', color=WHITE, fontsize=8)
        ax_dd.set_title('Curva de drawdown (underwater)', color=WHITE, fontsize=9, loc='left')
        ax_dd.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))

        f_pico, f_valle, peor = peor_tramo_drawdown(f_out, dd)
        dias_tramo = (f_valle - f_pico).days
        ax_dd.axvspan(f_pico, f_valle, color='white', alpha=0.10)
        ax_dd.annotate(f"{peor:.1f}% en {dias_tramo}d", xy=(f_valle, peor), xytext=(5, -18),
                        textcoords='offset points', color=WHITE, fontsize=7.5,
                        arrowprops=dict(arrowstyle='->', color=WHITE, lw=0.7))

        resumen.append(dict(perfil=nombre, capital_final=round(valores[-1], 2),
                             retorno_pct=round((valores[-1]/CAPITAL_INICIAL-1)*100, 1),
                             drawdown_max_pct=round(dd.min(), 1),
                             peor_tramo_dias=dias_tramo, peor_tramo_inicio=str(f_pico.date()), peor_tramo_fin=str(f_valle.date())))

    plt.tight_layout()
    out_png = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/perfiles_equity_drawdown.png'
    plt.savefig(out_png, dpi=150, facecolor=BG)
    print(f"Guardado: {out_png}")

    pd.DataFrame(resumen).to_csv(os.path.join(CARPETA, 'perfiles_equity_drawdown_resumen.csv'), index=False)
    for r in resumen:
        print(r)
