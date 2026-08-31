"""
Dia 1 (12/02/2026) con el motor UNIFICADO (M3 continuo sin reset + START
fusionado + doji excluido como señal standalone): el codigo ahora dispara
SELL exactamente a las 09:03, igual que Fabian. Una sola imagen (ya no dos)
porque coinciden. A pedido de Diego (28/08/2026): "resolvamos el dia 1".
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
from prueba_ventana_horaria import cargar, ventana_ny, backtest_dia

NY = pytz.timezone('America/New_York')
UTC = pytz.UTC
VERDE, ROJO = '#26a69a', '#ef5350'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/dia1_motor_unificado_confirmado.png'


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
    df = cargar()
    df['day'] = df.index.date
    dia = pd.Timestamp('2026-02-12').date()
    g = df[df['day'] == dia]
    ini, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
    g_amplia = g[g.index <= fin]
    trades = backtest_dia(g_amplia, t_inicio_entradas=ini)

    # recorte visual: 08:45 en adelante, para ver el contexto M3 previo a 09:01
    ini_visual, _ = ventana_ny(pd.Timestamp(dia), 8, 45, 10, 59)
    g_vis = g_amplia[g_amplia.index >= ini_visual].reset_index()
    g_vis.columns = ['time', 'open', 'high', 'low', 'close', 'n_ticks', 'day']
    x_map = {t: i for i, t in enumerate(g_vis['time'])}
    m3 = g_amplia.loc[ini_visual:].resample('3min').agg(open=('open', 'first'), high=('high', 'max'),
                                                          low=('low', 'min'), close=('close', 'last')).dropna()

    y_min, y_max = g_vis['low'].min(), g_vis['high'].max()
    y_rango = y_max - y_min

    fig, ax = plt.subplots(figsize=(16, 8), dpi=130, facecolor='#131722')
    ax.set_facecolor('#131722')
    dibujar_velas(ax, g_vis)
    marcar_m3(ax, m3, x_map)

    t_entrada = trades[0]['t_entrada']
    idx_e = g_vis['time'].searchsorted(t_entrada)
    precio_e = g_vis['high'].iloc[idx_e]
    nube(ax, idx_e, precio_e, 'SELL', True, y_rango)
    ax.axvline(idx_e, color='white', linestyle=':', linewidth=0.6, alpha=0.4)
    ax.axvline(x_map.get(pd.Timestamp('2026-02-12 14:01:00', tz='UTC'), 0), color='#42a5f5', linestyle='-', linewidth=1.2, alpha=0.5)

    ax.tick_params(colors='#787b86')
    for s in ax.spines.values():
        s.set_color('#2a2e39')
    r = trades[0]['R']
    t_ny = t_entrada.tz_convert(NY)
    ax.set_title(f"MOTOR UNIFICADO -- 12/02/2026: SELL {t_ny.strftime('%H:%M')} -- MEC/START -- R={r:+.2f}  ✓ COINCIDE EXACTO CON FABIAN (SELL 09:03)\n"
                 "Linea azul = apertura ventana operable 09:01 NY -- M3 se arma sin resetear (continuo desde antes de las 09:01)",
                 color='white', fontsize=11.5, fontweight='bold')
    ax.set_ylabel('Precio (USD)', color='white')
    plt.tight_layout()
    plt.savefig(OUT, facecolor='#131722', bbox_inches='tight')
    print(f"Guardado: {OUT}")
    print(f"Trade: {t_ny.strftime('%H:%M')} R={r:+.2f}")
