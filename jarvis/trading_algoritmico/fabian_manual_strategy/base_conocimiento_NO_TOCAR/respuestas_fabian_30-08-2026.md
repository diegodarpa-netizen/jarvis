# Respuestas de Fabian — 30/08/2026

Contexto: Diego le mandó a Fabian por WhatsApp las 5 imágenes de casos sin
resolver de la calibración vela por vela (07/04, 22/04, 30/04, 22/05,
25/08/2026). Estas son sus respuestas textuales, más el envío de los PDFs
actualizados (Plan Técnico y Plan Operativo, ver carpeta), guardadas acá
como parte de la base de conocimiento.

## Operaciones del 07/04 (SELL 10:01) y 30/04 (SELL 09:34)

> "La vela de entrada fue una 'Vela Envolvente Martillo'. La explicación de
> cómo identificar este tipo de velas se encuentra en el PDF del plan
> técnico en: Sección 'Entrada' > Patrón envolvente (punto a) > Vela
> envolvente Martillo (punto ii)"

Nota (Claude, 30/08/2026): el PDF define martillo como cuerpo entre 50% y
85% del rango total. Nuestro cálculo dio 47,6% (07/04) y 44,7% (30/04) --
por debajo del piso. Diferencia probablemente explicada por la fuente de
dato: Fabian opera con OANDA (ver Plan Técnico pág. 31, "instrumento
XAUUSD... commodity CFD OANDA visto en TradingView"), nosotros usamos
Dukascopy -- pequeñas diferencias de precio entre brokers para el mismo
minuto pueden mover el % de cuerpo lo suficiente para cruzar el piso.

## Operación del 25/08 (SELL 10:19)

> "Puedes volver a explicarle a Claude lo que te comenté antes sobre el uso
> de la herramienta 'rango de precios' para medir el volumen del 0.01%. En
> la imagen te dibujé en un cuadrado rojo cómo se ve el volumen del 0.01% y
> las flechas rojas muestran desde qué punto a qué punto posicioné la
> herramienta."

Nota: coincide con el PDF (pág. 21-22) -- la herramienta oficial es "Rango
de precios" de TradingView, posicionada entre 2 puntos marcados con
flechas rojas en los propios ejemplos del PDF. El PDF también dice
explícitamente que el quiebre se mide "con CUERPO" (cierre), no con la
mecha -- esto contradice el fix de "medir con la mecha" que se había
aplicado antes en el código a partir del caso 21/04. Revertido el
30/08/2026 para alinear con el texto exacto del PDF.

## Operación del 22/04 (BUY 09:28)

> "En realidad la vela de entrada SI supera el alto M3 (la línea continua
> en la imagen) y confirma el cambio de comportamiento a alcista, validando
> una ejecución por MER. En el recuadro rojo de la imagen te señalo lo que
> te acabo de indicar."

Nota: contradice nuestro cálculo (con datos Dukascopy, esa vela no
rompía el nivel por USD 0,22). Misma hipótesis de fondo: diferencia de
precio entre OANDA (Fabian) y Dukascopy (nuestro dato). Pendiente:
revisar si con el margen medido por cuerpo (revertido) este caso ahora
coincide, aunque sea por otra razón a la que Fabian describe.

## Operación del 22/05 (SELL 10:03) -- RESUELTO, mecanismo confirmado

> "Tienes toda la razón, la entrada en venta fue en base a la vela roja
> enorme que indicas, la de las 10:00h. Sin embargo, se ejecutó a las
> 10:03h debido a que cuando se generó la oportunidad de entrada de las
> 10:00h, se estaba publicando una noticia de mediano impacto (Revised UoM
> Consumer Sentiment, identificada en forexfactory.com), y la Regla N°5 del
> plan operativo indica: en noticias de mediano impacto (carpeta naranja),
> no se debe abrir ninguna operación durante la ventana de 3 minutos antes
> a 3 minutos después de la publicación (aumento de spread/slippage). Si
> para el momento de la publicación existe una operación abierta, es válido
> mantenerla. Se pueden tomar entradas luego de la publicación, al MISMO
> precio que ofreció la vela de entrada creada dentro de la ventana de no
> operativa -- solo si el precio no alcanzó antes el SL durante el
> bloqueo."

Confirma exactamente la hipótesis que ya habíamos armado sin saber la causa
exacta. Mecanismo real, documentado, e implementable a futuro (requiere
calendario económico -- no automatizado todavía, Forex Factory no tiene
API gratuita confiable).

## PDFs actualizados enviados junto con estas respuestas

Fabian aclaró que actualizó ambos documentos ("le he hecho pequeños ajustes
a algunos puntos") -- en la práctica son cambios grandes, no chicos:

- **Plan Operativo**: ahora define 3 sesiones habilitadas (antes solo 1):
  Pre New York (07:00-09:00 NY), New York (09:02-11:00 NY, la ya conocida),
  y Asia (20:02-22:00 NY). También amplía noticias no-operables a CNY/JPY
  además de USD, agrega receso de fin de año (3ra semana dic. a 3ra semana
  ene.), y detalla la Regla N°5 de noticias de mediano impacto completa.
- **Plan Técnico**: agrega una regla de flexibilidad para la envolvente
  clásica (si el cuerpo queda a menos de 0,01% del 85%, se puede validar
  igual -- pero SOLO si el resultado semanal acumulado es positivo Y es la
  primera operación de la sesión), y confirma que el margen de ruptura del
  0,01% se mide "con cuerpo" (cierre) usando la herramienta "Rango de
  precios" de TradingView.

**Ambos PDFs actualizados quedan guardados en esta misma carpeta** junto a
los originales (no se borran los viejos, quedan como historial):
`Plan tecnico XAU (actualizado 30-08-2026).pdf` y
`Plan operativo XAU (actualizado 30-08-2026).pdf`.
