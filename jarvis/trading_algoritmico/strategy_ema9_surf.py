"""
Estrategia propia de Diego (no es de manual) — "surfear" la EMA 9.

Regla, tal como la describió el 14/08/2026:
  1. Una vela "toca/cruza" la EMA 9 si el rango de la vela (low-high)
     incluye el valor de la EMA (low <= ema <= high).
  2. Una vela "surfea" la EMA si NO la toca: queda entera arriba
     (low > ema, surf alcista) o entera abajo (high < ema, surf bajista).
  3. Entrada: cuando una vela TOCA la EMA y la vela SIGUIENTE surfea limpio
     (arriba o abajo) → se entra compra o venta según el lado que surfeó.
  4. Continuidad: mientras las velas siguientes sigan surfeando DEL MISMO
     LADO (misma tendencia de la entrada), se mantiene la posición.
  5. Salida: en cuanto una vela TOCA la EMA, se sale. Esa misma vela que
     tocó pasa a ser el nuevo "setup" — si la vela de después vuelve a
     surfear, ahí se re-entra (mismo mecanismo del punto 3).

**Corrección 14/08/2026 (bug encontrado al backtestear):** con velas
diarias puede pasar que el precio pase de surfear un lado al otro SIN que
ninguna vela puntual llegue a tocar la EMA en el medio (la EMA también se
mueve día a día) — un "salto limpio" de lado. La primera versión de este
código interpretaba el punto 5 de forma demasiado literal ("mientras no
toque, seguir") y esto la dejaba OPERANDO EN CONTRA DE LA TENDENCIA un mes
entero (vendida surfeando el oro subiendo, sin ningún toque que la sacara).
Se corrige: un salto limpio al lado contrario también cierra la posición
(y funciona como la propia vela de confirmación de una entrada nueva en el
sentido nuevo) — es la lectura que hace consistente el punto 4 ("tiene que
seguir la MISMA tendencia") con el punto 5. Si esta interpretación no es la
que Diego tenía en mente, avisar para ajustarla.

*** IDEA PROPIA DE DIEGO — REFERENCIA DE INVESTIGACIÓN, NO ES CONSEJO DE
INVERSIÓN. ***
"""
import numpy as np
import pandas as pd


def ema(close: pd.Series, period: int = 9) -> pd.Series:
    return close.ewm(span=period, min_periods=period, adjust=False).mean()


def strategy_ema9_surf(df: pd.DataFrame, ema_period: int = 9) -> pd.Series:
    """Espera columnas close/high/low. Devuelve posición {-1,0,1} alineada
    al índice — la usa walk_forward_harness.py tal cual (position.shift(1)
    aplicado al retorno del período siguiente, ver ese archivo)."""
    ema_vals = ema(df["close"], ema_period)
    touches = (df["low"] <= ema_vals) & (ema_vals <= df["high"])
    surf_bull = df["low"] > ema_vals
    surf_bear = df["high"] < ema_vals

    positions = pd.Series(0, index=df.index)
    in_position = False
    direction = 0

    for i in range(1, len(df)):
        if np.isnan(ema_vals.iloc[i]):
            continue

        salto_limpio_contrario = False
        if in_position:
            sigue_mismo_lado = (direction == 1 and surf_bull.iloc[i]) or (direction == -1 and surf_bear.iloc[i])
            if sigue_mismo_lado:
                positions.iloc[i] = direction
                continue
            # o tocó, o saltó limpio al lado contrario -- en ambos casos se sale
            in_position = False
            direction = 0
            salto_limpio_contrario = not touches.iloc[i] and (surf_bull.iloc[i] or surf_bear.iloc[i])

        if not in_position:
            setup_previo = touches.iloc[i - 1] or salto_limpio_contrario
            if setup_previo and surf_bull.iloc[i]:
                in_position = True
                direction = 1
                positions.iloc[i] = 1
            elif setup_previo and surf_bear.iloc[i]:
                in_position = True
                direction = -1
                positions.iloc[i] = -1

    return positions
