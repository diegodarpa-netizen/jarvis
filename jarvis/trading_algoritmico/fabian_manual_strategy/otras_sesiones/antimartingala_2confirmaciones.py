"""
03/09/2026, a pedido de Diego: variante nueva de Anti-Martingala --
"si hay dos buenas, la tercera aumentamos", subiendo de a 1 punto
porcentual (lineal, no duplicando) por cada ganancia adicional despues
de la 2da confirmacion. Se compara contra Parejo y contra el
Anti-Martingala clasico (duplica desde la 1ra ganancia) en la grilla
1%-5% de base.

Regla exacta implementada:
  - Rachas ganadoras de 1 o 2: riesgo = base (no sube todavia).
  - 3ra ganancia seguida en adelante: riesgo = base + 1% por cada
    ganancia extra sobre la 2da (3ra->+1, 4ta->+2, 5ta->+3, ... tope en
    +4 puntos, o sea 5 niveles totales incluida la base).
  - Cualquier perdida: resetea de una a la base.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, DIAS_ORDEN, curva_riesgo_variable, max_drawdown
from escalera_de_riesgo_martingala import CAPITAL_INICIAL, N_ITER
from escalera_nivel_por_nivel_y_antimartingala import simular_anti_martingala

np.random.seed(101)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'

df = cargar_todo_cronologico()
r_serie = df['Beneficio_R'].values
n = len(r_serie)


def simular_antimartingala_2conf(r_seq, base_pct, incremento_pct=1.0, tope_niveles=5, capital_inicial=CAPITAL_INICIAL):
    """base_pct e incremento_pct en % (ej. 2.0 = 2%)."""
    capital = capital_inicial
    valores = [capital]
    racha_ganadora = 0
    for r in r_seq:
        if racha_ganadora < 2:
            riesgo = base_pct / 100
        else:
            # racha_ganadora==2 (va a jugarse la 3ra) -> +1 punto; ==3 -> +2; ...
            # tope en tope_niveles-1 puntos extra sobre la base.
            nivel_extra = min(racha_ganadora - 1, tope_niveles - 1)
            riesgo = (base_pct + incremento_pct * nivel_extra) / 100
        capital += capital * riesgo * r
        valores.append(capital)
        if r > 0:
            racha_ganadora += 1
        else:
            racha_ganadora = 0
    return valores


def bootstrap_2conf(r_pool, base_pct, incremento_pct, n_ops, n_iter=N_ITER):
    finales = np.empty(n_iter)
    drawdowns = np.empty(n_iter)
    for it in range(n_iter):
        muestra = np.random.choice(r_pool, size=n_ops, replace=True)
        valores = simular_antimartingala_2conf(muestra, base_pct, incremento_pct)
        finales[it] = valores[-1]
        drawdowns[it] = max_drawdown(valores)
    return finales, drawdowns


if __name__ == '__main__':
    BASES = [1, 2, 3, 4, 5]
    filas = []

    print("=" * 110)
    print("COMPARACION -- Parejo vs Anti-Martingala clasico (duplica) vs Anti-Martingala '2 confirmaciones +1%'")
    print("=" * 110)

    for b in BASES:
        # Parejo
        riesgo_dia = {d: b / 100 for d in DIAS_ORDEN}
        valores_p = curva_riesgo_variable(df, riesgo_dia, capital_inicial=CAPITAL_INICIAL)
        final_p, dd_p = valores_p[-1], max_drawdown(valores_p)
        ret_p = (final_p / CAPITAL_INICIAL - 1) * 100

        # Anti-Martingala clasico (duplica desde la 1ra ganancia, 5 niveles)
        niveles = [b/100 * (2 ** i) for i in range(5)]
        valores_amc, _, _ = simular_anti_martingala(r_serie, niveles)
        final_amc, dd_amc = valores_amc[-1], max_drawdown(valores_amc)
        ret_amc = (final_amc / CAPITAL_INICIAL - 1) * 100

        # Anti-Martingala 2 confirmaciones, +1% lineal
        valores_2c = simular_antimartingala_2conf(r_serie, b, incremento_pct=1.0)
        final_2c, dd_2c = valores_2c[-1], max_drawdown(valores_2c)
        ret_2c = (final_2c / CAPITAL_INICIAL - 1) * 100
        finales_b, drawdowns_b = bootstrap_2conf(r_serie, b, 1.0, n, n_iter=2000)
        p_pos_2c = (finales_b > CAPITAL_INICIAL).mean() * 100
        dd_p5_2c = np.percentile(drawdowns_b, 5)

        print(f"\n--- Base {b}% ---")
        print(f"{'Enfoque':<32}{'Capital final':>15}{'Retorno':>13}{'Drawdown real':>15}")
        print(f"{'Parejo':<32}USD {final_p:>10,.0f}{ret_p:>+12.1f}%{dd_p:>+14.1f}%")
        print(f"{'Anti-Mart. clasico (x2)':<32}USD {final_amc:>10,.0f}{ret_amc:>+12.1f}%{dd_amc:>+14.1f}%")
        print(f"{'Anti-Mart. 2conf (+1%/nivel)':<32}USD {final_2c:>10,.0f}{ret_2c:>+12.1f}%{dd_2c:>+14.1f}%   [bootstrap: P(+)={p_pos_2c:.1f}%  DD peor5%={dd_p5_2c:+.1f}%]")

        filas.append(dict(base_pct=b, enfoque='Parejo', capital_final=round(final_p, 2), retorno_pct=round(ret_p, 1), drawdown_pct=round(dd_p, 1)))
        filas.append(dict(base_pct=b, enfoque='Anti-Mart. clásico (x2)', capital_final=round(final_amc, 2), retorno_pct=round(ret_amc, 1), drawdown_pct=round(dd_amc, 1)))
        filas.append(dict(base_pct=b, enfoque='Anti-Mart. 2conf (+1%/nivel)', capital_final=round(final_2c, 2), retorno_pct=round(ret_2c, 1), drawdown_pct=round(dd_2c, 1),
                           p_positivo_bootstrap=round(p_pos_2c, 1), dd_peor5_bootstrap=round(dd_p5_2c, 1)))

    tabla = pd.DataFrame(filas)
    tabla.to_csv(os.path.join(CARPETA, 'antimartingala_2confirmaciones_tabla.csv'), index=False)

    # -- grafico --
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), facecolor=BG)
    ax1, ax2 = axes
    ax1.set_facecolor(BG); ax2.set_facecolor(BG)
    colores = {'Parejo': '#448aff', 'Anti-Mart. clásico (x2)': '#ef5350', 'Anti-Mart. 2conf (+1%/nivel)': '#26a69a'}
    for enfoque, g in tabla.groupby('enfoque'):
        ax1.plot(g['base_pct'], g['retorno_pct'], color=colores[enfoque], marker='o', linewidth=1.8, label=enfoque)
        ax2.plot(g['base_pct'], g['drawdown_pct'].abs(), color=colores[enfoque], marker='o', linewidth=1.8, label=enfoque)
    ax1.set_yscale('log')
    ax1.set_xlabel('Riesgo base (%)', color=WHITE, fontsize=9)
    ax1.set_ylabel('Retorno (%, escala log)', color=WHITE, fontsize=9)
    ax1.set_title('Retorno por enfoque, según riesgo base', color=WHITE, fontsize=10.5, loc='left')
    ax1.tick_params(colors=WHITE, labelsize=8)
    ax1.grid(color=GRID, linewidth=0.4, alpha=0.5)
    for s in ax1.spines.values():
        s.set_color(GRID)
    ax1.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=8)

    ax2.set_xlabel('Riesgo base (%)', color=WHITE, fontsize=9)
    ax2.set_ylabel('Drawdown máximo real (%, valor absoluto)', color=WHITE, fontsize=9)
    ax2.set_title('Drawdown por enfoque, según riesgo base', color=WHITE, fontsize=10.5, loc='left')
    ax2.tick_params(colors=WHITE, labelsize=8)
    ax2.grid(color=GRID, linewidth=0.4, alpha=0.5)
    for s in ax2.spines.values():
        s.set_color(GRID)
    ax2.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(GRAF_DIR, 'antimartingala_2confirmaciones.png'), dpi=150, facecolor=BG)
    print(f"\nGuardado: antimartingala_2confirmaciones.png")
