"""
3 casos nuevos sin explicar (28/10 SELL 09:04, 26/11 BUY 09:35, 26/11 BUY
10:10) -- analisis exhaustivo con imagenes, mismo estandar que los 5
anteriores. A pedido de Diego (30/08/2026).
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


def dibujar_velas(ax, g):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = VERDE if c >= o else ROJO
        ax.plot([i, i], [l, h], color=color, linewidth=1.3, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else 0.015
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


def graficar(dia_str, hora_str, direccion, ini_h, ini_m, fin_h, fin_m, nivel=None, texto_nivel='', out=''):
    df = cargar()
    df['day'] = df.index.date
    dia = pd.Timestamp(dia_str).date()
    g = df[df['day'] == dia]
    _, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
    g_amplia = g[g.index <= fin]
    ini_vis, fin_vis = ventana_ny(pd.Timestamp(dia), ini_h, ini_m, fin_h, fin_m)
    g_vis = g_amplia[(g_amplia.index >= ini_vis) & (g_amplia.index <= fin_vis)].reset_index()
    g_vis.columns = ['time', 'open', 'high', 'low', 'close', 'n_ticks', 'day']

    y_min, y_max = g_vis['low'].min() - 1.0, g_vis['high'].max() + 1.0
    y_rango = y_max - y_min

    fig, ax = plt.subplots(figsize=(15, 8), dpi=130, facecolor=FONDO)
    ax.set_facecolor(FONDO)
    dibujar_velas(ax, g_vis)

    t_entrada = NY.localize(pd.Timestamp(f'{dia_str} {hora_str}:00')).astimezone(UTC)
    idx_e = g_vis['time'].searchsorted(t_entrada)
    es_sell = direccion == 'SELL'
    precio_e = g_vis['high'].iloc[idx_e] if es_sell else g_vis['low'].iloc[idx_e]
    nube(ax, idx_e, precio_e, direccion, es_sell, y_rango)
    ax.axvline(idx_e, color='white', linestyle=':', linewidth=0.7, alpha=0.5)

    if nivel is not None:
        ax.plot([0, len(g_vis) - 1], [nivel, nivel], color='#787b86', linestyle='--', linewidth=1.0, alpha=0.8)
        ax.text(len(g_vis) - 1, nivel, f'  {texto_nivel}', color='#9aa0a8', fontsize=8, va='center')

    xt = list(range(0, len(g_vis), 3))
    ax.set_xticks(xt)
    ax.set_xticklabels([g_vis['time'].iloc[i].tz_convert(NY).strftime('%H:%M') for i in xt], color='#787b86', fontsize=8)
    ax.tick_params(colors='#787b86')
    for spine in ax.spines.values():
        spine.set_color('#2a2e39')
    ax.set_ylabel('XAUUSD (USD)', color='white')
    ax.set_title(f'{dia_str} -- FABIAN {direccion} {hora_str} (código no reconoce nada en esa dirección)',
                 color='white', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(out, facecolor=FONDO, bbox_inches='tight')
    print(f"Guardado: {out}")


if __name__ == '__main__':
    graficar('2025-10-28', '09:04', 'SELL', 8, 45, 9, 12, nivel=3926.17, texto_nivel='alto M3 3926.17',
              out='/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/caso_28oct_fabian.png')
    graficar('2025-11-26', '09:35', 'BUY', 9, 25, 9, 45,
              out='/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/caso_26nov_0935_fabian.png')
    graficar('2025-11-26', '10:10', 'BUY', 9, 55, 10, 20, nivel=4151.48, texto_nivel='alto M3 4151.48',
              out='/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/caso_26nov_1010_fabian.png')
