"""
Patron por dia de semana (02/09/2026), a pedido de Diego: de TODOS los
datos reales de Fabian (NY + Pre-NY + Asia), ver si hay un dia de la
semana con mas dias positivos que otros -- para evaluar subir riesgo ahi.

Metodologia: se agrupa por DIA CALENDARIO (sumando el R de todas las
operaciones de ese dia, en cualquier sesion que haya operado), y se
clasifica el dia como positivo/negativo/breakeven segun el R neto de ese
dia -- no por operacion individual (un dia puede tener una operacion
perdedora y otra ganadora y cerrar positivo en neto).

Se corre 2 veces: (1) cada sesion por separado, (2) las 3 combinadas por
dia calendario -- para no tapar un patron especifico de una sesion, ni
perder el panorama combinado que pidio Diego.

Chequeo de significancia: con pocos dias por dia-de-semana, un %
llamativo puede ser ruido. Se agrega un test binomial simple (¿el % de
dias positivos de ESE dia de semana es distinguible del % de dias
positivos del resto de la semana?) via bootstrap, no solo el numero
crudo.
"""
import pandas as pd
import numpy as np
import os

CARPETA = os.path.dirname(__file__)
NY_CSV = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
DIAS_ORDEN = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
DIAS_ES = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

np.random.seed(42)


def cargar_todo():
    ny = pd.read_csv(NY_CSV)
    ny['Fecha_dt'] = pd.to_datetime(ny['Fecha_dt'])
    ny['sesion'] = 'NY'

    pre = pd.read_csv(os.path.join(CARPETA, 'pre_ny_consolidado.csv'))
    pre['Fecha_dt'] = pd.to_datetime(pre['Fecha_dt'])
    pre['sesion'] = 'Pre-NY'

    asia = pd.read_csv(os.path.join(CARPETA, 'asia_consolidado.csv'))
    asia['Fecha_dt'] = pd.to_datetime(asia['Fecha_dt'])
    asia['sesion'] = 'Asia'

    cols = ['Fecha_dt', 'Beneficio_R', 'sesion']
    full = pd.concat([ny[cols], pre[cols], asia[cols]], ignore_index=True)
    return full


def dias_positivos_negativos(df):
    """df: operaciones (Fecha_dt, Beneficio_R). Agrupa por dia calendario
    -> R neto del dia, y clasifica."""
    r_dia = df.groupby('Fecha_dt')['Beneficio_R'].sum().reset_index()
    r_dia['dia_semana'] = r_dia['Fecha_dt'].dt.day_name(locale='es_ES.UTF-8') if False else r_dia['Fecha_dt'].dt.dayofweek.map(dict(enumerate(DIAS_ORDEN)))
    r_dia['positivo'] = r_dia['Beneficio_R'] > 0
    r_dia['negativo'] = r_dia['Beneficio_R'] < 0
    return r_dia


def resumen_por_dia_semana(r_dia, nombre):
    print(f"\n{'=' * 90}\n{nombre}\n{'=' * 90}")
    total_dias = len(r_dia)
    total_pos = r_dia['positivo'].sum()
    print(f"Total dias operados: {total_dias}  ({total_pos} positivos = {total_pos/total_dias*100:.1f}% -- linea base)")
    print(f"{'Dia':<12}{'N dias':>8}{'Positivos':>11}{'Negativos':>11}{'BE':>5}{'% Positivo':>12}{'R total':>10}{'R prom/dia':>12}")
    tabla = []
    for dia in DIAS_ORDEN:
        g = r_dia[r_dia['dia_semana'] == dia]
        if len(g) == 0:
            continue
        n = len(g)
        pos = g['positivo'].sum()
        neg = g['negativo'].sum()
        be = n - pos - neg
        pct = pos / n * 100
        r_total = g['Beneficio_R'].sum()
        r_prom = g['Beneficio_R'].mean()
        print(f"{dia:<12}{n:>8}{pos:>11}{neg:>11}{be:>5}{pct:>11.1f}%{r_total:>+10.1f}{r_prom:>+12.3f}")
        tabla.append(dict(dia=dia, n_dias=n, positivos=pos, negativos=neg, be=be,
                           pct_positivo=round(pct, 1), r_total=round(r_total, 2), r_promedio_dia=round(r_prom, 3)))
    return pd.DataFrame(tabla), total_pos / total_dias


def bootstrap_significancia(r_dia, tabla, pct_base, n_iter=5000):
    print(f"\n-- Test de significancia (bootstrap, {n_iter} iteraciones) --")
    print("¿El % de dias positivos de este dia de semana es distinguible del resto de la semana?")
    for _, row in tabla.iterrows():
        dia = row['dia']
        g_dia = r_dia[r_dia['dia_semana'] == dia]['positivo'].values
        g_resto = r_dia[r_dia['dia_semana'] != dia]['positivo'].values
        if len(g_dia) < 5:
            print(f"  {dia}: muestra muy chica ({len(g_dia)} dias) -- no evaluable, se ignora")
            continue
        obs_diff = g_dia.mean() - g_resto.mean()
        diffs = []
        combinado = np.concatenate([g_dia, g_resto])
        n_dia = len(g_dia)
        for _ in range(n_iter):
            np.random.shuffle(combinado)
            diffs.append(combinado[:n_dia].mean() - combinado[n_dia:].mean())
        diffs = np.array(diffs)
        p_value = (np.abs(diffs) >= np.abs(obs_diff)).mean()
        sig = "** SIGNIFICATIVO (p<0.05) **" if p_value < 0.05 else "no significativo (ruido probable)"
        print(f"  {dia}: {row['pct_positivo']:.1f}% vs {g_resto.mean()*100:.1f}% del resto -- p={p_value:.3f} -> {sig}")


if __name__ == '__main__':
    full = cargar_todo()

    print("\n\n" + "#" * 90)
    print("# 1) CADA SESION POR SEPARADO")
    print("#" * 90)
    for sesion in ['NY', 'Pre-NY', 'Asia']:
        r_dia = dias_positivos_negativos(full[full['sesion'] == sesion])
        tabla, base = resumen_por_dia_semana(r_dia, f"Sesion: {sesion}")
        bootstrap_significancia(r_dia, tabla, base)

    print("\n\n" + "#" * 90)
    print("# 2) LAS 3 SESIONES COMBINADAS POR DIA CALENDARIO")
    print("#" * 90)
    r_dia_combo = dias_positivos_negativos(full)
    tabla_combo, base_combo = resumen_por_dia_semana(r_dia_combo, "COMBINADO (NY + Pre-NY + Asia, por dia calendario)")
    bootstrap_significancia(r_dia_combo, tabla_combo, base_combo)

    tabla_combo.to_csv(os.path.join(CARPETA, 'patron_dia_semana_combinado.csv'), index=False)
