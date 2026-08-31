# Plan de organización: ManyChat + n8n + CRM liviano

Fecha: 04/08/2026
Estado: PROPUESTA — pendiente de validación de Diego antes de tocar nada en producción (WhatsApp, ManyChat, n8n).

## Contexto (equipo y canales actuales)

**Equipo (4 personas):**
- **Diego** — cirujano plástico, dueño. Prioridad #1 explícita: **atraer pacientes QUIRÚRGICOS** (no solo consultas estéticas no invasivas).
- **Saira** — secretaria. Maneja contenido de Instagram (estético y quirúrgico). También es el nombre del bot/asistente virtual en ManyChat (verificar si es la misma persona detrás del nombre del bot o coincidencia de nombre).
- **Pilar** — contenido de TikTok (mayormente estético — el contenido quirúrgico tiene problemas ahí, ver nota abajo). También responde/controla mensajes de Instagram.
- **Vanina** — maneja las cuentas de Instagram de publicidad (las mismas cuentas, pero desde el rol de pauta) — administra Meta Ads.

**Canales actuales:**
1. **ManyChat** (bot + n8n + OpenAI) — atiende Instagram/Facebook/WhatsApp general, etiqueta por interés en procedimiento (mayormente estético/no quirúrgico: rinomodelación, relleno de labios, botox, etc.). ~11.000 contactos, funcionando bien para volumen alto y bajo valor unitario por conversación.
2. **WhatsApp quirúrgico separado** — app normal de WhatsApp Business, SIN ManyChat, SIN n8n, SIN ningún tag ni registro. Recibe **70+ mensajes diarios**, atendido 100% manual (presumiblemente por Saira). Es el canal de **mayor prioridad para Diego y hoy es el más ciego de todos** — cero visibilidad de cuántos leads entran, en qué etapa están, cuántos se convierten en cirugía.

**Nota aparte (no bloqueante para este plan):** el contenido quirúrgico en TikTok "se cancela" (probablemente restricciones de política de contenido médico/quirúrgico de la plataforma) — por eso Pilar enfoca TikTok en estético. Esto es un tema de estrategia de contenido, no de CRM; lo dejamos anotado pero no es parte de este plan.

---

## Objetivo del plan

1. **Instrumentar el canal quirúrgico** (el que más importa) sin romper el flujo humano que ya funciona ahí.
2. **Unificar el dato** de todos los canales (ManyChat bot + WhatsApp quirúrgico humano) en un solo lugar con etapa de embudo, no solo interés.
3. **No sumar un CRM pago de $100-300 USD/mes** — usar lo que ya se paga (ManyChat + n8n) y sumar solo una capa de datos liviana.

---

## Fase 0 — Auditoría rápida (antes de tocar nada)

Verificar antes de decidir la Fase 1:
- [ ] ¿El número de WhatsApp quirúrgico puede migrarse a WhatsApp Business API (requisito para conectarlo a ManyChat)? Requiere confirmar con Meta/el proveedor que el número esté disponible para migrar (no todos los números en la app normal se pueden mover sin perder el historial).
- [ ] Plan actual de ManyChat: ¿permite conectar un segundo número de WhatsApp en la misma cuenta, o hace falta una segunda suscripción/workspace? (a confirmar en el panel de ManyChat o con su soporte).
- [ ] Confirmar quién administra el n8n cloud hoy (¿un tercero, una agencia, Vanina?) — necesario para saber quién ejecuta los workflows nuevos.

---

## Fase 1 — Instrumentar el canal quirúrgico (prioridad #1)

**Recomendación:** migrar el número quirúrgico a WhatsApp Business API conectado a ManyChat, pero con las automatizaciones/bot **apagadas** para ese número — Saira sigue respondiendo 100% manual, como hoy. El único cambio es la bandeja desde la que trabaja: en vez de la app de WhatsApp Business personal, usa la bandeja de ManyChat (Inbox).

**Por qué así y no con bot:** en consultas quirúrgicas el toque humano importa más que en botox/relleno — no tiene sentido automatizar respuestas ahí. Lo que falta no es automatización, es **registro**.

**Qué se gana sin cambiar el trabajo de Saira casi nada:**
- Historial completo de cada conversación, buscable
- Puede aplicar etiquetas (igual que ya hacemos en el otro número) para procedimiento + etapa
- Deja de perderse leads por rotación de personal o falta de memoria

**Si la migración de número no es viable (Fase 0 lo descarta):** alternativa mínima — Saira registra manualmente cada conversación en una vista de Airtable (nombre, teléfono, procedimiento, etapa) al cerrar el chat. Más trabajo manual, pero arranca sin tocar WhatsApp.

---

## Fase 2 — Etiquetas de etapa (además de las de procedimiento que ya existen)

Taxonomía actual: solo procedimiento (rinomodelacion, relleno de labios, implantes mamarios, lipoescultura, abdominoplastia, rinoplastia, mastopexia, Lipotransferencia, contorno mandibular, armonizacion facial, botox, etc.)

Agregar etapa de embudo (aplica a ambos canales):
- `turno_agendado`
- `turno_confirmado`
- `presupuesto_enviado`
- `paciente` (ya operado/tratado — para no tratarlo como lead nuevo en remarketing)
- `no_contesta` / `en_seguimiento`

Esto es lo que hoy no existe en ningún lado y es lo que le permite a Diego ver el embudo real, no solo "cuánta gente preguntó".

---

## Fase 3 — Capa de datos/CRM sobre n8n (en vez de pagar un CRM nuevo)

- Workflow en n8n que escucha eventos/tags de ManyChat (vía webhook) de AMBOS números (bot + quirúrgico) y los escribe en **Airtable** (~20 USD/mes — muchísimo menos que Ropofy/GoHighLevel).
- **Teléfono como clave única** → resuelve la deduplicación entre WhatsApp/Instagram/TikTok que ya veníamos viendo en el etiquetado manual (mismo paciente, 2-3 registros distintos).
- Vista tipo tablero (Kanban) en Airtable por etapa — Diego lo puede mirar de un vistazo sin entrar a ManyChat.

---

## Fase 4 — Roles sobre el sistema nuevo

- **Saira**: sigue respondiendo consultas (ahora desde la bandeja de ManyChat en vez de la app suelta), aplica etiqueta de etapa al cerrar cada conversación.
- **Pilar**: sin cambios — sigue con contenido TikTok + monitoreo de mensajes de Instagram.
- **Vanina**: se beneficia directo — puede cruzar qué campañas de pauta generan leads que después sí llegan a `turno_agendado` o `paciente`, no solo clics o mensajes.
- **Diego**: dashboard semanal en Airtable (leads quirúrgicos por semana, tasa de conversión por etapa, de dónde vienen).

---

## Próximo paso concreto

Antes de tocar producción, resolver Fase 0 (los 3 checks de arriba). Después de eso, se puede armar:
1. El detalle técnico de los workflows de n8n (para pasarle a quien administra el n8n)
2. La estructura exacta de las tablas de Airtable

**Pendiente de Diego**: confirmar quién administra el n8n hoy, y si tiene acceso al panel de configuración de números de ManyChat para chequear la Fase 0.
