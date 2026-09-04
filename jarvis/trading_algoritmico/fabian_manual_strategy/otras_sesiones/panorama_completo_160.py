"""
04/09/2026 -- panorama completo "en blanco", TODO sobre las 160
operaciones de la Gestion Hibrida (la que va en vivo): Parejo,
Martingala, Anti-Martingala clasico, y Confirmaciones (1 y 2, +1%/nivel),
cada uno en la grilla 1%-5% de riesgo base. Cierra con USD 1.000 y 2.000.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from escalera_de_riesgo_martingala import simular_escalera, max_drawdown, CAPITAL_INICIAL
from escalera_nivel_por_nivel_y_antimartingala import simular_anti_martingala
from antimartingala_2confirmaciones import simular_antimartingala_2conf

np.random.seed(291)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'

df = pd.read_csv(os.path.join(CARPETA, 'gestion_hibrida_resultado.csv'))
df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
df = df.sort_values(['Fecha_dt', 'Hora apertura (NY)'])
r = df['Beneficio_R'].values
n = len(r)

BASES = [1, 2, 3, 4, 5]


def parejo(r_seq, base_pct, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    valores = [capital]
    for x in r_seq:
        capital += capital * (base_pct / 100) * x
        valores.append(capital)
    return valores


def confirmaciones_1inc(r_seq, base_pct, n_conf, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    valores = [capital]
    racha = 0
    for x in r_seq:
        if racha < n_conf:
            riesgo = base_pct / 100
        else:
            nivel_extra = min(racha - (n_conf - 1), 4)
            riesgo = (base_pct + 1.0 * nivel_extra) / 100
        capital += capital * riesgo * x
        valores.append(capital)
        racha = racha + 1 if x > 0 else 0
    return valores


if __name__ == '__main__':
    filas = []
    print("=" * 110)
    print("PANORAMA COMPLETO -- 160 operaciones (Gestion Hibrida), grilla 1%-5%")
    print("=" * 110)
    for base in BASES:
        niveles = [base / 100 * (2 ** i) for i in range(5)]

        v_parejo = parejo(r, base)
        v_marti, _, _, _ = simular_escalera(r, niveles, con_tope=True)
        v_am = simular_anti_martingala(r, niveles)[0]
        v_1conf = confirmaciones_1inc(r, base, 1)
        v_2conf = confirmaciones_1inc(r, base, 2)

        print(f"\n--- Base {base}% ---")
        for nombre, valores in [('Parejo', v_parejo), ('Martingala (tope)', v_marti),
                                 ('Anti-Martingala clásico', v_am), ('1 confirmación (+1%)', v_1conf),
                                 ('2 confirmaciones (+1%)', v_2conf)]:
            final = valores[-1]
            ret = (final / CAPITAL_INICIAL - 1) * 100
            dd = max_drawdown(valores)
            print(f"  {nombre:<26} USD {final:>12,.0f}  retorno {ret:>+12.1f}%  drawdown {dd:>+7.1f}%")
            filas.append(dict(base_pct=base, esquema=nombre, capital_final=round(final, 2),
                               retorno_pct=round(ret, 1), drawdown_pct=round(dd, 1)))

    tabla = pd.DataFrame(filas)
    tabla.to_csv(os.path.join(CARPETA, 'panorama_completo_160_tabla.csv'), index=False)

    # ---- scatter retorno vs drawdown, 5 familias ----
    fig, ax = plt.subplots(figsize=(11, 7), facecolor=BG)
    ax.set_facecolor(BG)
    colores = {'Parejo': '#448aff', 'Martingala (tope)': '#ef5350', 'Anti-Martingala clásico': '#ab47bc',
               '1 confirmación (+1%)': '#ffb300', '2 confirmaciones (+1%)': '#26a69a'}
    marcadores = {'Parejo': 'o', 'Martingala (tope)': 'X', 'Anti-Martingala clásico': 'D',
                  '1 confirmación (+1%)': '^', '2 confirmaciones (+1%)': 's'}
    for esquema, g in tabla.groupby('esquema'):
        ax.scatter(g['drawdown_pct'].abs(), g['retorno_pct'], color=colores[esquema], marker=marcadores[esquema],
                   s=70, label=esquema, zorder=3)
        for _, row in g.iterrows():
            ax.annotate(f"{row['base_pct']}%", (abs(row['drawdown_pct']), row['retorno_pct']), fontsize=6.5,
                        color=WHITE, xytext=(4, 3), textcoords='offset points')
    ax.set_yscale('log')
    ax.set_xlabel('Drawdown máximo (%, valor absoluto)', color=WHITE, fontsize=9)
    ax.set_ylabel('Retorno (%, escala log)', color=WHITE, fontsize=9)
    ax.set_title('Panorama completo -- 5 esquemas x 5 niveles de riesgo, sobre las 160 operaciones', color=WHITE, fontsize=11, loc='left')
    ax.tick_params(colors=WHITE, labelsize=8)
    ax.grid(color=GRID, linewidth=0.4, alpha=0.5)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.legend(facecolor='#1e222d', edgecolor=GRID, labelcolor=WHITE, fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAF_DIR, 'panorama_completo_160.png'), dpi=150, facecolor=BG)
    print(f"\nGuardado: panorama_completo_160.png")

    # ---- USD 1.000 y 2.000, eje en 3% (2 confirmaciones, la ganadora) ----
    print(f"\n{'=' * 100}\nESCENARIO FINAL -- Base 3% (el eje), 2 confirmaciones, USD 1.000 y 2.000")
    print("=" * 100)
    fila3 = tabla[(tabla['base_pct'] == 3) & (tabla['esquema'] == '2 confirmaciones (+1%)')].iloc[0]
    for capital_inicial in [1000, 2000]:
        final = capital_inicial * (1 + fila3['retorno_pct'] / 100)
        print(f"  USD {capital_inicial:,} -> USD {final:,.0f}  (retorno {fila3['retorno_pct']:+.1f}%, drawdown {fila3['drawdown_pct']:+.1f}%)")
