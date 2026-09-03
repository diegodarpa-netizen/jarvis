"""
Graficos adicionales para completar el panorama visual del informe
(03/09/2026), a pedido de Diego: heatmap de dia de semana x sesion,
histograma de bootstrap, barras de Kelly por dia, y barras de la
escalera de descenso de riesgo ponderado.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, DIAS_ORDEN, kelly_por_dia
from combinacion_final_7_6_4 import bootstrap_por_dias_reales

np.random.seed(41)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'
GREEN, RED = '#26a69a', '#ef5350'

df = cargar_todo_cronologico()

# ============ 1) HEATMAP dia de semana x sesion (% dias positivos) ============
NY_CSV = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
ny = pd.read_csv(NY_CSV); ny['Fecha_dt'] = pd.to_datetime(ny['Fecha_dt']); ny['sesion'] = 'NY'
pre = pd.read_csv(os.path.join(CARPETA, 'pre_ny_consolidado.csv')); pre['Fecha_dt'] = pd.to_datetime(pre['Fecha_dt']); pre['sesion'] = 'Pre-NY'
asia = pd.read_csv(os.path.join(CARPETA, 'asia_consolidado.csv')); asia['Fecha_dt'] = pd.to_datetime(asia['Fecha_dt']); asia['sesion'] = 'Asia'
full = pd.concat([ny[['Fecha_dt', 'Beneficio_R', 'sesion']], pre[['Fecha_dt', 'Beneficio_R', 'sesion']], asia[['Fecha_dt', 'Beneficio_R', 'sesion']]], ignore_index=True)
full['dia_semana'] = full['Fecha_dt'].dt.dayofweek.map(dict(enumerate(DIAS_ORDEN)))

matriz = pd.DataFrame(index=['NY', 'Pre-NY', 'Asia'], columns=DIAS_ORDEN, dtype=float)
for sesion in ['NY', 'Pre-NY', 'Asia']:
    for dia in DIAS_ORDEN:
        g = full[(full['sesion'] == sesion) & (full['dia_semana'] == dia)]
        if len(g) == 0:
            continue
        r_dia = g.groupby('Fecha_dt')['Beneficio_R'].sum()
        matriz.loc[sesion, dia] = (r_dia > 0).mean() * 100

fig, ax = plt.subplots(figsize=(11, 4.2), facecolor=BG)
ax.set_facecolor(BG)
datos = matriz.values.astype(float)
im = ax.imshow(datos, cmap='RdYlGn', vmin=40, vmax=90, aspect='auto')
ax.set_xticks(range(len(DIAS_ORDEN))); ax.set_xticklabels(DIAS_ORDEN, color=WHITE, fontsize=9)
ax.set_yticks(range(3)); ax.set_yticklabels(['NY', 'Pre-NY', 'Asia'], color=WHITE, fontsize=9)
for i in range(3):
    for j in range(len(DIAS_ORDEN)):
        v = datos[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{v:.0f}%", ha='center', va='center', color='#131722', fontsize=9, fontweight='bold')
ax.set_title('% de días positivos por sesión y día de semana', color=WHITE, fontsize=11, loc='left', fontweight='bold')
cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
cbar.ax.yaxis.set_tick_params(color=WHITE)
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=WHITE)
for s in ax.spines.values():
    s.set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(GRAF_DIR, 'heatmap_dia_semana_sesion.png'), dpi=150, facecolor=BG)
print("Guardado: heatmap_dia_semana_sesion.png")

# ============ 2) HISTOGRAMA bootstrap (drawdown), 3% y 5% parejo ============
fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor=BG)
for ax, pct, color in zip(axes, [3, 5], ['#ffb300', '#ef5350']):
    riesgo_dia = {d: pct / 100 for d in DIAS_ORDEN}
    finales, drawdowns = bootstrap_por_dias_reales(df, riesgo_dia, n_iter=3000)
    ax.hist(drawdowns, bins=40, color=color, alpha=0.85, edgecolor=BG)
    ax.axvline(np.median(drawdowns), color=WHITE, linestyle='--', linewidth=1, label=f'Mediana: {np.median(drawdowns):.1f}%')
    ax.axvline(np.percentile(drawdowns, 5), color=WHITE, linestyle=':', linewidth=1, label=f'Percentil 5: {np.percentile(drawdowns, 5):.1f}%')
    ax.set_facecolor(BG)
    ax.set_title(f'Distribución de drawdown -- {pct}% parejo\n(3.000 universos bootstrap)', color=WHITE, fontsize=10.5)
    ax.set_xlabel('Drawdown máximo (%)', color=WHITE, fontsize=9)
    ax.set_ylabel('Frecuencia', color=WHITE, fontsize=9)
    ax.tick_params(colors=WHITE, labelsize=8)
    ax.grid(color=GRID, linewidth=0.4, alpha=0.5)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(GRAF_DIR, 'histograma_bootstrap_drawdown.png'), dpi=150, facecolor=BG)
print("Guardado: histograma_bootstrap_drawdown.png")

# ============ 3) BARRAS Kelly por dia ============
kelly = kelly_por_dia(df)
dias_validos = [d for d in DIAS_ORDEN if d in kelly]
fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG)
ax.set_facecolor(BG)
valores_kelly = [kelly[d] * 100 for d in dias_validos]
valores_medio = [v / 2 for v in valores_kelly]
x = np.arange(len(dias_validos))
ax.bar(x - 0.2, valores_kelly, width=0.4, color='#448aff', label='Kelly completo')
ax.bar(x + 0.2, valores_medio, width=0.4, color='#26a69a', label='Medio-Kelly')
ax.set_xticks(x); ax.set_xticklabels(dias_validos, color=WHITE, fontsize=9)
ax.set_ylabel('% de riesgo sugerido', color=WHITE, fontsize=9)
ax.set_title('Kelly Criterion por día de semana', color=WHITE, fontsize=11, loc='left', fontweight='bold')
ax.tick_params(colors=WHITE, labelsize=8)
ax.grid(color=GRID, linewidth=0.4, alpha=0.5, axis='y')
for s in ax.spines.values():
    s.set_color(GRID)
ax.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=9)
for i, v in enumerate(valores_kelly):
    ax.text(i - 0.2, v + 1, f"{v:.0f}%", ha='center', color=WHITE, fontsize=8)
for i, v in enumerate(valores_medio):
    ax.text(i + 0.2, v + 1, f"{v:.0f}%", ha='center', color=WHITE, fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(GRAF_DIR, 'kelly_por_dia.png'), dpi=150, facecolor=BG)
print("Guardado: kelly_por_dia.png")

# ============ 4) BARRAS escalera de descenso (retorno log + drawdown) ============
escalera = pd.read_csv(os.path.join(CARPETA, 'escalera_descenso_1pto_resumen.csv'))
fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor=BG)
ax1, ax2 = axes
colores_barra = plt.cm.autumn(np.linspace(0.1, 0.9, len(escalera)))[::-1]

ax1.bar(escalera['combinacion'], escalera['retorno_pct'], color=colores_barra)
ax1.set_yscale('log')
ax1.set_facecolor(BG)
ax1.set_title('Retorno por escalón (escala log)', color=WHITE, fontsize=10.5, loc='left')
ax1.tick_params(colors=WHITE, labelsize=7.5, rotation=30)
ax1.grid(color=GRID, linewidth=0.4, alpha=0.5, axis='y')
for s in ax1.spines.values():
    s.set_color(GRID)

ax2.bar(escalera['combinacion'], escalera['drawdown_real_pct'].abs(), color=colores_barra)
ax2.set_facecolor(BG)
ax2.set_title('Drawdown real por escalón (%)', color=WHITE, fontsize=10.5, loc='left')
ax2.tick_params(colors=WHITE, labelsize=7.5, rotation=30)
ax2.grid(color=GRID, linewidth=0.4, alpha=0.5, axis='y')
for s in ax2.spines.values():
    s.set_color(GRID)
plt.tight_layout()
plt.savefig(os.path.join(GRAF_DIR, 'escalera_descenso_barras.png'), dpi=150, facecolor=BG)
print("Guardado: escalera_descenso_barras.png")
