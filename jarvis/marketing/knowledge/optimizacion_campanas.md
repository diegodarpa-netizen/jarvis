# Optimización de Campañas Meta Ads — Protocolos y Decisiones

## Cuándo Optimizar, Pausar o Escalar

### Regla de los 3 Días / 3x CPL
Antes de tomar decisiones sobre un ad set nuevo, darle mínimo:
- **3 días de datos** (el algoritmo de Meta necesita tiempo para optimizar)
- **Mínimo 3x el CPL objetivo** en gasto (si el CPL objetivo es $15, necesitás gastar $45 antes de juzgar)
- **Mínimo 50 eventos de optimización** (si usás leads, necesitás ver 50 leads antes de escalar)

### Señales para PAUSAR un ad set
- CPL > 3x el benchmark del procedimiento por más de 5 días
- CTR < 0.5% consistentemente
- Frecuencia > 7 (saturación de audiencia)
- CPC > $5 USD en campañas de consideración
- 0 conversiones con $3x CPL gastado

### Señales para ESCALAR un ad set
- CPL < 80% del benchmark por 3+ días
- ROAS > 20 sostenido
- CTR > 3% y estable
- Frecuencia < 3 (audiencia no saturada)
- Costo por contacto calificado estable

### Cómo escalar (sin matar el rendimiento)
1. **Regla del 20%:** Subir el presupuesto máximo 20% por vez, esperar 3 días antes de volver a subir
2. **Duplicar el ad set:** Crear copia exacta con el mismo presupuesto en paralelo
3. **Expandir audiencia:** Aumentar el rango de edad o agregar intereses similares
4. **Lookalike:** Crear Lookalike de los que ya convirtieron y escalar ahí

---

## Protocolo de Testing Semanal

### Semana 1: Testing de Audiencias
Testear 3 ad sets diferentes con el mismo creative:
- Ad Set A: Intereses belleza + cuidado personal (amplio)
- Ad Set B: Intereses específicos del procedimiento
- Ad Set C: Lookalike 1-2% de clientes actuales

### Semana 2: Testing de Creatividades
Con la audiencia ganadora, testear 3 creatividades:
- Creative A: Video con hook emocional
- Creative B: Carrusel educativo
- Creative C: Imagen estática con copy largo

### Semana 3: Testing de Copy
Con audiencia + creative ganadores, testear:
- Copy A: Enfocado en el beneficio emocional
- Copy B: Enfocado en credenciales y seguridad
- Copy C: Enfocado en el proceso y la facilidad

### Semana 4: Scaling
Escalar lo que ganó en las 3 semanas anteriores.

---

## Estructura de Audiencias

### Audiencias Frías (primera vez que ven la clínica)
**Nivel 1 — Más amplio:**
- Mujeres 22-45 años, Buenos Aires, GBA, CABA
- Intereses: Belleza, Maquillaje, Moda femenina, Cuidado personal
- Excluir: Personas que interactuaron con la página en los últimos 180 días

**Nivel 2 — Más específico:**
- Mujeres 22-45, misma geo
- Intereses: Cirugía estética, Procedimientos estéticos, Medicina estética
- (Audiencia más pequeña pero más calificada)

**Nivel 3 — Comportamientos premium:**
- Mujeres 25-50, misma geo
- Comportamientos: Compradores frecuentes online, Usuarios de iPhone, Viajeros frecuentes
- Ingresos estimados altos

### Audiencias Tibias (consideración)
- Visitantes del sitio web (últimos 30, 60, 90 días)
- Personas que interactuaron con Instagram (últimos 60 días)
- Personas que vieron >50% de algún video (últimos 60 días)
- Lista de emails de leads previos (Custom Audience)

### Audiencias Calientes (retargeting)
- Visitantes que llegaron a la página de contacto pero no completaron
- Leads que no respondieron al primer contacto (últimos 14 días)
- Personas que abrieron el formulario de Meta pero no completaron

### Lookalike Audiences (usar cuando hay suficiente data)
- LAL 1%: de clientes actuales (lista de emails/teléfonos)
- LAL 1-3%: de visitantes web de los últimos 90 días
- LAL 1%: de leads que se convirtieron en pacientes

---

## Decisiones de Optimización por Métrica

### CPL demasiado alto
**Diagnóstico:**
- ¿CTR bajo? → Problema con la creatividad/copy
- ¿CTR alto pero CPL alto? → Problema con la landing o el formulario
- ¿Frecuencia alta? → Audiencia saturada
- ¿CPM muy alto? → Audiencia demasiado pequeña o competitiva

**Acciones:**
1. Revisar y cambiar creatividad (si CTR < 1%)
2. Ampliar audiencia (si frecuencia > 5)
3. Cambiar el objetivo de conversión
4. Agregar variantes de copy

### CTR muy bajo (< 1%)
**Causas comunes:**
- Hook visual no genera curiosidad
- La imagen no detiene el scroll
- Copy no resuena con la audiencia
- Creatividad saturada (frecuencia alta)

**Acciones:**
1. Cambiar imagen/video con hook más disruptivo
2. Testear copy más emocional vs más directo
3. Reducir el texto en la imagen
4. Rotar creatividades (máx 3-4 semanas por creative)

