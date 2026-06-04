# 🏥 Agente de Marketing - Cirugía Plástica

Módulo especializado para análisis de marketing, competencia y estrategia digital
enfocado en clínicas de cirugía plástica en Buenos Aires.

## Inicio Rápido

```bash
cd /Users/diegorodriguez/Desktop/Jarvis/jarvis/marketing

# Agente interactivo (chatear con el agente)
python run_marketing.py

# Briefing diario de mercado
python run_marketing.py daily

# Análisis de competidores
python run_marketing.py competidores

# Playbook de contenido viral
python run_marketing.py viral

# Blueprint de Meta Ads
python run_marketing.py meta

# Ejecutar TODO (análisis completo)
python run_marketing.py todos
```

## Módulos

| Módulo | Comando | Qué hace |
|--------|---------|----------|
| `market_daily.py` | `daily` | Briefing diario: tendencias, foco del día, idea de contenido |
| `competitor_analyzer.py` | `competidores` | Analiza qué hacen los competidores en Meta Ad Library |
| `viral_tracker.py` | `viral` | Patterns de videos virales + calendario de contenido |
| `meta_optimizer.py` | `meta` | Blueprint completo de campañas Meta Ads |
| `marketing_agent.py` | (sin arg) | Chat interactivo con el agente |

## Comandos del Agente Interactivo

Cuando estás en el chat, podés usar:
- `/competidores` → lanzar análisis de competidores
- `/viral` → generar playbook viral
- `/meta` → generar blueprint Meta
- `/daily` → briefing del día
- `/aprendizajes` → ver lo que aprendimos juntos
- `/salir` → terminar

## Reportes

Todos los análisis se guardan en `reports/` con fecha:
- `daily_briefing_YYYY-MM-DD.md`
- `competitors_YYYY-MM-DD.md`
- `viral_content_YYYY-MM-DD.md`
- `meta_strategy_YYYY-MM-DD.md`

## Base de Conocimiento

El agente aprende con el tiempo. Todo lo aprendido se acumula en:
`data/knowledge_base.json`

El agente usa este conocimiento en cada análisis para mejorar las recomendaciones.

## Configuración

Editá `data/config.json` para ajustar:
- Procedimientos a priorizar
- Budget de Meta
- Zonas geográficas
- Keywords de competidores
- Hashtags a rastrear
