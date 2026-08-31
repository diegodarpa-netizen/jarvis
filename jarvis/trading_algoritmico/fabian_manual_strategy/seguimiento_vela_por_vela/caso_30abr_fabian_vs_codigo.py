"""
Caso 3/5: 30/04/2026 -- Fabian SELL 09:34 (MEC/START) vs codigo SELL 09:35
(1 min despues). Analisis exhaustivo (28/08/2026).
"""
import pandas as pd
import numpy as np
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
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/caso_30abr_fabian_vs_codigo.png'


def dibujar_velas(ax, g):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = VERDE if c >= o else ROJO
        ax.plot([i, i], [l, h], color=color, linewidth=1.3, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else 0.01
        base = min(o, c)
        rect = patches.Rectangle((i - 0.32, base), 0.64, alto, facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)


def nube(ax, x, y_precio, texto, es_sell, y_rango):
    offset = y_rango * 0.07
    y_caja = y_precio + offset if es_sell else y_precio - offset
    box = FancyBboxPatch((x - 2.6, y_caja - (0 if es_sell else 0.55) * y_rango * 0.1),
                          5.2, y_rango * 0.1, boxstyle="round,pad=0.3,rounding_size=1.2",
                          facecolor='#8c8c8c', edgecolor='#6b6b6b', zorder=6)
    ax.add_patch(box)
    ax.text(x, y_caja + (y_rango * 0.05 if es_sell else -y_rango * 0.05), texto,
             ha='center', va='center', color='white', fontsize=11, fontweight='bold', zorder=7)
    ax.plot([x, x], [y_precio, y_caja], color='#6b6b6b', linewidth=1.3, zorder=5)


if __name__ == '__main__':
    df = cargar()
    df['day'] = df.index.date
    dia = pd.Timestamp('2026-04-30').date()
    g = df[df['day'] == dia]
    _, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
    g_amplia = g[g.index <= fin]

    ini_vis, fin_vis = ventana_ny(pd.Timestamp(dia), 9, 28, 9, 42)
    g_vis = g_amplia[(g_amplia.index >= ini_vis) & (g_amplia.index <= fin_vis)].reset_index()
    g_vis.columns = ['time', 'open', 'high', 'low', 'close', 'n_ticks', 'day']

    y_min, y_max = g_vis['low'].min(), g_vis['high'].max()
    y_rango = y_max - y_min

    fig, axes = plt.subplots(1, 2, figsize=(19, 8), dpi=130, facecolor='#131722')

    for ax, t_entrada_str, titulo, anot in zip(
        axes,
        ['2026-04-30 09:34:00', '2026-04-30 09:35:00'],
        ['FABIAN (real) -- SELL 09:34 -- MEC (START)',
         'CÓDIGO -- SELL 09:35 -- MEC-A (1 min después)'],
        ['09:34: vela bajista, en la dirección de la\ntendencia, pero cuerpo = 44,7% -- no llega\nal piso de 50% que exige la fórmula',
         '09:35: cuerpo = 69,7%, sí llega al piso -- se\ntoma como la vela de continuación válida']
    ):
        ax.set_facecolor('#131722')
        dibujar_velas(ax, g_vis)
        t_entrada = NY.localize(pd.Timestamp(t_entrada_str)).astimezone(UTC)
        idx_e = g_vis['time'].searchsorted(t_entrada)
        precio_e = g_vis['high'].iloc[idx_e]
        nube(ax, idx_e, precio_e, 'SELL', True, y_rango)
        ax.axvline(idx_e, color='white', linestyle=':', linewidth=0.7, alpha=0.5)
        ax.text(0.02, 0.03, anot, transform=ax.transAxes, color='#e0a030', fontsize=9,
                 va='bottom', ha='left', bbox=dict(facecolor='#1c2028', edgecolor='#e0a030', alpha=0.85, pad=6))
        ax.tick_params(colors='#787b86')
        for s in ax.spines.values():
            s.set_color('#2a2e39')
        ax.set_title(titulo, color='white', fontsize=12, fontweight='bold')
        ax.set_ylabel('Precio (USD)', color='white')

    plt.tight_layout()
    plt.savefig(OUT, facecolor='#131722', bbox_inches='tight')
    print(f"Guardado: {OUT}")
