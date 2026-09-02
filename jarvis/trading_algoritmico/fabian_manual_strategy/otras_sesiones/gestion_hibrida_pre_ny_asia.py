"""
Gestion hibrida Pre-NY + Asia (02/09/2026), parametros dados por Diego
(de Fabian) sobre los datos en bruto ya consolidados
(pre_ny_consolidado.csv, asia_consolidado.csv):

1. Dias operativos: Pre-NY solo Lunes-Jueves; Asia solo Lunes, Miercoles
   y Jueves.
2. Limite semanal de ganancia: +3R combinado entre las 2 sesiones -- al
   alcanzarlo, se frena TODA la operativa (ambas sesiones) el resto de
   esa semana.
3. Sin limite semanal de perdida.
4. Cada dia de cada sesion se corta en el primer TP o en el 2do SL (los
   "3 escenarios diarios" que describio Fabian son las 3 formas posibles
   en que puede terminar un dia bajo esta regla: a) 1 TP, b) 1 SL + 1 TP,
   c) 2 SL -- no es una regla nueva, es la misma "1 TP o 2 SL frena el
   dia" que ya usamos en NY, aplicada tambien aca).

IMPORTANTE -- esto es una SIMULACION sobre datos reales, no lo que
Fabian efectivamente hizo cada dia: se encontro al menos un dia (Pre-NY,
29/07/2026) con 3 operaciones reales (incluyendo un 2do TP despues del
primero), que bajo esta regla se recorta a solo la 1ra operacion. Se
declara explicitamente cada vez que se recorta un dia, para que quede
trazable.
"""
import pandas as pd
import numpy as np
import os

CARPETA = os.path.dirname(__file__)
DIAS_PRE_NY = {'lunes', 'martes', 'miercoles', 'miércoles', 'jueves'}
DIAS_ASIA = {'lunes', 'miercoles', 'miércoles', 'jueves'}
TOPE_SEMANAL_R = 3.0


def recortar_por_dia(df):
    """Corta cada (dia, sesion) en el primer TP o el 2do SL. Devuelve el
    df recortado + una lista de (fecha, operaciones descartadas) para
    trazabilidad."""
    filas_finales = []
    recortes = []
    for fecha, g in df.sort_values('Hora apertura (NY)').groupby('Fecha_dt'):
        g = g.reset_index(drop=True)
        tp_count, sl_count = 0, 0
        corte_en = None
        for i, row in g.iterrows():
            filas_finales.append(row)
            if row['Resultado'] == 'Take Profit':
                tp_count += 1
            elif row['Resultado'] == 'Stop Loss':
                sl_count += 1
            if tp_count >= 1 or sl_count >= 2:
                corte_en = i
                break
        if corte_en is not None and corte_en < len(g) - 1:
            descartadas = g.iloc[corte_en + 1:]
            recortes.append((fecha, len(descartadas), descartadas[['Hora apertura (NY)', 'Resultado', 'Beneficio_R']].values.tolist()))
    return pd.DataFrame(filas_finales), recortes


def aplicar_tope_semanal(df):
    """Recorta cronologicamente (combinando las 2 sesiones) una vez que
    el R acumulado de la semana ISO llega a +3R. Sin piso de perdida."""
    df = df.sort_values(['Fecha_dt', 'Hora apertura (NY)']).reset_index(drop=True)
    df['semana_iso'] = df['Fecha_dt'].dt.isocalendar().year.astype(str) + '-W' + df['Fecha_dt'].dt.isocalendar().week.astype(str)

    filas_ok = []
    cortes_semana = []
    for semana, g in df.groupby('semana_iso', sort=False):
        acumulado = 0.0
        for i, row in g.iterrows():
            filas_ok.append(row)
            acumulado += row['Beneficio_R']
            if acumulado >= TOPE_SEMANAL_R:
                resto = len(g) - (list(g.index).index(i) + 1)
                if resto > 0:
                    cortes_semana.append((semana, resto, acumulado))
                break
    return pd.DataFrame(filas_ok), cortes_semana


