"""
Rastrea contenido viral de cirugía plástica en redes sociales.
Identifica patrones en videos y posts que generan alto engagement.
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


def save_knowledge(kb):
    KNOWLEDGE_PATH.write_text(json.dumps(kb, indent=2, ensure_ascii=False))


def track_viral_content():
    config = load_config()
    kb = load_knowledge()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    procedures = config["clinic"]["procedures"]
    hashtags = config["tracking"]["viral_hashtags"]

    print("🎬 Rastreando contenido viral en cirugía plástica...")

    research_queries = [
        "videos virales transformacion rinoplastia liposuccion Instagram Reels 2025 2026 que elementos tienen en comun",
        "formato antes y despues cirugia plastica que funciona mejor Instagram TikTok estructura narrativa",
        "testimonios videos pacientes cirugia estetica Argentina qué genera mas engagement y confianza",
        "hooks virales primeros 3 segundos videos cirugia plastica que detiene el scroll",
        "tendencias contenido medico estetico redes sociales 2026 que esta funcionando ahora",
        "influencers micro nano cirugia plastica Argentina colaboraciones estrategia contenido",
    ]

    viral_patterns = []

    for query in research_queries:
        print(f"  → Analizando: {query[:55]}...")
        patterns_text = web_search_query(
            query=f"""Buscá información real y actual, y luego investigá y analizá: {query}

Contexto: Clínica en Buenos Aires, procedimientos: {', '.join(procedures)}.
Target: Mujeres 22-45 años, Buenos Aires y GBA.

Dame:
1. Patrón específico que hace viral este tipo de contenido
2. Estructura exacta del video/post (qué va primero, segundo, tercero)
3. Ejemplo concreto de un hook o frase que funciona
4. Duración y formato ideal
5. Cómo adaptarlo a nuestra clínica
""",
            system="""Eres un experto en contenido viral para clínicas de cirugía estética.
Conoces en profundidad qué hace que un video o post explote en Instagram, TikTok y Facebook.
Te especializas en el mercado argentino/latinoamericano y entiendes la psicología del paciente potencial.
Usá la herramienta de búsqueda web para verificar tendencias reales antes de responder — no respondas de memoria.
Das consejos extremadamente específicos y accionables, no generalidades.""",
            max_tokens=1500,
        )

        pattern = {
            "query": query,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "patterns": patterns_text
        }
        viral_patterns.append(pattern)

    # Generate viral content playbook
    print("\n📋 Generando playbook de contenido viral...")
    playbook_response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""Basándote en estos análisis de contenido viral para cirugía plástica:

{chr(10).join([f"ANÁLISIS:{chr(10)}{p['patterns'][:400]}" for p in viral_patterns[:4]])}

Crea un PLAYBOOK DE CONTENIDO VIRAL con:

## 🎬 Los 5 Formatos de Video que Más Convierten
(para cada uno: estructura exacta, duración, hook de apertura, CTA)

## 📱 Calendario de Contenido Semanal
(qué publicar cada día, tipo de contenido, hora ideal)

## 🪝 Banco de Hooks Virales
(15 frases de apertura para los primeros 3 segundos)

## 📊 Métricas que Indican que un Video Va a Viral
(qué señales mirar en las primeras 2 horas)

## ⚡ Ideas de Contenido para Esta Semana
(5 videos concretos listos para producir)
"""
        }]
    )

    # Update knowledge base
    kb["viral_content_patterns"].extend(viral_patterns[-5:])
    if len(kb["viral_content_patterns"]) > 30:
        kb["viral_content_patterns"] = kb["viral_content_patterns"][-30:]
    kb["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_knowledge(kb)

    # Save report
    REPORTS_PATH.mkdir(exist_ok=True)
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORTS_PATH / f"viral_content_{report_date}.md"
    report_path.write_text(f"""# Playbook Contenido Viral - {report_date}
## Cirugía Plástica Buenos Aires

{playbook_response.content[0].text}

---
*Generado por Jarvis Marketing Agent*
""", encoding="utf-8")

    print(f"\n✅ Playbook guardado en: {report_path}")
    print("\n" + "="*60)
    print(playbook_response.content[0].text)
    return playbook_response.content[0].text


if __name__ == "__main__":
    track_viral_content()
