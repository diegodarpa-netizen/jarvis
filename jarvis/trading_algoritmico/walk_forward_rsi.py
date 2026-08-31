"""
Walk-forward de RSI mean-reversion (14, 30/70, parámetros de manual, sin
ajustar) sobre XAU y SPY — 15 años, 6 ventanas, igual disciplina que
todo lo demás hoy. Se reporta el resultado tal cual salga.
"""

from decimal import Decimal

import pandas as pd

from backtest_portfolio import INSTRUMENTS, SIM, make_instrument
from strategy_rsi_mean_reversion import RSIMeanReversion, RSIMeanReversionConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import BacktestEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.objects import Money

N_WINDOWS = 6
ACTIVOS = {"XAU": "data_xau_daily_15y.csv", "SPY": "data_spy_daily_15y.csv"}


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


def run_window(engine, instrument, bar_type, trade_size, bars, w_start, w_end):
    window_bars = [b for b in bars if w_start <= pd.Timestamp(b.ts_event, unit="ns", tz="UTC") <= w_end]
    if len(window_bars) < 60:
        engine.reset(); engine.clear_data(); engine.clear_strategies(); engine.clear_actors()
        return None
    engine.add_data(window_bars)
    strategy = RSIMeanReversion(config=RSIMeanReversionConfig(
        instrument_id=instrument.id, bar_type=bar_type, trade_size=trade_size,
        rsi_period=14, oversold=30.0, overbought=70.0,
    ))
    engine.add_strategy(strategy)
    engine.run()
    pos = engine.trader.generate_positions_report()
    engine.reset(); engine.clear_data(); engine.clear_strategies(); engine.clear_actors()
    if not len(pos):
        return {"trades": 0, "return_pct": 0.0}
    eq, wins = 100.0, 0
    for r in pos["realized_return"]:
        eq *= (1 + r)
        if r > 0:
            wins += 1
    return {"trades": len(pos), "return_pct": round((eq / 100 - 1) * 100, 1), "win_rate": round(wins / len(pos) * 100, 1)}


def main():
    for symbol, csv in ACTIVOS.items():
        c, pp, pi, sp, si, ls, trade_size = INSTRUMENTS[symbol]
        instrument = make_instrument(symbol, pp, pi, sp, si, ls)
        bar_type = BarType.from_str(f"{instrument.id}-1-DAY-LAST-EXTERNAL")
        bars, raw_df = load_daily(csv, instrument, bar_type)

        engine = BacktestEngine(config=BacktestEngineConfig(trader_id=f"JARVIS-RSI-{symbol}", logging=LoggingConfig(log_level="ERROR")))
        engine.add_venue(venue=SIM, oms_type=OmsType.NETTING, account_type=AccountType.MARGIN,
                          base_currency=USD, starting_balances=[Money(200_000, USD)], default_leverage=Decimal(5))
        engine.add_instrument(instrument)

        start = pd.Timestamp(bars[0].ts_event, unit="ns", tz="UTC")
        end = pd.Timestamp(bars[-1].ts_event, unit="ns", tz="UTC")
        edges = pd.date_range(start, end, periods=N_WINDOWS + 1)

        print(f"\n{'='*65}\n  {symbol} — RSI(14) 30/70 mean-reversion — 15 años, {N_WINDOWS} ventanas\n{'='*65}")
        wins_count, total_trades = 0, 0
        for i in range(N_WINDOWS):
            w_start, w_end = edges[i], edges[i + 1]
            result = run_window(engine, instrument, bar_type, trade_size, bars, w_start, w_end)
            window_df = raw_df[(raw_df.index >= w_start) & (raw_df.index <= w_end)]
            bh = (window_df["Close"].iloc[-1] / window_df["Close"].iloc[0] - 1) * 100 if len(window_df) > 1 else 0.0
            if result is None:
                print(f"  V{i+1} ({w_start.date()}->{w_end.date()}): datos insuficientes")
                continue
            total_trades += result["trades"]
            if result["return_pct"] > 0:
                wins_count += 1
            tag = "GANO" if result["return_pct"] > 0 else "perdio"
            print(f"  V{i+1} ({w_start.date()}->{w_end.date()}): RSI {result['trades']:3} ops {result['return_pct']:+6.1f}% (WR {result.get('win_rate','?')}%) -> {tag}  |  B&H {bh:+6.1f}%")
        engine.dispose()
        print(f"  RESUMEN {symbol}: gano en {wins_count}/{N_WINDOWS} ventanas | {total_trades} operaciones totales")


if __name__ == "__main__":
    main()
