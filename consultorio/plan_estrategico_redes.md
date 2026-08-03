# Plan estratégico — Gestión integral de redes del Dr. Diego Rodríguez

Documento vivo. Se actualiza a medida que se suman plataformas, herramientas y datos reales. Pensado como lo armaría una agencia de marketing médico llevando la cuenta completa: contenido, publicidad, mensajería y reputación en un solo lugar.

---

## 1. Estructura de la cuenta (pilares)

| Pilar | Qué controla | Skill / archivo asociado |
|---|---|---|
| **Contenido y edición** | Qué se publica, en qué formato, calidad de edición, calendario | `contenido-redes` (skill) + `consultorio/redes/calendario/` |
| **Publicidad (Ads)** | Campañas de Meta Ads (y a futuro TikTok Ads), eficiencia, presupuesto | `analizar-campanas` (skill) + `marketing/meta/` |
| **Mensajería / CRM** | Mensajes entrantes (orgánicos y de publicidad), leads, respuesta | `reporte-mensajes` (skill) + ManyChat + `consultorio/reportes/` |
| **Comentarios y reputación** | Respuesta a comentarios, detección de riesgos (estafas, mala praxis percibida) | Auditoría de comentarios (`consultorio/redes/auditoria_comentarios_*.md`) |
| **Equipo** | Quién hace qué, responsables por plataforma | `consultorio/equipo/equipo.json` |

Cada plataforma nueva que sumes se integra a estos mismos 5 pilares — no se arma una estructura nueva por red social, se agrega como una fila más dentro de cada pilar existente.

---

## 2. Estado actual por plataforma (relevado 27/07/2026)

| Plataforma | Volumen mensual real | Estado |
|---|---|---|
| **TikTok** (@drdiegor) | ~50-60 publicaciones/mes, 88,9K seguidores | Fuerte en alcance viral. Formato ganador: **Rinomodelación** (60% de los posts top, más vistas totales). Comentarios sin responder de forma sistemática. |
| **Instagram** (@drdiegorop.cirugiaplastica) | 76+ publicaciones/mes, 28,6K seguidores | Mayor volumen de publicación que TikTok. Mismo problema de comentarios sin responder. Cuenta con historial de checkpoint de seguridad (ver nota de riesgo abajo). |
| **Facebook** (Clínica Estética Darpa) | Contenido espejo de Instagram | Irrelevante como canal propio — solo 1,8% del alcance total en la muestra verificada. No requiere gestión separada. |
| **WhatsApp Business** | ~127 mensajes nuevos/día (vía ManyChat) | Canal de mayor volumen de mensajería. |
| **Meta Ads** | $3,4M ARS gastados en 30 días → 3.773 contactos nuevos, $906/contacto promedio | Campaña "Interacción Rino 1\|7" es la más eficiente ($397/contacto); ver `marketing/meta/reportes/`. |

**A sumar cuando Diego las pase:** YouTube (canal ya identificado, sin datos cargados), y cualquier otra red nueva.

---

## 3. Contenido y edición

### 3.1 Qué ya sabemos que funciona
- Formato **Rinomodelación** domina en TikTok (60% del top, mayor volumen de vistas por lejos).
- Contenido de humor/tendencias (memes, cross-promos) genera alcance pero **poco lead real** — sirve para awareness, no para conversión directa.
- Contenido educativo directo ("Rinomodelación sin cirugía: qué es y resultados esperados") genera preguntas de alta intención (ubicación, precio, duración) que hoy se están perdiendo por falta de respuesta.

### 3.2 CapCut — integración pendiente de definir
Diego mencionó que va a dar acceso a CapCut para mejorar la edición. Antes de avanzar necesito precisar **qué tipo de acceso** es posible, porque cambia totalmente cómo se puede ayudar:

- **Si es acceso a la cuenta (login/contraseña):** no puedo iniciar sesión en CapCut ni en ninguna plataforma en tu nombre — es una restricción dura de seguridad, sin excepción.
- **Si es compartir archivos** (proyectos `.capcut`, plantillas, exports, la carpeta de assets): sí puedo trabajar con eso — analizar qué plantillas/transiciones se repiten en el contenido que mejor funciona, sugerir mejoras de ritmo/corte basadas en lo que ya sabemos que retiene (gancho de los primeros segundos, formato antes/después), y armar guías de edición para que el equipo las siga.
- **Si CapCut tiene una API o integración de automatización** (no es algo estándar en la versión de consumidor, habría que confirmarlo): se podría explorar automatizar exports o aplicar plantillas en lote, pero esto requiere investigación previa antes de prometerlo.

*(Pendiente: definir con Diego cuál de estas tres aplica.)*

### 3.3 Próximo paso concreto
Cuando se resuelva el checkpoint de Instagram y Diego confirme el tipo de acceso a CapCut, la skill `contenido-redes` pasa a incluir: análisis de qué plantillas/duración/ritmo de edición correlaciona con mejor retención, comparando los posts que más y menos funcionaron.

