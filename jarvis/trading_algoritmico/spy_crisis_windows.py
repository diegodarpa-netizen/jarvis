"""
La pregunta que nunca probamos: ¿la estrategia (EMA 20/50) protege capital
durante una caída REAL, como dice la investigación que debería? Todas las
pruebas de hoy fueron mayormente en ventanas alcistas con ruido — acá
aislamos específicamente 2008 (crisis financiera), 2020 (crash COVID) y
2022 (suba de tasas / mercado bajista), con SPY desde 1993.

Cada ventana lleva "colchón" de datos previos para que la EMA-50 ya esté
calentada antes de que arranque la crisis a medir.
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

CRISIS = {
    "2008 - Crisis Financiera": {"feed_start": "2007-09-01", "crisis_start": "2008-01-01", "crisis_end": "2009-06-30"},
    "2020 - Crash COVID": {"feed_start": "2019-11-01", "crisis_start": "2020-01-01", "crisis_end": "2020-08-31"},
    "2022 - Suba de tasas / bajista": {"feed_start": "2021-10-01", "crisis_start": "2022-01-01", "crisis_end": "2022-12-31"},
}


def load_daily(csv_path, instrument, bar_type, start, end):
    df = pd.read_csv(csv_path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df[(df.index >= start) & (df.index <= end)]
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


def build_engine():
    engine = BacktestEngine(config=BacktestEngineConfig(trader_id="JARVIS-CRISIS", logging=LoggingConfig(log_level="ERROR")))
    engine.add_venue(venue=SIM, oms_type=OmsType.NETTING, account_type=AccountType.MARGIN,
                      base_currency=USD, starting_balances=[Money(200_000, USD)], default_leverage=Decimal(5))
    csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS["SPY"]
    engine.add_instrument(make_instrument("SPY", pp, pi, sp, si, ls))
    return engine


def main():
    engine = build_engine()
    csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS["SPY"]

    print(f"\n{'='*70}\n  SPY EN CRISIS REALES — Estrategia vs. Comprar y mantener\n{'='*70}")

    for label, w in CRISIS.items():
        instrument = make_instrument("SPY", pp, pi, sp, si, ls)
        bar_type = BarType.from_str(f"{instrument.id}-1-DAY-LAST-EXTERNAL")
        bars, raw_df = load_daily("data_spy_daily_max.csv", instrument, bar_type, w["feed_start"], w["crisis_end"])

        engine.add_data(bars)
        strategy = EMACross(config=EMACrossConfig(
            instrument_id=instrument.id, bar_type=bar_type, trade_size=trade_size,
            fast_ema_period=20, slow_ema_period=50, request_bars=False, subscribe_trade_ticks=False,
        ))
        engine.add_strategy(strategy)
        engine.run()

        pos = engine.trader.generate_positions_report()
        engine.reset(); engine.clear_data(); engine.clear_strategies(); engine.clear_actors()

        crisis_start = pd.Timestamp(w["crisis_start"], tz="UTC")
        crisis_end = pd.Timestamp(w["crisis_end"], tz="UTC")

        print(f"\n{label} (medido {w['crisis_start']} -> {w['crisis_end']}, con colchón desde {w['feed_start']}):")

        if len(pos):
            pos_in_window = pos[(pos["ts_closed"] >= crisis_start) & (pos["ts_closed"] <= crisis_end)]
            if len(pos_in_window):
                equity = 100.0
                wins = 0
                for r in pos_in_window["realized_return"]:
                    equity *= (1 + r)
                    if r > 0:
                        wins += 1
                strat_return = (equity / 100 - 1) * 100
                print(f"  Estrategia: {len(pos_in_window):3} ops | {strat_return:+7.1f}% | WR {wins/len(pos_in_window)*100:.1f}%")
            else:
                print("  Estrategia: sin operaciones cerradas en la ventana")
        else:
            print("  Estrategia: sin operaciones")

        window_df = raw_df[(raw_df.index >= crisis_start) & (raw_df.index <= crisis_end)]
        bh_return = (window_df["Close"].iloc[-1] / window_df["Close"].iloc[0] - 1) * 100
        max_drawdown = ((window_df["Close"] / window_df["Close"].cummax()) - 1).min() * 100
        print(f"  Comprar y mantener: {bh_return:+7.1f}% | Peor drawdown en la ventana: {max_drawdown:.1f}%")

    engine.dispose()


if __name__ == "__main__":
    main()
