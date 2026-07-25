"""
Capa de datos (data_source): consultas ancladas a la web real vía la tool
web_search de Claude. Antes de este módulo, market_daily.py, meta_optimizer.py,
competitor_analyzer.py y viral_tracker.py le pedían a Claude "investigar
tendencias actuales" sin darle ninguna herramienta de búsqueda real — el
modelo respondía con contenido plausible pero no verificado (con la fecha de
corte de entrenamiento, no información del día). Este módulo centraliza el
único punto que sí trae datos reales; los demás scripts son la capa
funcional (generan copy/estrategia/reportes a partir de esos datos).
"""
import os
import anthropic

MODEL = "claude-opus-4-8"
WEB_SEARCH_TOOL_TYPE = "web_search_20260209"


def web_search_query(query: str, system: str, max_tokens: int = 1500, max_uses: int = 3) -> str:
    """Ejecuta una consulta con acceso real a la web y devuelve solo el texto final (sin bloques de búsqueda)."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    tools = [{"type": WEB_SEARCH_TOOL_TYPE, "name": "web_search", "max_uses": max_uses}]
    messages = [{"role": "user", "content": query}]

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        tools=tools,
        messages=messages,
    )

    # El tool de búsqueda es server-side: Claude ya resuelve las búsquedas dentro
    # de esta misma respuesta. Solo hace falta reintentar si agota el límite de
    # iteraciones del servidor (pause_turn) en una consulta muy larga.
    while response.stop_reason == "pause_turn":
        messages = [
            {"role": "user", "content": query},
            {"role": "assistant", "content": response.content},
        ]
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            tools=tools,
            messages=messages,
        )

    return "\n".join(block.text for block in response.content if block.type == "text")
