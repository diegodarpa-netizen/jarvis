"""
Analisis exploratorio de XAU/USD M1 (paso 1 del roadmap en knowledge/como_empezar.md).

Dataset: jarvis/trading/xau_strategy/data/XAUUSD_M1.csv -- 6 meses, ventana
08:00-11:30 NY, ~29.500 velas M1, 127/183 dias con datos.

Metodologia (siguiendo la advertencia de Ernie Chan sobre gaps -- ver
conversacion 13/08/2026 y knowledge/machine_learning_financiero.md):
NO se corren los tests sobre la serie concatenada ingenuamente. Cada dia
resetea la ventana (salto de ~20.5h entre el cierre de un dia y la apertura
del siguiente) -- tratar eso como continuidad estadistica contamina
ADF/Hurst/autocorrelacion. Se calculan retornos SOLO dentro de cada sesion
(el primer minuto de cada dia no se compara contra el ultimo del dia
anterior), y se agrupan (pool) esos retornos intra-sesion para los tests.

Resultado: preliminar (6 meses = ~1 regimen de mercado, no varios). Ver
knowledge/como_empezar.md y evidencia_traders_rentables_y_fracasos.md sobre
por que no alcanza para validar una estrategia, solo para un primer vistazo.
"""
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'

def load():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    return df


def within_session_log_returns(df):
    """Retornos log SOLO dentro de cada dia -- nunca comparando el ultimo
    minuto de un dia contra el primero del siguiente."""
    out = []
    for day, g in df.groupby('day'):
        logp = np.log(g['close'].values)
        r = np.diff(logp)
        out.append(r)
    return np.concatenate(out)


def naive_log_returns(df):
    """Version 'mal hecha' a proposito, para comparar -- concatena todo
    sin respetar los gaps entre sesiones."""
    logp = np.log(df['close'].values)
    return np.diff(logp)


def hurst_variance_scaling(df, lags=(1, 2, 5, 10, 20, 30, 60)):
    """Hurst por escalamiento de varianza, calculado SOLO con pares de
    barras del mismo dia (nunca cruzando la sesion)."""
    log_std = []
    log_lag = []
    for k in lags:
        diffs = []
        for day, g in df.groupby('day'):
            logp = np.log(g['close'].values)
            if len(logp) <= k:
                continue
            diffs.append(logp[k:] - logp[:-k])
        if not diffs:
            continue
        pooled = np.concatenate(diffs)
        if len(pooled) < 30:
            continue
        log_std.append(np.log(np.std(pooled)))
        log_lag.append(np.log(k))
    slope, intercept = np.polyfit(log_lag, log_std, 1)
    return slope, list(zip(lags, log_lag, log_std))


def adf_report(series, label):
    stat, pvalue, lags_used, nobs, crit, _ = adfuller(series, autolag='AIC')
    print(f"\n--- ADF: {label} ---")
    print(f"  n obs: {nobs} | lags usados: {lags_used}")
    print(f"  estadistico ADF: {stat:.4f} | p-valor: {pvalue:.6f}")
    print(f"  valores criticos: {dict((k, round(v,4)) for k,v in crit.items())}")
    veredicto = "ESTACIONARIA (rechaza raiz unitaria)" if pvalue < 0.05 else "NO estacionaria (no rechaza raiz unitaria)"
    print(f"  veredicto (5%): {veredicto}")
    return stat, pvalue


def autocorr_lag1(series):
    return np.corrcoef(series[:-1], series[1:])[0, 1]


if __name__ == '__main__':
    df = load()
    n_days = df['day'].nunique()
    print("="*70)
    print("ANALISIS EXPLORATORIO -- XAU/USD M1, ventana 08:00-11:30 NY")
    print("="*70)
    print(f"Velas totales: {len(df)} | Dias con datos: {n_days}")
    print(f"Rango de fechas: {df.index.min()} -> {df.index.max()}")

    # 1) ADF sobre PRECIO crudo (se espera que NO sea estacionario -- sanity check)
    adf_report(df['close'].values, "precio crudo (nivel), concatenado")

    # 2) ADF sobre retornos, version NAIVE (mal hecha, para comparar)
    naive_r = naive_log_returns(df)
    adf_report(naive_r, "retornos log, concatenado NAIVE (con gaps de sesion contaminando)")

    # 3) ADF sobre retornos, version CORRECTA (solo intra-sesion)
    session_r = within_session_log_returns(df)
    adf_report(session_r, "retornos log, SOLO intra-sesion (gaps excluidos)")

    print(f"\n  Diferencia de tamano de muestra: naive={len(naive_r)} vs correcto={len(session_r)}")
    print(f"  (la diferencia = {len(naive_r) - len(session_r)} son los saltos entre sesiones que se excluyeron)")

    # 4) Autocorrelacion lag-1 (version correcta)
    ac1 = autocorr_lag1(session_r)
    print(f"\n--- Autocorrelacion lag-1 (retornos intra-sesion) ---")
    print(f"  ACF(1) = {ac1:.5f}")
    print(f"  interpretacion: {'positiva (momentum de muy corto plazo)' if ac1 > 0.02 else 'negativa (reversion de muy corto plazo)' if ac1 < -0.02 else 'practicamente cero (sin memoria de corto plazo detectable)'}")

    # 5) Hurst por escalamiento de varianza
    h, detail = hurst_variance_scaling(df)
    print(f"\n--- Exponente de Hurst (escalamiento de varianza, intra-sesion) ---")
    for k, ll, ls in detail:
        print(f"  lag={k:>3} min | log(lag)={ll:.3f} | log(std)={ls:.3f}")
    print(f"  H estimado = {h:.4f}")
    if h > 0.55:
        interp = "TIENDE (momentum) -- un movimiento persiste mas de lo esperado por azar"
    elif h < 0.45:
        interp = "REVIERTE A LA MEDIA -- un movimiento tiende a corregirse"
    else:
        interp = "CAMINO ALEATORIO -- sin evidencia clara de tendencia ni reversion en esta ventana"
    print(f"  interpretacion: {interp}")

    print("\n" + "="*70)
    print("RECORDATORIO: resultado preliminar sobre 6 meses (1 solo regimen).")
    print("No usar todavia para elegir estrategia sin repetir en mas ventanas.")
    print("="*70)
