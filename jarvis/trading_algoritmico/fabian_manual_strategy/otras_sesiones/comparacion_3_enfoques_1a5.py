"""
03/09/2026: comparacion de los 3 enfoques (Parejo / Martingala / Anti-
Martingala) sobre la misma grilla de riesgo base 1%-5%, a pedido de
Diego -- "combinar las 3 cosas... y comparar los datos".

Para Martingala y Anti-Martingala, cada base b usa 5 niveles
duplicando: [b, 2b, 4b, 8b, 16b] (el mismo diseño de 5 niveles que
planteo Diego originalmente).
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, DIAS_ORDEN, curva_riesgo_variable, max_drawdown
from escalera_de_riesgo_martingala import simular_escalera, bootstrap_escalera, CAPITAL_INICIAL, N_ITER
from escalera_nivel_por_nivel_y_antimartingala import simular_anti_martingala, bootstrap_anti_martingala
from combinacion_final_7_6_4 import bootstrap_por_dias_reales

np.random.seed(81)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'

df = cargar_todo_cronologico()
r_serie = df['Beneficio_R'].values
n = len(r_serie)

BASES = [1, 2, 3, 4, 5]
filas = []

print("=" * 110)
print("COMPARACION -- Parejo vs Martingala (con tope) vs Anti-Martingala, base 1%-5%")
print("=" * 110)

for b in BASES:
    niveles = [b/100 * (2 ** i) for i in range(5)]

    # --- PAREJO ---
    riesgo_dia = {d: b/100 for d in DIAS_ORDEN}
    valores_p = curva_riesgo_variable(df, riesgo_dia, capital_inicial=CAPITAL_INICIAL)
    final_p = valores_p[-1]
    ret_p = (final_p / CAPITAL_INICIAL - 1) * 100
    dd_p = max_drawdown(valores_p)
    finales_pb, dd_pb = bootstrap_por_dias_reales(df, riesgo_dia, n_iter=2000)
    p_dd30_p = (dd_pb < -30).mean() * 100

    # --- MARTINGALA (con tope) ---
    valores_m, reventada_m, nivel_max_m, _ = simular_escalera(r_serie, niveles, con_tope=True)
    final_m = valores_m[-1]
    ret_m = (final_m / CAPITAL_INICIAL - 1) * 100
    dd_m = max_drawdown(valores_m)
    _, _, reventadas_sin_tope = bootstrap_escalera(r_serie, niveles, n, con_tope=False, n_iter=2000)
    p_ruina_m = reventadas_sin_tope / 2000 * 100

    # --- ANTI-MARTINGALA ---
    valores_am, reventada_am, nivel_max_am = simular_anti_martingala(r_serie, niveles)
    final_am = valores_am[-1]
    ret_am = (final_am / CAPITAL_INICIAL - 1) * 100
    dd_am = max_drawdown(valores_am)
    finales_amb, dd_amb = bootstrap_anti_martingala(r_serie, niveles, n, n_iter=2000)
    p_dd30_am = (dd_amb < -30).mean() * 100

    print(f"\n--- Base {b}% ---")
    print(f"{'Enfoque':<20}{'Capital final':>15}{'Retorno':>13}{'Drawdown real':>15}{'Riesgo de cola':>20}")
    print(f"{'Parejo':<20}USD {final_p:>10,.0f}{ret_p:>+12.1f}%{dd_p:>+14.1f}%{'P(DD<-30%)=' + f'{p_dd30_p:.1f}%':>20}")
    print(f"{'Martingala (tope)':<20}USD {final_m:>10,.0f}{ret_m:>+12.1f}%{dd_m:>+14.1f}%{'P(RUINA sin tope)=' + f'{p_ruina_m:.1f}%':>20}")
    print(f"{'Anti-Martingala':<20}USD {final_am:>10,.0f}{ret_am:>+12.1f}%{dd_am:>+14.1f}%{'P(DD<-30%)=' + f'{p_dd30_am:.1f}%':>20}")

    filas.append(dict(base_pct=b, enfoque='Parejo', capital_final=round(final_p, 2), retorno_pct=round(ret_p, 1),
                       drawdown_pct=round(dd_p, 1), riesgo_cola_pct=round(p_dd30_p, 1), tipo_riesgo_cola='P(DD<-30%)'))
    filas.append(dict(base_pct=b, enfoque='Martingala (tope nivel 5)', capital_final=round(final_m, 2), retorno_pct=round(ret_m, 1),
                       drawdown_pct=round(dd_m, 1), riesgo_cola_pct=round(p_ruina_m, 1), tipo_riesgo_cola='P(RUINA sin tope)'))
    filas.append(dict(base_pct=b, enfoque='Anti-Martingala', capital_final=round(final_am, 2), retorno_pct=round(ret_am, 1),
                       drawdown_pct=round(dd_am, 1), riesgo_cola_pct=round(p_dd30_am, 1), tipo_riesgo_cola='P(DD<-30%)'))

tabla = pd.DataFrame(filas)
tabla.to_csv(os.path.join(CARPETA, 'comparacion_3_enfoques_1a5_tabla.csv'), index=False)

# ---- grafico: 3 lineas (retorno log) x 3 lineas (drawdown), por enfoque, vs base ----
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), facecolor=BG)
ax1, ax2 = axes
ax1.set_facecolor(BG); ax2.set_facecolor(BG)
colores = {'Parejo': '#448aff', 'Martingala (tope nivel 5)': '#ef5350', 'Anti-Martingala': '#26a69a'}
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
plt.savefig(os.path.join(GRAF_DIR, 'comparacion_3_enfoques_1a5.png'), dpi=150, facecolor=BG)
print(f"\nGuardado: comparacion_3_enfoques_1a5.png")
