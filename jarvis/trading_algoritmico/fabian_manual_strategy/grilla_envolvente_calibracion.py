"""
Grilla comparando casos reales de "Envolvente" declarados por Fabian --
mitad que la formula del PDF reconoce, mitad que no -- con velas
rojas/verdes estandar (no blanco/negro), zoom en la vela de entrada y
las 2-3 anteriores, y el % de cuerpo / mecha anotado para poder calibrar
juntos. A pedido de Diego (27/08/2026).
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
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/grilla_envolvente_calibracion.png'
NY = pytz.timezone('America/New_York')
UTC = pytz.UTC

VERDE = '#26a69a'
ROJO = '#ef5350'


def dibujar_velas(ax, g, idx_resaltar):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = VERDE if c >= o else ROJO
        ax.plot([i, i], [l, h], color=color, linewidth=1.2, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else 0.01
        base = min(o, c)
        rect = patches.Rectangle((i - 0.3, base), 0.6, alto, facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)
    ax.axvspan(idx_resaltar - 0.45, idx_resaltar + 0.45, color='gold', alpha=0.15, zorder=1)


if __name__ == '__main__':
    ohlc = pd.read_csv(INPUT_OHLC, index_col=0)
    ohlc.index = pd.to_datetime(ohlc.index, utc=True)
    ohlc = ohlc.sort_index()
    val = pd.read_csv(INPUT_VAL)
    val['fecha_dt'] = pd.to_datetime(val['fecha'], format='%d/%m/%Y')

    env = val[val['patron_declarado'] == 'Envolvente']
    coinciden = env[env['coincide_con_codigo'] == True].head(3)
    no_coinciden = env[env['coincide_con_codigo'] == False].head(3)
    seleccion = pd.concat([coinciden, no_coinciden])

    fig, axes = plt.subplots(2, 3, figsize=(20, 11), dpi=120)
    axes = axes.flatten()

    for k, (_, ev) in enumerate(seleccion.iterrows()):
        h, m = map(int, ev['hora'].split(':'))
        fecha = ev['fecha_dt']
        t_ny = NY.localize(pd.Timestamp(fecha.year, fecha.month, fecha.day, h, m))
        t_utc = t_ny.astimezone(UTC)
        idx = ohlc.index.get_indexer([t_utc], method='nearest')[0]
        ini, fin = max(0, idx - 8), idx + 5
        ventana = ohlc.iloc[ini:fin]
        idx_rel = idx - ini

        ax = axes[k]
        dibujar_velas(ax, ventana, idx_rel)
        coincide = ev['coincide_con_codigo']
        color_titulo = '#2ca02c' if coincide else '#d62728'
        estado = 'SI coincide con la formula' if coincide else 'NO coincide -- ' + ev['motivo_codigo']
        ax.set_title(f"{ev['fecha']} {ev['hora']} · {ev['direccion']}\n{estado}", fontsize=9.5, color=color_titulo, fontweight='bold')
        ax.set_xticks([])
        ax.tick_params(axis='y', labelsize=7)

    fig.suptitle('Calibración Envolvente -- casos reales de Fabian: coinciden (verde) vs no coinciden (rojo) con la fórmula del PDF',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUT, bbox_inches='tight')
    print(f"Guardado en {OUT}")
