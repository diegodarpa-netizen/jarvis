"""
Day trading candidata #1: Opening Range Breakout (ORB) -- ya documentada en
knowledge/estrategias_oro_encontradas.md, sec. 8. A pedido de Diego
(26/08/2026, alcance de day trading recien agregado): probarla de verdad
sobre los 6 meses M1 de oro que ya tenemos.

Regla (tal como esta documentada, sin agregar nada nuevo):
- Rango de apertura = maximo/minimo de los primeros 30 minutos de la sesion
- Entrada: ruptura del rango (arriba = largo, abajo = corto) -- solo la
  primera ruptura de la sesion, una operacion por sesion
- Stop: al lado opuesto del rango de apertura
- Salida: al cierre de la sesion (no hay objetivo de ganancia, se documenta
  asi en la fuente original)

Advertencia ya encontrada en la investigacion: mas del 70% de los ORB
fallan en la primera hora -- se prueba igual, con esa expectativa.
"""
import pandas as pd
import numpy as np

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
MINUTOS_RANGO_APERTURA = 30
N_BOOTSTRAP = 5000
SEED = 42


def load():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    return df


def backtest_dia(g: pd.DataFrame, minutos_apertura=MINUTOS_RANGO_APERTURA):
    if len(g) < minutos_apertura + 5:
        return None
    apertura = g.iloc[:minutos_apertura]
    rango_alto = apertura['high'].max()
    rango_bajo = apertura['low'].min()
    resto = g.iloc[minutos_apertura:]

    for _, vela in resto.iterrows():
        if vela['high'] > rango_alto:
            entrada = rango_alto
            stop = rango_bajo
            direccion = 1
            break
        elif vela['low'] < rango_bajo:
            entrada = rango_bajo
            stop = rango_alto
            direccion = -1
            break
    else:
        return None  # no hubo ruptura en toda la sesion

    idx_entrada = resto.index[resto.index >= vela.name][0]
    resto_post_entrada = resto.loc[idx_entrada:]

    # chequear si el stop se toca antes del cierre
    if direccion == 1:
        tocado_stop = resto_post_entrada[resto_post_entrada['low'] <= stop]
    else:
        tocado_stop = resto_post_entrada[resto_post_entrada['high'] >= stop]

    if len(tocado_stop) > 0:
        precio_salida = stop
        salida_motivo = 'stop'
    else:
        precio_salida = g['close'].iloc[-1]
        salida_motivo = 'cierre_sesion'

    resultado_pct = (precio_salida - entrada) / entrada * 100 * direccion
    return {
        'dia': g['day'].iloc[0], 'direccion': 'LARGO' if direccion == 1 else 'CORTO',
        'rango_apertura_%': round((rango_alto - rango_bajo) / rango_bajo * 100, 3),
        'entrada': entrada, 'salida': precio_salida, 'motivo_salida': salida_motivo,
        'resultado_%': resultado_pct,
    }


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

    resultados = []
    for day, g in df.groupby('day'):
        r = backtest_dia(g)
        if r:
            resultados.append(r)

    trades = pd.DataFrame(resultados)
    print("=" * 90)
    print(f"OPENING RANGE BREAKOUT (30 min) -- XAU/USD M1, 6 meses ({df['day'].min()} a {df['day'].max()})")
    print("=" * 90)
    print(f"\nSesiones totales: {df['day'].nunique()} | Con ruptura operada: {len(trades)}")
    ganadoras = trades[trades['resultado_%'] > 0]
    print(f"Ganadoras: {len(ganadoras)} | Perdedoras: {len(trades)-len(ganadoras)} | Win rate: {len(ganadoras)/len(trades)*100:.1f}%")
    print(f"Resultado promedio por operacion: {trades['resultado_%'].mean():.4f}%")
    print(f"Suma de resultados (sin compounding): {trades['resultado_%'].sum():.3f}%")
    print(f"Por motivo de salida: {trades['motivo_salida'].value_counts().to_dict()}")

    media_boot, lo, hi = bootstrap_ci(trades['resultado_%'].values, rng=rng)
    sig = (lo > 0) or (hi < 0)
    print(f"\nBootstrap 95% CI: [{lo:.4f}%, {hi:.4f}%] -- {'SIGNIFICATIVO' if sig else 'NO significativo (cruza cero)'}")

    print(f"\nLargos: {(trades['direccion']=='LARGO').sum()} | Cortos: {(trades['direccion']=='CORTO').sum()}")
    for d in ['LARGO', 'CORTO']:
        sub = trades[trades['direccion'] == d]
        if len(sub):
            print(f"  {d}: WR={ (sub['resultado_%']>0).mean()*100:.1f}% | promedio={sub['resultado_%'].mean():.4f}%")

    trades.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/resultados_orb_oro.csv', index=False)
