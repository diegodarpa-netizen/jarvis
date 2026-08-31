"""
Scanner de oportunidades DENTRO de Binance P2P, multi-activo, simulando un
monto real (ej. USD 10.000) en vez de mirar solo el mejor precio de punta
de libro.

Por qué simula el "llenado" y no solo el mejor precio:
    Un solo anuncio rara vez tiene $10.000 USD de profundidad. Para mover
    ese monto hay que ir comiendo varios anuncios (como hizo el conocido
    de Diego con sus 17 vueltas) — el precio promedio que termina pagando
    es peor que el mejor precio de punta. Este script simula exactamente
    eso: acumula anuncios ordenados por precio hasta completar el monto
    objetivo y calcula el precio promedio ponderado real.

Uso:
    python3 oportunidades_binance.py                        # USD 10.000, activos por default
    python3 oportunidades_binance.py --monto-usd 5000
    python3 oportunidades_binance.py --activos USDT,BTC,ETH
    python3 oportunidades_binance.py --guardar               # loguea al historial para análisis de horarios

Fuente: API pública de anuncios de Binance P2P (p2p.binance.com).
"""
import argparse
import csv
import datetime
import os

import requests
from rich.console import Console
from rich.table import Table

BINANCE_P2P_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
HEADERS = {"User-Agent": "Mozilla/5.0"}
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
HISTORIAL_CSV = os.path.join(RESULTS_DIR, "historial_oportunidades.csv")

ACTIVOS_DEFAULT = ["USDT", "USDC", "BTC", "ETH", "BNB"]

console = Console()


def obtener_ads(activo: str, trade_type: str, filas: int = 20, paginas: int = 2) -> list:
    """trade_type='SELL' -> anunciantes vendiendo (precio al que VOS comprás).
    trade_type='BUY'  -> anunciantes comprando (precio al que VOS vendés).
    El endpoint de Binance rechaza rows > 20 ('illegal parameter'), así que
    para más profundidad de libro se piden varias páginas de 20."""
    todos = []
    for pagina in range(1, paginas + 1):
        body = {
            "page": pagina, "rows": filas, "payTypes": [], "countries": [],
            "publisherType": None, "asset": activo.upper(), "fiat": "ARS",
            "tradeType": trade_type,
        }
        try:
            r = requests.post(BINANCE_P2P_URL, json=body, headers=HEADERS, timeout=15)
            r.raise_for_status()
            body_json = r.json()
            data = body_json.get("data") or []
        except Exception as e:
            console.print(f"[yellow]  aviso: {activo} {trade_type} (pág. {pagina}) falló: {e}[/yellow]")
            data = []
        if not data:
            break
        todos.extend(data)

    ads = []
    for item in todos:
        adv = item["adv"]
        ads.append({
            "precio": float(adv["price"]),
            "disponible_unidad": float(adv["surplusAmount"]),
            "min_ars": float(adv["minSingleTransAmount"]),
            "max_ars": float(adv["maxSingleTransAmount"]),
        })
    return ads


def simular_llenado(ads: list, monto_ars_objetivo: float, comprando: bool) -> dict:
    """Recorre los anuncios en el mejor orden (más barato primero si
    comprás, más caro primero si vendés) y acumula hasta completar el
    monto objetivo en ARS. Devuelve el precio promedio ponderado real."""
    orden = sorted(ads, key=lambda a: a["precio"], reverse=not comprando)

    ars_acumulado = 0.0
    unidades_acumuladas = 0.0
    anuncios_usados = 0

    for ad in orden:
        if ars_acumulado >= monto_ars_objetivo:
            break
        disponible_ars = ad["disponible_unidad"] * ad["precio"]
        tomar_ars = min(disponible_ars, monto_ars_objetivo - ars_acumulado)
        ars_acumulado += tomar_ars
        unidades_acumuladas += tomar_ars / ad["precio"]
        anuncios_usados += 1

    completado = ars_acumulado >= monto_ars_objetivo * 0.999
    precio_promedio = (ars_acumulado / unidades_acumuladas) if unidades_acumuladas else None

    return {
        "precio_promedio": precio_promedio,
        "ars_llenado": ars_acumulado,
        "anuncios_usados": anuncios_usados,
        "completado": completado,
    }


