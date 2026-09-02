"""
Consolidacion de las operaciones reales de Fabian en Pre-NY (07:00-09:00)
y Asia (20:02-22:00), a pedido de Diego (02/09/2026): "solo tomemos la
info que nos da fabian, sin correr ningun codigo... archivo por archivo,
operacion por operacion, dia por dia, no dejamos nada al azar".

Fuente: exports de Notion via WhatsApp (mismo origen que
fabian_consolidado_limpio.csv de NY), 2 archivos trimestrales para Pre-NY
(Q1-26, Q3-26) y 4 para Asia (Q1-26, Q2-26, Q3-26 x2). Los archivos mas
viejos usan un formato de columnas distinto (minuscula, en español
informal) al que se usa desde mediados de 2026 -- se normalizan ambos al
formato final (el mismo de fabian_consolidado_limpio.csv).

Filas sin operacion (Fabian anoto el dia pero "no trades" / sin entrada)
se descartan del dataset de operaciones -- no son trades.
"""
import pandas as pd
import numpy as np
import glob
import os
import datetime

CARPETA = os.path.dirname(__file__)

MAPA_RESULTADO = {
    'tp': 'Take Profit', 'sl': 'Stop Loss', 'breakeven': 'Break Even',
    'take profit': 'Take Profit', 'stop loss': 'Stop Loss',
}


def normalizar_viejo(df):
    """Formato viejo: Fecha,dia,entradas,Patron de entrada,hora de
    entrada,hora de salida,Buy/sell,resultado,resultado (R),trades
    tp,trades SL,Entradas"""
    df = df.rename(columns={
        'dia': 'Día', 'entradas': 'Modelo de entrada',
        'Patron de entrada': 'Patrón de entrada',
        'hora de entrada': 'Hora apertura (NY)',
        'hora de salida': 'Hora cierre  (NY)',
        'Buy/sell': 'Buy / Sell',
        'resultado': 'Resultado',
        'resultado (R)': 'Beneficio (R)',
        'trades tp': 'Trades tp', 'trades SL': 'Trades sl',
    })
    df['Resultado'] = df['Resultado'].astype(str).str.strip().str.lower().map(MAPA_RESULTADO).fillna(df['Resultado'])
    df['Buy / Sell'] = df['Buy / Sell'].astype(str).str.strip().str.capitalize()
    return df


def normalizar_nuevo(df):
    """Formato nuevo: ya coincide con fabian_consolidado_limpio.csv,
    solo homogeneizar el nombre de la columna R:B."""
    ren = {}
    if 'R:B max' in df.columns:
        ren['R:B max'] = 'R:B máx'
    return df.rename(columns=ren)


COLUMNAS_FINALES = ['Fecha', 'Día', 'Modelo de entrada', 'Patrón de entrada',
                     'Hora apertura (NY)', 'Hora cierre  (NY)', 'Buy / Sell',
                     'Resultado', 'Beneficio (R)', 'Trades tp', 'Trades sl']

DIAS_ES = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']


def cargar_sesion(archivos):
    dfs = []
    for f in archivos:
        df = pd.read_csv(f)
        df.columns = [c.strip() for c in df.columns]
        if 'entradas' in df.columns:
            df = normalizar_viejo(df)
        else:
            df = normalizar_nuevo(df)
        for c in COLUMNAS_FINALES:
            if c not in df.columns:
                df[c] = np.nan
        dfs.append(df[COLUMNAS_FINALES])
    full = pd.concat(dfs, ignore_index=True)
    # descartar filas sin fecha (basura) y sin operacion real (dia anotado
    # sin entrada -- "no trades")
    full = full.dropna(subset=['Fecha'])
    full = full[full['Modelo de entrada'].notna()].reset_index(drop=True)

    full['Fecha_dt'] = pd.to_datetime(full['Fecha'], format='%d/%m/%Y', errors='coerce')
    filas_fecha_invalida = full[full['Fecha_dt'].isna()]
    if len(filas_fecha_invalida):
        print("¡OJO! filas con fecha no parseable (revisar a mano):")
        print(filas_fecha_invalida)

    full['Beneficio_R'] = full['Beneficio (R)'].astype(str).str.replace(',', '.').str.strip()
    full['Beneficio_R'] = pd.to_numeric(full['Beneficio_R'], errors='coerce')
    # Break Even sin valor de R -> 0 (semantica correcta, no "sin dato")
    full.loc[(full['Resultado'] == 'Break Even') & full['Beneficio_R'].isna(), 'Beneficio_R'] = 0.0
    # UNICO caso real de dato faltante encontrado (revisado a mano,
    # 02/09/2026): 20/03/2026 Pre-NY, MER Sell, "Stop Loss" sin R anotado
    # -- se asume -1R (el valor estandar de una perdida simple en este
    # dataset), marcado explicitamente para que quede claro que es un
    # supuesto, no un dato real de Fabian.
    mask_sl_sin_r = (full['Fecha'] == '20/03/2026') & (full['Resultado'] == 'Stop Loss') & full['Beneficio_R'].isna()
    full.loc[mask_sl_sin_r, 'Beneficio_R'] = -1.0
    full['es_hedge'] = full['Modelo de entrada'].astype(str).str.contains('Hegde', case=False, na=False)
    full['modelo_limpio'] = full['Modelo de entrada'].astype(str).str.replace('Hegde Position, ', '', regex=False).str.strip()
    full = full.sort_values('Fecha_dt').reset_index(drop=True)
    return full


