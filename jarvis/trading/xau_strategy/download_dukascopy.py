"""
Descarga ticks de XAU/USD de Dukascopy y arma velas M1 para un rango de
fechas completo. Reemplaza la versión anterior (URL/endpoint rotos —
apuntaba a un endpoint de velas que Dukascopy ya no sirve).

Endpoint real (verificado 12/08/2026): datos de TICK por hora, formato
LZMA "alone" (no gzip), 20 bytes por tick (ms offset, ask, bid, ask_vol,
bid_vol, todo big-endian). Se arman velas M1 agregando ticks.

Como la estructura M3 de la estrategia resetea todo al inicio de cada
sesión NY (09:01) — ver jarvis/trading/rules/estructura_m3.md — solo
hace falta la ventana 08:00-11:30 NY de cada día, no el día completo.
Reduce la descarga de ~24h/día a ~3.5h/día.
"""
import requests, struct, lzma, datetime, os, csv, time
import pytz

OUTPUT = os.path.join(os.path.dirname(__file__), 'data', 'XAUUSD_M1.csv')
SYMBOL = "XAUUSD"
NY_TZ = pytz.timezone("America/New_York")
UTC = pytz.UTC

# Ventana a descargar por día (hora NY) -> se convierte a UTC internamente
WINDOW_START_NY = datetime.time(8, 0)
WINDOW_END_NY = datetime.time(11, 30)

HEADERS = {'User-Agent': 'Mozilla/5.0'}


def fetch_hour_ticks(dt_utc_hour: datetime.datetime, retries: int = 4) -> list:
    """Descarga los ticks de UNA hora UTC dada. Devuelve lista de
    (datetime_utc, ask, bid). El servidor de Dukascopy es inestable
    (timeouts/503 intermitentes aunque el dato exista) — reintenta con
    backoff antes de dar por perdida la hora."""
    y, m, d, h = dt_utc_hour.year, dt_utc_hour.month, dt_utc_hour.day, dt_utc_hour.hour
    url = f"https://datafeed.dukascopy.com/datafeed/{SYMBOL}/{y}/{m-1:02d}/{d:02d}/{h:02d}h_ticks.bi5"

    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            if r.status_code == 200 and len(r.content) > 0:
                decompressed = lzma.decompress(r.content, format=lzma.FORMAT_ALONE)
                break
            elif r.status_code == 404:
                return []  # hora sin mercado (fin de semana feriado, etc.) — no reintentar
        except Exception:
            pass
        time.sleep(1.5 * (attempt + 1))
    else:
        return []  # se agotaron los reintentos

    base = dt_utc_hour.replace(minute=0, second=0, microsecond=0)
    ticks = []
    n = len(decompressed) // 20
    for i in range(n):
        off = i * 20
        try:
            ms, ask, bid, _ask_vol, _bid_vol = struct.unpack('>3I2f', decompressed[off:off + 20])
            price_ask = ask / 1000.0
            price_bid = bid / 1000.0
            if not (100 < price_bid < 20000):  # sanity check
                continue
            ts = base + datetime.timedelta(milliseconds=ms)
            ticks.append((ts, price_ask, price_bid))
        except Exception:
            continue
    return ticks


def ticks_to_m1(ticks: list) -> list:
    """Agrega ticks (mid price) a velas M1. Devuelve lista de
    (datetime_utc_minuto, open, high, low, close, n_ticks)."""
    if not ticks:
        return []
    buckets = {}
    for ts, ask, bid in ticks:
        mid = (ask + bid) / 2.0
        minute_key = ts.replace(second=0, microsecond=0)
        if minute_key not in buckets:
            buckets[minute_key] = []
        buckets[minute_key].append(mid)

    bars = []
    for minute, prices in sorted(buckets.items()):
        bars.append((minute, prices[0], max(prices), min(prices), prices[-1], len(prices)))
    return bars


def hours_for_day_ny(date_ny: datetime.date):
    """Genera las horas UTC a descargar para cubrir 08:00-11:30 NY de ese día."""
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


def download_range(start_date: datetime.date, end_date: datetime.date, delay=0.25):
    all_bars = []
    current = start_date
    days_done = 0
    days_with_data = 0
    total_days = (end_date - start_date).days + 1

    while current <= end_date:
        if current.weekday() < 5:  # solo dias habiles
            day_ticks = []
            for hour_utc in hours_for_day_ny(current):
                day_ticks.extend(fetch_hour_ticks(hour_utc))
                time.sleep(delay)
            day_bars = ticks_to_m1(day_ticks)
            if day_bars:
                all_bars.extend(day_bars)
                days_with_data += 1
                if days_done % 10 == 0:
                    print(f"  {current} — {len(day_bars)} velas M1 ({len(day_ticks)} ticks) OK")
            else:
                print(f"  {current} — sin datos")
        days_done += 1
        if days_done % 20 == 0:
            print(f"  Progreso: {days_done}/{total_days} dias ({days_with_data} con datos)")
        current += datetime.timedelta(days=1)

    return all_bars


if __name__ == '__main__':
    import sys
    days_back = int(sys.argv[1]) if len(sys.argv) > 1 else 180
    END = datetime.date.today()
    START = END - datetime.timedelta(days=days_back)

    print(f"Descargando XAU/USD M1 (ventana 08:00-11:30 NY) — {START} -> {END}")
    print(f"Guardando en: {OUTPUT}\n")

    bars = download_range(START, END)
    bars.sort(key=lambda x: x[0])

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['time', 'open', 'high', 'low', 'close', 'n_ticks'])
        for b in bars:
            w.writerow([b[0].strftime('%Y-%m-%d %H:%M:%S'), *[round(x, 3) for x in b[1:5]], b[5]])

    print(f"\nListo. {len(bars)} velas M1 guardadas en {OUTPUT}")
