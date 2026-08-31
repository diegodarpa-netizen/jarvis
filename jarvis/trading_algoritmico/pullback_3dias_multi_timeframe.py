"""
Validacion multi-timeframe de la regla "Pullback 3 dias" (ver
estrategias_validadas/pullback_3dias_spx.md), a pedido de Diego
(25/08/2026). Semanal y mensual se arman resampleando la MISMA data
diaria que ya tenemos (^GSPC, Yahoo Finance) -- no hace falta descargar
nada nuevo para estos dos.
"""
import pandas as pd
import numpy as np
import yfinance as yf

N_BOOTSTRAP = 5000
SEED = 42


def load_spx_daily():
    df = yf.download('^GSPC', start='2000-01-01', progress=False)
    df.columns = df.columns.get_level_values(0)
    df = df[['Open', 'High', 'Low', 'Close']].copy()
    df.columns = ['open', 'high', 'low', 'close']
    df.index = pd.to_datetime(df.index)
    return df


def resample_ohlc(df, rule):
    out = df.resample(rule).agg(open=('open', 'first'), high=('high', 'max'),
                                 low=('low', 'min'), close=('close', 'last')).dropna()
    return out


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


if __name__ == '__main__':
    rng = np.random.default_rng(SEED)
    print("Descargando S&P 500 diario (base para resamplear a semanal/mensual)...")
    daily = load_spx_daily()

    configs = {
        'Diario (ya validado)': (daily, 200, 5),
        'Semanal': (resample_ohlc(daily, 'W-FRI'), 40, 5),   # 40 semanas ~ 200 dias habiles
        'Mensual': (resample_ohlc(daily, 'ME'), 10, 3),       # 10 meses ~ 200 dias habiles; salida SMA3 (SMA5 mensual = casi medio año, demasiado laxo)
    }

    print("=" * 100)
    print("PULLBACK 3 DIAS -- MISMA REGLA, DISTINTOS TIMEFRAMES (S&P 500, 2000-2026)")
    print("=" * 100)

    resumen = []
    for nombre, (data, sma_t, sma_e) in configs.items():
        trades = backtest(data, sma_trend=sma_t, sma_exit=sma_e)
        if len(trades) < 5:
            print(f"\n{nombre}: solo {len(trades)} operaciones -- insuficiente para conclusion")
            continue
        wr = (trades['resultado_%'] > 0).mean() * 100
        media_boot, lo, hi = bootstrap_ci(trades['resultado_%'].values, rng=rng)
        sig = (lo > 0) or (hi < 0) if media_boot is not None else False
        print(f"\n--- {nombre} (SMA tendencia={sma_t}, SMA salida={sma_e}) ---")
        print(f"Operaciones: {len(trades)} | Win rate: {wr:.1f}% | Promedio/op: {trades['resultado_%'].mean():.3f}%")
        print(f"Bootstrap 95% CI: [{lo:.3f}%, {hi:.3f}%] -- {'SIGNIFICATIVO' if sig else 'NO significativo'}")
        print(f"Suma simple (sin compounding): {trades['resultado_%'].sum():.2f}%")
        resumen.append({'timeframe': nombre, 'n_operaciones': len(trades), 'win_rate_%': round(wr, 1),
                         'promedio_%': round(trades['resultado_%'].mean(), 3),
                         'IC95_lo': round(lo, 3), 'IC95_hi': round(hi, 3), 'significativo': sig})

    print("\n" + "=" * 100)
    print("RESUMEN COMPARATIVO")
    print("=" * 100)
    print(pd.DataFrame(resumen).to_string(index=False))
