"""
Paso 1 (a pedido de Diego, 25/08/2026): antes de probar cualquier regla,
entender bien el comportamiento base -- cuanto tiempo el precio se
mantiene alejado de la EMA9 (alcista y bajista por separado), y si hay
relacion entre CUAN LEJOS llega y CUANTO DURA alejado. Puramente
descriptivo, sobre velas diarias, 6 meses ya validados.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
OUTPUT_PNG = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/duracion_alejamiento_ema9.png'
N_BOOTSTRAP = 5000
SEED = 42


def load_daily():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    daily = df.groupby('day')['close'].last()
    daily.index = pd.to_datetime(daily.index)
    return daily.to_frame('close')


def calcular(daily):
    daily['ema9'] = daily['close'].ewm(span=9, adjust=False).mean()
    daily['dist_pct'] = (daily['close'] - daily['ema9']) / daily['ema9'] * 100
    return daily


def rachas(daily):
    sign = np.sign(daily['dist_pct'])
    change = sign.diff().fillna(1) != 0
    group_id = change.cumsum()
    filas = []
    for gid, idx in daily.groupby(group_id).groups.items():
        s = sign.loc[idx].iloc[0]
        dist = daily['dist_pct'].loc[idx].abs()
        filas.append({
            'inicio': idx[0], 'fin': idx[-1], 'dias': len(idx),
            'direccion': 'ALZA' if s > 0 else 'BAJA',
            'dist_maxima_%': dist.max(), 'dist_media_%': dist.mean(),
            'precio_inicio': daily['close'].loc[idx[0]], 'precio_fin': daily['close'].loc[idx[-1]],
        })
    return pd.DataFrame(filas)


def bootstrap_media(valores, n_boot=N_BOOTSTRAP, rng=None):
    if len(valores) < 5:
        return None, None, None
    valores = np.asarray(valores)
    medias = np.empty(n_boot)
    for i in range(n_boot):
        medias[i] = rng.choice(valores, size=len(valores), replace=True).mean()
    lo, hi = np.percentile(medias, [2.5, 97.5])
    return medias.mean(), lo, hi


def graficar(daily, tabla_rachas, out_path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9), sharex=True,
                                    gridspec_kw={'height_ratios': [3, 1]}, dpi=130)

    ax1.plot(daily.index, daily['close'], color='#333333', linewidth=1.1, label='Cierre diario XAU/USD')
    ax1.plot(daily.index, daily['ema9'], color='#1f77b4', linewidth=1.4, label='EMA9')

    for _, r in tabla_rachas.iterrows():
        color = '#2ca02c' if r['direccion'] == 'ALZA' else '#d62728'
        ax1.axvspan(r['inicio'], r['fin'], color=color, alpha=0.12)
        if r['dias'] >= 5:  # anotar solo las rachas largas, para no saturar
            mid = r['inicio'] + (r['fin'] - r['inicio']) / 2
            y = max(r['precio_inicio'], r['precio_fin'])
            ax1.annotate(f"{int(r['dias'])}d", xy=(mid, y), fontsize=8, ha='center', va='bottom', color=color)

    ax1.set_title('Distancia a EMA9 -- XAU/USD diario, 6 meses (12/02/2026-13/08/2026)\n'
                   'Verde = racha con precio ARRIBA de EMA9 | Rojo = racha ABAJO | numero = duracion en dias (solo rachas >=5 dias)',
                   fontsize=11)
    ax1.set_ylabel('Precio (USD)')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(alpha=0.25)

    ax2.plot(daily.index, daily['dist_pct'], color='#1f77b4', linewidth=1)
    ax2.axhline(0, color='black', linewidth=0.7)
    ax2.fill_between(daily.index, daily['dist_pct'], 0, where=(daily['dist_pct'] >= 0), color='#2ca02c', alpha=0.15)
    ax2.fill_between(daily.index, daily['dist_pct'], 0, where=(daily['dist_pct'] < 0), color='#d62728', alpha=0.15)
    ax2.set_ylabel('Distancia a EMA9 (%)')
    ax2.set_xlabel('Fecha')
    ax2.grid(alpha=0.25)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))

    plt.tight_layout()
    import os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, bbox_inches='tight')
    print(f"\nGrafico guardado en {out_path}")


if __name__ == '__main__':
    rng = np.random.default_rng(SEED)
    daily = load_daily()
    daily = calcular(daily)
    tabla = rachas(daily)

    print("=" * 90)
    print(f"RACHAS DE DISTANCIA A EMA9 -- {len(daily)} dias, {len(tabla)} rachas totales")
    print("=" * 90)

    print("\n--- Duracion, TODAS las rachas ---")
    print(f"Media: {tabla['dias'].mean():.2f} dias | Mediana: {tabla['dias'].median():.1f} | "
          f"Min: {tabla['dias'].min()} | Max: {tabla['dias'].max()}")
    ruido = (tabla['dias'] <= 2).sum()
    print(f"Rachas 'ruido' (<=2 dias, cruza y vuelve enseguida): {ruido} de {len(tabla)} ({ruido/len(tabla)*100:.1f}%)")

    print("\n--- Duracion, separado por direccion ---")
    for dirn in ['ALZA', 'BAJA']:
        sub = tabla[tabla['direccion'] == dirn]
        media_boot, lo, hi = bootstrap_media(sub['dias'].values, rng=rng)
        print(f"{dirn}: n={len(sub)} | media={sub['dias'].mean():.2f} dias | mediana={sub['dias'].median():.1f} | "
              f"IC95% de la media (bootstrap)=[{lo:.2f}, {hi:.2f}]" if media_boot else f"{dirn}: n={len(sub)} (insuficiente para bootstrap)")

    print("\n--- Distancia maxima alcanzada, separado por direccion ---")
    for dirn in ['ALZA', 'BAJA']:
        sub = tabla[tabla['direccion'] == dirn]
        print(f"{dirn}: media dist. maxima={sub['dist_maxima_%'].mean():.2f}% | mediana={sub['dist_maxima_%'].median():.2f}%")

    print("\n--- Patron: relacion entre CUAN LEJOS llega y CUANTO DURA la racha ---")
    corr_pearson = tabla['dist_maxima_%'].corr(tabla['dias'], method='pearson')
    corr_spearman = tabla['dist_maxima_%'].corr(tabla['dias'], method='spearman')
    print(f"Correlacion (distancia maxima vs duracion en dias): Pearson={corr_pearson:.3f} | Spearman={corr_spearman:.3f}")
    print("(Pearson mide relacion lineal, Spearman mide si va 'siempre en la misma direccion' sin exigir que sea lineal)")
    print("Lectura: cerca de 0 = no hay relacion clara. Cerca de +1 = a mas distancia, mas duracion. Cerca de -1 = a mas distancia, MENOS duracion (se revierte rapido si se extiende mucho).")

    print("\n--- Detalle de todas las rachas ---")
    print(tabla[['inicio', 'fin', 'dias', 'direccion', 'dist_maxima_%', 'dist_media_%']].round(2).to_string(index=False))

    graficar(daily, tabla, OUTPUT_PNG)
