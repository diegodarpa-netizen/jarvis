# OCC Strategy R5.1 — Análisis de Rentabilidad

## Activos analizados
- [x] Oro (XAU/USD) — DEEP backtest 1993-2026
- [ ] Bitcoin (BTC/USD)
- [ ] S&P 500 (SPX)
- [ ] Forex (EUR/USD, GBP/USD)
- [ ] CEDEARs (pendiente)

---

## ANÁLISIS PROFUNDO — ORO (XAU/USD)

### ¿Qué dicen los números realmente?

#### Lo que brilla
| Dato | Valor | Por qué importa |
|------|-------|-----------------|
| Profit Factor | **14.129** | Por cada $1 que se pierde, se ganan $14.13. Extraordinario. >2 ya es bueno |
| Win Rate | **79.23%** | 4 de cada 5 trades son ganadores |
| Ratio Gan/Pérd | **3.661** | Las ganancias son 3.6x más grandes que las pérdidas |
| Sharpe Ratio | **2.294** | >1 es bueno, >2 es excelente. Riesgo ajustado muy sólido |
| Max Drawdown | **0.02%** | Prácticamente nulo. Protección de capital impresionante |
| vs Buy & Hold | **+$7,455** | Aplastó completamente a la estrategia pasiva |

#### Lo que hay que cuestionar
| Dato | Valor | Alerta |
|------|-------|--------|
| CAGR | **0.55%** | Solo 0.55% anual en 33 años. ¿Por qué tan bajo? |
| Return on capital | **3.18%** | En 33 años, 3.18% total. Muy bajo en términos absolutos |
| Capital requerido | **$19.81** | Sospechosamente bajo — sugiere que el backtest usó capital muy pequeño |
| Delay setting | **Desconocido** | Si fue 0, todos los números están inflados por repainting |

### La Paradoja del Oro
Los números de calidad (win rate, profit factor, sharpe) son excelentes, pero el retorno absoluto (0.55% CAGR) es mínimo. Esto se explica por:
1. **Posición size**: 10% del capital por trade con capital inicial pequeño
2. **Timeframe largo**: 33 años diluyen el retorno porcentual
3. **Posible repainting**: Delay=0 infla calidad pero no el absoluto

### Short > Long en Oro
- Short win rate: 81.16% vs Long 77.29%
- Short avg PnL: $8.79 vs Long $6.56
- Short ratio: 3.935 vs Long 3.339
- **Conclusión:** El oro tiene mejores oportunidades bajistas en este TF con esta configuración

---

## ANÁLISIS POR TIMEFRAME (Pendiente de datos)

| Timeframe | Estilo | Estado | Win Rate | Profit Factor | CAGR |
|-----------|--------|--------|----------|---------------|------|
| 1m | Scalping | ⏳ Pendiente | - | - | - |
| 5m | Scalping | ⏳ Pendiente | - | - | - |
| 15m | Intraday | ⏳ Pendiente | - | - | - |
| 1h | Intraday | ⏳ Pendiente | - | - | - |
| 4h | Swing | ⏳ Pendiente | - | - | - |
| 1D | Swing | ✅ (Deep, posiblemente) | 79.23% | 14.129 | 0.55% |

---

## DATOS FALTANTES — SOLICITAR AL USUARIO

### Alta prioridad
1. **¿Qué timeframe es el backtest?** El chart muestra "May" con horas (08:04, 11:04...) — parece ser 1h o 4h
2. **¿Delay estaba en 0 o en 1?** Crítico para validar resultados
3. **¿Capital inicial configurado?** Para calcular retorno real
4. **¿Qué MA type y período usaste?** SMMA period 8 = default, o modificaste?
5. **Backtest en otros TFs del mismo oro** — para comparar

### Media prioridad
6. Backtest en BTC/USD misma configuración
7. Backtest en EUR/USD o S&P500
8. Resultados con Delay=1 (anti-repainting)

---

## CONCLUSIONES PRELIMINARES

### Esta estrategia ES válida para:
- **Swing trading en Oro** — los números de calidad son sobresalientes
- **Tendencias claras** — funciona mejor cuando el activo tiene movimientos direccionales
- **Largo plazo** — 33 años de datos positivos no es casualidad

### PRECAUCIONES antes de operar en vivo:
1. Verificar Delay=1 y re-correr el backtest (los resultados bajarán)
2. Definir capital inicial real y calcular retorno absoluto
3. Agregar stop loss fijo para proteger el capital en whipsaws
4. Testear en mercados laterales específicamente
5. No operar en scalping sin testeo profundo con comisiones reales incluidas
