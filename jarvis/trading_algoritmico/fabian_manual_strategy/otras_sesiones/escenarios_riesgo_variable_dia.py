"""
Escenarios de riesgo VARIABLE por dia de semana (02/09/2026), a pedido de
Diego: subir riesgo en los dias con mejor patron (Miercoles) y bajarlo en
los mas flojos (Viernes, Domingo/madrugada-Asia), usando la serie
CRONOLOGICA real combinada de las 3 sesiones (NY + Pre-NY + Asia, 482
operaciones reales, sin recortar por gestion hibrida -- "todos los datos
que tenemos con Fabian").

Cada trade aplica el riesgo % que le corresponde a SU dia de semana
(compuesto, capital += capital * riesgo_dia * R), en el orden
cronologico real (Pre-NY -> NY -> Asia dentro del mismo dia calendario).

Ademas de los escenarios manuales que planteo Diego, se calcula un
tamaño de posicion sugerido por dia de semana via CRITERIO DE KELLY
(f* = p - q/b, con p = win rate y b = ratio ganancia/perdida promedio,
ambos calculados a nivel de OPERACION -- no de dia -- para cada dia de
semana) como referencia estadistica, no como recomendacion ciega (Kelly
completo es agresivo; se muestra tambien medio-Kelly).
"""
import pandas as pd
import numpy as np
import os

CARPETA = os.path.dirname(__file__)
NY_CSV = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
DIAS_ORDEN = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
ORDEN_SESION = {'Pre-NY': 0, 'NY': 1, 'Asia': 2}
CAPITAL_INICIAL = 1000.0


def cargar_todo_cronologico():
    ny = pd.read_csv(NY_CSV)
    ny['Fecha_dt'] = pd.to_datetime(ny['Fecha_dt'])
    ny['sesion'] = 'NY'
    ny['hora'] = ny['Hora apertura (NY)']

    pre = pd.read_csv(os.path.join(CARPETA, 'pre_ny_consolidado.csv'))
    pre['Fecha_dt'] = pd.to_datetime(pre['Fecha_dt'])
    pre['sesion'] = 'Pre-NY'
    pre['hora'] = pre['Hora apertura (NY)']

    asia = pd.read_csv(os.path.join(CARPETA, 'asia_consolidado.csv'))
    asia['Fecha_dt'] = pd.to_datetime(asia['Fecha_dt'])
    asia['sesion'] = 'Asia'
    asia['hora'] = asia['Hora apertura (NY)']

    cols = ['Fecha_dt', 'hora', 'Beneficio_R', 'sesion']
    full = pd.concat([ny[cols], pre[cols], asia[cols]], ignore_index=True)
    full['dia_semana'] = full['Fecha_dt'].dt.dayofweek.map(dict(enumerate(DIAS_ORDEN)))
    full['orden_sesion'] = full['sesion'].map(ORDEN_SESION)
    full = full.sort_values(['Fecha_dt', 'orden_sesion', 'hora']).reset_index(drop=True)
    return full


