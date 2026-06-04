"""
XAU/USD Backtesting - Estrategia de Price Action
Sesión NY: 09:01 - 10:59
Timeframe estructura: m3 | Timeframe entrada: m1
RR: 1:0.9 | Stop diario: 2 SL | Stop semanal: -2R
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import mplfinance as mpf
from datetime import datetime, timedelta, time
import warnings
import os

warnings.filterwarnings('ignore')

CHARTS_DIR = os.path.join(os.path.dirname(__file__), 'charts')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')

# ─── PARÁMETROS ────────────────────────────────────────────────────────────────
SESSION_START_NY = time(9, 1)
SESSION_END_NY   = time(10, 59)
RR               = 0.9         # Take Profit = SL * 0.9
MAX_SL_PIPS      = 20_000      # Si SL > 20k pips se reduce a la mitad
MIN_BODY_PCT     = 0.50        # Vela con volumen: cuerpo >= 50%
BREAKOUT_MIN_PCT = 0.0001      # Quiebre válido: >= 0.01% del cuerpo
DAILY_SL_LIMIT   = 2
WEEKLY_R_LIMIT   = -2.0
RISK_PER_TRADE   = 1.0         # 1R por operación
SPREAD_PIPS      = 0.2


# ─── DESCARGA DE DATOS ─────────────────────────────────────────────────────────
def _flatten(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index)
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    return df.tz_convert('America/New_York')


def _download_chunks(ticker, interval, end, chunk_days, total_days):
    """Descarga en chunks y concatena — necesario por límites de Yahoo."""
    frames = []
    chunk_end = end
    downloaded = 0
    while downloaded < total_days:
        chunk_start = chunk_end - timedelta(days=min(chunk_days, total_days - downloaded))
        df = yf.download(ticker, start=chunk_start, end=chunk_end,
                         interval=interval, progress=False, auto_adjust=True)
        if not df.empty:
            frames.append(_flatten(df))
        chunk_end = chunk_start
        downloaded += chunk_days

    if not frames:
        return pd.DataFrame()
    result = pd.concat(frames).sort_index()
    result = result[~result.index.duplicated(keep='first')]
    return result


def download_data(months=8):
    end        = datetime.now()
    total_days = months * 31
    tickers    = ["GC=F", "XAUUSD=X"]

    print(f"Descargando XAU/USD ({months} meses)...")

    df1 = pd.DataFrame()
    df3 = pd.DataFrame()

    for ticker in tickers:
        print(f"  Intentando ticker: {ticker}")
        # m1: máximo 7 días por chunk, hasta 30 días atrás
        d1 = _download_chunks(ticker, "1m",  end, chunk_days=7,  total_days=30)
        # m5: máximo 58 días por chunk, hasta total_days atrás
        d3 = _download_chunks(ticker, "5m",  end, chunk_days=58, total_days=total_days)

        if not d1.empty and not d3.empty:
            df1, df3 = d1, d3
            print(f"  OK con {ticker}")
            break

    if df1.empty or df3.empty:
        # Fallback: usar solo m5 para ambos timeframes con más historia
        print("  Usando m5 para ambos timeframes...")
        for ticker in tickers:
            d3 = _download_chunks(ticker, "5m", end, chunk_days=58, total_days=total_days)
            if not d3.empty:
                df1, df3 = d3, d3
                print(f"  Fallback OK con {ticker}")
                break

    if df1.empty:
        raise ValueError("No se pudieron descargar datos de Yahoo Finance.")

    print(f"m1: {len(df1)} velas | m5: {len(df3)} velas")
    print(f"Rango m5: {df3.index[0].date()} → {df3.index[-1].date()}")
    return df1, df3


# ─── LÓGICA DE VELAS ──────────────────────────────────────────────────────────
def is_bullish(candle):
    return candle['Close'] > candle['Open']

def is_bearish(candle):
    return candle['Close'] < candle['Open']

def body_pct(candle):
    total = candle['High'] - candle['Low']
    if total == 0:
        return 0
    return abs(candle['Close'] - candle['Open']) / total

def has_volume(candle):
    return body_pct(candle) >= MIN_BODY_PCT

def is_engulfing(entry_candle, prev_candle, direction='long'):
    """Vela envolvente: cuerpo >= 50% y supera el cuerpo de la vela anterior"""
    if not has_volume(entry_candle):
        return False
    if direction == 'long':
        return (entry_candle['Close'] > prev_candle['High'] and
                is_bullish(entry_candle))
    else:
        return (entry_candle['Close'] < prev_candle['Low'] and
                is_bearish(entry_candle))


# ─── DETECCIÓN DE ALTOS Y BAJOS m3 ─────────────────────────────────────────────
def find_m3_levels(df3, session_start, session_end):
    """
    Alto m3: vela alcista seguida de bajista → nivel = High de la alcista
    Bajo m3: vela bajista seguida de alcista → nivel = Low de la bajista
    """
    levels = []
    session_df = df3.between_time(session_start.strftime('%H:%M'),
                                   session_end.strftime('%H:%M'))

    for i in range(len(session_df) - 1):
        curr = session_df.iloc[i]
        nxt  = session_df.iloc[i + 1]

        if is_bullish(curr) and is_bearish(nxt):
            levels.append({
                'time': session_df.index[i],
                'type': 'high',
                'level': float(curr['High']),
                'line': 'dotted'
            })

        elif is_bearish(curr) and is_bullish(nxt):
            levels.append({
                'time': session_df.index[i],
                'type': 'low',
                'level': float(curr['Low']),
                'line': 'dotted'
            })

    # Clasificar: si alterna high/low → reversión (línea continua); si repite → continuación (punteada)
    for i in range(1, len(levels)):
        if levels[i]['type'] != levels[i-1]['type']:
            levels[i]['line'] = 'solid'

    return levels


# ─── BACKTEST PRINCIPAL ───────────────────────────────────────────────────────
def run_backtest(df1, df3):
    trades    = []
    daily_sl  = {}
    weekly_r  = {}

    trading_days = df1.index.normalize().unique()

    for day in trading_days:
        day_date = day.date()
        week_key = day_date.isocalendar()[:2]

        # Inicializar contadores
        if day_date not in daily_sl:
            daily_sl[day_date] = 0
        if week_key not in weekly_r:
            weekly_r[week_key] = 0.0

        # Skip weekends
        if day_date.weekday() >= 5:
            continue

        # Stop diario/semanal
        if daily_sl[day_date] >= DAILY_SL_LIMIT:
            continue
        if weekly_r[week_key] <= WEEKLY_R_LIMIT:
            continue

        # Datos del día en sesión NY
        day_m1 = df1[df1.index.date == day_date]
        day_m3 = df3[df3.index.date == day_date]

        session_m1 = day_m1.between_time('09:01', '10:59')
        session_m3 = day_m3.between_time('09:00', '10:59')

        if len(session_m1) < 5 or len(session_m3) < 3:
            continue

        # Encontrar niveles m3 del día
        levels = find_m3_levels(session_m3, SESSION_START_NY, SESSION_END_NY)
        if not levels:
            continue

        in_trade = False
        trade_count_day = 0

        for i in range(2, len(session_m1)):
            if daily_sl[day_date] >= DAILY_SL_LIMIT:
                break
            if weekly_r[week_key] <= WEEKLY_R_LIMIT:
                break
            if in_trade:
                continue

            curr = session_m1.iloc[i]
            prev = session_m1.iloc[i - 1]
            curr_time = session_m1.index[i]

            # Obtener último nivel m3 antes de la vela actual
            prior_levels = [l for l in levels if l['time'] <= curr_time]
            if not prior_levels:
                continue

            last_level = prior_levels[-1]
            level_price = last_level['level']
            level_type  = last_level['type']

            # ── MEC LARGO: precio rompió un alto m3 con pullback y continuación ──
            if (level_type == 'high' and
                is_bullish(curr) and
                has_volume(curr) and
                float(curr['Close']) > level_price * (1 + BREAKOUT_MIN_PCT) and
                is_engulfing(curr, prev, 'long')):

                entry = float(curr['Close']) + SPREAD_PIPS
                sl_raw = level_price - float(curr['Low'])
                sl = min(sl_raw, MAX_SL_PIPS / 10000)
                if sl <= 0:
                    continue
                tp = entry + sl * RR

                result = simulate_trade(session_m1, i + 1, entry, sl, tp, 'long', entry)

                r_value = RISK_PER_TRADE if result == 'win' else -RISK_PER_TRADE
                trades.append({
                    'date': day_date,
                    'time': curr_time,
                    'direction': 'LONG',
                    'model': 'MEC',
                    'entry': entry,
                    'sl': entry - sl,
                    'tp': tp,
                    'sl_pips': sl * 10000,
                    'result': result,
                    'r': r_value
                })

                if result == 'loss':
                    daily_sl[day_date] = daily_sl.get(day_date, 0) + 1
                weekly_r[week_key] = weekly_r.get(week_key, 0) + r_value
                in_trade = True
                trade_count_day += 1

            # ── MEC CORTO: precio rompió un bajo m3 con pullback y continuación ──
            elif (level_type == 'low' and
                  is_bearish(curr) and
                  has_volume(curr) and
                  float(curr['Close']) < level_price * (1 - BREAKOUT_MIN_PCT) and
                  is_engulfing(curr, prev, 'short')):

                entry = float(curr['Close']) - SPREAD_PIPS
                sl_raw = float(curr['High']) - level_price
                sl = min(sl_raw, MAX_SL_PIPS / 10000)
                if sl <= 0:
                    continue
                tp = entry - sl * RR

                result = simulate_trade(session_m1, i + 1, entry, sl, tp, 'short', entry)

                r_value = RISK_PER_TRADE if result == 'win' else -RISK_PER_TRADE
                trades.append({
                    'date': day_date,
                    'time': curr_time,
                    'direction': 'SHORT',
                    'model': 'MEC',
                    'entry': entry,
                    'sl': entry + sl,
                    'tp': tp,
                    'sl_pips': sl * 10000,
                    'result': result,
                    'r': r_value
                })

                if result == 'loss':
                    daily_sl[day_date] = daily_sl.get(day_date, 0) + 1
                weekly_r[week_key] = weekly_r.get(week_key, 0) + r_value
                in_trade = True
                trade_count_day += 1

    return pd.DataFrame(trades)


def simulate_trade(df, start_idx, entry, sl_dist, tp_price, direction, ref_price):
    """Simula si el trade llega a TP o SL primero."""
    for j in range(start_idx, min(start_idx + 60, len(df))):
        candle = df.iloc[j]
        high = float(candle['High'])
        low  = float(candle['Low'])

        if direction == 'long':
            if low <= entry - sl_dist:
                return 'loss'
            if high >= tp_price:
                return 'win'
        else:
            if high >= entry + sl_dist:
                return 'loss'
            if low <= tp_price:
                return 'win'

    return 'timeout'


# ─── MÉTRICAS ──────────────────────────────────────────────────────────────────
def calculate_metrics(df):
    if df.empty:
        return {}

    df = df[df['result'].isin(['win', 'loss'])].copy()
    if df.empty:
        return {}

    df['cumulative_r'] = df['r'].cumsum()

    wins   = len(df[df['result'] == 'win'])
    losses = len(df[df['result'] == 'loss'])
    total  = wins + losses

    win_rate = wins / total * 100 if total > 0 else 0
    total_r  = df['r'].sum()
    max_dd   = (df['cumulative_r'].cummax() - df['cumulative_r']).max()
    profit_factor = (wins * RR) / losses if losses > 0 else float('inf')

    return {
        'total_trades': total,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'total_r': total_r,
        'max_drawdown_r': max_dd,
        'profit_factor': profit_factor,
        'avg_r_per_trade': total_r / total if total > 0 else 0,
        'df': df
    }


# ─── GRÁFICOS ─────────────────────────────────────────────────────────────────
def plot_equity_curve(metrics, save_path):
    df = metrics['df']
    fig, axes = plt.subplots(3, 1, figsize=(14, 12),
                              gridspec_kw={'height_ratios': [3, 1.5, 1.5]})
    fig.patch.set_facecolor('#0d1117')

    for ax in axes:
        ax.set_facecolor('#0d1117')
        ax.tick_params(colors='#8b949e')
        ax.spines['bottom'].set_color('#30363d')
        ax.spines['left'].set_color('#30363d')
        ax.spines['top'].set_color('#30363d')
        ax.spines['right'].set_color('#30363d')

    # ── Panel 1: Curva de equity ──
    ax = axes[0]
    x = range(len(df))
    cum_r = df['cumulative_r'].values

    ax.plot(x, cum_r, color='#58a6ff', linewidth=2, zorder=3)
    ax.fill_between(x, cum_r, alpha=0.15, color='#58a6ff')

    # Colorear debajo según positivo/negativo
    ax.fill_between(x, cum_r, 0,
                    where=np.array(cum_r) >= 0,
                    alpha=0.2, color='#3fb950', label='Ganancia')
    ax.fill_between(x, cum_r, 0,
                    where=np.array(cum_r) < 0,
                    alpha=0.2, color='#f85149', label='Pérdida')

    ax.axhline(0, color='#8b949e', linewidth=0.8, linestyle='--')
    ax.set_title('Curva de Equity — XAU/USD Strategy (8 meses)',
                  color='white', fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel('R acumulado', color='#8b949e')
    ax.legend(facecolor='#161b22', edgecolor='#30363d',
               labelcolor='white', fontsize=10)
    ax.grid(True, color='#21262d', linewidth=0.5)

    # Anotar resultado final
    final_r = cum_r[-1]
    ax.annotate(f'Total: {final_r:+.1f}R',
                xy=(len(df)-1, final_r),
                xytext=(-80, 15), textcoords='offset points',
                color='#3fb950' if final_r >= 0 else '#f85149',
                fontsize=11, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#8b949e'))

    # ── Panel 2: Win/Loss por trade ──
    ax2 = axes[1]
    colors = ['#3fb950' if r > 0 else '#f85149' for r in df['r'].values]
    ax2.bar(x, df['r'].values, color=colors, alpha=0.85, width=0.7)
    ax2.axhline(0, color='#8b949e', linewidth=0.8, linestyle='--')
    ax2.set_title('Resultado por Trade (R)', color='white', fontsize=11, pad=8)
    ax2.set_ylabel('R', color='#8b949e')
    ax2.grid(True, color='#21262d', linewidth=0.5, axis='y')

    # ── Panel 3: Distribución por mes ──
    ax3 = axes[2]
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
    monthly = df.groupby('month')['r'].sum()
    bar_colors = ['#3fb950' if v >= 0 else '#f85149' for v in monthly.values]
    bars = ax3.bar(range(len(monthly)), monthly.values, color=bar_colors, alpha=0.85)
    ax3.set_xticks(range(len(monthly)))
    ax3.set_xticklabels(monthly.index, rotation=30, ha='right', color='#8b949e', fontsize=9)
    ax3.axhline(0, color='#8b949e', linewidth=0.8, linestyle='--')
    ax3.set_title('Rentabilidad Mensual (R)', color='white', fontsize=11, pad=8)
    ax3.set_ylabel('R', color='#8b949e')
    ax3.grid(True, color='#21262d', linewidth=0.5, axis='y')

    plt.tight_layout(pad=2.5)
    plt.savefig(save_path, dpi=150, bbox_inches='tight',
                facecolor='#0d1117', edgecolor='none')
    plt.close()
    print(f"Guardado: {save_path}")


def plot_stats_dashboard(metrics, save_path):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.patch.set_facecolor('#0d1117')
    fig.suptitle('Dashboard — XAU/USD Backtest (8 meses)',
                  color='white', fontsize=16, fontweight='bold', y=0.98)

    df = metrics['df']

    for ax in axes.flat:
        ax.set_facecolor('#161b22')
        ax.tick_params(colors='#8b949e')
        for spine in ax.spines.values():
            spine.set_color('#30363d')

    # ── Win Rate Pie ──
    ax = axes[0, 0]
    wins   = metrics['wins']
    losses = metrics['losses']
    wedges, texts, autotexts = ax.pie(
        [wins, losses],
        labels=['Wins', 'Losses'],
        colors=['#3fb950', '#f85149'],
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'edgecolor': '#0d1117', 'linewidth': 2}
    )
    for t in texts + autotexts:
        t.set_color('white')
        t.set_fontsize(12)
    ax.set_title('Win Rate', color='white', fontsize=13, fontweight='bold')

    # ── Distribución de resultados ──
    ax2 = axes[0, 1]
    win_df  = df[df['result'] == 'win']['r']
    loss_df = df[df['result'] == 'loss']['r']
    ax2.hist(win_df,  bins=10, color='#3fb950', alpha=0.75, label='Win')
    ax2.hist(loss_df, bins=10, color='#f85149', alpha=0.75, label='Loss')
    ax2.set_title('Distribución de R', color='white', fontsize=13, fontweight='bold')
    ax2.set_xlabel('R', color='#8b949e')
    ax2.set_ylabel('Frecuencia', color='#8b949e')
    ax2.legend(facecolor='#0d1117', edgecolor='#30363d', labelcolor='white')
    ax2.grid(True, color='#21262d', linewidth=0.5)

    # ── Trades por día de la semana ──
    ax3 = axes[1, 0]
    df['weekday'] = pd.to_datetime(df['date']).dt.day_name()
    order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    wd_stats = df.groupby('weekday')['r'].sum().reindex(order, fill_value=0)
    bar_colors = ['#3fb950' if v >= 0 else '#f85149' for v in wd_stats.values]
    ax3.bar(range(len(wd_stats)), wd_stats.values, color=bar_colors, alpha=0.85)
    ax3.set_xticks(range(len(wd_stats)))
    ax3.set_xticklabels(['Lun', 'Mar', 'Mié', 'Jue', 'Vie'],
                         color='#8b949e', fontsize=10)
    ax3.axhline(0, color='#8b949e', linewidth=0.8, linestyle='--')
    ax3.set_title('Rentabilidad por Día', color='white', fontsize=13, fontweight='bold')
    ax3.set_ylabel('R', color='#8b949e')
    ax3.grid(True, color='#21262d', linewidth=0.5, axis='y')

    # ── KPIs ──
    ax4 = axes[1, 1]
    ax4.axis('off')
    kpis = [
        ('Total Trades',        f"{metrics['total_trades']}"),
        ('Win Rate',            f"{metrics['win_rate']:.1f}%"),
        ('Total R',             f"{metrics['total_r']:+.2f}R"),
        ('Profit Factor',       f"{metrics['profit_factor']:.2f}"),
        ('Max Drawdown',        f"{metrics['max_drawdown_r']:.2f}R"),
        ('Avg R / Trade',       f"{metrics['avg_r_per_trade']:+.3f}R"),
        ('RR Objetivo',         '1 : 0.9'),
        ('Stop Diario',         '2 SL'),
        ('Stop Semanal',        '-2R'),
    ]
    y_pos = 0.92
    for label, value in kpis:
        color = '#3fb950' if ('+' in value and value != '+0.000R') else '#f85149' if '-' in value else '#58a6ff'
        ax4.text(0.05, y_pos, f"{label}:", color='#8b949e', fontsize=11,
                  transform=ax4.transAxes, va='top')
        ax4.text(0.60, y_pos, value, color=color, fontsize=11,
                  fontweight='bold', transform=ax4.transAxes, va='top')
        y_pos -= 0.10

    plt.tight_layout(pad=2.0)
    plt.savefig(save_path, dpi=150, bbox_inches='tight',
                facecolor='#0d1117', edgecolor='none')
    plt.close()
    print(f"Guardado: {save_path}")


def plot_sample_trades(df1, trades_df, save_path, n_samples=6):
    """Muestra n ejemplos de trades con velas m1."""
    if trades_df.empty:
        return

    sample = trades_df[trades_df['result'].isin(['win', 'loss'])].head(n_samples)
    if sample.empty:
        return

    n = len(sample)
    cols = 2
    rows = (n + 1) // 2
    fig, axes = plt.subplots(rows, cols, figsize=(16, rows * 4))
    fig.patch.set_facecolor('#0d1117')
    fig.suptitle('Ejemplos de Trades — XAU/USD (m1)',
                  color='white', fontsize=14, fontweight='bold')

    axes = axes.flatten() if n > 1 else [axes]

    for idx, (_, trade) in enumerate(sample.iterrows()):
        ax = axes[idx]
        ax.set_facecolor('#161b22')
        for spine in ax.spines.values():
            spine.set_color('#30363d')
        ax.tick_params(colors='#8b949e', labelsize=8)

        t_time = pd.Timestamp(trade['time'])
        window_start = t_time - timedelta(minutes=15)
        window_end   = t_time + timedelta(minutes=30)

        window = df1[(df1.index >= window_start) & (df1.index <= window_end)].copy()
        if len(window) < 3:
            ax.text(0.5, 0.5, 'Sin datos', color='white', ha='center',
                     transform=ax.transAxes)
            continue

        x = range(len(window))
        for xi, (ts, row) in enumerate(window.iterrows()):
            o, c, h, l = float(row['Open']), float(row['Close']), float(row['High']), float(row['Low'])
            color = '#3fb950' if c >= o else '#f85149'
            ax.plot([xi, xi], [l, h], color=color, linewidth=1)
            ax.add_patch(plt.Rectangle(
                (xi - 0.3, min(o, c)), 0.6, abs(c - o),
                facecolor=color, edgecolor=color, linewidth=0.5
            ))

        # Líneas de entrada, SL, TP
        ax.axhline(trade['entry'], color='#f0e68c', linewidth=1.2,
                    linestyle='--', label=f"Entry {trade['entry']:.1f}")
        ax.axhline(trade['sl'],    color='#f85149', linewidth=1.2,
                    linestyle=':',  label=f"SL {trade['sl']:.1f}")
        ax.axhline(trade['tp'],    color='#3fb950', linewidth=1.2,
                    linestyle=':',  label=f"TP {trade['tp']:.1f}")

        result_color = '#3fb950' if trade['result'] == 'win' else '#f85149'
        title = (f"{trade['date']} | {trade['direction']} | {trade['model']} | "
                  f"{'WIN' if trade['result']=='win' else 'LOSS'}")
        ax.set_title(title, color=result_color, fontsize=9, fontweight='bold')
        ax.legend(fontsize=7, facecolor='#0d1117', edgecolor='#30363d',
                   labelcolor='white', loc='upper left')
        ax.grid(True, color='#21262d', linewidth=0.4)

    # Ocultar ejes vacíos
    for idx in range(n, len(axes)):
        axes[idx].set_visible(False)

    plt.tight_layout(pad=1.5)
    plt.savefig(save_path, dpi=150, bbox_inches='tight',
                facecolor='#0d1117', edgecolor='none')
    plt.close()
    print(f"Guardado: {save_path}")


# ─── REPORTE ──────────────────────────────────────────────────────────────────
def print_report(metrics):
    print("\n" + "="*55)
    print("    BACKTEST XAU/USD — REPORTE FINAL")
    print("="*55)
    print(f"  Total trades:       {metrics['total_trades']}")
    print(f"  Wins / Losses:      {metrics['wins']} / {metrics['losses']}")
    print(f"  Win Rate:           {metrics['win_rate']:.1f}%")
    print(f"  Total R:            {metrics['total_r']:+.2f}R")
    print(f"  Profit Factor:      {metrics['profit_factor']:.2f}")
    print(f"  Max Drawdown:       {metrics['max_drawdown_r']:.2f}R")
    print(f"  Avg R / Trade:      {metrics['avg_r_per_trade']:+.3f}R")
    print("="*55)


def save_csv(trades_df, path):
    trades_df.to_csv(path, index=False)
    print(f"CSV guardado: {path}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=== BACKTEST XAU/USD — Estrategia Price Action ===\n")

    df1, df3 = download_data(months=8)

    print("\nEjecutando backtest...")
    trades_df = run_backtest(df1, df3)

    if trades_df.empty:
        print("No se encontraron trades en el período.")
    else:
        metrics = calculate_metrics(trades_df)
        print_report(metrics)

        equity_path  = os.path.join(CHARTS_DIR, 'equity_curve.png')
        dash_path    = os.path.join(CHARTS_DIR, 'dashboard.png')
        trades_path  = os.path.join(CHARTS_DIR, 'sample_trades.png')
        csv_path     = os.path.join(REPORTS_DIR, 'trades_log.csv')

        print("\nGenerando gráficos...")
        plot_equity_curve(metrics, equity_path)
        plot_stats_dashboard(metrics, dash_path)
        plot_sample_trades(df1, metrics['df'], trades_path)
        save_csv(metrics['df'], csv_path)

        print(f"\nCharts guardados en: {CHARTS_DIR}")
        print(f"CSV guardado en:     {csv_path}")
