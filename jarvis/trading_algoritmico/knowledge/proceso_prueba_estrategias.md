# Proceso de prueba de estrategias — estructura para cuando tengamos toda la data

A pedido de Diego (14/08/2026): *"armar la estructura de lo que vamos a hacer cuando tengamos toda la información."* Este es el proceso ordenado, con el cruce de EMA como ejemplo trabajado (usa números ya calculados, propios o investigados, no inventados).

## Aclaración de base

Un cruce de media móvil (o cualquier patrón técnico) **no tiene una "probabilidad de ocurrir"** — con una serie de precios dada, los cruces pasan de forma determinística, siempre que la media corta y la larga se crucen matemáticamente. Lo único probabilístico es **qué pasa después de cada cruce** — si conviene actuar sobre esa señal o no. Esa es la pregunta que hay que medir, no "cuántas veces se da el cruce".

## Los 4 pasos, en orden

### 1. Hipótesis con lógica económica (no minería de datos)

Antes de testear nada, poder explicar en una frase **por qué** el patrón debería funcionar — qué sesgo humano o fricción de mercado está explotando. Ejemplo con EMA cross: la lógica es que el momentum (una vez que arranca un movimiento) persiste más tiempo del que explicaría el azar puro — por under-reacción inicial de los participantes del mercado. Si no hay una razón así, es más señal de sobreajuste que de edge real (ver `biblioteca/README.md`, síntesis de Ernest Chan).

### 2. Medir el win rate real — no asumirlo

Correr el backtest y sacar el número real, no una intuición. Dos referencias que ya tenemos, de fuentes distintas, que **coinciden entre sí**:

| Fuente | Dato |
|---|---|
| Industria en general (trend-following clásico) | Gana **35-45%** de las operaciones — pero los ganadores son mucho más grandes que los perdedores |
| Nuestro propio backtest de EMA cross en XAU | **25% de win rate**, 4 operaciones — muestra muy chica, dirección consistente con el patrón de industria, pero no concluyente por sí sola |

**Patrón esperable en trend-following: gana pocas veces, pero cuando gana, gana grande.** Si un backtest de EMA cross te da 60-70% de win rate, es más señal de sobreajuste que de estrategia genuina — no es el comportamiento natural de este tipo de estrategia (fue justo lo que le pasó al XAU viejo: 70%→38,5% WR en corridas sucesivas, la firma clásica de overfitting).

### 3. No confiar en el número agregado — walk-forward por ventanas

El win rate/retorno de todo el período junto puede esconder que la estrategia solo funcionó en un tramo puntual. Ya lo comprobamos nosotros mismos con TLT: "ganó" el agregado de 2 años, pero en realidad **ganó 1 de 4 ventanas** — todo el resultado vino de una sola racha. Correr walk-forward (ventanas secuenciales, parámetros fijos, sin reoptimizar) es lo que separa "funciona de verdad, de forma consistente" de "tuvo suerte una vez" (ver `metodologia_validacion.md`).

### 4. Comparar siempre contra comprar-y-mantener

Un win rate de 35% "suena mal" en el aire, pero hay que compararlo contra la alternativa real (no hacer nada, solo comprar y mantener) en la misma ventana exacta — a veces la estrategia activa gana igual con menos operaciones ganadoras porque las pérdidas son chicas y las ganancias grandes; a veces pierde contra el simple "comprar y mantener" (nos pasó con SPY, 6 de 6 ventanas).

## Aplicado a cualquier estrategia nueva que se nos ocurra probar

Mismo proceso, cambiando el paso 1:

1. ¿Cuál es la lógica económica/de comportamiento detrás de esta idea?
2. Correr el backtest, medir win rate + tamaño promedio de ganador/perdedor + Sharpe — con parámetros de manual, no ajustados.
3. Walk-forward en varias ventanas — ¿gana de forma consistente o solo en el agregado?
4. Comparar contra comprar-y-mantener en cada ventana.

Si una estrategia no pasa los 4 pasos, no se declara "buena" — se documenta el resultado (positivo o negativo) en `bitacora_activos.md` y se sigue con la próxima hipótesis.
