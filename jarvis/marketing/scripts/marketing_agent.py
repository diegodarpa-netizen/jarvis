"""
Agente de marketing de alto rendimiento para cirugía plástica.
Usa Claude Opus 4.8 con prompt caching, adaptive thinking, tool use y streaming.
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
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"
REPORTS_PATH = Path(__file__).parent.parent / "reports"

MODEL = "claude-opus-4-8"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def load_knowledge() -> dict:
    return json.loads(KNOWLEDGE_PATH.read_text())


def save_knowledge(kb: dict) -> None:
    KNOWLEDGE_PATH.write_text(json.dumps(kb, indent=2, ensure_ascii=False))


def load_static_knowledge() -> str:
    """Carga todos los archivos de conocimiento estático de la carpeta knowledge/."""
    if not KNOWLEDGE_DIR.exists():
        return ""
    parts = []
    for path in sorted(KNOWLEDGE_DIR.iterdir()):
        if path.suffix in (".md", ".json") and path.is_file():
            content = path.read_text(encoding="utf-8")
            parts.append(f"\n\n{'='*60}\n## ARCHIVO: {path.name}\n{'='*60}\n{content}")
    return "\n".join(parts)


def build_system_prompt(config: dict, kb: dict) -> list[dict]:
    """
    Construye el system prompt en dos bloques cacheados:
    - Bloque 1 (muy estable): conocimiento estático + config de clínica
    - Bloque 2 (semi-estable): aprendizajes dinámicos acumulados
    El orden importa: primero lo más estable para maximizar cache hits.
    """
    static_knowledge = load_static_knowledge()

    base_config = f"""Sos el Agente de Marketing especializado en cirugía plástica de la clínica de Diego en Buenos Aires.

CLÍNICA:
- Ubicación: {config['clinic']['location']}
- Procedimientos: {', '.join(config['clinic']['procedures'])}
- Presupuesto Meta Ads: ${config['meta_ads']['monthly_budget_usd']} USD/mes
- Plataformas: {config['meta_ads']['primary_platform']} + {config['meta_ads']['secondary_platform']}
- Target: Mujeres {config['meta_ads']['target_age_range'][0]}-{config['meta_ads']['target_age_range'][1]} años, {', '.join(config['meta_ads']['geo_target'])}

ROL:
- Experto en marketing digital para clínicas de cirugía plástica
- Dominio profundo de Meta Ads (Facebook/Instagram) incluyendo políticas para contenido médico
- Psicología del paciente potencial de cirugía estética
- Estrategias de contenido viral en el rubro
- Análisis de competidores y benchmarks de la industria

ESTILO:
- Directo y práctico, sin vueltas
- Siempre terminás con acciones concretas y métricas esperadas
- Cuando no tenés datos exactos, lo decís y das la mejor alternativa basada en experiencia
- Usás la base de conocimiento acumulada para personalizar las recomendaciones
- Respondés en español rioplatense

{static_knowledge}"""

    insights = kb.get("learned_insights", [])[-15:]
    meta_count = len(kb.get("meta_strategies", []))
    viral_count = len(kb.get("viral_content_patterns", []))
    competitor_count = len(kb.get("competitor_insights", []))

    knowledge_summary = f"""BASE DE CONOCIMIENTO ACUMULADA DE ESTA CLÍNICA:
