"""
El mismo portfolio de backtest_portfolio.py (XAU, EUR/USD, BTC, SPY, QQQ,
EMA 20/50, 1H, ~2 años reales), pero con el filtro de tendencia (Efficiency
Ratio >= 0.30) agregado — para comparar contra el resultado sin filtro.
"""

from decimal import Decimal

from backtest_portfolio import INSTRUMENTS, SIM, make_instrument, load_bars
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import BacktestEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.objects import Money
from strategy_ema_cross_filtered import EMACrossFiltered, EMACrossFilteredConfig


def main() -> None:
    engine = BacktestEngine(
        config=BacktestEngineConfig(
            trader_id="JARVIS-PORTFOLIO-FILTERED",
            logging=LoggingConfig(log_level="ERROR"),
        ),
    )
    engine.add_venue(
        venue=SIM, oms_type=OmsType.NETTING, account_type=AccountType.MARGIN,
        base_currency=USD, starting_balances=[Money(200_000, USD)], default_leverage=Decimal(5),
    )

    for symbol, (csv, pp, pi, sp, si, ls, trade_size) in INSTRUMENTS.items():
        instrument = make_instrument(symbol, pp, pi, sp, si, ls)
        engine.add_instrument(instrument)
        bar_type = BarType.from_str(f"{instrument.id}-1-HOUR-LAST-EXTERNAL")
        engine.add_data(load_bars(csv, instrument, bar_type))
        strategy = EMACrossFiltered(
            config=EMACrossFilteredConfig(
                instrument_id=instrument.id, bar_type=bar_type, trade_size=trade_size,
                fast_ema_period=20, slow_ema_period=50, er_period=20, er_threshold=0.30,
                order_id_tag=symbol,
            ),
        )
        engine.add_strategy(strategy)

    engine.run()

    result = engine.get_result()
    print("\n=== PORTFOLIO CON FILTRO DE TENDENCIA (Efficiency Ratio >= 0.30) ===")
    print(f"Órdenes totales: {result.total_orders}")
    print(f"Posiciones totales: {result.total_positions}")
    print("\n--- PnL combinado ---")
    print(result.stats_pnls)
    print("\n--- Retornos combinados ---")
    print(result.stats_returns)

    pos = engine.trader.generate_positions_report()
    if len(pos):
        pos["symbol"] = pos["instrument_id"].astype(str).str.split(".").str[0]
        pos["pnl_num"] = pos["realized_pnl"].astype(str).str.replace(" USD", "").astype(float)
        summary = pos.groupby("symbol").agg(
            operaciones=("pnl_num", "count"),
            pnl_total=("pnl_num", "sum"),
        )
        summary["ganadoras"] = pos.groupby("symbol")["pnl_num"].apply(lambda s: (s > 0).sum())
        summary["win_rate_%"] = (summary["ganadoras"] / summary["operaciones"] * 100).round(1)
        print("\n--- Por instrumento ---")
        print(summary)
    else:
        print("(sin posiciones)")

    engine.dispose()


if __name__ == "__main__":
    main()
