"""
03/09/2026, a pedido de Diego: (1) stress-test -- ¿que pasaria si las
rachas de 3+ perdidas seguidas hubiesen pasado MAS SEGUIDO de lo que
realmente paso en los 10 meses? (2) un mecanismo concreto de mitigacion
de perdidas para cada uno de los 3 enfoques (Parejo/Martingala/
Anti-Martingala).

Dato real de partida: en las 482 operaciones reales, una racha de
EXACTAMENTE 3 perdidas seguidas ya paso 9 veces (y una de 4, una vez).
Diego pregunta que pasaria si pasara "3 veces o mas" -- como 9 ya es
mas que 3, se prueba una ESCALERA de estres: mantener el volumen total
de operaciones fijo (482) pero forzar que aparezcan K rachas de 3
perdidas seguidas (ademas de lo que ya pasa por azar), para
K = 9 (real), 15, 20, 30, 40 -- y ver el impacto en cada enfoque.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico, DIAS_ORDEN
from escalera_de_riesgo_martingala import simular_escalera, max_drawdown, CAPITAL_INICIAL
from escalera_nivel_por_nivel_y_antimartingala import simular_anti_martingala

np.random.seed(91)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'

df = cargar_todo_cronologico()
r_serie = df['Beneficio_R'].values
n = len(r_serie)
losses_pool = r_serie[r_serie < 0]
wins_pool = r_serie[r_serie > 0]
be_pool = r_serie[r_serie == 0]


def construir_secuencia_estresada(k_rachas_de_3, n_total=n, seed=None):
    """Arma una secuencia sintetica de n_total operaciones, con
    k_rachas_de_3 bloques forzados de 3 perdidas seguidas (usando R
    reales del pool de perdidas), el resto relleno por muestreo con
    reemplazo del pool real completo (preserva win rate real)."""
    rng = np.random.RandomState(seed)
    ops_en_streaks = k_rachas_de_3 * 3
    ops_relleno = max(n_total - ops_en_streaks, 0)

    bloques = [rng.choice(losses_pool, size=3, replace=True) for _ in range(k_rachas_de_3)]

    # relleno: muestreo con reemplazo del pool real completo (preserva win rate),
    # se insertan los bloques forzados de a 3 en posiciones aleatorias
    secuencia = list(rng.choice(r_serie, size=ops_relleno, replace=True))
    posiciones = sorted(rng.choice(range(len(secuencia) + 1), size=k_rachas_de_3, replace=False)) if len(secuencia) >= k_rachas_de_3 else list(range(k_rachas_de_3))
    offset = 0
    for pos, bloque in zip(posiciones, bloques):
        idx = pos + offset
        secuencia[idx:idx] = list(bloque)
        offset += 3
    return np.array(secuencia)


def evaluar_metodo(r_seq, metodo, base_pct=3):
    b = base_pct / 100
    if metodo == 'parejo':
        capital = CAPITAL_INICIAL
        valores = [capital]
        for r in r_seq:
            capital += capital * b * r
            valores.append(capital)
        return valores
    niveles = [b * (2 ** i) for i in range(5)]
    if metodo == 'martingala':
        valores, _, _, _ = simular_escalera(r_seq, niveles, con_tope=True)
        return valores
    if metodo == 'antimartingala':
        valores, _, _ = simular_anti_martingala(r_seq, niveles)
        return valores


if __name__ == '__main__':
    K_VALUES = [9, 15, 20, 30, 40]
    N_SIM = 300
    BASE_PCT = 3

    print("=" * 100)
    print(f"STRESS TEST -- ¿que pasa si las rachas de 3 perdidas seguidas pasan MAS SEGUIDO?")
    print(f"(real: 9 veces en 482 operaciones / 10 meses. Base de riesgo: {BASE_PCT}%, {N_SIM} simulaciones por escalon)")
    print("=" * 100)

    resultados = []
    for k in K_VALUES:
        for metodo in ['parejo', 'martingala', 'antimartingala']:
            finales, drawdowns = [], []
            for sim in range(N_SIM):
                seq = construir_secuencia_estresada(k, seed=1000 * k + sim)
                valores = evaluar_metodo(seq, metodo, BASE_PCT)
                finales.append(valores[-1])
                drawdowns.append(max_drawdown(valores))
            finales = np.array(finales)
            drawdowns = np.array(drawdowns)
            ret_mediana = (np.median(finales) / CAPITAL_INICIAL - 1) * 100
            dd_mediana = np.median(drawdowns)
            dd_p5 = np.percentile(drawdowns, 5)
            p_positivo = (finales > CAPITAL_INICIAL).mean() * 100
            resultados.append(dict(k_rachas_3=k, metodo=metodo, retorno_mediana_pct=round(ret_mediana, 1),
                                    dd_mediana_pct=round(dd_mediana, 1), dd_peor5_pct=round(dd_p5, 1),
                                    p_positivo=round(p_positivo, 1)))

    tabla = pd.DataFrame(resultados)
    tabla.to_csv(os.path.join(CARPETA, 'stress_test_rachas_resumen.csv'), index=False)

    for metodo in ['parejo', 'martingala', 'antimartingala']:
        print(f"\n--- {metodo.upper()} (base {BASE_PCT}%) ---")
        print(f"{'K rachas de 3L':>16}{'Retorno mediana':>18}{'DD mediana':>13}{'DD peor 5%':>13}{'P(positivo)':>14}")
        for _, row in tabla[tabla['metodo'] == metodo].iterrows():
            print(f"{row['k_rachas_3']:>16}{row['retorno_mediana_pct']:>+17.1f}%{row['dd_mediana_pct']:>+12.1f}%{row['dd_peor5_pct']:>+12.1f}%{row['p_positivo']:>13.1f}%")

    # -- grafico --
    fig, ax = plt.subplots(figsize=(11, 6), facecolor=BG)
    ax.set_facecolor(BG)
    colores = {'parejo': '#448aff', 'martingala': '#ef5350', 'antimartingala': '#26a69a'}
    etiquetas = {'parejo': 'Parejo', 'martingala': 'Martingala (tope)', 'antimartingala': 'Anti-Martingala'}
    for metodo, g in tabla.groupby('metodo'):
        ax.plot(g['k_rachas_3'], g['dd_mediana_pct'].abs(), color=colores[metodo], marker='o', linewidth=1.8, label=etiquetas[metodo])
        ax.fill_between(g['k_rachas_3'], g['dd_mediana_pct'].abs(), g['dd_peor5_pct'].abs(), color=colores[metodo], alpha=0.15)
    ax.axvline(9, color=WHITE, linestyle=':', linewidth=1, alpha=0.6)
    ax.text(9, ax.get_ylim()[1] * 0.95, ' ← lo que ya pasó (9 veces)', color=WHITE, fontsize=8, va='top')
    ax.set_xlabel('Cantidad de rachas de 3 pérdidas seguidas en el período', color=WHITE, fontsize=9)
    ax.set_ylabel('Drawdown máximo (%, mediana con banda hasta el peor 5%)', color=WHITE, fontsize=9)
    ax.set_title(f'Stress test -- drawdown según cuántas rachas de 3L pasan (base {BASE_PCT}%)', color=WHITE, fontsize=11, loc='left')
    ax.tick_params(colors=WHITE, labelsize=8)
    ax.grid(color=GRID, linewidth=0.4, alpha=0.5)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAF_DIR, 'stress_test_rachas.png'), dpi=150, facecolor=BG)
    print(f"\nGuardado: stress_test_rachas.png")
