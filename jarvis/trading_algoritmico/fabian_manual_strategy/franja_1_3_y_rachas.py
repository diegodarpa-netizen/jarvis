"""
Parte 1: franja de riesgo razonable 1%-3%, informe detallado.
Parte 2: analisis de rachas -- despues de N resultados iguales seguidos
(ganadores O perdedores, sin importar la direccion), como se comporta la
operacion siguiente. A pedido de Diego (27/08/2026).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
CAPITAL_INICIAL = 10000.0
N_BOOTSTRAP = 5000
SEED = 42


def bootstrap_ci_wr(vals, n_boot=N_BOOTSTRAP, rng=None):
    """bootstrap sobre una serie binaria (1/0) para el win rate"""
    if len(vals) < 5:
        return None, None, None
    vals = np.asarray(vals)
    medias = np.empty(n_boot)
    for i in range(n_boot):
        medias[i] = rng.choice(vals, size=len(vals), replace=True).mean()
    lo, hi = np.percentile(medias, [2.5, 97.5])
    return medias.mean() * 100, lo * 100, hi * 100


if __name__ == '__main__':
    rng = np.random.default_rng(SEED)
    df = pd.read_csv(INPUT)
    df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
    df = df.sort_values('Fecha_dt').reset_index(drop=True)

    print("=" * 100)
    print("PARTE 1 -- FRANJA DE RIESGO RAZONABLE: 1%, 1.5%, 2%, 2.5%, 3%")
    print("=" * 100)
    niveles = [1.0, 1.5, 2.0, 2.5, 3.0]
    r_serie = df['Beneficio_R'].values
    resumen = []
    curvas = {}
    for pct in niveles:
        riesgo = pct / 100
        capital = CAPITAL_INICIAL
        valores = [capital]
        for r in r_serie:
            capital += capital * riesgo * r
            valores.append(capital)
        curvas[pct] = valores
        s = pd.Series(valores)
        dd = ((s - s.cummax()) / s.cummax() * 100).min()
        resumen.append({'riesgo_%': pct, 'capital_final': round(valores[-1], 2),
                         'retorno_%': round((valores[-1]/CAPITAL_INICIAL - 1) * 100, 1),
                         'drawdown_max_%': round(dd, 2)})
    tabla1 = pd.DataFrame(resumen)
    print(tabla1.to_string(index=False))
    tabla1.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/franja_1_3_resumen.csv', index=False)

    fig1, ax = plt.subplots(figsize=(15, 8), dpi=130)
    colores = ['#1a9850', '#66bd63', '#fee08b', '#fc8d59', '#d73027']
    for (pct, valores), color in zip(curvas.items(), colores):
        ax.plot(range(len(valores)), valores, label=f'{pct}% (${valores[-1]:,.0f}, DD max {tabla1[tabla1["riesgo_%"]==pct]["drawdown_max_%"].values[0]:.1f}%)',
                color=color, linewidth=1.8)
    ax.axhline(CAPITAL_INICIAL, color='black', linestyle=':', linewidth=0.8)
    ax.set_title('Franja de riesgo razonable (1%-3%) -- USD 10.000 iniciales, 191 operaciones reales', fontsize=13, fontweight='bold')
    ax.set_xlabel('N° de operación')
    ax.set_ylabel('Capital (USD)')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/franja_1_3.png', bbox_inches='tight')
    print("\nGrafico guardado en graficos/franja_1_3.png")

    print("\n\n" + "=" * 100)
    print("PARTE 2 -- ANALISIS DE RACHAS: despues de N resultados IGUALES seguidos (sin importar signo), que hace el siguiente")
    print("=" * 100)
    df_sh = df[~df['es_hedge']].reset_index(drop=True)  # secuencia limpia, sin duplicar el mismo dia
    df_sh = df_sh[df_sh['Beneficio_R'] != 0].reset_index(drop=True)  # se excluyen breakeven para una racha binaria limpia
    resultado_bin = (df_sh['Beneficio_R'] > 0).astype(int).values  # 1=ganadora, 0=perdedora

    # calcular longitud de racha ANTES de cada operacion (cuantos iguales consecutivos vienen justo antes)
    long_racha = np.zeros(len(resultado_bin), dtype=int)
    tipo_racha = np.zeros(len(resultado_bin), dtype=int)  # 1=racha ganadora, 0=racha perdedora, -1=sin racha previa
    for i in range(1, len(resultado_bin)):
        j = i - 1
        valor_racha = resultado_bin[j]
        largo = 0
        while j >= 0 and resultado_bin[j] == valor_racha:
            largo += 1
            j -= 1
        long_racha[i] = largo
        tipo_racha[i] = valor_racha

    print("\n--- Win rate de la operacion SIGUIENTE, segun cuantas iguales vinieron antes (cualquier signo) ---")
    filas = []
    for n in [1, 2, 3, 4]:
        mask = long_racha == n
        siguientes = resultado_bin[mask]
        if len(siguientes) >= 5:
            wr, lo, hi = bootstrap_ci_wr(siguientes, rng=rng)
            sig = (lo > 65.45) or (hi < 65.45)  # comparado contra el win rate base, no contra 50%
            print(f"Racha de {n} iguales antes: n={len(siguientes)} | win rate del siguiente={wr:.1f}% | IC95=[{lo:.1f}%,{hi:.1f}%] | "
                  f"{'distinto del promedio general (65,45%)' if sig else 'no distinto del promedio general'}")
            filas.append({'largo_racha': n, 'n': len(siguientes), 'win_rate_siguiente_%': round(wr,1), 'IC_lo': round(lo,1), 'IC_hi': round(hi,1)})
        else:
            print(f"Racha de {n} iguales antes: n={len(siguientes)} (insuficiente para bootstrap)")

    print("\n--- Desglosado por tipo de racha (ganadora vs perdedora) ---")
    for n in [2, 3]:
        for tipo, nombre in [(1, 'GANADORA'), (0, 'PERDEDORA')]:
            mask = (long_racha == n) & (tipo_racha == tipo)
            siguientes = resultado_bin[mask]
            if len(siguientes) >= 5:
                wr, lo, hi = bootstrap_ci_wr(siguientes, rng=rng)
                print(f"  Racha de {n} {nombre}s seguidas -> siguiente: n={len(siguientes)} | win rate={wr:.1f}% | IC95=[{lo:.1f}%,{hi:.1f}%]")
            else:
                print(f"  Racha de {n} {nombre}s seguidas -> siguiente: n={len(siguientes)} (insuficiente)")

    pd.DataFrame(filas).to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/analisis_rachas.csv', index=False)
    print("\nGuardado en analisis_rachas.csv")
