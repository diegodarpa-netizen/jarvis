"""
03/09/2026, a pedido de Diego: (1) desglose nivel por nivel de la
escalera de riesgo (Martingala) -- ¿en que racha empieza a ser
realmente peligroso, con que probabilidad se llega ahi, y cuanto
capital queda en el camino? (2) el modelo "anti-Martingala" que
propuse: escalar el riesgo en rachas GANADORAS (no perdedoras),
resetear a base apenas hay una perdida.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico
from escalera_de_riesgo_martingala import PERFILES, simular_escalera, max_drawdown, CAPITAL_INICIAL, N_ITER

np.random.seed(71)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'

df = cargar_todo_cronologico()
r_serie = df['Beneficio_R'].values
n = len(r_serie)
AVG_LOSS_R = r_serie[r_serie < 0].mean()   # ~ -0.88
P_LOSS = (r_serie < 0).mean()               # ~ 31.5%


# ══════════════════════════════════════════════════════════════════
# PARTE 1 -- nivel por nivel: ¿donde empieza el peligro real?
# ══════════════════════════════════════════════════════════════════
def prob_streak_al_menos_n(r_pool, n_ops, n_max=12, n_iter=N_ITER):
    """Bootstrap: en una secuencia de n_ops operaciones (misma cantidad
    que el historico), ¿con que probabilidad aparece en algun punto una
    racha de AL MENOS N perdidas seguidas?"""
    max_streaks = np.empty(n_iter)
    for it in range(n_iter):
        muestra = np.random.choice(r_pool, size=n_ops, replace=True)
        resultado = np.where(muestra < 0, 1, 0)
        racha = 0
        peor = 0
        for x in resultado:
            racha = racha + 1 if x else 0
            peor = max(peor, racha)
        max_streaks[it] = peor
    return {n_: (max_streaks >= n_).mean() * 100 for n_ in range(1, n_max + 1)}


if __name__ == '__main__':
    probs = prob_streak_al_menos_n(r_serie, n, n_max=12)

    print("=" * 100)
    print(f"PROBABILIDAD DE QUE APAREZCA UNA RACHA DE AL MENOS N PERDIDAS SEGUIDAS")
    print(f"(en una ventana de {n} operaciones, como tu historico real -- bootstrap {N_ITER} universos)")
    print("=" * 100)
    print(f"{'N perdidas seguidas':>20}{'Probabilidad':>15}")
    for n_, p in probs.items():
        print(f"{n_:>20}{p:>14.1f}%")

    print(f"\n{'=' * 100}\nNIVEL POR NIVEL -- riesgo % y capital restante si la racha llega justo ahi")
    print(f"(usando la perdida promedio real, {AVG_LOSS_R:.2f}R, en cada nivel)")
    print("=" * 100)

    filas = []
    for nombre, niveles_base in PERFILES.items():
        base = niveles_base[0]
        capital = 100.0  # en % del capital inicial, para leer directo
        print(f"\n-- {nombre} (base {base*100:.2f}%) --")
        print(f"{'Nivel (perdida #)':>18}{'Riesgo de ese trade':>20}{'Prob. de llegar ahi':>20}{'Capital restante':>18}")
        for nivel in range(1, 9):
            riesgo = base * (2 ** (nivel - 1))
            capital *= (1 + riesgo * AVG_LOSS_R) if riesgo < 1.0 else 0.0
            prob = probs.get(nivel, 0.0)
            alerta = ""
            if riesgo >= 0.5:
                alerta = "  <-- mas de mitad del capital en 1 trade"
            elif riesgo >= 1.0:
                alerta = "  <-- CUENTA REVENTADA"
            print(f"{nivel:>18}{riesgo*100:>19.2f}%{prob:>19.1f}%{capital:>17.1f}%{alerta}")
            filas.append(dict(perfil=nombre, nivel=nivel, riesgo_pct=round(riesgo*100, 2),
                               prob_llegar_pct=round(prob, 2), capital_restante_pct=round(capital, 1)))
            if riesgo >= 1.0:
                break

    pd.DataFrame(filas).to_csv(os.path.join(CARPETA, 'escalera_nivel_por_nivel.csv'), index=False)

    # -- grafico: probabilidad de racha vs capital restante por nivel, 4 perfiles --
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), facecolor=BG)
    ax1, ax2 = axes
    ax1.set_facecolor(BG); ax2.set_facecolor(BG)
    ns = list(range(1, 9))
    ax1.plot(ns, [probs.get(n_, 0) for n_ in ns], color='#ffb300', marker='o', linewidth=1.8)
    ax1.set_title('Probabilidad de una racha de al menos N pérdidas seguidas\n(en una ventana como tu histórico real)', color=WHITE, fontsize=10, loc='left')
    ax1.set_xlabel('N pérdidas consecutivas', color=WHITE, fontsize=9)
    ax1.set_ylabel('Probabilidad (%)', color=WHITE, fontsize=9)
    ax1.tick_params(colors=WHITE, labelsize=8)
    ax1.grid(color=GRID, linewidth=0.4, alpha=0.5)
    for s in ax1.spines.values():
        s.set_color(GRID)

    colores = {'Conservador': '#42a5f5', 'Moderado': '#ffb300', 'Arriesgado': '#ff7043', 'Muy arriesgado': '#ef5350'}
    tabla = pd.DataFrame(filas)
    for nombre, g in tabla.groupby('perfil'):
        ax2.plot(g['nivel'], g['capital_restante_pct'], color=colores[nombre], marker='o', linewidth=1.6, label=nombre)
    ax2.axhline(50, color=WHITE, linestyle=':', linewidth=0.8, alpha=0.6)
    ax2.set_title('Capital restante (%) si la racha llega a ese nivel\n(con la pérdida promedio real de cada trade)', color=WHITE, fontsize=10, loc='left')
    ax2.set_xlabel('Nivel (pérdida consecutiva #)', color=WHITE, fontsize=9)
    ax2.set_ylabel('Capital restante (%)', color=WHITE, fontsize=9)
    ax2.tick_params(colors=WHITE, labelsize=8)
    ax2.grid(color=GRID, linewidth=0.4, alpha=0.5)
    for s in ax2.spines.values():
        s.set_color(GRID)
    ax2.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(GRAF_DIR, 'escalera_nivel_por_nivel.png'), dpi=150, facecolor=BG)
    print(f"\nGuardado: escalera_nivel_por_nivel.png")


# ══════════════════════════════════════════════════════════════════
# PARTE 2 -- ANTI-MARTINGALA: escalar en rachas GANADORAS
# ══════════════════════════════════════════════════════════════════
def simular_anti_martingala(r_pool, niveles, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    valores = [capital]
    nivel = 0
    nivel_max_alcanzado = 0
    for r in r_pool:
        riesgo = niveles[min(nivel, len(niveles) - 1)]
        capital += capital * riesgo * r
        valores.append(capital)
        nivel_max_alcanzado = max(nivel_max_alcanzado, nivel)
        if r > 0:
            nivel = min(nivel + 1, len(niveles) - 1)
        else:
            nivel = 0
        if capital <= 0:
            return valores, True, nivel_max_alcanzado
    return valores, False, nivel_max_alcanzado


def bootstrap_anti_martingala(r_pool, niveles, n_ops, n_iter=N_ITER):
    finales = np.empty(n_iter)
    drawdowns = np.empty(n_iter)
    for it in range(n_iter):
        muestra = np.random.choice(r_pool, size=n_ops, replace=True)
        valores, _, _ = simular_anti_martingala(muestra, niveles)
        finales[it] = valores[-1]
        drawdowns[it] = max_drawdown(valores)
    return finales, drawdowns


if __name__ == '__main__':
    print(f"\n\n{'=' * 100}\nANTI-MARTINGALA -- escalar en rachas GANADORAS, resetear a base ante CUALQUIER perdida")
    print("=" * 100)
    print(f"{'Perfil':<18}{'Capital final (real)':>20}{'Retorno':>13}{'Drawdown real':>15}")
    resumen_am = []
    for nombre, niveles in PERFILES.items():
        valores, reventada, nivel_max = simular_anti_martingala(r_serie, niveles)
        final = valores[-1]
        ret = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        print(f"{nombre:<18}USD {final:>16,.0f}{ret:>+12.1f}%{dd:>+14.1f}%")
        resumen_am.append(dict(perfil=nombre, capital_final=round(final, 2), retorno_pct=round(ret, 1), drawdown_pct=round(dd, 1)))

    print(f"\n-- Bootstrap ({N_ITER} universos) --")
    print(f"{'Perfil':<18}{'P(positivo)':>13}{'Retorno mediana':>18}{'DD mediana':>13}{'DD peor 5%':>13}")
    for nombre, niveles in PERFILES.items():
        finales, drawdowns = bootstrap_anti_martingala(r_serie, niveles, n)
        p_pos = (finales > CAPITAL_INICIAL).mean() * 100
        ret_b = (finales / CAPITAL_INICIAL - 1) * 100
        print(f"{nombre:<18}{p_pos:>12.1f}%{np.median(ret_b):>+17.1f}%{np.median(drawdowns):>+12.1f}%{np.percentile(drawdowns,5):>+12.1f}%")
        for d in resumen_am:
            if d['perfil'] == nombre:
                d['p_positivo_bootstrap'] = round(p_pos, 1)
                d['dd_mediana_bootstrap'] = round(np.median(drawdowns), 1)
                d['dd_p5_bootstrap'] = round(np.percentile(drawdowns, 5), 1)

    pd.DataFrame(resumen_am).to_csv(os.path.join(CARPETA, 'anti_martingala_resumen.csv'), index=False)

    # -- comparacion visual: Martingala (sin tope) vs Anti-Martingala, drawdown --
    marti = pd.read_csv(os.path.join(CARPETA, 'escalera_martingala_sin_tope_bootstrap.csv'))
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor=BG)
    ax.set_facecolor(BG)
    x = np.arange(len(PERFILES))
    width = 0.35
    ax.bar(x - width/2, marti['p_reventada_pct'], width, color='#ef5350', label='Martingala -- P(reventar la cuenta)')
    dd_am = [abs(d['dd_p5_bootstrap']) for d in resumen_am]
    ax.bar(x + width/2, dd_am, width, color='#26a69a', label='Anti-Martingala -- peor 5% de drawdown (%)')
    ax.set_xticks(x); ax.set_xticklabels(list(PERFILES.keys()), color=WHITE, fontsize=9)
    ax.set_ylabel('%', color=WHITE, fontsize=9)
    ax.set_title('Martingala (riesgo de ruina) vs. Anti-Martingala (peor drawdown, sin riesgo de ruina)', color=WHITE, fontsize=10.5, loc='left')
    ax.tick_params(colors=WHITE, labelsize=9)
    ax.grid(color=GRID, linewidth=0.4, alpha=0.5, axis='y')
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=8.5)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAF_DIR, 'martingala_vs_antimartingala.png'), dpi=150, facecolor=BG)
    print(f"\nGuardado: martingala_vs_antimartingala.png")
