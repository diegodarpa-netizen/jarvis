"""
Visual de la escalera de riesgo / Martingala (03/09/2026): barras de
probabilidad de reventar la cuenta (sin tope) + ejemplos de caminos
simulados para "Muy arriesgado" (algunos sobreviven, uno revienta).
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico
from escalera_de_riesgo_martingala import PERFILES, simular_escalera, CAPITAL_INICIAL

np.random.seed(61)
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'
GREEN, RED = '#26a69a', '#ef5350'
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'

df = cargar_todo_cronologico()
r_serie = df['Beneficio_R'].values
n = len(r_serie)

sin_tope = pd.read_csv(os.path.join(os.path.dirname(__file__), 'escalera_martingala_sin_tope_bootstrap.csv'))

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), facecolor=BG)

# --- panel 1: barras de probabilidad de reventar ---
ax = axes[0]
ax.set_facecolor(BG)
colores = ['#42a5f5', '#ffb300', '#ff7043', '#ef5350']
bars = ax.bar(sin_tope['perfil'], sin_tope['p_reventada_pct'], color=colores)
for b, v in zip(bars, sin_tope['p_reventada_pct']):
    ax.text(b.get_x() + b.get_width()/2, v + 0.5, f"{v:.1f}%", ha='center', color=WHITE, fontsize=10, fontweight='bold')
ax.set_ylabel('Probabilidad de perder TODO el capital (%)', color=WHITE, fontsize=9)
ax.set_title('Escalera de riesgo SIN TOPE -- probabilidad de reventar la cuenta\n(5.000 universos bootstrap, misma cantidad de operaciones que el histórico)', color=WHITE, fontsize=10, loc='left')
ax.tick_params(colors=WHITE, labelsize=9)
ax.grid(color=GRID, linewidth=0.4, alpha=0.5, axis='y')
for s in ax.spines.values():
    s.set_color(GRID)

# --- panel 2: 8 caminos simulados de "Muy arriesgado" sin tope ---
ax2 = axes[1]
ax2.set_facecolor(BG)
niveles = PERFILES['Muy arriesgado']
n_caminos = 15
reventados = 0
for i in range(n_caminos):
    muestra = np.random.choice(r_serie, size=n, replace=True)
    valores, reventada, _, _ = simular_escalera(muestra, niveles, con_tope=False)
    color = RED if reventada else GREEN
    alpha = 0.9 if reventada else 0.35
    ax2.plot(valores, color=color, linewidth=1.3 if reventada else 0.8, alpha=alpha)
    if reventada:
        reventados += 1
ax2.set_yscale('symlog')
ax2.set_title(f'15 caminos simulados -- "Muy arriesgado" SIN TOPE\n({reventados} de {n_caminos} terminaron en cero, en rojo)', color=WHITE, fontsize=10, loc='left')
ax2.set_xlabel('Operación #', color=WHITE, fontsize=9)
ax2.set_ylabel('Capital (USD, escala simétrica-log)', color=WHITE, fontsize=9)
ax2.tick_params(colors=WHITE, labelsize=8)
ax2.grid(color=GRID, linewidth=0.4, alpha=0.5)
for s in ax2.spines.values():
    s.set_color(GRID)

plt.tight_layout()
out_png = os.path.join(GRAF_DIR, 'escalera_martingala_riesgo_ruina.png')
plt.savefig(out_png, dpi=150, facecolor=BG)
print(f"Guardado: {out_png}")
