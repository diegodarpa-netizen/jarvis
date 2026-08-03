"""
Analizador de exports del Administrador de Anuncios de Meta.
Uso: python marketing/scripts/analizar_meta.py --file marketing/meta/exports/meta_campanas_202605.csv
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
except ImportError:
    print("Faltan dependencias. Ejecutá: pip install pandas rich")
    sys.exit(1)

console = Console()

# Mapeo de columnas comunes de Meta (ES e EN)
COLUMN_MAP = {
    # Español
    "nombre de la campaña": "campana",
    "nombre del conjunto de anuncios": "conjunto",
    "nombre del anuncio": "anuncio",
    "importe gastado (ars)": "gasto",
    "importe gastado (usd)": "gasto",
    "importe gastado": "gasto",
    "resultados": "conversiones",
    "costo por resultado": "cpa",
    "alcance": "alcance",
    "impresiones": "impresiones",
    "frecuencia": "frecuencia",
    "clics (todos)": "clics",
    "ctr (todos)": "ctr",
    "cpc (todos)": "cpc",
    "cpm (costo por 1.000 impresiones)": "cpm",
    "roas de compra": "roas",
    "valor de conversión de compras": "valor_conversion",
    # Inglés
    "campaign name": "campana",
    "ad set name": "conjunto",
    "ad name": "anuncio",
    "amount spent (usd)": "gasto",
    "amount spent": "gasto",
    "results": "conversiones",
    "cost per result": "cpa",
    "reach": "alcance",
    "impressions": "impresiones",
    "frequency": "frecuencia",
    "clicks (all)": "clics",
    "ctr (all)": "ctr",
    "cpc (all)": "cpc",
    "cpm (cost per 1,000 impressions)": "cpm",
    "purchase roas": "roas",
    "purchase conversion value": "valor_conversion",
}


def cargar_csv(filepath):
    try:
        df = pd.read_csv(filepath, encoding="utf-8-sig", thousands=",", decimal=".")
    except Exception:
        df = pd.read_csv(filepath, encoding="latin-1", thousands=",", decimal=".")

    # Normalizar nombres de columnas
    df.columns = [c.strip().lower() for c in df.columns]
    rename = {col: COLUMN_MAP[col] for col in df.columns if col in COLUMN_MAP}
    df = df.rename(columns=rename)

    # Convertir columnas numéricas
    numeric_cols = ["gasto", "conversiones", "cpa", "alcance", "impresiones",
                    "frecuencia", "clics", "ctr", "cpc", "cpm", "roas", "valor_conversion"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ".").str.replace("%", ""), errors="coerce")

    return df


def analizar_campanas(df):
    if "campana" not in df.columns:
        console.print("[red]No se encontró la columna 'Nombre de la campaña'. Verificá el formato del CSV.[/red]")
        return

    console.rule("[bold cyan]ANÁLISIS DE CAMPAÑAS — META ADS[/bold cyan]")
    console.print(f"Archivo analizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    # Agrupar por campaña
    agg = {}
    for col in ["gasto", "impresiones", "clics", "alcance", "conversiones", "valor_conversion"]:
        if col in df.columns:
            agg[col] = "sum"
    for col in ["frecuencia", "roas", "ctr", "cpc", "cpm", "cpa"]:
        if col in df.columns:
            agg[col] = "mean"

    grupo = df.groupby("campana").agg(agg).reset_index()
    grupo = grupo.sort_values("gasto", ascending=False)

    # Tabla de rendimiento
    tabla = Table(title="Rendimiento por Campaña", show_lines=True)
    tabla.add_column("Campaña", style="bold white", min_width=20)
    tabla.add_column("Gasto", justify="right", style="yellow")
    tabla.add_column("Impresiones", justify="right")
    tabla.add_column("Clics", justify="right")
    tabla.add_column("CTR", justify="right", style="cyan")
    tabla.add_column("CPM", justify="right")
    tabla.add_column("CPC", justify="right")
    tabla.add_column("ROAS", justify="right", style="green")

    for _, row in grupo.iterrows():
        nombre = str(row["campana"])[:35]
        gasto = f"${row['gasto']:,.2f}" if "gasto" in row else "—"
        impresiones = f"{int(row['impresiones']):,}" if "impresiones" in row else "—"
        clics = f"{int(row['clics']):,}" if "clics" in row else "—"
        ctr = f"{row['ctr']:.2f}%" if "ctr" in row else "—"
        cpm = f"${row['cpm']:,.2f}" if "cpm" in row else "—"
        cpc = f"${row['cpc']:,.2f}" if "cpc" in row else "—"

        roas_val = row.get("roas", None)
        if pd.notna(roas_val) and roas_val > 0:
            roas_str = f"{roas_val:.2f}x"
            roas_color = "green" if roas_val >= 3 else ("yellow" if roas_val >= 1.5 else "red")
        else:
            roas_str = "N/D"
            roas_color = "white"

        tabla.add_row(nombre, gasto, impresiones, clics, ctr, cpm, cpc,
                      f"[{roas_color}]{roas_str}[/{roas_color}]")

    console.print(tabla)

    # Resumen total
    total_gasto = grupo["gasto"].sum() if "gasto" in grupo else 0
    total_impresiones = grupo["impresiones"].sum() if "impresiones" in grupo else 0
    total_clics = grupo["clics"].sum() if "clics" in grupo else 0
    roas_prom = grupo["roas"].mean() if "roas" in grupo else None

    console.print()
    console.print(Panel(
        f"[bold]Total gastado:[/bold]     ${total_gasto:,.2f}\n"
        f"[bold]Total impresiones:[/bold] {int(total_impresiones):,}\n"
        f"[bold]Total clics:[/bold]       {int(total_clics):,}\n"
        f"[bold]CTR promedio:[/bold]      {(total_clics/total_impresiones*100):.2f}% " if total_impresiones > 0 else ""
        f"[bold]ROAS promedio:[/bold]     {roas_prom:.2f}x" if roas_prom and pd.notna(roas_prom) else "",
        title="[cyan]Resumen General[/cyan]"
    ))

    # Alertas automáticas
    alertas = []

    if "frecuencia" in grupo.columns:
        fat = grupo[grupo["frecuencia"] > 3]
        for _, row in fat.iterrows():
            alertas.append(f"⚠️  [yellow]FATIGA[/yellow]: '{row['campana'][:40]}' tiene frecuencia {row['frecuencia']:.1f} (recomendado < 3)")

    if "roas" in grupo.columns:
        bajos = grupo[(grupo["roas"] < 1.5) & (grupo["roas"] > 0)]
        for _, row in bajos.iterrows():
            alertas.append(f"🔴 [red]ROAS BAJO[/red]: '{row['campana'][:40]}' tiene ROAS {row['roas']:.2f}x — considerar pausar o ajustar")

    if "ctr" in grupo.columns:
        ctr_bajo = grupo[grupo["ctr"] < 0.5]
        for _, row in ctr_bajo.iterrows():
            alertas.append(f"📉 [yellow]CTR BAJO[/yellow]: '{row['campana'][:40]}' tiene CTR {row['ctr']:.2f}% — revisar creatividad")

    if alertas:
        console.print()
        console.rule("[bold red]Alertas detectadas[/bold red]")
        for alerta in alertas:
            console.print(f"  {alerta}")

    console.print()
    console.rule("[bold green]Análisis completado[/bold green]")


def main():
    parser = argparse.ArgumentParser(description="Analizador de campañas Meta Ads")
    parser.add_argument("--file", "-f", required=True, help="Ruta al CSV exportado de Meta")
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        console.print(f"[red]Archivo no encontrado: {filepath}[/red]")
        console.print(f"Guardá el export de Meta en: marketing/meta/exports/")
        sys.exit(1)

    df = cargar_csv(filepath)
    analizar_campanas(df)


if __name__ == "__main__":
    main()
