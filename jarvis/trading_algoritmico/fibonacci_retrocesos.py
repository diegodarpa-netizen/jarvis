"""
Retrocesos de Fibonacci -- zonas de retroceso de un swing confirmado
(zigzag con umbral fijo, deteccion objetiva de picos/valles, sin
subjetividad de conteo de ondas) vs retorno del periodo siguiente,
orientado a favor de la direccion ORIGINAL del swing.

A pedido de Diego (25/08/2026): separar la parte de Fibonacci/Elliott que
SI se puede testear de forma mecanica (zonas de retroceso) de la parte
subjetiva (conteo de ondas), que no es reproducible algoritmicamente y
por eso se descarto como base de estrategia (ver conversacion).

Metodologia (mismo rigor que grilla_multiframe_ema.py):
- Swings detectados con ZigZag de umbral fijo (% minimo de movimiento
  para confirmar un pivote nuevo) -- deterministico, sin discrecion.
  Nota honesta: como cualquier zigzag, un pivote recien se CONFIRMA
  cuando el precio se revierte el umbral completo -- hay un pequeno
  desfasaje inevitable (no es lookahead sobre el retorno que se mide,
  pero si implica que "ahora mismo" nunca se sabe si el ultimo pivote
  visible es realmente el ultimo hasta que se confirma el siguiente).
- Para cada barra dentro de una correccion (entre el pivote B y el
  siguiente pivote C), se mide cuanto se retrocedio del swing previo
  (A->B), en % de ese swing.
- Se bandea en zonas estilo Fibonacci: <0% (sin retroceso todavia),
  0-23.6, 23.6-38.2, 38.2-50, 50-61.8, 61.8-78.6, 78.6-100, >100%
  (ya rompio el origen del swing -- reversion completa).
- Retorno del periodo siguiente (M1: +15 min; Diario: +1 dia), orientado
  a favor de la direccion ORIGINAL del swing A->B.
- Bootstrap 95% CI por celda (umbral x resolucion x zona) -- mismo
  criterio que la grilla de EMAs, para no repetir el error de leer un
  numero puntual como si fuera prueba.
- M1 respeta cortes de sesion (nunca cruza el gap entre dias). Diario ya
  es una serie continua por definicion (cada barra = un dia).
"""
import pandas as pd
import numpy as np
import time

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
UMBRALES_M1 = [0.3, 0.6]      # % minimo de reversion para confirmar pivote, intradia
UMBRALES_DIARIO = [1.5, 3.0]  # % minimo de reversion para confirmar pivote, diario
HORIZONTE_M1 = 15   # barras (minutos) hacia adelante
HORIZONTE_DIARIO = 1  # dias hacia adelante
BANDAS = [-np.inf, 0, 23.6, 38.2, 50, 61.8, 78.6, 100, np.inf]
ETIQUETAS = ['<0% (sin retroceso)', '0-23.6%', '23.6-38.2%', '38.2-50%',
             '50-61.8%', '61.8-78.6%', '78.6-100%', '>100% (rompio origen)']
N_BOOTSTRAP = 5000
SEED = 42


def load():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    return df


def daily_series(df):
    daily = df.groupby('day')['close'].last()
    daily.index = pd.to_datetime(daily.index)
    return daily


def zigzag_pivots(serie: pd.Series, umbral_pct: float):
    """Devuelve lista de (timestamp, precio, tipo) con tipo 'high'/'low',
    detectados con umbral fijo -- deterministico, sin discrecion."""
    idx = serie.index
    precios = serie.values
    if len(precios) < 3:
        return []
    pivots = []
    trend = 0
    ext_i, ext_p = 0, precios[0]
    for i in range(1, len(precios)):
        p = precios[i]
        if trend == 0:
            if p >= ext_p * (1 + umbral_pct / 100):
                trend = 1
                ext_i, ext_p = i, p
            elif p <= ext_p * (1 - umbral_pct / 100):
                trend = -1
                ext_i, ext_p = i, p
        elif trend == 1:
            if p > ext_p:
                ext_i, ext_p = i, p
            elif p <= ext_p * (1 - umbral_pct / 100):
                pivots.append((idx[ext_i], ext_p, 'high'))
                trend = -1
                ext_i, ext_p = i, p
        else:
            if p < ext_p:
                ext_i, ext_p = i, p
            elif p >= ext_p * (1 + umbral_pct / 100):
                pivots.append((idx[ext_i], ext_p, 'low'))
                trend = 1
                ext_i, ext_p = i, p
    return pivots


