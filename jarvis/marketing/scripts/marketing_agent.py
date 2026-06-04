"""
Agente principal de marketing. Orquesta todos los módulos y permite
interacción conversacional para análisis y estrategia de marketing.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import anthropic

CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"
KNOWLEDGE_PATH = Path(__file__).parent.parent / "data" / "knowledge_base.json"
REPORTS_PATH = Path(__file__).parent.parent / "reports"


def load_config():
    return json.loads(CONFIG_PATH.read_text())


def load_knowledge():
    return json.loads(KNOWLEDGE_PATH.read_text())


def get_knowledge_summary(kb):
    """Build a context summary from accumulated knowledge."""
    summary_parts = []

    if kb.get("learned_insights"):
        recent = kb["learned_insights"][-10:]
        summary_parts.append("APRENDIZAJES ACUMULADOS:\n" + "\n".join(f"- {i}" for i in recent))

    if kb.get("meta_strategies"):
        summary_parts.append(f"Estrategias Meta analizadas: {len(kb['meta_strategies'])}")

    if kb.get("viral_content_patterns"):
        summary_parts.append(f"Patrones de contenido viral documentados: {len(kb['viral_content_patterns'])}")

    if kb.get("competitor_insights"):
        summary_parts.append(f"Análisis de competidores: {len(kb['competitor_insights'])}")

    return "\n".join(summary_parts) if summary_parts else "Base de conocimiento vacía - ejecuta los módulos de análisis primero."


def run_interactive_agent():
    config = load_config()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    print("=" * 60)
    print("🏥 JARVIS - AGENTE DE MARKETING CIRUGÍA PLÁSTICA")
    print("=" * 60)
    print("Clínica: Buenos Aires | Presupuesto Meta: $500-2000 USD/mes")
    print("Procedimientos: Rinoplastia, Liposucción, Mamoplastia, Facial")
    print()
    print("Comandos especiales:")
    print("  /competidores  → Análisis de competidores")
    print("  /viral         → Playbook de contenido viral")
    print("  /meta          → Blueprint de Meta Ads")
    print("  /daily         → Briefing diario de mercado")
    print("  /aprendizajes  → Ver lo que hemos aprendido")
    print("  /salir         → Terminar")
    print("=" * 60)

    kb = load_knowledge()
    knowledge_context = get_knowledge_summary(kb)

    conversation_history = []

    system_prompt = f"""Eres el Agente de Marketing especializado en cirugía plástica de la clínica de Diego en Buenos Aires.

CONTEXTO DE LA CLÍNICA:
- Ubicación: Buenos Aires, Argentina
- Procedimientos principales: Rinoplastia, Liposucción, Lipoescultura, Mamoplastia, Bichectomía
- Presupuesto Meta Ads: $500-2000 USD/mes
- Plataforma principal: Instagram + Facebook
- Target: Mujeres 22-45 años, Buenos Aires y GBA

BASE DE CONOCIMIENTO ACUMULADA:
{knowledge_context}

TU ROL:
- Eres un experto en marketing digital para clínicas de cirugía plástica
- Conoces Meta Ads (Facebook/Instagram) en profundidad
- Entiendes la psicología del paciente potencial de cirugía estética
- Sabes qué contenido viral funciona en el rubro
- Conoces las mejores estrategias de los competidores
- Aprendes de cada conversación y mejoras las recomendaciones

ESTILO:
- Directo y práctico, sin vueltas
- Siempre termina con acciones concretas
- Cuando no tenés datos exactos, lo decís y das la mejor alternativa
- Recordá las cosas que Diego te dice y aplicalas
"""

    while True:
        user_input = input("\n💬 Vos: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "/salir":
            print("\n👋 Hasta luego! Tus aprendizajes fueron guardados.")
            break

        # Handle special commands
        if user_input.lower() == "/competidores":
            print("\n🔍 Ejecutando análisis de competidores...")
            from competitor_analyzer import analyze_competitors
            analyze_competitors()
            continue

        elif user_input.lower() == "/viral":
            print("\n🎬 Generando playbook de contenido viral...")
            from viral_tracker import track_viral_content
            track_viral_content()
            continue

        elif user_input.lower() == "/meta":
            print("\n📊 Generando blueprint de Meta Ads...")
            from meta_optimizer import generate_meta_strategy
            generate_meta_strategy()
            continue

        elif user_input.lower() == "/daily":
            print("\n📰 Generando briefing diario...")
            from market_daily import generate_daily_briefing
            generate_daily_briefing()
            continue

        elif user_input.lower() == "/aprendizajes":
            kb = load_knowledge()
            insights = kb.get("learned_insights", [])
            if insights:
                print("\n📚 LO QUE HEMOS APRENDIDO:")
                for i, insight in enumerate(insights, 1):
                    print(f"{i}. {insight}")
            else:
                print("\n📚 Todavía no tenemos aprendizajes guardados. Ejecutá /daily primero.")
            continue

        # Regular conversation
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=2000,
            system=system_prompt,
            messages=conversation_history
        )

        assistant_message = response.content[0].text
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        print(f"\n🤖 Jarvis Marketing: {assistant_message}")

        # Auto-save insights from conversation
        if any(word in user_input.lower() for word in ["aprendi", "funciona", "no funciona", "resultado", "conversion", "leads"]):
            kb = load_knowledge()
            kb["learned_insights"].append(
                f"[{datetime.now().strftime('%Y-%m-%d')}] Diego reportó: {user_input[:150]}"
            )
            if len(kb["learned_insights"]) > 30:
                kb["learned_insights"] = kb["learned_insights"][-30:]
            KNOWLEDGE_PATH.write_text(json.dumps(kb, indent=2, ensure_ascii=False))
            print("\n  💾 (Aprendizaje guardado en la base de conocimiento)")


if __name__ == "__main__":
    run_interactive_agent()
