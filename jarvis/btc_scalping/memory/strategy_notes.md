# BTC Scalping — Notas de Estrategia

## Versión activa
- En desarrollo — sin script Pine aún
- Timeframe ejecución: M2 / M3
- Timeframe estructura: M15 / M30

## Reglas base (a confirmar con backtest)
- Sesión: 13:00–16:00 UTC (apertura NY)
- Estructura mayor en M15: highs / lows / ChOC
- Ejecución en M2/M3: patrón ENV o START (igual que XAU)
- SL: último pivot M15
- TP: 0.9R (mínimo), objetivo 1.5R si volatilidad lo permite
- Filtro noticias: bloquear 15 min antes/después de CPI, FOMC, NFP (afectan BTC)

## Estado
- [ ] Definir gray box en M15
- [ ] Adaptar lógica ChOC a BTC M2/M3
- [ ] Primer script Pine (basado en XAU v9)
- [ ] Backtest 30 días
