"""
04/09/2026 -- corrida COMPLETA y definitiva sobre las 160 operaciones de
la Gestion Hibrida (la que se va a operar en vivo), con la configuracion
final confirmada: Base 3% + incremento 2%/nivel + 2 confirmaciones +
techo en la operacion #6 (tope_extra=4). Junta en un solo lugar: equity
+ drawdown en el tiempo, todos los episodios de drawdown, stress test de
rachas (clasico y calibrado con crisis reales del oro), y el resumen de
semanas.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from escalera_de_riesgo_martingala import max_drawdown, CAPITAL_INICIAL

np.random.seed(281)
CARPETA = os.path.dirname(__file__)
GRAF_DIR = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos'
BG, GRID, WHITE = '#131722', '#2a2e39', '#d1d4dc'
GREEN, RED = '#26a69a', '#ef5350'

BASE, INC, N_CONF, TOPE_EXTRA = 3.0, 2.0, 2, 4

df = pd.read_csv(os.path.join(CARPETA, 'gestion_hibrida_resultado.csv'))
df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
df = df.sort_values(['Fecha_dt', 'Hora apertura (NY)']).reset_index(drop=True)
fechas = df['Fecha_dt'].tolist()
r = df['Beneficio_R'].values
n = len(r)
losses_pool = r[r < 0]


def simular(r_seq, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    valores = [capital]
    racha = 0
    for x in r_seq:
        if racha < N_CONF:
            riesgo = BASE / 100
        else:
            nivel_extra = min(racha - (N_CONF - 1), TOPE_EXTRA)
            riesgo = (BASE + INC * nivel_extra) / 100
        capital += capital * riesgo * x
        valores.append(capital)
        racha = racha + 1 if x > 0 else 0
    return valores


def bootstrap(r_pool, n_ops, n_iter=3000):
    finales = np.empty(n_iter); drawdowns = np.empty(n_iter)
    for it in range(n_iter):
        muestra = np.random.choice(r_pool, size=n_ops, replace=True)
        valores = simular(muestra)
        finales[it] = valores[-1]; drawdowns[it] = max_drawdown(valores)
    return finales, drawdowns


def drawdown_curva(valores):
    s = pd.Series(valores)
    return ((s - s.cummax()) / s.cummax() * 100).values


def extraer_episodios(fechas_dd, dd, umbral=1.0):
    episodios = []
    en_ep = False; inicio = None; peor = 0.0; peor_f = None
    for f, d in zip(fechas_dd, dd):
        if d < 0 and not en_ep:
            en_ep = True; inicio = f; peor = d; peor_f = f
        elif d < 0 and en_ep:
            if d < peor: peor = d; peor_f = f
        elif d >= 0 and en_ep:
            if abs(peor) >= umbral:
                episodios.append(dict(inicio=inicio, fondo=peor_f, fin=f, profundidad=round(peor, 2),
                                       dias_fondo=(peor_f - inicio).days, dias_recup=(f - peor_f).days))
            en_ep = False
    return episodios


if __name__ == '__main__':
    print("=" * 100)
    print(f"ESCENARIO FINAL -- 160 operaciones, Base {BASE}% + incremento {INC}% + {N_CONF} confirmaciones, techo op.#{N_CONF+TOPE_EXTRA}")
    print("=" * 100)

    valores = simular(r)
    final = valores[-1]
    ret = (final / CAPITAL_INICIAL - 1) * 100
    dd_real = max_drawdown(valores)
    dd_curva = drawdown_curva(valores)
    print(f"Capital: USD {CAPITAL_INICIAL:.0f} -> USD {final:,.0f}  ({ret:+.1f}%)")
    print(f"Drawdown real: {dd_real:+.1f}%")

    finales_b, dd_b = bootstrap(r, n)
    print(f"Bootstrap: P(+)={( finales_b>CAPITAL_INICIAL).mean()*100:.1f}%  DD mediana={np.median(dd_b):+.1f}%  DD peor5%={np.percentile(dd_b,5):+.1f}%")

    # -- episodios de drawdown --
    episodios = extraer_episodios([fechas[0]] + fechas, dd_curva)
    print(f"\nEpisodios de drawdown (>1%): {len(episodios)}")
    for ep in sorted(episodios, key=lambda e: e['profundidad'])[:8]:
        print(f"  {ep['inicio'].date()} -> fondo {ep['fondo'].date()} -> recupera {ep['fin'].date()}: {ep['profundidad']:+.1f}% ({ep['dias_fondo']}d caida, {ep['dias_recup']}d recup.)")

    # -- stress rachas clasico --
    print(f"\n-- Stress test rachas de 3 perdidas (K forzadas) --")
    def construir_stress(k, seed):
        rng = np.random.RandomState(seed)
        ops_relleno = max(n - k*3, 0)
        seq = list(rng.choice(r, size=ops_relleno, replace=True))
        bloques = [rng.choice(losses_pool, size=3, replace=True) for _ in range(k)]
        posiciones = sorted(rng.choice(range(len(seq)+1), size=k, replace=False)) if len(seq)>=k else list(range(k))
        offset=0
        for pos, bloque in zip(posiciones, bloques):
            idx = pos+offset
            seq[idx:idx] = list(bloque)
            offset += 3
        return np.array(seq)

    for k in [3, 6, 9, 12]:
        finales_s, dd_s = [], []
        for sim in range(300):
            seq = construir_stress(k, seed=k*100+sim)
            valores_s = simular(seq)
            finales_s.append(valores_s[-1]); dd_s.append(max_drawdown(valores_s))
        finales_s=np.array(finales_s); dd_s=np.array(dd_s)
        print(f"  K={k} rachas de 3L: retorno_mediana={(np.median(finales_s)/CAPITAL_INICIAL-1)*100:+.1f}%  dd_mediana={np.median(dd_s):+.1f}%  dd_peor5={np.percentile(dd_s,5):+.1f}%  P(+)={(finales_s>CAPITAL_INICIAL).mean()*100:.1f}%")

    # -- stress crisis real oro (racha larga + gap) --
    print(f"\n-- Stress test crisis real del oro (racha larga + gap -3R) --")
    def stress_crisis(longitud, seed):
        rng = np.random.RandomState(seed)
        n_relleno = n - longitud - 1
        seq = list(rng.choice(r, size=n_relleno, replace=True))
        racha = list(rng.choice(losses_pool, size=longitud, replace=True))
        pos = rng.randint(0, len(seq))
        seq[pos:pos] = racha
        pos2 = rng.randint(0, len(seq))
        seq.insert(pos2, -3.0)
        return np.array(seq)

    for longitud in [5, 6, 7]:
        finales_c, dd_c = [], []
        for sim in range(300):
            seq = stress_crisis(longitud, seed=1000*longitud+sim)
            valores_c = simular(seq)
            finales_c.append(valores_c[-1]); dd_c.append(max_drawdown(valores_c))
        finales_c=np.array(finales_c); dd_c=np.array(dd_c)
        print(f"  Racha de {longitud}+gap: retorno_mediana={(np.median(finales_c)/CAPITAL_INICIAL-1)*100:+.1f}%  dd_mediana={np.median(dd_c):+.1f}%  dd_peor5={np.percentile(dd_c,5):+.1f}%  P(+)={(finales_c>CAPITAL_INICIAL).mean()*100:.1f}%")

    # -- grafico equity + drawdown --
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), facecolor=BG, gridspec_kw={'height_ratios': [1.3, 1]})
    ax_eq, ax_dd = axes
    fechas_completo = [fechas[0]] + fechas
    ax_eq.plot(fechas_completo, valores, color=GREEN, linewidth=1.3)
    ax_eq.set_yscale('log')
    ax_eq.set_facecolor(BG)
    ax_eq.set_title(f"Escenario final -- 160 ops, Base {BASE}%+2conf+incremento {INC}%, techo op.#6\nUSD {CAPITAL_INICIAL:,.0f} -> USD {final:,.0f} ({ret:+,.1f}%)", color=WHITE, fontsize=11, loc='left', fontweight='bold')
    ax_eq.grid(color=GRID, linewidth=0.4, alpha=0.5)
    ax_eq.tick_params(colors=WHITE, labelsize=8)
    for s in ax_eq.spines.values(): s.set_color(GRID)
    ax_eq.set_ylabel('Capital USD (log)', color=WHITE, fontsize=8)
    ax_eq.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))

    ax_dd.fill_between(fechas_completo, dd_curva, 0, color=RED, alpha=0.4)
    ax_dd.plot(fechas_completo, dd_curva, color=RED, linewidth=0.9)
    ax_dd.set_facecolor(BG)
    ax_dd.set_title(f'Drawdown en el tiempo -- máximo {dd_real:.1f}%', color=WHITE, fontsize=9.5, loc='left')
    ax_dd.grid(color=GRID, linewidth=0.4, alpha=0.5)
    ax_dd.tick_params(colors=WHITE, labelsize=8)
    for s in ax_dd.spines.values(): s.set_color(GRID)
    ax_dd.set_ylabel('Drawdown %', color=WHITE, fontsize=8)
    ax_dd.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))

    plt.tight_layout()
    out = os.path.join(GRAF_DIR, 'escenario_final_160_completo.png')
    plt.savefig(out, dpi=150, facecolor=BG)
    print(f"\nGuardado: {out}")
