"""
Descarga el tramo 14/08/2026 - 27/08/2026 (9 dias con operaciones reales de
Fabian que todavia no evaluamos) para completar el dataset del proceso vela
por vela. Mismo motor validado que los downloaders anteriores. Ventana
08:00-11:59 NY por dia (ajustada a DST automaticamente via pytz).
"""
import requests, struct, lzma, datetime, time
import pandas as pd
import pytz

OUTPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
SYMBOL = "XAUUSD"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
NY = pytz.timezone('America/New_York')
UTC = pytz.UTC

DIAS = ['2026-08-14', '2026-08-15', '2026-08-16', '2026-08-17', '2026-08-18',
        '2026-08-19', '2026-08-20', '2026-08-21', '2026-08-22', '2026-08-23',
        '2026-08-24', '2026-08-25', '2026-08-26', '2026-08-27']


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
    todas_barras = []
    for dstr in DIAS:
        dia = pd.Timestamp(dstr)
        ini_ny = NY.localize(datetime.datetime(dia.year, dia.month, dia.day, 8, 0))
        fin_ny = NY.localize(datetime.datetime(dia.year, dia.month, dia.day, 11, 59))
        ini_utc = ini_ny.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
        fin_utc = fin_ny.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
        hora = ini_utc
        n_dia = 0
        while hora <= fin_utc:
            ticks = fetch_hour_ticks(hora)
            barras = ticks_to_m1(ticks)
            n_dia += len(barras)
            todas_barras.extend(barras)
            hora += pd.Timedelta(hours=1)
        print(f"{dstr}: {n_dia} velas M1")

    if todas_barras:
        nuevo = pd.DataFrame(todas_barras, columns=['time', 'open', 'high', 'low', 'close', 'n_ticks'])
        nuevo['time'] = pd.to_datetime(nuevo['time'], utc=True)
        nuevo = nuevo.set_index('time')
        existente = pd.read_csv(OUTPUT, index_col=0)
        existente.index = pd.to_datetime(existente.index, utc=True)
        combinado = pd.concat([existente, nuevo])
        combinado = combinado[~combinado.index.duplicated(keep='last')].sort_index()
        combinado.to_csv(OUTPUT)
        print(f"\nCSV actualizado: {len(existente)} -> {len(combinado)} filas")
    else:
        print("No se descargo nada nuevo")
