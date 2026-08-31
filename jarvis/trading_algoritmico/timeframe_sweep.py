"""
Barrido de timeframe × activo — MISMA estrategia (EMA 20/50), MISMOS
parámetros fijos, sobre 5 activos (XAU=futuros, EUR=divisas, BTC=cripto,
SPY=acciones, TLT=renta fija) y 3 timeframes (1H, 4H, 1D).

Objetivo: encontrar si hay una combinación timeframe/activo donde esta
estrategia tenga edge real — mostrando la TABLA COMPLETA (15 combinaciones),
no solo la que ganó, para no repetir el error de elegir con el diario
del lunes. Cualquier combinación que se vea bien acá TODAVÍA necesita
walk-forward antes de confiar en ella — esto es solo el paso de barrido,
no la validación.

"Opciones" queda fuera — necesita datos de cadenas de opciones/IV,
infraestructura distinta a esto.
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
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money

from backtest_portfolio import INSTRUMENTS, make_instrument

SIM = Venue("SIM")

# Fuente de datos por timeframe: 1H y 1D vienen de CSVs propios; 4H se arma
# resampleando el CSV de 1H (mismo dato fuente, distinta agregación).
TIMEFRAMES = {
    "1H": {"suffix": "hourly", "bar_str": "1-HOUR", "resample": None},
    "4H": {"suffix": "hourly", "bar_str": "4-HOUR", "resample": "4h"},
    "1D": {"suffix": "daily", "bar_str": "1-DAY", "resample": None},
}

CSV_MAP = {
    "XAU": {"hourly": "data_xau_hourly.csv", "daily": None},  # no hay XAU daily separado -> se resamplea de 1H
    "EUR": {"hourly": "data_eurusd_hourly.csv", "daily": "data_eurusd_daily.csv"},
    "BTC": {"hourly": "data_btc_hourly.csv", "daily": "data_btc_daily.csv"},
    "SPY": {"hourly": "data_spy_hourly.csv", "daily": "data_spy_daily.csv"},
    "TLT": {"hourly": "data_tlt_hourly.csv", "daily": "data_tlt_daily.csv"},
}


def load_and_resample(symbol: str, tf_key: str, instrument, bar_type: BarType) -> list[Bar]:
    tf = TIMEFRAMES[tf_key]
    csv_key = tf["suffix"]
    csv_path = CSV_MAP[symbol].get(csv_key)

    if csv_path is None:
        # No hay XAU daily propio -> resamplear desde el hourly
        df = pd.read_csv(CSV_MAP[symbol]["hourly"], index_col=0)
        df.index = pd.to_datetime(df.index, utc=True)
        df = df.resample("1D").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}).dropna()
    else:
        df = pd.read_csv(csv_path, index_col=0)
        df.index = pd.to_datetime(df.index, utc=True)
        if tf["resample"]:
            df = df.resample(tf["resample"]).agg({"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}).dropna()

    # Saneo de OHLC: yfinance a veces entrega barras diarias/resampleadas con
    # high/low que no encierran correctamente open/close (más común en forex
    # diario, por gaps de fin de semana). NautilusTrader rechaza esas barras.
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
    return bars


def build_engine() -> BacktestEngine:
    """Motor único reutilizado entre corridas — el backend de logging en Rust
    no admite reinicializarse por proceso (ver walk_forward_portfolio.py)."""
    engine = BacktestEngine(config=BacktestEngineConfig(trader_id="JARVIS-SWEEP", logging=LoggingConfig(log_level="ERROR")))
    engine.add_venue(venue=SIM, oms_type=OmsType.NETTING, account_type=AccountType.MARGIN,
                      base_currency=USD, starting_balances=[Money(200_000, USD)], default_leverage=Decimal(5))
    for symbol in INSTRUMENTS:
        csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS[symbol]
        engine.add_instrument(make_instrument(symbol, pp, pi, sp, si, ls))
    return engine


def run_one(engine: BacktestEngine, symbol: str, tf_key: str) -> dict:
    csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS[symbol]
    instrument = make_instrument(symbol, pp, pi, sp, si, ls)
    bar_type = BarType.from_str(f"{instrument.id}-{TIMEFRAMES[tf_key]['bar_str']}-LAST-EXTERNAL")
    bars = load_and_resample(symbol, tf_key, instrument, bar_type)
    if len(bars) < 60:
        return {"trades": 0, "return_pct": 0.0, "note": "datos insuficientes"}

    engine.add_data(bars)
    strategy = EMACross(config=EMACrossConfig(
        instrument_id=instrument.id, bar_type=bar_type, trade_size=trade_size,
        fast_ema_period=20, slow_ema_period=50, request_bars=False, subscribe_trade_ticks=False,
    ))
    engine.add_strategy(strategy)
    engine.run()

    pos = engine.trader.generate_positions_report()

    engine.reset()
    engine.clear_data()
    engine.clear_strategies()
    engine.clear_actors()

    if not len(pos):
        return {"trades": 0, "return_pct": 0.0}

    equity = 100.0
    wins = 0
    for r in pos["realized_return"]:
        equity *= (1 + r)
        if r > 0:
            wins += 1
    return {
        "trades": len(pos),
        "return_pct": round((equity / 100 - 1) * 100, 1),
        "win_rate": round(wins / len(pos) * 100, 1),
    }


def main() -> None:
    engine = build_engine()
    rows = []
    for symbol in INSTRUMENTS:
        for tf_key in TIMEFRAMES:
            result = run_one(engine, symbol, tf_key)
            rows.append({"Activo": symbol, "Timeframe": tf_key, **result})
            print(f"{symbol:5} {tf_key:4}  →  {result}")
    engine.dispose()

    df = pd.DataFrame(rows)
    pivot_ret = df.pivot(index="Activo", columns="Timeframe", values="return_pct")
    pivot_trades = df.pivot(index="Activo", columns="Timeframe", values="trades")

    print("\n=== TABLA COMPLETA — Retorno % (US$100 inicial) ===")
    print(pivot_ret.to_string())
    print("\n=== TABLA COMPLETA — Cantidad de operaciones ===")
    print(pivot_trades.to_string())

    df.to_csv("timeframe_sweep_results.csv", index=False)


if __name__ == "__main__":
    main()
