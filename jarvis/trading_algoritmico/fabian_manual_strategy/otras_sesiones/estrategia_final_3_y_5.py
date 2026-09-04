"""
04/09/2026 -- curva final de la estrategia ganadora (2 confirmaciones,
incremento lineal 2%/nivel, todos los dias) a base 3% y 5%, para el
informe completo que se le va a mostrar a Fabian.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico
from escalera_de_riesgo_martingala import CAPITAL_INICIAL
from antimartingala_2confirmaciones import simular_antimartingala_2conf

CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'
GREEN, RED = '#26a69a', '#ef5350'


def curva_con_fechas_2conf(fechas, r_serie, base_pct, incremento_pct, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    fechas_out = [fechas[0]]
    valores = [capital]
    racha = 0
    for f, r in zip(fechas, r_serie):
        if racha < 2:
            riesgo = base_pct / 100
        else:
            nivel_extra = min(racha - 1, 4)
            riesgo = (base_pct + incremento_pct * nivel_extra) / 100
        capital += capital * riesgo * r
        fechas_out.append(f)
        valores.append(capital)
        racha = racha + 1 if r > 0 else 0
    return fechas_out, valores


def drawdown_curva(valores):
    s = pd.Series(valores)
    pico = s.cummax()
    return ((s - pico) / pico * 100).values


if __name__ == '__main__':
    df = cargar_todo_cronologico()
    fechas = df['Fecha_dt'].tolist()
    r_serie = df['Beneficio_R'].values

    fig, axes = plt.subplots(2, 2, figsize=(15, 8.5), facecolor=BG,
                              gridspec_kw={'height_ratios': [1.3, 1]})

    for col, base in enumerate([3, 5]):
        f_out, valores = curva_con_fechas_2conf(fechas, r_serie, base, incremento_pct=2.0)
        dd = drawdown_curva(valores)

        ax_eq = axes[0][col]
        ax_eq.plot(f_out, valores, color='#26a69a' if base == 3 else '#ffb300', linewidth=1.2)
        ax_eq.set_yscale('log')
        ax_eq.set_facecolor(BG)
        ret = (valores[-1] / CAPITAL_INICIAL - 1) * 100
        ax_eq.set_title(f"Estrategia final -- Base {base}% + 2 confirmaciones (+2%/nivel)\n"
                         f"USD {CAPITAL_INICIAL:,.0f} -> USD {valores[-1]:,.0f}  ({ret:+,.1f}%)",
                         color=WHITE, fontsize=10, loc='left', fontweight='bold')
        ax_eq.grid(color=GRID, linewidth=0.4, alpha=0.5)
        ax_eq.tick_params(colors=WHITE, labelsize=8)
        for s in ax_eq.spines.values():
            s.set_color(GRID)
        ax_eq.set_ylabel('Capital USD (log)', color=WHITE, fontsize=8)
        ax_eq.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))

        ax_dd = axes[1][col]
        ax_dd.fill_between(f_out, dd, 0, color=RED, alpha=0.4)
        ax_dd.plot(f_out, dd, color=RED, linewidth=0.9)
        ax_dd.set_facecolor(BG)
        ax_dd.set_title(f'Drawdown en el tiempo -- máximo {dd.min():.1f}%', color=WHITE, fontsize=9, loc='left')
        ax_dd.grid(color=GRID, linewidth=0.4, alpha=0.5)
        ax_dd.tick_params(colors=WHITE, labelsize=8)
        for s in ax_dd.spines.values():
            s.set_color(GRID)
        ax_dd.set_ylabel('Drawdown %', color=WHITE, fontsize=8)
        ax_dd.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))

    plt.tight_layout()
    out_png = os.path.join(GRAF_DIR, 'estrategia_final_3_y_5.png')
    plt.savefig(out_png, dpi=150, facecolor=BG)
    print(f"Guardado: {out_png}")