---

## 4. Publicidad — orgánico + pago en un solo tablero

El objetivo es que Diego vea **un solo número de "costo por lead"**, sin importar si el lead vino de un comentario orgánico o de una campaña paga.

| Fuente | Cómo se mide hoy | Automatizable |
|---|---|---|
| Meta Ads (pago) | `analizar-campanas`: costo por nuevo contacto de mensaje, por campaña | Sí — ya funciona con exports de Ads Manager |
| Mensajes orgánicos (WhatsApp/IG/TikTok) | `reporte-mensajes`: filtro de ManyChat por "última interacción" | Parcial — requiere armar tags por fecha (pendiente, ver sección 6) |
| Comentarios orgánicos con intención de compra | Auditoría manual (ver `auditoria_comentarios_2026-07.md`) | No automatizado todavía — ver sección 5 |

**Regla de oro que ya aprendimos hoy:** cuando una campaña se optimiza para "clics en el enlace" en vez de "conversación de mensaje", el costo por resultado parece bueno pero el costo real por lead de mensajería es mucho peor (caso real: "Interacción 20\|5 Vani", $27 por clic pero $2.401 por contacto real — la pausamos por esto). Toda campaña nueva se revisa primero por su **objetivo de optimización**, no solo por el costo por resultado.

**Oportunidad detectada hoy (viralización → pauta):** al revisar TikTok Studio encontramos publicaciones viejas (enero, abril) que están resurgiendo con miles de vistas nuevas por semana sin gastar un peso en publicidad. Esto es una señal real: cuando un video viejo empieza a repuntar orgánicamente, es el momento de meterle presupuesto antes de que se enfríe — vale la pena chequear esto cada vez que se revisen las campañas.

---

## 5. Comentarios — automatización de respuestas

Diego pidió explorar si se puede automatizar la respuesta a comentarios. Esto es técnicamente distinto de automatizar mensajes directos (que ya hace ManyChat). Antes de prometer algo, hay que confirmar qué permite cada plataforma:

- **ManyChat tiene una función específica para esto** ("Comment Growth Tool" / automatización de comentarios de Instagram): cuando alguien comenta una palabra clave en un posteo (ej. "info"), el sistema responde automáticamente el comentario público *y* le manda un DM con más información. Esto está disponible en el plan que Diego ya tiene contratado — **es el camino más directo y rápido para resolver el problema real que encontramos en la auditoría de hoy**.
- **TikTok** no tiene una automatización de comentarios nativa tan robusta ni integración con ManyChat para esto — ahí la respuesta seguiría siendo manual del equipo, al menos por ahora.
- Esto no reemplaza necesitar que una persona responda lo que la automatización no cubra (preguntas fuera de las palabras clave configuradas, casos sensibles como la pregunta de una menor de edad que encontramos hoy) — sirve para los pedidos repetitivos de "info"/"precio"/"ubicación", no para reemplazar al equipo humano.

**Próximo paso concreto:** configurar el Comment Growth Tool de ManyChat para Instagram, empezando por las palabras clave que más se repiten en los comentarios sin responder que ya identificamos (info, precio, dónde, cuánto dura).

---

## 6. Pendientes estructurales (de sesiones anteriores, siguen en pie)

1. Armar tags automáticos en ManyChat por fecha (contar mensajes de forma confiable) y por interés/procedimiento (segmentar para remarketing).
2. Terminar de completar `consultorio/data/perfil_consultorio.json` (ciudad, contacto, horario de reportes).
3. Revisar por qué la campaña "Ventas foto 17\|6" figura como Rechazada en Ads Manager.
4. Decidir si limpiar las campañas de Meta Ads sin actividad (19 de 27 no gastaron nada en el último mes).
5. Resolver el checkpoint de verificación de identidad de Instagram (bloquea auditorías más profundas de esa cuenta).

---

## 7. Cómo se suman redes nuevas

Cuando Diego pase una red nueva, el proceso es:
1. Cargarla en `consultorio/competencia/perfiles/` (si es competencia) o `consultorio/data/perfil_consultorio.json` (si es propia).
2. Confirmar si es propiedad de Meta (requiere navegación manual de Diego, no automatizada) o no (se puede manejar con el browser automatizado sin riesgo).
3. Integrarla a los 5 pilares de la sección 1 — no se crea estructura nueva.

---

## Notas de seguridad que rigen todo este plan

- Nunca se navega de forma automatizada por Instagram, Facebook o WhatsApp Business con la cuenta real logueada de Diego — ya causó un checkpoint de verificación de identidad el 27/07/2026. TikTok no tiene este riesgo.
- Nunca se ingresan credenciales (usuario/contraseña) de ninguna plataforma en nombre de Diego, incluyendo CapCut.
- Cambios de presupuesto o pausado de campañas los ejecuta Diego manualmente, con confirmación antes de darlos por hechos en los reportes.