def validar_dia_semana(df, nombre_sesion):
    """Chequea que el 'Día' anotado coincida con el dia de semana real de
    la 'Fecha' -- asi encontramos los mismos errores de tipeo que en NY
    (08/02 y 10/02/2026)."""
    print(f"\n-- Validacion dia de semana vs fecha real ({nombre_sesion}) --")
    problemas = 0
    for idx, row in df.iterrows():
        if pd.isna(row['Fecha_dt']):
            continue
        dia_real = DIAS_ES[row['Fecha_dt'].weekday()]
        dia_anotado = str(row['Día']).strip().lower()
        # normalizar tildes simples
        dia_anotado_norm = dia_anotado.replace('miercoles', 'miércoles').replace('sabado', 'sábado')
        if dia_anotado_norm != dia_real:
            print(f"  {row['Fecha']} -- anotado '{row['Día']}', el real es '{dia_real}' "
                  f"({row['Buy / Sell']} {row['Modelo de entrada']} {row['Hora apertura (NY)']})")
            problemas += 1
    if problemas == 0:
        print("  Sin problemas -- todas las fechas coinciden con su dia de semana real.")
    return problemas


def metricas(df, nombre_sesion):
    n = len(df)
    ganadores = (df['Beneficio_R'] > 0).sum()
    perdedores = (df['Beneficio_R'] < 0).sum()
    be = (df['Beneficio_R'] == 0).sum()
    sin_dato = df['Beneficio_R'].isna().sum()
    wr = ganadores / (ganadores + perdedores) * 100 if (ganadores + perdedores) > 0 else float('nan')
    total_r = df['Beneficio_R'].sum()
    avg_r = df['Beneficio_R'].mean()
    print(f"\n{'=' * 80}\n{nombre_sesion} -- {n} operaciones ({df['Fecha_dt'].min().date()} -> {df['Fecha_dt'].max().date()})\n{'=' * 80}")
    print(f"  Ganadoras: {ganadores} ({wr:.1f}% WR excl. BE)  Perdedoras: {perdedores}  BE: {be}  Sin dato R: {sin_dato}")
    print(f"  R total: {total_r:+.1f}R   R promedio: {avg_r:+.3f}R")
    print(f"  Dias operados: {df['Fecha_dt'].nunique()}")
    print(f"  Hedge: {df['es_hedge'].sum()} ({df['es_hedge'].sum()/n*100:.1f}%)")
    print("  -- por modelo --")
    print(df.groupby('modelo_limpio')['Beneficio_R'].agg(['count', 'mean', 'sum']).round(3).to_string())
    print("  -- por direccion --")
    print(df.groupby('Buy / Sell')['Beneficio_R'].agg(['count', 'mean', 'sum']).round(3).to_string())


if __name__ == '__main__':
    pre_ny_files = sorted(glob.glob(os.path.join(CARPETA, 'raw_pre_ny', '*.csv')))
    asia_files = sorted(glob.glob(os.path.join(CARPETA, 'raw_asia', '*.csv')))

    pre_ny = cargar_sesion(pre_ny_files)
    asia = cargar_sesion(asia_files)

    validar_dia_semana(pre_ny, 'Pre-NY')
    validar_dia_semana(asia, 'Asia')

    pre_ny.to_csv(os.path.join(CARPETA, 'pre_ny_consolidado.csv'), index=False)
    asia.to_csv(os.path.join(CARPETA, 'asia_consolidado.csv'), index=False)

    metricas(pre_ny, 'PRE NEW YORK (07:00-09:00 NY)')
    metricas(asia, 'ASIA (20:02-22:00 NY)')
