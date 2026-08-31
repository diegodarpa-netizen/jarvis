"""
Scanner de arbitraje cripto ARS.

Compara el precio de USDT (u otra stablecoin) contra el peso argentino
entre ~20 exchanges/P2P locales (vía la API pública de Criptoya) y,
además, mide el spread DENTRO de Binance P2P (comprar a un anunciante y
vender a otro, sin mover fondos entre plataformas) — que es exactamente
lo que hizo el conocido de Diego con los $11.000.000 ARS.

Dos tipos de oportunidad que reporta, porque NO son comparables en riesgo:

1. Arbitraje INTRA-plataforma (dentro de Binance P2P): comprás a un
   anunciante y vendés a otro, todo en la misma cuenta/plataforma.
   Es rápido (minutos) y sin fricción de red — el tipo de operación
   del ejemplo real (17 vueltas en 2 horas).

2. Arbitraje INTER-plataforma (ej. comprás barato en un exchange y
   vendés caro en otro): exige mover USDT entre exchanges (red
   blockchain, minutos de confirmación) y tener cuenta verificada y
   fondos en ambos lados de antemano. Más lento, más riesgo de precio
   mientras el USDT viaja, pero spreads a veces más anchos.

Uso:
    python scanner_arbitraje.py
    python scanner_arbitraje.py --activo usdc --monto 500000
    python scanner_arbitraje.py --guardar

Fuentes:
    - Criptoya API (agrega exchanges/P2P de Argentina): https://criptoya.com/api
    - Binance P2P (anuncios reales en vivo, endpoint público de la web)
"""
import argparse
import datetime
import json
import os

import requests
from rich.console import Console
from rich.table import Table

