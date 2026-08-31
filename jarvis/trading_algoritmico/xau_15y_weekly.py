"""
XAU (GC=F) 15 años diarios (2011-2026) — el activo que más rentabilidad
dio con nuestra propia estrategia (EMA 20/50) en cada prueba de hoy.

Corre la estrategia sobre los 15 años completos y desglosa el resultado
SEMANA A SEMANA (no solo en 4-6 ventanas grandes como antes) — cuántas
semanas ganó, cuántas perdió, retorno promedio por semana, mejor y peor
semana. Compara además contra comprar-y-mantener en el mismo período.
"""

from decimal import Decimal

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from backtest_portfolio import INSTRUMENTS, SIM, make_instrument
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import BacktestEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.examples.strategies.ema_cross import EMACross
from nautilus_trader.examples.strategies.ema_cross import EMACrossConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.objects import Money


def load_daily(csv_path, instrument, bar_type):
    df = pd.read_csv(csv_path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    o, h, l, c = df["Open"], df["High"], df["Low"], df["Close"]
    df["High"] = pd.concat([h, o, c], axis=1).max(axis=1)
    df["Low"] = pd.concat([l, o, c], axis=1).min(axis=1)
    bars = []
    for ts, row in df.iterrows():
        ts_ns = int(pd.Timestamp(ts).value)
        bars.append(Bar(
            bar_type=bar_type,
            open=instrument.make_price(row["Open"]), high=instrument.make_price(row["High"]),
            low=instrument.make_price(row["Low"]), close=instrument.make_price(row["Close"]),
            volume=instrument.make_qty(max(row["Volume"], 1)),
            ts_event=ts_ns, ts_init=ts_ns,
        ))
    return bars, df


def main():
    csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS["XAU"]
    instrument = make_instrument("XAU", pp, pi, sp, si, ls)
    bar_type = BarType.from_str(f"{instrument.id}-1-DAY-LAST-EXTERNAL")
    bars, raw_df = load_daily("data_xau_daily_15y.csv", instrument, bar_type)

    engine = BacktestEngine(config=BacktestEngineConfig(trader_id="JARVIS-XAU15Y", logging=LoggingConfig(log_level="ERROR")))
    engine.add_venue(venue=SIM, oms_type=OmsType.NETTING, account_type=AccountType.MARGIN,
                      base_currency=USD, starting_balances=[Money(200_000, USD)], default_leverage=Decimal(5))
    engine.add_instrument(instrument)
    engine.add_data(bars)

    strategy = EMACross(config=EMACrossConfig(
        instrument_id=instrument.id, bar_type=bar_type, trade_size=trade_size,
        fast_ema_period=20, slow_ema_period=50, request_bars=False, subscribe_trade_ticks=False,
    ))
    engine.add_strategy(strategy)
    engine.run()

    pos = engine.trader.generate_positions_report()
    engine.dispose()

    print(f"\n{'='*60}\n  XAU DIARIO — 15 AÑOS ({len(bars)} barras)\n{'='*60}")
    print(f"Operaciones totales: {len(pos)}")

    # Curva de equity día a día ($100 iniciales), luego resampleada a semanal
    pos = pos.sort_values("ts_closed")
    equity_points = [(pd.Timestamp(bars[0].ts_event, unit="ns", tz="UTC"), 100.0)]
    eq = 100.0
    for _, row in pos.iterrows():
        eq *= (1 + row["realized_return"])
        equity_points.append((row["ts_closed"], eq))

    eq_series = pd.Series({t: v for t, v in equity_points})
    eq_series = eq_series[~eq_series.index.duplicated(keep="last")].sort_index()

    daily_grid = pd.date_range(eq_series.index.min(), eq_series.index.max(), freq="D")
    eq_daily = eq_series.reindex(daily_grid.union(eq_series.index)).ffill().reindex(daily_grid)

    weekly = eq_daily.resample("W").last()
    weekly_returns = weekly.pct_change().dropna() * 100

    total_weeks = len(weekly_returns)
    winning_weeks = (weekly_returns > 0).sum()
    losing_weeks = (weekly_returns < 0).sum()
    flat_weeks = (weekly_returns == 0).sum()

    print(f"\n--- Desglose semana a semana ({total_weeks} semanas) ---")
    print(f"Semanas ganadoras: {winning_weeks} ({winning_weeks/total_weeks*100:.1f}%)")
    print(f"Semanas perdedoras: {losing_weeks} ({losing_weeks/total_weeks*100:.1f}%)")
    print(f"Semanas sin cambio: {flat_weeks} ({flat_weeks/total_weeks*100:.1f}%)")
    print(f"Retorno promedio semanal: {weekly_returns.mean():+.3f}%")
    print(f"Mejor semana: {weekly_returns.max():+.2f}% ({weekly_returns.idxmax().date()})")
    print(f"Peor semana: {weekly_returns.min():+.2f}% ({weekly_returns.idxmin().date()})")
    print(f"Desvío estándar semanal: {weekly_returns.std():.3f}%")

    final_strat = eq_daily.iloc[-1]
    bh_return = (raw_df["Close"].iloc[-1] / raw_df["Close"].iloc[0] - 1) * 100
    print(f"\nEstrategia (EMA 20/50), 15 años completos: {(final_strat/100-1)*100:+.1f}%")
    print(f"Comprar y mantener XAU, 15 años completos: {bh_return:+.1f}%")

    # Gráfico
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9))
    ax1.plot(eq_daily.index, eq_daily.values, color="#d4a017", linewidth=1.2, label="Estrategia (US$100 iniciales)")
    bh_curve = 100 * (raw_df["Close"] / raw_df["Close"].iloc[0])
    ax1.plot(raw_df.index, bh_curve.values, color="gray", linewidth=1, linestyle="--", label="Comprar y mantener")
    ax1.set_title("XAU — 15 años — Estrategia vs. Comprar y mantener")
    ax1.set_ylabel("US$")
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.bar(weekly_returns.index, weekly_returns.values,
            color=["#2ca02c" if v > 0 else "#d62728" for v in weekly_returns.values], width=5)
    ax2.set_title(f"Retorno semanal de la estrategia ({total_weeks} semanas — {winning_weeks/total_weeks*100:.1f}% positivas)")
    ax2.set_ylabel("Retorno semanal (%)")
    ax2.axhline(0, color="black", linewidth=0.5)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig("xau_15y_weekly.png", dpi=150)
    print("\nGráfico guardado: xau_15y_weekly.png")


if __name__ == "__main__":
    main()
