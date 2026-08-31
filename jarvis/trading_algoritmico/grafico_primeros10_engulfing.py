"""
Grilla con las primeras 10 apariciones de engulfing alcista, cada una con
contexto (20 velas antes, 16 despues), para inspeccion visual real -- a
pedido de Diego (26/08/2026).
"""
import pandas as pd
import numpy as np
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
OUTPUT_PNG = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/primeros10_engulfing_alcista.png'
CONTEXTO_ANTES = 15
CONTEXTO_DESPUES = 15


def load():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    return df


def dibujar_velas(ax, g, idx_patron_pos):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = '#26a69a' if c >= o else '#ef5350'
        ax.plot([i, i], [l, h], color=color, linewidth=0.8, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else 0.01
        base = min(o, c)
        rect = patches.Rectangle((i - 0.3, base), 0.6, alto, facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)
    # resaltar las 2 velas del patron (la anterior + la actual)
    for j in [idx_patron_pos - 1, idx_patron_pos]:
        ax.axvspan(j - 0.45, j + 0.45, color='gold', alpha=0.25, zorder=1)


if __name__ == '__main__':
    df = load()
    with open('ocurrencias_patrones.pkl', 'rb') as f:
        oc = pickle.load(f)
    primeros10 = oc['engulfing_alcista'][:10]

    fig, axes = plt.subplots(2, 5, figsize=(22, 9), dpi=120)
    axes = axes.flatten()

    for k, ev in enumerate(primeros10):
        t, ret, dia = ev['t'], ev['ret'], ev['dia']
        g_dia = df[df.index.date == dia]
        pos = g_dia.index.get_loc(t)
        ini = max(0, pos - CONTEXTO_ANTES)
        fin = min(len(g_dia), pos + CONTEXTO_DESPUES + 1)
        ventana = g_dia.iloc[ini:fin]
        pos_relativa = pos - ini

        ax = axes[k]
        dibujar_velas(ax, ventana, pos_relativa)
        color_resultado = '#2ca02c' if ret > 0 else '#d62728'
        ax.set_title(f"#{k+1} · {t.strftime('%H:%M')} · resultado +15min: {ret:+.3f}%",
                     fontsize=9, color=color_resultado, fontweight='bold')
        ax.set_xticks([])
        ax.tick_params(axis='y', labelsize=7)
        ax.axvline(pos_relativa, color='gray', linestyle=':', linewidth=0.6, alpha=0.5)

    fig.suptitle('Primeras 10 apariciones de "Engulfing Alcista" -- XAU/USD M1, 12/02/2026\n'
                  'Velas doradas = las 2 velas del patrón (bajista + envolvente alcista) · línea punteada = punto de entrada',
                  fontsize=12)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, bbox_inches='tight')
    print(f"Guardado en {OUTPUT_PNG}")
