"""
Jarvis - Generador de Reportes Dinámicos
Reportes HTML profesionales, interactivos y en español.
Se adapta a lo que Diego necesita — no es una plantilla fija.

Tipos:
  portfolio      Cartera con gráficos de asignación y P&L
  market         Briefing del mercado con índices, sectores y macro
  company        Análisis de empresa con candlestick y fundamentals
  opportunities  Ranking de oportunidades con scoring visual

Uso:
  python report_builder.py --type portfolio
  python report_builder.py --type market
  python report_builder.py --type company --ticker NVDA --period 1y
  python report_builder.py --type opportunities --list tech --top 10
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio
    from plotly.offline import get_plotlyjs
except ImportError:
    print("ERROR: plotly no instalado. Ejecutá: pip install plotly", file=sys.stderr)
    sys.exit(1)

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance no instalado. Ejecutá: pip install yfinance", file=sys.stderr)
    sys.exit(1)

REPORTS_DIR = Path(__file__).parent.parent / "reports"
SCRIPTS_DIR = Path(__file__).parent
REPORTS_DIR.mkdir(exist_ok=True)

T = {
    "bg":       "#0d1117",
    "paper":    "#161b22",
    "border":   "#21262d",
    "text":     "#e6edf3",
    "muted":    "#8b949e",
    "up":       "#3fb950",
    "down":     "#f85149",
    "blue":     "#58a6ff",
    "purple":   "#d2a8ff",
    "orange":   "#ffa657",
    "font":     "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
}

PLOTLY_CONFIG = dict(
    plot_bgcolor=T["bg"],
    paper_bgcolor=T["paper"],
    font=dict(color=T["text"], family=T["font"], size=12),
    margin=dict(l=50, r=30, t=50, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=T["text"])),
    xaxis=dict(gridcolor=T["border"], zerolinecolor=T["border"], tickfont=dict(color=T["muted"])),
    yaxis=dict(gridcolor=T["border"], zerolinecolor=T["border"], tickfont=dict(color=T["muted"])),
)


# ─── helpers ──────────────────────────────────────────────────────────────────

def run(script: str, args: list) -> dict:
    cmd = [sys.executable, str(SCRIPTS_DIR / script)] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
    except Exception:
        pass
    return {}


def chart_html(fig: go.Figure, height: int = 380) -> str:
    fig.update_layout(height=height)
    return pio.to_html(fig, full_html=False, include_plotlyjs=False,
                       config={"displayModeBar": False, "responsive": True})


def fmt_usd(v) -> str:
    if v is None: return "—"
    try:
        v = float(v)
        sign = "+" if v > 0 else ""
        return f"{sign}${abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(v)


def fmt_pct(v) -> str:
    if v is None: return "—"
    try:
        v = float(v)
        sign = "+" if v > 0 else ""
        return f"{sign}{v:.2f}%"
    except Exception:
        return str(v)


def color_class(v) -> str:
    try:
        return "pos" if float(v) >= 0 else "neg"
    except Exception:
        return ""


def now_str() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")


# ─── CSS + HTML base ──────────────────────────────────────────────────────────

BASE_CSS = f"""
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: {T["font"]};
  background: {T["bg"]};
  color: {T["text"]};
  padding: 0;
  min-height: 100vh;
}}
a {{ color: {T["blue"]}; text-decoration: none; }}

/* layout */
.wrapper {{ max-width: 960px; margin: 0 auto; padding: 32px 24px 64px; }}
.header {{ margin-bottom: 36px; }}
.header-top {{ display: flex; align-items: center; gap: 16px; margin-bottom: 6px; }}
.logo {{ font-size: 22px; font-weight: 700; color: {T["blue"]}; letter-spacing: -0.5px; }}
.logo span {{ color: {T["muted"]}; font-weight: 400; }}
.report-title {{ font-size: 28px; font-weight: 700; color: {T["text"]}; margin-bottom: 4px; }}
.report-meta {{ font-size: 13px; color: {T["muted"]}; }}