def analizar_activo(activo: str, monto_ars_objetivo: float) -> dict:
    ads_compra = obtener_ads(activo, "SELL")  # gente vendiendo -> vos comprás
    ads_venta = obtener_ads(activo, "BUY")    # gente comprando -> vos vendés

    if not ads_compra or not ads_venta:
        return {"activo": activo, "error": "sin liquidez suficiente en este momento"}

    fill_compra = simular_llenado(ads_compra, monto_ars_objetivo, comprando=True)
    fill_venta = simular_llenado(ads_venta, monto_ars_objetivo, comprando=False)

    if not fill_compra["precio_promedio"] or not fill_venta["precio_promedio"]:
        return {"activo": activo, "error": "sin liquidez suficiente en este momento"}

    gap_pct = (fill_venta["precio_promedio"] / fill_compra["precio_promedio"] - 1) * 100
    ganancia_ars = monto_ars_objetivo * gap_pct / 100

    return {
        "activo": activo,
        "precio_compra": fill_compra["precio_promedio"],
        "precio_venta": fill_venta["precio_promedio"],
        "gap_pct": gap_pct,
        "ganancia_ars": ganancia_ars,
        "anuncios_compra": fill_compra["anuncios_usados"],
        "anuncios_venta": fill_venta["anuncios_usados"],
        "liquidez_completa": fill_compra["completado"] and fill_venta["completado"],
    }


def guardar_historial(resultados: list, monto_usd: float):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    existe = os.path.isfile(HISTORIAL_CSV)
    ahora = datetime.datetime.now()
    with open(HISTORIAL_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["timestamp", "fecha", "hora", "dia_semana", "monto_usd", "activo",
                        "precio_compra", "precio_venta", "gap_pct", "ganancia_ars", "liquidez_completa"])
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        for r in resultados:
            if "error" in r:
                continue
            w.writerow([
                ahora.isoformat(), ahora.strftime("%d/%m/%Y"), ahora.strftime("%H:%M"),
                dias[ahora.weekday()], monto_usd, r["activo"],
                round(r["precio_compra"], 2), round(r["precio_venta"], 2),
                round(r["gap_pct"], 3), round(r["ganancia_ars"], 2), r["liquidez_completa"],
            ])


def simular_vueltas(gap_pct: float, monto_ars: float, monto_usd: float, vueltas_hitos: list) -> None:
    """Compone la brecha observada AHORA a lo largo de N vueltas seguidas,
    reinvirtiendo capital + ganancia cada vez (igual que el caso real que
    analizamos). Es un escenario, no una promesa: asume que la brecha se
    mantiene igual en cada vuelta, lo cual es optimista si se repite el
    mismo monto grande muchas veces seguidas sin que el libro se renueve."""
    factor = 1 + gap_pct / 100
    console.print(f"\n[bold]Escenario: {vueltas_hitos[-1]} vueltas seguidas usando la brecha de HOY ({gap_pct:.3f}%)[/bold]")
    console.print(f"Capital inicial: USD {monto_usd:,.0f} (${monto_ars:,.0f} ARS)\n")

    tabla = Table(title="Capital compuesto vuelta a vuelta (reinvirtiendo todo)")
    tabla.add_column("Vuelta", justify="right")
    tabla.add_column("Capital ARS", justify="right")
    tabla.add_column("Capital USD equiv.", justify="right")
    tabla.add_column("Ganancia acumulada", justify="right")

    capital = monto_ars
    usd_por_ars = monto_usd / monto_ars
    max_hito = max(vueltas_hitos)
    for v in range(1, max_hito + 1):
        capital *= factor
        if v in vueltas_hitos or v == max_hito:
            ganancia_pct = (capital / monto_ars - 1) * 100
            tabla.add_row(
                str(v), f"${capital:,.0f}", f"USD {capital * usd_por_ars:,.0f}",
                f"[green]+{ganancia_pct:.2f}%[/green] (+${capital - monto_ars:,.0f} ARS)",
            )
    console.print(tabla)
    console.print("[yellow]  Ojo: esto asume que la brecha de hoy se mantiene idéntica en cada vuelta. Si repetís el "
                  "mismo monto grande muchas veces seguidas SIN que pase tiempo entre una y otra, en la práctica vas "
                  "comiendo los mismos anuncios baratos y el spread real se va angostando — este número es un techo "
                  "optimista, no un piso garantizado.[/yellow]")


