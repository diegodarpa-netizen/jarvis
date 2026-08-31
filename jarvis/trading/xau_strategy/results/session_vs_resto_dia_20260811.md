# Comparación sesión vs. resto del día — 11/08/2026

Pedido de Diego: comparar la ventana operativa oficial (09:01-10:59 NY) contra el resto del día, para ver si se están perdiendo oportunidades fuera de esa franja, antes de considerar extender la estrategia a otros activos (EUR/BTC/SPY/TLT).

## Método

Se corrió `session_vs_resto_dia.py` (nuevo, reutiliza las funciones de `backtest.py` sin modificar su lógica) sobre datos reales de 1 minuto de `GC=F` (yfinance). **Yfinance solo entrega 30 días de historial en 1m** — el script asumía 60d, terminó con 23 días reales (19/07 → 11/08/2026).

## Resultado

| Franja horaria | Operaciones | Win Rate | Total R | R/semana |
|---|---|---|---|---|
| Sesión actual (09:01-10:59 NY) | 16 | 25,0% | −8,4R | −2,1R |
| Resto del día | 15 | 20,0% | −9,3R | −1,86R |
| Apertura Londres (03:00-05:00 NY) | 20 | 45,0% | −2,9R | −0,73R |
| Tarde NY (13:00-15:00 NY) | 9 | 22,2% | −5,2R | −1,3R |

**Ninguna franja fue rentable en las últimas 3 semanas.** La sesión oficial no le gana claramente al resto del día — ambas negativas, en rangos similares. Apertura de Londres tuvo mejor win rate (45%) pero sigue sin superar el umbral de equilibrio (>52,6% necesario con TP=0,9R / SL=1R).

## Advertencias

1. **Muestra chica** (9-20 operaciones por franja, 23 días) — no es concluyente por sí sola.
2. **`backtest.py` es una réplica más simple que `xau_v9.pine` actual** — falta filtro de tamaño mínimo del gray box, MEC-B, MER, invalidación dinámica del gray box. Puede estar subestimando el resultado real de la versión en vivo.

## Contexto

Coincide con la caída de win rate ya documentada en `ANALISIS_ESTRATEGICO_IA_FINANCIERA.md` (70,0%→58,8%→38,5% en corridas de junio/julio) — confirma el mismo patrón de inestabilidad con datos más recientes (agosto), no una señal nueva y aislada.

## Pendiente

Decidir si el foco pasa a: (a) resolver por qué la estrategia base de XAU viene floja antes de extenderla, o (b) actualizar `session_vs_resto_dia.py` para usar la lógica completa de `xau_v9.pine` (gray-box con filtro mínimo, MEC-B, MER) en vez de la versión simplificada, para descartar que el resultado negativo sea artefacto de código desactualizado.
