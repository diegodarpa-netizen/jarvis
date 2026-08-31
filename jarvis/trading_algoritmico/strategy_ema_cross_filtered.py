"""
Mismo cruce de EMA de siempre, pero con un FILTRO DE TENDENCIA (Efficiency
Ratio de Perry Kaufman) — solo opera cuando el mercado está realmente
tendiendo, no en cualquier momento. Ver knowledge/filtros_de_tendencia.md.

Efficiency Ratio: 0 a 1. Cerca de 1 = movimiento eficiente/derecho
(tendencia limpia). Cerca de 0 = precio va y viene sin progreso neto
(mercado picado/rango) — ahí NO se opera, aunque la EMA cruce.

Umbral elegido (0.30): el valor de referencia más citado en la literatura
de Kaufman para separar "hay tendencia" de "ruido". No se ajustó mirando
los resultados de este backtest — sería la misma trampa de siempre.
"""

from decimal import Decimal

from nautilus_trader.common.enums import LogColor
from nautilus_trader.config import PositiveInt
from nautilus_trader.config import StrategyConfig
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.indicators.averages import ExponentialMovingAverage
from nautilus_trader.indicators.momentum import EfficiencyRatio
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Quantity
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.trading.strategy import Strategy


class EMACrossFilteredConfig(StrategyConfig, frozen=True):
    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    fast_ema_period: PositiveInt = 20
    slow_ema_period: PositiveInt = 50
    er_period: PositiveInt = 20
    er_threshold: float = 0.30


class EMACrossFiltered(Strategy):
    """
    Cruce de EMA clásico + filtro de tendencia (Efficiency Ratio).

    *** ESTRATEGIA DE REFERENCIA CON FINES EDUCATIVOS — NO ES CONSEJO DE INVERSIÓN. ***
    """

    def __init__(self, config: EMACrossFilteredConfig) -> None:
        PyCondition.is_true(
            config.fast_ema_period < config.slow_ema_period,
            "fast_ema_period debe ser menor a slow_ema_period",
        )
        super().__init__(config)
        self.instrument: Instrument = None
        self.fast_ema = ExponentialMovingAverage(config.fast_ema_period)
        self.slow_ema = ExponentialMovingAverage(config.slow_ema_period)
        self.trend_filter = EfficiencyRatio(config.er_period)

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        if self.instrument is None:
            self.log.error(f"No se encontró el instrumento {self.config.instrument_id}")
            self.stop()
            return

        self.register_indicator_for_bars(self.config.bar_type, self.fast_ema)
        self.register_indicator_for_bars(self.config.bar_type, self.slow_ema)
        self.register_indicator_for_bars(self.config.bar_type, self.trend_filter)

        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        trending = self.trend_filter.value >= self.config.er_threshold

        if not trending:
            return  # Mercado en rango: no operar, aunque la EMA cruce

        if self.fast_ema.value >= self.slow_ema.value:
            if self.portfolio.is_flat(self.config.instrument_id):
                self._buy()
            elif self.portfolio.is_net_short(self.config.instrument_id):
                self.close_all_positions(self.config.instrument_id)
                self._buy()
        elif self.fast_ema.value < self.slow_ema.value:
            if self.portfolio.is_flat(self.config.instrument_id):
                self._sell()
            elif self.portfolio.is_net_long(self.config.instrument_id):
                self.close_all_positions(self.config.instrument_id)
                self._sell()

    def _buy(self) -> None:
        order: MarketOrder = self.order_factory.market(
            instrument_id=self.config.instrument_id,
            order_side=OrderSide.BUY,
            quantity=self.instrument.make_qty(self.config.trade_size),
            time_in_force=TimeInForce.GTC,
        )
        self.submit_order(order)

    def _sell(self) -> None:
        order: MarketOrder = self.order_factory.market(
            instrument_id=self.config.instrument_id,
            order_side=OrderSide.SELL,
            quantity=self.instrument.make_qty(self.config.trade_size),
            time_in_force=TimeInForce.GTC,
        )
        self.submit_order(order)

    def on_stop(self) -> None:
        self.cancel_all_orders(self.config.instrument_id)
        self.close_all_positions(self.config.instrument_id)

    def on_reset(self) -> None:
        self.fast_ema.reset()
        self.slow_ema.reset()
        self.trend_filter.reset()