### Leads de baja calidad
**Síntomas:**
- Muchos leads que no responden
- Leads que no pueden pagar
- Leads de otras ciudades/países

**Acciones:**
1. Agregar pre-calificación en el formulario: "¿Tenés consulta médica previa?" / "¿En qué zona de Buenos Aires estás?"
2. Segmentar más la audiencia (excluir fuera del GBA)
3. Cambiar el mensaje a uno que filtre por precio percibido ("atención premium", "cirujano certificado")
4. Usar Lead Score: darle prioridad a leads que completan todos los campos

---

## Ciclo de Vida de una Creatividad

### Señales de fatiga de anuncio:
- Frecuencia > 5 y CTR baja 30% vs. primera semana
- Costo por resultado sube >50% vs. primera semana
- Engagement baja (menos likes, comments, shares)

### Cuándo refrescar:
- Regla general: refrescar creatividades cada 3-4 semanas
- Si hay fatiga (señales de arriba): refrescar inmediatamente
- Para audiencias más pequeñas (<50k personas): refrescar cada 2 semanas

### Cómo refrescar sin perder aprendizaje:
- Opción 1: Duplicar el ad set, nuevo creative, misma audiencia
- Opción 2: Subir nueva creatividad dentro del mismo ad set
- Opción 3: Testear variación del mismo concepto (mismo hook, diferente imagen)

---

## Optimización del Proceso de Leads

### La velocidad de respuesta es el factor #1 de conversión
- Responder en < 15 minutos → 3x más probabilidad de conversión
- Responder en < 1 hora → 2x más
- Responder después de 4 horas → tasas normales o menores

### Proceso óptimo de gestión de leads:
1. **Lead entra por Meta Forms / WhatsApp**
2. **Respuesta automática inmediata** (bot o mensaje guardado): agradecimiento + "en X minutos te contactamos"
3. **Humano responde en < 15 min**: calificación, info, oferta de consulta
4. **Agendar consulta** en el mismo primer contacto si es posible
5. **Recordatorio automático** 24 hs antes de la consulta

### Template de seguimiento para leads que no respondieron:

**Día 1 (mismo día, si no respondió en 2 horas):**
"Hola [Nombre]! 😊 Te escribo de [Clínica] por tu consulta sobre [procedimiento]. ¿Tenés alguna pregunta que pueda responderte yo o querés hablar directamente con el doctor?"

**Día 3 (si sigue sin responder):**
"Hola [Nombre], no queremos perderte 🙂 Si todavía tenés dudas sobre [procedimiento], el Dr. [apellido] tiene turnos disponibles esta semana. ¿Te cuento más?"

**Día 7 (último intento):**
"[Nombre], entendemos que la decisión lleva su tiempo. Cuando estés lista, acá estamos. Te mando [contenido de valor: guía del procedimiento]."

---

## Herramientas y Recursos Meta Ads

### Dentro de Meta:
- **Ads Manager:** gestión principal
- **Meta Pixel:** tracking de conversiones en sitio web
- **Conversions API (CAPI):** envío server-side de eventos (más confiable post iOS 14)
- **Meta Advantage+:** campaña automatizada (buen punto de partida)
- **Campaign Budget Optimization (CBO):** Meta distribuye el presupuesto entre ad sets
- **Ad Set Budget Optimization (ABO):** vos controlás el budget por ad set (mejor para testing)

### Configuración técnica recomendada:
- Instalar Pixel en el sitio web → mínimo eventos: PageView, ViewContent, Lead, Contact
- Habilitar Conversions API para mayor precisión de datos
- Conectar WhatsApp Business con Meta (para tracking de mensajes)
- Crear Custom Conversions para eventos específicos del sitio

### Para seguimiento y análisis:
- UTM parameters en todos los links
- Google Analytics 4 como capa adicional de datos
- Planilla de seguimiento semanal de KPIs

---

## Errores Clásicos en Cuentas de Clínicas Estéticas

1. **Cambiar la campaña antes de que tenga datos suficientes** — El algoritmo necesita tiempo. Mínimo 3-7 días antes de juzgar.

2. **Una sola creatividad por ad set** — Siempre tener 2-3 creatividades activas para que Meta optimice.

3. **No usar retargeting** — Las personas que ya visitaron el sitio son las más baratas de convertir.

4. **Público demasiado pequeño** — Audiencias < 100.000 personas en Argentina suelen subir el CPM significativamente.

5. **Usar solo segmentación por intereses** — Combinar intereses + Lookalike + Custom Audiences.

6. **No separar objetivos de campaña** — Una campaña para awareness y otra para conversión. No mezclar.

7. **Ignorar la calidad de los leads** — Muchos leads baratos que no convierten = problema en la segmentación o en el proceso de ventas.

8. **No testear sistemáticamente** — Sin testing, no hay aprendizaje. Sin aprendizaje, siempre dependés de "lo que crees que funciona".

9. **No tener seguimiento del proceso de ventas** — El CPL no dice todo. ¿Cuántos leads se convierten en consultas? ¿Cuántas consultas en cirugías?

10. **Parar la publicidad en temporada baja** — La temporada baja es el momento de construir audiencias a menor costo para la temporada alta.
