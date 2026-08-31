"""
Analiza el historial acumulado por oportunidades_binance.py (--guardar) para
encontrar en qué horarios/días suele abrirse más la brecha intra-Binance.

Necesita varios días de datos logueados para decir algo confiable — con una
sola corrida no hay patrón que sacar, solo una foto.

Uso:
    python3 analizar_historial.py                  # todos los activos
    python3 analizar_historial.py --activo USDT     # uno solo
"""
import argparse
import csv
import os
from collections import defaultdict

from rich.console import Console
from rich.table import Table

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
HISTORIAL_CSV = os.path.join(RESULTS_DIR, "historial_oportunidades.csv")

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Analiza el historial de brechas logueado")
    parser.add_argument("--activo", default=None, help="Filtrar por un activo (ej. USDT)")
    args = parser.parse_args()

    if not os.path.isfile(HISTORIAL_CSV):
        console.print(f"[yellow]Todavía no hay historial en {HISTORIAL_CSV}. "
                       f"Corré oportunidades_binance.py con --guardar varias veces (idealmente en distintos "
                       f"horarios/días) antes de analizar.[/yellow]")
        return

    filas = []
    with open(HISTORIAL_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if args.activo and row["activo"] != args.activo.upper():
                continue
            filas.append(row)

    if len(filas) < 5:
        console.print(f"[yellow]Solo hay {len(filas)} registros — muy pocos para sacar un patrón horario confiable. "
                       f"Seguí logueando (--guardar) durante unos días.[/yellow]")

    if not filas:
        console.print("[yellow]Sin datos para el filtro pedido.[/yellow]")
        return

    por_hora = defaultdict(list)
    por_dia = defaultdict(list)
    for row in filas:
        hora = row["hora"].split(":")[0]
        por_hora[hora].append(float(row["gap_pct"]))
        por_dia[row["dia_semana"]].append(float(row["gap_pct"]))

    tabla_hora = Table(title="Brecha promedio por hora del día")
    tabla_hora.add_column("Hora", style="cyan")
    tabla_hora.add_column("Brecha promedio", justify="right")
    tabla_hora.add_column("Muestras", justify="right")
    for hora in sorted(por_hora, key=lambda h: int(h)):
        vals = por_hora[hora]
        tabla_hora.add_row(f"{hora}:00", f"{sum(vals)/len(vals):.3f}%", str(len(vals)))
    console.print(tabla_hora)

    dias_orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    tabla_dia = Table(title="Brecha promedio por día de la semana")
    tabla_dia.add_column("Día", style="cyan")
    tabla_dia.add_column("Brecha promedio", justify="right")
    tabla_dia.add_column("Muestras", justify="right")
    for dia in dias_orden:
        if dia in por_dia:
            vals = por_dia[dia]
            tabla_dia.add_row(dia, f"{sum(vals)/len(vals):.3f}%", str(len(vals)))
    console.print(tabla_dia)

    console.print(f"\n[bold]Total de registros analizados:[/bold] {len(filas)}")


if __name__ == "__main__":
    main()
