"""
Deteccion OBJETIVA de patrones de velas japonesas (sin subjetividad -- cada
patron tiene una definicion matematica exacta) sobre XAU/USD M1, 6 meses.
A pedido de Diego (26/08/2026): investigar si existen patrones reales,
con hipotesis + estadistica, evitando la trampa de Elliott (interpretacion
visual sin regla fija).

Patrones detectados:
- Engulfing alcista/bajista: el cuerpo de la vela actual envuelve
  completamente al cuerpo de la anterior, de signo opuesto.
- Martillo (hammer) / estrella fugaz (shooting star): cuerpo chico cerca
  de un extremo del rango, mecha opuesta >= 2x el cuerpo.
- Doji: cuerpo muy chico respecto al rango total de la vela (<=10%).

Metodologia: retorno del periodo siguiente (+15 min), orientado a la
direccion que implica el patron, bootstrap 95% CI, respetando cortes de
sesion (nunca un patron ni su retorno futuro cruza el gap entre dias).
"""
import pandas as pd
import numpy as np

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
HORIZONTE = 15  # minutos hacia adelante
N_BOOTSTRAP = 5000
SEED = 42


def load():
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df['day'] = df.index.date
    return df


def detectar_patrones(g: pd.DataFrame):
    o, h, l, c = g['open'], g['high'], g['low'], g['close']
    cuerpo = (c - o).abs()
    rango = (h - l).replace(0, np.nan)
    mecha_sup = h - np.maximum(o, c)
    mecha_inf = np.minimum(o, c) - l

    bajista_prev = (c.shift(1) < o.shift(1))
    alcista_prev = (c.shift(1) > o.shift(1))

    engulfing_alcista = (c > o) & bajista_prev & (o <= c.shift(1)) & (c >= o.shift(1))
    engulfing_bajista = (c < o) & alcista_prev & (o >= c.shift(1)) & (c <= o.shift(1))

    hammer = (cuerpo <= 0.35 * rango) & (mecha_inf >= 2 * cuerpo) & (mecha_sup <= 0.15 * rango)
    shooting_star = (cuerpo <= 0.35 * rango) & (mecha_sup >= 2 * cuerpo) & (mecha_inf <= 0.15 * rango)
    doji = (cuerpo <= 0.10 * rango)

    return pd.DataFrame({
        'engulfing_alcista': engulfing_alcista, 'engulfing_bajista': engulfing_bajista,
        'hammer': hammer, 'shooting_star': shooting_star, 'doji': doji,
    }, index=g.index)


def bootstrap_ci(valores, n_boot=N_BOOTSTRAP, rng=None):
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
    df = load()

    filas = []
    ocurrencias = {p: [] for p in ['engulfing_alcista', 'engulfing_bajista', 'hammer', 'shooting_star', 'doji']}

    for day, g in df.groupby('day'):
        if len(g) < HORIZONTE + 5:
            continue
        patrones = detectar_patrones(g)
        for patron in patrones.columns:
            idx_true = patrones.index[patrones[patron]]
            for t in idx_true:
                pos = g.index.get_loc(t)
                if pos + HORIZONTE >= len(g):
                    continue
                precio_t = g['close'].iloc[pos]
                precio_fut = g['close'].iloc[pos + HORIZONTE]
                direccion = 1 if 'alcista' in patron or patron == 'hammer' else (-1 if 'bajista' in patron or patron == 'shooting_star' else 0)
                if direccion == 0:  # doji no tiene direccion implicita, se mide sin orientar
                    ret = (precio_fut - precio_t) / precio_t * 100
                else:
                    ret = (precio_fut - precio_t) / precio_t * 100 * direccion
                ocurrencias[patron].append({'t': t, 'ret': ret, 'dia': day})

    print("=" * 95)
    print(f"PATRONES DE VELAS -- XAU/USD M1, 6 meses, horizonte +{HORIZONTE}min, retorno orientado a favor del patron")
    print("=" * 95)

    for patron, lista in ocurrencias.items():
        if not lista:
            continue
        vals = np.array([x['ret'] for x in lista])
        n = len(vals)
        media_boot, lo, hi = bootstrap_ci(vals, rng=rng)
        sig = (lo > 0) or (hi < 0) if media_boot is not None else False
        wr = (vals > 0).mean() * 100
        print(f"\n{patron}: n={n} | WR={wr:.1f}% | promedio={vals.mean():.4f}% | "
              f"IC95=[{lo:.4f},{hi:.4f}]" if media_boot is not None else f"\n{patron}: n={n} (insuficiente)")
        if media_boot is not None:
            print(f"  -> {'SIGNIFICATIVO' if sig else 'no significativo'}")
        filas.append({'patron': patron, 'n': n, 'win_rate_%': round(wr, 1),
                       'promedio_%': round(vals.mean(), 4),
                       'IC95_lo': round(lo, 4) if media_boot is not None else None,
                       'IC95_hi': round(hi, 4) if media_boot is not None else None,
                       'significativo': sig if media_boot is not None else None})

    tabla = pd.DataFrame(filas)
    tabla.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/resultados_patrones_velas.csv', index=False)
    print("\nGuardado en resultados_patrones_velas.csv")

    # Guardar las ocurrencias completas de cada patron para poder elegir despues
    # las primeras 10 y graficarlas.
    import pickle
    with open('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/ocurrencias_patrones.pkl', 'wb') as f:
        pickle.dump(ocurrencias, f)
