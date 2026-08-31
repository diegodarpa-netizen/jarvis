"""
Reporte completo de la estrategia "Pullback 3 dias" (ver
estrategias_validadas/pullback_3dias_spx.md), a pedido de Diego
(25/08/2026): equity en dolares desde $1.000, drawdown real (marcado a
mercado dia a dia, no solo entre cierres de operacion), comparacion
diario vs semanal, y todas las metricas de riesgo/retorno juntas.
"""
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CAPITAL_INICIAL = 1000.0
OUTPUT_PNG = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/pullback_3dias_reporte_completo.png'


def load_spx_daily():
    df = yf.download('^GSPC', start='2000-01-01', progress=False)
    df.columns = df.columns.get_level_values(0)
    df = df[['Open', 'High', 'Low', 'Close']].copy()
    df.columns = ['open', 'high', 'low', 'close']
    df.index = pd.to_datetime(df.index)
    return df


def resample_ohlc(df, rule):
    return df.resample(rule).agg(open=('open', 'first'), high=('high', 'max'),
                                  low=('low', 'min'), close=('close', 'last')).dropna()


def backtest_con_equity(df, sma_trend, sma_exit, capital_inicial=CAPITAL_INICIAL):
    """Backtest que ademas devuelve una serie de equity marcada a mercado
    DIA A DIA (o barra a barra, segun el timeframe) mientras hay una
    posicion abierta -- no solo el valor al cerrar cada operacion. Esto
    permite calcular el drawdown real, no una subestimacion."""
    df = df.copy()
    df['sma_trend'] = df['close'].rolling(sma_trend).mean()
    df['sma_exit'] = df['close'].rolling(sma_exit).mean()

    close = df['close'].values
    smat = df['sma_trend'].values
    smae = df['sma_exit'].values
    fechas = df.index

    equity = np.full(len(df), np.nan)
    capital = capital_inicial
    en_posicion = False
    precio_entrada = None
    unidades = None
    trades = []
    fecha_entrada = None

    for i in range(len(df)):
        if i < 3 or np.isnan(smat[i]) or np.isnan(smae[i]):
            equity[i] = capital
            continue

        if en_posicion:
            equity[i] = unidades * close[i]  # marcado a mercado
            if close[i] > smae[i]:
                capital = unidades * close[i]
                ret_pct = (close[i] - precio_entrada) / precio_entrada * 100
                trades.append({'entrada_fecha': fecha_entrada, 'salida_fecha': fechas[i], 'resultado_%': ret_pct})
                en_posicion = False
            continue

        equity[i] = capital
        tendencia_alcista = close[i] > smat[i]
        pullback_3 = close[i] < close[i-1] < close[i-2] < close[i-3]
        if tendencia_alcista and pullback_3:
            en_posicion = True
            precio_entrada = close[i]
            unidades = capital / close[i]
            fecha_entrada = fechas[i]
            equity[i] = capital

    eq_serie = pd.Series(equity, index=df.index).ffill().fillna(capital_inicial)
    return eq_serie, pd.DataFrame(trades)


def metricas(eq_serie: pd.Series, trades: pd.DataFrame, dias_por_año: float, capital_inicial=CAPITAL_INICIAL):
    retorno_total_pct = (eq_serie.iloc[-1] / capital_inicial - 1) * 100
    años = (eq_serie.index[-1] - eq_serie.index[0]).days / 365.25
    cagr = ((eq_serie.iloc[-1] / capital_inicial) ** (1 / años) - 1) * 100 if años > 0 else np.nan

    pico = eq_serie.cummax()
    drawdown = (eq_serie - pico) / pico * 100
    max_dd = drawdown.min()

    calmar = cagr / abs(max_dd) if max_dd != 0 else np.nan

    wr = (trades['resultado_%'] > 0).mean() * 100 if len(trades) else np.nan
    avg_trade = trades['resultado_%'].mean() if len(trades) else np.nan

    return {
        'valor_final_$': round(eq_serie.iloc[-1], 2),
        'retorno_total_%': round(retorno_total_pct, 1),
        'CAGR_%': round(cagr, 2),
        'max_drawdown_%': round(max_dd, 2),
        'calmar_ratio': round(calmar, 2),
        'n_operaciones': len(trades),
        'win_rate_%': round(wr, 1),
        'promedio_por_operacion_%': round(avg_trade, 3),
    }, drawdown


