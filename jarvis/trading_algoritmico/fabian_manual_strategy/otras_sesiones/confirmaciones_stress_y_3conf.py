"""
03/09/2026, a pedido de Diego: (1) 3 confirmaciones en vez de 2 antes de
escalar (comparar contra la variante de 2), y (2) el mismo stress test
de rachas de 3 perdidas seguidas aplicado a la variante ganadora
(2 confirmaciones + 1% lineal) y a la de 3 confirmaciones.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, DIAS_ORDEN, curva_riesgo_variable, max_drawdown
from escalera_de_riesgo_martingala import CAPITAL_INICIAL, N_ITER
from stress_test_rachas_y_mitigacion import construir_secuencia_estresada

np.random.seed(111)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'

df = cargar_todo_cronologico()
r_serie = df['Beneficio_R'].values
n = len(r_serie)


def simular_antimartingala_nconf(r_seq, base_pct, n_confirmaciones=2, incremento_pct=1.0, tope_extra=4, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    valores = [capital]
    racha = 0
    for r in r_seq:
        if racha < n_confirmaciones:
            riesgo = base_pct / 100
        else:
            nivel_extra = min(racha - (n_confirmaciones - 1), tope_extra)
            riesgo = (base_pct + incremento_pct * nivel_extra) / 100
        capital += capital * riesgo * r
        valores.append(capital)
        racha = racha + 1 if r > 0 else 0
    return valores


def bootstrap_nconf(r_pool, base_pct, n_confirmaciones, n_ops, n_iter=N_ITER):
    finales = np.empty(n_iter)
    drawdowns = np.empty(n_iter)
    for it in range(n_iter):
        muestra = np.random.choice(r_pool, size=n_ops, replace=True)
        valores = simular_antimartingala_nconf(muestra, base_pct, n_confirmaciones)
        finales[it] = valores[-1]
        drawdowns[it] = max_drawdown(valores)
    return finales, drawdowns


if __name__ == '__main__':
    # ══════════════ PARTE 1: 2 vs 3 confirmaciones, grilla 1-5% ══════════════
    BASES = [1, 2, 3, 4, 5]
    filas = []
    print("=" * 100)
    print("2 CONFIRMACIONES vs 3 CONFIRMACIONES -- grilla 1%-5%")
    print("=" * 100)
    for b in BASES:
        v2 = simular_antimartingala_nconf(r_serie, b, n_confirmaciones=2)
        v3 = simular_antimartingala_nconf(r_serie, b, n_confirmaciones=3)
        f2, dd2 = v2[-1], max_drawdown(v2)
        f3, dd3 = v3[-1], max_drawdown(v3)
        ret2 = (f2 / CAPITAL_INICIAL - 1) * 100
        ret3 = (f3 / CAPITAL_INICIAL - 1) * 100
        print(f"\n--- Base {b}% ---")
        print(f"  2 confirmaciones: USD {f2:>12,.0f}  retorno {ret2:>+12.1f}%  drawdown {dd2:>+7.1f}%")
        print(f"  3 confirmaciones: USD {f3:>12,.0f}  retorno {ret3:>+12.1f}%  drawdown {dd3:>+7.1f}%")
        filas.append(dict(base_pct=b, variante='2 confirmaciones', capital_final=round(f2, 2), retorno_pct=round(ret2, 1), drawdown_pct=round(dd2, 1)))
        filas.append(dict(base_pct=b, variante='3 confirmaciones', capital_final=round(f3, 2), retorno_pct=round(ret3, 1), drawdown_pct=round(dd3, 1)))
    pd.DataFrame(filas).to_csv(os.path.join(CARPETA, 'comparacion_2vs3_confirmaciones.csv'), index=False)

    # ══════════════ PARTE 2: stress test rachas de 3L, base 3% ══════════════
    print(f"\n\n{'=' * 100}\nSTRESS TEST -- Parejo vs 2 confirmaciones vs 3 confirmaciones (base 3%)")
    print("=" * 100)
    K_VALUES = [9, 15, 20, 30, 40]
    N_SIM = 300
    BASE_PCT = 3
    resultados = []
    for k in K_VALUES:
        for metodo_nombre, fn in [
            ('parejo', None),
            ('2 confirmaciones', lambda seq: simular_antimartingala_nconf(seq, BASE_PCT, 2)),
            ('3 confirmaciones', lambda seq: simular_antimartingala_nconf(seq, BASE_PCT, 3)),
        ]:
            finales, drawdowns = [], []
            for sim in range(N_SIM):
                seq = construir_secuencia_estresada(k, seed=2000 * k + sim)
                if metodo_nombre == 'parejo':
                    capital = CAPITAL_INICIAL
                    valores = [capital]
                    for r in seq:
                        capital += capital * (BASE_PCT / 100) * r
                        valores.append(capital)
                else:
                    valores = fn(seq)
                finales.append(valores[-1])
                drawdowns.append(max_drawdown(valores))
            finales = np.array(finales)
            drawdowns = np.array(drawdowns)
            ret_mediana = (np.median(finales) / CAPITAL_INICIAL - 1) * 100
            dd_mediana = np.median(drawdowns)
            dd_p5 = np.percentile(drawdowns, 5)
            p_pos = (finales > CAPITAL_INICIAL).mean() * 100
            resultados.append(dict(k_rachas_3=k, metodo=metodo_nombre, retorno_mediana_pct=round(ret_mediana, 1),
                                    dd_mediana_pct=round(dd_mediana, 1), dd_peor5_pct=round(dd_p5, 1), p_positivo=round(p_pos, 1)))

    tabla_stress = pd.DataFrame(resultados)
    tabla_stress.to_csv(os.path.join(CARPETA, 'stress_test_confirmaciones.csv'), index=False)
    for metodo in ['parejo', '2 confirmaciones', '3 confirmaciones']:
        print(f"\n--- {metodo.upper()} (base {BASE_PCT}%) ---")
        print(f"{'K rachas de 3L':>16}{'Retorno mediana':>18}{'DD mediana':>13}{'DD peor 5%':>13}{'P(positivo)':>14}")
        for _, row in tabla_stress[tabla_stress['metodo'] == metodo].iterrows():
            print(f"{row['k_rachas_3']:>16}{row['retorno_mediana_pct']:>+17.1f}%{row['dd_mediana_pct']:>+12.1f}%{row['dd_peor5_pct']:>+12.1f}%{row['p_positivo']:>13.1f}%")

    # ══════════════ graficos ══════════════
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), facecolor=BG)
    ax1, ax2 = axes
    ax1.set_facecolor(BG); ax2.set_facecolor(BG)

    tabla_23 = pd.DataFrame(filas)
    colores_23 = {'2 confirmaciones': '#26a69a', '3 confirmaciones': '#ab47bc'}
    for variante, g in tabla_23.groupby('variante'):
        ax1.plot(g['base_pct'], g['retorno_pct'], color=colores_23[variante], marker='o', linewidth=1.8, label=f'{variante} -- retorno')
    ax1b = ax1.twinx()
    for variante, g in tabla_23.groupby('variante'):
        ax1b.plot(g['base_pct'], g['drawdown_pct'].abs(), color=colores_23[variante], marker='s', linestyle='--', linewidth=1.2, alpha=0.6)
    ax1.set_yscale('log')
    ax1.set_xlabel('Riesgo base (%)', color=WHITE, fontsize=9)
    ax1.set_ylabel('Retorno (%, línea sólida, log)', color=WHITE, fontsize=9)
    ax1b.set_ylabel('Drawdown (%, línea punteada)', color=WHITE, fontsize=9)
    ax1b.tick_params(colors=WHITE, labelsize=8)
    ax1.set_title('2 vs 3 confirmaciones -- retorno y drawdown', color=WHITE, fontsize=10.5, loc='left')
    ax1.tick_params(colors=WHITE, labelsize=8)
    ax1.grid(color=GRID, linewidth=0.4, alpha=0.5)
    for s in ax1.spines.values():
        s.set_color(GRID)
    for s in ax1b.spines.values():
        s.set_color(GRID)
    ax1.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=7.5, loc='upper left')

    colores_stress = {'parejo': '#448aff', '2 confirmaciones': '#26a69a', '3 confirmaciones': '#ab47bc'}
    for metodo, g in tabla_stress.groupby('metodo'):
        ax2.plot(g['k_rachas_3'], g['dd_mediana_pct'].abs(), color=colores_stress[metodo], marker='o', linewidth=1.8, label=metodo)
        ax2.fill_between(g['k_rachas_3'], g['dd_mediana_pct'].abs(), g['dd_peor5_pct'].abs(), color=colores_stress[metodo], alpha=0.12)
    ax2.axvline(9, color=WHITE, linestyle=':', linewidth=1, alpha=0.6)
    ax2.set_xlabel('Cantidad de rachas de 3 pérdidas seguidas', color=WHITE, fontsize=9)
    ax2.set_ylabel('Drawdown máximo (%, mediana + banda peor 5%)', color=WHITE, fontsize=9)
    ax2.set_title('Stress test -- Parejo vs 2conf vs 3conf (base 3%)', color=WHITE, fontsize=10.5, loc='left')
    ax2.tick_params(colors=WHITE, labelsize=8)
    ax2.grid(color=GRID, linewidth=0.4, alpha=0.5)
    for s in ax2.spines.values():
        s.set_color(GRID)
    ax2.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(GRAF_DIR, 'confirmaciones_stress_2vs3.png'), dpi=150, facecolor=BG)
    print(f"\nGuardado: confirmaciones_stress_2vs3.png")
