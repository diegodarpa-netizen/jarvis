"""
04/09/2026, a pedido de Diego:
(1) aplicar "2 confirmaciones" a la Gestion Hibrida (160 operaciones).
(2) grilla 2x2: {1 confirmacion, 2 confirmaciones} x {incremento
    lineal +1%, incremento doblando} -- para ver que combinacion es mas
    eficiente.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escalera_de_riesgo_martingala import CAPITAL_INICIAL, N_ITER, max_drawdown

np.random.seed(131)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'


def simular_confirmaciones(r_seq, base_pct, n_confirmaciones=2, modo='lineal',
                            incremento_pct=1.0, tope_extra=4, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    valores = [capital]
    racha = 0
    for r in r_seq:
        if racha < n_confirmaciones:
            riesgo = base_pct / 100
        else:
            nivel_extra = min(racha - (n_confirmaciones - 1), tope_extra)
            if modo == 'lineal':
                riesgo = (base_pct + incremento_pct * nivel_extra) / 100
            else:  # doblando
                riesgo = (base_pct * (2 ** nivel_extra)) / 100
        capital += capital * riesgo * r
        valores.append(capital)
        racha = racha + 1 if r > 0 else 0
    return valores


def bootstrap_confirmaciones(r_pool, base_pct, n_confirmaciones, modo, n_ops, n_iter=N_ITER):
    finales = np.empty(n_iter)
    drawdowns = np.empty(n_iter)
    for it in range(n_iter):
        muestra = np.random.choice(r_pool, size=n_ops, replace=True)
        valores = simular_confirmaciones(muestra, base_pct, n_confirmaciones, modo)
        finales[it] = valores[-1]
        drawdowns[it] = max_drawdown(valores)
    return finales, drawdowns


if __name__ == '__main__':
    from escenarios_riesgo_variable_dia import cargar_todo_cronologico
    df = cargar_todo_cronologico()
    r_todos = df['Beneficio_R'].values
    n_todos = len(r_todos)

    # ══════════ PARTE 1: 2 confirmaciones sobre la Gestion Hibrida ══════════
    df_hib = pd.read_csv(os.path.join(CARPETA, 'gestion_hibrida_resultado.csv'))
    df_hib['Fecha_dt'] = pd.to_datetime(df_hib['Fecha_dt'])
    r_hib = df_hib.sort_values(['Fecha_dt', 'Hora apertura (NY)'])['Beneficio_R'].values
    n_hib = len(r_hib)

    print("=" * 100)
    print(f"2 CONFIRMACIONES sobre la GESTION HIBRIDA ({n_hib} operaciones)")
    print("=" * 100)
    print(f"{'Base':>6}{'Capital final':>16}{'Retorno':>13}{'Drawdown':>11}{'P(positivo) boot':>18}")
    filas_hib = []
    for b in [1, 2, 3, 4, 5]:
        valores = simular_confirmaciones(r_hib, b, n_confirmaciones=2, modo='lineal')
        final, dd = valores[-1], max_drawdown(valores)
        ret = (final / CAPITAL_INICIAL - 1) * 100
        finales_b, dd_b = bootstrap_confirmaciones(r_hib, b, 2, 'lineal', n_hib, n_iter=2000)
        p_pos = (finales_b > CAPITAL_INICIAL).mean() * 100
        print(f"{b:>5}%USD {final:>11,.0f}{ret:>+12.1f}%{dd:>+10.1f}%{p_pos:>17.1f}%")
        filas_hib.append(dict(base_pct=b, capital_final=round(final, 2), retorno_pct=round(ret, 1),
                               drawdown_pct=round(dd, 1), p_positivo_bootstrap=round(p_pos, 1)))
    pd.DataFrame(filas_hib).to_csv(os.path.join(CARPETA, 'hibrida_2conf_tabla.csv'), index=False)

    # comparacion directa vs la Hibrida con riesgo parejo (ya calculada antes)
    print("\n-- Comparacion vs Gestion Hibrida con riesgo PAREJO (ya calculado antes) --")
    print("   Parejo 3%: +615.1% / -16.0%   |   Parejo 4%: +1238.9% / -21.0%   |   Parejo 5%: +2371.9% / -25.9%")

    # ══════════ PARTE 2: grilla 2x2, sobre TODOS los dias (482 ops) ══════════
    print(f"\n\n{'=' * 100}\nGRILLA 2x2 -- {{1,2}} confirmaciones x {{lineal +1%, doblando}}, sobre las 482 operaciones")
    print("=" * 100)
    combos = [(1, 'lineal'), (1, 'doblando'), (2, 'lineal'), (2, 'doblando')]
    filas_grilla = []
    for b in [1, 2, 3, 4, 5]:
        print(f"\n--- Base {b}% ---")
        for n_conf, modo in combos:
            valores = simular_confirmaciones(r_todos, b, n_confirmaciones=n_conf, modo=modo)
            final, dd = valores[-1], max_drawdown(valores)
            ret = (final / CAPITAL_INICIAL - 1) * 100
            etiqueta = f"{n_conf} conf. / {modo}"
            print(f"  {etiqueta:<20}USD {final:>14,.0f}  retorno {ret:>+14.1f}%  drawdown {dd:>+7.1f}%")
            filas_grilla.append(dict(base_pct=b, n_confirmaciones=n_conf, modo=modo, etiqueta=etiqueta,
                                      capital_final=round(final, 2), retorno_pct=round(ret, 1), drawdown_pct=round(dd, 1)))

    tabla_grilla = pd.DataFrame(filas_grilla)
    tabla_grilla.to_csv(os.path.join(CARPETA, 'grilla_2x2_confirmaciones_modo.csv'), index=False)

    # ══════════ graficos ══════════
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), facecolor=BG)
    ax1, ax2 = axes
    ax1.set_facecolor(BG); ax2.set_facecolor(BG)
    colores = {'1 conf. / lineal': '#42a5f5', '1 conf. / doblando': '#ef5350',
               '2 conf. / lineal': '#26a69a', '2 conf. / doblando': '#ab47bc'}
    for etiqueta, g in tabla_grilla.groupby('etiqueta'):
        ax1.plot(g['base_pct'], g['retorno_pct'], color=colores[etiqueta], marker='o', linewidth=1.8, label=etiqueta)
        ax2.plot(g['base_pct'], g['drawdown_pct'].abs(), color=colores[etiqueta], marker='o', linewidth=1.8, label=etiqueta)
    ax1.set_yscale('log')
    ax1.set_xlabel('Riesgo base (%)', color=WHITE, fontsize=9)
    ax1.set_ylabel('Retorno (%, escala log)', color=WHITE, fontsize=9)
    ax1.set_title('Grilla 2x2 -- retorno', color=WHITE, fontsize=10.5, loc='left')
    ax1.tick_params(colors=WHITE, labelsize=8)
    ax1.grid(color=GRID, linewidth=0.4, alpha=0.5)
    for s in ax1.spines.values():
        s.set_color(GRID)
    ax1.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=7.5)

    ax2.set_xlabel('Riesgo base (%)', color=WHITE, fontsize=9)
    ax2.set_ylabel('Drawdown máximo real (%, valor absoluto)', color=WHITE, fontsize=9)
    ax2.set_title('Grilla 2x2 -- drawdown', color=WHITE, fontsize=10.5, loc='left')
    ax2.tick_params(colors=WHITE, labelsize=8)
    ax2.grid(color=GRID, linewidth=0.4, alpha=0.5)
    for s in ax2.spines.values():
        s.set_color(GRID)
    ax2.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=7.5)

    plt.tight_layout()
    plt.savefig(os.path.join(GRAF_DIR, 'grilla_2x2_confirmaciones_modo.png'), dpi=150, facecolor=BG)
    print(f"\nGuardado: grilla_2x2_confirmaciones_modo.png")
