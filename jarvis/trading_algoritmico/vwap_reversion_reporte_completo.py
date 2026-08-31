"""
Reporte completo de VWAP mean reversion (banda 2 desvios estandar), a
pedido de Diego (26/08/2026): oro (M1, 6 meses, ya probado) + SPY
(preliminar, 5min/60 dias via Yahoo Finance -- CON VOLUMEN REAL, mientras
se completa la descarga intradia de Dukascopy para USA500).

Nota de honestidad: el test de SPY es preliminar por dos motivos --
(1) resolucion mas gruesa (5min, no M1, por limite de Yahoo Finance para
datos intradia gratis) y (2) ventana mucho mas corta (60 dias vs 6 meses
de oro). Pero SI tiene volumen real (a diferencia de oro, donde se uso
n_ticks como proxy) -- es un test mas fiel al concepto original de VWAP,
aunque con menos historia.
"""
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

N_DESVIOS = 2
N_BOOTSTRAP = 5000
SEED = 42
CAPITAL_INICIAL = 1000.0
INPUT_ORO = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
OUTPUT_PNG = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/vwap_reversion_oro_vs_spy.png'


def load_oro():
    df = pd.read_csv(INPUT_ORO, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    df['volumen'] = df['n_ticks'].clip(lower=1)  # proxy, no hay volumen real
    return df


def load_spy():
    df = yf.download('SPY', period='60d', interval='5m', progress=False)
    df.columns = df.columns.get_level_values(0)
    df = df.rename(columns={'Close': 'close', 'Volume': 'volumen'})
    df.index = pd.to_datetime(df.index)
    df['day'] = df.index.date
    return df[['close', 'volumen', 'day']]


def backtest_sesion(g: pd.DataFrame, n_desvios=N_DESVIOS):
    precio = g['close']
    vol = g['volumen'].clip(lower=1)
    pv = (precio * vol).cumsum()
    vv = vol.cumsum()
    vwap = pv / vv
    dist = precio - vwap
    de = dist.expanding(min_periods=10).std()

    resultados = []
    en_posicion = False
    direccion = None
    precio_entrada = None
    t_entrada = None

    idx = g.index
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
                resultados.append({'entrada_t': t_entrada, 'salida_t': idx[i],
                                    'direccion': 'LARGO' if direccion == 1 else 'CORTO',
                                    'resultado_%': ret_pct,
                                    'motivo_salida': 'vwap' if tocado else 'cierre_sesion'})
                en_posicion = False
            continue
        z = dist.iloc[i] / de_i
        if z >= n_desvios:
            en_posicion, direccion, precio_entrada, t_entrada = True, -1, precio_i, idx[i]
        elif z <= -n_desvios:
            en_posicion, direccion, precio_entrada, t_entrada = True, 1, precio_i, idx[i]
    return resultados


def bootstrap_ci(valores, n_boot=N_BOOTSTRAP, rng=None):
    if len(valores) < 5:
        return None, None, None
    valores = np.asarray(valores)
    medias = np.empty(n_boot)
    for i in range(n_boot):
        medias[i] = rng.choice(valores, size=len(valores), replace=True).mean()
    lo, hi = np.percentile(medias, [2.5, 97.5])
    return medias.mean(), lo, hi


def equity_curve(trades_df, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    pico = capital
    max_dd = 0.0
    valores = [capital]
    for r in trades_df.sort_values('salida_t')['resultado_%']:
        capital *= (1 + r / 100)
        pico = max(pico, capital)
        dd = (capital - pico) / pico * 100
        max_dd = min(max_dd, dd)
        valores.append(capital)
    return valores, capital, max_dd


def reporte(nombre, trades, rng):
    df_t = pd.DataFrame(trades)
    n = len(df_t)
    wr = (df_t['resultado_%'] > 0).mean() * 100
    prom = df_t['resultado_%'].mean()
    media_boot, lo, hi = bootstrap_ci(df_t['resultado_%'].values, rng=rng)
    sig = (lo > 0) or (hi < 0)
    valores_eq, final, max_dd = equity_curve(df_t)
    print(f"\n{'='*90}\n{nombre}\n{'='*90}")
    print(f"Operaciones: {n} | Win rate: {wr:.1f}% | Promedio/op: {prom:.4f}%")
    print(f"Bootstrap 95% CI: [{lo:.4f}%, {hi:.4f}%] -- {'SIGNIFICATIVO' if sig else 'NO significativo'}")
    print(f"Suma simple (sin compounding): {df_t['resultado_%'].sum():.3f}%")
    print(f"$1.000 inicial -> ${final:.2f} (compuesto) | Drawdown máximo: {max_dd:.2f}%")
    for d in ['LARGO', 'CORTO']:
        sub = df_t[df_t['direccion'] == d]
        if len(sub):
            print(f"  {d}: n={len(sub)} | WR={(sub['resultado_%']>0).mean()*100:.1f}% | promedio={sub['resultado_%'].mean():.4f}%")
    return df_t, valores_eq, {'n': n, 'wr': wr, 'promedio': prom, 'IC_lo': lo, 'IC_hi': hi,
                              'significativo': sig, 'final_$1000': final, 'max_dd_%': max_dd}


if __name__ == '__main__':
    rng = np.random.default_rng(SEED)

    print("Cargando oro (M1, 6 meses)...")
    oro = load_oro()
    trades_oro_raw = []
    for day, g in oro.groupby('day'):
        if len(g) < 30:
            continue
        trades_oro_raw.extend(backtest_sesion(g))

    print("Descargando SPY (5min, 60 dias, volumen REAL)...")
    spy = load_spy()
    trades_spy_raw = []
    for day, g in spy.groupby('day'):
        if len(g) < 20:
            continue
        trades_spy_raw.extend(backtest_sesion(g))

    df_oro, eq_oro, m_oro = reporte("ORO (XAU/USD) -- M1, 6 meses, volumen=proxy (n_ticks)", trades_oro_raw, rng)
    df_spy, eq_spy, m_spy = reporte("SPY -- 5min, 60 dias, volumen REAL (preliminar, ventana corta)", trades_spy_raw, rng)

    print(f"\n{'='*90}\nTABLA COMPARATIVA\n{'='*90}")
    tabla = pd.DataFrame({'Oro (M1, 6m)': m_oro, 'SPY (5m, 60d)': m_spy}).T
    print(tabla.to_string())

    fig, axes = plt.subplots(2, 1, figsize=(13, 9), dpi=130)
    axes[0].plot(range(len(eq_oro)), eq_oro, color='#d4af37', label=f'Oro (${m_oro["final_$1000"]:.0f})')
    axes[0].axhline(1000, color='gray', linewidth=0.8, linestyle='--')
    axes[0].set_title(f'VWAP Reversion -- Oro, $1.000 inicial, {m_oro["n"]} operaciones (DD max {m_oro["max_dd_%"]:.1f}%)')
    axes[0].set_ylabel('Cuenta (USD)')
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot(range(len(eq_spy)), eq_spy, color='#1f77b4', label=f'SPY (${m_spy["final_$1000"]:.0f})')
    axes[1].axhline(1000, color='gray', linewidth=0.8, linestyle='--')
    axes[1].set_title(f'VWAP Reversion -- SPY (preliminar), $1.000 inicial, {m_spy["n"]} operaciones (DD max {m_spy["max_dd_%"]:.1f}%)')
    axes[1].set_ylabel('Cuenta (USD)')
    axes[1].set_xlabel('N° de operación (orden cronológico)')
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    import os
    os.makedirs(os.path.dirname(OUTPUT_PNG), exist_ok=True)
    plt.savefig(OUTPUT_PNG, bbox_inches='tight')
    print(f"\nGrafico guardado en {OUTPUT_PNG}")

    df_oro.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/resultados_vwap_reversion_oro_completo.csv', index=False)
    df_spy.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/resultados_vwap_reversion_spy.csv', index=False)