def curva_riesgo_variable(df, riesgo_por_dia, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    valores = [capital]
    for _, row in df.iterrows():
        riesgo = riesgo_por_dia.get(row['dia_semana'], 0.0)
        capital += capital * riesgo * row['Beneficio_R']
        valores.append(capital)
    return valores


def max_drawdown(valores):
    s = pd.Series(valores)
    pico = s.cummax()
    dd = (s - pico) / pico * 100
    return dd.min()


def peor_racha_perdedora_real(df, riesgo_por_dia, n=3):
    """Aplica una racha real de n perdidas seguidas (usa el R real y el
    riesgo del dia real de cada una) sobre capital=1 para medir el % de
    golpe."""
    capital = 1.0
    racha = []
    peor = 0.0
    for _, row in df.iterrows():
        r = row['Beneficio_R']
        riesgo = riesgo_por_dia.get(row['dia_semana'], 0.0)
        if r < 0:
            racha.append((riesgo, r))
        else:
            racha = []
        if len(racha) >= n:
            c = 1.0
            for riesgo_i, r_i in racha[-n:]:
                c *= (1 + riesgo_i * r_i)
            peor = min(peor, c - 1.0)
    return peor * 100


def kelly_por_dia(df):
    print("\n-- Kelly por dia de semana (a nivel de OPERACION, no de dia) --")
    print(f"{'Dia':<12}{'N ops':>7}{'Win %':>8}{'Avg win R':>11}{'Avg loss R':>12}{'Kelly f*':>10}{'1/2 Kelly':>11}")
    resumen = {}
    for dia in DIAS_ORDEN:
        g = df[df['dia_semana'] == dia]
        if len(g) < 10:
            continue
        wins = g[g['Beneficio_R'] > 0]['Beneficio_R']
        losses = g[g['Beneficio_R'] < 0]['Beneficio_R']
        if len(wins) == 0 or len(losses) == 0:
            continue
        p = len(wins) / (len(wins) + len(losses))
        q = 1 - p
        avg_win = wins.mean()
        avg_loss = abs(losses.mean())
        b = avg_win / avg_loss
        kelly = p - q / b
        kelly = max(kelly, 0.0)
        print(f"{dia:<12}{len(g):>7}{p*100:>7.1f}%{avg_win:>+11.3f}{-avg_loss:>+12.3f}{kelly*100:>9.1f}%{kelly/2*100:>10.1f}%")
        resumen[dia] = kelly
    return resumen


if __name__ == '__main__':
    df = cargar_todo_cronologico()
    print(f"Base: {len(df)} operaciones reales combinadas (NY+Pre-NY+Asia), "
          f"{df['Fecha_dt'].min().date()} -> {df['Fecha_dt'].max().date()}")

    kelly = kelly_por_dia(df)

    escenarios = {
        'E0 -- 3% parejo (control)': {d: 0.03 for d in DIAS_ORDEN},
        'E1 -- Miercoles 15%, resto 3% (ejemplo de Diego)': {**{d: 0.03 for d in DIAS_ORDEN}, 'Miércoles': 0.15},
        'E2 -- Escalonado por patron empirico': {
            'Lunes': 0.05, 'Martes': 0.08, 'Miércoles': 0.15, 'Jueves': 0.08,
            'Viernes': 0.02, 'Sábado': 0.0, 'Domingo': 0.01,
        },
        'E3 -- Conservador (Miercoles 10%, resto 3%, floja 1%)': {
            'Lunes': 0.03, 'Martes': 0.03, 'Miércoles': 0.10, 'Jueves': 0.03,
            'Viernes': 0.01, 'Sábado': 0.0, 'Domingo': 0.01,
        },
        'E4 -- Medio-Kelly por dia (estadistico)': {d: kelly.get(d, 0.0) / 2 for d in DIAS_ORDEN},
    }

    print(f"\n{'Escenario':<48}{'Capital final':>15}{'Retorno':>11}{'Drawdown max':>14}{'Peor racha 3L':>15}")
    print("-" * 105)
    resumen_rows = []
    for nombre, riesgo_por_dia in escenarios.items():
        valores = curva_riesgo_variable(df, riesgo_por_dia)
        final = valores[-1]
        ret = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        racha = peor_racha_perdedora_real(df, riesgo_por_dia)
        print(f"{nombre:<48}USD {final:>10,.0f}{ret:>+10.1f}%{dd:>+13.1f}%{racha:>+14.1f}%")
        resumen_rows.append(dict(escenario=nombre, capital_final=round(final, 2), retorno_pct=round(ret, 1),
                                  drawdown_max_pct=round(dd, 1), peor_racha_3L_pct=round(racha, 1),
                                  riesgo_por_dia=riesgo_por_dia))

    pd.DataFrame(resumen_rows).to_csv(os.path.join(CARPETA, 'escenarios_riesgo_variable_dia_resumen.csv'), index=False)
