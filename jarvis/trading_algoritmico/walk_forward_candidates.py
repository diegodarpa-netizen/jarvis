"""
Walk-forward sobre los dos únicos candidatos de la barrida de timeframes
que tenían muestra decente y todavía no fueron validados: BTC 4H (84
operaciones, +38,6% agregado) y SPY 4H (28 operaciones, +35,6% agregado).

Mismo criterio de siempre: parámetros fijos (EMA 20/50), partir el
período en ventanas sucesivas, ver si el resultado se sostiene ventana
a ventana o es un espejismo del agregado — como ya pasó con XAU 1H y TLT.
"""

from decimal import Decimal

import pandas as pd

from backtest_portfolio import INSTRUMENTS, SIM, make_instrument
from timeframe_sweep import load_and_resample, TIMEFRAMES
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import BacktestEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.examples.strategies.ema_cross import EMACross
from nautilus_trader.examples.strategies.ema_cross import EMACrossConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.objects import Money

N_WINDOWS = 4
CANDIDATES = [("BTC", "4H"), ("SPY", "4H")]


def build_engine() -> BacktestEngine:
    engine = BacktestEngine(config=BacktestEngineConfig(trader_id="JARVIS-WF2", logging=LoggingConfig(log_level="ERROR")))
    engine.add_venue(venue=SIM, oms_type=OmsType.NETTING, account_type=AccountType.MARGIN,
                      base_currency=USD, starting_balances=[Money(200_000, USD)], default_leverage=Decimal(5))
    for symbol in INSTRUMENTS:
        csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS[symbol]
        engine.add_instrument(make_instrument(symbol, pp, pi, sp, si, ls))
    return engine


def run_window(engine, symbol, tf_key, bars, window_start, window_end):
    csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS[symbol]
    instrument = make_instrument(symbol, pp, pi, sp, si, ls)
    bar_type = BarType.from_str(f"{instrument.id}-{TIMEFRAMES[tf_key]['bar_str']}-LAST-EXTERNAL")

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
    engine = build_engine()

    for symbol, tf_key in CANDIDATES:
        csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS[symbol]
        instrument = make_instrument(symbol, pp, pi, sp, si, ls)
        bar_type = BarType.from_str(f"{instrument.id}-{TIMEFRAMES[tf_key]['bar_str']}-LAST-EXTERNAL")
        bars = load_and_resample(symbol, tf_key, instrument, bar_type)

        start = pd.Timestamp(bars[0].ts_event, unit="ns", tz="UTC")
        end = pd.Timestamp(bars[-1].ts_event, unit="ns", tz="UTC")
        edges = pd.date_range(start, end, periods=N_WINDOWS + 1)

        print(f"\n{'='*55}\n  {symbol} {tf_key} — walk-forward ({len(bars)} barras, {start.date()} -> {end.date()})\n{'='*55}")
        wins_count = 0
        for i in range(N_WINDOWS):
            w_start, w_end = edges[i], edges[i + 1]
            result = run_window(engine, symbol, tf_key, bars, w_start, w_end)
            if result is None:
                print(f"  Ventana {i+1} ({w_start.date()} -> {w_end.date()}): datos insuficientes")
                continue
            tag = "GANO" if result["return_pct"] > 0 else "perdio"
            if result["return_pct"] > 0:
                wins_count += 1
            print(f"  Ventana {i+1} ({w_start.date()} -> {w_end.date()}): {result['trades']} ops, {result['return_pct']:+.1f}%, WR {result.get('win_rate','?')}% -> {tag}")
        print(f"  RESUMEN: gano en {wins_count}/{N_WINDOWS} ventanas")

    engine.dispose()


if __name__ == "__main__":
    main()
