"""
Primera estrategia REAL del proyecto: cruce de EMA clásico (probado por décadas,
estilo Ed Seykota/turtle-trading) sobre XAU/USD, con datos históricos reales.

Datos: GC=F (futuros de oro COMEX vía yfinance) como proxy de XAU/USD spot —
se mueven prácticamente idénticos. Es una fuente rápida para esta primera
pasada; HistData.com (tick/M1 real de XAU/USD) queda para cuando se necesite
mayor resolución intradía.

Esto es el "paso 1" del camino a trading algorítmico: backtest con datos
reales. Todavía NO es walk-forward, NO es paper trading, NO es plata real.
"""

from decimal import Decimal

import pandas as pd

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
from nautilus_trader.model.enums import AssetClass
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.instruments import Commodity
from nautilus_trader.model.objects import Money
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity


def load_bars(csv_path: str, instrument, bar_type: BarType) -> list[Bar]:
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    bars = []
    for ts, row in df.iterrows():
        ts_ns = int(pd.Timestamp(ts).tz_localize("UTC").value)
        bars.append(
            Bar(
                bar_type=bar_type,
                open=instrument.make_price(row["Open"]),
                high=instrument.make_price(row["High"]),
                low=instrument.make_price(row["Low"]),
                close=instrument.make_price(row["Close"]),
                volume=instrument.make_qty(max(row["Volume"], 1)),
                ts_event=ts_ns,
                ts_init=ts_ns,
            ),
        )
    return bars


def main() -> None:
    engine = BacktestEngine(
        config=BacktestEngineConfig(
            trader_id="JARVIS-XAU-001",
            logging=LoggingConfig(log_level="ERROR"),
        ),
    )

    SIM = Venue("SIM")
    engine.add_venue(
        venue=SIM,
        oms_type=OmsType.NETTING,
        account_type=AccountType.MARGIN,
        base_currency=USD,
        starting_balances=[Money(100_000, USD)],
        default_leverage=Decimal(10),
    )

    # Instrumento tipo "commodity" (no un par de forex genérico) — el oro se
    # opera en onzas troy, con lote mínimo de 1 unidad, no 1000 como un lote
    # estándar de forex. Con default_fx_ccy el motor rechazaba todas las
    # órdenes por "quantity < minimum trade size of 1000".
    instrument = Commodity(
        instrument_id=InstrumentId(symbol=Symbol("XAU"), venue=SIM),
        raw_symbol=Symbol("XAU"),
        asset_class=AssetClass.COMMODITY,
        quote_currency=USD,
        price_precision=2,
        price_increment=Price.from_str("0.01"),
        size_precision=0,
        size_increment=Quantity.from_int(1),
        lot_size=Quantity.from_int(1),
        ts_event=0,
        ts_init=0,
    )
    engine.add_instrument(instrument)

    bar_type = BarType.from_str(f"{instrument.id}-1-DAY-LAST-EXTERNAL")
    bars = load_bars("data_xau_daily.csv", instrument, bar_type)
    engine.add_data(bars)

    # EMA 20/50 en diario — el punto de partida clásico de trend-following
    strategy = EMACross(
        config=EMACrossConfig(
            instrument_id=instrument.id,
            bar_type=bar_type,
            trade_size=Decimal(1),
            fast_ema_period=20,
            slow_ema_period=50,
            request_bars=False,
            subscribe_trade_ticks=False,
        ),
    )
    engine.add_strategy(strategy)

    engine.run()

    result = engine.get_result()
    print(f"\nBarras cargadas: {len(bars)}")
    print(f"Período: {bars[0].ts_event} → {bars[-1].ts_event}")
    print(f"Órdenes totales: {result.total_orders}")
    print(f"Posiciones totales: {result.total_positions}")
    print("\n--- PnL ---")
    print(result.stats_pnls)
    print("\n--- Retornos ---")
    print(result.stats_returns)

    print("\n--- Cuenta final ---")
    print(engine.trader.generate_account_report(SIM).tail(3))

    print("\n--- Posiciones (detalle) ---")
    pos = engine.trader.generate_positions_report()
    if len(pos):
        cols = [c for c in ["ts_opened", "ts_closed", "entry_price", "avg_px_open", "avg_px_close", "realized_pnl"] if c in pos.columns]
        print(pos[cols] if cols else pos)
    else:
        print("(sin posiciones)")

    engine.dispose()


if __name__ == "__main__":
    main()
