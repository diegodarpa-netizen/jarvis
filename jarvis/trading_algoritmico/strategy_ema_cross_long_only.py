"""
Versión SOLO-LARGA del cruce de EMA: compra en señal alcista, y en señal
bajista CIERRA la posición y queda en efectivo — nunca va corto.

Hipótesis a probar (ver bitacora_activos.md, 12/08/2026): en activos con
tendencia secular fuerte (SPY, NVDA, SHOP, NET, BLK, SCHW), ir corto
periódicamente apuesta contra la tendencia de fondo y arruina el resultado.
Sacar el lado corto podría acercar el resultado al de comprar-y-mantener,
sin perder la disciplina de salir en tramos bajistas.
"""

from decimal import Decimal

from nautilus_trader.config import PositiveInt
from nautilus_trader.config import StrategyConfig
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.indicators.averages import ExponentialMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.trading.strategy import Strategy


class EMACrossLongOnlyConfig(StrategyConfig, frozen=True):
    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    fast_ema_period: PositiveInt = 20
    slow_ema_period: PositiveInt = 50


class EMACrossLongOnly(Strategy):
    """*** ESTRATEGIA DE REFERENCIA CON FINES EDUCATIVOS — NO ES CONSEJO DE INVERSIÓN. ***"""

    def __init__(self, config: EMACrossLongOnlyConfig) -> None:
        PyCondition.is_true(config.fast_ema_period < config.slow_ema_period, "fast < slow")
        super().__init__(config)
        self.instrument: Instrument = None
        self.fast_ema = ExponentialMovingAverage(config.fast_ema_period)
        self.slow_ema = ExponentialMovingAverage(config.slow_ema_period)

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        if self.instrument is None:
            self.stop()
            return
        self.register_indicator_for_bars(self.config.bar_type, self.fast_ema)
        self.register_indicator_for_bars(self.config.bar_type, self.slow_ema)
        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return
        if bar.is_single_price():
            return

        bullish = self.fast_ema.value >= self.slow_ema.value

        if bullish and self.portfolio.is_flat(self.config.instrument_id):
            order: MarketOrder = self.order_factory.market(
                instrument_id=self.config.instrument_id, order_side=OrderSide.BUY,
                quantity=self.instrument.make_qty(self.config.trade_size), time_in_force=TimeInForce.GTC,
            )
            self.submit_order(order)
        elif not bullish and self.portfolio.is_net_long(self.config.instrument_id):
            # Señal bajista: cerrar y quedar en efectivo. NUNCA abrir corto.
            self.close_all_positions(self.config.instrument_id)

    def on_stop(self) -> None:
        self.close_all_positions(self.config.instrument_id)

    def on_reset(self) -> None:
        self.fast_ema.reset()
        self.slow_ema.reset()
