"""
Mean-reversion clásica con RSI — la versión de manual, sin ajustar.

RSI(14), umbrales 70/30 — los valores estándar de cualquier libro de
texto sobre RSI (Wilder, el creador del indicador). Compra cuando el
mercado está sobrevendido (RSI<30), vende/corto cuando está sobrecomprado
(RSI>70). Simétrica, igual que el EMA cross que ya probamos — para que
la comparación sea justa (misma disciplina, otra familia de estrategia).

*** REFERENCIA EDUCATIVA — NO ES CONSEJO DE INVERSIÓN. ***
"""

from decimal import Decimal

from nautilus_trader.config import PositiveInt
from nautilus_trader.config import StrategyConfig
from nautilus_trader.indicators.momentum import RelativeStrengthIndex
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.trading.strategy import Strategy


class RSIMeanReversionConfig(StrategyConfig, frozen=True):
    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    rsi_period: PositiveInt = 14
    oversold: float = 30.0
    overbought: float = 70.0


class RSIMeanReversion(Strategy):
    def __init__(self, config: RSIMeanReversionConfig) -> None:
        super().__init__(config)
        self.instrument: Instrument = None
        self.rsi = RelativeStrengthIndex(config.rsi_period)

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        if self.instrument is None:
            self.stop()
            return
        self.register_indicator_for_bars(self.config.bar_type, self.rsi)
        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        rsi = self.rsi.value

        if rsi < self.config.oversold:
            if self.portfolio.is_flat(self.config.instrument_id):
                self._order(OrderSide.BUY)
            elif self.portfolio.is_net_short(self.config.instrument_id):
                self.close_all_positions(self.config.instrument_id)
                self._order(OrderSide.BUY)
        elif rsi > self.config.overbought:
            if self.portfolio.is_flat(self.config.instrument_id):
                self._order(OrderSide.SELL)
            elif self.portfolio.is_net_long(self.config.instrument_id):
                self.close_all_positions(self.config.instrument_id)
                self._order(OrderSide.SELL)

    def _order(self, side: OrderSide) -> None:
        order: MarketOrder = self.order_factory.market(
            instrument_id=self.config.instrument_id, order_side=side,
            quantity=self.instrument.make_qty(self.config.trade_size), time_in_force=TimeInForce.GTC,
        )
        self.submit_order(order)

    def on_stop(self) -> None:
        self.close_all_positions(self.config.instrument_id)

    def on_reset(self) -> None:
        self.rsi.reset()
