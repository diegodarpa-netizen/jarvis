"""
04/09/2026, a pedido de Diego: 1 y 2 confirmaciones (base 3%, incremento
2%) corridas sobre (a) las 482 operaciones completas (todas las
sesiones, sin restriccion) y (b) las 160 de la Gestion Hibrida
(Pre-NY+Asia, dias limitados + tope +3R + corte 1TP/2SL). Ademas:
semanas negativas en la Gestion Hibrida bajo cada esquema, y si no
existen, stress test forzando semanas negativas.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, DIAS_ORDEN
from escalera_de_riesgo_martingala import max_drawdown, CAPITAL_INICIAL
from antimartingala_2confirmaciones import simular_antimartingala_2conf
from grilla_pasos_y_patron_rachas import simular_pasos  # no se usa, solo referencia

CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'

np.random.seed(231)
BASE = 3.0
INCREMENTO = 2.0


def simular_nconf_fechas(fechas, r_seq, n_confirmaciones, base_pct=BASE, incremento_pct=INCREMENTO,
                          tope_extra=4, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    filas = []
    racha = 0
    for f, r in zip(fechas, r_seq):
        if racha < n_confirmaciones:
            riesgo = base_pct / 100
        else:
            nivel_extra = min(racha - (n_confirmaciones - 1), tope_extra)
            riesgo = (base_pct + incremento_pct * nivel_extra) / 100
        cambio = capital * riesgo * r
        capital += cambio
        filas.append(dict(fecha=f, riesgo_pct=riesgo * 100, r=r, cambio_usd=cambio, capital=capital))
        racha = racha + 1 if r > 0 else 0
    return pd.DataFrame(filas)


def resumen(df_sim, nombre):
    final = df_sim['capital'].iloc[-1]
    ret = (final / CAPITAL_INICIAL - 1) * 100
    dd = max_drawdown([CAPITAL_INICIAL] + list(df_sim['capital']))
    print(f"{nombre}: USD {CAPITAL_INICIAL:.0f} -> USD {final:,.0f}  retorno {ret:+.1f}%  drawdown {dd:+.1f}%")
    return final, ret, dd


if __name__ == '__main__':
    df_todas = cargar_todo_cronologico()
    fechas_todas = df_todas['Fecha_dt'].tolist()
    r_todas = df_todas['Beneficio_R'].values

    df_hib = pd.read_csv(os.path.join(CARPETA, 'gestion_hibrida_resultado.csv'))
    df_hib['Fecha_dt'] = pd.to_datetime(df_hib['Fecha_dt'])
    df_hib = df_hib.sort_values(['Fecha_dt', 'Hora apertura (NY)'])
    fechas_hib = df_hib['Fecha_dt'].tolist()
    r_hib = df_hib['Beneficio_R'].values

    print("=" * 100)
    print(f"COMPARACION -- Base {BASE}% + incremento {INCREMENTO}%, 1 vs 2 confirmaciones")
    print("=" * 100)
    resultados = {}
    for universo, fechas, r_seq in [('482 operaciones (todas)', fechas_todas, r_todas),
                                     ('160 operaciones (Gestion Hibrida)', fechas_hib, r_hib)]:
        print(f"\n--- {universo} ---")
        for n_conf in [1, 2]:
            sim = simular_nconf_fechas(fechas, r_seq, n_conf)
            resumen(sim, f"{n_conf} confirmacion(es)")
            resultados[(universo, n_conf)] = sim

    # ══════════ Semanas negativas -- Gestion Hibrida ══════════
    print(f"\n\n{'=' * 100}\nSEMANAS NEGATIVAS -- Gestion Hibrida (160 operaciones)\n{'=' * 100}")
    for n_conf in [1, 2]:
        sim = resultados[('160 operaciones (Gestion Hibrida)', n_conf)]
        sim['semana_iso'] = sim['fecha'].dt.isocalendar().year.astype(str) + '-W' + sim['fecha'].dt.isocalendar().week.astype(str)
        r_por_semana_usd = sim.groupby('semana_iso')['cambio_usd'].sum()
        neg = (r_por_semana_usd < 0).sum()
        total_semanas = len(r_por_semana_usd)
        print(f"\n{n_conf} confirmacion(es): {total_semanas} semanas -- {neg} NEGATIVAS")
        if neg > 0:
            print("  Semanas negativas:")
            for sem, val in r_por_semana_usd[r_por_semana_usd < 0].items():
                print(f"    {sem}: USD {val:+,.2f}")
        else:
            print("  Ninguna semana termino en perdida neta con esta gestion.")

    pd.DataFrame([dict(universo=u, n_conf=n, capital_final=round(resultados[(u,n)]['capital'].iloc[-1],2),
                        retorno_pct=round((resultados[(u,n)]['capital'].iloc[-1]/CAPITAL_INICIAL-1)*100,1))
                  for u in ['482 operaciones (todas)', '160 operaciones (Gestion Hibrida)'] for n in [1,2]]
                 ).to_csv(os.path.join(CARPETA, 'comparacion_482_vs_160_1y2conf_tabla.csv'), index=False)
