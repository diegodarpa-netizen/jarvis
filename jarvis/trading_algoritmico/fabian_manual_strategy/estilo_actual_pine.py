"""
Como se ve el formato de etiqueta que YA ESTA en EstrategiaXAU.pine (sin
tocar) -- label.new con triangulo + modelo, fondo de color al 15%,
size.tiny, estilo label_down/label_up. A pedido de Diego (28/08/2026) para
comparar contra las alternativas nuevas antes de decidir.
"""
import pandas as pd
import pytz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import sys
sys.path.append('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy')
from prueba_ventana_horaria import cargar, ventana_ny

NY = pytz.timezone('America/New_York')
UTC = pytz.UTC
VERDE, ROJO = '#26a69a', '#ef5350'
FONDO = '#131722'
GRID = '#1e222d'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/estilo_actual_pine.png'


def dibujar_velas(ax, g):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = VERDE if c >= o else ROJO
        ax.plot([i, i], [l, h], color=color, linewidth=1.4, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else 0.015
        base = min(o, c)
        rect = patches.Rectangle((i - 0.32, base), 0.64, alto, facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)


def label_actual(ax, x, y_ancla, direccion, y_rango):
    """Replica label.new(..., color=color.new(green/red,15), textcolor=white,
    size=size.tiny, style=label_up/label_down) -- fondo solido tenue
    (15% opacity = 85% alpha en matplotlib), triangulo + texto chico."""
    color = ROJO if direccion == 'SELL' else VERDE
    tri = '▼' if direccion == 'SELL' else '▲'
    texto = f'{tri} MEC-A'
    if direccion == 'SELL':
        y_caja = y_ancla + y_rango * 0.02
        va = 'bottom'
    else:
        y_caja = y_ancla - y_rango * 0.02
        va = 'top'
    ax.text(x, y_caja, texto, color='white', fontsize=7, fontweight='bold',
            ha='center', va=va, zorder=7,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.85, edgecolor='none'))


if __name__ == '__main__':
    df = cargar()
    df['day'] = df.index.date
    dia = pd.Timestamp('2026-02-12').date()
    g = df[df['day'] == dia]
    _, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
    g_amplia = g[g.index <= fin]
    ini_vis, fin_vis = ventana_ny(pd.Timestamp(dia), 9, 0, 9, 9)
    g_vis = g_amplia[(g_amplia.index >= ini_vis) & (g_amplia.index <= fin_vis)].reset_index()
    g_vis.columns = ['time', 'open', 'high', 'low', 'close', 'n_ticks', 'day']

    y_min, y_max = g_vis['low'].min() - 1.0, g_vis['high'].max() + 1.0
    y_rango = y_max - y_min
    x_entrada = 3

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), dpi=140, facecolor=FONDO)

    for ax, direccion in zip(axes, ['SELL', 'BUY']):
        ax.set_facecolor(FONDO)
        ax.grid(True, color=GRID, linewidth=0.5, zorder=0)
        ax.set_axisbelow(True)
        dibujar_velas(ax, g_vis)
        y_ancla = g_vis['low'].iloc[x_entrada] if direccion == 'SELL' else g_vis['low'].iloc[x_entrada]
        # el pine actual ancla label_down en el HIGH (arriba de la vela) para
        # SELL y label_up en el LOW (abajo) para BUY
        y_ancla = g_vis['high'].iloc[x_entrada] if direccion == 'SELL' else g_vis['low'].iloc[x_entrada]
        ax.axvline(x_entrada, color='#e0e0e0', linestyle=':', linewidth=0.6, alpha=0.35)
        label_actual(ax, x_entrada, y_ancla, direccion, y_rango)
        ax.set_xlim(-0.6, len(g_vis) - 0.4)
        ax.set_ylim(y_min, y_max)
        ax.set_xticks([])
        ax.tick_params(colors='#787b86', labelsize=7)
        for spine in ax.spines.values():
            spine.set_color('#2a2e39')
        ax.set_title(direccion, color='#d1d4dc', fontsize=12, fontweight='bold')

    fig.suptitle('Formato ACTUAL del .pine (sin tocar) -- ▲/▼ + modelo, fondo tenue', color='white', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(OUT, facecolor=FONDO, bbox_inches='tight')
    print(f"Guardado: {OUT}")
