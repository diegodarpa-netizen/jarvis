"""
Portfolio de 5 instrumentos no (o poco) correlacionados, MISMA estrategia,
MISMOS parámetros fijos (EMA 20/50, 1 hora) — sin tocar nada por instrumento.

Objetivo: medir si diversificar en varias clases de activo mejora el Sharpe
combinado frente a cada instrumento por separado, tal como plantea la
matemática de Sharpe_portfolio ≈ Sharpe_individual × sqrt(N) para apuestas
no correlacionadas (ver knowledge/portfolio_de_estrategias.md).

Instrumentos: XAU/USD (metales), EUR/USD (forex), BTC/USD (cripto),
SPY (equities EE.UU.), QQQ (equities tech EE.UU.) — datos reales por hora,
últimos ~2 años, vía yfinance.

IMPORTANTE: los parámetros de la estrategia (20/50) NO se ajustaron para
que el resultado se vea bien — son los mismos que en el backtest anterior
de XAU en diario. Ajustarlos hasta que el número guste sería exactamente
el data snooping / overfitting que ya identificamos como el problema
central de todo esto.
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
from nautilus_trader.model.enums import AssetClass
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.instruments import Commodity
from nautilus_trader.model.objects import Money
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity


SIM = Venue("SIM")

# symbol -> (csv, price_precision, price_increment, size_precision, size_increment, lot_size, trade_size)
#
# Universo corregido (11/08/2026, ver knowledge/seleccion_de_universo.md): se
# saca QQQ (redundante con SPY, misma clase de activo, alta correlación) y se
# suma TLT (bonos largos del Tesoro EE.UU.) para cubrir la clase de renta fija
# que faltaba — siguiendo el modelo real de KMLM/DBMF (commodities, monedas,
# bonos, acciones). BTC queda aparte, como activo especulativo sin el mismo
# respaldo histórico que las otras cuatro clases.
INSTRUMENTS = {
    "XAU": ("data_xau_hourly.csv", 2, "0.01", 0, "1", "1", Decimal(1)),
    "EUR": ("data_eurusd_hourly.csv", 5, "0.00001", 0, "1000", "1000", Decimal(1000)),
    "BTC": ("data_btc_hourly.csv", 2, "0.01", 3, "0.001", "0.001", Decimal("0.01")),
    "SPY": ("data_spy_hourly.csv", 2, "0.01", 0, "1", "1", Decimal(10)),
    "TLT": ("data_tlt_hourly.csv", 2, "0.01", 0, "1", "1", Decimal(10)),
    # Sumados 12/08/2026 — candidatos del scanner de oportunidades, validados
    # con probabilidad histórica de ganancia por ventana (ver bitacora_activos.md,
    # entrada "Scanner + validación de probabilidad"). GLD quedó afuera a
    # propósito: es prácticamente el mismo activo que XAU (oro), misma
    # redundancia que ya corregimos con SPY+QQQ. Tamaño de posición ajustado
    # para notional ~US$3.000-3.600 por operación, comparable al resto.
    "JPM":  ("data_jpm_hourly.csv",  2, "0.01", 0, "1", "1", Decimal(10)),
    "BAC":  ("data_bac_hourly.csv",  2, "0.01", 0, "1", "1", Decimal(50)),
    "BLK":  ("data_blk_hourly.csv",  2, "0.01", 0, "1", "1", Decimal(3)),
    "NVDA": ("data_nvda_hourly.csv", 2, "0.01", 0, "1", "1", Decimal(15)),
    "SHOP": ("data_shop_hourly.csv", 2, "0.01", 0, "1", "1", Decimal(20)),
    "NET":  ("data_net_hourly.csv",  2, "0.01", 0, "1", "1", Decimal(10)),
    "SCHW": ("data_schw_hourly.csv", 2, "0.01", 0, "1", "1", Decimal(30)),
}


def make_instrument(symbol: str, price_precision: int, price_increment: str,
                     size_precision: int, size_increment: str, lot_size: str) -> Commodity:
    return Commodity(
        instrument_id=InstrumentId(symbol=Symbol(symbol), venue=SIM),
        raw_symbol=Symbol(symbol),
        asset_class=AssetClass.COMMODITY,
        quote_currency=USD,
        price_precision=price_precision,
        price_increment=Price.from_str(price_increment),
        size_precision=size_precision,
        size_increment=Quantity.from_str(size_increment),
        lot_size=Quantity.from_str(lot_size),
        ts_event=0,
        ts_init=0,
    )


def load_bars(csv_path: str, instrument, bar_type: BarType) -> list[Bar]:
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    bars = []
    for ts, row in df.iterrows():
        ts_ns = int(pd.Timestamp(ts).tz_convert("UTC").value)
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
            trader_id="JARVIS-PORTFOLIO-001",
            logging=LoggingConfig(log_level="ERROR"),
        ),
    )

    engine.add_venue(
        venue=SIM,
        oms_type=OmsType.NETTING,
        account_type=AccountType.MARGIN,
        base_currency=USD,
        starting_balances=[Money(200_000, USD)],
        default_leverage=Decimal(5),
    )

    per_instrument_trades = {}

    for symbol, (csv, pp, pi, sp, si, ls, trade_size) in INSTRUMENTS.items():
        instrument = make_instrument(symbol, pp, pi, sp, si, ls)
        engine.add_instrument(instrument)

        bar_type = BarType.from_str(f"{instrument.id}-1-HOUR-LAST-EXTERNAL")
        bars = load_bars(csv, instrument, bar_type)
        engine.add_data(bars)

        strategy = EMACross(
            config=EMACrossConfig(
                instrument_id=instrument.id,
                bar_type=bar_type,
                trade_size=trade_size,
                fast_ema_period=20,
                slow_ema_period=50,
                request_bars=False,
                subscribe_trade_ticks=False,
                order_id_tag=symbol,
            ),
        )
        engine.add_strategy(strategy)
        per_instrument_trades[symbol] = len(bars)

    engine.run()

    result = engine.get_result()
    print("\n=== PORTFOLIO: XAU + EUR/USD + BTC + SPY + QQQ, EMA 20/50 1H ===")
    print(f"Barras por instrumento: {per_instrument_trades}")
    print(f"Órdenes totales: {result.total_orders}")
    print(f"Posiciones totales: {result.total_positions}")
    print("\n--- PnL combinado (portfolio) ---")
    print(result.stats_pnls)
    print("\n--- Retornos combinados (portfolio) ---")
    print(result.stats_returns)

    print("\n--- Posiciones por instrumento ---")
    pos = engine.trader.generate_positions_report()
    if len(pos):
        pos["symbol"] = pos["instrument_id"].astype(str).str.split(".").str[0]
        summary = pos.groupby("symbol").agg(
            operaciones=("realized_pnl", "count"),
            pnl_total=("realized_pnl", lambda s: s.astype(str).str.replace(" USD", "").astype(float).sum()),
        )
        summary["ganadoras"] = pos.assign(
            pnl_num=pos["realized_pnl"].astype(str).str.replace(" USD", "").astype(float),
        ).groupby("symbol")["pnl_num"].apply(lambda s: (s > 0).sum())
        summary["win_rate_%"] = (summary["ganadoras"] / summary["operaciones"] * 100).round(1)
        print(summary)
    else:
        print("(sin posiciones)")

    print("\n--- Cuenta final ---")
    print(engine.trader.generate_account_report(SIM).tail(1))

    engine.dispose()


if __name__ == "__main__":
    main()
