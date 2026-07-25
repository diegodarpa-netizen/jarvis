"""
Optimizador de Meta Ads para cirugía plástica.
Genera recomendaciones de segmentación, copy, creatividades y estructura de campañas.
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


def generate_meta_strategy():
    config = load_config()
    kb = load_knowledge()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    procedures = config["clinic"]["procedures"]
    budget = config["meta_ads"]["monthly_budget_usd"]
    geo = config["meta_ads"]["geo_target"]

    print("📊 Generando estrategia de Meta Ads optimizada...")

    analysis_queries = [
        f"segmentacion Meta Ads cirugia plastica Argentina 2026 audiencias personalizadas lookalike intereses que funciona mejor",
        f"estructura campanas Meta Ads clinica estetica presupuesto ${budget} mensual como distribuir awareness conversion retargeting",
        f"copy publicitario anuncios cirugia plastica que genera leads calificados objeciones manejo precio confianza",
        f"creatividades Meta Ads cirugia estetica que tienen mejor CTR y conversion imagenes vs videos carrusel",
        f"retargeting estrategia clientes potenciales cirugia plastica que no convirtieron como recuperarlos",
    ]

    strategies = []

    for query in analysis_queries:
        print(f"  → Analizando: {query[:55]}...")
        strategy_text = web_search_query(
            query=f"""Buscá información real y actualizada, y luego dame estrategia detallada sobre: {query}

Contexto específico:
- Ubicación: {', '.join(geo)}
- Procedimientos: {', '.join(procedures)}
- Presupuesto mensual: ${budget} USD
- Objetivo principal: generar consultas/leads calificados
- Plataforma primaria: Instagram

Necesito configuraciones exactas, no generalidades.
""",
            system="""Eres un experto certificado en Meta Ads (Facebook e Instagram) especializado en el sector médico-estético.
Has gestionado cuentas de clínicas de cirugía plástica en Argentina y Latinoamérica con presupuestos de $500 a $50.000 USD/mes.
Conoces en detalle las políticas de publicidad de Meta para contenido médico y cómo trabajar dentro de esas restricciones.
Usá la herramienta de búsqueda web para verificar benchmarks y políticas vigentes antes de responder — no respondas de memoria.
Siempre das recomendaciones ultra-específicas con números, porcentajes y configuraciones exactas.""",
            max_tokens=1500,
        )

        strategies.append({
            "topic": query[:60],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "strategy": strategy_text
        })

    # Generate full Meta campaign blueprint
    print("\n🗺️ Generando blueprint completo de campaña...")
    blueprint_response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=3000,
        messages=[{
            "role": "user",
            "content": f"""Basándote en estos análisis de Meta Ads para cirugía plástica:

{chr(10).join([f"TEMA: {s['topic']}{chr(10)}{s['strategy'][:350]}{chr(10)}" for s in strategies[:4]])}

Crea el BLUEPRINT COMPLETO DE CAMPAÑA META ADS para:
- Clínica cirugía plástica, Buenos Aires
- Procedimientos: {', '.join(procedures)}
- Presupuesto: ${budget} USD/mes
- Meta: máximos leads calificados

## 🏗️ Estructura de Cuenta Recomendada
(campañas, conjuntos de anuncios, distribución de presupuesto)

## 🎯 Segmentación Detallada por Procedimiento
(para cada procedimiento: intereses, comportamientos, demografía, excluir)

## 📝 3 Versiones de Copy por Procedimiento
(titular, texto, CTA - listo para copiar y pegar)

## 🖼️ Especificaciones de Creatividades
(qué mostrar, qué evitar por políticas de Meta, formatos y tamaños)

## 🔄 Estrategia de Funnel Completa
Frío → Tibio → Caliente → Retargeting (con acciones específicas en cada etapa)

## 📈 KPIs y Benchmarks
(CPL objetivo, CTR esperado, frecuencia máxima, cuándo escalar/pausar)

## ⚠️ Errores Comunes en Meta Ads Médicos y Cómo Evitarlos
"""
        }]
    )

    # Update knowledge base
    kb["meta_strategies"] = strategies[-10:]
    kb["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    KNOWLEDGE_PATH.write_text(json.dumps(kb, indent=2, ensure_ascii=False))

    # Save report
    REPORTS_PATH.mkdir(exist_ok=True)
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORTS_PATH / f"meta_strategy_{report_date}.md"
    report_path.write_text(f"""# Blueprint Meta Ads - {report_date}
## Cirugía Plástica Buenos Aires | Budget: ${budget} USD/mes

{blueprint_response.content[0].text}

---
*Generado por Jarvis Marketing Agent*
""", encoding="utf-8")

    print(f"\n✅ Blueprint guardado en: {report_path}")
    print("\n" + "="*60)
    print(blueprint_response.content[0].text)
    return blueprint_response.content[0].text


if __name__ == "__main__":
    generate_meta_strategy()