def analizar_swings(serie: pd.Series, pivots: list, horizonte: int):
    """Para cada terna de pivotes consecutivos A-B-C, banda de retroceso
    de cada barra entre B y C respecto del swing A->B, y retorno
    horizonte-barras-despues orientado a la direccion original A->B."""
    filas = []
    if len(pivots) < 3:
        return pd.DataFrame(columns=['zona', 'ret'])
    for k in range(len(pivots) - 2):
        tA, pA, _ = pivots[k]
        tB, pB, _ = pivots[k + 1]
        tC, pC, _ = pivots[k + 2]
        swing_size = pB - pA
        if swing_size == 0:
            continue
        direccion = 1 if swing_size > 0 else -1
        sub_idx = serie.index[(serie.index > tB) & (serie.index <= tC)]
        if len(sub_idx) == 0:
            continue
        precios_sub = serie.loc[sub_idx]
        retroceso_pct = (pB - precios_sub) / swing_size * 100 * direccion
        # retorno horizonte barras despues, orientado a favor de la direccion ORIGINAL (A->B)
        pos = serie.index.get_indexer(sub_idx)
        fut_pos = pos + horizonte
        validos = fut_pos < len(serie)
        for j, (t, ret_pct) in enumerate(zip(sub_idx[validos], retroceso_pct[validos])):
            precio_t = serie.iloc[pos[j]]
            precio_fut = serie.iloc[fut_pos[j]]
            ret_fwd = (precio_fut - precio_t) / precio_t * 100 * direccion
            zona = pd.cut([ret_pct], bins=BANDAS, labels=ETIQUETAS)[0]
            filas.append({'zona': zona, 'ret': ret_fwd})
    return pd.DataFrame(filas)


def bootstrap_ci(valores, n_boot=N_BOOTSTRAP, rng=None):
    if len(valores) < 5:
        return None, None, None
    valores = np.asarray(valores)
    medias = np.empty(n_boot)
    n = len(valores)
    for i in range(n_boot):
        muestra = rng.choice(valores, size=n, replace=True)
        medias[i] = muestra.mean()
    lo, hi = np.percentile(medias, [2.5, 97.5])
    return medias.mean(), lo, hi


if __name__ == '__main__':
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    df = load()

    print("=" * 100)
    print("RETROCESOS DE FIBONACCI -- zonas de retroceso de swing vs retorno del periodo siguiente")
    print("(swings detectados con zigzag de umbral fijo -- sin conteo de ondas subjetivo)")
    print("=" * 100)

    filas_resultado = []

    # --- M1, por sesion (no cruza el gap entre dias) ---
    for umbral in UMBRALES_M1:
        tablas = []
        for day, g in df.groupby('day'):
            serie = g['close']
            if len(serie) < 30:
                continue
            pivots = zigzag_pivots(serie, umbral)
            tabla = analizar_swings(serie, pivots, HORIZONTE_M1)
            if not tabla.empty:
                tablas.append(tabla)
        if not tablas:
            continue
        tabla_total = pd.concat(tablas, ignore_index=True)
        for zona, grupo in tabla_total.groupby('zona', observed=True):
            vals = grupo['ret'].values
            n = len(vals)
            media_boot, lo, hi = bootstrap_ci(vals, rng=rng)
            if media_boot is None:
                continue
            significativo = (lo > 0) or (hi < 0)
            filas_resultado.append({
                'resolucion': 'M1', 'umbral_zigzag_%': umbral, 'zona': zona, 'n': n,
                'retorno_medio_%': round(vals.mean(), 4),
                'IC95_lo': round(lo, 4), 'IC95_hi': round(hi, 4),
                'significativo_95%': significativo,
            })

    # --- Diario (serie continua) ---
    daily = daily_series(df)
    for umbral in UMBRALES_DIARIO:
        pivots = zigzag_pivots(daily, umbral)
        tabla = analizar_swings(daily, pivots, HORIZONTE_DIARIO)
        if tabla.empty:
            continue
        for zona, grupo in tabla.groupby('zona', observed=True):
            vals = grupo['ret'].values
            n = len(vals)
            media_boot, lo, hi = bootstrap_ci(vals, rng=rng)
            if media_boot is None:
                continue
            significativo = (lo > 0) or (hi < 0)
            filas_resultado.append({
                'resolucion': 'Diario', 'umbral_zigzag_%': umbral, 'zona': zona, 'n': n,
                'retorno_medio_%': round(vals.mean(), 4),
                'IC95_lo': round(lo, 4), 'IC95_hi': round(hi, 4),
                'significativo_95%': significativo,
            })

    tabla_final = pd.DataFrame(filas_resultado)
    elapsed = time.time() - t0

    print(f"\nCeldas procesadas (resolucion x umbral x zona): {len(tabla_final)}")
    print(f"Tiempo de procesamiento: {elapsed:.1f} segundos")

    print("\n--- TODAS las celdas ---")
    print(tabla_final.sort_values(['resolucion', 'umbral_zigzag_%']).to_string(index=False))

    sig = tabla_final[tabla_final['significativo_95%']]
    print(f"\n--- Celdas ESTADISTICAMENTE SIGNIFICATIVAS (IC95% no cruza cero): {len(sig)} de {len(tabla_final)} ---")
    if len(sig) > 0:
        print(sig.sort_values('retorno_medio_%').to_string(index=False))
    else:
        print("Ninguna celda fue significativa al 95% con esta muestra.")

    tabla_final.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/resultados_fibonacci.csv', index=False)
    print("\nGuardado en resultados_fibonacci.csv")
