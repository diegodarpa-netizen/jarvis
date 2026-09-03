"""
"Escalera de riesgo" (Martingala clasica: duplicar tras cada perdida,
resetear a base tras la primera ganancia), 03/09/2026, a pedido de
Diego. 4 perfiles con 5 niveles cada uno:
  Conservador:    0.25 / 0.50 / 1 / 2 / 4 %
  Moderado:       0.50 / 1 / 2 / 4 / 8 %
  Arriesgado:     1 / 2 / 4 / 8 / 16 %
  Muy arriesgado: 2 / 4 / 8 / 16 / 32 %

Interpretacion (siguiendo el "Funcionamiento" que dio Diego, el mas
claro y operacional de los dos textos): gano -> arriesgo base. Pierdo ->
el proximo trade duplico. Gano de nuevo -> reseteo de golpe a base, sin
importar si ya recupere en dolares lo perdido o no.

Con SOLO 5 niveles definidos por perfil: si aparece una 5ta perdida
consecutiva (nivel 6), hay 2 formas de manejarlo y las comparamos las
DOS explicitamente, porque cambia todo el resultado:
  (A) TOPE: se queda en el nivel 5 (el mas alto definido) sin duplicar mas.
  (B) SIN TOPE (Martingala pura): sigue duplicando indefinidamente --
      en 'Muy arriesgado' el nivel 6 ya séria 64%, el 7 séria 128%
      (IMPOSIBLE, mas que el 100% del capital -> cuenta reventada).
"""
import pandas as pd
import numpy as np
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico

np.random.seed(51)
CARPETA = os.path.dirname(__file__)
CAPITAL_INICIAL = 1000.0
N_ITER = 5000

PERFILES = {
    'Conservador':     [0.0025, 0.005, 0.01, 0.02, 0.04],
    'Moderado':        [0.005, 0.01, 0.02, 0.04, 0.08],
    'Arriesgado':      [0.01, 0.02, 0.04, 0.08, 0.16],
    'Muy arriesgado':  [0.02, 0.04, 0.08, 0.16, 0.32],
}


def simular_escalera(r_serie, niveles, capital_inicial=CAPITAL_INICIAL, con_tope=True):
    """Devuelve (valores_capital, reventada:bool, nivel_max_alcanzado,
    n_veces_nivel_max). reventada=True si en algun punto el riesgo
    requerido supera 100% (sin tope) -> capital a 0."""
    capital = capital_inicial
    valores = [capital]
    nivel = 0  # indice 0 = riesgo base
    reventada = False
    nivel_max_alcanzado = 0
    veces_en_nivel_max = 0

    for r in r_serie:
        if nivel < len(niveles):
            riesgo = niveles[nivel]
        else:
            if con_tope:
                riesgo = niveles[-1]
            else:
                riesgo = niveles[0] * (2 ** nivel)  # sigue duplicando sin limite
                if riesgo >= 1.0:
                    reventada = True
                    capital = 0.0
                    valores.append(capital)
                    return valores, reventada, nivel_max_alcanzado, veces_en_nivel_max

        capital += capital * riesgo * r
        valores.append(capital)
        nivel_max_alcanzado = max(nivel_max_alcanzado, nivel)
        if nivel == len(niveles) - 1:
            veces_en_nivel_max += 1

        if r < 0:
            nivel += 1
        else:
            nivel = 0

        if capital <= 0:
            reventada = True
            return valores, reventada, nivel_max_alcanzado, veces_en_nivel_max

    return valores, reventada, nivel_max_alcanzado, veces_en_nivel_max


def max_drawdown(valores):
    s = pd.Series(valores)
    pico = s.cummax()
    dd = (s - pico) / pico * 100
    return dd.min()


def bootstrap_escalera(r_pool, niveles, n_dias_o_trades, con_tope, n_iter=N_ITER):
    """Bootstrap simple por operacion individual (no por dia, porque acá
    lo que importa es la secuencia de rachas, no la agrupacion por dia)."""
    finales = np.empty(n_iter)
    drawdowns = np.empty(n_iter)
    reventadas = 0
    for it in range(n_iter):
        muestra = np.random.choice(r_pool, size=n_dias_o_trades, replace=True)
        valores, reventada, _, _ = simular_escalera(muestra, niveles, con_tope=con_tope)
        finales[it] = valores[-1]
        drawdowns[it] = max_drawdown(valores)
        if reventada:
            reventadas += 1
    return finales, drawdowns, reventadas


