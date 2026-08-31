"""
Infraestructura reutilizable de walk-forward -- PREPARADA, no corrida para
sacar conclusiones todavia (ver conversacion 14/08/2026: primero se prepara
el codigo, recien despues -- cuando haya mas historia o se decida
explicitamente que 6 meses alcanza como primer paso preliminar -- se corre
para interpretar resultados).

Sigue el proceso de knowledge/proceso_prueba_estrategias.md:
  1. Parametros FIJOS, nunca reoptimizados mirando el resultado.
  2. Ventanas secuenciales (walk-forward), no un solo numero agregado.
  3. Comparacion contra comprar-y-mantener en la MISMA ventana.
  4. Reporte por ventana, no solo el promedio.

Uso: importar `walk_forward` y pasarle una funcion de estrategia. Cada
funcion de estrategia recibe un DataFrame de precios (con columna 'close',
indice datetime) y devuelve una Serie de posiciones {-1, 0, 1} alineada al
mismo indice -- 1 = largo, -1 = corto, 0 = afuera. El harness se encarga de
partir en ventanas, calcular retornos y comparar contra buy-and-hold.
"""
import pandas as pd
import numpy as np


def make_windows(df: pd.DataFrame, n_windows: int):
    """Parte el DataFrame en n_windows tramos secuenciales de igual tamano
    (por cantidad de barras, no por fecha calendario)."""
    n = len(df)
    size = n // n_windows
    windows = []
    for i in range(n_windows):
        start = i * size
        end = (i + 1) * size if i < n_windows - 1 else n
        windows.append(df.iloc[start:end])
    return windows


def strategy_returns(df: pd.DataFrame, positions: pd.Series, cost_bps=0.0):
    """Retorno de la estrategia dado un DataFrame de precios y una serie de
    posiciones {-1,0,1}. cost_bps = costo de transaccion en basis points por
    cambio de posicion (0 por defecto -- se puede sumar despues)."""
    ret = df['close'].pct_change().fillna(0)
    pos = positions.reindex(df.index).fillna(0)
    strat_ret = pos.shift(1).fillna(0) * ret
    if cost_bps > 0:
        turnover = pos.diff().abs().fillna(0)
        strat_ret -= turnover * (cost_bps / 10000.0)
    return strat_ret


def buy_hold_returns(df: pd.DataFrame):
    return df['close'].pct_change().fillna(0)


def window_stats(returns: pd.Series, label: str):
    total_ret = (1 + returns).prod() - 1
    n = len(returns)
    sharpe = (returns.mean() / returns.std() * np.sqrt(252 * (n / max(1, n)))) if returns.std() > 0 else 0.0
    # Sharpe simplificado -- anualizacion real depende de la frecuencia de las barras,
    # se deja como comparativo relativo entre estrategia y buy-hold, no como numero absoluto final.
    n_trades = int((returns != 0).sum())
    win_rate = float((returns[returns != 0] > 0).mean()) if n_trades > 0 else float('nan')
    return {
        'label': label,
        'retorno_total_%': round(total_ret * 100, 3),
        'n_barras_con_movimiento': n_trades,
        'win_rate_%': round(win_rate * 100, 2) if not np.isnan(win_rate) else None,
    }


def walk_forward(df: pd.DataFrame, strategy_fn, n_windows: int, strategy_name: str, cost_bps=0.0, verbose=True):
    """Corre `strategy_fn` (parametros ya fijos adentro de la funcion) sobre
    cada ventana secuencial y compara contra buy-and-hold en la misma
    ventana. Devuelve una lista de dicts, uno por ventana, con ambos
    resultados -- no promedia nada solo, para forzar mirar ventana por
    ventana (la leccion de TLT: agregado != consistencia)."""
    windows = make_windows(df, n_windows)
    results = []
    for i, w in enumerate(windows):
        if len(w) < 10:
            continue
        positions = strategy_fn(w)
        strat_ret = strategy_returns(w, positions, cost_bps=cost_bps)
        bh_ret = buy_hold_returns(w)
        s_stats = window_stats(strat_ret, f"{strategy_name} (ventana {i+1})")
        b_stats = window_stats(bh_ret, f"buy-hold (ventana {i+1})")
        gano_vs_bh = s_stats['retorno_total_%'] > b_stats['retorno_total_%']
        results.append({
            'ventana': i + 1,
            'desde': w.index[0], 'hasta': w.index[-1], 'n_barras': len(w),
            'estrategia': s_stats, 'buy_hold': b_stats,
            'estrategia_le_gano_a_bh': gano_vs_bh,
        })
        if verbose:
            print(f"Ventana {i+1} [{w.index[0]} -> {w.index[-1]}, {len(w)} barras]: "
                  f"estrategia {s_stats['retorno_total_%']}% vs buy-hold {b_stats['retorno_total_%']}% "
                  f"-> {'GANO' if gano_vs_bh else 'perdio'}")
    return results


# --- Ejemplos de funciones de estrategia (parametros fijos, de manual) ---
# NO se interpretan resultados todavia -- estas funciones estan listas para
# usarse, la lectura de resultados queda para cuando se decida arrancar la
# fase de analisis (ver conversacion 14/08/2026).

def strategy_ma_trend(df: pd.DataFrame, period=200):
    """Filtro de tendencia simple: largo si el cierre esta por encima de su
    media movil de `period` barras, afuera si no. (hipotesis #2 de
    knowledge/estrategias_oro_encontradas.md, adaptada a la resolucion de
    barras que se le pase -- OJO: 200 barras en M1 es ~3.3hs, no 200 dias;
    hay que decidir a que resolucion correrla antes de interpretar nada)."""
    ma = df['close'].rolling(period, min_periods=period).mean()
    pos = (df['close'] > ma).astype(int)
    return pos.fillna(0)


def strategy_orb(df: pd.DataFrame, orb_bars=30):
    """Opening range breakout: usa las primeras `orb_bars` barras del
    DataFrame como rango de apertura, opera la ruptura hasta el final de la
    ventana. (hipotesis #8 de knowledge/estrategias_oro_encontradas.md)."""
    if len(df) <= orb_bars:
        return pd.Series(0, index=df.index)
    orb_high = df['close'].iloc[:orb_bars].max()
    orb_low = df['close'].iloc[:orb_bars].min()
    pos = pd.Series(0, index=df.index)
    in_position = 0
    for i in range(orb_bars, len(df)):
        price = df['close'].iloc[i]
        if in_position == 0:
            if price > orb_high:
                in_position = 1
            elif price < orb_low:
                in_position = -1
        pos.iloc[i] = in_position
    return pos


if __name__ == '__main__':
    # Smoke test tecnico UNICAMENTE -- confirma que el codigo corre sin
    # errores. No se interpreta ni se muestra el numero como conclusion.
    import sys
    INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()

    print("=== SMOKE TEST TECNICO -- verifica que el harness corre, no es analisis ===")
    try:
        r1 = walk_forward(df, lambda w: strategy_ma_trend(w, period=200), n_windows=3, strategy_name="MA200", verbose=False)
        r2 = walk_forward(df, lambda w: strategy_orb(w, orb_bars=30), n_windows=3, strategy_name="ORB30", verbose=False)
        print(f"OK -- strategy_ma_trend corrio en {len(r1)} ventanas sin errores")
        print(f"OK -- strategy_orb corrio en {len(r2)} ventanas sin errores")
        print("\nInfraestructura lista. Resultados NO mostrados a proposito -- se interpretan cuando se decida arrancar la fase de analisis.")
    except Exception as e:
        print(f"ERROR -- el harness fallo: {e}")
        sys.exit(1)
