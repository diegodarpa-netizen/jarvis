"""
Descarga datos de XAU/USD M3 de Dukascopy para un rango de fechas completo.
"""
import requests, struct, datetime, os, csv, time, gzip
from io import BytesIO

OUTPUT = os.path.join(os.path.dirname(__file__), 'data', 'XAUUSD_M3.csv')

START = datetime.date(2025, 10, 1)
END   = datetime.date(2026, 5, 29)

def fetch_day(date):
    """Descarga velas M3 BID de Dukascopy para una fecha dada."""
    ts = int(datetime.datetime.combine(date, datetime.time(0,0)).timestamp()) * 1000
    url = (f"https://freeserv.dukascopy.com/2.0/?"
           f"path=chart/json/{date.year}/{date.month-1:02d}/{date.day:02d}/BID_candles_min_3"
           f"&jsonp=_callbacks____chart_json_")

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://freeserv.dukascopy.com'
    }

    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return []

        text = r.text.strip()
        # Remover wrapper jsonp
        if text.startswith('_callbacks____chart_json_('):
            text = text[len('_callbacks____chart_json_('):-1]

        import json
        data = json.loads(text)
        candles = []
        for item in data:
            ts_ms, o, h, l, c, vol = item
            dt = datetime.datetime.fromtimestamp(ts_ms/1000, tz=datetime.timezone.utc)
            candles.append((dt, round(o,3), round(h,3), round(l,3), round(c,3), int(vol)))
        return candles
    except Exception as e:
        return []


def fetch_day_binary(date):
    """Descarga datos binarios tick de Dukascopy y parsea OHLCV M3."""
    # URL formato binario de Dukascopy
    y = date.year
    m = date.month - 1  # Dukascopy usa mes base 0
    d = date.day

    # Intentar con diferentes formatos de URL de Dukascopy
    urls = [
        f"https://datafeed.dukascopy.com/datafeed/XAUUSD/{y}/{m:02d}/{d:02d}/BID_candles_min_3.bi5",
        f"https://freeserv.dukascopy.com/2.0/?path=chart/json/{y}/{m:02d}/{d:02d}/BID_candles_min_3&jsonp=cb",
    ]

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200 and len(r.content) > 0:
                if url.endswith('.bi5'):
                    return parse_bi5(r.content, date)
        except:
            continue
    return []


def parse_bi5(data, date):
    """Parsea el formato binario .bi5 de Dukascopy."""
    try:
        decompressed = gzip.decompress(data)
    except:
        try:
            import lzma
            decompressed = lzma.decompress(data)
        except:
            return []

    # Cada registro: 4 bytes timestamp (ms desde medianoche) + 4 floats OHLCV
    RECORD = 20  # 4 + 4*4 bytes (LZMA format for candles)
    candles = []
    base_dt = datetime.datetime.combine(date, datetime.time(0,0), tzinfo=datetime.timezone.utc)

    for i in range(0, len(decompressed) - RECORD + 1, RECORD):
        try:
            ts_ms = struct.unpack('>I', decompressed[i:i+4])[0]
            o = struct.unpack('>f', decompressed[i+4:i+8])[0]
            h = struct.unpack('>f', decompressed[i+8:i+12])[0]
            l = struct.unpack('>f', decompressed[i+12:i+16])[0]
            c = struct.unpack('>f', decompressed[i+16:i+20])[0]
            dt = base_dt + datetime.timedelta(milliseconds=ts_ms)
            if 1000 < o < 10000:
                candles.append((dt, round(o,3), round(h,3), round(l,3), round(c,3), 0))
        except:
            continue
    return candles


if __name__ == '__main__':
    print(f"Descargando XAU/USD M3 — {START} → {END}")
    print(f"Guardando en: {OUTPUT}\n")

    all_candles = []
    current = START
    days_total = (END - START).days + 1
    days_done  = 0
    errors     = 0

    while current <= END:
        if current.weekday() < 5:  # Solo días de semana
            candles = fetch_day_binary(current)
            if candles:
                all_candles.extend(candles)
                print(f"  {current} — {len(candles)} velas OK")
            else:
                errors += 1
                print(f"  {current} — sin datos")
            time.sleep(0.3)  # Respetar el servidor

        days_done += 1
        if days_done % 20 == 0:
            pct = days_done / days_total * 100
            print(f"\n  Progreso: {pct:.0f}% ({days_done}/{days_total} días)\n")

        current += datetime.timedelta(days=1)

    # Guardar CSV
    all_candles.sort(key=lambda x: x[0])
    with open(OUTPUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['time','open','high','low','close','volume'])
        for c in all_candles:
            w.writerow([c[0].strftime('%Y-%m-%d %H:%M:%S'), c[1], c[2], c[3], c[4], c[5]])

    print(f"\nListo. {len(all_candles)} velas guardadas en {OUTPUT}")
    print(f"Errores/días sin datos: {errors}")