/* cards */
.section {{ margin-bottom: 32px; }}
.section-title {{
  font-size: 13px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.08em; color: {T["muted"]};
  margin-bottom: 14px; padding-bottom: 8px;
  border-bottom: 1px solid {T["border"]};
}}
.card {{
  background: {T["paper"]};
  border: 1px solid {T["border"]};
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 12px;
}}
.card-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 20px; }}

/* métricas */
.metric {{ background: {T["paper"]}; border: 1px solid {T["border"]}; border-radius: 8px; padding: 16px 18px; }}
.metric-label {{ font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; color: {T["muted"]}; margin-bottom: 6px; }}
.metric-value {{ font-size: 24px; font-weight: 700; color: {T["text"]}; }}
.metric-sub {{ font-size: 12px; color: {T["muted"]}; margin-top: 2px; }}

/* tabla */
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
thead th {{
  text-align: left; padding: 10px 12px;
  font-size: 11px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.06em; color: {T["muted"]};
  border-bottom: 1px solid {T["border"]};
}}
tbody td {{ padding: 11px 12px; border-bottom: 1px solid {T["border"]}; vertical-align: middle; }}
tbody tr:last-child td {{ border-bottom: none; }}
tbody tr:hover td {{ background: rgba(88,166,255,0.04); }}

/* colores */
.pos {{ color: {T["up"]}; font-weight: 600; }}
.neg {{ color: {T["down"]}; font-weight: 600; }}
.muted {{ color: {T["muted"]}; }}
.bold {{ font-weight: 600; }}
.ticker-badge {{
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 12px; font-weight: 700; font-family: monospace;
  background: rgba(88,166,255,0.12); color: {T["blue"]};
}}
.score-bar {{
  display: inline-block; height: 6px; border-radius: 3px;
  background: {T["blue"]}; vertical-align: middle; margin-right: 6px;
}}
.signal-tag {{
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 11px; font-weight: 500; margin: 2px;
  background: rgba(88,166,255,0.1); color: {T["blue"]};
}}
.signal-tag.up {{ background: rgba(63,185,80,0.12); color: {T["up"]}; }}
.signal-tag.down {{ background: rgba(248,81,73,0.12); color: {T["down"]}; }}

/* noticias */
.news-item {{ padding: 14px 0; border-bottom: 1px solid {T["border"]}; }}
.news-item:last-child {{ border-bottom: none; }}
.news-title {{ font-size: 14px; font-weight: 500; margin-bottom: 4px; line-height: 1.4; }}
.news-meta {{ font-size: 11px; color: {T["muted"]}; }}
.news-summary {{ font-size: 13px; color: {T["muted"]}; margin-top: 5px; line-height: 1.5; }}

/* chart container */
.chart-wrap {{ background: {T["paper"]}; border: 1px solid {T["border"]}; border-radius: 10px; padding: 4px; margin-bottom: 12px; overflow: hidden; }}

/* footer */
.footer {{ margin-top: 48px; padding-top: 20px; border-top: 1px solid {T["border"]}; font-size: 12px; color: {T["muted"]}; text-align: center; }}

@media (max-width: 600px) {{
  .wrapper {{ padding: 20px 16px 48px; }}
  .card-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .metric-value {{ font-size: 20px; }}
}}
</style>
"""

PLOTLY_JS = f'<script type="text/javascript">{get_plotlyjs()}</script>'


def html_doc(title: str, subtitle: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jarvis — {title}</title>
{PLOTLY_JS}
{BASE_CSS}
</head>
<body>
<div class="wrapper">
  <div class="header">
    <div class="header-top">
      <div class="logo">Jarvis <span>/ Asistente Financiero</span></div>
    </div>
    <div class="report-title">{title}</div>
    <div class="report-meta">{subtitle} · Generado el {now_str()}</div>
  </div>
  {body}
  <div class="footer">
    Reporte generado por Jarvis · Asistente Financiero Personal de Diego Rodriguez
  </div>
</div>
</body>
</html>"""


# ─── REPORTE DE PORTFOLIO ─────────────────────────────────────────────────────

