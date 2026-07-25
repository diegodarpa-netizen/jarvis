"""
XAU/USD Backtest Engine — Replica de Plan Técnico + Operativo
Usa datos 1m de yfinance (GC=F = Gold Futures, proxy de XAU/USD)
Ejecutar: python3 backtest.py
Resultados guardados en: results/backtest_YYYYMMDD.json
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, time as dtime
import pytz

# ─── CONFIG ──────────────────────────────────────────────────────────────────
TICKER      = "GC=F"          # Gold Futures (proxy XAU/USD)
PERIOD      = "60d"           # Máximo histórico — se descarga en chunks de 7d
INTERVAL    = "1m"
NY_TZ       = pytz.timezone("America/New_York")
SESSION_START = dtime(9, 1)
SESSION_END   = dtime(10, 59)
RR_TP         = 0.9           # Take profit ratio
MAX_SL_PIPS   = 20000         # Si SL > 20k pips → reducir al 60%
PIP           = 0.01          # 1 pip XAU/USD = $0.01

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ─── DESCARGA DE DATOS ───────────────────────────────────────────────────────
def download_data():
    """
    yfinance limita 1m a 8 días por request.
    Descargamos en chunks de 7 días para cubrir ~60 días.
    """
    from datetime import timedelta, datetime as dt
    end   = dt.now(NY_TZ)
    days  = int(PERIOD.replace("d",""))
    start = end - timedelta(days=days)

    chunks = []
    cur = start
    print(f"[↓] Descargando {TICKER} {INTERVAL} en chunks de 7d...")
    while cur < end:
        chunk_end = min(cur + timedelta(days=7), end)
        try:
            part = yf.download(TICKER, start=cur, end=chunk_end,
                               interval=INTERVAL, auto_adjust=True,
                               progress=False, multi_level_index=False)
            if not part.empty:
                chunks.append(part)
        except Exception as e:
            print(f"  [!] Error chunk {cur.date()}: {e}")
        cur = chunk_end

    if not chunks:
        raise RuntimeError("No se pudo descargar ningún dato.")

    df = pd.concat(chunks).sort_index()
    df = df[~df.index.duplicated(keep="first")]

    # Normalizar columnas (pueden ser MultiIndex o simples)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0].lower() for c in df.columns]
    else:
        df.columns = [str(c).lower() for c in df.columns]

    df.index = pd.to_datetime(df.index)
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df.index = df.index.tz_convert(NY_TZ)
    df = df.dropna(subset=["close"])

    print(f"[✓] {len(df)} velas. Rango: {df.index[0].date()} → {df.index[-1].date()}")
    return df

# ─── RESAMPLE A M3 ───────────────────────────────────────────────────────────
def resample_m3(df1):
    df3 = df1.resample("3min").agg({
        "open":  "first",
        "high":  "max",
        "low":   "min",
        "close": "last",
        "volume":"sum"
    }).dropna()
    return df3

# ─── NIVELES M3 ──────────────────────────────────────────────────────────────
def compute_m3_levels(df3):
    """
    Alto M3: vela[i-2] alcista + vela[i-1] bajista → max(high[i-2], high[i-1])
    Bajo M3: vela[i-2] bajista + vela[i-1] alcista → min(low[i-2],  low[i-1])
    """
    highs = []
    lows  = []
    for i in range(2, len(df3)):
        c2, o2 = df3["close"].iloc[i-2], df3["open"].iloc[i-2]
        c1, o1 = df3["close"].iloc[i-1], df3["open"].iloc[i-1]
        h1, h2 = df3["high"].iloc[i-1],  df3["high"].iloc[i-2]
        l1, l2 = df3["low"].iloc[i-1],   df3["low"].iloc[i-2]
        ts = df3.index[i]
        if c2 > o2 and c1 < o1:   # alcista→bajista = alto M3
            highs.append((ts, max(h1, h2)))
        if c2 < o2 and c1 > o1:   # bajista→alcista = bajo M3
            lows.append((ts, min(l1, l2)))
    highs_df = pd.DataFrame(highs, columns=["time","level"]).set_index("time")
    lows_df  = pd.DataFrame(lows,  columns=["time","level"]).set_index("time")
    return highs_df, lows_df

# ─── TENDENCIA M3 (higher highs / lower lows) ────────────────────────────────
def compute_trend(highs_df, lows_df, all_times):
    """
    Retorna Serie con tendencia (1=alcista, -1=bajista, 0=neutral) para cada timestamp M1.
    """
    trend_series = pd.Series(0, index=all_times)
    h_iter = highs_df.itertuples()
    l_iter = lows_df.itertuples()

    trend     = 0
    prev_h    = None
    prev_l    = None
    h_events  = list(highs_df.itertuples())
    l_events  = list(lows_df.itertuples())

    # Combinar eventos cronológicamente
    events = (
        [(t.Index, "H", t.level) for t in h_events] +
        [(t.Index, "L", t.level) for t in l_events]
    )
    events.sort(key=lambda x: x[0])

    choc_levels = []   # (time, level, direction)

    for ts, kind, level in events:
        if kind == "H":
            if prev_h is not None and level > prev_h:
                old_trend = trend
                trend = 1
                if old_trend == -1:
                    choc_levels.append((ts, level, 1))
            prev_h = level
        else:
            if prev_l is not None and level < prev_l:
                old_trend = trend
                trend = -1
                if old_trend == 1:
                    choc_levels.append((ts, level, -1))
            prev_l = level
        # Propagar tendencia hacia adelante
        trend_series[trend_series.index >= ts] = trend

    return trend_series, choc_levels

# ─── FUNCIONES DE VELA ENVOLVENTE ────────────────────────────────────────────
def body_ratio(h, l, o, c):
    total = h - l
    return abs(c - o) / total if total > 0 else 0

def upper_wick(h, o, c):
    total = h - l if (l := min(o,c)) else 1
    return (h - max(o, c)) / (h - total) if (h - total) > 0 else 0

def f_ur(h, l, o, c):
    total = h - l
    return (h - max(o,c)) / total if total > 0 else 0

def f_lr(h, l, o, c):
    total = h - l
    return (min(o,c) - l) / total if total > 0 else 0

def f_body(o, c): return abs(c - o)
def f_upper(h, o, c): return h - max(o, c)
def f_lower(l, o, c): return min(o, c) - l

def is_engulf_bull(h, l, o, c, prev_h):
    br = body_ratio(h, l, o, c)
    if c <= o: return False
    if c <= prev_h: return False
    # Estándar
    if br >= 0.85 and f_ur(h,l,o,c) < 0.15:
        return True
    # Martillo
    if 0.50 <= br < 0.85 and f_lower(l,o,c) > f_body(o,c):
        return True
    # Doji
    total = h - l
    if total > 0:
        sym = abs(f_lower(l,o,c) - f_upper(h,o,c)) / total <= 0.30
        if br <= 0.50 and f_lr(h,l,o,c) >= 0.15 and f_ur(h,l,o,c) >= 0.15 and sym:
            return True
    return False

def is_engulf_bear(h, l, o, c, prev_l):
    br = body_ratio(h, l, o, c)
    if c >= o: return False
    if c >= prev_l: return False
    # Estándar
    if br >= 0.85 and f_lr(h,l,o,c) < 0.15:
        return True
    # Martillo bajista
    if 0.50 <= br < 0.85 and f_upper(h,o,c) > f_body(o,c):
        return True
    # Doji
    total = h - l
    if total > 0:
        sym = abs(f_lower(l,o,c) - f_upper(h,o,c)) / total <= 0.30
        if br <= 0.50 and f_lr(h,l,o,c) >= 0.15 and f_ur(h,l,o,c) >= 0.15 and sym:
            return True
    return False

def is_indecision(h, l, o, c):
    return body_ratio(h, l, o, c) <= 0.50

# ─── BACKTEST PRINCIPAL ───────────────────────────────────────────────────────
def run_backtest(df1, trend_series, m3h_df, m3l_df):
    trades = []

    day_sl   = {}
    day_tp   = {}
    week_r   = {}

    pos_open    = False
    pos_dir     = 0       # 1=long, -1=short
    pos_entry   = 0.0
    pos_sl      = 0.0
    pos_tp      = 0.0
    pos_date    = None
    pos_type    = ""

    m3h_list = list(m3h_df.itertuples())
    m3l_list = list(m3l_df.itertuples())
    m3h_idx  = 0
    m3l_idx  = 0

    cur_m3h1 = None
    cur_m3h2 = None
    cur_m3l1 = None
    cur_m3l2 = None

    bars = df1.copy()
    bars.index.name = "ts"
    ts_arr = bars.index.to_list()

    for i in range(3, len(bars)):
        row   = bars.iloc[i]
        ts    = ts_arr[i]
        if hasattr(ts, "to_pydatetime"):
            ts = ts.to_pydatetime()
        if ts.tzinfo is None:
            ts = NY_TZ.localize(ts)

        ny_time = ts.astimezone(NY_TZ)
        t       = ny_time.time()
        date_k  = ny_time.date()
        week_k  = ny_time.isocalendar()[1]

        h, l, o, c = float(row["high"]), float(row["low"]), float(row["open"]), float(row["close"])
        ph = float(bars.iloc[i-1]["high"])
        pl = float(bars.iloc[i-1]["low"])
        po = float(bars.iloc[i-1]["open"])
        pc = float(bars.iloc[i-1]["close"])

        # Actualizar niveles M3 disponibles hasta este momento
        while m3h_idx < len(m3h_list) and m3h_list[m3h_idx].Index <= ts:
            lvl = m3h_list[m3h_idx].level
            if cur_m3h1 is not None and lvl > cur_m3h1:
                pass  # trend ya calculada externamente
            cur_m3h2 = cur_m3h1
            cur_m3h1 = lvl
            m3h_idx += 1

        while m3l_idx < len(m3l_list) and m3l_list[m3l_idx].Index <= ts:
            lvl = m3l_list[m3l_idx].level
            cur_m3l2 = cur_m3l1
            cur_m3l1 = lvl
            m3l_idx += 1

        # Límites del día y semana
        if date_k not in day_sl: day_sl[date_k] = 0
        if date_k not in day_tp: day_tp[date_k] = 0
        if week_k not in week_r:  week_r[week_k]  = 0.0

        can_trade = (day_tp[date_k] == 0 and
                     day_sl[date_k] < 2  and
                     week_r[week_k] > -2.0)

        # ── Gestión de posición abierta ─────────────────────────────────────
        if pos_open:
            if pos_dir == 1:   # LONG
                if l <= pos_sl:
                    trades.append({"dir":"BUY","entry":pos_entry,"exit":pos_sl,
                                   "result":"SL","type":pos_type,"date":str(pos_date)})
                    day_sl[date_k] = day_sl.get(date_k,0) + 1
                    week_r[week_k] = week_r.get(week_k,0.0) - 1.0
                    pos_open = False
                elif h >= pos_tp:
                    trades.append({"dir":"BUY","entry":pos_entry,"exit":pos_tp,
                                   "result":"TP","type":pos_type,"date":str(pos_date)})
                    day_tp[date_k] = day_tp.get(date_k,0) + 1
                    week_r[week_k] = week_r.get(week_k,0.0) + 0.9
                    pos_open = False
            else:              # SHORT
                if h >= pos_sl:
                    trades.append({"dir":"SELL","entry":pos_entry,"exit":pos_sl,
                                   "result":"SL","type":pos_type,"date":str(pos_date)})
                    day_sl[date_k] = day_sl.get(date_k,0) + 1
                    week_r[week_k] = week_r.get(week_k,0.0) - 1.0
                    pos_open = False
                elif l <= pos_tp:
                    trades.append({"dir":"SELL","entry":pos_entry,"exit":pos_tp,
                                   "result":"TP","type":pos_type,"date":str(pos_date)})
                    day_tp[date_k] = day_tp.get(date_k,0) + 1
                    week_r[week_k] = week_r.get(week_k,0.0) + 0.9
                    pos_open = False

        # ── Solo operar en sesión ────────────────────────────────────────────
        if not (SESSION_START <= t <= SESSION_END):
            continue
        if not can_trade or pos_open:
            continue

        # Tendencia M3 en este momento
        trend = trend_series.asof(ts) if ts in trend_series.index or True else 0
        try:
            trend = int(trend_series.asof(ts))
        except Exception:
            trend = 0

        if trend == 0:
            continue

        # ── Detección de patrones ────────────────────────────────────────────
        # Datos de barras anteriores
        ph2 = float(bars.iloc[i-2]["high"])
        pl2 = float(bars.iloc[i-2]["low"])
        po2 = float(bars.iloc[i-2]["open"])
        pc2 = float(bars.iloc[i-2]["close"])

        # Patrón ENVOLVENTE BULL: bar[1]=roja + bar[0]=engulf_bull
        pat_env_bull = (pc < po and                        # bar[1] pullback rojo
                        is_engulf_bull(h, l, o, c, ph))    # bar[0] envolvente

        # Patrón START BULL: bar[2]=rojo + bar[1]=indecisión + bar[0]=engulf_bull
        pat_strt_bull = (pc2 < po2 and                            # bar[2] pullback
                         is_indecision(ph, pl, po, pc) and        # bar[1] indecisión
                         is_engulf_bull(h, l, o, c, ph))          # bar[0] envolvente

        # Patrón ENVOLVENTE BEAR: bar[1]=verde + bar[0]=engulf_bear
        pat_env_bear = (pc > po and
                        is_engulf_bear(h, l, o, c, pl))

        # Patrón START BEAR: bar[2]=verde + bar[1]=indecisión + bar[0]=engulf_bear
        pat_strt_bear = (pc2 > po2 and
                         is_indecision(ph, pl, po, pc) and
                         is_engulf_bear(h, l, o, c, pl))

        sig_bull = trend == 1  and (pat_env_bull or pat_strt_bull)
        sig_bear = trend == -1 and (pat_env_bear or pat_strt_bear)

        # ── Abrir posición ────────────────────────────────────────────────────
        if sig_bull:
            sl_raw  = cur_m3l1 if cur_m3l1 else c - 300 * PIP
            dist    = (c - sl_raw) / PIP
            sl_price = c - dist * 0.60 * PIP if dist > MAX_SL_PIPS else sl_raw
            sl_price = min(sl_price, c - 5 * PIP)
            tp_price = c + (c - sl_price) * RR_TP
            pos_open  = True
            pos_dir   = 1
            pos_entry = c
            pos_sl    = sl_price
            pos_tp    = tp_price
            pos_date  = date_k
            pos_type  = "START" if pat_strt_bull else "ENV"

        elif sig_bear:
            sl_raw   = cur_m3h1 if cur_m3h1 else c + 300 * PIP
            dist     = (sl_raw - c) / PIP
            sl_price = c + dist * 0.60 * PIP if dist > MAX_SL_PIPS else sl_raw
            sl_price = max(sl_price, c + 5 * PIP)
            tp_price = c - (sl_price - c) * RR_TP
            pos_open  = True
            pos_dir   = -1
            pos_entry = c
            pos_sl    = sl_price
            pos_tp    = tp_price
            pos_date  = date_k
            pos_type  = "START" if pat_strt_bear else "ENV"

    return trades

# ─── MÉTRICAS ─────────────────────────────────────────────────────────────────
def compute_metrics(trades):
    if not trades:
        return {"total":0,"tp":0,"sl":0,"win_rate":0,"total_r":0,"r_per_week":0}
    total = len(trades)
    tp    = sum(1 for t in trades if t["result"] == "TP")
    sl    = total - tp
    wr    = tp / total * 100
    total_r = tp * 0.9 - sl * 1.0

    # Semanas con trades
    dates  = pd.to_datetime([t["date"] for t in trades])
    weeks  = dates.isocalendar().week.nunique() if hasattr(dates, "isocalendar") else 1
    r_pw   = total_r / weeks if weeks > 0 else 0

    by_type = {}
    for t in trades:
        k = t.get("type","?")
        if k not in by_type:
            by_type[k] = {"tp":0,"sl":0}
        if t["result"] == "TP":
            by_type[k]["tp"] += 1
        else:
            by_type[k]["sl"] += 1

    return {
        "total":     total,
        "tp":        tp,
        "sl":        sl,
        "win_rate":  round(wr, 1),
        "total_r":   round(total_r, 2),
        "r_per_week":round(r_pw, 2),
        "weeks":     int(weeks),
        "by_type":   by_type
    }

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  XAU/USD Backtest Engine — Plan Técnico v9")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    df1 = download_data()
    df3 = resample_m3(df1)

    print("[→] Calculando niveles M3 y tendencia...")
    m3h_df, m3l_df = compute_m3_levels(df3)
    trend_series, choc_events = compute_trend(m3h_df, m3l_df, df1.index)

    print(f"[✓] Altos M3: {len(m3h_df)} | Bajos M3: {len(m3l_df)} | ChOC eventos: {len(choc_events)}")

    print("[→] Ejecutando backtest...")
    trades = run_backtest(df1, trend_series, m3h_df, m3l_df)

    metrics = compute_metrics(trades)

    print()
    print("─" * 40)
    print(f"  RESULTADOS ({metrics['weeks']} semanas)")
    print("─" * 40)
    print(f"  Total trades : {metrics['total']}")
    print(f"  TP           : {metrics['tp']}")
    print(f"  SL           : {metrics['sl']}")
    print(f"  Win Rate     : {metrics['win_rate']}%")
    print(f"  Total R      : {metrics['total_r']}R")
    print(f"  R / semana   : {metrics['r_per_week']}R")
    print()
    print("  Por tipo de patrón:")
    for k, v in metrics.get("by_type", {}).items():
        total_k = v["tp"] + v["sl"]
        wr_k = round(v["tp"]/total_k*100,1) if total_k > 0 else 0
        print(f"    {k:10} → {total_k:3} trades | {wr_k}% WR")
    print("─" * 40)

    # Objetivo: 135 trades / 24 semanas = ~5.6/semana | 71% WR | 55.98R
    target_w = 135 / 24
    print()
    print("  TARGET PDF:")
    print(f"    Trades/semana : {target_w:.1f}  (actual: {metrics['total']/max(metrics['weeks'],1):.1f})")
    print(f"    Win Rate      : 71.0%  (actual: {metrics['win_rate']}%)")
    print(f"    R/semana      : 2.3R   (actual: {metrics['r_per_week']}R)")
    print()

    # Guardar resultados
    result = {
        "run_date": datetime.now().isoformat(),
        "metrics":  metrics,
        "trades":   trades
    }
    fname = os.path.join(RESULTS_DIR, f"backtest_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
    with open(fname, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"  Guardado en: {fname}")
    print("=" * 60)

    return metrics

if __name__ == "__main__":
    main()
