"""
Jarvis - Chart Generator
Genera gráficos interactivos HTML usando Plotly
Uso: python chart_generator.py TICKER [--period 1y] [--type candlestick|line|area] [--compare TICKER2]
"""

import argparse
import json
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance no instalado. Ejecutá: pip install yfinance")
    sys.exit(1)

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:
    print("ERROR: plotly no instalado. Ejecutá: pip install plotly")
    sys.exit(1)

CHARTS_DIR = Path(__file__).parent.parent / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd", "max"]
CHART_TYPES = ["candlestick", "line", "area"]

JARVIS_THEME = {
    "bg_color": "#0d1117",
    "paper_color": "#161b22",
    "grid_color": "#21262d",
    "text_color": "#e6edf3",
    "up_color": "#3fb950",
    "down_color": "#f85149",
    "line_color": "#58a6ff",
    "volume_color": "#388bfd",
    "ma_colors": ["#d2a8ff", "#ffa657", "#ff7b72"]
}


def fetch_data(ticker: str, period: str):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        print(f"ERROR: No hay datos para {ticker}", file=sys.stderr)
        sys.exit(1)
    info = stock.info
    name = info.get("longName") or info.get("shortName") or ticker
    return hist, name


def add_moving_averages(fig, hist, row=1):
    colors = JARVIS_THEME["ma_colors"]
    for i, window in enumerate([20, 50, 200]):
        if len(hist) >= window:
            ma = hist["Close"].rolling(window=window).mean()
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=ma,
                mode="lines",
                name=f"MA{window}",
                line=dict(color=colors[i % len(colors)], width=1, dash="dot"),
                opacity=0.8
            ), row=row, col=1)


def build_candlestick_chart(ticker: str, hist, name: str) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25]
    )

    colors = [JARVIS_THEME["up_color"] if c >= o else JARVIS_THEME["down_color"]
              for c, o in zip(hist["Close"], hist["Open"])]

    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist["Open"],
        high=hist["High"],
        low=hist["Low"],
        close=hist["Close"],
        name=ticker,
        increasing_line_color=JARVIS_THEME["up_color"],
        decreasing_line_color=JARVIS_THEME["down_color"],
        increasing_fillcolor=JARVIS_THEME["up_color"],
        decreasing_fillcolor=JARVIS_THEME["down_color"]
    ), row=1, col=1)

    add_moving_averages(fig, hist, row=1)

    fig.add_trace(go.Bar(
        x=hist.index,
        y=hist["Volume"],
        name="Volumen",
        marker_color=colors,
        opacity=0.6
    ), row=2, col=1)

    return fig


def build_line_chart(ticker: str, hist, name: str, area: bool = False) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25]
    )

    fill = "tozeroy" if area else None

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["Close"],
        mode="lines",
        name=ticker,
        line=dict(color=JARVIS_THEME["line_color"], width=2),
        fill=fill,
        fillcolor="rgba(88, 166, 255, 0.1)"
    ), row=1, col=1)

    add_moving_averages(fig, hist, row=1)

    fig.add_trace(go.Bar(
        x=hist.index,
        y=hist["Volume"],
        name="Volumen",
        marker_color=JARVIS_THEME["volume_color"],
        opacity=0.6
    ), row=2, col=1)

    return fig


def apply_jarvis_theme(fig, title: str, ticker: str, period: str):
    t = JARVIS_THEME
    first_close = None
    last_close = None

    for trace in fig.data:
        if hasattr(trace, 'close') and trace.close is not None:
            first_close = trace.close[0]
            last_close = trace.close[-1]
            break
        elif hasattr(trace, 'y') and trace.y is not None and trace.name == ticker:
            first_close = trace.y[0]
            last_close = trace.y[-1]
            break

    if first_close and last_close:
        change = last_close - first_close
        pct = (change / first_close) * 100
        sign = "+" if change >= 0 else ""
        color = t["up_color"] if change >= 0 else t["down_color"]
        subtitle = f"<span style='color:{color}'>{sign}${change:.2f} ({sign}{pct:.2f}%) — período: {period}</span>"
        full_title = f"<b>{title}</b><br><sub>{subtitle}</sub>"
    else:
        full_title = f"<b>{title}</b>"

    fig.update_layout(
        title=dict(text=full_title, font=dict(color=t["text_color"], size=18), x=0.02),
        plot_bgcolor=t["bg_color"],
        paper_bgcolor=t["paper_color"],
        font=dict(color=t["text_color"], family="Inter, sans-serif"),
        xaxis_rangeslider_visible=False,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=t["grid_color"],
            font=dict(color=t["text_color"])
        ),
        margin=dict(l=60, r=30, t=80, b=40),
        height=600
    )

    for axis in ["xaxis", "yaxis", "xaxis2", "yaxis2"]:
        fig.update_layout(**{axis: dict(
            gridcolor=t["grid_color"],
            zerolinecolor=t["grid_color"],
            tickfont=dict(color=t["text_color"])
        )})


def main():
    parser = argparse.ArgumentParser(description="Jarvis Chart Generator")
    parser.add_argument("ticker", help="Ticker principal (ej: AAPL)")
    parser.add_argument("--period", default="6mo", choices=PERIODS)
    parser.add_argument("--type", default="candlestick", choices=CHART_TYPES, dest="chart_type")
    parser.add_argument("--open", action="store_true", help="Abrir el gráfico en el browser")
    parser.add_argument("--output", help="Nombre del archivo de salida (sin extensión)")

    args = parser.parse_args()
    ticker = args.ticker.upper()

    hist, name = fetch_data(ticker, args.period)

    if args.chart_type == "candlestick":
        fig = build_candlestick_chart(ticker, hist, name)
    elif args.chart_type == "area":
        fig = build_line_chart(ticker, hist, name, area=True)
    else:
        fig = build_line_chart(ticker, hist, name, area=False)

    title = f"{ticker} — {name}"
    apply_jarvis_theme(fig, title, ticker, args.period)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = args.output or f"{ticker}_{args.period}_{args.chart_type}_{timestamp}"
    output_path = CHARTS_DIR / f"{filename}.html"

    fig.write_html(str(output_path), include_plotlyjs=True)

    result = {
        "ticker": ticker,
        "name": name,
        "period": args.period,
        "chart_type": args.chart_type,
        "output_file": str(output_path),
        "data_points": len(hist)
    }
    print(json.dumps(result, indent=2))

    if args.open:
        webbrowser.open(str(output_path))


if __name__ == "__main__":
    main()
