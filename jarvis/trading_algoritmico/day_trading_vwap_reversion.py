"""
Day trading candidata #2: VWAP mean reversion. A pedido de Diego
(26/08/2026). Evidencia encontrada: estudio de QuantConnect sobre 100
acciones liquidas de NASDAQ (2022) -- vender en la banda superior de 2
desvios estandar de VWAP dio 63% de acierto, comprar en la banda inferior
de 2 DE dio 61%, ambos con ratio riesgo:beneficio ~1.4-1.5:1. Se prueba
la misma logica sobre oro.

Limitacion importante: no tenemos volumen real (el CSV solo trae
n_ticks, cantidad de ticks por minuto). Se usa n_ticks como proxy de
volumen para el VWAP -- practica comun quApara instrumentos OTC sin
volumen centralizado, pero no es volumen real de exchange. Flagueado.

Regla:
- VWAP y desvio estandar de la distancia a VWAP, calculados de forma
  ACUMULATIVA dentro de cada sesion (nunca cruza el gap entre dias)
- Entrada corta: cierre >= VWAP + 2*DE (apuesta a reversion hacia VWAP)
- Entrada larga: cierre <= VWAP - 2*DE
- Salida: cuando el precio vuelve a tocar el VWAP, o al cierre de la
  sesion si no lo alcanza (day trading, nunca overnight)
- Una operacion a la vez por sesion
"""
import pandas as pd
import numpy as np

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
N_DESVIOS = 2
N_BOOTSTRAP = 5000
SEED = 42


def load():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    return df


def backtest_sesion(g: pd.DataFrame, n_desvios=N_DESVIOS):
    g = g.copy()
    precio = g['close']
    vol = g['n_ticks'].clip(lower=1)  # proxy de volumen

    pv = (precio * vol).cumsum()
    vv = vol.cumsum()
    vwap = pv / vv

    dist = precio - vwap
    # desvio estandar acumulado de la distancia (expanding, sin mirar el futuro)
    de = dist.expanding(min_periods=10).std()

    resultados = []
    en_posicion = False
    direccion = None
    precio_entrada = None

    for i in range(len(g)):
        precio_i = precio.iloc[i]
        vwap_i = vwap.iloc[i]
        de_i = de.iloc[i]
        if pd.isna(de_i) or de_i == 0:
            continue

        if en_posicion:
            tocado_vwap = (direccion == 1 and precio_i >= vwap_i) or (direccion == -1 and precio_i <= vwap_i)
            es_ultima = (i == len(g) - 1)
            if tocado_vwap or es_ultima:
                ret_pct = (precio_i - precio_entrada) / precio_entrada * 100 * direccion
                resultados.append({
                    'dia': g['day'].iloc[0], 'direccion': 'LARGO' if direccion == 1 else 'CORTO',
                    'resultado_%': ret_pct, 'motivo_salida': 'vwap' if tocado_vwap else 'cierre_sesion',
                })
                en_posicion = False
            continue

        z = dist.iloc[i] / de_i
        if z >= n_desvios:
            en_posicion = True
            direccion = -1  # short, apuesta a que baja hacia VWAP
            precio_entrada = precio_i
        elif z <= -n_desvios:
            en_posicion = True
            direccion = 1
            precio_entrada = precio_i

    return resultados


def bootstrap_ci(valores, n_boot=N_BOOTSTRAP, rng=None):
    if len(valores) < 5:
        return None, None, None
    valores = np.asarray(valores)
    medias = np.empty(n_boot)
    for i in range(n_boot):
        medias[i] = rng.choice(valores, size=len(valores), replace=True).mean()
    lo, hi = np.percentile(medias, [2.5, 97.5])
    return medias.mean(), lo, hi


if __name__ == '__main__':
    rng = np.random.default_rng(SEED)
    df = load()

    todas = []
    for day, g in df.groupby('day'):
        if len(g) < 30:
            continue
        todas.extend(backtest_sesion(g))

    trades = pd.DataFrame(todas)
    print("=" * 90)
    print(f"VWAP MEAN REVERSION (banda 2 DE, n_ticks como proxy de volumen) -- XAU/USD M1, 6 meses")
    print("=" * 90)
    print(f"\nOperaciones totales: {len(trades)} (sobre {df['day'].nunique()} sesiones)")
    ganadoras = trades[trades['resultado_%'] > 0]
    print(f"Ganadoras: {len(ganadoras)} | Perdedoras: {len(trades)-len(ganadoras)} | Win rate: {len(ganadoras)/len(trades)*100:.1f}%")
    print(f"Resultado promedio por operacion: {trades['resultado_%'].mean():.4f}%")
    print(f"Suma de resultados (sin compounding): {trades['resultado_%'].sum():.3f}%")
    print(f"Por motivo de salida: {trades['motivo_salida'].value_counts().to_dict()}")

    media_boot, lo, hi = bootstrap_ci(trades['resultado_%'].values, rng=rng)
    sig = (lo > 0) or (hi < 0)
    print(f"\nBootstrap 95% CI: [{lo:.4f}%, {hi:.4f}%] -- {'SIGNIFICATIVO' if sig else 'NO significativo (cruza cero)'}")

    for d in ['LARGO', 'CORTO']:
        sub = trades[trades['direccion'] == d]
        if len(sub):
            print(f"  {d}: n={len(sub)} | WR={(sub['resultado_%']>0).mean()*100:.1f}% | promedio={sub['resultado_%'].mean():.4f}%")

    trades.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/resultados_vwap_reversion_oro.csv', index=False)
