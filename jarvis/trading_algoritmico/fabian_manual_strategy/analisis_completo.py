"""
Analisis completo del historial real de trades de Fabian (estrategia
scalping XAU/USD manual, MEC/MER + estructura M3), a pedido de Diego
(27/08/2026). Trade por trade, dia por dia, desde 27/10/2025 hasta la
actualidad.

Fuente: export de Notion via WhatsApp, 4 archivos trimestrales
(Q3-25, Q1-26, Q2-26, Q3-26).

Correccion de dato aplicada: fila con fecha "28/04/2026" en Q3-25 es un
error de tipeo evidente (el dia de semana dice "Martes", y la secuencia
cronologica del archivo es 27/10 (Lunes) -> ??? (Martes) -> 29/10
(Miercoles) -> se corrige a 28/10/2025.
"""
import pandas as pd
import numpy as np
import glob
import os

CARPETA = os.path.dirname(__file__)
OHLC_6M = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'


def cargar_todo():
    archivos = sorted([f for f in glob.glob(os.path.join(CARPETA, '*.csv'))
                        if '_all' not in f and 'consolidado' not in f])
    dfs = []
    for f in archivos:
        df = pd.read_csv(f)
        df.columns = [c.strip() for c in df.columns]
        dfs.append(df)
    full = pd.concat(dfs, ignore_index=True)
    full = full.dropna(how='all')

    # correccion del typo de fecha identificado
    mask_typo = (full['Fecha'] == '28/04/2026') & (full['Día'] == 'Martes')
    full.loc[mask_typo, 'Fecha'] = '28/10/2025'

    full['Fecha_dt'] = pd.to_datetime(full['Fecha'], format='%d/%m/%Y')
    full['Beneficio_R'] = full['Beneficio (R)'].astype(str).str.replace(',', '.').astype(float)
    full['es_hedge'] = full['Modelo de entrada'].astype(str).str.contains('Hegde', case=False, na=False)
    full['modelo_limpio'] = full['Modelo de entrada'].astype(str).str.replace('Hegde Position, ', '', regex=False).str.strip()
    full = full.sort_values('Fecha_dt').reset_index(drop=True)
    return full


def metricas_generales(df):
    n = len(df)
    ganadores = (df['Beneficio_R'] > 0).sum()
    perdedores = (df['Beneficio_R'] < 0).sum()
    breakeven = (df['Beneficio_R'] == 0).sum()
    win_rate_estricto = ganadores / n * 100
    win_rate_sin_be = ganadores / (ganadores + perdedores) * 100 if (ganadores + perdedores) > 0 else np.nan

    total_r = df['Beneficio_R'].sum()
    promedio_r = df['Beneficio_R'].mean()

    dias_operados = df['Fecha_dt'].nunique()
    r_por_dia = df.groupby('Fecha_dt')['Beneficio_R'].sum()

    return {
        'n_trades': n, 'ganadores': int(ganadores), 'perdedores': int(perdedores), 'breakeven': int(breakeven),
        'win_rate_%_estricto': round(win_rate_estricto, 2),
        'win_rate_%_sin_breakeven': round(win_rate_sin_be, 2),
        'total_R': round(total_r, 2), 'promedio_R_por_trade': round(promedio_r, 4),
        'dias_operados': dias_operados,
        'promedio_R_por_dia': round(r_por_dia.mean(), 4),
        'mejor_dia_R': round(r_por_dia.max(), 2), 'peor_dia_R': round(r_por_dia.min(), 2),
    }


def analisis_semanal(df):
    df = df.copy()
    df['semana'] = df['Fecha_dt'].dt.to_period('W-SUN')
    r_semanal = df.groupby('semana')['Beneficio_R'].sum()
    semanas_cumplieron_2R = (r_semanal >= 2).sum()
    return r_semanal, semanas_cumplieron_2R, len(r_semanal)


def racha_maxima(serie_r):
    racha_actual_g, racha_actual_p = 0, 0
    max_g, max_p = 0, 0
    for r in serie_r:
        if r > 0:
            racha_actual_g += 1
            racha_actual_p = 0
        elif r < 0:
            racha_actual_p += 1
            racha_actual_g = 0
        else:
            racha_actual_g, racha_actual_p = 0, 0
        max_g = max(max_g, racha_actual_g)
        max_p = max(max_p, racha_actual_p)
    return max_g, max_p


