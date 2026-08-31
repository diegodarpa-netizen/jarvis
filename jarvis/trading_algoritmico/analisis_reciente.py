"""
Foto de "dónde estamos parados ahora" — últimas semanas, 1 mes, 3 meses,
6 meses, 1 año. Estrategia (EMA 20/50) vs. comprar-y-mantener, en SPY y
XAU, más el indicador de régimen (Efficiency Ratio) para ver si el
mercado actual se parece más a una tendencia limpia (2008) o a un
mercado picado (2022) — la pregunta que decide si la cobertura debería
estar activada hoy.
"""

from decimal import Decimal

import pandas as pd

from backtest_portfolio import INSTRUMENTS, SIM, make_instrument
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import BacktestEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.examples.strategies.ema_cross import EMACross
from nautilus_trader.examples.strategies.ema_cross import EMACrossConfig
from nautilus_trader.indicators.momentum import EfficiencyRatio
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.objects import Money

VENTANAS = {"1 semana": 7, "1 mes": 30, "3 meses": 90, "6 meses": 182, "1 año": 365}
ACTIVOS = {"SPY": "data_spy_daily_max.csv", "XAU": "data_xau_daily_15y.csv"}


def load_daily(csv_path, instrument, bar_type, start=None):
    df = pd.read_csv(csv_path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    if start is not None:
        df = df[df.index >= start]
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
    engine = BacktestEngine(config=BacktestEngineConfig(trader_id="JARVIS-RECIENTE", logging=LoggingConfig(log_level="ERROR")))
    engine.add_venue(venue=SIM, oms_type=OmsType.NETTING, account_type=AccountType.MARGIN,
                      base_currency=USD, starting_balances=[Money(200_000, USD)], default_leverage=Decimal(5))
    for symbol in ACTIVOS:
        csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS[symbol]
        engine.add_instrument(make_instrument(symbol, pp, pi, sp, si, ls))
    return engine


def main():
    engine = build_engine()
    hoy = pd.Timestamp.now(tz="UTC")

    print(f"\n{'='*72}\n  FOTO ACTUAL — Estrategia vs. Comprar y mantener, ventanas recientes\n{'='*72}")

    for symbol in ACTIVOS:
        csv, pp, pi, sp, si, ls, trade_size = INSTRUMENTS[symbol]
        instrument = make_instrument(symbol, pp, pi, sp, si, ls)
        bar_type = BarType.from_str(f"{instrument.id}-1-DAY-LAST-EXTERNAL")
        # 3 años de colchón para que la EMA y el ER estén bien calentados
        bars, raw_df = load_daily(ACTIVOS[symbol], instrument, bar_type, start=hoy - pd.Timedelta(days=365 * 3))

        engine.add_data(bars)
        strategy = EMACross(config=EMACrossConfig(
            instrument_id=instrument.id, bar_type=bar_type, trade_size=trade_size,
            fast_ema_period=20, slow_ema_period=50, request_bars=False, subscribe_trade_ticks=False,
        ))
        engine.add_strategy(strategy)
        engine.run()
        pos = engine.trader.generate_positions_report()
        engine.reset(); engine.clear_data(); engine.clear_strategies(); engine.clear_actors()

        # Indicador de régimen actual (Efficiency Ratio, período 20) sobre el cierre de los datos
        er = EfficiencyRatio(20)
        for close in raw_df["Close"].tail(60):
            er.update_raw(close)
        regimen = "TENDENCIA" if er.value >= 0.30 else "MERCADO PICADO / sin tendencia clara"

        print(f"\n--- {symbol} --- (Efficiency Ratio actual: {er.value:.2f} -> {regimen})")
        for label, days in VENTANAS.items():
            w_start = pd.Timestamp(raw_df.index.max()) - pd.Timedelta(days=days)
            w_end = pd.Timestamp(raw_df.index.max())

            strat_return = None
            if len(pos):
                pos_w = pos[(pos["ts_closed"] >= w_start) & (pos["ts_closed"] <= w_end)]
                if len(pos_w):
                    eq = 100.0
                    for r in pos_w["realized_return"]:
                        eq *= (1 + r)
                    strat_return = (eq / 100 - 1) * 100

            window_df = raw_df[(raw_df.index >= w_start) & (raw_df.index <= w_end)]
            bh_return = (window_df["Close"].iloc[-1] / window_df["Close"].iloc[0] - 1) * 100 if len(window_df) > 1 else None

            strat_txt = f"{strat_return:+6.1f}%" if strat_return is not None else "sin operaciones"
            bh_txt = f"{bh_return:+6.1f}%" if bh_return is not None else "s/d"
            print(f"  {label:8}: Estrategia {strat_txt:>16}  |  Comprar y mantener {bh_txt}")

    engine.dispose()


if __name__ == "__main__":
    main()
