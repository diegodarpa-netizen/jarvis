"""
Comparacion 21/04/2026: Fabian real (SELL 09:05, MER) vs codigo (SELL 09:06,
MER) -- caso de duda del margen 0.01%, a pedido de Diego (28/08/2026) para
poder comparar visualmente y, si hace falta, consultarle a Fabian por que
entro un minuto antes de que el nivel se rompiera formalmente.
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
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/comparacion_21abr_fabian_vs_codigo.png'


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


def marcar_nivel(ax, nivel, x_ini, x_fin, y_rango, texto):
    ax.plot([x_ini, x_fin], [nivel, nivel], color='#787b86', linestyle='--', linewidth=1.1, alpha=0.85)
    ax.text(x_fin + 0.3, nivel, texto, color='#9aa0a8', fontsize=8, va='center')


if __name__ == '__main__':
    df = cargar()
    df['day'] = df.index.date
    dia = pd.Timestamp('2026-04-21').date()
    g = df[df['day'] == dia]
    _, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
    g_amplia = g[g.index <= fin]

    # ventana visual: 08:57 a 09:12 NY
    ini_vis, fin_vis = ventana_ny(pd.Timestamp(dia), 8, 57, 9, 12)
    g_vis = g_amplia[(g_amplia.index >= ini_vis) & (g_amplia.index <= fin_vis)].reset_index()
    g_vis.columns = ['time', 'open', 'high', 'low', 'close', 'n_ticks', 'day']
    x_map = {t: i for i, t in enumerate(g_vis['time'])}

    nivel_bajo = 4776.305  # nivel M3 bajo activo en ese momento (calculado antes)
    y_min, y_max = g_vis['low'].min(), g_vis['high'].max()
    y_rango = y_max - y_min

    fig, axes = plt.subplots(1, 2, figsize=(19, 8), dpi=130, facecolor='#131722')

    for ax, t_entrada_str, titulo in zip(
        axes,
        ['2026-04-21 09:05:00', '2026-04-21 09:06:00'],
        ['FABIAN (real) -- SELL 09:05 -- MER',
         'CÓDIGO -- SELL 09:06 -- MER (1 min después, margen 0,01%)']
    ):
        ax.set_facecolor('#131722')
        dibujar_velas(ax, g_vis)
        t_entrada = NY.localize(pd.Timestamp(t_entrada_str)).astimezone(UTC)
        idx_e = g_vis['time'].searchsorted(t_entrada)
        precio_e = g_vis['high'].iloc[idx_e]
        nube(ax, idx_e, precio_e, 'SELL', True, y_rango)
        ax.axvline(idx_e, color='white', linestyle=':', linewidth=0.7, alpha=0.5)
        marcar_nivel(ax, nivel_bajo, 0, len(g_vis) - 1, y_rango, f'nivel M3 bajo {nivel_bajo:.2f}')
        umbral = nivel_bajo * 0.9999
        ax.axhline(umbral, color='#e57373', linestyle=':', linewidth=0.8, alpha=0.6)
        ax.text(len(g_vis) - 1, umbral, f'  umbral 0,01% {umbral:.2f}', color='#e57373', fontsize=7.5, va='center')
        ax.tick_params(colors='#787b86')
        for s in ax.spines.values():
            s.set_color('#2a2e39')
        ax.set_title(titulo, color='white', fontsize=12, fontweight='bold')
        ax.set_ylabel('Precio (USD)', color='white')

    plt.tight_layout()
    plt.savefig(OUT, facecolor='#131722', bbox_inches='tight')
    print(f"Guardado: {OUT}")
