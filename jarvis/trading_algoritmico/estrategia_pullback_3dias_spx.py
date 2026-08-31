"""
Test de la regla de pullback descrita por Diego (25/08/2026), atribuida a
Ivan Scherman pero que en realidad coincide con la "3-Day Pullback" de
Larry Connors (ver conversacion -- no se encontro esa regla exacta
documentada como de Scherman, se prueba igual por su merito propio).

Regla:
- Filtro de tendencia: cierre > SMA200 (diario)
- Señal de pullback: 3 cierres consecutivos a la baja (cada uno menor
  al anterior) mientras el filtro de tendencia sigue activo
- Entrada: compra al cierre del dia que completa el 3er cierre a la baja
- Salida: al cierre del primer dia en que el precio supera la SMA5
- Solo largos, sin pirampidar (no se abre una 2da posicion si ya hay una abierta)

Test sobre S&P 500 (^GSPC), 2000-2026 -- el activo real de la estrategia,
no oro (que desvirtuaria el test). Con el mismo rigor del proyecto:
walk-forward por decada, bootstrap de significancia, comparacion vs
buy-and-hold en la MISMA ventana.
"""
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUTPUT_PNG_EQUITY = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/pullback_3dias_equity_spx.png'
OUTPUT_PNG_ZOOM = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/pullback_3dias_zoom_2023.png'
N_BOOTSTRAP = 5000
SEED = 42


def load_spx():
    df = yf.download('^GSPC', start='2000-01-01', progress=False)
    df.columns = df.columns.get_level_values(0)
    df = df[['Open', 'High', 'Low', 'Close']].copy()
    df.columns = ['open', 'high', 'low', 'close']
    df.index = pd.to_datetime(df.index)
    return df


def calcular_indicadores(df):
    df['sma200'] = df['close'].rolling(200).mean()
    df['sma5'] = df['close'].rolling(5).mean()
    return df


def backtest(df):
    trades = []
    en_posicion = False
    precio_entrada = None
    fecha_entrada = None

    close = df['close'].values
    sma200 = df['sma200'].values
    sma5 = df['sma5'].values
    fechas = df.index

    for i in range(3, len(df)):
        if en_posicion:
            if close[i] > sma5[i]:
                precio_salida = close[i]
                ret_pct = (precio_salida - precio_entrada) / precio_entrada * 100
                trades.append({
                    'entrada_fecha': fecha_entrada, 'salida_fecha': fechas[i],
                    'precio_entrada': precio_entrada, 'precio_salida': precio_salida,
                    'resultado_%': ret_pct, 'dias_en_posicion': (fechas[i] - fecha_entrada).days,
                })
                en_posicion = False
            continue

        if np.isnan(sma200[i]) or np.isnan(sma5[i]):
            continue

        tendencia_alcista = close[i] > sma200[i]
        pullback_3d = close[i] < close[i-1] < close[i-2] < close[i-3]

        if tendencia_alcista and pullback_3d:
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


def buy_hold_return(df, start, end):
    sub = df.loc[start:end]
    if len(sub) < 2:
        return None
    return (sub['close'].iloc[-1] - sub['close'].iloc[0]) / sub['close'].iloc[0] * 100


def equity_curve(df, trades):
    """Curva de equity simple: 100 al inicio, se mueve solo durante trades
    (sin compounding entre trades, suma simple de %), para comparar forma
    contra buy&hold del mismo periodo."""
    eq = pd.Series(100.0, index=df.index)
    valor = 100.0
    idx_trades = trades.set_index('salida_fecha')
    for fecha in df.index:
        if fecha in idx_trades.index:
            valor += valor * (idx_trades.loc[fecha, 'resultado_%'] / 100)
        eq[fecha] = valor
    return eq