if __name__ == '__main__':
    print("Descargando S&P 500...")
    daily = load_spx_daily()
    weekly = resample_ohlc(daily, 'W-FRI')

    eq_daily, trades_daily = backtest_con_equity(daily, 200, 5)
    eq_weekly, trades_weekly = backtest_con_equity(weekly, 40, 5)

    bh = CAPITAL_INICIAL * daily['close'] / daily['close'].iloc[0]
    pico_bh = bh.cummax()
    dd_bh = (bh - pico_bh) / pico_bh * 100

    m_daily, dd_daily = metricas(eq_daily, trades_daily, 252)
    m_weekly, dd_weekly = metricas(eq_weekly, trades_weekly, 52)
    m_bh, _ = metricas(bh, pd.DataFrame({'resultado_%': []}), 252)
    m_bh['max_drawdown_%'] = round(dd_bh.min(), 2)
    m_bh['n_operaciones'] = 1
    m_bh['win_rate_%'] = np.nan
    m_bh['promedio_por_operacion_%'] = np.nan
    m_bh['calmar_ratio'] = round(m_bh['CAGR_%'] / abs(m_bh['max_drawdown_%']), 2)

    print("=" * 100)
    print(f"REPORTE COMPLETO -- Pullback 3 dias, capital inicial ${CAPITAL_INICIAL:,.0f}, S&P 500 2000-2026")
    print("=" * 100)
    tabla = pd.DataFrame({'Diario': m_daily, 'Semanal': m_weekly, 'Buy&Hold': m_bh}).T
    print(tabla.to_string())

    print(f"\n--- ¿$1.000 invertidos el 03/01/2000, hoy valen? ---")
    print(f"Estrategia DIARIA:  ${m_daily['valor_final_$']:,.2f}  ({m_daily['retorno_total_%']:.1f}%)")
    print(f"Estrategia SEMANAL: ${m_weekly['valor_final_$']:,.2f}  ({m_weekly['retorno_total_%']:.1f}%)")
    print(f"Comprar y mantener: ${m_bh['valor_final_$']:,.2f}  ({m_bh['retorno_total_%']:.1f}%)")

    print(f"\n--- ¿Cuál es mejor, diario o semanal? ---")
    print(f"CAGR:            Diario {m_daily['CAGR_%']:.2f}% vs Semanal {m_weekly['CAGR_%']:.2f}%")
    print(f"Max drawdown:     Diario {m_daily['max_drawdown_%']:.2f}% vs Semanal {m_weekly['max_drawdown_%']:.2f}%")
    print(f"Calmar (CAGR/DD): Diario {m_daily['calmar_ratio']:.2f} vs Semanal {m_weekly['calmar_ratio']:.2f}  (mas alto = mejor retorno por unidad de riesgo)")
    print(f"N operaciones:    Diario {m_daily['n_operaciones']} vs Semanal {m_weekly['n_operaciones']} (mas operaciones = mas trabajo/costos, pero mas robustez estadistica)")

    # --- Grafico ---
    fig, axes = plt.subplots(3, 1, figsize=(15, 12), dpi=130, gridspec_kw={'height_ratios': [3, 1.3, 1.3]}, sharex=True)

    ax1 = axes[0]
    ax1.plot(bh.index, bh.values, color='#888888', linewidth=1.1, label=f'Comprar y mantener (${m_bh["valor_final_$"]:,.0f})')
    ax1.plot(eq_daily.index, eq_daily.values, color='#1f77b4', linewidth=1.3, label=f'Pullback 3d DIARIO (${m_daily["valor_final_$"]:,.0f})')
    ax1.plot(eq_weekly.index, eq_weekly.values, color='#2ca02c', linewidth=1.3, label=f'Pullback 3d SEMANAL (${m_weekly["valor_final_$"]:,.0f})')
    ax1.set_title(f'Pullback 3 dias -- $1.000 invertidos en 03/01/2000, S&P 500 (2000-2026)', fontsize=12)
    ax1.set_ylabel('Valor de la cuenta (USD)')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(alpha=0.3)

    ax2 = axes[1]
    ax2.fill_between(dd_daily.index, dd_daily.values, 0, color='#1f77b4', alpha=0.4, label=f'Diario (max {m_daily["max_drawdown_%"]:.1f}%)')
    ax2.fill_between(dd_bh.index, dd_bh.values, 0, color='#888888', alpha=0.25, label=f'Buy&Hold (max {m_bh["max_drawdown_%"]:.1f}%)')
    ax2.set_ylabel('Drawdown Diario (%)')
    ax2.legend(loc='lower left', fontsize=8)
    ax2.grid(alpha=0.3)

    ax3 = axes[2]
    ax3.fill_between(dd_weekly.index, dd_weekly.values, 0, color='#2ca02c', alpha=0.4, label=f'Semanal (max {m_weekly["max_drawdown_%"]:.1f}%)')
    ax3.fill_between(dd_bh.index, dd_bh.values, 0, color='#888888', alpha=0.25, label=f'Buy&Hold (max {m_bh["max_drawdown_%"]:.1f}%)')
    ax3.set_ylabel('Drawdown Semanal (%)')
    ax3.set_xlabel('Fecha')
    ax3.legend(loc='lower left', fontsize=8)
    ax3.grid(alpha=0.3)

    plt.tight_layout()
    import os
    os.makedirs(os.path.dirname(OUTPUT_PNG), exist_ok=True)
    plt.savefig(OUTPUT_PNG, bbox_inches='tight')
    print(f"\nGrafico guardado en {OUTPUT_PNG}")

    tabla.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/resultados_pullback_3dias_reporte_completo.csv')