def build_portfolio_report() -> str:
    data = run("portfolio_tracker.py", ["--json"])
    if not data or "positions" not in data:
        return html_doc("Sin datos de portfolio", "Cargá tus posiciones en jarvis/portfolio/active_positions.json",
                        "<p class='muted'>No se encontraron posiciones en el portfolio.</p>")

    summary = data["summary"]
    positions = [p for p in data["positions"] if p.get("current_price")]

    total_inv = summary.get("total_invested_usd", 0)
    total_val = summary.get("total_current_value_usd", 0)
    total_pnl = summary.get("total_pnl_usd", 0)
    total_pct = summary.get("total_pnl_pct", 0)

    # ── Gráfico 1: Asignación del portfolio (torta) ──
    tickers = [p["ticker"] for p in positions]
    values  = [p.get("current_value_usd") or 0 for p in positions]
    colors  = [T["blue"], T["purple"], T["orange"], T["up"], "#ff7b72", "#79c0ff",
               "#ffa198", "#c3e88d", "#89ddff", "#f78c6c"]

    fig_pie = go.Figure(go.Pie(
        labels=tickers, values=values,
        hole=0.55,
        marker=dict(colors=colors[:len(tickers)], line=dict(color=T["bg"], width=2)),
        textfont=dict(size=12, color=T["text"]),
        hovertemplate="<b>%{label}</b><br>Valor: $%{value:,.2f}<br>%{percent}<extra></extra>",
    ))
    fig_pie.update_layout(
        **PLOTLY_CONFIG,
        title=dict(text="Distribución del Portfolio", font=dict(size=14, color=T["text"]), x=0.02),
        showlegend=True,
        legend=dict(orientation="v", x=1, y=0.5, font=dict(size=12)),
        annotations=[dict(text=f"<b>${total_val:,.0f}</b>", x=0.5, y=0.5,
                          font=dict(size=16, color=T["text"]), showarrow=False)],
    )

    # ── Gráfico 2: P&L por posición (barras) ──
    pnl_vals = [p.get("pnl_pct") or 0 for p in positions]
    bar_colors = [T["up"] if v >= 0 else T["down"] for v in pnl_vals]

    fig_pnl = go.Figure(go.Bar(
        x=tickers, y=pnl_vals,
        marker_color=bar_colors,
        text=[f"{v:+.1f}%" for v in pnl_vals],
        textposition="outside",
        textfont=dict(color=T["text"], size=11),
        hovertemplate="<b>%{x}</b><br>P&L: %{y:+.2f}%<extra></extra>",
    ))
    fig_pnl.add_hline(y=0, line_color=T["border"], line_width=1)
    _b = {k: v for k, v in PLOTLY_CONFIG.items() if k not in ("xaxis","yaxis")}
    fig_pnl.update_layout(
        **_b,
        title=dict(text="Rendimiento por Posición (%)", font=dict(size=14, color=T["text"]), x=0.02),
        xaxis=PLOTLY_CONFIG["xaxis"],
        yaxis=dict(**PLOTLY_CONFIG["yaxis"], ticksuffix="%"),
    )

    # ── Tabla de posiciones ──
    rows = ""
    for p in positions:
        pnl_usd = p.get("pnl_usd")
        pnl_pct = p.get("pnl_pct")
        cls = color_class(pnl_pct)
        rows += f"""
        <tr>
          <td><span class="ticker-badge">{p["ticker"]}</span></td>
          <td class="muted">{p["name"][:28]}</td>
          <td class="bold">{p["quantity"]}</td>
          <td>${p["avg_buy_price"]:,.2f}</td>
          <td class="bold">${p["current_price"]:,.2f}</td>
          <td class="{cls}">{fmt_usd(pnl_usd)}</td>
          <td class="{cls}">{fmt_pct(pnl_pct)}</td>
        </tr>"""

    pnl_cls = color_class(total_pnl)
    body = f"""
    <div class="section">
      <div class="section-title">Resumen del Portfolio</div>
      <div class="card-grid">
        <div class="metric">
          <div class="metric-label">Capital invertido</div>
          <div class="metric-value">${total_inv:,.0f}</div>
          <div class="metric-sub">USD</div>
        </div>
        <div class="metric">
          <div class="metric-label">Valor actual</div>
          <div class="metric-value">${total_val:,.0f}</div>
          <div class="metric-sub">USD</div>
        </div>
        <div class="metric">
          <div class="metric-label">Ganancia / Pérdida</div>
          <div class="metric-value {pnl_cls}">{fmt_usd(total_pnl)}</div>
          <div class="metric-sub {pnl_cls}">{fmt_pct(total_pct)}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Posiciones activas</div>
          <div class="metric-value">{len(positions)}</div>
          <div class="metric-sub">instrumentos</div>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Distribución y Rendimiento</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        <div class="chart-wrap">{chart_html(fig_pie, 340)}</div>
        <div class="chart-wrap">{chart_html(fig_pnl, 340)}</div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Detalle de Posiciones</div>
      <div class="card" style="padding:0;overflow:hidden;">
        <table>
          <thead><tr>
            <th>Ticker</th><th>Nombre</th><th>Cantidad</th>
            <th>P. Compra</th><th>P. Actual</th><th>G/P (USD)</th><th>G/P (%)</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>"""

    return html_doc("Reporte de Portfolio", "Diego Rodriguez", body)