- Estrategias Meta analizadas: {meta_count}
- Patrones de contenido viral documentados: {viral_count}
- Análisis de competidores: {competitor_count}
"""
    if insights:
        knowledge_summary += "\nAPRENDIZAJES RECIENTES DE DIEGO:\n" + "\n".join(f"- {i}" for i in insights)

    return [
        {
            "type": "text",
            "text": base_config,
            "cache_control": {"type": "ephemeral"},  # bloque estable — se cachea
        },
        {
            "type": "text",
            "text": knowledge_summary,
            # sin cache_control — este bloque cambia con cada aprendizaje nuevo
        },
    ]


TOOLS = [
    {
        "name": "generate_copy",
        "description": (
            "Genera copies publicitarios, textos para ads, posts de Instagram/Facebook, "
            "hooks para videos, headlines y CTAs. Llamá esta herramienta cuando Diego pida "
            "crear textos, copies, contenido, anuncios, creatividades o cualquier pieza de copy."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "procedure": {
                    "type": "string",
                    "description": "Procedimiento (ej: rinoplastia, liposuccion, mamoplastia)",
                },
                "format": {
                    "type": "string",
                    "enum": ["ad_facebook", "ad_instagram", "caption_post", "video_hook", "email", "whatsapp"],
                    "description": "Formato del copy",
                },
                "objective": {
                    "type": "string",
                    "enum": ["leads", "awareness", "engagement", "retargeting"],
                    "description": "Objetivo de la pieza",
                },
                "tone": {
                    "type": "string",
                    "enum": ["emocional", "informativo", "urgencia", "aspiracional", "testimonial"],
                    "description": "Tono del copy",
                },
                "versions": {
                    "type": "integer",
                    "description": "Cantidad de versiones a generar (default 3)",
                },
            },
            "required": ["procedure", "format", "objective"],
        },
    },
    {
        "name": "analyze_campaign",
        "description": (
            "Analiza métricas de campañas de Meta Ads, interpreta KPIs, detecta problemas, "
            "sugiere optimizaciones y distribuye presupuesto. Llamá cuando Diego comparta "
            "datos de campañas, métricas, resultados, costos o pida analizar performance."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "object",
                    "description": "Métricas de la campaña (CPL, CTR, conversiones, gasto, alcance, etc.)",
                },
                "period": {
                    "type": "string",
                    "description": "Período analizado (ej: última semana, mes de mayo)",
                },
                "procedures": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Procedimientos o campañas específicos a analizar",
                },
                "budget": {
                    "type": "number",
                    "description": "Presupuesto total invertido en el período",
                },
            },
            "required": ["metrics"],
        },
    },
    {
        "name": "create_strategy",
        "description": (
            "Crea estrategias de marketing, planes de campaña, calendarios editoriales, "
            "estructura de funnels, blueprints de Meta Ads y planificación mensual. "
            "Llamá cuando Diego pida estrategia, plan, blueprint, funnel o planificación. "
            "Esta herramienta usa razonamiento profundo para dar estrategias de alto nivel."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "focus": {
                    "type": "string",
                    "enum": ["meta_ads", "contenido", "funnel_completo", "mensual", "lanzamiento"],
                    "description": "Foco de la estrategia",
                },
                "procedures": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Procedimientos a incluir (vacío = todos)",
                },
                "budget": {
                    "type": "number",
                    "description": "Presupuesto disponible en USD",
                },
                "timeframe": {
                    "type": "string",
                    "description": "Período de la estrategia (ej: próximo mes, Q3 2026)",
                },
                "goal": {
                    "type": "string",
                    "description": "Objetivo principal (ej: maximizar leads, bajar CPL, aumentar brand awareness)",
                },
            },
            "required": ["focus"],
        },
    },
    {
        "name": "research_market",
        "description": (
            "Investiga el mercado, analiza tendencias, estudia competidores, identifica "
            "oportunidades y genera insights del sector de cirugía plástica en Argentina. "
            "Llamá cuando Diego pida investigación, análisis de competencia, tendencias o insights."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "enum": ["competidores", "tendencias", "audiencias", "precios", "temporadas", "plataformas"],
                    "description": "Tema a investigar",
                },
                "specific_question": {
                    "type": "string",
                    "description": "Pregunta específica de investigación",
                },
                "procedures": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Procedimientos de interés",
                },
            },
            "required": ["topic"],
        },
    },
]


def execute_tool(tool_name: str, tool_input: dict, config: dict, kb: dict) -> str:
    """
    Ejecuta la herramienta usando Claude con thinking adaptativo para estrategia
    y respuesta directa para copy y análisis.
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    procedures = config["clinic"]["procedures"]
    budget = config["meta_ads"]["monthly_budget_usd"]
    geo = config["meta_ads"]["geo_target"]

    use_thinking = tool_name == "create_strategy"

    if tool_name == "generate_copy":
        procedure = tool_input.get("procedure", "procedimiento general")
        fmt = tool_input.get("format", "ad_instagram")
        objective = tool_input.get("objective", "leads")
        tone = tool_input.get("tone", "emocional")
        versions = tool_input.get("versions", 3)

        prompt = f"""Generá {versions} versiones de copy para Meta Ads.

PARÁMETROS:
- Procedimiento: {procedure}
- Formato: {fmt}
- Objetivo: {objective}
- Tono: {tone}
- Ubicación: {', '.join(geo)}

Para cada versión incluí:
1. Headline (máx 40 caracteres)
2. Texto principal (adaptado al formato)
3. CTA específico
4. Nota sobre la creatividad visual sugerida

Respetá las políticas de Meta para contenido médico (no usar palabras prohibidas, no hacer promesas de resultados garantizados)."""

    elif tool_name == "analyze_campaign":
        metrics = json.dumps(tool_input.get("metrics", {}), ensure_ascii=False)
        period = tool_input.get("period", "período no especificado")
        procs = tool_input.get("procedures", procedures)
        camp_budget = tool_input.get("budget", budget)

        prompt = f"""Analizá estas métricas de campaña Meta Ads y dá recomendaciones accionables.

PERÍODO: {period}
PRESUPUESTO INVERTIDO: ${camp_budget} USD
PROCEDIMIENTOS: {', '.join(procs)}
MÉTRICAS: {metrics}

Benchmarks del sector en Argentina:
- CPL rinoplastia: $8-25 USD
- CPL liposucción: $5-18 USD
- CPL mamoplastia: $6-20 USD
- CTR promedio: 1.5-3.5%
- Frecuencia óptima: 2-4

Incluí:
1. Diagnóstico rápido (qué está funcionando / qué no)
2. KPIs vs benchmarks del sector
3. Top 3 optimizaciones inmediatas con impacto esperado
4. Redistribución de presupuesto sugerida
5. Próximos pasos (qué hacer esta semana)"""

    elif tool_name == "create_strategy":
        focus = tool_input.get("focus", "meta_ads")
        procs = tool_input.get("procedures") or procedures
        strat_budget = tool_input.get("budget", budget)
        timeframe = tool_input.get("timeframe", "próximo mes")
        goal = tool_input.get("goal", "maximizar leads calificados")

        prompt = f"""Creá una estrategia completa de marketing para la clínica de cirugía plástica.

PARÁMETROS:
- Foco: {focus}
- Procedimientos: {', '.join(procs)}
- Presupuesto: ${strat_budget} USD
- Período: {timeframe}
- Objetivo principal: {goal}
- Mercado: {', '.join(geo)}

Creá una estrategia detallada y ejecutable con:
- Estructura de campañas con distribución de presupuesto
- Segmentación de audiencias por procedimiento
- Calendario de contenido con frecuencia
- KPIs objetivo y métricas de control
- Plan de optimización semanal
- Acciones inmediatas para los próximos 7 días"""

    elif tool_name == "research_market":
        topic = tool_input.get("topic", "tendencias")
        question = tool_input.get("specific_question", "")
        procs = tool_input.get("procedures") or procedures

        prompt = f"""Hacé un análisis de mercado sobre: {topic}
{'Pregunta específica: ' + question if question else ''}

CONTEXTO:
- Mercado: Cirugía plástica en Buenos Aires, Argentina
- Procedimientos: {', '.join(procs)}
- Año: 2026

Analizá:
1. Estado actual del mercado y tendencias
2. Oportunidades identificadas para la clínica
3. Amenazas o riesgos a considerar
4. Recomendaciones estratégicas basadas en el análisis
5. Datos o métricas clave a monitorear"""

    else:
        return f"Herramienta desconocida: {tool_name}"

    create_kwargs: dict = {
        "model": MODEL,
        "max_tokens": 4096,
        "system": "Sos un experto en marketing digital especializado en cirugía plástica en Argentina. Respondés con análisis profundos, concretos y accionables.",
        "messages": [{"role": "user", "content": prompt}],
    }
    if use_thinking:
        create_kwargs["thinking"] = {"type": "adaptive"}
        create_kwargs["max_tokens"] = 8192

    response = client.messages.create(**create_kwargs)

    result_parts = []
    for block in response.content:
        if block.type == "text":
            result_parts.append(block.text)

    result = "\n".join(result_parts)

    # Persistir aprendizajes si es estrategia o investigación
    if tool_name in ("create_strategy", "research_market"):
        kb["learned_insights"].append(
            f"[{datetime.now().strftime('%Y-%m-%d')}] {tool_name}: {tool_input.get('focus') or tool_input.get('topic')} — {result[:200]}"
        )
        kb["learned_insights"] = kb["learned_insights"][-30:]
        if tool_name == "create_strategy":
            kb["meta_strategies"] = kb.get("meta_strategies", [])
            kb["meta_strategies"].append({"date": datetime.now().strftime("%Y-%m-%d"), "summary": result[:500]})
            kb["meta_strategies"] = kb["meta_strategies"][-10:]
        save_knowledge(kb)

    return result


