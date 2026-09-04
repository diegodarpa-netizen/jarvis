"""
04/09/2026 -- referencia visual rapida de la operativa de "2
confirmaciones + incremento 2%" (base 3%), para consulta del dia a dia.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'
GREEN, RED, GRAY = '#26a69a', '#ef5350', '#787b86'

operaciones = ['1ra', '2da', '3ra', '4ta', '5ta', '6ta', '7ma+']
riesgos = [3, 3, 5, 7, 9, 11, 11]
ganancias_seguidas = ['0 (recien empieza)', '1 ganancia', '2 ganancias', '3 ganancias',
                       '4 ganancias', '5 ganancias', '6+ ganancias (tope)']

fig, ax = plt.subplots(figsize=(11, 6), facecolor=BG)
ax.set_facecolor(BG)
colores = [GRAY, GRAY, '#42a5f5', '#42a5f5', '#42a5f5', '#42a5f5', GREEN]
bars = ax.bar(operaciones, riesgos, color=colores, width=0.6)
for b, r, g in zip(bars, riesgos, ganancias_seguidas):
    ax.text(b.get_x() + b.get_width()/2, r + 0.3, f"{r}%", ha='center', color=WHITE, fontsize=12, fontweight='bold')
    ax.text(b.get_x() + b.get_width()/2, -0.9, g, ha='center', color=GRAY, fontsize=7.5, rotation=0)

ax.axhline(3, color=WHITE, linestyle=':', linewidth=1, alpha=0.5)
ax.text(6.7, 3.3, 'base (3%)', color=WHITE, fontsize=8, ha='right')
ax.axhline(11, color=GREEN, linestyle=':', linewidth=1, alpha=0.5)
ax.text(6.7, 11.4, 'techo (11%, no sube más)', color=GREEN, fontsize=8, ha='right')

ax.set_ylim(-1.5, 13)
ax.set_ylabel('Riesgo de esa operación (%)', color=WHITE, fontsize=10)
ax.set_title('Operativa "2 confirmaciones + incremento 2%" (base 3%)\nAnte CUALQUIER pérdida, vuelve directo a la 1ra columna (3%)',
              color=WHITE, fontsize=11, loc='left', fontweight='bold')
ax.tick_params(colors=WHITE, labelsize=9)
ax.grid(color=GRID, linewidth=0.4, alpha=0.4, axis='y')
for s in ax.spines.values():
    s.set_color(GRID)

plt.tight_layout()
out = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/operativa_2confirmaciones_visual.png'
plt.savefig(out, dpi=150, facecolor=BG)
print(f"Guardado: {out}")
