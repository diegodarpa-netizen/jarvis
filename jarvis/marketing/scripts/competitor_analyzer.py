"""
Analiza competidores en Meta Ad Library y web.
Busca anuncios activos, creatividades y estrategias de cirugía plástica en Argentina.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Support running from any directory
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import anthropic

from web_research import web_search_query

CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"
KNOWLEDGE_PATH = Path(__file__).parent.parent / "data" / "knowledge_base.json"
REPORTS_PATH = Path(__file__).parent.parent / "reports"


def load_config():
    return json.loads(CONFIG_PATH.read_text())


def load_knowledge():
    return json.loads(KNOWLEDGE_PATH.read_text())


def save_knowledge(kb):
    KNOWLEDGE_PATH.write_text(json.dumps(kb, indent=2, ensure_ascii=False))


def analyze_competitors():
    config = load_config()
    kb = load_knowledge()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    keywords = config["competitors_keywords"]
    procedures = config["clinic"]["procedures"]

    print("🔍 Analizando competidores en cirugía plástica - Buenos Aires...")

    # Build search queries for Meta Ad Library and general web
    search_tasks = [
        f"Meta Ad Library anuncios activos cirugía plástica Buenos Aires 2026",
        f"mejores anuncios Instagram cirugía estética Argentina creatividades virales",
        f"estrategias marketing digital clínicas cirugía plástica Argentina 2025 2026",
        f"competidores cirugía plástica Buenos Aires publicidad Instagram Facebook",
        f"copy publicitario rinoplastia liposuccion mamoplastia Argentina que funciona",
    ]

    all_insights = []

    for task in search_tasks:
        print(f"  → Investigando: {task[:60]}...")
        analysis_text = web_search_query(
            query=f"""Buscá información real y actual, y luego analizá y dame insights sobre: {task}

Contexto: Clínica de cirugía plástica en Buenos Aires, procedimientos principales: {', '.join(procedures)}.
Budget Meta: $500-2000 USD/mes. Target: mujeres 22-45 años, Buenos Aires y GBA.

Dame:
1. Qué están haciendo los competidores exitosos
2. Qué formatos de anuncio funcionan mejor
3. Qué copy/mensajes son más efectivos
4. Recomendación concreta que puedo implementar HOY
""",
            system="""Eres un experto en marketing digital para clínicas de cirugía plástica en Argentina.
Tu objetivo es analizar la competencia y extraer insights accionables sobre:
- Qué tipo de anuncios están usando los competidores
- Qué mensajes/copy resuena mejor con la audiencia
- Qué creatividades (videos/imágenes) generan más engagement
- Qué estrategias de targeting usan en Meta
- Qué ofertas o ganchos usan para captar leads
Usá la herramienta de búsqueda web para verificar esta información antes de responder — no respondas de memoria.
Sé específico, práctico y orientado a resultados.""",
            max_tokens=2000,
        )

        insight = {
            "query": task,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "analysis": analysis_text
        }
        all_insights.append(insight)

    # Update knowledge base
    kb["competitor_insights"].extend(all_insights[-10:])  # Keep last 10 per run
    if len(kb["competitor_insights"]) > 50:
        kb["competitor_insights"] = kb["competitor_insights"][-50:]
    kb["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Generate executive summary
    summary_response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""Basándote en estos análisis de competidores para cirugía plástica en Buenos Aires:

{chr(10).join([f"ANÁLISIS {i+1}:{chr(10)}{ins['analysis'][:500]}" for i, ins in enumerate(all_insights)])}

Genera un RESUMEN EJECUTIVO con:
## Top 3 hallazgos sobre la competencia
## Oportunidades detectadas (qué NO están haciendo bien)
## 5 acciones concretas para implementar esta semana en Meta Ads
## Tipo de contenido viral que está funcionando en el rubro
"""
        }]
    )

    save_knowledge(kb)

    # Save report
    REPORTS_PATH.mkdir(exist_ok=True)
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORTS_PATH / f"competitors_{report_date}.md"
    report_path.write_text(f"""# Análisis de Competidores - {report_date}
## Cirugía Plástica Buenos Aires

{summary_response.content[0].text}

---
*Generado por Jarvis Marketing Agent*
""", encoding="utf-8")

    print(f"\n✅ Análisis guardado en: {report_path}")
    print("\n" + "="*60)
    print(summary_response.content[0].text)
    return summary_response.content[0].text


if __name__ == "__main__":
    analyze_competitors()
