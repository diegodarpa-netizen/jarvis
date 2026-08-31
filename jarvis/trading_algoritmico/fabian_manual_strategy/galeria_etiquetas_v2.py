"""
Galeria v2 (28/08/2026) -- los primeros 3 estilos (capsula/diamante/
banderin) no gustaron ("es la forma"). Prueba con formas mas simples:
D) punto/circulo chico, E) solo texto sin fondo, F) flecha minimalista.
"""
import pandas as pd
import pytz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle
import sys
sys.path.append('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy')
from prueba_ventana_horaria import cargar, ventana_ny

NY = pytz.timezone('America/New_York')
UTC = pytz.UTC
VERDE, ROJO = '#26a69a', '#ef5350'
FONDO = '#131722'
GRID = '#1e222d'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/galeria_etiquetas_v2.png'


def dibujar_velas(ax, g):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = VERDE if c >= o else ROJO
        ax.plot([i, i], [l, h], color=color, linewidth=1.4, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else 0.015
        base = min(o, c)
        rect = patches.Rectangle((i - 0.32, base), 0.64, alto, facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)


def estilo_punto(ax, x, y_entrada, direccion, color, y_rango):
    """Estilo D: circulo chico solido sobre la linea de entrada + texto
    diminuto al lado, sin caja."""
    r = y_rango * 0.014
    circ = Circle((x, y_entrada), r, facecolor=color, edgecolor='white', linewidth=0.8, zorder=6)
    ax.add_patch(circ)
    ax.text(x + 0.5, y_entrada, direccion, color=color, fontsize=7.5, fontweight='bold',
            ha='left', va='center', zorder=7)


def estilo_texto(ax, x, y_entrada, direccion, color, y_rango):
    """Estilo E: solo texto en negrita, sin fondo ni forma, chico y
    discreto, apenas separado de la vela."""
    signo = -1 if direccion == 'SELL' else 1
    y_txt = y_entrada + signo * y_rango * 0.035
    ax.text(x, y_txt, direccion, color=color, fontsize=8.5, fontweight='bold',
            ha='center', va='center', zorder=7,
            path_effects=[])


def estilo_flecha(ax, x, y_entrada, direccion, color, y_rango):
    """Estilo F: flecha minimalista (linea + punta) mas grande y prolija
    que el triangulo viejo, con texto chico al lado."""
    signo = -1 if direccion == 'SELL' else 1
    largo = y_rango * 0.05
    y0 = y_entrada + signo * (largo + y_rango * 0.012)
    y1 = y_entrada + signo * y_rango * 0.012
    ax.annotate('', xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle='-|>', color=color, lw=2.0, mutation_scale=14), zorder=6)
    ax.text(x + 0.55, (y0 + y1) / 2, direccion, color=color, fontsize=7.5, fontweight='bold',
            ha='left', va='center', zorder=7)


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
        ('D -- Punto + texto', estilo_punto),
        ('E -- Solo texto', estilo_texto),
        ('F -- Flecha', estilo_flecha),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(17, 10), dpi=140, facecolor=FONDO)

    for col, (nombre, fn) in enumerate(estilos):
        for row, direccion in enumerate(['SELL', 'BUY']):
            color = ROJO if direccion == 'SELL' else VERDE
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

    fig.suptitle('Galería v2 -- formas más simples', color='white', fontsize=14, fontweight='bold', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(OUT, facecolor=FONDO, bbox_inches='tight')
    print(f"Guardado: {OUT}")
