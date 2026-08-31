"""
Walk-forward de verdad (validación por ventanas, no optimización de
parámetros — los parámetros siguen fijos en 20/50, nunca se tocaron):

Parte el período común a los 5 instrumentos (13/08/2024 -> hoy, ~2 años,
limitado por BTC que es el que tiene menos historia) en 4 ventanas
sucesivas de ~6 meses cada una, y corre la MISMA estrategia con los
MISMOS parámetros en cada ventana por separado.

La pregunta que responde: ¿XAU/TLT/SPY ganan en CADA ventana (edge
real, consistente) o solo ganaron en el agregado de 2 años (pudo ser
racha de régimen en alguna ventana puntual)? Lo mismo para BTC/EUR:
¿perdieron siempre, o hay ventanas donde ganaron y el agregado los
esconde?
"""

from decimal import Decimal

import pandas as pd

from backtest_portfolio import INSTRUMENTS, SIM, make_instrument, load_bars
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


def build_engine() -> BacktestEngine:
    """Crea el motor UNA sola vez (el backend de logging en Rust no admite
    reinicializarse por proceso — reusar el mismo engine entre ventanas,
    limpiando datos/estrategias con reset()/clear_*() en vez de instanciar
    uno nuevo por ventana)."""
    engine = BacktestEngine(
        config=BacktestEngineConfig(trader_id="JARVIS-WF", logging=LoggingConfig(log_level="ERROR")),
    )
    engine.add_venue(
        venue=SIM, oms_type=OmsType.NETTING, account_type=AccountType.MARGIN,
        base_currency=USD, starting_balances=[Money(200_000, USD)], default_leverage=Decimal(5),
    )
    for symbol, (csv, pp, pi, sp, si, ls, trade_size) in INSTRUMENTS.items():
        engine.add_instrument(make_instrument(symbol, pp, pi, sp, si, ls))
    return engine


def run_window(engine: BacktestEngine, bars_by_symbol: dict, window_start, window_end) -> dict:
    """Corre el portfolio completo sobre una ventana de tiempo y devuelve
    el retorno % normalizado (US$100 inicial) por símbolo."""
    for symbol, (csv, pp, pi, sp, si, ls, trade_size) in INSTRUMENTS.items():
        instrument = make_instrument(symbol, pp, pi, sp, si, ls)
        bar_type = BarType.from_str(f"{instrument.id}-1-HOUR-LAST-EXTERNAL")

        all_bars = bars_by_symbol[symbol]
        window_bars = [b for b in all_bars if window_start <= pd.Timestamp(b.ts_event, unit="ns", tz="UTC") <= window_end]
        if len(window_bars) < 60:  # no alcanza ni para calentar la EMA lenta
            continue
        engine.add_data(window_bars)

        strategy = EMACross(
            config=EMACrossConfig(
                instrument_id=instrument.id, bar_type=bar_type, trade_size=trade_size,
                fast_ema_period=20, slow_ema_period=50,
                request_bars=False, subscribe_trade_ticks=False, order_id_tag=symbol,
            ),
        )
        engine.add_strategy(strategy)

    engine.run()
    pos = engine.trader.generate_positions_report()

    returns = {}
    if len(pos):
        pos["symbol"] = pos["instrument_id"].astype(str).str.split(".").str[0]
        for symbol, group in pos.groupby("symbol"):
            equity = 100.0
            for r in group["realized_return"]:
                equity *= (1 + r)
            returns[symbol] = (equity / 100 - 1) * 100  # % return

    # Limpiar para la próxima ventana (venue e instrumentos persisten)
    engine.reset()
    engine.clear_data()
    engine.clear_strategies()
    engine.clear_actors()

    return returns


def main() -> None:
    # Cargar todas las barras una sola vez (con su instrumento "real" para
    # que make_price/make_qty funcionen), reutilizables entre ventanas.
    bars_by_symbol = {}
    for symbol, (csv, pp, pi, sp, si, ls, trade_size) in INSTRUMENTS.items():
        instrument = make_instrument(symbol, pp, pi, sp, si, ls)
        bar_type = BarType.from_str(f"{instrument.id}-1-HOUR-LAST-EXTERNAL")
        bars_by_symbol[symbol] = load_bars(csv, instrument, bar_type)

    # Período común a los 5 (limitado por el que tiene menos historia: BTC)
    starts = [pd.Timestamp(b[0].ts_event, unit="ns", tz="UTC") for b in bars_by_symbol.values()]
    ends = [pd.Timestamp(b[-1].ts_event, unit="ns", tz="UTC") for b in bars_by_symbol.values()]
    common_start, common_end = max(starts), min(ends)
    print(f"Período común: {common_start.date()} -> {common_end.date()}")

    edges = pd.date_range(common_start, common_end, periods=N_WINDOWS + 1)
    engine = build_engine()

    all_results = {}
    for i in range(N_WINDOWS):
        w_start, w_end = edges[i], edges[i + 1]
        print(f"\n=== Ventana {i+1}/{N_WINDOWS}: {w_start.date()} -> {w_end.date()} ===")
        result = run_window(engine, bars_by_symbol, w_start, w_end)
        all_results[f"V{i+1}\n({w_start.date()}\n{w_end.date()})"] = result
        for symbol, ret in sorted(result.items()):
            print(f"  {symbol}: {ret:+.1f}%")

    engine.dispose()

    df = pd.DataFrame(all_results).T
    df = df[["XAU", "TLT", "SPY", "BTC", "EUR"]]
    print("\n=== TABLA COMPLETA: retorno % por instrumento y ventana ===")
    print(df.round(1).to_string())

    print("\n=== ¿Ganó en TODAS las ventanas? ===")
    for symbol in df.columns:
        wins = (df[symbol] > 0).sum()
        print(f"  {symbol}: ganó en {wins}/{N_WINDOWS} ventanas")

    df.to_csv("walk_forward_results.csv")


if __name__ == "__main__":
    main()