def main():
    pre = pd.read_csv(os.path.join(CARPETA, 'pre_ny_consolidado.csv'))
    asia = pd.read_csv(os.path.join(CARPETA, 'asia_consolidado.csv'))
    pre['Fecha_dt'] = pd.to_datetime(pre['Fecha_dt'])
    asia['Fecha_dt'] = pd.to_datetime(asia['Fecha_dt'])

    pre['dia_norm'] = pre['Día'].str.strip().str.lower()
    asia['dia_norm'] = asia['Día'].str.strip().str.lower()

    pre_f = pre[pre['dia_norm'].isin(DIAS_PRE_NY)].copy()
    asia_f = asia[asia['dia_norm'].isin(DIAS_ASIA)].copy()
    print(f"Pre-NY: {len(pre)} -> {len(pre_f)} tras filtro de dias (Lun-Jue)")
    print(f"Asia:   {len(asia)} -> {len(asia_f)} tras filtro de dias (Lun/Mie/Jue)")

    pre_f['sesion'] = 'Pre-NY'
    asia_f['sesion'] = 'Asia'

    pre_rec, recortes_pre = recortar_por_dia(pre_f)
    asia_rec, recortes_asia = recortar_por_dia(asia_f)
    print(f"\nPre-NY: {len(pre_f)} -> {len(pre_rec)} tras recorte diario (1 TP o 2 SL)")
    print(f"  Dias recortados: {len(recortes_pre)}")
    for fecha, n, desc in recortes_pre:
        print(f"    {fecha.date()}: se descartan {n} operacion(es) -> {desc}")
    print(f"Asia:   {len(asia_f)} -> {len(asia_rec)} tras recorte diario (1 TP o 2 SL)")
    print(f"  Dias recortados: {len(recortes_asia)}")
    for fecha, n, desc in recortes_asia:
        print(f"    {fecha.date()}: se descartan {n} operacion(es) -> {desc}")

    combinado = pd.concat([pre_rec, asia_rec], ignore_index=True)
    combinado_final, cortes_semana = aplicar_tope_semanal(combinado)
    print(f"\nCombinado (Pre-NY + Asia): {len(combinado)} -> {len(combinado_final)} tras tope semanal +{TOPE_SEMANAL_R}R")
    print(f"  Semanas donde se corto por tope: {len(cortes_semana)}")
    for semana, resto, acumulado in cortes_semana:
        print(f"    {semana}: alcanzo {acumulado:+.2f}R, se descartan {resto} operacion(es) restantes de la semana")

    combinado_final = combinado_final.sort_values(['Fecha_dt', 'Hora apertura (NY)']).reset_index(drop=True)
    combinado_final.to_csv(os.path.join(CARPETA, 'gestion_hibrida_resultado.csv'), index=False)

    n = len(combinado_final)
    wins = (combinado_final['Beneficio_R'] > 0).sum()
    losses = (combinado_final['Beneficio_R'] < 0).sum()
    be = (combinado_final['Beneficio_R'] == 0).sum()
    total_r = combinado_final['Beneficio_R'].sum()
    print(f"\n{'=' * 80}")
    print(f"GESTION HIBRIDA FINAL -- {n} operaciones ({combinado_final['Fecha_dt'].min().date()} -> {combinado_final['Fecha_dt'].max().date()})")
    print(f"{'=' * 80}")
    print(f"Ganadoras: {wins} ({wins/(wins+losses)*100:.1f}% WR excl. BE)  Perdedoras: {losses}  BE: {be}")
    print(f"R total: {total_r:+.1f}R   R promedio: {combinado_final['Beneficio_R'].mean():+.3f}R")
    print(f"Semanas operadas: {combinado_final['semana_iso'].nunique()}")
    r_por_semana = combinado_final.groupby('semana_iso')['Beneficio_R'].sum()
    print(f"R promedio por semana: {r_por_semana.mean():+.3f}R   (max {r_por_semana.max():+.2f}R / min {r_por_semana.min():+.2f}R)")
    print(f"Semanas que llegaron al tope de +{TOPE_SEMANAL_R}R: {(r_por_semana >= TOPE_SEMANAL_R).sum()} de {len(r_por_semana)}")


if __name__ == '__main__':
    main()
