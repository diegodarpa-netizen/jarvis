"""
Grilla COMPLETA de las 51 operaciones reales de Fabian con patron
"Envolvente", con la formula YA CORREGIDA (mecha chica <15% -> clasica,
sin la pared dura del 85% de cuerpo). Verde = vela alcista, rojo = vela
bajista (colores estandar), recuadro de color segun si la formula
corregida coincide o no con lo que declaro Fabian. A pedido de Diego
(27/08/2026).
"""
import pandas as pd
import numpy as np
import pytz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

INPUT_OHLC = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
INPUT_VAL = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/validacion_trade_por_trade.csv'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/grilla_completa_envolvente.png'
NY = pytz.timezone('America/New_York')
UTC = pytz.UTC
VERDE_VELA, ROJO_VELA = '#26a69a', '#ef5350'
ENV_DOJI_MIN, ENV_MARTILLO_MIN = 0.15, 0.50


def tipo_envolvente_v2(o, h, l, c, es_compra):
    total = h - l
    if total <= 0:
        return 0
    body = abs(c - o)
    bp = body / total
    if es_compra:
        if c <= o:
            return 0
        w_op = (h - max(o, c)) / total
        w_fav = (min(o, c) - l) / total
    else:
        if c >= o:
            return 0
        w_op = (min(o, c) - l) / total
        w_fav = (h - max(o, c)) / total
    if bp >= ENV_MARTILLO_MIN and w_op < ENV_DOJI_MIN:
        return 1
    elif ENV_MARTILLO_MIN <= bp < 0.85 and w_op >= ENV_DOJI_MIN:
        return 2
    elif ENV_DOJI_MIN <= w_op <= 0.85 and ENV_DOJI_MIN <= w_fav <= 0.85:
        return 3
    return 0


def dibujar_velas_mini(ax, g, idx_resaltar):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = VERDE_VELA if c >= o else ROJO_VELA
        ax.plot([i, i], [l, h], color=color, linewidth=0.9, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else (h - l) * 0.02
        base = min(o, c)
        rect = patches.Rectangle((i - 0.3, base), 0.6, alto, facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)
    ax.axvspan(idx_resaltar - 0.45, idx_resaltar + 0.45, color='gold', alpha=0.18, zorder=1)


if __name__ == '__main__':
    ohlc = pd.read_csv(INPUT_OHLC, index_col=0)
    ohlc.index = pd.to_datetime(ohlc.index, utc=True)
    ohlc = ohlc.sort_index()
    val = pd.read_csv(INPUT_VAL)
    env = val[val['patron_declarado'] == 'Envolvente'].reset_index(drop=True)

    n = len(env)
    cols, rows = 6, int(np.ceil(n / 6))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3.3, rows * 2.6), dpi=115)
    axes = axes.flatten()

    n_verde = 0
    for k, (_, ev) in enumerate(env.iterrows()):
        h, m = map(int, ev['hora'].split(':'))
        fecha = pd.to_datetime(ev['fecha'], format='%d/%m/%Y')
        t_ny = NY.localize(pd.Timestamp(fecha.year, fecha.month, fecha.day, h, m))
        t_utc = t_ny.astimezone(UTC)
        idx = ohlc.index.get_indexer([t_utc], method='nearest')[0]
        vela = ohlc.iloc[idx]
        es_compra = ev['direccion'] == 'Buy'
        tipo = tipo_envolvente_v2(vela['open'], vela['high'], vela['low'], vela['close'], es_compra)
        coincide = tipo > 0
        n_verde += coincide

        ini, fin = max(0, idx - 5), idx + 3
        ventana = ohlc.iloc[ini:fin]
        idx_rel = idx - ini

        ax = axes[k]
        dibujar_velas_mini(ax, ventana, idx_rel)
        borde = '#2ca02c' if coincide else '#d62728'
        for spine in ax.spines.values():
            spine.set_edgecolor(borde)
            spine.set_linewidth(2.2)
        ax.set_title(f"{ev['fecha']} {ev['hora']} {ev['direccion']}", fontsize=7.5,
                     color=borde, fontweight='bold')
        ax.set_xticks([])
        ax.set_yticks([])

    for k in range(n, len(axes)):
        axes[k].axis('off')

    fig.suptitle(f'Las 51 operaciones reales "Envolvente" de Fabian -- fórmula corregida: {n_verde}/{n} coinciden ({n_verde/n*100:.1f}%)\n'
                 'Borde verde = coincide · borde rojo = no coincide todavía · velas verde/rojo = alcista/bajista',
                 fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(OUT, bbox_inches='tight')
    print(f"Guardado en {OUT}")
    print(f"{n_verde} de {n} coinciden ({n_verde/n*100:.1f}%)")
