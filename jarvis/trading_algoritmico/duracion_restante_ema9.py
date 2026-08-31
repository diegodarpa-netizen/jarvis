"""
Paso 2 (a pedido de Diego, 25/08/2026): en vez de mirar la distancia
MAXIMA que termino alcanzando una racha (eso solo se sabe despues), ver
si la distancia ACTUAL -- mientras la racha todavia esta en curso -- sirve
para anticipar cuantos dias MAS le quedan. Esto si es utilizable en
tiempo real, sin mirar el futuro.
"""
import pandas as pd
import numpy as np

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
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


def estado_por_dia(daily):
    daily['ema9'] = daily['close'].ewm(span=9, adjust=False).mean()
    daily['dist_pct'] = (daily['close'] - daily['ema9']) / daily['ema9'] * 100
    sign = np.sign(daily['dist_pct'])
    change = sign.diff().fillna(1) != 0
    group_id = change.cumsum()

    filas = []
    for gid, idx in daily.groupby(group_id).groups.items():
        total = len(idx)
        for pos, t in enumerate(idx):
            dias_transcurridos = pos + 1
            dias_restantes = total - dias_transcurridos  # 0 = hoy es el ultimo dia de la racha
            filas.append({
                'fecha': t, 'dias_transcurridos': dias_transcurridos,
                'dias_restantes': dias_restantes,
                'distancia_actual_%': abs(daily['dist_pct'].loc[t]),
                'direccion': 'ALZA' if sign.loc[t] > 0 else 'BAJA',
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


if __name__ == '__main__':
    rng = np.random.default_rng(SEED)
    daily = load_daily()
    estados = estado_por_dia(daily)

    print("=" * 95)
    print(f"DIAS RESTANTES SEGUN ESTADO ACTUAL -- {len(estados)} observaciones diarias (dentro de rachas)")
    print("=" * 95)

    print("\n--- Por DISTANCIA ACTUAL a la EMA9 (bandas) ---")
    bandas = [0, 0.5, 1, 2, 4, np.inf]
    etiquetas = [f"{bandas[i]}-{bandas[i+1]}%" for i in range(len(bandas) - 1)]
    estados['zona_distancia'] = pd.cut(estados['distancia_actual_%'], bins=bandas, labels=etiquetas)
    for zona, grupo in estados.groupby('zona_distancia', observed=True):
        vals = grupo['dias_restantes'].values
        media_boot, lo, hi = bootstrap_media(vals, rng=rng)
        ci_txt = f"IC95%=[{lo:.2f}, {hi:.2f}]" if media_boot is not None else "IC95%=n/a (n chico)"
        print(f"  {zona:>10}: n={len(vals):3d} | dias_restantes promedio={vals.mean():.2f} | {ci_txt}")

    print("\n--- Por DIAS YA TRANSCURRIDOS en la racha actual ---")
    for dt in sorted(estados['dias_transcurridos'].unique()):
        if dt > 8:
            break
        grupo = estados[estados['dias_transcurridos'] == dt]
        vals = grupo['dias_restantes'].values
        media_boot, lo, hi = bootstrap_media(vals, rng=rng)
        ci_txt = f"IC95%=[{lo:.2f}, {hi:.2f}]" if media_boot is not None else "IC95%=n/a (n chico)"
        print(f"  Dia {dt}: n={len(vals):3d} | dias_restantes promedio={vals.mean():.2f} | {ci_txt}")

    print("\n--- Correlacion distancia_actual vs dias_restantes (sin mirar el futuro, solo estado presente) ---")
    corr_p = estados['distancia_actual_%'].corr(estados['dias_restantes'], method='pearson')
    corr_s = estados['distancia_actual_%'].corr(estados['dias_restantes'], method='spearman')
    print(f"Pearson={corr_p:.3f} | Spearman={corr_s:.3f}")

    print("\n--- Correlacion dias_transcurridos vs dias_restantes ('memoria' de la racha) ---")
    corr_p2 = estados['dias_transcurridos'].corr(estados['dias_restantes'], method='pearson')
    corr_s2 = estados['dias_transcurridos'].corr(estados['dias_restantes'], method='spearman')
    print(f"Pearson={corr_p2:.3f} | Spearman={corr_s2:.3f}")
    print("(negativo = cuantos mas dias ya lleva, menos le quedan -- 'memoryless'. Positivo = las que ya vienen largas siguen largas.)")
