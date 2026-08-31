"""
Resumen visual de la calibracion vela por vela -- estado final 30/08/2026,
para el informe completo que pidio Diego.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/resumen_calibracion_30ago.png'

fig, axes = plt.subplots(1, 2, figsize=(18, 7), dpi=130)

# --- Panel 1: EXACTO vs pendientes, sobre las 191 operaciones ---
ax1 = axes[0]
categorias = ['EXACTO (180)', 'Diferencia broker OANDA/Dukascopy (8)', 'Regla N°5 noticias -- confirmado (1)',
              'Sin explicar todavia (1)', 'Fecha ambigua en el registro (1)']
valores = [180, 8, 1, 1, 1]
colores = ['#2ca02c', '#f0a020', '#5b8def', '#d62728', '#888888']
wedges, texts, autotexts = ax1.pie(valores, colors=colores, autopct=lambda p: f'{p:.1f}%' if p > 3 else '',
                                     startangle=90, textprops={'fontsize': 10, 'color': 'white', 'fontweight': 'bold'},
                                     pctdistance=0.8)
ax1.legend(wedges, categorias, loc='center left', bbox_to_anchor=(-0.55, 0.5), fontsize=10, frameon=False)
ax1.set_title('Las 191 operaciones reales de Fabian\n180/191 exactas (94,2%)', fontsize=13, fontweight='bold')

# --- Panel 2: evolucion del % de acierto durante la sesion ---
ax2 = axes[1]
etapas = ['Antes\n(sin patrón\nSTART)', 'M3 continuo +\nSTART fusionado\n(139 op.)', 'Fix mecha\n(139 op.)',
          'Revert a\ncuerpo (PDF)\n(191 op.)', 'Mecha\nrestaurada\n(191 op.)']
pct = [0, 96.4, 96.4, 91.6, 94.2]
n_ops = [139, 139, 139, 191, 191]
colores2 = ['#888888', '#5b8def', '#2ca02c', '#d62728', '#2ca02c']
barras = ax2.bar(range(len(etapas)), pct, color=colores2)
for i, (bar, p, n) in enumerate(zip(barras, pct, n_ops)):
    if p > 0:
        ax2.text(bar.get_x() + bar.get_width()/2, p + 1.5, f'{p:.1f}%\n(n={n})', ha='center', fontsize=9, fontweight='bold')
ax2.set_xticks(range(len(etapas)))
ax2.set_xticklabels(etapas, fontsize=9)
ax2.set_ylabel('% de operaciones EXACTAS')
ax2.set_ylim(0, 105)
ax2.set_title('Evolución del % de acierto durante la calibración (28-30/08/2026)', fontsize=13, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUT, bbox_inches='tight')
print(f"Guardado: {OUT}")
