"""
Descarga de XAU/USD 24 HORAS (Asia + Londres + NY completas), desde el
mismo arranque que el historial real de Fabian (27/10/2025) hasta hoy.
A pedido de Diego (27/08/2026): probar la estrategia con datos de
sesion completa, no solo la ventana angosta que usa Fabian.

Mismo motor validado que download_dukascopy_5y.py / download_gap_fabian.py
(resume + caffeinate + sin repaint), unico cambio es la ventana horaria:
00:00-23:59 NY en vez de una franja acotada.
"""
import requests, struct, lzma, datetime, os, csv, time
import pytz

OUTPUT = os.path.join(os.path.dirname(__file__), 'XAUUSD_M1_24h_fabian.csv')
SYMBOL = "XAUUSD"
NY_TZ = pytz.timezone("America/New_York")
UTC = pytz.UTC
WINDOW_START_NY = datetime.time(0, 0)
WINDOW_END_NY = datetime.time(23, 59)
HEADERS = {'User-Agent': 'Mozilla/5.0'}

START = datetime.date(2025, 10, 27)

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
            ms, ask, bid, _av, _bv = struct.unpack('>3I2f', decompressed[off:off+20])
            price_bid = bid / 1000.0
            if not (100 < price_bid < 20000):
                continue
            ts = base + datetime.timedelta(milliseconds=ms)
            ticks.append((ts, ask/1000.0, price_bid))
        except Exception:
            continue
    return ticks

def ticks_to_m1(ticks):
    if not ticks:
        return []
    buckets = {}
    for ts, ask, bid in ticks:
        mid = (ask+bid)/2.0
        mk = ts.replace(second=0, microsecond=0)
        buckets.setdefault(mk, []).append(mid)
    return [(m, p[0], max(p), min(p), p[-1], len(p)) for m, p in sorted(buckets.items())]

def hours_for_day_ny(date_ny):
    s = NY_TZ.localize(datetime.datetime.combine(date_ny, WINDOW_START_NY)).astimezone(UTC)
    e = NY_TZ.localize(datetime.datetime.combine(date_ny, WINDOW_END_NY)).astimezone(UTC)
    hour = s.replace(minute=0, second=0, microsecond=0)
    hours = []
    while hour <= e:
        hours.append(hour)
        hour += datetime.timedelta(hours=1)
    return hours

def cargar_existente():
    if not os.path.exists(OUTPUT):
        return []
    bars = []
    with open(OUTPUT, newline='') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 6:
                continue
            ts = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').replace(tzinfo=UTC)
            bars.append((ts, float(row[1]), float(row[2]), float(row[3]), float(row[4]), int(row[5])))
    return bars

def _save(bars):
    bars_sorted = sorted(bars, key=lambda x: x[0])
    with open(OUTPUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['time','open','high','low','close','n_ticks'])
        for b in bars_sorted:
            w.writerow([b[0].strftime('%Y-%m-%d %H:%M:%S'), *[round(x,3) for x in b[1:5]], b[5]])

if __name__ == '__main__':
    END = datetime.date.today()
    existentes = cargar_existente()
    if existentes:
        ultima = max(b[0].date() for b in existentes)
        resume_from = ultima + datetime.timedelta(days=1)
        existentes = [b for b in existentes if b[0].date() < ultima]
        print(f"Retomando -- ya habia datos hasta {ultima}. Continua desde {resume_from}.", flush=True)
    else:
        resume_from = START
        existentes = []
        print(f"Descargando XAU/USD 24hs: {START} -> {END}", flush=True)

    all_bars = existentes
    current = resume_from
    dias_done = 0
    total_days = (END - START).days + 1
    while current <= END:
        if current.weekday() < 5:
            day_ticks = []
            for hu in hours_for_day_ny(current):
                day_ticks.extend(fetch_hour_ticks(hu))
                time.sleep(0.2)
            db = ticks_to_m1(day_ticks)
            if db:
                all_bars.extend(db)
        dias_done += 1
        if dias_done % 5 == 0:
            print(f"  Progreso: {current} ({dias_done}/{total_days} dias, {len(all_bars)} velas)", flush=True)
            _save(all_bars)
        current += datetime.timedelta(days=1)
    _save(all_bars)
    print(f"Listo. {len(all_bars)} velas guardadas.", flush=True)