CRIPTOYA_URL = "https://criptoya.com/api/{activo}/ars/{volumen}"
BINANCE_P2P_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Plataformas que Criptoya a veces devuelve con datos rotos (ask=0, sin
# liquidez real) o que no son operables de forma directa para este análisis.
EXCLUIR = {"huobip2p"}

console = Console()


def obtener_criptoya(activo: str, volumen: float) -> dict:
    """Trae ask/bid de todos los exchanges que agrega Criptoya para el par
    activo/ARS, al volumen indicado (para reflejar slippage real, no el
    precio de referencia de $1)."""
    url = CRIPTOYA_URL.format(activo=activo, volumen=volumen)
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()

    limpio = {}
    for exch, d in data.items():
        if exch in EXCLUIR:
            continue
        ask = d.get("totalAsk") or d.get("ask")
        bid = d.get("totalBid") or d.get("bid")
        if not ask or not bid or ask <= 0 or bid <= 0:
            continue
        limpio[exch] = {"ask": float(ask), "bid": float(bid)}
    return limpio


def obtener_binance_p2p(activo: str, filas: int = 15) -> dict:
    """Trae los anuncios reales de Binance P2P (compra y venta) para medir
    el spread operable DENTRO de Binance, tal como lo hizo el amigo de
    Diego. tradeType=SELL son anunciantes vendiendo (precio al que VOS
    comprás); tradeType=BUY son anunciantes comprando (precio al que VOS
    vendés)."""
    resultado = {"comprar": [], "vender": []}
    for trade_type, key in [("SELL", "comprar"), ("BUY", "vender")]:
        body = {
            "page": 1, "rows": filas, "payTypes": [], "countries": [],
            "publisherType": None, "asset": activo.upper(), "fiat": "ARS",
            "tradeType": trade_type,
        }
        try:
            r = requests.post(BINANCE_P2P_URL, json=body, headers=HEADERS, timeout=15)
            r.raise_for_status()
            data = r.json().get("data", [])
        except Exception as e:
            console.print(f"[yellow]  aviso: no se pudo traer anuncios Binance P2P ({trade_type}): {e}[/yellow]")
            data = []
        for item in data:
            adv = item["adv"]
            resultado[key].append({
                "precio": float(adv["price"]),
                "min_ars": float(adv["minSingleTransAmount"]),
                "max_ars": float(adv["maxSingleTransAmount"]),
                "disponible_usdt": float(adv["surplusAmount"]),
                "metodos": [m.get("tradeMethodName", "?") for m in adv.get("tradeMethods", [])],
            })
    return resultado


def reporte_inter_plataforma(datos: dict, monto_ars: float) -> dict:
    """Ranking de exchanges por precio y mejor combo compra/venta entre
    DISTINTAS plataformas."""
    tabla = Table(title="Comparativa entre plataformas (comprás en una, vendés en otra)")
    tabla.add_column("Plataforma", style="cyan")
    tabla.add_column("Comprás a (ask)", justify="right")
    tabla.add_column("Vendés a (bid)", justify="right")

    filas_ordenadas = sorted(datos.items(), key=lambda x: x[1]["ask"])
    for exch, d in filas_ordenadas:
        tabla.add_row(exch, f"${d['ask']:,.2f}", f"${d['bid']:,.2f}")
    console.print(tabla)

    mejor_compra = min(datos.items(), key=lambda x: x[1]["ask"])
    mejor_venta = max(datos.items(), key=lambda x: x[1]["bid"])

    exch_compra, d_compra = mejor_compra
    exch_venta, d_venta = mejor_venta
    gap = d_venta["bid"] - d_compra["ask"]
    gap_pct = (gap / d_compra["ask"]) * 100

    console.print("\n[bold]Mejor combinación inter-plataforma:[/bold]")
    if exch_compra == exch_venta:
        console.print(f"  La misma plataforma ({exch_compra}) tiene el mejor ask Y el mejor bid — no hay arbitraje inter-plataforma real, mirá el spread intra-plataforma.")
    else:
        console.print(f"  Comprar en [cyan]{exch_compra}[/cyan] a ${d_compra['ask']:,.2f} y vender en [cyan]{exch_venta}[/cyan] a ${d_venta['bid']:,.2f}")
        console.print(f"  Brecha bruta: ${gap:,.2f} ({gap_pct:.2f}%) — [yellow]sin descontar fee de red por mover USDT entre exchanges ni el tiempo de confirmación[/yellow]")

    return {
        "mejor_compra": {"exchange": exch_compra, "ask": d_compra["ask"]},
        "mejor_venta": {"exchange": exch_venta, "bid": d_venta["bid"]},
        "gap_ars": gap,
        "gap_pct": gap_pct,
    }


def reporte_intra_binance(ads: dict, monto_ars: float) -> dict:
    """Spread operable DENTRO de Binance P2P, replicando la operatoria del
    ejemplo real: comprar a un anunciante y vender a otro."""
    compras = [a for a in ads["comprar"] if a["min_ars"] <= monto_ars <= a["max_ars"]]
    ventas = [a for a in ads["vender"] if a["min_ars"] <= monto_ars <= a["max_ars"]]

    tabla = Table(title=f"Binance P2P — anuncios que aceptan ~${monto_ars:,.0f} ARS por vuelta")
    tabla.add_column("Lado", style="cyan")
    tabla.add_column("Precio", justify="right")
    tabla.add_column("Límite ARS", justify="right")
    tabla.add_column("Métodos de pago")

    for a in sorted(compras, key=lambda x: x["precio"])[:5]:
        tabla.add_row("Comprás a", f"${a['precio']:,.2f}", f"${a['min_ars']:,.0f}–${a['max_ars']:,.0f}", ", ".join(a["metodos"]))
    for a in sorted(ventas, key=lambda x: -x["precio"])[:5]:
        tabla.add_row("Vendés a", f"${a['precio']:,.2f}", f"${a['min_ars']:,.0f}–${a['max_ars']:,.0f}", ", ".join(a["metodos"]))
    console.print(tabla)

    if not compras or not ventas:
        console.print(f"[yellow]  No hay anuncios que acepten un monto de ${monto_ars:,.0f} ARS por vuelta en este momento (ajustá --monto).[/yellow]")
        return {}

    mejor_compra = min(compras, key=lambda x: x["precio"])
    mejor_venta = max(ventas, key=lambda x: x["precio"])
    gap = mejor_venta["precio"] - mejor_compra["precio"]
    gap_pct = (gap / mejor_compra["precio"]) * 100

    console.print("\n[bold]Mejor combinación intra-Binance (comprar y vender dentro de la misma plataforma):[/bold]")
    console.print(f"  Comprás a ${mejor_compra['precio']:,.2f} → vendés a ${mejor_venta['precio']:,.2f}")
    console.print(f"  Brecha: ${gap:,.2f} ({gap_pct:.2f}%) por vuelta, sin mover fondos entre exchanges")

    return {
        "mejor_compra": mejor_compra["precio"],
        "mejor_venta": mejor_venta["precio"],
        "gap_ars": gap,
        "gap_pct": gap_pct,
    }


def main():
    parser = argparse.ArgumentParser(description="Scanner de arbitraje cripto ARS")
    parser.add_argument("--activo", default="usdt", help="Stablecoin/activo a comparar (usdt, usdc, dai...)")
    parser.add_argument("--monto", type=float, default=500000, help="Monto ARS de referencia por vuelta (default 500.000)")
    parser.add_argument("--guardar", action="store_true", help="Guarda el resultado como JSON en results/")
    args = parser.parse_args()

    volumen_usdt = round(args.monto / 1500)  # aprox, solo para pedir profundidad de libro representativa

    console.print(f"\n[bold]Scanner de arbitraje — {args.activo.upper()}/ARS — {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}[/bold]")
    console.print(f"Monto de referencia por vuelta: ${args.monto:,.0f} ARS\n")

    console.print("[bold]1) Comparando entre plataformas (Criptoya)...[/bold]")
    datos_criptoya = obtener_criptoya(args.activo, volumen_usdt)
    inter = reporte_inter_plataforma(datos_criptoya, args.monto) if datos_criptoya else {}

    console.print("\n[bold]2) Comparando anuncios reales dentro de Binance P2P...[/bold]")
    ads = obtener_binance_p2p(args.activo)
    intra = reporte_intra_binance(ads, args.monto)

    console.print("\n[bold underline]Veredicto[/bold underline]")
    veredicto = []
    if intra.get("gap_pct", 0) > 0.3:
        veredicto.append(f"Hay brecha intra-Binance operable ahora: {intra['gap_pct']:.2f}% por vuelta (el ejemplo real fue ~0,4-0,6%).")
    elif intra:
        veredicto.append(f"Brecha intra-Binance chica en este momento ({intra['gap_pct']:.2f}%) — no da para operar con margen cómodo.")
    if inter.get("gap_pct", 0) > 0.5 and inter.get("mejor_compra", {}).get("exchange") != inter.get("mejor_venta", {}).get("exchange"):
        veredicto.append(f"Hay brecha inter-plataforma de {inter['gap_pct']:.2f}%, pero requiere mover fondos entre exchanges (riesgo de precio + tiempo de red).")
    if not veredicto:
        veredicto.append("Sin oportunidades claras en este momento con los datos disponibles.")
    for v in veredicto:
        console.print(f"  • {v}")

    if args.guardar:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        fname = os.path.join(RESULTS_DIR, f"scan_{args.activo}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.datetime.now().isoformat(),
                "activo": args.activo,
                "monto_ars": args.monto,
                "inter_plataforma": inter,
                "intra_binance": intra,
                "criptoya_raw": datos_criptoya,
            }, f, ensure_ascii=False, indent=2)
        console.print(f"\n[green]Guardado en {fname}[/green]")


if __name__ == "__main__":
    main()
