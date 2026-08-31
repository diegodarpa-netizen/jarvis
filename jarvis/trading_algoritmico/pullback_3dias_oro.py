"""
Test de la regla "Pullback 3 dias" (ver estrategias_validadas/pullback_3dias_spx.md)
sobre ORO, a pedido de Diego (25/08/2026).

Nota importante: los 6 meses de M1 que tenemos (jarvis/trading/xau_strategy/data)
dan solo 130 dias de velas diarias -- INSUFICIENTE para la SMA200 (necesita
200 dias de historia para dar un solo valor no-nulo). No se puede correr la
regla tal cual sobre esos 6 meses. Se usa en cambio GC=F (futuro de oro
COMEX, Yahoo Finance) que tiene ~26 años de historia diaria, misma fuente
y metodo que se uso para validar la regla en S&P 500 -- comparacion directa,
mismo periodo (2000-2026).
"""
import pandas as pd
import numpy as np
import yfinance as yf

N_BOOTSTRAP = 5000
SEED = 42


def load_gold_daily():
    df = yf.download('GC=F', start='2000-01-01', progress=False)
    df.columns = df.columns.get_level_values(0)
    df = df[['Open', 'High', 'Low', 'Close']].copy()
    df.columns = ['open', 'high', 'low', 'close']
    df.index = pd.to_datetime(df.index)
    return df


def backtest(df, sma_trend=200, sma_exit=5):
    df = df.copy()
    df['sma_trend'] = df['close'].rolling(sma_trend).mean()
    df['sma_exit'] = df['close'].rolling(sma_exit).mean()

    trades = []
    en_posicion = False
    precio_entrada = None
    fecha_entrada = None

    close = df['close'].values
    smat = df['sma_trend'].values
    smae = df['sma_exit'].values
    fechas = df.index

    for i in range(3, len(df)):
        if en_posicion:
            if close[i] > smae[i]:
                precio_salida = close[i]
                ret_pct = (precio_salida - precio_entrada) / precio_entrada * 100
                trades.append({'entrada_fecha': fecha_entrada, 'salida_fecha': fechas[i], 'resultado_%': ret_pct})
                en_posicion = False
            continue
        if np.isnan(smat[i]) or np.isnan(smae[i]):
            continue
        tendencia_alcista = close[i] > smat[i]
        pullback_3 = close[i] < close[i-1] < close[i-2] < close[i-3]
        if tendencia_alcista and pullback_3:
            en_posicion = True
            precio_entrada = close[i]
            fecha_entrada = fechas[i]
    return pd.DataFrame(trades)


def bootstrap_ci(valores, n_boot=N_BOOTSTRAP, rng=None):
    if len(valores) < 5:
        return None, None, None
    valores = np.asarray(valores)
    medias = np.empty(n_boot)
    for i in range(n_boot):
        medias[i] = rng.choice(valores, size=len(valores), replace=True).mean()
    lo, hi = np.percentile(medias, [2.5, 97.5])
    return medias.mean(), lo, hi


def buy_hold(df, ini, fin):
    sub = df.loc[ini:fin]
    if len(sub) < 2:
        return None
    return (sub['close'].iloc[-1] - sub['close'].iloc[0]) / sub['close'].iloc[0] * 100


if __name__ == '__main__':
    rng = np.random.default_rng(SEED)

    print("=" * 90)
    print("PASO 1: intentar con los 6 meses de M1 que ya tenemos (XAUUSD_M1.csv)")
    print("=" * 90)
    df6m = pd.read_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv', index_col=0)
    df6m.index = pd.to_datetime(df6m.index, utc=True)
    df6m = df6m.sort_index()
    df6m['day'] = df6m.index.date
    daily6m = df6m.groupby('day')['close'].last()
    print(f"Dias de historia diaria disponibles: {len(daily6m)}")
    print(f"SMA200 necesita 200 dias para dar un solo valor -- {'INSUFICIENTE, 0 señales posibles' if len(daily6m) < 200 else 'suficiente'}")

    print("\n" + "=" * 90)
    print("PASO 2: misma regla, sobre oro con historia completa (GC=F, futuro COMEX, 2000-2026)")
    print("=" * 90)
    gold = load_gold_daily()
    trades = backtest(gold)

    print(f"\nTotal de operaciones: {len(trades)}")
    if len(trades) > 0:
        ganadoras = trades[trades['resultado_%'] > 0]
        print(f"Ganadoras: {len(ganadoras)} | Perdedoras: {len(trades)-len(ganadoras)} | Win rate: {len(ganadoras)/len(trades)*100:.1f}%")
        print(f"Resultado promedio por operacion: {trades['resultado_%'].mean():.3f}%")
        print(f"Suma de resultados (sin compounding): {trades['resultado_%'].sum():.2f}%")
        media_boot, lo, hi = bootstrap_ci(trades['resultado_%'].values, rng=rng)
        sig = (lo > 0) or (hi < 0)
        print(f"Bootstrap 95% CI: [{lo:.3f}%, {hi:.3f}%] -- {'SIGNIFICATIVO' if sig else 'NO significativo'}")

        print("\n--- Por régimen ---")
        for periodo, (ini, fin) in {
            '2000-2007': ('2000-01-01', '2007-12-31'),
            '2008-2009 (crisis)': ('2008-01-01', '2009-12-31'),
            '2010-2019': ('2010-01-01', '2019-12-31'),
            '2020 (COVID)': ('2020-01-01', '2020-12-31'),
            '2021-2026 (reciente, incl. gran suba 2025-26)': ('2021-01-01', '2026-12-31'),
        }.items():
            sub = trades[(trades['entrada_fecha'] >= ini) & (trades['entrada_fecha'] <= fin)]
            bh = buy_hold(gold, ini, fin)
            if len(sub) == 0:
                print(f"{periodo}: sin operaciones")
                continue
            wr = (sub['resultado_%'] > 0).mean() * 100
            print(f"{periodo}: {len(sub)} ops | WR={wr:.1f}% | suma_estrategia={sub['resultado_%'].sum():.1f}% | buy&hold={bh:.1f}%")

        bh_total = buy_hold(gold, gold.index[0], gold.index[-1])
        print(f"\nBuy&hold total del periodo (2000-2026): {bh_total:.1f}%")
        trades.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/resultados_pullback_3dias_oro.csv', index=False)
    else:
        print("Cero operaciones generadas.")