if __name__ == '__main__':
    rng = np.random.default_rng(SEED)
    print("Descargando S&P 500 (^GSPC) 2000-2026...")
    df = load_spx()
    df = calcular_indicadores(df)
    trades = backtest(df)

    print("=" * 95)
    print(f"PULLBACK 3 DIAS (SMA200 + 3 cierres a la baja + salida sobre SMA5) -- S&P 500, {df.index[0].date()} a {df.index[-1].date()}")
    print("=" * 95)
    print(f"\nTotal de operaciones: {len(trades)}")
    ganadores = trades[trades['resultado_%'] > 0]
    perdedores = trades[trades['resultado_%'] <= 0]
    print(f"Ganadoras: {len(ganadores)} | Perdedoras: {len(perdedores)} | Win rate: {len(ganadores)/len(trades)*100:.1f}%")
    print(f"Resultado promedio por operacion: {trades['resultado_%'].mean():.3f}%")
    print(f"Resultado promedio ganadoras: {ganadores['resultado_%'].mean():.3f}% | perdedoras: {perdedores['resultado_%'].mean():.3f}%")
    print(f"Dias promedio en posicion: {trades['dias_en_posicion'].mean():.1f}")
    print(f"Suma de resultados (sin compounding): {trades['resultado_%'].sum():.2f}%")

    media_boot, lo, hi = bootstrap_ci(trades['resultado_%'].values, rng=rng)
    sig = (lo > 0) or (hi < 0)
    print(f"\nBootstrap 95% CI del resultado promedio por operacion: [{lo:.3f}%, {hi:.3f}%] -- {'SIGNIFICATIVO (no cruza cero)' if sig else 'NO significativo (cruza cero, no se distingue de azar)'}")

    print("\n--- Walk-forward informal: resultado por decada ---")
    for periodo, (ini, fin) in {
        '2000-2007 (dot-com crash + recovery)': ('2000-01-01', '2007-12-31'),
        '2008-2009 (crisis financiera)': ('2008-01-01', '2009-12-31'),
        '2010-2019 (bull market largo)': ('2010-01-01', '2019-12-31'),
        '2020 (COVID crash + recovery)': ('2020-01-01', '2020-12-31'),
        '2021-2026 (reciente)': ('2021-01-01', '2026-12-31'),
    }.items():
        sub_trades = trades[(trades['entrada_fecha'] >= ini) & (trades['entrada_fecha'] <= fin)]
        bh = buy_hold_return(df, ini, fin)
        if len(sub_trades) == 0:
            print(f"{periodo}: sin operaciones")
            continue
        wr = (sub_trades['resultado_%'] > 0).mean() * 100
        print(f"{periodo}: {len(sub_trades)} ops | WR={wr:.1f}% | suma_estrategia={sub_trades['resultado_%'].sum():.1f}% | buy&hold_mismo_periodo={bh:.1f}%")

    bh_total = buy_hold_return(df, df.index[0], df.index[-1])
    print(f"\nBuy & hold TOTAL del periodo completo (2000-2026): {bh_total:.1f}%")
    print(f"Suma simple de la estrategia (sin compounding, no comparable directo a buy&hold compuesto): {trades['resultado_%'].sum():.1f}%")

    # equity curve compuesta para comparacion justa
    eq_estrategia = equity_curve(df, trades)
    eq_bh = 100 * df['close'] / df['close'].iloc[0]
    ret_compuesto_estrategia = (eq_estrategia.iloc[-1] / 100 - 1) * 100
    print(f"Retorno COMPUESTO de la estrategia (asumiendo que se reinvierte cada operacion): {ret_compuesto_estrategia:.1f}%")
    print(f"Retorno COMPUESTO buy&hold: {(eq_bh.iloc[-1]/100 - 1)*100:.1f}%")

    fig, ax = plt.subplots(figsize=(14, 7), dpi=130)
    ax.plot(eq_bh.index, eq_bh.values, label='Buy & Hold S&P 500', color='#888888', linewidth=1.2)
    ax.plot(eq_estrategia.index, eq_estrategia.values, label='Estrategia Pullback 3 dias (compuesto)', color='#1f77b4', linewidth=1.4)
    ax.set_yscale('log')
    ax.set_title('Pullback 3 dias (SMA200 + 3 cierres a la baja + salida sobre SMA5) vs Buy&Hold -- S&P 500 2000-2026\n(escala logaritmica)')
    ax.set_ylabel('Valor (base 100, log)')
    ax.legend()
    ax.grid(alpha=0.3)
    import os
    os.makedirs(os.path.dirname(OUTPUT_PNG_EQUITY), exist_ok=True)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG_EQUITY, bbox_inches='tight')
    print(f"\nGrafico de equity guardado en {OUTPUT_PNG_EQUITY}")

    # zoom 2023 (el año del triunfo de Scherman) para ver la regla en accion
    zoom = df.loc['2022-06-01':'2023-12-31']
    zoom_trades = trades[(trades['entrada_fecha'] >= '2022-06-01') & (trades['entrada_fecha'] <= '2023-12-31')]
    fig2, ax2 = plt.subplots(figsize=(15, 7), dpi=130)
    ax2.plot(zoom.index, zoom['close'], color='#333333', linewidth=1.1, label='S&P 500 cierre')
    ax2.plot(zoom.index, zoom['sma200'], color='#9467bd', linewidth=1.2, label='SMA200')
    ax2.plot(zoom.index, zoom['sma5'], color='#ff7f0e', linewidth=0.9, alpha=0.7, label='SMA5')
    for _, t in zoom_trades.iterrows():
        color = '#2ca02c' if t['resultado_%'] > 0 else '#d62728'
        ax2.axvspan(t['entrada_fecha'], t['salida_fecha'], color=color, alpha=0.15)
        ax2.scatter([t['entrada_fecha']], [t['precio_entrada']], marker='^', color=color, s=60, zorder=5, edgecolors='black', linewidths=0.5)
        ax2.scatter([t['salida_fecha']], [t['precio_salida']], marker='x', color=color, s=50, zorder=5)
    ax2.set_title('Pullback 3 dias en accion -- S&P 500, jun/2022 a dic/2023 (año del triunfo de Scherman)')
    ax2.set_ylabel('Precio (puntos)')
    ax2.legend(loc='upper left', fontsize=8)
    ax2.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG_ZOOM, bbox_inches='tight')
    print(f"Grafico zoom 2023 guardado en {OUTPUT_PNG_ZOOM}")

    trades.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/resultados_pullback_3dias_spx.csv', index=False)
