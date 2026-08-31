"""
Caso 5/5: 25/08/2026 -- Fabian SELL 10:19 (MER) vs codigo: NUNCA reconoce
esta señal en toda la sesion. Analisis exhaustivo (28/08/2026).
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
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/caso_25ago_fabian_vs_codigo.png'


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
    dia = pd.Timestamp('2026-08-25').date()
    g = df[df['day'] == dia]
    _, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
    g_amplia = g[g.index <= fin]

    ini_vis, fin_vis = ventana_ny(pd.Timestamp(dia), 10, 13, 10, 26)
    g_vis = g_amplia[(g_amplia.index >= ini_vis) & (g_amplia.index <= fin_vis)].reset_index()
    g_vis.columns = ['time', 'open', 'high', 'low', 'close', 'n_ticks', 'day']

    nivel_bajo = 4619.71
    umbral = nivel_bajo * 0.9999
    y_min, y_max = g_vis['low'].min(), g_vis['high'].max()
    y_rango = y_max - y_min

    fig, ax = plt.subplots(figsize=(12, 8), dpi=130, facecolor='#131722')
    ax.set_facecolor('#131722')
    dibujar_velas(ax, g_vis)

    t_entrada = NY.localize(pd.Timestamp('2026-08-25 10:19:00')).astimezone(UTC)
    idx_e = g_vis['time'].searchsorted(t_entrada)
    precio_e = g_vis['high'].iloc[idx_e]
    nube(ax, idx_e, precio_e, 'SELL', True, y_rango)
    ax.axvline(idx_e, color='white', linestyle=':', linewidth=0.7, alpha=0.5)

    ax.plot([0, len(g_vis) - 1], [nivel_bajo, nivel_bajo], color='#787b86', linestyle='--', linewidth=1.0, alpha=0.85)
    ax.text(len(g_vis) - 1, nivel_bajo, f'  nivel M3 {nivel_bajo:.3f}', color='#9aa0a8', fontsize=8, va='center')
    ax.axhline(umbral, color='#e57373', linestyle=':', linewidth=0.9, alpha=0.7)
    ax.text(len(g_vis) - 1, umbral, f'  umbral 0,01% {umbral:.3f}', color='#e57373', fontsize=8, va='center')

    anot = ('FABIAN entra SELL 10:19 -- MER.\n'
            'La vela: cuerpo 81,9%, cierra en su propio\n'
            'mínimo (4619,375) -- patrón limpio y fuerte.\n'
            'Pero el low queda a solo USD 0,13 del umbral\n'
            'del 0,01% (4619,248) -- no lo cruza.\n\n'
            'CÓDIGO: nunca reconoce esta señal en toda\n'
            'la sesión -- el nivel recién se rompe a las\n'
            '10:22 (vela distinta, sin patrón propio).')
    ax.text(0.02, 0.03, anot, transform=ax.transAxes, color='#e0a030', fontsize=9.5,
            va='bottom', ha='left', bbox=dict(facecolor='#1c2028', edgecolor='#e0a030', alpha=0.9, pad=8))

    ax.tick_params(colors='#787b86')
    for s in ax.spines.values():
        s.set_color('#2a2e39')
    ax.set_title('25/08/2026 -- FABIAN SELL 10:19 (MER) -- CÓDIGO: sin reconocer', color='white', fontsize=13, fontweight='bold')
    ax.set_ylabel('Precio (USD)', color='white')

    plt.tight_layout()
    plt.savefig(OUT, facecolor='#131722', bbox_inches='tight')
    print(f"Guardado: {OUT}")
