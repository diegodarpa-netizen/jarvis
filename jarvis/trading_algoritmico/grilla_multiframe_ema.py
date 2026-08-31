"""
Grilla multi-EMA x multi-resolucion de distancia a la media movil, con
bootstrap de significancia. A pedido de Diego (15/08/2026): encontrar
patrones en distintos frames respecto a la distancia a la EMA, con
escenarios/hipotesis multiples y rigor estadistico (no solo el numero
puntual, tambien si es distinguible de ruido).

EMAs: 9, 20, 50, 200 (las mismas del grafico de Diego)
Resoluciones: M1, M5, M15, M30, diario -- todas respetando el corte de
sesion (nunca una racha/zona cruza de un dia a otro, ver conversacion
sobre el aviso de Ernie Chan de gaps).

Bootstrap: para cada celda (EMA x resolucion x zona de distancia), se
remuestrea con reemplazo N veces el conjunto de retornos observados, para
estimar un intervalo de confianza del retorno medio -- si el intervalo
cruza el cero, el patron no es distinguible de ruido con esta muestra.
"""
import pandas as pd
import numpy as np
import time

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
EMAS = [9, 20, 50, 200]
BANDAS = [0, 0.5, 1, 2, 4, np.inf]
N_BOOTSTRAP = 5000
SEED = 42


def load():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    return df


def resample_within_session_list(df, rule):
    out = []
    for day, g in df.groupby('day'):
        if rule == '1D':
            continue
        r = g['close'].resample(rule).last().dropna()
        if len(r) > max(20, 3):
            out.append(r)
    return out


def daily_series(df):
    daily = df.groupby('day')['close'].last()
    daily.index = pd.to_datetime(daily.index)
    return daily


def zona_returns_por_serie(serie_lista, ema_period, bandas=BANDAS):
    """Dado una lista de series (una por sesion) o una sola serie continua
    (diario), devuelve un DataFrame con zona y retorno-siguiente orientado,
    calculando la EMA de nuevo en cada sesion (sin cruzar el gap)."""
    filas = []
    series = serie_lista if isinstance(serie_lista, list) else [serie_lista]
    for s in series:
        if len(s) <= ema_period:
            continue
        ema = s.ewm(span=ema_period, adjust=False).mean()
        dist_pct = (s - ema) / ema * 100
        dist_abs = dist_pct.abs()
        signo = np.sign(dist_pct)
        ret_sig = s.pct_change().shift(-1) * 100 * signo
        zona = pd.cut(dist_abs, bins=bandas, labels=[f"{bandas[i]}-{bandas[i+1]}%" for i in range(len(bandas)-1)])
        filas.append(pd.DataFrame({'zona': zona, 'ret': ret_sig}).dropna())
    if not filas:
        return pd.DataFrame(columns=['zona', 'ret'])
    return pd.concat(filas, ignore_index=True)


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
    print("="*100)
    print(f"GRILLA MULTI-EMA x MULTI-RESOLUCION -- {len(EMAS)} EMAs x 5 resoluciones, bootstrap {N_BOOTSTRAP} iteraciones/celda")
    print("="*100)

    resoluciones = {
        'M1': None,  # se usa el df crudo agrupado por dia
        'M5': '5min', 'M15': '15min', 'M30': '30min',
    }

    filas_resultado = []
    celdas_procesadas = 0

    for ema_p in EMAS:
        for res_nombre, rule in resoluciones.items():
            if res_nombre == 'M1':
                series_lista = [g['close'] for day, g in df.groupby('day') if len(g) > ema_p]
            else:
                series_lista = resample_within_session_list(df, rule)
                series_lista = [s for s in series_lista if len(s) > ema_p]
            tabla = zona_returns_por_serie(series_lista, ema_p)
            if tabla.empty:
                continue
            for zona, grupo in tabla.groupby('zona', observed=True):
                vals = grupo['ret'].values
                n = len(vals)
                media_boot, lo, hi = bootstrap_ci(vals, rng=rng)
                celdas_procesadas += 1
                if media_boot is None:
                    continue
                significativo = (lo > 0) or (hi < 0)  # el IC no cruza el cero
                filas_resultado.append({
                    'EMA': ema_p, 'resolucion': res_nombre, 'zona': zona, 'n': n,
                    'retorno_medio_%': round(vals.mean(), 4),
                    'IC95_lo': round(lo, 4), 'IC95_hi': round(hi, 4),
                    'significativo_95%': significativo,
                })

    # diario aparte (una sola serie continua, sin gaps intra-dia)
    daily = daily_series(df)
    for ema_p in EMAS:
        tabla = zona_returns_por_serie(daily, ema_p)
        if tabla.empty:
            continue
        for zona, grupo in tabla.groupby('zona', observed=True):
            vals = grupo['ret'].values
            n = len(vals)
            media_boot, lo, hi = bootstrap_ci(vals, rng=rng)
            celdas_procesadas += 1
            if media_boot is None:
                continue
            significativo = (lo > 0) or (hi < 0)
            filas_resultado.append({
                'EMA': ema_p, 'resolucion': 'Diario', 'zona': zona, 'n': n,
                'retorno_medio_%': round(vals.mean(), 4),
                'IC95_lo': round(lo, 4), 'IC95_hi': round(hi, 4),
                'significativo_95%': significativo,
            })

    tabla_final = pd.DataFrame(filas_resultado)
    elapsed = time.time() - t0

    print(f"\nCeldas procesadas (EMA x resolucion x zona): {celdas_procesadas}")
    print(f"Tiempo real de procesamiento: {elapsed:.1f} segundos ({elapsed/60:.2f} minutos)")

    print("\n--- TODAS las celdas ---")
    print(tabla_final.sort_values(['EMA', 'resolucion']).to_string(index=False))

    sig = tabla_final[tabla_final['significativo_95%']]
    print(f"\n--- Celdas con patron ESTADISTICAMENTE SIGNIFICATIVO (IC95% no cruza cero): {len(sig)} de {len(tabla_final)} ---")
    if len(sig) > 0:
        print(sig.sort_values('retorno_medio_%').to_string(index=False))
    else:
        print("Ninguna celda fue significativa al 95% con esta muestra.")

    tabla_final.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/resultados_grilla_multiframe.csv', index=False)
    print("\nGuardado completo en resultados_grilla_multiframe.csv")