# ─── REPORTE DE MERCADO ───────────────────────────────────────────────────────

def build_market_report() -> str:
    data = run("market_briefing.py", [])
    if not data:
        return html_doc("Sin datos de mercado", "", "<p class='muted'>No se pudo obtener datos del mercado.</p>")

    sentiment = data.get("market_sentiment", "—")
    vix = data.get("vix", {})
    yc = data.get("yield_curve", {})
    indices = data.get("indices", [])
    sectors = data.get("sectors", {}).get("all", [])
    macro = data.get("macro", [])

    sent_colors = {"risk-on (mercado alcista)": T["up"], "risk-off (mercado bajista)": T["down"]}
    sent_color = sent_colors.get(sentiment, T["orange"])

    # ── Gráfico 1: Índices (variación diaria) ──
    idx_valid = [i for i in indices if i.get("change_1d_pct") is not None]
    idx_labels = [i["label"].replace(" (Volatilidad)", "") for i in idx_valid]
    idx_vals   = [i["change_1d_pct"] for i in idx_valid]
    idx_colors = [T["up"] if v >= 0 else T["down"] for v in idx_vals]

    fig_idx = go.Figure(go.Bar(
        x=idx_labels, y=idx_vals,
        marker_color=idx_colors,
        text=[f"{v:+.2f}%" for v in idx_vals],
        textposition="outside",
        textfont=dict(color=T["text"], size=11),
        hovertemplate="<b>%{x}</b><br>Variación: %{y:+.2f}%<extra></extra>",
    ))
    fig_idx.add_hline(y=0, line_color=T["border"])
    _base = {k: v for k, v in PLOTLY_CONFIG.items() if k not in ("xaxis","yaxis")}
    fig_idx.update_layout(**_base,
        title=dict(text="Índices Principales — Variación del Día (%)", font=dict(size=14, color=T["text"]), x=0.02),
        xaxis=PLOTLY_CONFIG["xaxis"],
        yaxis=dict(**PLOTLY_CONFIG["yaxis"], ticksuffix="%"))

    # ── Gráfico 2: Sectores (barras horizontales) ──
    sec_valid = sorted([s for s in sectors if s.get("change_1d_pct") is not None],
                       key=lambda x: x["change_1d_pct"])
    sec_labels = [s["label"] for s in sec_valid]
    sec_vals   = [s["change_1d_pct"] for s in sec_valid]
    sec_colors = [T["up"] if v >= 0 else T["down"] for v in sec_vals]

    fig_sec = go.Figure(go.Bar(
        x=sec_vals, y=sec_labels,
        orientation="h",
        marker_color=sec_colors,
        text=[f"{v:+.2f}%" for v in sec_vals],
        textposition="outside",
        textfont=dict(color=T["text"], size=11),
        hovertemplate="<b>%{y}</b><br>%{x:+.2f}%<extra></extra>",
    ))
    fig_sec.add_vline(x=0, line_color=T["border"])
    fig_sec.update_layout(**_base,
        title=dict(text="Sectores del S&P 500 — Rendimiento del Día (%)", font=dict(size=14, color=T["text"]), x=0.02),
        xaxis=dict(**PLOTLY_CONFIG["xaxis"], ticksuffix="%"),
        yaxis=PLOTLY_CONFIG["yaxis"],
        height=440)

    # ── Tabla macro ──
    macro_rows = ""
    for m in macro:
        if m.get("error"): continue
        c = m.get("change_1d_pct", 0)
        cls = color_class(c)
        macro_rows += f"""
        <tr>
          <td class="bold">{m["label"]}</td>
          <td class="bold">{m.get("current", "—"):,.4f}</td>
          <td class="{cls}">{fmt_pct(m.get("change_1d_pct"))}</td>
          <td class="{cls}">{fmt_pct(m.get("change_5d_pct"))}</td>
        </tr>"""

    vix_level = vix.get("level")
    vix_signal = vix.get("signal", "—")
    vix_cls = "pos" if vix_signal == "bajo" else ("neg" if vix_signal == "elevado" else "")
    yc_spread = yc.get("spread_10y_2y") if yc else None
    yc_inv = yc.get("inverted", False) if yc else False

    body = f"""
    <div class="section">
      <div class="section-title">Panorama General</div>
      <div class="card-grid">
        <div class="metric">
          <div class="metric-label">Sentimiento del mercado</div>
          <div class="metric-value" style="font-size:16px;color:{sent_color}">{sentiment.upper()}</div>
        </div>
        <div class="metric">
          <div class="metric-label">VIX (Volatilidad)</div>
          <div class="metric-value {vix_cls}">{f"{vix_level:.1f}" if vix_level else "—"}</div>
          <div class="metric-sub">{vix_signal}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Curva de rendimientos</div>
          <div class="metric-value {'neg' if yc_inv else 'pos'}">{f'{yc_spread:+.3f}%' if yc_spread else '—'}</div>
          <div class="metric-sub">{'Invertida ⚠' if yc_inv else 'Normal'}</div>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Índices y Sectores</div>
      <div class="chart-wrap">{chart_html(fig_idx, 320)}</div>
      <div class="chart-wrap">{chart_html(fig_sec, 460)}</div>
    </div>

    <div class="section">
      <div class="section-title">Activos Macroeconómicos</div>
      <div class="card" style="padding:0;overflow:hidden;">
        <table>
          <thead><tr>
            <th>Activo</th><th>Valor actual</th><th>Var. día</th><th>Var. semana</th>
          </tr></thead>
          <tbody>{macro_rows}</tbody>
        </table>
      </div>
    </div>"""

    return html_doc(f"Briefing del Mercado — {datetime.now().strftime('%d/%m/%Y')}",
                    "Análisis global del día", body)


