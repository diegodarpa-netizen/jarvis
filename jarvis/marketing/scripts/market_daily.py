"""
Briefing diario de mercado de marketing para cirugía plástica.
Analiza tendencias, noticias del sector y oportunidades del día.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

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


def generate_daily_briefing():
    config = load_config()
    kb = load_knowledge()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    today = datetime.now().strftime("%Y-%m-%d")
    day_of_week = datetime.now().strftime("%A")
    month = datetime.now().strftime("%B")
    procedures = config["clinic"]["procedures"]

    print(f"📰 Generando briefing diario de marketing - {today}...")

    # Gather daily market intelligence
    daily_queries = [
        f"tendencias marketing cirugia plastica estetica Argentina {month} 2026 que esta pasando ahora",
        f"actualizaciones algoritmo Instagram Facebook 2026 como impactan publicidad medica estetica",
        f"demanda procedimientos esteticos Argentina temporada {month} comportamiento consumidor",
        f"noticias sector cirugia plastica Argentina 2026 regulaciones tendencias mercado",
    ]

    daily_insights = []
    for query in daily_queries:
        print(f"  → {query[:55]}...")
        insight = web_search_query(
            query=f"Buscá información real y actual sobre: {query}\nDame 2-3 puntos clave con su implicancia práctica para una clínica de Buenos Aires, citando qué encontraste.",
            system="""Eres el analista de marketing de una clínica de cirugía plástica en Buenos Aires.
Cada mañana preparas un briefing ejecutivo con la información más relevante del mercado.
Usá la herramienta de búsqueda web para verificar datos reales y actuales antes de responder — no respondas de memoria.
Eres directo, práctico y siempre terminas cada punto con una implicancia accionable para hoy.""",
            max_tokens=800,
        )
        daily_insights.append(insight)

    # Generate the full daily briefing
    print("\n📋 Compilando briefing completo...")

    # Load recent learnings from knowledge base
    recent_insights = kb.get("learned_insights", [])[-5:]
    recent_context = "\n".join([f"- {i}" for i in recent_insights]) if recent_insights else "Sin aprendizajes previos aún."

    briefing_response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2500,
        messages=[{
            "role": "user",
            "content": f"""Genera el BRIEFING DIARIO DE MARKETING para hoy {today} ({day_of_week}).
Clínica de cirugía plástica en Buenos Aires. Procedimientos: {', '.join(procedures)}.

Información recopilada hoy:
{chr(10).join([f"INSIGHT {i+1}:{chr(10)}{ins}" for i, ins in enumerate(daily_insights)])}

Aprendizajes acumulados anteriores:
{recent_context}

Crea el briefing con este formato:

# 📊 BRIEFING MARKETING - {today}

## 🌡️ Temperatura del Mercado
(cómo está el mercado hoy - caliente/tibio/frío y por qué)

## 📈 Tendencias del Día
(2-3 tendencias específicas relevantes para hoy)

## 🎯 Foco de Hoy en Meta Ads
(qué procedimiento priorizar hoy y por qué - basado en temporada/tendencias)

## 📱 Idea de Contenido Urgente
(1 video o post que deberías publicar HOY con su estructura)

## ⚡ Acciones Concretas para Hoy
(lista de 3-5 cosas a hacer hoy mismo en marketing)

## 💡 Insight Aprendido
(1 cosa nueva que aprendemos hoy y cómo cambia nuestra estrategia)

## 🔮 Predicción de la Semana
(qué esperar en los próximos 7 días en el mercado)
"""
        }]
    )

    briefing_text = briefing_response.content[0].text

    # Extract and save the learned insight
    lines = briefing_text.split("\n")
    insight_section = False
    learned_today = ""
    for line in lines:
        if "## 💡 Insight Aprendido" in line:
            insight_section = True
            continue
        if insight_section and line.startswith("##"):
            break
        if insight_section and line.strip():
            learned_today += line.strip() + " "

    if learned_today:
        kb["learned_insights"].append(f"[{today}] {learned_today[:200]}")
        if len(kb["learned_insights"]) > 30:
            kb["learned_insights"] = kb["learned_insights"][-30:]

    kb["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    KNOWLEDGE_PATH.write_text(json.dumps(kb, indent=2, ensure_ascii=False))

    # Save report
    REPORTS_PATH.mkdir(exist_ok=True)
    report_path = REPORTS_PATH / f"daily_briefing_{today}.md"
    report_path.write_text(briefing_text, encoding="utf-8")

    print(f"\n✅ Briefing guardado en: {report_path}")
    print("\n" + "="*60)
    print(briefing_text)
    return briefing_text


if __name__ == "__main__":
    generate_daily_briefing()
