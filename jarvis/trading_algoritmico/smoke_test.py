"""
Prueba de humo (smoke test) del entorno de NautilusTrader.

Objetivo: validar que el motor de backtest corre de punta a punta en esta
máquina (venv Python 3.12 + nautilus_trader 1.230.0), usando datos
SINTÉTICOS generados en memoria — todavía no datos reales de XAU/USD.
Esa es la etapa siguiente (ver PLAN_CONSTRUCCION.md).

No representa ninguna estrategia real ni tiene ventaja estadística.
"""

from decimal import Decimal

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
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.test_kit.providers import TestDataGenerator
from nautilus_trader.test_kit.providers import TestInstrumentProvider


def main() -> None:
    # 1) Motor de backtest
    engine = BacktestEngine(
        config=BacktestEngineConfig(
            trader_id="JARVIS-SMOKE-001",
            logging=LoggingConfig(log_level="ERROR"),
        ),
    )

    # 2) Venue simulado (SIM) — cuenta de margen en USD
    SIM = Venue("SIM")
    engine.add_venue(
        venue=SIM,
        oms_type=OmsType.NETTING,
        account_type=AccountType.MARGIN,
        base_currency=USD,
        starting_balances=[Money(1_000_000, USD)],
        default_leverage=Decimal(1),
    )

    # 3) Instrumento — EUR/USD genérico (solo para validar el entorno)
    instrument = TestInstrumentProvider.default_fx_ccy("EUR/USD", venue=SIM)
    engine.add_instrument(instrument)

    # 4) Datos sintéticos: barras de 1 minuto con progresión de precio
    bar_type = BarType.from_str(f"{instrument.id}-1-MINUTE-LAST-EXTERNAL")

    first_bar = Bar(
        bar_type=bar_type,
        open=instrument.make_price(1.1000),
        high=instrument.make_price(1.1005),
        low=instrument.make_price(1.0995),
        close=instrument.make_price(1.1000),
        volume=instrument.make_qty(100_000),
        ts_event=0,
        ts_init=0,
    )

    bars_up = TestDataGenerator.generate_monotonic_bars(
        instrument=instrument,
        first_bar=first_bar,
        bar_count=150,
        increasing_series=True,
    )
    bars_down = TestDataGenerator.generate_monotonic_bars(
        instrument=instrument,
        first_bar=bars_up[-1],
        bar_count=150,
        increasing_series=False,
    )
    engine.add_data(bars_up + bars_down)

    # 5) Estrategia de referencia (cruce de medias móviles, sin ventaja real)
    strategy = EMACross(
        config=EMACrossConfig(
            instrument_id=instrument.id,
            bar_type=bar_type,
            trade_size=Decimal(10_000),
            fast_ema_period=5,
            slow_ema_period=15,
            request_bars=False,
            subscribe_trade_ticks=False,
        ),
    )
    engine.add_strategy(strategy)

    # 6) Correr el backtest
    engine.run()

    # 7) Resumen de resultados
    print("\n=== SMOKE TEST OK — el entorno de NautilusTrader funciona ===")
    print(engine.trader.generate_account_report(SIM))
    print("\n--- Órdenes (fills) ---")
    print(engine.trader.generate_order_fills_report())
    print("\n--- Órdenes (todas) ---")
    print(engine.trader.generate_orders_report())
    print("\n--- Posiciones ---")
    print(engine.trader.generate_positions_report())
    print(f"\nTotal barras cargadas: {len(bars_up) + len(bars_down)}")

    engine.dispose()


if __name__ == "__main__":
    main()
