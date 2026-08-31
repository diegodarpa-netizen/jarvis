"""
Compara la ventana de sesión operativa (09:01-10:59 NY, la que usa el Plan
Técnico/Operativo) contra EL RESTO DEL DÍA, con la misma lógica exacta
(M3, ENV/START, SL desde nivel M3, TP=0.9R) — para responder si restringir
a esa franja horaria es necesario o si se están perdiendo oportunidades
fuera de ella.

Reutiliza las funciones de backtest.py tal cual están (no se reimplementa
nada de la lógica) — solo se parametriza la ventana horaria.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import time as dtime
import pandas as pd

from backtest import (
    download_data, resample_m3, compute_m3_levels, compute_trend,
    is_engulf_bull, is_engulf_bear, is_indecision,
    compute_metrics, PIP, MAX_SL_PIPS, RR_TP, NY_TZ,
)


def run_backtest_windowed(df1, trend_series, m3h_df, m3l_df, in_window_fn):
    """Copia de run_backtest() de backtest.py, parametrizada por una función
    in_window_fn(time) -> bool en vez de la ventana fija 09:01-10:59."""
    trades = []
    day_sl, day_tp, week_r = {}, {}, {}
    pos_open = False
    pos_dir = 0
    pos_entry = pos_sl = pos_tp = 0.0
    pos_date = None
    pos_type = ""

    m3h_list = list(m3h_df.itertuples())
    m3l_list = list(m3l_df.itertuples())
    m3h_idx = m3l_idx = 0
    cur_m3h1 = cur_m3h2 = cur_m3l1 = cur_m3l2 = None

    bars = df1.copy()
    ts_arr = bars.index.to_list()

    for i in range(3, len(bars)):
        row = bars.iloc[i]
        ts = ts_arr[i]
        if hasattr(ts, "to_pydatetime"):
            ts = ts.to_pydatetime()
        if ts.tzinfo is None:
            ts = NY_TZ.localize(ts)
        ny_time = ts.astimezone(NY_TZ)
        t = ny_time.time()
        date_k = ny_time.date()
        week_k = ny_time.isocalendar()[1]

        h, l, o, c = float(row["high"]), float(row["low"]), float(row["open"]), float(row["close"])
        ph = float(bars.iloc[i - 1]["high"])
        pl = float(bars.iloc[i - 1]["low"])
        po = float(bars.iloc[i - 1]["open"])
        pc = float(bars.iloc[i - 1]["close"])

        while m3h_idx < len(m3h_list) and m3h_list[m3h_idx].Index <= ts:
            cur_m3h2 = cur_m3h1
            cur_m3h1 = m3h_list[m3h_idx].level
            m3h_idx += 1
        while m3l_idx < len(m3l_list) and m3l_list[m3l_idx].Index <= ts:
            cur_m3l2 = cur_m3l1
            cur_m3l1 = m3l_list[m3l_idx].level
            m3l_idx += 1

        if date_k not in day_sl: day_sl[date_k] = 0
        if date_k not in day_tp: day_tp[date_k] = 0
        if week_k not in week_r: week_r[week_k] = 0.0

        can_trade = (day_tp[date_k] == 0 and day_sl[date_k] < 2 and week_r[week_k] > -2.0)

        if pos_open:
            if pos_dir == 1:
                if l <= pos_sl:
                    trades.append({"dir": "BUY", "result": "SL", "type": pos_type, "date": str(pos_date), "time": str(t)})
                    day_sl[date_k] += 1
                    week_r[week_k] -= 1.0
                    pos_open = False
                elif h >= pos_tp:
                    trades.append({"dir": "BUY", "result": "TP", "type": pos_type, "date": str(pos_date), "time": str(t)})
                    day_tp[date_k] += 1
                    week_r[week_k] += 0.9
                    pos_open = False
            else:
                if h >= pos_sl:
                    trades.append({"dir": "SELL", "result": "SL", "type": pos_type, "date": str(pos_date), "time": str(t)})
                    day_sl[date_k] += 1
                    week_r[week_k] -= 1.0
                    pos_open = False
                elif l <= pos_tp:
                    trades.append({"dir": "SELL", "result": "TP", "type": pos_type, "date": str(pos_date), "time": str(t)})
                    day_tp[date_k] += 1
                    week_r[week_k] += 0.9
                    pos_open = False

        if not in_window_fn(t):
            continue
        if not can_trade or pos_open:
            continue

        try:
            trend = int(trend_series.asof(ts))
        except Exception:
            trend = 0
        if trend == 0:
            continue

        ph2 = float(bars.iloc[i - 2]["high"])
        pl2 = float(bars.iloc[i - 2]["low"])
        po2 = float(bars.iloc[i - 2]["open"])
        pc2 = float(bars.iloc[i - 2]["close"])

        pat_env_bull = (pc < po and is_engulf_bull(h, l, o, c, ph))
        pat_strt_bull = (pc2 < po2 and is_indecision(ph, pl, po, pc) and is_engulf_bull(h, l, o, c, ph))
        pat_env_bear = (pc > po and is_engulf_bear(h, l, o, c, pl))
        pat_strt_bear = (pc2 > po2 and is_indecision(ph, pl, po, pc) and is_engulf_bear(h, l, o, c, pl))

        sig_bull = trend == 1 and (pat_env_bull or pat_strt_bull)
        sig_bear = trend == -1 and (pat_env_bear or pat_strt_bear)

        if sig_bull:
            sl_raw = cur_m3l1 if cur_m3l1 else c - 300 * PIP
            dist = (c - sl_raw) / PIP
            sl_price = c - dist * 0.60 * PIP if dist > MAX_SL_PIPS else sl_raw
            sl_price = min(sl_price, c - 5 * PIP)
            tp_price = c + (c - sl_price) * RR_TP
            pos_open, pos_dir, pos_entry, pos_sl, pos_tp, pos_date = True, 1, c, sl_price, tp_price, date_k
            pos_type = "START" if pat_strt_bull else "ENV"
        elif sig_bear:
            sl_raw = cur_m3h1 if cur_m3h1 else c + 300 * PIP
            dist = (sl_raw - c) / PIP
            sl_price = c + dist * 0.60 * PIP if dist > MAX_SL_PIPS else sl_raw
            sl_price = max(sl_price, c + 5 * PIP)
            tp_price = c - (sl_price - c) * RR_TP
            pos_open, pos_dir, pos_entry, pos_sl, pos_tp, pos_date = True, -1, c, sl_price, tp_price, date_k
            pos_type = "START" if pat_strt_bear else "ENV"

    return trades


def main():
    df1 = download_data()
    df3 = resample_m3(df1)
    m3h_df, m3l_df = compute_m3_levels(df3)
    trend_series, _ = compute_trend(m3h_df, m3l_df, df1.index)

    SESSION_START, SESSION_END = dtime(9, 1), dtime(10, 59)

    windows = {
        "Sesion actual (09:01-10:59 NY)": lambda t: SESSION_START <= t <= SESSION_END,
        "Resto del dia (todo menos 09:01-10:59)": lambda t: not (SESSION_START <= t <= SESSION_END),
        "Apertura Londres (03:00-05:00 NY)": lambda t: dtime(3, 0) <= t <= dtime(5, 0),
        "Tarde NY (13:00-15:00 NY)": lambda t: dtime(13, 0) <= t <= dtime(15, 0),
    }

    print("\n" + "=" * 60)
    print("  SESION vs. RESTO DEL DIA — misma logica, misma data")
    print("=" * 60)

    results = {}
    for name, fn in windows.items():
        trades = run_backtest_windowed(df1, trend_series, m3h_df, m3l_df, fn)
        metrics = compute_metrics(trades)
        results[name] = metrics
        print(f"\n{name}:")
        print(f"  Trades: {metrics['total']} | WR: {metrics['win_rate']}% | Total R: {metrics['total_r']} | R/semana: {metrics['r_per_week']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
