# BTC/USD Scalping — Análisis y Estrategia

## Estado del mercado — 27 Jun 2026

### Precio actual
- **BTC/USD:** ~$60,000 (rango $59,000–$60,150)
- **Tendencia general:** BAJISTA — cayó ~50% desde el ATH de 2025
- **Mínimo reciente:** ~$58,000 (nivel no visto desde Sep 2024)
- **Volumen 24h:** $25.39B

### Niveles clave
| Nivel | Precio |
|-------|--------|
| Resistencia 1 | $62,500 – $63,000 |
| Resistencia 2 | $68,000 – $68,500 |
| Soporte fuerte | $58,000 |
| Soporte siguiente | $54,000 – $55,000 |

### Macro / sentimiento
- ETFs Bitcoin cerraron Mayo 2026 con **$2.3B en salidas netas** (mayor outflow mensual del año)
- Indicadores técnicos: **30 bajistas vs 3 alcistas**
- SMA 200 días proyectada en $74,281 (precio actual ~17% por debajo)
- Contexto: mercado en distribución / corrección post-bull run

### Proyección 2026
- Rango conservador: $58,000 – $78,000
- Rango bullish (recuperación): hasta $91,000 – $118,000
- Catalizador positivo necesario: flujo institucional de regreso vía ETFs

---

## Estrategia de Scalping BTC — M2/M3

### Contexto del activo
BTC opera 24/7 — no hay "sesión NY" como en XAU. Las sesiones más líquidas son:
- **Asia:** 00:00–08:00 UTC
- **Londres:** 08:00–12:00 UTC
- **NY:** 13:00–20:00 UTC (foco principal)
- **Mejor ventana para scalping:** 13:00–16:00 UTC (apertura NY + máxima liquidez)

### Marco base de análisis (adaptado de XAU)
El mismo principio que usamos en XAU aplica:
- **M15 o M30** = estructura mayor (equivalente al M3 de XAU) → define tendencia
- **M2 o M3** = ejecución → buscar patrones de entrada

### Modelos de entrada (a definir)
1. **ChOC + MEC (como XAU):** rango inicial de sesión → ruptura → pullback → envolvente
2. **Bollinger Squeeze:** consolidación en BB → expansión → entrada en dirección del breakout
3. **RSI + MA:** RSI cruza 50 + precio sobre/bajo MA rápida (EMA 9/21)

### Risk Management
- **Riesgo por trade:** 0.5% – 1% del capital
- **Max pérdida diaria:** 3% del capital → parar operaciones
- **RR mínimo:** 1:0.9 (igual que XAU, pero pueden usarse 1:1.5 en BTC por volatilidad)
- **Trades diarios:** máx 3–5 (evitar sobretrading)

### Diferencias clave vs XAU
| | XAU/USD | BTC/USD |
|--|--|--|
| Timeframe ejecución | M1 | M2–M3 |
| Sesión | 09:01–10:59 NY | 13:00–16:00 UTC |
| Volatilidad | Alta pero controlada | Muy alta (news crypto) |
| Spread/fees | Bajo (forex) | Medio (exchange fees) |
| 24/7 | No | Sí |

---

## Próximos pasos

- [ ] Elegir exchange y par (BTC/USDT perpetuo en Binance/Bybit?)
- [ ] Definir estructura del gray box en M15 para BTC
- [ ] Adaptar el script XAU → BTC (cambiar sesión y timeframes)
- [ ] Primer backtest manual: 5 días de sesión NY en M2/M3
- [ ] Comparar con trader de referencia si hay uno disponible
