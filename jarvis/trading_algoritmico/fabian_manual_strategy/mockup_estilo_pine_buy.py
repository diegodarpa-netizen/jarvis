"""
Mismo mockup de estetica que mockup_estilo_pine.py, pero para un caso BUY
(18/02/2026, 09:31, MEC/Envolvente, TP +1R) -- a pedido de Diego, para ver
como quedaria la etiqueta verde antes de pasar todo al .pine.
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
FONDO = '#131722'
GRID = '#1e222d'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/mockup_estilo_pine_buy_dia3.png'


def dibujar_velas(ax, g):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = VERDE if c >= o else ROJO
        ax.plot([i, i], [l, h], color=color, linewidth=1.1, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else 0.015
        base = min(o, c)
        rect = patches.Rectangle((i - 0.35, base), 0.70, alto, facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)


if __name__ == '__main__':
    df = cargar()
    df['day'] = df.index.date
    dia = pd.Timestamp('2026-02-18').date()
    g = df[df['day'] == dia]
    _, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
    g_amplia = g[g.index <= fin]

    ini_vis, fin_vis = ventana_ny(pd.Timestamp(dia), 9, 20, 9, 42)
    g_vis = g_amplia[(g_amplia.index >= ini_vis) & (g_amplia.index <= fin_vis)].reset_index()
    g_vis.columns = ['time', 'open', 'high', 'low', 'close', 'n_ticks', 'day']

    t_entrada = NY.localize(pd.Timestamp('2026-02-18 09:31:00')).astimezone(UTC)
    t_salida = NY.localize(pd.Timestamp('2026-02-18 09:36:00')).astimezone(UTC)
    idx_entrada = g_vis['time'].searchsorted(t_entrada)
    idx_salida = g_vis['time'].searchsorted(t_salida)

    entrada, sl, tp = 4967.965, 4955.620, 4979.076
    bajo_m3_level_viejo = 4952.325
    bajo_m3_level_nuevo = 4955.620

    # todo el tramo visible esta en tendencia alcista (tend_state=1)
    tend_por_vela = [1] * len(g_vis)

    y_min = min(g_vis['low'].min(), sl) - 1.5
    y_max = max(g_vis['high'].max(), tp) + 1.5

    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=140, facecolor=FONDO)
    ax.set_facecolor(FONDO)

    for i in range(len(tend_por_vela)):
        pass
    ax.axvspan(-0.5, len(g_vis) - 0.5, color=VERDE, alpha=0.14, zorder=0)

    ax.grid(True, color=GRID, linewidth=0.6, zorder=1)
    ax.set_axisbelow(True)

    dibujar_velas(ax, g_vis)

    ax.plot([0, 6], [bajo_m3_level_viejo, bajo_m3_level_viejo], color='#787b86', linestyle=':', linewidth=1.0, alpha=0.5)
    ax.plot([6, len(g_vis) - 1], [bajo_m3_level_nuevo, bajo_m3_level_nuevo], color='#787b86', linestyle='--', linewidth=1.1, alpha=0.8)

    ax.plot([idx_entrada, idx_salida], [entrada, entrada], color='#e0e0e0', linestyle='-', linewidth=1.4, zorder=4)
    ax.plot([idx_entrada, idx_salida], [sl, sl], color=ROJO, linestyle='--', linewidth=1.2, alpha=0.9, zorder=4)
    ax.plot([idx_entrada, idx_salida], [tp, tp], color=VERDE, linestyle='--', linewidth=1.2, alpha=0.9, zorder=4)

    color_label = VERDE  # BUY
    label_w, label_h = 0.85, (y_max - y_min) * 0.075
    label_y = entrada + (y_max - y_min) * 0.025
    box = FancyBboxPatch((idx_entrada - label_w / 2, label_y), label_w, label_h,
                          boxstyle="round,pad=0.1,rounding_size=0.7",
                          facecolor=color_label, edgecolor='none', zorder=6)
    ax.add_patch(box)
    ax.text(idx_entrada, label_y + label_h / 2, 'BUY', color='white', fontsize=8,
            fontweight='bold', ha='center', va='center', rotation=90, zorder=7)
    ax.plot([idx_entrada, idx_entrada], [entrada, label_y], color=color_label, linewidth=1.0, alpha=0.6, zorder=5)
    ax.axvline(idx_entrada, color='#e0e0e0', linestyle=':', linewidth=0.6, alpha=0.4)
    ax.axvline(idx_salida, color='#e0e0e0', linestyle=':', linewidth=0.6, alpha=0.4)

    xt = list(range(0, len(g_vis), 3))
    ax.set_xticks(xt)
    ax.set_xticklabels([g_vis['time'].iloc[i].tz_convert(NY).strftime('%H:%M') for i in xt], color='#787b86', fontsize=8)
    ax.set_xlim(-1, len(g_vis) + 3)
    ax.set_ylim(y_min, y_max)

    ax.tick_params(colors='#787b86')
    for spine in ax.spines.values():
        spine.set_color('#2a2e39')
    ax.set_ylabel('XAUUSD (USD)', color='#d1d4dc')
    ax.set_title('EstrategiaXAU -- mockup estetica (caso BUY)\n18/02/2026 -- BUY 09:31 -- MEC/Envolvente -- TP +1.0R',
                  color='#d1d4dc', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUT, facecolor=FONDO, bbox_inches='tight')
    print(f"Guardado: {OUT}")
