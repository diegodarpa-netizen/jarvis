"""
Descarga una semana completa (Lunes a Viernes) de 24hs de XAUUSD para el
analisis de franjas horarias que pidio Diego (28/08/2026): "quiero que solo
analicemos una semana... todo el dia... dame todos los datos". Semana
elegida: 17/08/2026 (Lunes, arranca domingo 23:00 NY = apertura semanal) a
22/08/2026 (Viernes).
"""
import requests, struct, lzma, datetime, time
import pandas as pd
import pytz

SYMBOL = "XAUUSD"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
NY = pytz.timezone('America/New_York')
UTC = pytz.UTC
OUTPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/franjas_horarias/XAUUSD_M1_semana_18al22ago2026.csv'

# apertura semanal domingo ~17:00 NY (23/08 es sabado, no hay) -- arranca
# domingo 16/08 17:00 NY hasta viernes 22/08 17:00 NY (cierre semanal)
INICIO = NY.localize(datetime.datetime(2026, 8, 16, 17, 0))
FIN = NY.localize(datetime.datetime(2026, 8, 22, 17, 0))


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
    ini_utc = INICIO.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
    fin_utc = FIN.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
    horas_totales = int((fin_utc - ini_utc).total_seconds() / 3600) + 1
    print(f"Descargando {horas_totales} horas: {ini_utc} -> {fin_utc}")

    todas_barras = []
    fallidas = []
    hora = ini_utc
    n = 0
    while hora <= fin_utc:
        ticks = fetch_hour_ticks(hora)
        barras = ticks_to_m1(ticks)
        todas_barras.extend(barras)
        if not barras:
            fallidas.append(hora)
        n += 1
        if n % 20 == 0:
            print(f"  ... {n}/{horas_totales} horas procesadas")
        hora += pd.Timedelta(hours=1)

    print(f"\nHoras sin dato (posible fin de semana o fallo): {len(fallidas)}")
    for h in fallidas:
        print(" ", h)

    df = pd.DataFrame(todas_barras, columns=['time', 'open', 'high', 'low', 'close', 'n_ticks'])
    df['time'] = pd.to_datetime(df['time'], utc=True)
    df = df.set_index('time').sort_index()
    df = df[~df.index.duplicated(keep='last')]
    df.to_csv(OUTPUT)
    print(f"\nGuardado: {OUTPUT} ({len(df)} velas M1)")
