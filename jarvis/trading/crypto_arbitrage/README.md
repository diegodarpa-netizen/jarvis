# Scanner de arbitraje cripto (ARS)

Origen: análisis del caso real de un conocido de Diego que hizo 17 "vueltas"
de compra/venta de USDT dentro de Binance P2P en 2 horas, con $11.000.000
ARS, capturando una brecha de ~$6-8 por USDT entre anunciantes.

## Qué hace

`scanner_arbitraje.py` mide dos tipos de brecha en vivo, porque **no son
comparables en riesgo**:

1. **Intra-Binance P2P** (lo que hizo el conocido de Diego): comprar a un
   anunciante y vender a otro, todo dentro de Binance. Rápido (minutos),
   sin mover fondos entre exchanges. Fuente: API pública de anuncios de
   Binance P2P (`p2p.binance.com`).
2. **Inter-plataforma**: comprar barato en un exchange y vender caro en
   otro. Requiere mover USDT por red blockchain entre exchanges (minutos
   de confirmación + exposición a que el precio se mueva mientras tanto).
   Fuente: [Criptoya API](https://criptoya.com/api) (agrega ~30
   exchanges/P2P argentinos).

## Uso

```bash
python3 scanner_arbitraje.py                      # USDT/ARS, $500.000 ARS de referencia
python3 scanner_arbitraje.py --monto 650000        # otro monto por vuelta
python3 scanner_arbitraje.py --activo usdc         # otra stablecoin
python3 scanner_arbitraje.py --guardar             # guarda snapshot JSON en results/
```

### `oportunidades_binance.py` — simulación multi-activo para un monto real

Extiende el análisis a **USDT, USDC, BTC, ETH, BNB** dentro de Binance P2P,
simulando el "llenado" real de un monto (ej. USD 10.000) comiendo varios
anuncios en vez de mirar solo el mejor precio de punta de libro — porque un
solo anuncio casi nunca tiene esa profundidad.

```bash
python3 oportunidades_binance.py                     # USD 10.000, todos los activos
python3 oportunidades_binance.py --monto-usd 5000
python3 oportunidades_binance.py --activos USDT,BTC,ETH
python3 oportunidades_binance.py --guardar            # loguea a results/historial_oportunidades.csv
```

**Hallazgo clave (13/08/2026, simulando USD 10.000):** con USDT la brecha
real fue ~0,5% (ejecutable, libro profundo, ~10 anuncios de cada lado). Con
BTC/ETH/BNB/USDC el script mostró brechas de 7% a 22% — **eso NO es
arbitraje real**: son pares con muy poca profundidad en ARS, donde 1-3
anuncios alcanzan a "llenar" el monto simulado y el precio promedio queda
distorsionado por anuncios sueltos que probablemente no sean realmente
ejecutables (verificación extra del comprador, poca reputación del
anunciante, o directamente anuncios trampa). El script marca esto con 🚩
cuando la brecha supera 3%. **Para $10.000 en serio, USDT es el único par
con liquidez suficiente para operar con confianza.**

### `analizar_historial.py` — en qué horarios se abre más la brecha

Lee el CSV que va logueando `oportunidades_binance.py --guardar` y calcula
el promedio de brecha por hora del día y por día de la semana. Necesita
varios días de datos acumulados (correr el scanner repetidas veces, no una
sola vez) para que el patrón sea confiable — con una corrida no dice nada.

```bash
python3 analizar_historial.py
python3 analizar_historial.py --activo USDT
```

## Conclusión del análisis inicial (13/08/2026)

Con datos en vivo, el spread intra-Binance rondaba **0,2-0,4% por vuelta**
en condiciones normales de mercado — consistente con el ejemplo real
($6 netos sobre ~$1.460-1.580, ≈0,4%). El spread inter-plataforma
comparando los mejores exchanges entre sí fue mucho más chico (~0,02%) y
casi nunca compensa el riesgo/tiempo de mover fondos entre exchanges.

Ver también la conversación donde se auditaron los números del "30% en un
mes" — la brecha por vuelta que reporta este scanner es la variable clave
para chequear si un mes de operatoria como esa es realista o no.

## Pendiente si Diego quiere ir más en serio con esto

- Correr el scanner en distintos horarios/días para ver si el spread se
  abre en ventanas específicas (volatilidad, fines de semana, noticias).
- Sumar el costo real de mover cuentas bancarias a escala (evaluar riesgo
  de "cuenta señalada" — no está modelado acá, es el riesgo más grande).
- Si hay volumen sostenido, evaluar bot de gestión de anuncios (ver
  conversación — así operan los que "viven de esto").
