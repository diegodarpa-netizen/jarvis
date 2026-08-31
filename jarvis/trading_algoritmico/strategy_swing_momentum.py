"""
Estrategia de swing "momentum + salud técnica", para usar con
walk_forward_harness.py — retoma la metodología del research de equities
swing de 03/08/2026 (ver memoria project_swing_trading_equities), esta vez
con walk-forward real en vez de un solo backtest estático.

Criterio de entrada (largo únicamente — no se opera corto, es un setup de
continuación alcista, no simétrico):
  1. Momentum de 10 ruedas positivo y por encima de un piso mínimo.
  2. RSI(14) en zona sana (50-70): impulso alcista sin estar ya sobrecomprado.
  3. Precio a menos de X% del máximo de las últimas 20 ruedas (cerca de
     máximos, no en medio de un rango).
  4. Volumen relativo por encima del promedio de 20 ruedas (confirma interés,
     no un movimiento de baja convicción).

Salida: stop en entry - 1.5×ATR(14), target en entry + 2.5R (R = distancia
al stop) — mismo money management ya validado con Diego (riesgo 1%/trade,
tope 10% de concentración; ESO se aplica en el sizing real, no en esta
función, que solo devuelve la señal direccional {-1,0,1}).

Parámetros fijos de manual (RSI 14, umbrales 50/70, ATR 14, stop 1.5×ATR,
target 2.5R) — igual que el resto del proyecto, no se ajustan mirando el
resultado de este mismo backtest.

*** REFERENCIA DE INVESTIGACIÓN — NO ES CONSEJO DE INVERSIÓN. ***
"""
import numpy as np
import pandas as pd


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()


def strategy_swing_momentum(
    df: pd.DataFrame,
    mom_period: int = 10,
    mom_min: float = 0.0,
    rsi_period: int = 14,
    rsi_low: float = 50.0,
    rsi_high: float = 70.0,
    near_high_period: int = 20,
    near_high_pct: float = 0.05,
    vol_period: int = 20,
    vol_mult: float = 1.2,
    atr_period: int = 14,
    atr_stop_mult: float = 1.5,
    target_r: float = 2.5,
) -> pd.Series:
    """Espera un DataFrame con columnas close/high/low/volume, índice
    datetime. Devuelve una Serie {0,1} (solo largo) alineada al índice."""
    momentum = df["close"].pct_change(mom_period)
    rsi_vals = rsi(df["close"], rsi_period)
    rolling_high = df["high"].rolling(near_high_period).max()
    distance_to_high = (rolling_high - df["close"]) / rolling_high
    avg_volume = df["volume"].rolling(vol_period).mean()
    rel_volume = df["volume"] / avg_volume
    atr_vals = atr(df, atr_period)

    entry_signal = (
        (momentum > mom_min)
        & (rsi_vals >= rsi_low) & (rsi_vals <= rsi_high)
        & (distance_to_high <= near_high_pct)
        & (rel_volume >= vol_mult)
    ).fillna(False)

    positions = pd.Series(0, index=df.index)
    in_position = False
    stop_price = target_price = None

    for i in range(len(df)):
        close = df["close"].iloc[i]
        high = df["high"].iloc[i]
        low = df["low"].iloc[i]

        if in_position:
            if low <= stop_price or high >= target_price:
                in_position = False
                stop_price = target_price = None
            else:
                positions.iloc[i] = 1
                continue

        if not in_position and entry_signal.iloc[i] and not np.isnan(atr_vals.iloc[i]) and atr_vals.iloc[i] > 0:
            in_position = True
            stop_price = close - atr_stop_mult * atr_vals.iloc[i]
            target_price = close + atr_stop_mult * atr_vals.iloc[i] * target_r
            positions.iloc[i] = 1

    return positions
