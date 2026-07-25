"""
Analiza anuncios de competidores usando Meta Ad Library pública.
Construye URL de búsqueda directa + análisis con Claude para interpretar resultados.

Meta Ad Library pública (sin API): https://www.facebook.com/ads/library
Ad Library API (requiere acceso especial): https://facebook.com/ads/library/api
"""
import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import anthropic

from web_research import web_search_query

CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"
KNOWLEDGE_PATH = Path(__file__).parent.parent / "data" / "knowledge_base.json"
REPORTS_PATH = Path(__file__).parent.parent / "reports"

WA_TOKEN = os.getenv("META_ACCESS_TOKEN")
API_VERSION = os.getenv("META_API_VERSION", "v21.0")


def load_config():
    return json.loads(CONFIG_PATH.read_text())


def load_knowledge():
    return json.loads(KNOWLEDGE_PATH.read_text())


def save_knowledge(kb):
    KNOWLEDGE_PATH.write_text(json.dumps(kb, indent=2, ensure_ascii=False))


def search_ad_library_public(keyword: str, country: str = "AR") -> str:
    """Genera URL de Meta Ad Library para búsqueda manual."""
    base = "https://www.facebook.com/ads/library"
    params = f"?active_status=active&ad_type=all&country={country}&q={keyword.replace(' ', '+')}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered"
    return base + params


