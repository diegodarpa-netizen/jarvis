"""
SPY diario, 15 años reales (2011-2026) — walk-forward de la estrategia
(EMA 20/50, sin ajustar) en 6 ventanas de ~2,5 años cada una, más
comparación contra comprar-y-mantener en el mismo período exacto.

Cruza: recuperación post-2008, bull market largo de los 2010s,
crash COVID 2020, suba de tasas / baja 2022.
"""

from decimal import Decimal

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

N_WINDOWS = 6


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


def run_window(engine, instrument, bar_type, trade_size, bars, window_start, window_end):
    window_bars = [b for b in bars if window_start <= pd.Timestamp(b.ts_event, unit="ns", tz="UTC") <= window_end]
    if len(window_bars) < 60:
        engine.reset(); engine.clear_data(); engine.clear_strategies(); engine.clear_actors()
        return None

    engine.add_data(window_bars)
    strategy = EMACross(config=EMACrossConfig(
        instrument_id=instrument.id, bar_type=bar_type, trade_size=trade_size,
        fast_ema_period=20, slow_ema_period=50, request_bars=False, subscribe_trade_ticks=False,
    ))
    engine.add_strategy(strategy)
    engine.run()

    pos = engine.trader.generate_positions_report()
    engine.reset(); engine.clear_data(); engine.clear_strategies(); engine.clear_actors()

    if not len(pos):
        return {"trades": 0, "return_pct": 0.0}
    equity = 100.0
    wins = 0
    for r in pos["realized_return"]:
        equity *= (1 + r)
        if r > 0:
            wins += 1
    return {"trades": len(pos), "return_pct": round((equity / 100 - 1) * 100, 1), "win_rate": round(wins / len(pos) * 100, 1)}


def main():
    csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS["SPY"]
    instrument = make_instrument("SPY", pp, pi, sp, si, ls)
    bar_type = BarType.from_str(f"{instrument.id}-1-DAY-LAST-EXTERNAL")
    bars, raw_df = load_daily("data_spy_daily_15y.csv", instrument, bar_type)

    engine = BacktestEngine(config=BacktestEngineConfig(trader_id="JARVIS-SPY15Y", logging=LoggingConfig(log_level="ERROR")))
    engine.add_venue(venue=SIM, oms_type=OmsType.NETTING, account_type=AccountType.MARGIN,
                      base_currency=USD, starting_balances=[Money(200_000, USD)], default_leverage=Decimal(5))
    engine.add_instrument(instrument)

    start = pd.Timestamp(bars[0].ts_event, unit="ns", tz="UTC")
    end = pd.Timestamp(bars[-1].ts_event, unit="ns", tz="UTC")
    edges = pd.date_range(start, end, periods=N_WINDOWS + 1)

    print(f"\n{'='*60}\n  SPY DIARIO — 15 AÑOS ({len(bars)} barras, {start.date()} -> {end.date()})\n{'='*60}")

    wins_count = 0
    total_trades = 0
    for i in range(N_WINDOWS):
        w_start, w_end = edges[i], edges[i + 1]
        result = run_window(engine, instrument, bar_type, trade_size, bars, w_start, w_end)

        # Comprar y mantener en la misma ventana exacta, para comparar
        window_df = raw_df[(raw_df.index >= w_start) & (raw_df.index <= w_end)]
        bh_return = (window_df["Close"].iloc[-1] / window_df["Close"].iloc[0] - 1) * 100 if len(window_df) > 1 else 0.0

        if result is None:
            print(f"  Ventana {i+1} ({w_start.date()} -> {w_end.date()}): datos insuficientes")
            continue
        total_trades += result["trades"]
        tag = "GANO" if result["return_pct"] > 0 else "perdio"
        if result["return_pct"] > 0:
            wins_count += 1
        print(f"  Ventana {i+1} ({w_start.date()} -> {w_end.date()}):")
        print(f"    Estrategia (EMA 20/50): {result['trades']:3} ops | {result['return_pct']:+6.1f}% | WR {result.get('win_rate','?')}% -> {tag}")
        print(f"    Comprar y mantener:            | {bh_return:+6.1f}%")

    engine.dispose()

    print(f"\n{'='*60}")
    print(f"  RESUMEN: estrategia ganó en {wins_count}/{N_WINDOWS} ventanas | {total_trades} operaciones totales")
    full_bh = (raw_df['Close'].iloc[-1] / raw_df['Close'].iloc[0] - 1) * 100
    print(f"  Comprar y mantener SPY, los 15 años completos: {full_bh:+.1f}%")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