if __name__ == '__main__':
    df = cargar_todo_cronologico()
    r_serie = df['Beneficio_R'].values
    n = len(r_serie)

    print("=" * 100)
    print(f"BACKTEST REAL -- serie cronologica real completa ({n} operaciones)")
    print("=" * 100)
    print(f"{'Perfil':<18}{'Capital final':>15}{'Retorno':>13}{'Drawdown':>11}{'Nivel max usado':>17}{'Veces en nivel max':>20}")
    resumen_real = []
    for nombre, niveles in PERFILES.items():
        valores, reventada, nivel_max, veces_max = simular_escalera(r_serie, niveles, con_tope=True)
        final = valores[-1]
        ret = (final / CAPITAL_INICIAL - 1) * 100 if not reventada else -100.0
        dd = max_drawdown(valores)
        etiqueta_nivel = f"{niveles[nivel_max]*100:.2f}% (nivel {nivel_max+1}/5)"
        print(f"{nombre:<18}USD {final:>10,.0f}{ret:>+12.1f}%{dd:>+10.1f}%{etiqueta_nivel:>17}{veces_max:>20}")
        resumen_real.append(dict(perfil=nombre, capital_final=round(final, 2), retorno_pct=round(ret, 1),
                                  drawdown_pct=round(dd, 1), nivel_max_alcanzado=nivel_max + 1, reventada=reventada))

    print(f"\n{'=' * 100}\nBOOTSTRAP -- {N_ITER} universos alternativos, CON TOPE (se queda en nivel 5 maximo)")
    print("=" * 100)
    print(f"{'Perfil':<18}{'P(positivo)':>13}{'Retorno mediana':>18}{'DD mediana':>13}{'DD peor 5%':>13}{'P(reventada)':>14}")
    for nombre, niveles in PERFILES.items():
        finales, drawdowns, reventadas = bootstrap_escalera(r_serie, niveles, n, con_tope=True)
        p_pos = (finales > CAPITAL_INICIAL).mean() * 100
        ret_b = (finales / CAPITAL_INICIAL - 1) * 100
        print(f"{nombre:<18}{p_pos:>12.1f}%{np.median(ret_b):>+17.1f}%{np.median(drawdowns):>+12.1f}%{np.percentile(drawdowns,5):>+12.1f}%{reventadas/N_ITER*100:>13.2f}%")

    print(f"\n{'=' * 100}\nBOOTSTRAP -- SIN TOPE (Martingala pura, sigue duplicando mas alla del nivel 5)")
    print("=" * 100)
    print(f"{'Perfil':<18}{'P(positivo)':>13}{'Retorno mediana':>18}{'DD mediana':>13}{'P(CUENTA REVENTADA)':>22}")
    resumen_sin_tope = []
    for nombre, niveles in PERFILES.items():
        finales, drawdowns, reventadas = bootstrap_escalera(r_serie, niveles, n, con_tope=False)
        p_pos = (finales > CAPITAL_INICIAL).mean() * 100
        ret_b = (finales / CAPITAL_INICIAL - 1) * 100
        p_reventada = reventadas / N_ITER * 100
        print(f"{nombre:<18}{p_pos:>12.1f}%{np.median(ret_b):>+17.1f}%{np.median(drawdowns):>+12.1f}%{p_reventada:>21.2f}%")
        resumen_sin_tope.append(dict(perfil=nombre, p_positivo=round(p_pos, 1), retorno_mediana=round(np.median(ret_b), 1),
                                      dd_mediana=round(np.median(drawdowns), 1), p_reventada_pct=round(p_reventada, 2)))

    pd.DataFrame(resumen_real).to_csv(os.path.join(CARPETA, 'escalera_martingala_backtest_real.csv'), index=False)
    pd.DataFrame(resumen_sin_tope).to_csv(os.path.join(CARPETA, 'escalera_martingala_sin_tope_bootstrap.csv'), index=False)

    # -- cuantas perdidas seguidas se necesitan para reventar cada perfil, sin tope --
    print(f"\n{'=' * 100}\n¿Cuantas perdidas seguidas revientan la cuenta? (sin tope, riesgo >= 100%)")
    print("=" * 100)
    for nombre, niveles in PERFILES.items():
        base = niveles[0]
        n_perdidas = 0
        riesgo = base
        while riesgo < 1.0:
            n_perdidas += 1
            riesgo = base * (2 ** n_perdidas)
        print(f"{nombre}: revienta en la perdida consecutiva numero {n_perdidas + 1} (ese nivel pediria {riesgo*100:.0f}% de riesgo)")
