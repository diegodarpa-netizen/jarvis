"""
Mean-reversion con Bandas de Bollinger + VWAP — otra familia distinta a
todo lo que probamos hoy (ni cruce de EMA, ni RSI).

Bollinger Bands(20, 2.0) — parámetros estándar de manual (John Bollinger).
VWAP rolling de 20 barras — NautilusTrader no trae VWAP nativo, se calcula
a mano: suma(close*volumen) / suma(volumen) en la ventana.

Lógica (roles clásicos de cada indicador, no inventados):
- Bollinger marca el extremo (entrada): precio toca la banda inferior/superior.
- VWAP marca el "valor justo" (salida): se cierra la posición cuando el
  precio vuelve al VWAP, en vez de un R fijo o la banda opuesta.

*** REFERENCIA EDUCATIVA — NO ES CONSEJO DE INVERSIÓN. ***
"""

from collections import deque
from decimal import Decimal

from nautilus_trader.config import PositiveInt
from nautilus_trader.config import StrategyConfig
from nautilus_trader.indicators.volatility import BollingerBands
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.trading.strategy import Strategy


class VWAPBollingerConfig(StrategyConfig, frozen=True):
    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    bb_period: PositiveInt = 20
    bb_k: float = 2.0
    vwap_period: PositiveInt = 20


class VWAPBollinger(Strategy):
    def __init__(self, config: VWAPBollingerConfig) -> None:
        super().__init__(config)
        self.instrument: Instrument = None
        self.bb = BollingerBands(config.bb_period, config.bb_k)
        self._pv = deque(maxlen=config.vwap_period)  # (price * volumen)
        self._vol = deque(maxlen=config.vwap_period)

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        if self.instrument is None:
            self.stop()
            return
        self.register_indicator_for_bars(self.config.bar_type, self.bb)
        self.subscribe_bars(self.config.bar_type)

    def _vwap(self) -> float:
        if not self._vol or sum(self._vol) == 0:
            return None
        return sum(self._pv) / sum(self._vol)

    def on_bar(self, bar: Bar) -> None:
        close = bar.close.as_double()
        volume = bar.volume.as_double()
        self._pv.append(close * volume)
        self._vol.append(volume)

        if not self.bb.initialized or len(self._vol) < self.config.vwap_period:
            return
        if bar.is_single_price():
            return

        vwap = self._vwap()
        if vwap is None:
            return

        flat = self.portfolio.is_flat(self.config.instrument_id)
        long_pos = self.portfolio.is_net_long(self.config.instrument_id)
        short_pos = self.portfolio.is_net_short(self.config.instrument_id)

        # Entrada: Bollinger marca el extremo
        if flat:
            if close <= self.bb.lower:
                self._order(OrderSide.BUY)
            elif close >= self.bb.upper:
                self._order(OrderSide.SELL)
        # Salida: vuelta al "valor justo" (VWAP)
        elif long_pos and close >= vwap:
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
        self.bb.reset()
        self._pv.clear()
        self._vol.clear()
