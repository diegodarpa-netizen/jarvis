"""
Parche: 4 dias donde el M1 arranca a las 09:00 NY en vez de las 08:00 NY
habituales (falta la hora previa a la sesion, necesaria para construir M3
antes de que abra la ventana operable). Encontrado al investigar por que el
codigo no reconocia la entrada real de Fabian del 16/06/2026.
"""
import requests, struct, lzma, datetime, time
import pandas as pd
import pytz

OUTPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
SYMBOL = "XAUUSD"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
NY = pytz.timezone('America/New_York')
UTC = pytz.UTC

DIAS = ['2026-03-06', '2026-04-27', '2026-06-04', '2026-06-16']


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
        objetivo_ny = NY.localize(datetime.datetime(dia.year, dia.month, dia.day, 8, 0))
        hora_utc = objetivo_ny.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
        print(f"Descargando {dstr}: hora faltante {hora_utc}")
        ticks = fetch_hour_ticks(hora_utc.to_pydatetime() if hasattr(hora_utc, 'to_pydatetime') else hora_utc)
        barras = ticks_to_m1(ticks)
        print(f"  {len(ticks)} ticks -> {len(barras)} velas")
        todas_barras.extend(barras)

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
