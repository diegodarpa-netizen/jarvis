"""
Grafico de velas (estilo TradingView) mostrando las operaciones de VWAP
reversion en detalle -- entradas, duracion, salidas -- a pedido de Diego
(26/08/2026). Usa mplfinance sobre un dia real de oro M1.

Nota importante que se ve reflejada en el grafico: la regla actual NO
tiene stop-loss -- solo objetivo (tocar VWAP) o cierre forzado al final
de sesion. Se etiqueta la salida real (TP o cierre_sesion), no un SL
que no existe en la regla.
"""
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
DIA = '2026-05-15'
OUTPUT_PNG = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/velas_vwap_trades_15may.png'
N_DESVIOS = 2


def load_dia(dia):
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
    df = df.sort_index()
    g = df.loc[dia]
    g = g.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'})
    g['volumen'] = g['n_ticks'].clip(lower=1)
    return g


def calcular_vwap_bandas(g, n_desvios=N_DESVIOS):
    precio = g['Close']
    vol = g['volumen']
    pv = (precio * vol).cumsum()
    vv = vol.cumsum()
    vwap = pv / vv
    dist = precio - vwap
    de = dist.expanding(min_periods=10).std()
    banda_sup = vwap + n_desvios * de
    banda_inf = vwap - n_desvios * de
    return vwap, banda_sup, banda_inf, dist, de


def backtest_dia(g, vwap, dist, de, n_desvios=N_DESVIOS):
    precio = g['Close']
    resultados = []
    en_posicion = False
    direccion = None
    precio_entrada = None
    t_entrada = None

    for i in range(len(g)):
        precio_i = precio.iloc[i]
        vwap_i = vwap.iloc[i]
        de_i = de.iloc[i]
        if pd.isna(de_i) or de_i == 0:
            continue
        if en_posicion:
            tocado = (direccion == 1 and precio_i >= vwap_i) or (direccion == -1 and precio_i <= vwap_i)
            es_ultima = (i == len(g) - 1)
            if tocado or es_ultima:
                ret_pct = (precio_i - precio_entrada) / precio_entrada * 100 * direccion
                resultados.append({
                    't_entrada': t_entrada, 't_salida': g.index[i],
                    'precio_entrada': precio_entrada, 'precio_salida': precio_i,
                    'direccion': 'LARGO' if direccion == 1 else 'CORTO',
                    'resultado_%': ret_pct,
                    'motivo_salida': 'TP (toco VWAP)' if tocado else 'cierre forzado sesion',
                    'duracion_min': int((g.index[i] - t_entrada).total_seconds() / 60),
                })
                en_posicion = False
            continue
        z = dist.iloc[i] / de_i
        if z >= n_desvios:
            en_posicion, direccion, precio_entrada, t_entrada = True, -1, precio_i, g.index[i]
        elif z <= -n_desvios:
            en_posicion, direccion, precio_entrada, t_entrada = True, 1, precio_i, g.index[i]
    return pd.DataFrame(resultados)


if __name__ == '__main__':
    g = load_dia(DIA)
    vwap, banda_sup, banda_inf, dist, de = calcular_vwap_bandas(g)
    trades = backtest_dia(g, vwap, dist, de)

    print(f"Operaciones el {DIA}: {len(trades)}")
    print(trades[['t_entrada', 't_salida', 'direccion', 'duracion_min', 'motivo_salida', 'resultado_%']].to_string(index=False))

    addplots = [
        mpf.make_addplot(vwap, color='#1f77b4', width=1.4, label='VWAP'),
        mpf.make_addplot(banda_sup, color='#888888', width=0.8, linestyle='--'),
        mpf.make_addplot(banda_inf, color='#888888', width=0.8, linestyle='--'),
    ]

    fig, axes = mpf.plot(
        g[['Open', 'High', 'Low', 'Close']],
        type='candle', style='yahoo', addplot=addplots,
        title=f'\nVWAP Reversion en accion -- XAU/USD, {DIA} (M1)',
        ylabel='Precio (USD)', returnfig=True, figsize=(16, 9), volume=False,
    )
    ax = axes[0]

    # mplfinance usa posiciones ENTERAS en el eje X (no datetime real) --
    # hay que mapear cada timestamp a su posicion dentro de g.index
    posiciones = {ts: i for i, ts in enumerate(g.index)}

    for _, t in trades.iterrows():
        color = '#2ca02c' if t['resultado_%'] > 0 else '#d62728'
        marker_entrada = '^' if t['direccion'] == 'LARGO' else 'v'
        x_entrada = posiciones[t['t_entrada']]
        x_salida = posiciones[t['t_salida']]
        ax.scatter([x_entrada], [t['precio_entrada']], marker=marker_entrada, color=color,
                   s=140, zorder=6, edgecolors='black', linewidths=1)
        ax.scatter([x_salida], [t['precio_salida']], marker='X', color=color, s=110, zorder=6,
                   edgecolors='black', linewidths=0.8)
        ax.plot([x_entrada, x_salida], [t['precio_entrada'], t['precio_salida']],
                color=color, linestyle=':', linewidth=1.3, zorder=5)
        mid_x = (x_entrada + x_salida) / 2
        mid_p = max(t['precio_entrada'], t['precio_salida']) + 0.6
        ax.annotate(f"{t['direccion']} · {t['duracion_min']}min\n{t['motivo_salida']}\n{t['resultado_%']:+.3f}%",
                    xy=(mid_x, mid_p), fontsize=6.5, ha='center', color=color,
                    bbox=dict(boxstyle='round,pad=0.2', fc='white', ec=color, alpha=0.85))

    ax.text(0.01, 0.02, 'Nota: esta regla NO tiene stop-loss -- solo TP (tocar VWAP) o cierre forzado a fin de sesión.\n'
                          '▲/▼ = entrada (largo/corto) · X = salida · línea punteada gris = bandas ±2 desvíos estándar',
            transform=ax.transAxes, fontsize=8, va='bottom', style='italic',
            bbox=dict(boxstyle='round', fc='#fffbe6', ec='#d4af37', alpha=0.9))

    plt.tight_layout()
    fig.savefig(OUTPUT_PNG, bbox_inches='tight', dpi=130)
    print(f"\nGrafico guardado en {OUTPUT_PNG}")
