"""
Jarvis - Deep Research
Estructura búsquedas web profundas para que Claude las ejecute con su herramienta WebSearch.
Este script genera los queries óptimos para investigar un tema financiero.
Claude ejecuta las búsquedas y sintetiza los resultados.

Uso: python deep_research.py --topic "NVDA earnings Q1 2025" [--type company|macro|sector|news]
     python deep_research.py --ticker AAPL --type company
"""

import argparse
import json
import sys
from datetime import datetime


def build_company_queries(ticker: str, company_name: str = "") -> list:
    name = company_name or ticker
    return [
        f"{ticker} {name} latest earnings results revenue guidance",
        f"{ticker} analyst upgrade downgrade price target 2025",
        f"{ticker} {name} news today site:reuters.com OR site:bloomberg.com OR site:wsj.com",
        f"{name} competitive landscape market share {datetime.now().year}",
        f"{ticker} SEC filing 10-K 10-Q risk factors",
        f"{name} CEO strategy outlook investor day",
        f"{ticker} short interest institutional ownership changes"
    ]


def build_macro_queries(topic: str) -> list:
    return [
        f"{topic} Federal Reserve policy impact",
        f"{topic} economic data GDP inflation unemployment",
        f"{topic} site:federalreserve.gov OR site:bls.gov OR site:census.gov",
        f"{topic} analyst forecast Wall Street outlook {datetime.now().year}",
        f"{topic} emerging markets developing countries impact",
        f"US Treasury yield curve {topic} bond market"
    ]


def build_sector_queries(sector: str) -> list:
    return [
        f"{sector} sector ETF performance YTD {datetime.now().year}",
        f"{sector} industry trends disruption growth drivers",
        f"best stocks {sector} sector analyst picks {datetime.now().year}",
        f"{sector} sector earnings season results surprises",
        f"{sector} regulation policy headwinds tailwinds",
        f"{sector} sector valuation multiples historical comparison"
    ]


def build_news_queries(topic: str) -> list:
    return [
        f"{topic} breaking news today",
        f"{topic} market reaction impact stocks",
        f"{topic} site:reuters.com OR site:ft.com OR site:cnbc.com",
        f"{topic} expert analysis opinion",
        f"{topic} historical precedent comparison"
    ]


RESEARCH_TEMPLATES = {
    "company": {
        "label": "Análisis de empresa",
        "instructions": """
Ejecutá cada query de búsqueda web en orden. Para cada resultado:
1. Extraé los datos clave (números, fechas, declaraciones importantes)
2. Identificá si es bullish, bearish o neutral para la acción
3. Anotá la fuente y fecha

Al terminar, sintetizá en estas secciones:
- **Últimos resultados financieros**: revenue, earnings, guidance
- **Posicionamiento de analistas**: targets, recomendaciones recientes
- **Catalizadores**: eventos próximos, productos, contratos
- **Riesgos identificados**: competencia, regulación, macro
- **Sentimiento general**: alcista / bajista / neutral + fundamento
""".strip()
    },
    "macro": {
        "label": "Análisis macroeconómico",
        "instructions": """
Ejecutá cada query de búsqueda web en orden. Para cada resultado:
1. Extraé los datos económicos clave y sus variaciones
2. Identificá el impacto en mercados de renta variable y fija
3. Anotá consenso de economistas vs datos reales

Al terminar, sintetizá en:
- **Estado actual**: datos más recientes del indicador/tema
- **Tendencia**: dirección y velocidad del cambio
- **Impacto en mercados**: acciones, bonos, dólar, commodities
- **Fed/política monetaria**: implicancias para tasas
- **Oportunidades y riesgos** para el portfolio de Diego
""".strip()
    },
    "sector": {
        "label": "Análisis de sector",
        "instructions": """
Ejecutá cada query de búsqueda web en orden. Para cada resultado:
1. Identificá los líderes y rezagados del sector
2. Extraé múltiplos de valuación comparativos
3. Notá las tendencias estructurales (AI, regulación, demanda)

Al terminar, sintetizá en:
- **Performance reciente**: vs S&P 500, vs otros sectores
- **Tesis de inversión**: por qué invertir (o no) en este sector ahora
- **Top picks**: 3-5 acciones del sector más atractivas con fundamento
- **Riesgos del sector**: headwinds específicos
""".strip()
    },
    "news": {
        "label": "Investigación de noticia/evento",
        "instructions": """
Ejecutá cada query en orden. Para cada resultado:
1. Verificá la veracidad y fuentes de la noticia
2. Identificá el alcance real del evento (no solo el titular)
3. Buscá reacciones iniciales del mercado

Al terminar, sintetizá en:
- **Qué pasó exactamente**: hechos concretos sin interpretación
- **Impacto en mercados**: movimientos y sectores afectados
- **Perspectiva de corto plazo**: próximos 1-5 días
- **Perspectiva estructural**: si cambia algo de fondo
- **Acción recomendada** para el portfolio de Diego
""".strip()
    }
}


def main():
    parser = argparse.ArgumentParser(description="Jarvis Deep Research Query Builder")
    parser.add_argument("--topic", help="Tema a investigar (texto libre)")
    parser.add_argument("--ticker", help="Ticker de empresa")
    parser.add_argument("--type", choices=["company", "macro", "sector", "news"],
                        default="company", dest="research_type")
    args = parser.parse_args()

    if not args.topic and not args.ticker:
        print("ERROR: Especificá --topic o --ticker", file=sys.stderr)
        sys.exit(1)

    topic = args.topic or args.ticker
    research_type = args.research_type

    if args.ticker and research_type == "company":
        queries = build_company_queries(args.ticker, args.topic or "")
    elif research_type == "macro":
        queries = build_macro_queries(topic)
    elif research_type == "sector":
        queries = build_sector_queries(topic)
    else:
        queries = build_news_queries(topic)

    template = RESEARCH_TEMPLATES[research_type]

    result = {
        "research_topic": topic,
        "research_type": research_type,
        "label": template["label"],
        "generated_at": datetime.utcnow().isoformat(),
        "total_queries": len(queries),
        "queries": queries,
        "synthesis_instructions": template["instructions"],
        "note": "Claude ejecuta estos queries con WebSearch y sintetiza los resultados según las instrucciones."
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
