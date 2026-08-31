"""
Cruza 6 operaciones reales de Fabian (dentro de la ventana de 6 meses que
tenemos en M1) contra las velas reales de precio, para verificar
visualmente. A pedido de Diego (27/08/2026).

IMPORTANTE -- limitacion honesta: el CSV de Fabian no trae el precio
exacto de entrada/salida, solo hora y resultado en R. Los marcadores de
precio en el grafico usan el CIERRE de nuestra vela M1 en esa hora como
aproximacion, NO es necesariamente su precio de fill real (puede diferir
por el spread/slippage del momento exacto de ejecucion).
"""
import pandas as pd
import numpy as np
import pytz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

INPUT_OHLC = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
INPUT_FABIAN = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
OUTPUT_PNG = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/fabian_cruce_ohlc_real.png'
NY = pytz.timezone('America/New_York')
UTC = pytz.UTC
CONTEXTO_ANTES = 20
CONTEXTO_DESPUES = 20


def cargar():
    ohlc = pd.read_csv(INPUT_OHLC, index_col=0)
    ohlc.index = pd.to_datetime(ohlc.index, utc=True)
    fab = pd.read_csv(INPUT_FABIAN)
    fab['Fecha_dt'] = pd.to_datetime(fab['Fecha_dt'])
    return ohlc, fab


def hora_ny_a_utc(fecha, hora_str):
    h, m = map(int, hora_str.split(':'))
    dt_ny = NY.localize(pd.Timestamp(fecha.year, fecha.month, fecha.day, h, m))
    return dt_ny.astimezone(UTC)


def dibujar_velas(ax, g, pos_entrada, pos_salida):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = '#26a69a' if c >= o else '#ef5350'
        ax.plot([i, i], [l, h], color=color, linewidth=0.8, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else 0.01
        base = min(o, c)
        rect = patches.Rectangle((i - 0.3, base), 0.6, alto, facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)
    if pos_entrada is not None:
        ax.axvline(pos_entrada, color='#1f77b4', linestyle='--', linewidth=1.2, alpha=0.8)
    if pos_salida is not None:
        ax.axvline(pos_salida, color='#9467bd', linestyle='--', linewidth=1.2, alpha=0.8)


if __name__ == '__main__':
    ohlc, fab = cargar()

    ini_ventana, fin_ventana = ohlc.index.min().tz_convert(None), ohlc.index.max().tz_convert(None)
    overlap = fab[(fab['Fecha_dt'] >= ini_ventana) & (fab['Fecha_dt'] <= fin_ventana)].copy()

    # elegir 6 casos representativos: 3 ganadores, 3 perdedores, repartidos en el tiempo
    ganadores = overlap[overlap['Beneficio_R'] > 0].iloc[[0, len(overlap[overlap['Beneficio_R']>0])//2, -1]]
    perdedores = overlap[overlap['Beneficio_R'] < 0].iloc[[0, len(overlap[overlap['Beneficio_R']<0])//2, -1]]
    seleccion = pd.concat([ganadores, perdedores]).sort_values('Fecha_dt')

    fig, axes = plt.subplots(2, 3, figsize=(19, 10), dpi=120)
    axes = axes.flatten()

    for k, (_, t) in enumerate(seleccion.iterrows()):
        try:
            t_apertura_utc = hora_ny_a_utc(t['Fecha_dt'], t['Hora apertura (NY)'])
            t_cierre_utc = hora_ny_a_utc(t['Fecha_dt'], t['Hora cierre  (NY)'])
        except Exception as e:
            continue

        # buscar la barra M1 mas cercana
        idx_cercano_entrada = ohlc.index.get_indexer([t_apertura_utc], method='nearest')[0]
        idx_cercano_salida = ohlc.index.get_indexer([t_cierre_utc], method='nearest')[0]

        ini = max(0, idx_cercano_entrada - CONTEXTO_ANTES)
        fin = min(len(ohlc), idx_cercano_salida + CONTEXTO_DESPUES)
        ventana = ohlc.iloc[ini:fin]
        pos_entrada = idx_cercano_entrada - ini
        pos_salida = idx_cercano_salida - ini

        ax = axes[k]
        dibujar_velas(ax, ventana, pos_entrada, pos_salida)
        color = '#2ca02c' if t['Beneficio_R'] > 0 else '#d62728'
        ax.set_title(f"{t['Fecha_dt'].strftime('%d/%m/%Y')} · {t['modelo_limpio']} · {t['Buy / Sell']}\n"
                     f"{t['Resultado']} · {t['Beneficio_R']:+.2f}R",
                     fontsize=9.5, color=color, fontweight='bold')
        ax.set_xticks([])
        ax.tick_params(axis='y', labelsize=7)

    fig.suptitle('6 operaciones reales de Fabian cruzadas contra velas M1 reales (XAU/USD)\n'
                  'Línea azul = hora de apertura registrada · línea violeta = hora de cierre registrada\n'
                  '(el precio de fill exacto no está en el CSV de Fabian -- estas velas son las reales del mercado en esos horarios)',
                  fontsize=11)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, bbox_inches='tight')
    print(f"Guardado en {OUTPUT_PNG}")
    print(f"\n{len(overlap)} operaciones de Fabian caen dentro de nuestra ventana de 6 meses de datos M1.")
