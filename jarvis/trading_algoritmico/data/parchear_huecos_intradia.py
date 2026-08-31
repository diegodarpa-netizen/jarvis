"""
Parche general: detecta y descarga TODOS los huecos intra-dia reales del
XAUUSD_M1.csv base (gaps entre 10 min y 19 horas -- excluye el salto normal
de ~20h entre sesiones diarias y los ~2-3 dias de fin de semana). Encontrado
al validar el dia 4 de Fabian (19/02/2026), donde un hueco de 1 hora hacia
parecer "no reconocida" una entrada que en realidad si estaba bien.
"""
import requests, struct, lzma, datetime, time
import pandas as pd

OUTPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
SYMBOL = "XAUUSD"
HEADERS = {'User-Agent': 'Mozilla/5.0'}


def fetch_hour_ticks(dt_utc_hour, retries=4):
    y, m, d, h = dt_utc_hour.year, dt_utc_hour.month, dt_utc_hour.day, dt_utc_hour.hour
    url = f"https://datafeed.dukascopy.com/datafeed/{SYMBOL}/{y}/{m-1:02d}/{d:02d}/{h:02d}h_ticks.bi5"
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            if r.status_code == 200 and len(r.content) > 0:
                decompressed = lzma.decompress(r.content, format=lzma.FORMAT_ALONE)
                break
            elif r.status_code == 404:
                return []
        except Exception:
            pass
        time.sleep(1.5 * (attempt + 1))
    else:
        return []
    base = dt_utc_hour.replace(minute=0, second=0, microsecond=0)
    ticks = []
    n = len(decompressed) // 20
    for i in range(n):
        off = i * 20
        try:
            ms, ask, bid, _av, _bv = struct.unpack('>3I2f', decompressed[off:off + 20])
            price_bid = bid / 1000.0
            if not (100 < price_bid < 20000):
                continue
            ts = base + datetime.timedelta(milliseconds=ms)
            ticks.append((ts, ask / 1000.0, price_bid))
        except Exception:
            continue
    return ticks


def ticks_to_m1(ticks):
    if not ticks:
        return []
    buckets = {}
    for ts, ask, bid in ticks:
        mid = (ask + bid) / 2.0
        mk = ts.replace(second=0, microsecond=0)
        buckets.setdefault(mk, []).append(mid)
    return [(m, p[0], max(p), min(p), p[-1], len(p)) for m, p in sorted(buckets.items())]


if __name__ == '__main__':
    df = pd.read_csv(OUTPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    diffs = df.index.to_series().diff()
    intra = diffs[(diffs > pd.Timedelta(minutes=10)) & (diffs < pd.Timedelta(hours=19))]

    print(f"{len(intra)} huecos intra-dia a parchear")
    todas_barras = []
    for t_despues, delta in intra.items():
        t_antes = t_despues - delta
        # horas UTC completas a rellenar entre t_antes y t_despues
        hora = t_antes.replace(minute=0, second=0, microsecond=0) + pd.Timedelta(hours=1)
        while hora < t_despues:
            print(f"  Descargando {hora} ...")
            ticks = fetch_hour_ticks(hora.to_pydatetime())
            barras = ticks_to_m1(ticks)
            print(f"    {len(ticks)} ticks -> {len(barras)} velas")
            todas_barras.extend(barras)
            hora += pd.Timedelta(hours=1)

    if todas_barras:
        nuevo = pd.DataFrame(todas_barras, columns=['time', 'open', 'high', 'low', 'close', 'n_ticks'])
        nuevo['time'] = pd.to_datetime(nuevo['time'], utc=True)
        nuevo = nuevo.set_index('time')
        combinado = pd.concat([df, nuevo])
        combinado = combinado[~combinado.index.duplicated(keep='last')].sort_index()
        combinado.to_csv(OUTPUT)
        print(f"\nCSV actualizado: {len(df)} -> {len(combinado)} filas")
    else:
        print("\nNo se pudo descargar ninguna vela nueva.")
