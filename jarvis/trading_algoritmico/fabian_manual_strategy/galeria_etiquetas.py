"""
Galeria de 3 estilos de etiqueta (BUY/SELL) para elegir antes de pasar al
.pine -- a pedido de Diego (28/08/2026): "jugar con colores y formas, que
se vea super estetico, lindo, elegante". Usa un recorte real de velas
(dia 1, 12/02/2026) como fondo para los 6 paneles.
"""
import pandas as pd
import numpy as np
import pytz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, RegularPolygon, Polygon, Circle
import sys
sys.path.append('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy')
from prueba_ventana_horaria import cargar, ventana_ny

NY = pytz.timezone('America/New_York')
UTC = pytz.UTC
VERDE, ROJO = '#26a69a', '#ef5350'
FONDO = '#131722'
GRID = '#1e222d'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/galeria_etiquetas.png'

# paletas mas suaves/elegantes para explorar (ademas del rojo/verde base)
CORAL = '#ff5d73'
MENTA = '#2dd4a7'
AMBAR = '#f0a020'
AZUL_SUAVE = '#5b8def'


def dibujar_velas(ax, g):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = VERDE if c >= o else ROJO
        ax.plot([i, i], [l, h], color=color, linewidth=1.4, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else 0.015
        base = min(o, c)
        rect = patches.Rectangle((i - 0.32, base), 0.64, alto, facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)


def estilo_capsula(ax, x, y_entrada, direccion, color, y_rango):
    """Estilo A: capsula solida vertical, texto rotado, sombra sutil."""
    label_w, label_h = 0.62, y_rango * 0.10
    if direccion == 'SELL':
        label_y = y_entrada - y_rango * 0.02 - label_h
    else:
        label_y = y_entrada + y_rango * 0.02
    sombra = FancyBboxPatch((x - label_w / 2 + 0.04, label_y - 0.015 * y_rango), label_w, label_h,
                             boxstyle="round,pad=0.06,rounding_size=0.5",
                             facecolor='black', alpha=0.25, edgecolor='none', zorder=5)
    ax.add_patch(sombra)
    box = FancyBboxPatch((x - label_w / 2, label_y), label_w, label_h,
                          boxstyle="round,pad=0.06,rounding_size=0.5",
                          facecolor=color, edgecolor='white', linewidth=0.4, zorder=6)
    ax.add_patch(box)
    ax.text(x, label_y + label_h / 2, direccion[0], color='white', fontsize=9,
            fontweight='bold', ha='center', va='center', zorder=7)
    ax.plot([x, x], [y_entrada, label_y + (label_h if direccion == 'SELL' else 0)],
            color=color, linewidth=0.9, alpha=0.55, zorder=4)


def estilo_diamante(ax, x, y_entrada, direccion, color, y_rango):
    """Estilo B: diamante (rombo) con contorno, chico y preciso."""
    signo = -1 if direccion == 'SELL' else 1
    yc = y_entrada + signo * y_rango * 0.05
    sx, sy = 0.22, y_rango * 0.024
    pts = [(x, yc + sy), (x + sx, yc), (x, yc - sy), (x - sx, yc)]
    diamante = Polygon(pts, closed=True, facecolor=color, edgecolor='white', linewidth=1.0, alpha=0.95, zorder=6)
    ax.add_patch(diamante)
    txt_y = yc + signo * y_rango * 0.045
    ax.text(x, txt_y, direccion, color=color, fontsize=7.5, fontweight='bold',
            ha='center', va='center', zorder=7)
    ax.plot([x, x], [y_entrada, yc - signo * sy], color=color, linewidth=0.9, alpha=0.5, zorder=4)


def estilo_bandera(ax, x, y_entrada, direccion, color, y_rango):
    """Estilo C: banderin/flag apuntando a la vela, forma de pendon."""
    w, h = 0.55, y_rango * 0.085
    if direccion == 'SELL':
        base_y = y_entrada - y_rango * 0.015
        pts = [(x, base_y), (x - w / 2, base_y - h), (x - w / 2, base_y - h * 1.55),
               (x + w / 2, base_y - h * 1.55), (x + w / 2, base_y - h)]
        txt_y = base_y - h * 1.27
    else:
        base_y = y_entrada + y_rango * 0.015
        pts = [(x, base_y), (x - w / 2, base_y + h), (x - w / 2, base_y + h * 1.55),
               (x + w / 2, base_y + h * 1.55), (x + w / 2, base_y + h)]
        txt_y = base_y + h * 1.27
    flag = Polygon(pts, closed=True, facecolor=color, edgecolor='white', linewidth=0.5, alpha=0.95, zorder=6)
    ax.add_patch(flag)
    ax.text(x, txt_y, direccion, color='white', fontsize=6.5, fontweight='bold',
            ha='center', va='center', zorder=7)


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

    estilos = [
        ('A -- Cápsula sólida', estilo_capsula, ROJO, VERDE),
        ('B -- Diamante contorno', estilo_diamante, CORAL, MENTA),
        ('C -- Banderín', estilo_bandera, ROJO, VERDE),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(17, 10), dpi=140, facecolor=FONDO)

    for col, (nombre, fn, color_sell, color_buy) in enumerate(estilos):
        for row, (direccion, color) in enumerate([('SELL', color_sell), ('BUY', color_buy)]):
            ax = axes[row, col]
            ax.set_facecolor(FONDO)
            ax.grid(True, color=GRID, linewidth=0.5, zorder=0)
            ax.set_axisbelow(True)
            dibujar_velas(ax, g_vis)
            y_entrada = g_vis['close'].iloc[x_entrada]
            ax.axvline(x_entrada, color='#e0e0e0', linestyle=':', linewidth=0.6, alpha=0.35)
            fn(ax, x_entrada, y_entrada, direccion, color, y_rango)
            ax.set_xlim(-0.6, len(g_vis) - 0.4)
            ax.set_ylim(y_min, y_max)
            ax.set_xticks([])
            ax.tick_params(colors='#787b86', labelsize=7)
            for spine in ax.spines.values():
                spine.set_color('#2a2e39')
            if row == 0:
                ax.set_title(nombre, color='#d1d4dc', fontsize=12, fontweight='bold', pad=10)
            if col == 0:
                ax.set_ylabel(direccion, color='#d1d4dc', fontsize=11, fontweight='bold')

    fig.suptitle('Galería de etiquetas -- 3 estilos x SELL/BUY', color='white', fontsize=14, fontweight='bold', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(OUT, facecolor=FONDO, bbox_inches='tight')
    print(f"Guardado: {OUT}")
