"""
Paso 3 (a pedido de Diego, 25/08/2026): repetir el test de "duracion
restante en tiempo real" (duracion_restante_ema9.py) pero con EMAs mas
lentas (20 y 50), para ver si una EMA que filtra mas ruido anticipa mejor
cuanto le queda a una racha -- misma metodologia, generalizada a
cualquier periodo de EMA, para comparar los tres (9/20/50) lado a lado.
"""
import pandas as pd
import numpy as np

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
EMAS = [9, 20, 50]
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


def estado_por_dia(daily_close: pd.Series, span: int):
    ema = daily_close.ewm(span=span, adjust=False).mean()
    dist_pct = (daily_close - ema) / ema * 100
    sign = np.sign(dist_pct)
    change = sign.diff().fillna(1) != 0
    group_id = change.cumsum()

    filas = []
    for gid, idx in daily_close.groupby(group_id).groups.items():
        total = len(idx)
        for pos, t in enumerate(idx):
            dias_transcurridos = pos + 1
            dias_restantes = total - dias_transcurridos
            filas.append({
                'fecha': t, 'dias_transcurridos': dias_transcurridos,
                'dias_restantes': dias_restantes,
                'distancia_actual_%': abs(dist_pct.loc[t]),
                'direccion': 'ALZA' if sign.loc[t] > 0 else 'BAJA',
            })
    return pd.DataFrame(filas), group_id.nunique()


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
    close = daily['close']

    resumen_correlaciones = []

    for span in EMAS:
        estados, n_rachas = estado_por_dia(close, span)
        print("=" * 95)
        print(f"EMA{span} -- {n_rachas} rachas totales, {len(estados)} observaciones diarias")
        print("=" * 95)

        print(f"\n--- EMA{span}: duracion promedio de racha = {(len(estados)/n_rachas):.2f} dias | "
              f"ruido (rachas <=2 dias): calculando... ---")

        print(f"\n--- EMA{span}: dias restantes por ZONA DE DISTANCIA actual ---")
        bandas = [0, 0.5, 1, 2, 4, np.inf]
        etiquetas = [f"{bandas[i]}-{bandas[i+1]}%" for i in range(len(bandas) - 1)]
        estados['zona_distancia'] = pd.cut(estados['distancia_actual_%'], bins=bandas, labels=etiquetas)
        for zona, grupo in estados.groupby('zona_distancia', observed=True):
            vals = grupo['dias_restantes'].values
            media_boot, lo, hi = bootstrap_media(vals, rng=rng)
            ci_txt = f"IC95%=[{lo:.2f}, {hi:.2f}]" if media_boot is not None else "IC95%=n/a (n chico)"
            print(f"  {zona:>10}: n={len(vals):3d} | dias_restantes promedio={vals.mean():.2f} | {ci_txt}")

        print(f"\n--- EMA{span}: dias restantes por DIAS YA TRANSCURRIDOS ---")
        for dt in sorted(estados['dias_transcurridos'].unique()):
            if dt > 8:
                break
            grupo = estados[estados['dias_transcurridos'] == dt]
            vals = grupo['dias_restantes'].values
            media_boot, lo, hi = bootstrap_media(vals, rng=rng)
            ci_txt = f"IC95%=[{lo:.2f}, {hi:.2f}]" if media_boot is not None else "IC95%=n/a (n chico)"
            print(f"  Dia {dt}: n={len(vals):3d} | dias_restantes promedio={vals.mean():.2f} | {ci_txt}")

        corr_dist_p = estados['distancia_actual_%'].corr(estados['dias_restantes'], method='pearson')
        corr_dist_s = estados['distancia_actual_%'].corr(estados['dias_restantes'], method='spearman')
        corr_dt_p = estados['dias_transcurridos'].corr(estados['dias_restantes'], method='pearson')
        corr_dt_s = estados['dias_transcurridos'].corr(estados['dias_restantes'], method='spearman')

        print(f"\n--- EMA{span}: correlaciones ---")
        print(f"distancia_actual vs dias_restantes: Pearson={corr_dist_p:.3f} | Spearman={corr_dist_s:.3f}")
        print(f"dias_transcurridos vs dias_restantes: Pearson={corr_dt_p:.3f} | Spearman={corr_dt_s:.3f}")
        print()

        resumen_correlaciones.append({
            'EMA': span, 'n_rachas': n_rachas, 'dias_promedio_racha': round(len(estados) / n_rachas, 2),
            'corr_distancia_vs_restante_pearson': round(corr_dist_p, 3),
            'corr_distancia_vs_restante_spearman': round(corr_dist_s, 3),
            'corr_transcurrido_vs_restante_pearson': round(corr_dt_p, 3),
            'corr_transcurrido_vs_restante_spearman': round(corr_dt_s, 3),
        })

    print("=" * 95)
    print("RESUMEN COMPARATIVO -- EMA9 vs EMA20 vs EMA50")
    print("=" * 95)
    tabla_resumen = pd.DataFrame(resumen_correlaciones)
    print(tabla_resumen.to_string(index=False))
    tabla_resumen.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/resultados_duracion_restante_multi_ema.csv', index=False)
    print("\nGuardado en resultados_duracion_restante_multi_ema.csv")
