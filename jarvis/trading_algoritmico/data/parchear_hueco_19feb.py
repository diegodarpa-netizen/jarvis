"""
Parche puntual: al XAUUSD_M1.csv base le falta la hora 14:00-14:59 UTC
(09:00-09:59 NY) del 19/02/2026 -- encontrado al validar el dia 4 de Fabian
(SELL 09:07, no reconocido por falta de dato, no por logica). Descarga esa
sola hora via Dukascopy (mismo motor validado) y la inserta en el CSV.
"""
import requests, struct, lzma, datetime, os
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
                print("404 -- sin datos para esa hora en Dukascopy")
                return []
        except Exception as e:
            print("error:", e)
        import time
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
    hora_faltante = datetime.datetime(2026, 2, 19, 14, 0, tzinfo=datetime.timezone.utc)
    print(f"Descargando hora faltante: {hora_faltante}")
    ticks = fetch_hour_ticks(hora_faltante)
    print(f"{len(ticks)} ticks descargados")
    barras = ticks_to_m1(ticks)
    print(f"{len(barras)} velas M1 generadas")

    if not barras:
        print("Sin datos -- no se puede parchear (revisar si Dukascopy realmente no tiene esa hora)")
    else:
        nuevo = pd.DataFrame(barras, columns=['time', 'open', 'high', 'low', 'close', 'n_ticks'])
        nuevo['time'] = pd.to_datetime(nuevo['time'], utc=True)
        nuevo = nuevo.set_index('time')

        existente = pd.read_csv(OUTPUT, index_col=0)
        existente.index = pd.to_datetime(existente.index, utc=True)

        combinado = pd.concat([existente, nuevo])
        combinado = combinado[~combinado.index.duplicated(keep='last')].sort_index()
        combinado.to_csv(OUTPUT)
        print(f"CSV actualizado: {len(existente)} -> {len(combinado)} filas")