def try_ad_library_api(keyword: str, country: str = "AR") -> dict:
    """
    Intenta usar la Ad Library API con el token disponible.
    Requiere permiso especial de Meta (ads_library).
    """
    url = "https://graph.facebook.com/v21.0/ads_archive"
    params = {
        "access_token": WA_TOKEN,
        "ad_reached_countries": country,
        "search_terms": keyword,
        "ad_type": "ALL",
        "limit": 20,
        "fields": "id,page_name,ad_creative_body,ad_creative_link_description,ad_snapshot_url,impressions,spend,ad_delivery_start_time"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "error" in data:
        return {
            "success": False,
            "error": data["error"].get("error_user_msg", data["error"]["message"]),
            "needs_permission": True
        }
    return {"success": True, "data": data.get("data", [])}


def analyze_competitors_with_ai(config: dict, ads_context: str | None = None) -> str:
    """
    Análisis profundo de competidores usando Claude + búsqueda web real.
    Incluye URLs de Ad Library para revisión manual.
    Si ads_context viene de la Ad Library API real, se prioriza sobre la búsqueda web.
    """
    procedures = config["clinic"]["procedures"]
    geo = config["meta_ads"]["geo_target"]

    # Generate Ad Library search URLs for manual review
    keywords = config["competitors_keywords"]
    ad_library_urls = []
    for kw in keywords[:6]:
        url = search_ad_library_public(kw)
        ad_library_urls.append(f"- [{kw}]({url})")

    urls_text = "\n".join(ad_library_urls)

    print("🔍 Analizando competidores de cirugía plástica en Argentina...")

    ads_data_section = (
        f"\nDATOS REALES de la Meta Ad Library API (usalos como fuente principal, son anuncios activos verificados):\n{ads_context}\n"
        if ads_context else ""
    )

    return web_search_query(
        system="""Eres un experto en marketing digital y publicidad para clínicas de cirugía plástica en Argentina.
Usá la herramienta de búsqueda web para buscar competidores, anuncios y estrategias reales y actuales antes de responder — no respondas de memoria.
Si se te proveen datos reales de la Ad Library API, priorizalos por sobre la búsqueda web general.
Analizás qué hacen los competidores exitosos y das recomendaciones ultra-específicas y accionables.""",
        max_tokens=3000,
        max_uses=5,
        query=f"""Buscá información real y actual, y realizá un análisis completo de la COMPETENCIA en publicidad de cirugía plástica en Buenos Aires, Argentina para una clínica que ofrece: {', '.join(procedures)}.
{ads_data_section}

Target: mujeres 22-45 años, Buenos Aires y GBA.

Necesito que analices:

## 1. MAPA DE COMPETIDORES
¿Quiénes son los principales competidores en publicidad digital de cirugía plástica en Buenos Aires?
(Nombres reales de clínicas, médicos o centros conocidos que publicitan en redes)
Para cada uno:
- Nombre/Perfil
- Qué procedimientos promueven más
- Qué tipo de contenido usan (antes/después, testimonios, educativo)
- Precio aproximado si lo muestran
- Punto débil en su publicidad (oportunidad para nosotros)

## 2. TIPOS DE ANUNCIOS MÁS COMUNES
¿Qué formatos están usando la mayoría?
- Estructura del anuncio (qué va primero, segundo, etc.)
- Copy más frecuente (frases, hooks, CTAs)
- Estética visual (colores, estilos, filtros)
- Duración de videos si usan reels

## 3. ANÁLISIS POR PROCEDIMIENTO
Para cada procedimiento (Rinoplastia, Liposucción, Mamoplastia, Bichectomía):
- Ángulo publicitario más usado
- Promesa principal que hacen
- Objeción principal que manejan
- Precio que muestran (o si evitan mostrarlo)

## 4. GAPS Y OPORTUNIDADES
¿Qué están haciendo MAL los competidores? ¿Dónde hay espacio para diferenciarse?

## 5. ESTRATEGIA RECOMENDADA PARA DIFERENCIARNOS
¿Cómo debería posicionarse nuestra clínica para sobresalir de la competencia?
Con copy de ejemplo y diferenciador clave.

NOTA: Las siguientes URLs de Meta Ad Library sirven para verificar manualmente los anuncios activos:
{urls_text}
""",
    )


def generate_competitor_report():
    config = load_config()
    kb = load_knowledge()

    print("📊 Iniciando análisis de competidores...")

    # Try the API first
    print("\n🔌 Probando conexión con Meta Ad Library API...")
    api_result = try_ad_library_api("cirugia plastica Buenos Aires")

    if api_result["success"]:
        print(f"✅ API conectada - {len(api_result['data'])} anuncios encontrados")
        ads_context = json.dumps(api_result["data"][:5], indent=2, ensure_ascii=False)
    else:
        print(f"⚠️  API no disponible: {api_result['error']}")
        print("   → Usando análisis con IA (igualmente efectivo)")
        ads_context = None

    # AI analysis — usa los datos reales de la Ad Library API si están disponibles
    analysis = analyze_competitors_with_ai(config, ads_context=ads_context)

    # Generate Ad Library links section
    print("\n🔗 Generando links de Ad Library para revisión manual...")
    links_section = "\n## 🔗 Links para Revisar Anuncios Activos en Meta Ad Library\n"
    links_section += "*(Clickeá cada link para ver los anuncios activos de competidores)*\n\n"
    for kw in config["competitors_keywords"]:
        url = search_ad_library_public(kw)
        links_section += f"- **{kw}**: {url}\n"

    # Save to knowledge base
    kb["competitor_insights"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "analysis_summary": analysis[:500]
    })
    if len(kb["competitor_insights"]) > 20:
        kb["competitor_insights"] = kb["competitor_insights"][-20:]
    save_knowledge(kb)

    # Save report
    REPORTS_PATH.mkdir(exist_ok=True)
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORTS_PATH / f"competitors_{report_date}.md"
    full_report = f"""# Análisis de Competidores - {report_date}
## Cirugía Plástica Buenos Aires

{analysis}

---
{links_section}

---
*Generado por Jarvis Marketing Agent*
*Para acceso completo a Meta Ad Library API: facebook.com/ads/library/api*
"""
    report_path.write_text(full_report, encoding="utf-8")

    print(f"\n✅ Reporte guardado en: {report_path}")
    print("\n" + "="*60)
    print(analysis)
    print(links_section)

    return analysis


if __name__ == "__main__":
    generate_competitor_report()