def run_agent():
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    config = load_config()

    print("=" * 60)
    print("🏥 JARVIS MARKETING — Agente IA de Cirugía Plástica")
    print("=" * 60)
    print(f"Clínica: {config['clinic']['location']} | Budget: ${config['meta_ads']['monthly_budget_usd']} USD/mes")
    print()
    print("Comandos: /salir, /aprendizajes, /reporte")
    print("Podés pedirme: copies, análisis de campañas, estrategias, investigación de mercado")
    print("=" * 60)

    kb = load_knowledge()
    system_prompt = build_system_prompt(config, kb)
    conversation: list[dict] = []

    while True:
        try:
            user_input = input("\n💬 Diego: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Hasta luego!")
            break

        if not user_input:
            continue

        if user_input.lower() == "/salir":
            print("\n👋 Hasta luego!")
            break

        if user_input.lower() == "/aprendizajes":
            kb = load_knowledge()
            insights = kb.get("learned_insights", [])
            if insights:
                print("\n📚 BASE DE CONOCIMIENTO:")
                for i, insight in enumerate(insights[-10:], 1):
                    print(f"{i}. {insight}")
            else:
                print("\n📚 Todavía no hay aprendizajes. Pedime estrategias o análisis para acumular conocimiento.")
            continue

        if user_input.lower() == "/reporte":
            REPORTS_PATH.mkdir(exist_ok=True)
            date = datetime.now().strftime("%Y-%m-%d")
            kb = load_knowledge()
            report = f"""# Reporte de Marketing — {date}

## Base de Conocimiento
- Estrategias Meta: {len(kb.get('meta_strategies', []))}
- Patrones virales: {len(kb.get('viral_content_patterns', []))}
- Análisis de competidores: {len(kb.get('competitor_insights', []))}

## Últimos Aprendizajes
{chr(10).join('- ' + i for i in kb.get('learned_insights', [])[-10:])}
"""
            path = REPORTS_PATH / f"reporte_{date}.md"
            path.write_text(report, encoding="utf-8")
            print(f"\n✅ Reporte guardado: {path}")
            continue

        conversation.append({"role": "user", "content": user_input})

        print("\n🤖 Jarvis Marketing: ", end="", flush=True)

        # Primer llamado al modelo — puede decidir usar herramientas
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=conversation,
        )

        # Agentic loop — ejecuta herramientas hasta que Claude termine
        while response.stop_reason == "tool_use":
            # Mostrar texto de razonamiento previo a la herramienta si existe
            for block in response.content:
                if block.type == "text" and block.text.strip():
                    print(block.text)

            tool_results = []
            kb = load_knowledge()  # Refrescar kb antes de ejecutar

            for block in response.content:
                if block.type != "tool_use":
                    continue

                tool_name = block.name
                tool_input = block.input
                print(f"\n  🔧 [{tool_name}] ", end="", flush=True)

                result = execute_tool(tool_name, tool_input, config, kb)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
                print("✓", flush=True)

            conversation.append({"role": "assistant", "content": response.content})
            conversation.append({"role": "user", "content": tool_results})

            # Respuesta final con streaming
            print("\n")
            final_text = ""
            with client.messages.stream(
                model=MODEL,
                max_tokens=4096,
                system=system_prompt,
                tools=TOOLS,
                messages=conversation,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    final_text += text
                response = stream.get_final_message()

            if response.stop_reason != "tool_use":
                conversation.append({"role": "assistant", "content": final_text})
                break

        else:
            # Sin herramientas — stream directo
            if response.stop_reason == "end_turn":
                full_response = ""
                with client.messages.stream(
                    model=MODEL,
                    max_tokens=4096,
                    system=system_prompt,
                    tools=TOOLS,
                    messages=conversation,
                ) as stream:
                    for text in stream.text_stream:
                        print(text, end="", flush=True)
                        full_response += text
                print()
                conversation.append({"role": "assistant", "content": full_response})

        # Auto-guardar insights de la conversación
        if any(word in user_input.lower() for word in ["funciona", "resultado", "leads", "conversión", "cpl", "aprend"]):
            kb = load_knowledge()
            kb["learned_insights"].append(
                f"[{datetime.now().strftime('%Y-%m-%d')}] Diego reportó: {user_input[:150]}"
            )
            kb["learned_insights"] = kb["learned_insights"][-30:]
            save_knowledge(kb)
            print("\n  💾 (Insight guardado en base de conocimiento)", flush=True)

        print()


if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY no configurada.")
        sys.exit(1)
    run_agent()
