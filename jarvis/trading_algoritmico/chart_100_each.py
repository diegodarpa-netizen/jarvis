"""
Gráfico: "si hubiésemos puesto US$100 en cada uno de los 5 instrumentos"
usando el RETORNO % real de cada operación (columna `realized_return` que
ya calcula NautilusTrader), no el PnL en dólares crudo — así se saca de
encima la distorsión de tamaño de posición desigual que encontramos en
backtest_portfolio.py, y se ve la diversificación "limpia".

Genera: chart_100_each.png
"""

from decimal import Decimal

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from backtest_portfolio import (
    INSTRUMENTS,
    SIM,
    make_instrument,
    load_bars,
)
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


def run_and_get_positions() -> pd.DataFrame:
    engine = BacktestEngine(
        config=BacktestEngineConfig(trader_id="JARVIS-CHART", logging=LoggingConfig(log_level="ERROR")),
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
    engine.dispose()
    return pos


def main() -> None:
    pos = run_and_get_positions()
    pos["symbol"] = pos["instrument_id"].astype(str).str.split(".").str[0]
    pos = pos.sort_values("ts_closed")

    curves = {}
    for symbol, group in pos.groupby("symbol"):
        equity = [100.0]
        times = [group["ts_opened"].min()]
        for _, row in group.iterrows():
            equity.append(equity[-1] * (1 + row["realized_return"]))
            times.append(row["ts_closed"])
        s = pd.Series(equity, index=pd.to_datetime(times))
        s = s[~s.index.duplicated(keep="last")].sort_index()
        curves[symbol] = s

    # Grilla diaria común para poder sumar las 5 curvas (combinado)
    start = min(s.index.min() for s in curves.values())
    end = max(s.index.max() for s in curves.values())
    grid = pd.date_range(start, end, freq="D")

    aligned = {}
    for symbol, s in curves.items():
        aligned[symbol] = s.reindex(grid.union(s.index)).ffill().reindex(grid).fillna(100.0)

    combined = sum(aligned.values())  # US$500 iniciales -> evolución de la suma

    # --- Gráfico ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9), sharex=True,
                                    gridspec_kw={"height_ratios": [2, 1]})

    colors = {"XAU": "#d4a017", "EUR": "#2a6fbb", "BTC": "#f7931a", "SPY": "#2ca02c", "QQQ": "#8e44ad"}
    for symbol, s in aligned.items():
        ax1.plot(grid, s.values, label=f"{symbol} (US$100 iniciales)", color=colors.get(symbol), linewidth=1.6)
    ax1.axhline(100, color="gray", linewidth=0.8, linestyle="--")
    ax1.set_ylabel("Valor de la posición (US$)")
    ax1.set_title("Si hubiéramos puesto US$100 en cada instrumento — EMA 20/50, 1H, ~2 años")
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(alpha=0.3)

    ax2.plot(grid, combined.values, color="black", linewidth=2, label="Suma de las 5 (US$500 iniciales)")
    ax2.axhline(500, color="gray", linewidth=0.8, linestyle="--")
    ax2.set_ylabel("Portfolio combinado (US$)")
    ax2.set_xlabel("Fecha")
    ax2.legend(loc="upper left", fontsize=9)
    ax2.grid(alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    fig.tight_layout()
    fig.savefig("chart_100_each.png", dpi=150)

    print("=== Valor final de cada US$100 ===")
    for symbol, s in aligned.items():
        print(f"{symbol}: US${s.iloc[-1]:.2f}  ({(s.iloc[-1]/100 - 1)*100:+.1f}%)")
    print(f"\nCombinado (US$500 -> ?): US${combined.iloc[-1]:.2f}  ({(combined.iloc[-1]/500 - 1)*100:+.1f}%)")

    # Volatilidad diaria de cada curva vs. la combinada -> evidencia de diversificación
    print("\n=== Desvío estándar de los retornos diarios (suavidad de la curva) ===")
    for symbol, s in aligned.items():
        print(f"{symbol}: {s.pct_change().std()*100:.3f}%")
    print(f"Combinado: {combined.pct_change().std()*100:.3f}%")
    prom_individual = sum(s.pct_change().std() for s in aligned.values()) / len(aligned)
    print(f"(Promedio de volatilidad individual: {prom_individual*100:.3f}% — si el combinado es menor a esto, SÍ hubo diversificación real)")


if __name__ == "__main__":
    main()
