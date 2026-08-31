"""
Descarga de S&P 500 CFD (USA500.IDX) para jarvis/trading_algoritmico.

Decidido con Diego el 25/08/2026: se valido la regla "Pullback 3 dias"
(ver estrategias_validadas/pullback_3dias_spx.md) en diario y semanal
sobre el indice (Yahoo Finance) con resultado positivo y significativo.
El paso que falta es intradia -- para eso hace falta tick data real, y
Yahoo Finance solo da ~2 anios de horario (insuficiente). Dukascopy
ofrece USA500.IDX con años de historia real en tick, mismo formato que
ya usamos y validamos con XAUUSD.

Simbolo verificado: Dukascopy Bank SA ofrece USA500.IDX como CFD sobre
S&P 500 (correlaciona con el futuro del mes siguiente), tick data
exportable a M1/M5/M15/M30/H1/H4/D1.

Mismo motor y logica de resume que download_dukascopy_5y.py (clonado
13/08-25/08/2026): ticks por hora, LZMA "alone", 20 bytes/tick, ventana
03:00-17:00 hora NY (cubre pre-market + sesion regular NYSE 09:30-16:00
+ un margen), resume automatico desde el ultimo dia guardado, pensado
para correr con `caffeinate -i` en background.
"""
import requests, struct, lzma, datetime, os, csv, time
import pytz

OUTPUT = os.path.join(os.path.dirname(__file__), 'USA500_M1_5y.csv')
SYMBOL = "USA500IDXUSD"  # verificado 25/08/2026: USA500.IDX solo (sin USD) da 404
NY_TZ = pytz.timezone("America/New_York")
UTC = pytz.UTC

WINDOW_START_NY = datetime.time(3, 0)
WINDOW_END_NY = datetime.time(17, 0)

HEADERS = {'User-Agent': 'Mozilla/5.0'}


def fetch_hour_ticks(dt_utc_hour: datetime.datetime, retries: int = 4) -> list:
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
            ms, ask, bid, _ask_vol, _bid_vol = struct.unpack('>3I2f', decompressed[off:off + 20])
            price_ask = ask / 1000.0
            price_bid = bid / 1000.0
            if not (100 < price_bid < 20000):
                continue
            ts = base + datetime.timedelta(milliseconds=ms)
            ticks.append((ts, price_ask, price_bid))
        except Exception:
            continue
    return ticks


def ticks_to_m1(ticks: list) -> list:
    if not ticks:
        return []
    buckets = {}
    for ts, ask, bid in ticks:
        mid = (ask + bid) / 2.0
        minute_key = ts.replace(second=0, microsecond=0)
        buckets.setdefault(minute_key, []).append(mid)

    bars = []
    for minute, prices in sorted(buckets.items()):
        bars.append((minute, prices[0], max(prices), min(prices), prices[-1], len(prices)))
    return bars


def hours_for_day_ny(date_ny: datetime.date):
    start_ny = NY_TZ.localize(datetime.datetime.combine(date_ny, WINDOW_START_NY))
    end_ny = NY_TZ.localize(datetime.datetime.combine(date_ny, WINDOW_END_NY))
    start_utc = start_ny.astimezone(UTC)
    end_utc = end_ny.astimezone(UTC)

    hour = start_utc.replace(minute=0, second=0, microsecond=0)
    hours = []
    while hour <= end_utc:
        hours.append(hour)
        hour += datetime.timedelta(hours=1)
    return hours


def cargar_existente() -> list:
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


def download_range(start_date: datetime.date, end_date: datetime.date,
                    all_bars: list, dias_ya_hechos: int, total_days: int, delay=0.2):
    current = start_date
    days_done = dias_ya_hechos
    days_with_data = len({b[0].date() for b in all_bars})

    while current <= end_date:
        if current.weekday() < 5:
            day_ticks = []
            for hour_utc in hours_for_day_ny(current):
                day_ticks.extend(fetch_hour_ticks(hour_utc))
                time.sleep(delay)
            day_bars = ticks_to_m1(day_ticks)
            if day_bars:
                all_bars.extend(day_bars)
                days_with_data += 1
        days_done += 1
        if days_done % 10 == 0:
            print(f"  Progreso: {days_done}/{total_days} dias ({days_with_data} con datos, {len(all_bars)} velas)", flush=True)
            _save(all_bars)
        current += datetime.timedelta(days=1)

    return all_bars


def _save(bars):
    bars_sorted = sorted(bars, key=lambda x: x[0])
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['time', 'open', 'high', 'low', 'close', 'n_ticks'])
        for b in bars_sorted:
            w.writerow([b[0].strftime('%Y-%m-%d %H:%M:%S'), *[round(x, 3) for x in b[1:5]], b[5]])


if __name__ == '__main__':
    import sys
    days_back = int(sys.argv[1]) if len(sys.argv) > 1 else 5 * 365

    END = datetime.date.today()
    START = END - datetime.timedelta(days=days_back)

    existentes = cargar_existente()
    if existentes:
        ultima_fecha = max(b[0].date() for b in existentes)
        resume_from = ultima_fecha + datetime.timedelta(days=1)
        dias_ya_hechos = (ultima_fecha - START).days + 1
        existentes = [b for b in existentes if b[0].date() < ultima_fecha]
        dias_ya_hechos -= 1
        print(f"Retomando descarga -- ya habia {len(existentes)} velas guardadas hasta {ultima_fecha}.", flush=True)
        print(f"Continua desde {resume_from} (dia {dias_ya_hechos}/{(END - START).days + 1} de la ventana completa).\n", flush=True)
    else:
        resume_from = START
        dias_ya_hechos = 0
        existentes = []
        print(f"Descargando S&P 500 CFD ({SYMBOL}) M1 (ventana 03:00-17:00 NY) — {START} -> {END}", flush=True)
        print(f"Guardando en: {OUTPUT}\n", flush=True)

    total_days = (END - START).days + 1
    bars = download_range(resume_from, END, existentes, dias_ya_hechos, total_days)
    _save(bars)

    print(f"\nListo. {len(bars)} velas M1 guardadas en {OUTPUT}", flush=True)
