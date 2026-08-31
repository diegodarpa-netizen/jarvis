"""
Descarga ampliada de XAU/USD para jarvis/trading_algoritmico (proyecto nuevo,
dataset propio -- no comparte carpeta con jarvis/trading/xau_strategy).

Alcance decidido el 13/08/2026 con Diego: 5 anios de historia, ventana
Londres+NY (03:00-17:00 hora NY) en vez de solo el solapamiento angosto
08:00-11:30 NY que se usaba antes. Se deja afuera la sesion asiatica a
proposito (ya investigado: la mas tranquila/menos relevante) -- se puede
sumar despues sin reiniciar nada, corriendo este mismo script con otra
ventana y pegando el resultado.

Mismo endpoint y logica de reintento que jarvis/trading/xau_strategy/download_dukascopy.py
(verificado 12/08/2026): ticks por hora, LZMA "alone", 20 bytes/tick.
"""
import requests, struct, lzma, datetime, os, csv, time
import pytz

OUTPUT = os.path.join(os.path.dirname(__file__), 'XAUUSD_M1_5y.csv')
SYMBOL = "XAUUSD"
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
    """Lee el CSV ya guardado (si existe) y lo devuelve como lista de tuplas
    en el mismo formato que arma download_range, para poder retomar sin
    perder lo ya bajado."""
    if not os.path.exists(OUTPUT):
        return []
    bars = []
    with open(OUTPUT, newline='') as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for row in reader:
            if len(row) < 6:
                continue
            ts = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').replace(tzinfo=UTC)
            bars.append((ts, float(row[1]), float(row[2]), float(row[3]), float(row[4]), int(row[5])))
    return bars


def download_range(start_date: datetime.date, end_date: datetime.date,
                    all_bars: list, dias_ya_hechos: int, total_days: int, delay=0.2):
    """`all_bars` viene pre-cargado con lo que ya se bajo en corridas
    anteriores (ver cargar_existente/resume). `dias_ya_hechos` y
    `total_days` son sobre la VENTANA COMPLETA de 5 anios, no sobre el
    tramo que falta, para que el progreso mostrado sea real."""
    current = start_date
    days_done = dias_ya_hechos
    days_with_data = sum(1 for _ in {b[0].date() for b in all_bars})

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
            # guardado incremental cada 10 dias procesados, por si el proceso se corta
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
        # descarta el ultimo dia cargado por si habia quedado a medio bajar,
        # se vuelve a pedir completo junto con lo que sigue
        existentes = [b for b in existentes if b[0].date() < ultima_fecha]
        dias_ya_hechos -= 1
        print(f"Retomando descarga -- ya habia {len(existentes)} velas guardadas hasta {ultima_fecha}.", flush=True)
        print(f"Continua desde {resume_from} (dia {dias_ya_hechos}/{(END - START).days + 1} de la ventana completa).\n", flush=True)
    else:
        resume_from = START
        dias_ya_hechos = 0
        existentes = []
        print(f"Descargando XAU/USD M1 (ventana 03:00-17:00 NY, Londres+NY) — {START} -> {END}", flush=True)
        print(f"Guardando en: {OUTPUT}\n", flush=True)

    total_days = (END - START).days + 1
    bars = download_range(resume_from, END, existentes, dias_ya_hechos, total_days)
    _save(bars)

    print(f"\nListo. {len(bars)} velas M1 guardadas en {OUTPUT}", flush=True)
