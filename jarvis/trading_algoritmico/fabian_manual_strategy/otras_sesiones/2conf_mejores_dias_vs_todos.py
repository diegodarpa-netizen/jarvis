"""
04/09/2026, a pedido de Diego: combinar la variante ganadora (Anti-
Martingala 2 confirmaciones + incremento lineal 1%) con el patron de
dia de semana -- comparar operar SOLO los mejores dias (Miercoles,
Martes, Jueves) vs operar TODOS los dias que realmente opera Fabian
(las 482 operaciones completas, los 6 dias que aparecen en el dataset).
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, max_drawdown
from escalera_de_riesgo_martingala import CAPITAL_INICIAL, N_ITER
from antimartingala_2confirmaciones import simular_antimartingala_2conf, bootstrap_2conf

np.random.seed(121)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'

df = cargar_todo_cronologico()
MEJORES_DIAS = ['Martes', 'Miércoles', 'Jueves']

r_todos = df['Beneficio_R'].values
r_mejores = df[df['dia_semana'].isin(MEJORES_DIAS)].sort_values(['Fecha_dt', 'orden_sesion', 'hora'])['Beneficio_R'].values

print(f"Todos los dias: {len(r_todos)} operaciones")
print(f"Solo Martes/Miercoles/Jueves: {len(r_mejores)} operaciones ({len(r_mejores)/len(r_todos)*100:.1f}% del total)")

BASES = [1, 2, 3, 4, 5]
filas = []

print("\n" + "=" * 100)
print("2 CONFIRMACIONES -- Solo mejores dias (Mar/Mie/Jue) vs TODOS los dias")
print("=" * 100)

for b in BASES:
    v_todos = simular_antimartingala_2conf(r_todos, b, incremento_pct=1.0)
    v_mejores = simular_antimartingala_2conf(r_mejores, b, incremento_pct=1.0)

    f_t, dd_t = v_todos[-1], max_drawdown(v_todos)
    f_m, dd_m = v_mejores[-1], max_drawdown(v_mejores)
    ret_t = (f_t / CAPITAL_INICIAL - 1) * 100
    ret_m = (f_m / CAPITAL_INICIAL - 1) * 100

    finales_tb, dd_tb = bootstrap_2conf(r_todos, b, 1.0, len(r_todos), n_iter=2000)
    finales_mb, dd_mb = bootstrap_2conf(r_mejores, b, 1.0, len(r_mejores), n_iter=2000)
    p_pos_t = (finales_tb > CAPITAL_INICIAL).mean() * 100
    p_pos_m = (finales_mb > CAPITAL_INICIAL).mean() * 100

    print(f"\n--- Base {b}% ---")
    print(f"  TODOS los dias ({len(r_todos)} ops):        USD {f_t:>12,.0f}  retorno {ret_t:>+12.1f}%  drawdown {dd_t:>+7.1f}%  P(+)={p_pos_t:.1f}%")
    print(f"  Solo Mar/Mie/Jue ({len(r_mejores)} ops):     USD {f_m:>12,.0f}  retorno {ret_m:>+12.1f}%  drawdown {dd_m:>+7.1f}%  P(+)={p_pos_m:.1f}%")

    filas.append(dict(base_pct=b, universo='Todos los días', n_ops=len(r_todos), capital_final=round(f_t, 2),
                       retorno_pct=round(ret_t, 1), drawdown_pct=round(dd_t, 1), p_positivo_bootstrap=round(p_pos_t, 1)))
    filas.append(dict(base_pct=b, universo='Solo Mar/Mié/Jue', n_ops=len(r_mejores), capital_final=round(f_m, 2),
                       retorno_pct=round(ret_m, 1), drawdown_pct=round(dd_m, 1), p_positivo_bootstrap=round(p_pos_m, 1)))

tabla = pd.DataFrame(filas)
tabla.to_csv(os.path.join(CARPETA, '2conf_mejores_dias_vs_todos_tabla.csv'), index=False)

# -- grafico --
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), facecolor=BG)
ax1, ax2 = axes
ax1.set_facecolor(BG); ax2.set_facecolor(BG)
colores = {'Todos los días': '#448aff', 'Solo Mar/Mié/Jue': '#ff9800'}
for universo, g in tabla.groupby('universo'):
    ax1.plot(g['base_pct'], g['retorno_pct'], color=colores[universo], marker='o', linewidth=1.8, label=universo)
    ax2.plot(g['base_pct'], g['drawdown_pct'].abs(), color=colores[universo], marker='o', linewidth=1.8, label=universo)
ax1.set_yscale('log')
ax1.set_xlabel('Riesgo base (%)', color=WHITE, fontsize=9)
ax1.set_ylabel('Retorno (%, escala log)', color=WHITE, fontsize=9)
ax1.set_title('2 confirmaciones -- retorno: todos los días vs. mejores días', color=WHITE, fontsize=10, loc='left')
ax1.tick_params(colors=WHITE, labelsize=8)
ax1.grid(color=GRID, linewidth=0.4, alpha=0.5)
for s in ax1.spines.values():
    s.set_color(GRID)
ax1.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=8.5)

ax2.set_xlabel('Riesgo base (%)', color=WHITE, fontsize=9)
ax2.set_ylabel('Drawdown máximo real (%, valor absoluto)', color=WHITE, fontsize=9)
ax2.set_title('2 confirmaciones -- drawdown: todos los días vs. mejores días', color=WHITE, fontsize=10, loc='left')
ax2.tick_params(colors=WHITE, labelsize=8)
ax2.grid(color=GRID, linewidth=0.4, alpha=0.5)
for s in ax2.spines.values():
    s.set_color(GRID)
ax2.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=8.5)

plt.tight_layout()
plt.savefig(os.path.join(GRAF_DIR, '2conf_mejores_dias_vs_todos.png'), dpi=150, facecolor=BG)
print(f"\nGuardado: 2conf_mejores_dias_vs_todos.png")