# ─── REPORTE DE EMPRESA ───────────────────────────────────────────────────────

def build_company_report(ticker: str, period: str = "1y") -> str:
    data = run("analyze_company.py", [ticker, "--period", period, "--no-chart"])
    if not data:
        return html_doc(f"Sin datos para {ticker}", "", "<p class='muted'>No se pudo obtener datos.</p>")

    info   = data.get("company_info", {})
    price  = data.get("price_data", {})
    tech   = data.get("technicals", {})
    val    = data.get("valuation", {})
    health = data.get("financial_health", {})
    news   = data.get("news", [])
    name   = info.get("name", ticker)

    # ── Gráfico: historial de precios ──
    hist_data = run("fetch_market.py", [ticker, "--period", period])
    history   = hist_data.get("market", {}).get("history", [])

    fig_price = go.Figure()
    if history:
        dates  = [h["date"] for h in history]
        closes = [h["close"] for h in history]
        opens  = [h["open"] for h in history]
        highs  = [h["high"] for h in history]
        lows   = [h["low"] for h in history]
        vols   = [h["volume"] for h in history]

        fig_price = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                  vertical_spacing=0.04, row_heights=[0.75, 0.25])

        candle_colors = [T["up"] if c >= o else T["down"] for c, o in zip(closes, opens)]
        fig_price.add_trace(go.Candlestick(
            x=dates, open=opens, high=highs, low=lows, close=closes,
            name=ticker,
            increasing_line_color=T["up"], decreasing_line_color=T["down"],
            increasing_fillcolor=T["up"], decreasing_fillcolor=T["down"],
        ), row=1, col=1)

        for window, color in [(20, T["purple"]), (50, T["orange"]), (200, T["blue"])]:
            if len(closes) >= window:
                ma = [sum(closes[max(0,i-window):i])/min(i,window) for i in range(1, len(closes)+1)]
                fig_price.add_trace(go.Scatter(
                    x=dates, y=ma, mode="lines", name=f"MA{window}",
                    line=dict(color=color, width=1.2, dash="dot"), opacity=0.85
                ), row=1, col=1)

        fig_price.add_trace(go.Bar(
            x=dates, y=vols, name="Volumen",
            marker_color=candle_colors, opacity=0.5,
        ), row=2, col=1)

        fig_price.update_layout(
            **PLOTLY_CONFIG,
            title=dict(text=f"{ticker} — Precio histórico ({period})", font=dict(size=14, color=T["text"]), x=0.02),
            xaxis_rangeslider_visible=False,
            xaxis2=dict(**PLOTLY_CONFIG["xaxis"]),
            yaxis2=dict(**PLOTLY_CONFIG["yaxis"]),
            height=460,
        )

    # ── Señales ──
    all_signals = (val.get("signals", []) + health.get("signals", []) +
                   ([f"Tendencia {tech['trend']}"] if tech.get("trend") else []) +
                   ([tech["rsi_signal"]] if tech.get("rsi_signal") and tech["rsi_signal"] != "neutral" else []))

    def signal_tag(s: str) -> str:
        cls = "up" if any(w in s.lower() for w in ["alto", "fuerte", "sólido", "alcista", "positivo", "bajo"]) else \
              "down" if any(w in s.lower() for w in ["bajista", "elevada", "riesgo"]) else ""
        return f'<span class="signal-tag {cls}">{s}</span>'

    signals_html = "".join(signal_tag(s) for s in all_signals)

    # ── Noticias ──
    news_html = ""
    for n in news[:6]:
        news_html += f"""
        <div class="news-item">
          <div class="news-title">{n.get("title","")}</div>
          <div class="news-meta">{n.get("source","")} · {str(n.get("published_at",""))[:10]}</div>
          {"<div class='news-summary'>" + n.get("summary","")[:200] + "...</div>" if n.get("summary") else ""}
        </div>"""

    current = tech.get("current_price", price.get("current_price"))
    change  = price.get("pct_change", 0)
    chg_cls = color_class(change)

    def metric_row(label, value, sub=""):
        return f"""
        <div class="metric">
          <div class="metric-label">{label}</div>
          <div class="metric-value" style="font-size:18px">{value}</div>
          {"<div class='metric-sub'>" + sub + "</div>" if sub else ""}
        </div>"""

    def row(label, value, cls=""):
        return f"<tr><td class='muted'>{label}</td><td class='bold {cls}'>{value}</td></tr>"

    fund_rows = (
        row("Capitalización de mercado", f"${(info.get('market_cap') or 0)/1e9:.1f}B") +
        row("PE Trailing / Forward",
            f"{val.get('trailing_pe','—')} / {val.get('forward_pe','—')}") +
        row("Price/Book", f"{val.get('price_to_book','—')}") +
        row("Target de analistas",
            f"${val.get('analyst_target','—')} ({fmt_pct(val.get('upside_to_target_pct'))} upside)" if val.get('analyst_target') else "—") +
        row("Consenso analistas", (val.get("analyst_recommendation") or "—").upper()) +
        row("Número de analistas", str(val.get("num_analysts","—")))
    )

    fin_rows = (
        row("Margen neto", fmt_pct(health.get("profit_margin_pct"))) +
        row("ROE", fmt_pct(health.get("roe_pct"))) +
        row("Crecimiento de ingresos", fmt_pct(health.get("revenue_growth_pct"))) +
        row("Crecimiento de ganancias", fmt_pct(health.get("earnings_growth_pct"))) +
        row("Deuda neta / EBITDA", str(health.get("debt_to_ebitda","—"))) +
        row("Free Cash Flow", f"${(health.get('free_cashflow') or 0)/1e9:.1f}B")
    )

    tech_rows = (
        row("MA 20", f"${tech.get('ma20','—')}") +
        row("MA 50", f"${tech.get('ma50','—')}") +
        row("MA 200", f"${tech.get('ma200','—')}") +
        row("RSI 14", f"{tech.get('rsi_14','—')} — {tech.get('rsi_signal','—')}") +
        row("Tendencia", tech.get("trend","—").upper()) +
        row("Máx. 52 semanas", f"${tech.get('52w_high','—')}") +
        row("Mín. 52 semanas", f"${tech.get('52w_low','—')}")
    )

    body = f"""
    <div class="section">
      <div class="section-title">Resumen</div>
      <div class="card-grid">
        {metric_row("Precio actual", f"${current:,.2f}" if current else "—",
                    f"<span class='{chg_cls}'>{fmt_pct(change)}</span> — {period}")}
        {metric_row("Sector", info.get("sector","—"))}
        {metric_row("Industria", info.get("industry","—"))}
        {metric_row("Empleados", f"{(info.get('employees') or 0):,}")}
      </div>
      {"<div class='card'><p style='font-size:13px;color:" + T["muted"] + ";line-height:1.6'>" + info.get("description","")[:500] + "...</p></div>" if info.get("description") else ""}
    </div>

    <div class="section">
      <div class="section-title">Precio Histórico</div>
      <div class="chart-wrap">{chart_html(fig_price, 460)}</div>
    </div>

    <div class="section">
      <div class="section-title">Señales clave</div>
      <div class="card">{signals_html or "<span class='muted'>Sin señales destacadas</span>"}</div>
    </div>

    <div class="section">
      <div class="section-title">Análisis detallado</div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
        <div class="card" style="padding:0;overflow:hidden;">
          <div style="padding:12px 16px;border-bottom:1px solid {T["border"]};font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:{T["muted"]}">Valuación</div>
          <table><tbody>{fund_rows}</tbody></table>
        </div>
        <div class="card" style="padding:0;overflow:hidden;">
          <div style="padding:12px 16px;border-bottom:1px solid {T["border"]};font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:{T["muted"]}">Salud Financiera</div>
          <table><tbody>{fin_rows}</tbody></table>
        </div>
        <div class="card" style="padding:0;overflow:hidden;">
          <div style="padding:12px 16px;border-bottom:1px solid {T["border"]};font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:{T["muted"]}">Análisis Técnico</div>
          <table><tbody>{tech_rows}</tbody></table>
        </div>
      </div>
    </div>

    {"<div class='section'><div class='section-title'>Noticias recientes</div><div class='card'>" + news_html + "</div></div>" if news_html else ""}
    """

    return html_doc(f"{ticker} — {name}", f"Análisis completo · Período {period}", body)


