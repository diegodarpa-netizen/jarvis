"""
Comparacion dia por dia: 12/02/2026 (primer dia del backtesting), Fabian
(real, mano) vs codigo mecanico (EstrategiaXAU replicado en Python).
Dos imagenes, mismo estilo aprobado (velas rojo/verde, lineas M3
punteadas, cartel tipo nube). A pedido de Diego (27/08/2026).
"""
import pandas as pd
import numpy as np
import pytz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
NY = pytz.timezone('America/New_York')
UTC = pytz.UTC
VERDE, ROJO = '#26a69a', '#ef5350'


def dibujar_velas(ax, g):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = VERDE if c >= o else ROJO
        ax.plot([i, i], [l, h], color=color, linewidth=1, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else 0.01
        base = min(o, c)
        rect = patches.Rectangle((i - 0.3, base), 0.6, alto, facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)


def nube(ax, x, y_precio, texto, es_sell, y_rango):
    offset = y_rango * 0.06
    y_caja = y_precio + offset if es_sell else y_precio - offset
    box = FancyBboxPatch((x - 3, y_caja - (0 if es_sell else 0.55) * y_rango * 0.09),
                          6, y_rango * 0.09, boxstyle="round,pad=0.3,rounding_size=1.2",
                          facecolor='#8c8c8c', edgecolor='#6b6b6b', zorder=6)
    ax.add_patch(box)
    ax.text(x, y_caja + (y_rango * 0.045 if es_sell else -y_rango * 0.045), texto,
             ha='center', va='center', color='white', fontsize=10, fontweight='bold', zorder=7)
    ax.plot([x, x], [y_precio, y_caja], color='#6b6b6b', linewidth=1.3, zorder=5)


def marcar_m3(ax, m3, x_offset_map):
    for i in range(len(m3) - 1):
        v2, v1 = m3.iloc[i], m3.iloc[i + 1]
        if v2['close'] > v2['open'] and v1['close'] < v1['open']:
            nivel = max(v2['high'], v1['high'])
            t_ini = m3.index[i]
            if t_ini in x_offset_map:
                ax.plot([x_offset_map[t_ini], x_offset_map[t_ini] + 15], [nivel, nivel],
                        color='#787b86', linestyle='--', linewidth=0.9, alpha=0.7)
        if v2['close'] < v2['open'] and v1['close'] > v1['open']:
            nivel = min(v2['low'], v1['low'])
            t_ini = m3.index[i]
            if t_ini in x_offset_map:
                ax.plot([x_offset_map[t_ini], x_offset_map[t_ini] + 15], [nivel, nivel],
                        color='#787b86', linestyle='--', linewidth=0.9, alpha=0.7)


if __name__ == '__main__':
    ohlc = pd.read_csv(INPUT, index_col=0)
    ohlc.index = pd.to_datetime(ohlc.index, utc=True)
    ohlc = ohlc.sort_index()

    dia = pd.Timestamp('2026-02-12').date()
    g = ohlc[ohlc.index.date == dia]
    ini = NY.localize(pd.Timestamp(2026, 2, 12, 9, 1)).astimezone(UTC)
    fin = NY.localize(pd.Timestamp(2026, 2, 12, 10, 59)).astimezone(UTC)
    g_sesion = g[(g.index >= ini) & (g.index <= fin)].reset_index()
    g_sesion.columns = ['time', 'open', 'high', 'low', 'close', 'n_ticks']

    x_map = {t: i for i, t in enumerate(g_sesion['time'])}
    m3 = g['close'].loc[ini:fin].resample('3min').ohlc().dropna()

    y_min, y_max = g_sesion['low'].min(), g_sesion['high'].max()
    y_rango = y_max - y_min

    # --- Imagen 1: Fabian real (09:03 entrada, 09:16 salida, SELL) ---
    fig1, ax1 = plt.subplots(figsize=(15, 8), dpi=130, facecolor='#131722')
    ax1.set_facecolor('#131722')
    dibujar_velas(ax1, g_sesion)
    marcar_m3(ax1, m3, x_map)
    t_entrada_fab = NY.localize(pd.Timestamp(2026, 2, 12, 9, 3)).astimezone(UTC)
    idx_fab = g_sesion['time'].searchsorted(t_entrada_fab)
    precio_fab = g_sesion['high'].iloc[idx_fab]
    nube(ax1, idx_fab, precio_fab, 'SELL', True, y_rango)
    ax1.axvline(idx_fab, color='white', linestyle=':', linewidth=0.6, alpha=0.4)
    t_salida_fab = NY.localize(pd.Timestamp(2026, 2, 12, 9, 16)).astimezone(UTC)
    idx_salida_fab = g_sesion['time'].searchsorted(t_salida_fab)
    ax1.axvline(idx_salida_fab, color='#ffeb3b', linestyle=':', linewidth=1.2, alpha=0.7)
    ax1.tick_params(colors='#787b86')
    for s in ax1.spines.values(): s.set_color('#2a2e39')
    ax1.set_title('FABIAN (real) -- 12/02/2026: SELL 09:03 -> salida 09:16 (línea amarilla) -- MEC→START -- TP +1.0R',
                   color='white', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Precio (USD)', color='white')
    plt.tight_layout()
    plt.savefig('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/dia1_fabian_real.png', facecolor='#131722', bbox_inches='tight')

    # --- Imagen 2: Codigo mecanico (09:19 entrada, SELL) ---
    fig2, ax2 = plt.subplots(figsize=(15, 8), dpi=130, facecolor='#131722')
    ax2.set_facecolor('#131722')
    dibujar_velas(ax2, g_sesion)
    marcar_m3(ax2, m3, x_map)
    t_entrada_cod = NY.localize(pd.Timestamp(2026, 2, 12, 9, 19)).astimezone(UTC)
    idx_cod = g_sesion['time'].searchsorted(t_entrada_cod)
    precio_cod = g_sesion['high'].iloc[idx_cod]
    nube(ax2, idx_cod, precio_cod, 'SELL', True, y_rango)
    ax2.axvline(idx_cod, color='white', linestyle=':', linewidth=0.6, alpha=0.4)
    ax2.tick_params(colors='#787b86')
    for s in ax2.spines.values(): s.set_color('#2a2e39')
    ax2.set_title('CÓDIGO MECÁNICO -- 12/02/2026: SELL 09:19 (16 min después de que Fabian ya había cerrado) -- MEC-A/MER -- TP +0.9R',
                   color='white', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Precio (USD)', color='white')
    plt.tight_layout()
    plt.savefig('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/dia1_codigo_mecanico.png', facecolor='#131722', bbox_inches='tight')

    print("Guardadas las 2 imagenes.")
