"""
Vuelta a la base, a pedido de Diego (25/08/2026): antes de seguir probando
estrategias sueltas, analizar la data de 6 meses M1 de oro con reglas
basicas de EMA y mostrar el resultado en un GRAFICO, no solo en tablas.
Objetivo puntual: ver si en estos 6 meses aparece el patron de "surfear
la EMA9" que Diego señalo en sus graficos de TradingView.

Reutiliza la logica ya validada de surf_ema9.py (regla pulida: confirmar
racha >=3 dias, salir con 50% de retroceso de la distancia) sobre velas
DIARIAS (resample del M1 que tenemos completo).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
OUTPUT_PNG = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/surf_ema9_6meses.png'


def load_daily():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    daily = df.groupby('day').agg(open=('open', 'first'), high=('high', 'max'),
                                   low=('low', 'min'), close=('close', 'last')).reset_index()
    daily['day'] = pd.to_datetime(daily['day'])
    daily = daily.set_index('day')
    return daily


def calcular_emas(daily):
    for span in [9, 20, 50]:
        daily[f'ema{span}'] = daily['close'].ewm(span=span, adjust=False).mean()
    daily['dist_ema9_pct'] = (daily['close'] - daily['ema9']) / daily['ema9'] * 100
    return daily


def identificar_episodios(daily, dias_confirmacion=3, retroceso_pct=50):
    """Misma logica de surf_ema9.py: racha = tramo continuo del mismo signo
    de distancia a la EMA9. Se opera solo si la racha confirma >=3 dias.
    Salida: 50% de retroceso desde el pico de distancia, o fin de racha."""
    sign = np.sign(daily['dist_ema9_pct'])
    change = sign.diff().fillna(1) != 0
    group_id = change.cumsum()

    episodios = []
    for gid, idx in daily.groupby(group_id).groups.items():
        s = sign.loc[idx].iloc[0]
        if len(idx) < dias_confirmacion:
            continue
        entrada_idx = idx[dias_confirmacion - 1]
        precio_entrada = daily['close'].loc[entrada_idx]
        dist_racha = daily['dist_ema9_pct'].loc[idx].abs()
        pico = dist_racha.cummax()
        retroceso = (pico - dist_racha) / pico.replace(0, np.nan) * 100
        candidatas = retroceso[(retroceso >= retroceso_pct) & (retroceso.index >= entrada_idx)]
        salida_idx = candidatas.index[0] if len(candidatas) > 0 else idx[-1]
        precio_salida = daily['close'].loc[salida_idx]
        resultado_pct = (precio_salida - precio_entrada) / precio_entrada * 100 * s
        episodios.append({
            'inicio_racha': idx[0], 'entrada': entrada_idx, 'salida': salida_idx,
            'direccion': 'ALZA' if s > 0 else 'BAJA',
            'precio_entrada': precio_entrada, 'precio_salida': precio_salida,
            'resultado_%': resultado_pct, 'dias_racha_total': len(idx),
        })
    return pd.DataFrame(episodios)


def graficar(daily, episodios, out_path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9), sharex=True,
                                    gridspec_kw={'height_ratios': [3, 1]}, dpi=130)

    ax1.plot(daily.index, daily['close'], color='#333333', linewidth=1.1, label='Cierre diario XAU/USD')
    ax1.plot(daily.index, daily['ema9'], color='#1f77b4', linewidth=1.3, label='EMA9')
    ax1.plot(daily.index, daily['ema20'], color='#ff7f0e', linewidth=0.9, alpha=0.6, label='EMA20')
    ax1.plot(daily.index, daily['ema50'], color='#9467bd', linewidth=0.9, alpha=0.5, label='EMA50')

    for _, ep in episodios.iterrows():
        color = '#2ca02c' if ep['resultado_%'] > 0 else '#d62728'
        ax1.axvspan(ep['entrada'], ep['salida'], color=color, alpha=0.15)
        ax1.scatter([ep['entrada']], [ep['precio_entrada']], marker='^' if ep['direccion'] == 'ALZA' else 'v',
                    color=color, s=70, zorder=5, edgecolors='black', linewidths=0.5)
        ax1.scatter([ep['salida']], [ep['precio_salida']], marker='x', color=color, s=60, zorder=5)

    ax1.set_title('Surf EMA9 -- XAU/USD diario, 6 meses (12/02/2026 - 13/08/2026)\n'
                   'Sombreado verde = episodio ganador | rojo = perdedor | ^v = entrada confirmada (dia 3 de racha) | x = salida (50% retroceso)',
                   fontsize=11)
    ax1.set_ylabel('Precio (USD)')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(alpha=0.25)

    ax2.plot(daily.index, daily['dist_ema9_pct'], color='#1f77b4', linewidth=1)
    ax2.axhline(0, color='black', linewidth=0.7)
    ax2.fill_between(daily.index, daily['dist_ema9_pct'], 0,
                      where=(daily['dist_ema9_pct'] >= 0), color='#2ca02c', alpha=0.15)
    ax2.fill_between(daily.index, daily['dist_ema9_pct'], 0,
                      where=(daily['dist_ema9_pct'] < 0), color='#d62728', alpha=0.15)
    ax2.set_ylabel('Distancia a EMA9 (%)')
    ax2.set_xlabel('Fecha')
    ax2.grid(alpha=0.25)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))

    plt.tight_layout()
    import os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, bbox_inches='tight')
    print(f"Grafico guardado en {out_path}")


if __name__ == '__main__':
    daily = load_daily()
    daily = calcular_emas(daily)
    episodios = identificar_episodios(daily)

    print("=" * 90)
    print(f"SURF EMA9 -- {len(daily)} dias, {len(episodios)} episodios operados (de {daily['dist_ema9_pct'].pipe(lambda s: (np.sign(s).diff().fillna(1) != 0).cumsum().nunique())} rachas totales)")
    print("=" * 90)
    ganadores = episodios[episodios['resultado_%'] > 0]
    perdedores = episodios[episodios['resultado_%'] <= 0]
    print(f"Ganadores: {len(ganadores)} | Perdedores: {len(perdedores)} | Win rate: {len(ganadores)/len(episodios)*100:.1f}%")
    print(f"Resultado promedio por episodio: {episodios['resultado_%'].mean():.3f}%")
    print(f"Suma de resultados (sin compounding): {episodios['resultado_%'].sum():.2f}%")
    print("\nDetalle:")
    print(episodios[['inicio_racha', 'entrada', 'salida', 'direccion', 'resultado_%', 'dias_racha_total']].to_string(index=False))

    graficar(daily, episodios, OUTPUT_PNG)
