"""
04/09/2026, a pedido de Diego (aclarado): grilla de TAMAÑO DE PASO por
nivel -- 1er escalon (tras la 1ra confirmacion) sube 1% o 2%; 2do
escalon (tras la 2da) suma ADEMAS 1%, 2% o 3% mas (acumulativo). Usa 1
confirmacion como gatillo (la ganadora de la ronda anterior), variando
SOLO el tamaño de los pasos.

Ademas: patron de rachas ganadoras/perdedoras en las 482 operaciones
reales -- distribucion completa, cada cuanto aparece una perdida, y
test de autocorrelacion (¿una ganancia predice otra ganancia mas de lo
que predice el azar?).
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escenarios_riesgo_variable_dia import cargar_todo_cronologico
from escalera_de_riesgo_martingala import CAPITAL_INICIAL, max_drawdown

np.random.seed(141)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'

df = cargar_todo_cronologico()
r_serie = df['Beneficio_R'].values
n = len(r_serie)


def simular_pasos(r_seq, base_pct, paso1_pct, paso2_pct, tope_extra=4, capital_inicial=CAPITAL_INICIAL):
    """1 confirmacion como gatillo: racha=0 -> base. racha=1 (tras 1
    ganancia) -> base+paso1. racha=2 (tras 2) -> base+paso1+paso2.
    racha>=3 -> se mantiene en base+paso1+paso2 (tope, sin mas pasos
    definidos mas alla del 2do escalon)."""
    capital = capital_inicial
    valores = [capital]
    racha = 0
    for r in r_seq:
        if racha == 0:
            riesgo = base_pct / 100
        elif racha == 1:
            riesgo = (base_pct + paso1_pct) / 100
        else:
            riesgo = (base_pct + paso1_pct + paso2_pct) / 100
        capital += capital * riesgo * r
        valores.append(capital)
        racha = racha + 1 if r > 0 else 0
    return valores


if __name__ == '__main__':
    # ══════════ PARTE 1: grilla de pasos ══════════
    print("=" * 100)
    print("GRILLA DE PASOS -- 1er escalon (1%% o 2%%) x 2do escalon (+1, +2 o +3 puntos mas)")
    print("Base de riesgo: 3%%")
    print("=" * 100)
    BASE = 3
    filas = []
    print(f"{'Paso 1':>10}{'Paso 2':>10}{'Nivel 2 total':>15}{'Capital final':>16}{'Retorno':>13}{'Drawdown':>11}")
    for paso1 in [1, 2]:
        for paso2 in [1, 2, 3]:
            valores = simular_pasos(r_serie, BASE, paso1, paso2)
            final, dd = valores[-1], max_drawdown(valores)
            ret = (final / CAPITAL_INICIAL - 1) * 100
            nivel2_total = BASE + paso1 + paso2
            print(f"{paso1:>9}%{paso2:>9}%{nivel2_total:>14}%USD {final:>10,.0f}{ret:>+12.1f}%{dd:>+10.1f}%")
            filas.append(dict(paso1_pct=paso1, paso2_pct=paso2, nivel1_pct=BASE+paso1, nivel2_pct=nivel2_total,
                               capital_final=round(final, 2), retorno_pct=round(ret, 1), drawdown_pct=round(dd, 1)))

    tabla = pd.DataFrame(filas)
    tabla.to_csv(os.path.join(CARPETA, 'grilla_pasos_1y2_resumen.csv'), index=False)

    fig, ax = plt.subplots(figsize=(9, 6), facecolor=BG)
    ax.set_facecolor(BG)
    pivot_ret = tabla.pivot(index='paso1_pct', columns='paso2_pct', values='retorno_pct')
    pivot_dd = tabla.pivot(index='paso1_pct', columns='paso2_pct', values='drawdown_pct')
    im = ax.imshow(pivot_ret.values, cmap='YlGn', aspect='auto')
    ax.set_xticks(range(len(pivot_ret.columns))); ax.set_xticklabels([f"+{c}%" for c in pivot_ret.columns], color=WHITE)
    ax.set_yticks(range(len(pivot_ret.index))); ax.set_yticklabels([f"+{i}%" for i in pivot_ret.index], color=WHITE)
    ax.set_xlabel('Paso 2 (2da confirmación)', color=WHITE, fontsize=9)
    ax.set_ylabel('Paso 1 (1ra confirmación)', color=WHITE, fontsize=9)
    ax.set_title(f'Retorno (%) y drawdown (%) por combinación de pasos -- base {BASE}%', color=WHITE, fontsize=10.5)
    for i in range(len(pivot_ret.index)):
        for j in range(len(pivot_ret.columns)):
            ax.text(j, i, f"{pivot_ret.values[i,j]:,.0f}%\nDD {pivot_dd.values[i,j]:.1f}%", ha='center', va='center', color='#131722', fontsize=8, fontweight='bold')
    for s in ax.spines.values():
        s.set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAF_DIR, 'grilla_pasos_1y2.png'), dpi=150, facecolor=BG)
    print(f"\nGuardado: grilla_pasos_1y2.png")

    # ══════════ PARTE 2: patron de rachas ganadoras/perdedoras ══════════
    print(f"\n\n{'=' * 100}\nPATRON DE RACHAS -- las 482 operaciones reales de Fabian\n{'=' * 100}")
    resultado = np.where(r_serie > 0, 1, np.where(r_serie < 0, -1, 0))
    n_wins = (resultado == 1).sum()
    n_losses = (resultado == -1).sum()
    n_be = (resultado == 0).sum()
    print(f"Total: {n} operaciones -- {n_wins} ganadoras ({n_wins/n*100:.1f}%), {n_losses} perdedoras ({n_losses/n*100:.1f}%), {n_be} break-even ({n_be/n*100:.1f}%)")
    print(f"Cada cuantas operaciones (en promedio) aparece una perdida: 1 cada {n/n_losses:.2f} operaciones")
    print(f"Cada cuantas operaciones (en promedio) aparece una ganancia: 1 cada {n/n_wins:.2f} operaciones")

    def rachas_de(valor):
        rachas = []
        actual = 0
        for x in resultado:
            if x == valor:
                actual += 1
            else:
                if actual > 0:
                    rachas.append(actual)
                actual = 0
        if actual > 0:
            rachas.append(actual)
        return np.array(rachas)

    rachas_ganadoras = rachas_de(1)
    rachas_perdedoras = rachas_de(-1)

    print(f"\n-- Rachas GANADORAS (n={len(rachas_ganadoras)}) --")
    for k in range(1, rachas_ganadoras.max() + 1):
        cnt = (rachas_ganadoras == k).sum()
        if cnt:
            print(f"  {k} ganadora(s) seguidas: {cnt} veces")
    print(f"  Racha ganadora maxima: {rachas_ganadoras.max()}")

    print(f"\n-- Rachas PERDEDORAS (n={len(rachas_perdedoras)}) --")
    for k in range(1, rachas_perdedoras.max() + 1):
        cnt = (rachas_perdedoras == k).sum()
        if cnt:
            print(f"  {k} perdida(s) seguida(s): {cnt} veces")
    print(f"  Racha perdedora maxima: {rachas_perdedoras.max()}")

    # -- autocorrelacion: ¿una ganancia predice otra ganancia mas que el azar? --
    print(f"\n-- ¿Hay 'mano caliente' o independencia? (autocorrelacion lag-1) --")
    solo_wl = resultado[resultado != 0]  # sacamos los break-even para este test
    p_win_base = (solo_wl == 1).mean()
    siguiente_tras_win = solo_wl[1:][solo_wl[:-1] == 1]
    siguiente_tras_loss = solo_wl[1:][solo_wl[:-1] == -1]
    p_win_tras_win = (siguiente_tras_win == 1).mean()
    p_win_tras_loss = (siguiente_tras_loss == 1).mean()
    print(f"  P(ganar) base (sin condicionar):        {p_win_base*100:.1f}%")
    print(f"  P(ganar | la anterior fue ganadora):     {p_win_tras_win*100:.1f}%  (n={len(siguiente_tras_win)})")
    print(f"  P(ganar | la anterior fue perdedora):    {p_win_tras_loss*100:.1f}%  (n={len(siguiente_tras_loss)})")
    diff = p_win_tras_win - p_win_tras_loss
    print(f"  Diferencia: {diff*100:+.1f} puntos porcentuales")

    # significancia con bootstrap (shuffle test)
    n_iter = 5000
    diffs_shuffled = []
    solo_wl_copy = solo_wl.copy()
    for _ in range(n_iter):
        np.random.shuffle(solo_wl_copy)
        s_tras_win = solo_wl_copy[1:][solo_wl_copy[:-1] == 1]
        s_tras_loss = solo_wl_copy[1:][solo_wl_copy[:-1] == -1]
        if len(s_tras_win) and len(s_tras_loss):
            diffs_shuffled.append((s_tras_win == 1).mean() - (s_tras_loss == 1).mean())
    diffs_shuffled = np.array(diffs_shuffled)
    p_value = (np.abs(diffs_shuffled) >= np.abs(diff)).mean()
    print(f"  Test de significancia (shuffle, {n_iter} iteraciones): p={p_value:.3f} -> "
          f"{'SIGNIFICATIVO' if p_value < 0.05 else 'NO significativo (compatible con independencia / azar)'}")
