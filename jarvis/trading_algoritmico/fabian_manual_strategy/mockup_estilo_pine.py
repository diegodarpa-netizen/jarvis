"""
Mockup de la nueva estetica del Pine (28/08/2026, a pedido de Diego):
sin triangulos ni carteles -- solo LINEAS (entrada solida, SL/TP
punteadas) que se extienden desde la entrada hasta el cierre, estilo
limpio de TradingView. Simulado con datos reales del dia 1 (12/02/2026,
SELL 09:03, TP +0.9R) para poder iterar el diseño antes de tocar el .pine.
"""
import pandas as pd
import numpy as np
import pytz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
sys.path.append('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy')
from prueba_ventana_horaria import cargar, ventana_ny

NY = pytz.timezone('America/New_York')
UTC = pytz.UTC
VERDE, ROJO = '#26a69a', '#ef5350'
FONDO = '#131722'
GRID = '#1e222d'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/mockup_estilo_pine_dia1.png'


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
    dia = pd.Timestamp('2026-02-12').date()
    g = df[df['day'] == dia]
    _, fin = ventana_ny(pd.Timestamp(dia), 9, 1, 10, 59)
    g_amplia = g[g.index <= fin]

    ini_vis, fin_vis = ventana_ny(pd.Timestamp(dia), 8, 51, 9, 25)
    g_vis = g_amplia[(g_amplia.index >= ini_vis) & (g_amplia.index <= fin_vis)].reset_index()
    g_vis.columns = ['time', 'open', 'high', 'low', 'close', 'n_ticks', 'day']
    x_map = {t: i for i, t in enumerate(g_vis['time'])}

    m3 = g_amplia.loc[ini_vis:].resample('3min').agg(open=('open', 'first'), high=('high', 'max'),
                                                       low=('low', 'min'), close=('close', 'last')).dropna()

    t_entrada = NY.localize(pd.Timestamp('2026-02-12 09:03:00')).astimezone(UTC)
    t_salida = NY.localize(pd.Timestamp('2026-02-12 09:16:00')).astimezone(UTC)
    idx_entrada = g_vis['time'].searchsorted(t_entrada)
    idx_salida = g_vis['time'].searchsorted(t_salida)

    entrada, sl, tp = 5072.106, 5083.870, 5061.518
    alto_m3_level = 5083.870  # mismo nivel que uso como SL en este caso
    nivel_previo = 5077.62

    # tend_state vela por vela (recalculado con el motor calibrado) -- para
    # las franjas verticales de fondo (alcista/bajista), estilo ya aprobado
    # en apariencia_labels.md ("Fondo de sesion: tendencia ALCISTA/BAJISTA")
    tend_por_vela = ([1] * 8) + ([-1] * (len(g_vis) - 8))  # cambia a las 08:59

    y_min = min(g_vis['low'].min(), tp) - 1.5
    y_max = max(g_vis['high'].max(), sl) + 1.5

    fig, ax = plt.subplots(figsize=(15, 8.5), dpi=140, facecolor=FONDO)
    ax.set_facecolor(FONDO)

    # --- franjas verticales de fondo por tendencia ---
    tramo_ini = 0
    for i in range(1, len(tend_por_vela) + 1):
        if i == len(tend_por_vela) or tend_por_vela[i] != tend_por_vela[tramo_ini]:
            color_fondo = VERDE if tend_por_vela[tramo_ini] == 1 else ROJO
            ax.axvspan(tramo_ini - 0.5, i - 0.5, color=color_fondo, alpha=0.14, zorder=0)
            tramo_ini = i

    ax.grid(True, color=GRID, linewidth=0.6, zorder=1)
    ax.set_axisbelow(True)

    dibujar_velas(ax, g_vis)

    ax.plot([0, idx_entrada], [nivel_previo, nivel_previo], color='#787b86', linestyle=':', linewidth=1.0, alpha=0.5)
    ax.plot([0, len(g_vis) - 1], [alto_m3_level, alto_m3_level], color='#787b86', linestyle='--', linewidth=1.1, alpha=0.8)

    # --- lineas de la operacion: entrada solida, SL/TP punteadas, SIN texto
    # de precio -- extienden desde la entrada hasta el cierre ---
    ax.plot([idx_entrada, idx_salida], [entrada, entrada], color='#e0e0e0', linestyle='-', linewidth=1.4, zorder=4)
    ax.plot([idx_entrada, idx_salida], [sl, sl], color=ROJO, linestyle='--', linewidth=1.2, alpha=0.9, zorder=4)
    ax.plot([idx_entrada, idx_salida], [tp, tp], color=VERDE, linestyle='--', linewidth=1.2, alpha=0.9, zorder=4)

    # --- etiqueta de direccion en la entrada: vertical, angosta (no tapa la
    # vela de al lado), del mismo color que la operacion (rojo=SELL,
    # verde=BUY) -- sin precio ---
    from matplotlib.patches import FancyBboxPatch
    color_label = ROJO  # SELL en este ejemplo -- BUY usaria VERDE
    label_w, label_h = 0.85, (y_max - y_min) * 0.075
    label_y = entrada - (y_max - y_min) * 0.025 - label_h
    box = FancyBboxPatch((idx_entrada - label_w / 2, label_y), label_w, label_h,
                          boxstyle="round,pad=0.1,rounding_size=0.7",
                          facecolor=color_label, edgecolor='none', zorder=6)
    ax.add_patch(box)
    ax.text(idx_entrada, label_y + label_h / 2, 'SELL', color='white', fontsize=8,
            fontweight='bold', ha='center', va='center', rotation=90, zorder=7)
    ax.plot([idx_entrada, idx_entrada], [entrada, label_y + label_h], color=color_label, linewidth=1.0, alpha=0.6, zorder=5)
    ax.axvline(idx_entrada, color='#e0e0e0', linestyle=':', linewidth=0.6, alpha=0.4)
    ax.axvline(idx_salida, color='#e0e0e0', linestyle=':', linewidth=0.6, alpha=0.4)

    xt = list(range(0, len(g_vis), 3))
    ax.set_xticks(xt)
    ax.set_xticklabels([g_vis['time'].iloc[i].tz_convert(NY).strftime('%H:%M') for i in xt], color='#787b86', fontsize=8)
    ax.set_xlim(-1, len(g_vis) + 6)
    ax.set_ylim(y_min, y_max)

    ax.tick_params(colors='#787b86')
    for spine in ax.spines.values():
        spine.set_color('#2a2e39')
    ax.set_ylabel('XAUUSD (USD)', color='#d1d4dc')
    ax.set_title('EstrategiaXAU -- mockup de estetica nueva (solo líneas, sin triángulos ni carteles)\n12/02/2026 -- SELL 09:03 -- MEC/START -- TP +0.9R',
                  color='#d1d4dc', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUT, facecolor=FONDO, bbox_inches='tight')
    print(f"Guardado: {OUT}")
