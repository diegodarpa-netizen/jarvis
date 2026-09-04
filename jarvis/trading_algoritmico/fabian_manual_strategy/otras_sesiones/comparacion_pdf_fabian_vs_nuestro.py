"""
04/09/2026 -- comparacion final: la Martingala de Fabian (3 perfiles del
PDF "TRDNG SYSTEM") vs. nuestro sistema "2 confirmaciones", corridos
ambos sobre LA MISMA base de datos (157 operaciones, Gestion Hibrida
Pre-NY+Asia, 26/01/2026-28/08/2026, ~31 semanas) para que la
comparacion sea de igual a igual.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escalera_de_riesgo_martingala import simular_escalera, bootstrap_escalera, max_drawdown, CAPITAL_INICIAL
from antimartingala_2confirmaciones import simular_antimartingala_2conf, bootstrap_2conf

np.random.seed(221)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'

df = pd.read_csv(os.path.join(CARPETA, 'gestion_hibrida_31semanas_resultado.csv'))
df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
df = df.sort_values(['Fecha_dt', 'Hora apertura (NY)'])
r = df['Beneficio_R'].values
n = len(r)
N_MESES = 7.04

PARES = [
    ('Conservador', 0.25, [0.0025, 0.005, 0.01, 0.02, 0.04]),
    ('Moderado', 0.5, [0.005, 0.01, 0.02, 0.04, 0.08]),
    ('Arriesgado', 1.0, [0.01, 0.02, 0.04, 0.08, 0.16]),
]

filas = []
for nombre, base, niveles in PARES:
    # Martingala de Fabian
    valores_m, _, _, _ = simular_escalera(r, niveles, con_tope=True)
    ret_m = ((valores_m[-1] / CAPITAL_INICIAL) ** (1 / N_MESES) - 1) * 100
    dd_m = max_drawdown(valores_m)
    _, _, reventadas = bootstrap_escalera(r, niveles, n, con_tope=False, n_iter=3000)
    p_ruina_m = reventadas / 3000 * 100

    # Nuestro 2 confirmaciones, mismo base
    valores_2c = simular_antimartingala_2conf(r, base, incremento_pct=1.0)
    ret_2c = ((valores_2c[-1] / CAPITAL_INICIAL) ** (1 / N_MESES) - 1) * 100
    dd_2c = max_drawdown(valores_2c)

    filas.append(dict(perfil=nombre, base=base, ret_mensual_martingala=round(ret_m, 2), dd_martingala=round(dd_m, 1),
                       p_ruina_martingala=round(p_ruina_m, 2), ret_mensual_2conf=round(ret_2c, 2), dd_2conf=round(dd_2c, 1)))

tabla = pd.DataFrame(filas)
tabla.to_csv(os.path.join(CARPETA, 'comparacion_pdf_fabian_vs_nuestro_tabla.csv'), index=False)
print(tabla.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), facecolor=BG)
ax1, ax2 = axes
ax1.set_facecolor(BG); ax2.set_facecolor(BG)
x = np.arange(3)
width = 0.35
ax1.bar(x - width/2, tabla['ret_mensual_martingala'], width, color='#ef5350', label='Martingala (Fabian)')
ax1.bar(x + width/2, tabla['ret_mensual_2conf'], width, color='#26a69a', label='2 confirmaciones (nuestro)')
ax1.set_xticks(x); ax1.set_xticklabels(tabla['perfil'], color=WHITE, fontsize=9)
ax1.set_ylabel('Retorno MENSUAL geométrico (%)', color=WHITE, fontsize=9)
ax1.set_title('Retorno mensual -- misma base de 157 operaciones', color=WHITE, fontsize=10.5, loc='left')
ax1.tick_params(colors=WHITE, labelsize=8)
ax1.grid(color=GRID, linewidth=0.4, alpha=0.5, axis='y')
for s in ax1.spines.values():
    s.set_color(GRID)
ax1.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=8)

ax2.bar(x - width/2, tabla['dd_martingala'].abs(), width, color='#ef5350', label='Martingala (Fabian)')
ax2.bar(x + width/2, tabla['dd_2conf'].abs(), width, color='#26a69a', label='2 confirmaciones (nuestro)')
ax2.set_xticks(x); ax2.set_xticklabels(tabla['perfil'], color=WHITE, fontsize=9)
ax2.set_ylabel('Drawdown real (%)', color=WHITE, fontsize=9)
ax2.set_title('Drawdown -- misma base de 157 operaciones', color=WHITE, fontsize=10.5, loc='left')
ax2.tick_params(colors=WHITE, labelsize=8)
ax2.grid(color=GRID, linewidth=0.4, alpha=0.5, axis='y')
for s in ax2.spines.values():
    s.set_color(GRID)
ax2.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(GRAF_DIR, 'comparacion_pdf_fabian_vs_nuestro.png'), dpi=150, facecolor=BG)
print(f"\nGuardado: comparacion_pdf_fabian_vs_nuestro.png")