def main():
    parser = argparse.ArgumentParser(description="Scanner multi-activo de oportunidades dentro de Binance P2P")
    parser.add_argument("--monto-usd", type=float, default=10000, help="Monto en USD a simular (default 10.000)")
    parser.add_argument("--activos", default=",".join(ACTIVOS_DEFAULT), help="Lista separada por comas (default USDT,USDC,BTC,ETH,BNB)")
    parser.add_argument("--guardar", action="store_true", help="Loguea el resultado en results/historial_oportunidades.csv")
    parser.add_argument("--simular-vueltas", type=str, default=None,
                         help="Lista de hitos de vueltas a mostrar compuestas, ej. '15,20'. Usa el activo con mejor liquidez real (USDT).")
    args = parser.parse_args()
    activos = [a.strip().upper() for a in args.activos.split(",")]

    console.print(f"\n[bold]Oportunidades dentro de Binance P2P — {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}[/bold]")

    # Referencia dólar->ARS usando USDT (si no está en la lista, la pedimos igual para la conversión)
    ref_ads_compra = obtener_ads("USDT", "SELL")
    ref = simular_llenado(ref_ads_compra, args.monto_usd * 1500, comprando=True)  # aprox inicial
    usdt_ars_ref = ref["precio_promedio"] or 1500
    monto_ars_objetivo = args.monto_usd * usdt_ars_ref

    console.print(f"USD {args.monto_usd:,.0f} ≈ ${monto_ars_objetivo:,.0f} ARS (referencia USDT ${usdt_ars_ref:,.2f})\n")

    resultados = [analizar_activo(a, monto_ars_objetivo) for a in activos]
    resultados_ok = [r for r in resultados if "error" not in r]
    resultados_ok.sort(key=lambda r: r["gap_pct"], reverse=True)

    tabla = Table(title=f"Ranking de brecha intra-Binance simulando USD {args.monto_usd:,.0f}")
    tabla.add_column("Activo", style="cyan")
    tabla.add_column("Precio compra prom.", justify="right")
    tabla.add_column("Precio venta prom.", justify="right")
    tabla.add_column("Brecha %", justify="right")
    tabla.add_column("Ganancia est. ARS", justify="right")
    tabla.add_column("Anuncios necesarios", justify="right")
    tabla.add_column("¿Liquidez alcanza?", justify="center")

    UMBRAL_SOSPECHOSO = 3.0  # % — arriba de esto, casi seguro es libro fino/anuncios poco confiables, no arbitraje real
    for r in resultados_ok:
        if r["gap_pct"] > UMBRAL_SOSPECHOSO:
            color = "red"
        elif r["gap_pct"] > 0.3:
            color = "green"
        elif r["gap_pct"] > 0.1:
            color = "yellow"
        else:
            color = "white"
        etiqueta_liquidez = "✅" if r["liquidez_completa"] else "⚠️ parcial"
        if r["gap_pct"] > UMBRAL_SOSPECHOSO:
            etiqueta_liquidez = "🚩 sospechoso"
        tabla.add_row(
            r["activo"],
            f"${r['precio_compra']:,.2f}",
            f"${r['precio_venta']:,.2f}",
            f"[{color}]{r['gap_pct']:.3f}%[/{color}]",
            f"${r['ganancia_ars']:,.0f}",
            f"{r['anuncios_compra']}+{r['anuncios_venta']}",
            etiqueta_liquidez,
        )
    console.print(tabla)
    if any(r["gap_pct"] > UMBRAL_SOSPECHOSO for r in resultados_ok):
        console.print(f"[red]  🚩 Brechas > {UMBRAL_SOSPECHOSO}% casi nunca son arbitraje real: suele ser libro fino (pocos "
                       f"anuncios, poca profundidad) o anuncios cuyo precio no es realmente ejecutable. Verificar a mano "
                       f"en la app antes de confiar en el número.[/red]")

    for r in resultados:
        if "error" in r:
            console.print(f"[yellow]  {r['activo']}: {r['error']}[/yellow]")

    if resultados_ok:
        mejor = resultados_ok[0]
        console.print(f"\n[bold]Mejor oportunidad ahora:[/bold] {mejor['activo']} — {mejor['gap_pct']:.3f}% "
                       f"(≈${mejor['ganancia_ars']:,.0f} ARS sobre USD {args.monto_usd:,.0f}, "
                       f"necesitando {mejor['anuncios_compra']} anuncios para comprar y {mejor['anuncios_venta']} para vender)")
        if not mejor["liquidez_completa"]:
            console.print("[yellow]  Ojo: la liquidez visible no alcanza a llenar completo el monto — la brecha real sería menor si hay que buscar más anuncios de menor calidad.[/yellow]")

    if args.guardar:
        guardar_historial(resultados, args.monto_usd)
        console.print(f"\n[green]Guardado en {HISTORIAL_CSV}[/green]")

    if args.simular_vueltas:
        hitos = sorted(int(x.strip()) for x in args.simular_vueltas.split(","))
        usdt_r = next((r for r in resultados_ok if r["activo"] == "USDT"), None)
        base = usdt_r if usdt_r else (resultados_ok[0] if resultados_ok else None)
        if base:
            simular_vueltas(base["gap_pct"], monto_ars_objetivo, args.monto_usd, hitos)
        else:
            console.print("[yellow]No hay datos suficientes para simular vueltas.[/yellow]")


if __name__ == "__main__":
    main()
