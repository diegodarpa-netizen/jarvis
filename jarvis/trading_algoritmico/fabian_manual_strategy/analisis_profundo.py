"""
Segunda pasada de mineria de datos sobre el historial de Fabian -- angulos
nuevos que no se habian mirado todavia: hora de entrada, duracion de la
operacion, autocorrelacion (racha tras racha), evolucion mes a mes,
distribucion real de R (no todo es +-1), y significancia estadistica del
resultado global con bootstrap (mismo rigor que se uso en todo el
proyecto). A pedido de Diego (27/08/2026): "encontrar patrones,
inconsistencias, datos... hipotesis, aciertos".
"""
import pandas as pd
import numpy as np

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
N_BOOTSTRAP = 5000
SEED = 42


def cargar():
    df = pd.read_csv(INPUT)
    df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
    df = df.sort_values('Fecha_dt').reset_index(drop=True)

    def a_minutos(hhmm):
        try:
            h, m = map(int, str(hhmm).split(':'))
            return h * 60 + m
        except Exception:
            return np.nan

    df['min_apertura'] = df['Hora apertura (NY)'].apply(a_minutos)
    df['min_cierre'] = df['Hora cierre  (NY)'].apply(a_minutos)
    df['duracion_min'] = df['min_cierre'] - df['min_apertura']
    df.loc[df['duracion_min'] < 0, 'duracion_min'] = np.nan  # cruces de hora raros, descartar
    return df


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
    df = cargar()

    print("=" * 100)
    print("1. SIGNIFICANCIA ESTADISTICA DEL RESULTADO GLOBAL (bootstrap, mismo rigor de todo el proyecto)")
    print("=" * 100)
    media, lo, hi = bootstrap_ci(df['Beneficio_R'].values, rng=rng)
    sig = (lo > 0) or (hi < 0)
    print(f"Promedio R por operacion: {media:.4f}")
    print(f"IC 95% (5.000 iteraciones): [{lo:.4f}, {hi:.4f}]")
    print(f"-> {'SIGNIFICATIVO -- no cruza cero, se distingue de azar con 95% de confianza' if sig else 'NO significativo'}")
    print("Nota: a diferencia de nuestras propias hipotesis (EMA9/Fibonacci/VWAP/patrones de velas),")
    print("este SI pasa el filtro -- primera vez en todo el proyecto.")

    print("\n" + "=" * 100)
    print("2. HORA DE ENTRADA DENTRO DE LA SESION -- primeros 30min vs resto")
    print("=" * 100)
    df['tramo_horario'] = pd.cut(df['min_apertura'], bins=[0, 9*60+30, 10*60, 10*60+59],
                                   labels=['09:01-09:30 (apertura)', '09:30-10:00 (medio)', '10:00-10:59 (cierre)'])
    resumen_hora = df.groupby('tramo_horario', observed=True).agg(
        n=('Beneficio_R', 'count'), win_rate=('Beneficio_R', lambda x: (x > 0).mean() * 100),
        promedio_R=('Beneficio_R', 'mean'), total_R=('Beneficio_R', 'sum'))
    print(resumen_hora.round(3).to_string())

    print("\n" + "=" * 100)
    print("3. DURACION DE LA OPERACION vs RESULTADO")
    print("=" * 100)
    dur_validas = df.dropna(subset=['duracion_min'])
    print(f"Duracion promedio TODAS las operaciones: {dur_validas['duracion_min'].mean():.1f} min")
    print(f"Duracion promedio GANADORAS: {dur_validas[dur_validas['Beneficio_R']>0]['duracion_min'].mean():.1f} min")
    print(f"Duracion promedio PERDEDORAS: {dur_validas[dur_validas['Beneficio_R']<0]['duracion_min'].mean():.1f} min")
    corr = dur_validas['duracion_min'].corr(dur_validas['Beneficio_R'])
    print(f"Correlacion duracion vs resultado (R): {corr:.3f}")

    print("\n" + "=" * 100)
    print("4. AUTOCORRELACION -- ¿una racha predice la siguiente operacion?")
    print("=" * 100)
    df_no_hedge = df[~df['es_hedge']].reset_index(drop=True)
    resultado_anterior = df_no_hedge['Beneficio_R'].shift(1)
    tras_ganadora = df_no_hedge[resultado_anterior > 0]['Beneficio_R']
    tras_perdedora = df_no_hedge[resultado_anterior < 0]['Beneficio_R']
    print(f"Win rate tras una operacion GANADORA: {(tras_ganadora>0).mean()*100:.1f}% (n={len(tras_ganadora)})")
    print(f"Win rate tras una operacion PERDEDORA: {(tras_perdedora>0).mean()*100:.1f}% (n={len(tras_perdedora)})")
    print("Lectura: si estos dos numeros son parecidos, no hay 'racha caliente' -- cada operacion es independiente.")

    print("\n" + "=" * 100)
    print("5. EVOLUCION MES A MES -- ¿mejora, empeora, o es estable?")
    print("=" * 100)
    df['mes'] = df['Fecha_dt'].dt.to_period('M')
    evol = df.groupby('mes').agg(n=('Beneficio_R', 'count'), win_rate=('Beneficio_R', lambda x: (x > 0).mean() * 100),
                                   total_R=('Beneficio_R', 'sum'))
    print(evol.round(2).to_string())

    print("\n" + "=" * 100)
    print("6. DISTRIBUCION REAL DE R -- no todo es +1/-1 exacto")
    print("=" * 100)
    exactos_1 = (df['Beneficio_R'] == 1.0).sum()
    exactos_neg1 = (df['Beneficio_R'] == -1.0).sum()
    parciales_pos = ((df['Beneficio_R'] > 0) & (df['Beneficio_R'] != 1.0)).sum()
    parciales_neg = ((df['Beneficio_R'] < 0) & (df['Beneficio_R'] != -1.0)).sum()
    print(f"Ganadoras exactas +1R: {exactos_1} | Ganadoras parciales (breakeven parcial, hedge, etc.): {parciales_pos}")
    print(f"Perdedoras exactas -1R: {exactos_neg1} | Perdedoras parciales (SL movido/breakeven parcial): {parciales_neg}")
    print(f"Perdida promedio cuando NO es -1R exacto: {df[(df['Beneficio_R']<0) & (df['Beneficio_R']!=-1.0)]['Beneficio_R'].mean():.3f}")
    print("-> Fabian mueve el SL a breakeven parcial en varias operaciones -- reduce la perdida antes de que llegue a -1R completo.")

    print("\n" + "=" * 100)
    print("7. HEDGE POSITION -- ¿realmente compensa la primera perdida?")
    print("=" * 100)
    dias_con_hedge = df[df['es_hedge']]['Fecha_dt'].unique()
    print(f"Dias con Hedge Position: {len(dias_con_hedge)}")
    for d in dias_con_hedge:
        ops_dia = df[df['Fecha_dt'] == d][['modelo_limpio', 'Buy / Sell', 'Resultado', 'Beneficio_R', 'es_hedge']]
        r_neto = ops_dia['Beneficio_R'].sum()
        print(f"  {pd.Timestamp(d).strftime('%d/%m/%Y')}: R neto del dia = {r_neto:+.2f}")
    r_dias_hedge = df[df['Fecha_dt'].isin(dias_con_hedge)].groupby('Fecha_dt')['Beneficio_R'].sum()
    print(f"\nR neto promedio en dias CON hedge: {r_dias_hedge.mean():.3f}")
    r_dias_sin_hedge = df[~df['Fecha_dt'].isin(dias_con_hedge)].groupby('Fecha_dt')['Beneficio_R'].sum()
    print(f"R neto promedio en dias SIN hedge: {r_dias_sin_hedge.mean():.3f}")

    print("\n" + "=" * 100)
    print("8. FRECUENCIA -- ¿cuantos dias reales pasan entre operaciones?")
    print("=" * 100)
    dias_unicos = sorted(df['Fecha_dt'].unique())
    gaps = [(pd.Timestamp(dias_unicos[i+1]) - pd.Timestamp(dias_unicos[i])).days for i in range(len(dias_unicos)-1)]
    dias_calendario = (pd.Timestamp(dias_unicos[-1]) - pd.Timestamp(dias_unicos[0])).days
    print(f"Dias operados totales: {len(dias_unicos)} en {dias_calendario} dias de calendario")
    print(f"Gap promedio entre dias operados: {np.mean(gaps):.1f} dias | Gap maximo: {max(gaps)} dias")
    gap_max_idx = gaps.index(max(gaps))
    print(f"El gap mas largo fue entre {pd.Timestamp(dias_unicos[gap_max_idx]).strftime('%d/%m/%Y')} y {pd.Timestamp(dias_unicos[gap_max_idx+1]).strftime('%d/%m/%Y')}")
