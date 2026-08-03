"""
Genera un dashboard HTML con metricas de contenido de TikTok del consultorio.
Uso: python consultorio/scripts/generar_dashboard_tiktok.py
"""
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}


def parse_fecha_es(texto, anio=2026):
    match = re.match(r"(\d{1,2}) de (\w+)", str(texto).strip())
    if not match:
        return None
    dia, mes_nombre = match.groups()
    mes = MESES.get(mes_nombre.lower())
    if not mes:
        return None
    return datetime(anio, mes, int(dia))


def clasificar_tema(titulo):
    t = titulo.lower()
    if "rinomodelacion" in t or "rinomodelación" in t:
        return "Rinomodelación"
    if "relleno de labios" in t:
        return "Relleno de labios"
    return "Otro"


def main():
    base = Path(__file__).resolve().parent.parent
    csv_path = base / "redes" / "tiktok" / "metricas" / "contenido_export_20260727.csv"
    df = pd.read_csv(csv_path)

    df["fecha_post"] = df["Post time"].apply(parse_fecha_es)
    df["tema"] = df["Video title"].apply(clasificar_tema)
    df["mes"] = df["fecha_post"].dt.strftime("%Y-%m")
    df = df.sort_values("fecha_post")

    posts_por_mes = df.groupby("mes").size().reset_index(name="cantidad")
    posts_por_tema = df.groupby("tema").size().reset_index(name="cantidad")
    vistas_por_tema = df.groupby("tema")["Total views"].sum().reset_index()

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "bar"}, {"type": "pie"}], [{"type": "pie"}, {"type": "table"}]],
        subplot_titles=(
            "Publicaciones por mes",
            "Distribución de temas (cantidad de posteos)",
            "Vistas totales por tema",
            "Top publicaciones por vistas",
        ),
        row_heights=[0.5, 0.5],
    )

    fig.add_trace(
        go.Bar(x=posts_por_mes["mes"], y=posts_por_mes["cantidad"], marker_color="#E85D75", name="Posteos"),
        row=1, col=1,
    )

    fig.add_trace(
        go.Pie(labels=posts_por_tema["tema"], values=posts_por_tema["cantidad"], hole=0.4,
               marker=dict(colors=["#E85D75", "#5DA9E8", "#B0B0B0"])),
        row=1, col=2,
    )

    fig.add_trace(
        go.Pie(labels=vistas_por_tema["tema"], values=vistas_por_tema["Total views"], hole=0.4,
               marker=dict(colors=["#E85D75", "#5DA9E8", "#B0B0B0"])),
        row=2, col=1,
    )

    top5 = df.sort_values("Total views", ascending=False).head(5)
    fig.add_trace(
        go.Table(
            header=dict(values=["Título", "Fecha", "Vistas", "Likes"], fill_color="#333", font=dict(color="white")),
            cells=dict(values=[
                top5["Video title"].str.slice(0, 35),
                top5["fecha_post"].dt.strftime("%d/%m/%Y"),
                top5["Total views"].map("{:,}".format),
                top5["Total likes"].map("{:,}".format),
            ]),
        ),
        row=2, col=2,
    )

    fig.update_layout(
        title_text=f"Dashboard de contenido TikTok — @drdiegor (generado {datetime.now().strftime('%d/%m/%Y %H:%M')})",
        height=900,
        showlegend=False,
    )

    out_path = base / "redes" / "tiktok" / "dashboard_tiktok.html"
    fig.write_html(str(out_path))
    print(f"Dashboard generado: {out_path}")
    print()
    print("Resumen:")
    print(posts_por_mes.to_string(index=False))
    print()
    print(posts_por_tema.to_string(index=False))


if __name__ == "__main__":
    main()
