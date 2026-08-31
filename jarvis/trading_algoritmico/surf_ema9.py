"""
"Surfear la EMA9" -- version pulida de la regla de entrada/salida por
distancia a la EMA9. A pedido de Diego (15/08/2026): en vez de esperar el
cruce completo (regla naive ya probada), afinar con (a) duracion minima
antes de confirmar la entrada, y (b) salida por retroceso de la distancia
(no por el cruce completo).

Sigue siendo DESCRIPTIVO/comparativo sobre los mismos 32 episodios diarios
ya identificados -- no es todavia una validacion con walk-forward real
(para eso hace falta mas historia, ya lo tenemos anotado).
"""
import pandas as pd
import numpy as np

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'


def load_daily():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    daily = df.groupby('day')['close'].last()
    daily.index = pd.to_datetime(daily.index)
    return daily


def streaks_con_series(close: pd.Series, span=9):
    ema = close.ewm(span=span, adjust=False).mean()
    dist_pct = (close - ema) / ema * 100
    sign = np.sign(dist_pct)
    change = sign.diff().fillna(1) != 0
    group_id = change.cumsum()
    return close, dist_pct, sign, group_id


def regla_naive(close, dist_pct, sign, group_id):
    """La ya probada: entra al cruce, sale al proximo cruce."""
    resultados = []
    for gid, idx in close.groupby(group_id).groups.items():
        s = sign.loc[idx].iloc[0]
        p0, p1 = close.loc[idx].iloc[0], close.loc[idx].iloc[-1]
        mov = (p1 - p0) / p0 * 100 * s  # ya orientado a favor de la direccion
        resultados.append({'inicio': idx[0], 'fin': idx[-1], 'dias': len(idx),
                            'direccion': 'ALZA' if s > 0 else 'BAJA', 'resultado_%': mov})
    return pd.DataFrame(resultados)


def regla_pulida(close, dist_pct, sign, group_id, dias_confirmacion=3, retroceso_pct=50):
    """Entra recien cuando la racha lleva >= dias_confirmacion dias
    (filtro de duracion minima). Sale cuando la distancia retrocede
    retroceso_pct% desde su maximo DENTRO de la racha (no espera el cruce
    completo)."""
    resultados = []
    for gid, idx in close.groupby(group_id).groups.items():
        s = sign.loc[idx].iloc[0]
        if len(idx) < dias_confirmacion:
            continue  # no se confirma la entrada, se descarta el episodio
        entrada_idx = idx[dias_confirmacion - 1]  # entra al confirmar
        precio_entrada = close.loc[entrada_idx]
        dist_racha = dist_pct.loc[idx].abs()
        pico = dist_racha.cummax()
        retroceso = (pico - dist_racha) / pico.replace(0, np.nan) * 100
        salida_candidatas = retroceso[retroceso >= retroceso_pct]
        salida_candidatas = salida_candidatas[salida_candidatas.index >= entrada_idx]
        if len(salida_candidatas) > 0:
            salida_idx = salida_candidatas.index[0]
        else:
            salida_idx = idx[-1]  # si nunca retrocede lo suficiente, sale al final de la racha
        precio_salida = close.loc[salida_idx]
        mov = (precio_salida - precio_entrada) / precio_entrada * 100 * s
        resultados.append({'inicio_racha': idx[0], 'entrada_confirmada': entrada_idx,
                            'salida': salida_idx, 'dias_en_posicion': (salida_idx - entrada_idx).days + 1,
                            'direccion': 'ALZA' if s > 0 else 'BAJA', 'resultado_%': mov})
    return pd.DataFrame(resultados)


if __name__ == '__main__':
    daily = load_daily()
    close, dist_pct, sign, group_id = streaks_con_series(daily)

    print("="*80)
    print("COMPARACION: regla naive (cruce completo) vs regla pulida (surf + filtro)")
    print("="*80)

    naive = regla_naive(close, dist_pct, sign, group_id)
    print(f"\n--- REGLA NAIVE (ya vista) ---")
    print(f"Episodios: {len(naive)} | Ganadores: {(naive['resultado_%']>0).sum()} | "
          f"Perdedores: {(naive['resultado_%']<0).sum()} | Planos: {(naive['resultado_%']==0).sum()}")
    print(f"Resultado promedio por episodio: {naive['resultado_%'].mean():.3f}%")
    print(f"Suma de todos los resultados (si se operaran todos, sin compounding): {naive['resultado_%'].sum():.2f}%")

    pulida = regla_pulida(close, dist_pct, sign, group_id, dias_confirmacion=3, retroceso_pct=50)
    print(f"\n--- REGLA PULIDA (confirmar >=3 dias, salir con 50% de retroceso de distancia) ---")
    print(f"Episodios operados (los que confirmaron): {len(pulida)} de {group_id.nunique()} rachas totales")
    print(f"Ganadores: {(pulida['resultado_%']>0).sum()} | Perdedores: {(pulida['resultado_%']<0).sum()}")
    print(f"Resultado promedio por episodio operado: {pulida['resultado_%'].mean():.3f}%")
    print(f"Suma de todos los resultados: {pulida['resultado_%'].sum():.2f}%")
    print(f"Win rate: {(pulida['resultado_%']>0).mean()*100:.1f}%")

    print("\n--- Detalle de la regla pulida, episodio por episodio ---")
    print(pulida.to_string(index=False))

    print("\nNota: sigue siendo comparativo sobre 6 meses (muestra chica, ~10-13")
    print("episodios operados). No es todavia validacion -- para eso hace falta")
    print("mas historia y walk-forward real, ya documentado como pendiente.")
