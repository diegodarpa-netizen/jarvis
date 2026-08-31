"""
Estrategia combinada por régimen — no es "probar mezclas hasta que guste",
es la combinación que ya investigamos y decidimos con criterio:

- Efficiency Ratio(20) >= 0.30 -> HAY TENDENCIA -> usar cruce de EMA(20/50)
  (funcionó en 2008, en caídas sostenidas — knowledge/filtros_de_tendencia.md)
- Efficiency Ratio(20) <  0.30 -> MERCADO EN RANGO -> usar Bollinger(20,2) +
  VWAP(20) (le ganó a comprar-y-mantener en XAU 2014-2019, un mercado sin
  tendencia clara — bitácora 12/08/2026)

Cada posición recuerda bajo qué régimen entró, y usa la lógica de salida
de ESE régimen (no cambia de criterio a mitad de operación).

*** REFERENCIA EDUCATIVA — NO ES CONSEJO DE INVERSIÓN. ***
"""

from collections import deque
from decimal import Decimal

from nautilus_trader.config import PositiveInt
from nautilus_trader.config import StrategyConfig
from nautilus_trader.indicators.averages import ExponentialMovingAverage
from nautilus_trader.indicators.momentum import EfficiencyRatio
from nautilus_trader.indicators.volatility import BollingerBands
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.trading.strategy import Strategy


class RegimeSwitchConfig(StrategyConfig, frozen=True):
    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    fast_ema_period: PositiveInt = 20
    slow_ema_period: PositiveInt = 50
    er_period: PositiveInt = 20
    er_threshold: float = 0.30
    bb_period: PositiveInt = 20
    bb_k: float = 2.0
    vwap_period: PositiveInt = 20


class RegimeSwitch(Strategy):
    def __init__(self, config: RegimeSwitchConfig) -> None:
        super().__init__(config)
        self.instrument: Instrument = None
        self.fast_ema = ExponentialMovingAverage(config.fast_ema_period)
        self.slow_ema = ExponentialMovingAverage(config.slow_ema_period)
        self.er = EfficiencyRatio(config.er_period)
        self.bb = BollingerBands(config.bb_period, config.bb_k)
        self._pv = deque(maxlen=config.vwap_period)
        self._vol = deque(maxlen=config.vwap_period)
        self._entry_mode = None  # "trend" | "reversion" | None

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        if self.instrument is None:
            self.stop()
            return
        for ind in (self.fast_ema, self.slow_ema, self.er, self.bb):
            self.register_indicator_for_bars(self.config.bar_type, ind)
        self.subscribe_bars(self.config.bar_type)

    def _vwap(self):
        if not self._vol or sum(self._vol) == 0:
            return None
        return sum(self._pv) / sum(self._vol)

    def on_bar(self, bar: Bar) -> None:
        close = bar.close.as_double()
        self._pv.append(close * bar.volume.as_double())
        self._vol.append(bar.volume.as_double())

        if not self.indicators_initialized() or len(self._vol) < self.config.vwap_period:
            return
        if bar.is_single_price():
            return

        trending = self.er.value >= self.config.er_threshold
        flat = self.portfolio.is_flat(self.config.instrument_id)
        long_pos = self.portfolio.is_net_long(self.config.instrument_id)
        short_pos = self.portfolio.is_net_short(self.config.instrument_id)

        if flat:
            self._entry_mode = None
            if trending:
                if self.fast_ema.value >= self.slow_ema.value:
                    self._order(OrderSide.BUY); self._entry_mode = "trend"
                else:
                    self._order(OrderSide.SELL); self._entry_mode = "trend"
            else:
                if close <= self.bb.lower:
                    self._order(OrderSide.BUY); self._entry_mode = "reversion"
                elif close >= self.bb.upper:
                    self._order(OrderSide.SELL); self._entry_mode = "reversion"
            return

        # Salida: según el régimen bajo el que se entró (no el actual)
        if self._entry_mode == "trend":
            if long_pos and self.fast_ema.value < self.slow_ema.value:
                self.close_all_positions(self.config.instrument_id)
            elif short_pos and self.fast_ema.value >= self.slow_ema.value:
                self.close_all_positions(self.config.instrument_id)
        elif self._entry_mode == "reversion":
            vwap = self._vwap()
            if vwap is not None:
                if long_pos and close >= vwap:
                    self.close_all_positions(self.config.instrument_id)
                elif short_pos and close <= vwap:
                    self.close_all_positions(self.config.instrument_id)

    def _order(self, side: OrderSide) -> None:
        order: MarketOrder = self.order_factory.market(
            instrument_id=self.config.instrument_id, order_side=side,
            quantity=self.instrument.make_qty(self.config.trade_size), time_in_force=TimeInForce.GTC,
        )
        self.submit_order(order)

    def on_stop(self) -> None:
        self.close_all_positions(self.config.instrument_id)

    def on_reset(self) -> None:
        self.fast_ema.reset(); self.slow_ema.reset(); self.er.reset(); self.bb.reset()
        self._pv.clear(); self._vol.clear(); self._entry_mode = None
