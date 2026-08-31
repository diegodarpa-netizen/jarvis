import sys
from decimal import Decimal
from backtest_portfolio import INSTRUMENTS, SIM, make_instrument, load_bars
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.models import FixedFeeModel
from nautilus_trader.config import BacktestEngineConfig, LoggingConfig
from nautilus_trader.examples.strategies.ema_cross import EMACross, EMACrossConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.objects import Money

fee_per_order = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0

csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS["XAU"]
instrument = make_instrument("XAU", pp, pi, sp, si, ls)
bar_type = BarType.from_str(f"{instrument.id}-1-HOUR-LAST-EXTERNAL")
bars = load_bars(csv, instrument, bar_type)

engine = BacktestEngine(config=BacktestEngineConfig(trader_id="JARVIS-FEE3", logging=LoggingConfig(log_level="ERROR")))
kwargs = dict(venue=SIM, oms_type=OmsType.NETTING, account_type=AccountType.MARGIN, base_currency=USD,
              starting_balances=[Money(200_000, USD)], default_leverage=Decimal(5))
if fee_per_order > 0:
    kwargs["fee_model"] = FixedFeeModel(Money(fee_per_order, USD))
engine.add_venue(**kwargs)
engine.add_instrument(instrument)
engine.add_data(bars)
strategy = EMACross(config=EMACrossConfig(instrument_id=instrument.id, bar_type=bar_type, trade_size=trade_size,
    fast_ema_period=20, slow_ema_period=50, request_bars=False, subscribe_trade_ticks=False))
engine.add_strategy(strategy)
engine.run()
acc = engine.trader.generate_account_report(SIM)
pos = engine.trader.generate_positions_report()
final_balance = float(str(acc["total"].iloc[-1]))
ret_pct = (final_balance / 200000 - 1) * 100
total_fees = sum(float(str(x).strip("[]'").replace(" USD", "")) for x in pos["commissions"])
print(f"fee/orden=${fee_per_order:.2f} -> balance final ${final_balance:,.2f} ({ret_pct:+.1f}%) | comisiones totales: ${total_fees:,.2f} | {len(pos)} ops")
engine.dispose()
