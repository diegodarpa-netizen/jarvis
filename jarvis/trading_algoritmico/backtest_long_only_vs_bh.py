"""
Compara la versión SOLO-LARGA del EMA cross contra comprar-y-mantener,
sobre los 6 activos que dieron mal con la estrategia larga+corta:
SPY, NVDA, SHOP, NET, BLK, SCHW. Mismos datos (2 años, 1H) que se usaron
en el portfolio del 12/08 — comparación directa, sin cambiar nada más.
"""

from decimal import Decimal

import pandas as pd

from backtest_portfolio import INSTRUMENTS, SIM, make_instrument, load_bars
from strategy_ema_cross_long_only import EMACrossLongOnly, EMACrossLongOnlyConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import BacktestEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.objects import Money

CANDIDATOS = ["SPY", "NVDA", "SHOP", "NET", "BLK", "SCHW"]


def build_engine():
    engine = BacktestEngine(config=BacktestEngineConfig(trader_id="JARVIS-LONGONLY", logging=LoggingConfig(log_level="ERROR")))
    engine.add_venue(venue=SIM, oms_type=OmsType.NETTING, account_type=AccountType.MARGIN,
                      base_currency=USD, starting_balances=[Money(200_000, USD)], default_leverage=Decimal(5))
    for symbol in CANDIDATOS:
        csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS[symbol]
        engine.add_instrument(make_instrument(symbol, pp, pi, sp, si, ls))
    return engine


def main():
    engine = build_engine()
    print(f"\n{'='*70}\n  SOLO-LARGO vs. COMPRAR-Y-MANTENER — mismos datos (2 años, 1H)\n{'='*70}")

    for symbol in CANDIDATOS:
        csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS[symbol]
        instrument = make_instrument(symbol, pp, pi, sp, si, ls)
        bar_type = BarType.from_str(f"{instrument.id}-1-HOUR-LAST-EXTERNAL")
        bars = load_bars(csv, instrument, bar_type)

        engine.add_data(bars)
        strategy = EMACrossLongOnly(config=EMACrossLongOnlyConfig(
            instrument_id=instrument.id, bar_type=bar_type, trade_size=trade_size,
            fast_ema_period=20, slow_ema_period=50,
        ))
        engine.add_strategy(strategy)
        engine.run()

        pos = engine.trader.generate_positions_report()
        engine.reset(); engine.clear_data(); engine.clear_strategies(); engine.clear_actors()

        df = pd.read_csv(csv)
        bh_return = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100

        if len(pos):
            equity = 100.0
            wins = 0
            for r in pos["realized_return"]:
                equity *= (1 + r)
                if r > 0:
                    wins += 1
            strat_return = (equity / 100 - 1) * 100
            wr = wins / len(pos) * 100
            print(f"\n{symbol}:")
            print(f"  Solo-largo (EMA 20/50):  {len(pos):3} ops | {strat_return:+7.1f}% | WR {wr:.1f}%")
            print(f"  Comprar y mantener:            | {bh_return:+7.1f}%")
        else:
            print(f"\n{symbol}: sin operaciones | Comprar y mantener: {bh_return:+.1f}%")

    engine.dispose()


if __name__ == "__main__":
    main()