# ─── REPORTE DE OPORTUNIDADES ─────────────────────────────────────────────────

def build_opportunities_report(sector: str = "tech", top: int = 10) -> str:
    data = run("scan_opportunities.py", ["--list", sector, "--top", str(top), "--min-score", "40"])
    if not data:
        return html_doc("Sin datos de oportunidades", "", "<p class='muted'>No se pudo ejecutar el scanner.</p>")

    opps = data.get("top_opportunities", [])
    if not opps:
        return html_doc("Sin oportunidades", "", "<p class='muted'>No se encontraron oportunidades con el score mínimo.</p>")

    sector_labels = {"tech":"Tecnología","finance":"Finanzas","etfs":"ETFs","latam":"Latinoamérica","custom":"Personalizada"}

    # ── Gráfico: ranking de scores ──
    names  = [f"{o['ticker']}" for o in opps]
    scores = [o.get("score", 0) for o in opps]
    bar_colors = [T["up"] if s >= 65 else T["orange"] if s >= 55 else T["muted"] for s in scores]

    fig_scores = go.Figure(go.Bar(
        x=names, y=scores,
        marker_color=bar_colors,
        text=[f"{s}/100" for s in scores],
        textposition="outside",
        textfont=dict(color=T["text"], size=11),
        hovertemplate="<b>%{x}</b><br>Score: %{y}/100<extra></extra>",
    ))
    fig_scores.add_hline(y=65, line_color=T["up"], line_dash="dot", opacity=0.5,
                         annotation_text="Zona de compra", annotation_font_color=T["up"])
    _bs = {k: v for k, v in PLOTLY_CONFIG.items() if k not in ("xaxis","yaxis")}
    fig_scores.update_layout(**_bs,
        title=dict(text=f"Score de oportunidad — Sector {sector_labels.get(sector, sector)}", font=dict(size=14, color=T["text"]), x=0.02),
        xaxis=PLOTLY_CONFIG["xaxis"],
        yaxis=dict(**PLOTLY_CONFIG["yaxis"], range=[0, 110]))

    # ── Tabla detallada ──
    rows = ""
    for o in opps:
        cls = color_class(o.get("period_return_pct", 0))
        upcls = color_class(o.get("upside_to_target_pct", 0))
        signals = "".join(
            f'<span class="signal-tag" style="font-size:10px">{s[:35]}</span>'
            for s in (o.get("signals") or [])[:3]
        )
        rows += f"""
        <tr>
          <td>
            <span class="ticker-badge">{o["ticker"]}</span>
            <div style="font-size:11px;color:{T["muted"]};margin-top:3px">{o.get("name","")[:22]}</div>
          </td>
          <td>
            <div style="display:flex;align-items:center;gap:8px">
              <div class="score-bar" style="width:{o.get('score',0) * 1.2}px"></div>
              <span class="bold">{o.get("score",0)}</span>
            </div>
          </td>
          <td class="bold">${o.get("current_price","—")}</td>
          <td class="{cls}">{fmt_pct(o.get("period_return_pct"))}</td>
          <td class="{upcls}">{fmt_pct(o.get("upside_to_target_pct")) if o.get("upside_to_target_pct") else "—"}</td>
          <td>{o.get("analyst_recommendation","—").upper()}</td>
          <td>{signals}</td>
        </tr>"""

    body = f"""
    <div class="section">
      <div class="section-title">Resumen del escaneo</div>
      <div class="card-grid">
        <div class="metric">
          <div class="metric-label">Tickers analizados</div>
          <div class="metric-value">{data.get("total_scanned","—")}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Con score suficiente</div>
          <div class="metric-value">{data.get("total_results","—")}</div>
        </div>
        <div class="metric">
          <div class="metric-label">Sector</div>
          <div class="metric-value" style="font-size:18px">{sector_labels.get(sector,sector)}</div>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Ranking de oportunidades</div>
      <div class="chart-wrap">{chart_html(fig_scores, 340)}</div>
    </div>

    <div class="section">
      <div class="section-title">Detalle de candidatos</div>
      <div class="card" style="padding:0;overflow:hidden;">
        <table>
          <thead><tr>
            <th>Ticker</th><th>Score</th><th>Precio</th>
            <th>Rend. período</th><th>Upside analistas</th><th>Consenso</th><th>Señales</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>"""

    return html_doc(f"Oportunidades — {sector_labels.get(sector,sector)}",
                    f"Top {len(opps)} candidatos por score de oportunidad", body)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Jarvis — Generador de Reportes Dinámicos")
    parser.add_argument("--type", choices=["portfolio","market","company","opportunities"],
                        default="market")
    parser.add_argument("--ticker", default="SPY")
    parser.add_argument("--period", default="1y")
    parser.add_argument("--list",   default="tech", dest="sector")
    parser.add_argument("--top",    type=int, default=10)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    print(f"Generando reporte: {args.type}...", file=sys.stderr)

    if args.type == "portfolio":
        html = build_portfolio_report()
    elif args.type == "market":
        html = build_market_report()
    elif args.type == "company":
        html = build_company_report(args.ticker.upper(), args.period)
    elif args.type == "opportunities":
        html = build_opportunities_report(args.sector, args.top)
    else:
        html = build_market_report()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = args.output or f"reporte_{args.type}_{ts}"
    path = REPORTS_DIR / f"{name}.html"

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(json.dumps({
        "reporte_tipo": args.type,
        "archivo": str(path),
        "generado_el": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