def drawdown_en_R(serie_r):
    curva = serie_r.cumsum()
    pico = curva.cummax()
    dd = curva - pico
    return dd.min(), curva


def por_categoria(df, columna):
    resultados = []
    for val, sub in df.groupby(columna):
        n = len(sub)
        wr = (sub['Beneficio_R'] > 0).sum() / n * 100
        resultados.append({columna: val, 'n': n, 'win_rate_%': round(wr, 1),
                            'total_R': round(sub['Beneficio_R'].sum(), 2),
                            'promedio_R': round(sub['Beneficio_R'].mean(), 4)})
    return pd.DataFrame(resultados).sort_values('n', ascending=False)


if __name__ == '__main__':
    df = cargar_todo()
    print("=" * 100)
    print(f"HISTORIAL COMPLETO DE FABIAN -- {df['Fecha_dt'].min().date()} a {df['Fecha_dt'].max().date()}")
    print(f"Total de filas (incluye hedge positions): {len(df)}")
    print("=" * 100)

    print("\n--- TRADE POR TRADE (completo) ---")
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 220)
    print(df[['Fecha_dt', 'Día', 'modelo_limpio', 'es_hedge', 'Patrón de entrada', 'Buy / Sell',
               'Resultado', 'Beneficio_R']].to_string(index=False))

    print("\n\n" + "=" * 100)
    print("METRICAS GENERALES")
    print("=" * 100)
    m = metricas_generales(df)
    for k, v in m.items():
        print(f"  {k}: {v}")

    print("\n--- SOLO TRADES PRINCIPALES (excluyendo hedge positions) ---")
    m_sin_hedge = metricas_generales(df[~df['es_hedge']])
    for k, v in m_sin_hedge.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 100)
    print("ANALISIS SEMANAL -- objetivo declarado: 2R por semana")
    print("=" * 100)
    r_semanal, cumplieron, total_semanas = analisis_semanal(df)
    print(f"Semanas operadas: {total_semanas} | Semanas que alcanzaron o superaron 2R: {cumplieron} ({cumplieron/total_semanas*100:.1f}%)")
    print(f"Promedio R por semana: {r_semanal.mean():.3f} | Mediana: {r_semanal.median():.2f}")
    print("\nDetalle semanal:")
    print(r_semanal.to_string())

    print("\n" + "=" * 100)
    print("RACHAS Y DRAWDOWN (en unidades R, trade por trade)")
    print("=" * 100)
    max_g, max_p = racha_maxima(df['Beneficio_R'].values)
    print(f"Racha maxima de operaciones ganadoras seguidas: {max_g}")
    print(f"Racha maxima de operaciones perdedoras seguidas: {max_p}")
    dd_min, curva_r = drawdown_en_R(df['Beneficio_R'])
    print(f"Drawdown maximo (en R, sobre la curva acumulada de trades): {dd_min:.2f}R")
    print(f"R acumulado final: {curva_r.iloc[-1]:.2f}R")

    print("\n" + "=" * 100)
    print("DESGLOSE POR MODELO DE ENTRADA")
    print("=" * 100)
    print(por_categoria(df, 'modelo_limpio').to_string(index=False))

    print("\n" + "=" * 100)
    print("DESGLOSE POR PATRON DE ENTRADA")
    print("=" * 100)
    print(por_categoria(df.dropna(subset=['Patrón de entrada']), 'Patrón de entrada').to_string(index=False))

    print("\n" + "=" * 100)
    print("DESGLOSE POR DIRECCION (Buy/Sell)")
    print("=" * 100)
    print(por_categoria(df, 'Buy / Sell').to_string(index=False))

    print("\n" + "=" * 100)
    print("DESGLOSE POR DIA DE LA SEMANA")
    print("=" * 100)
    print(por_categoria(df, 'Día').to_string(index=False))

    df.to_csv(os.path.join(CARPETA, 'fabian_consolidado_limpio.csv'), index=False)
    print(f"\nGuardado consolidado en fabian_consolidado_limpio.csv")
