# encoding: utf-8
"""
Genera el documento de estructura de campanas Meta Ads
para implantes mamarios y lipoescultura - segmentacion premium Argentina
"""

estructura = """
=============================================================
  ESTRUCTURA COMPLETA DE CAMPANAS META ADS
  Dr. Diego Rop | Cirugia Estetica
  Tratamientos: Implantes Mamarios + Lipoescultura
  Mercado: Argentina | Segmento: Alto poder adquisitivo
  Generado: 02/06/2026
=============================================================

LOGICA GENERAL
--------------
3 etapas de embudo x 2 tratamientos = 6 campanas principales
Cada campana tiene conjuntos de anuncios por segmento de audiencia
El presupuesto fluye de arriba hacia abajo segun performance

ETAPA 1 - AWARENESS (Frio)  -> objetivo: Reach / ThruPlay
ETAPA 2 - CONSIDERACION     -> objetivo: Engagement / Mensajes
ETAPA 3 - CONVERSION        -> objetivo: Conversaciones WhatsApp/IG

=============================================================
  CAPITULO 1: IMPLANTES MAMARIOS
=============================================================

--- CAMPANA 1A: IMPLANTES_AWARENESS_FRIO ---
Objetivo: Outcome Awareness | Optimizacion: ThruPlay
Presupuesto diario campana: $15.000 ARS
Genero: Mujeres
Pais: Argentina

  [CONJUNTO A1] IMPL_FRIO_PROFESIONALES_18-40
  Edad: 25-45
  Genero: Mujeres
  Segmentacion por intereses:
    - Emprendedoras / Duenas de negocio
    - LinkedIn (profesionales activas)
    - Viajes al exterior / Aerolineas premium
    - Hoteles 5 estrellas / Spa de lujo
    - Marcas de ropa premium: Zara, H&M, Mango (piso medio-alto)
    - American Express / Visa Platinum / Black
    - Compras online frecuentes
  Ubicaciones: CABA, Zona Norte GBA (San Isidro, Martinez, Tigre, Pilar)
                Rosario (zona norte), Cordoba capital, Mendoza capital
  Excluir: publico tibio (remarketing ya captado)
  Presupuesto: $6.000 ARS/dia

  [CONJUNTO A2] IMPL_FRIO_PODER_ADQUISITIVO_ALTO
  Edad: 28-50
  Genero: Mujeres
  Segmentacion por intereses:
    - Compradores de lujo (Luxury goods)
    - Viajeras frecuentes internacionales
    - Golf / Polo / Equitacion (deportes premium)
    - Propietarias (real estate de alto valor)
    - Marcas premium: Louis Vuitton, Gucci, Prada (comportamiento)
    - Restaurantes fine dining
    - Arte y cultura / Coleccionistas
  Ubicaciones: CABA (Palermo, Recoleta, Belgrano, Nuñez, Puerto Madero)
               San Isidro, Nordelta, Countries del GBA Norte
  Excluir: publico tibio
  Presupuesto: $5.000 ARS/dia

  [CONJUNTO A3] IMPL_FRIO_MUJERES_FITNESS
  Edad: 22-38
  Genero: Mujeres
  Segmentacion por intereses:
    - Fitness premium / CrossFit / Pilates
    - Nutricion y dietas (interesadas en su cuerpo)
    - Ropa deportiva premium (Lululemon, Gymshark)
    - Cosmetica y beauty premium
    - Seguidoras de ciruganos esteticos (comportamiento)
    - Bienestar y autocuidado
  Ubicaciones: Todo Argentina
  Excluir: publico tibio
  Presupuesto: $4.000 ARS/dia


--- CAMPANA 1B: IMPLANTES_CONSIDERACION_TIBIO ---
Objetivo: Outcome Engagement | Optimizacion: Conversations
Presupuesto diario campana: $12.000 ARS
Genero: Mujeres

  [CONJUNTO B1] IMPL_TIBIO_VIO_VIDEO_50PCT
  Audiencia personalizada: vio el 50%+ de cualquier video de implantes (ultimos 60 dias)
  Edad: 18-55
  Excluyendo: quienes ya enviaron mensaje
  Presupuesto: $4.500 ARS/dia

  [CONJUNTO B2] IMPL_TIBIO_INTERACCION_PERFIL
  Audiencia personalizada: interactuo con el perfil de Instagram (ultimos 60 dias)
  + visito el sitio web (si hay pixel)
  Edad: 18-55
  Excluyendo: quienes ya enviaron mensaje
  Presupuesto: $4.000 ARS/dia

  [CONJUNTO B3] IMPL_TIBIO_SIMILAR_CLIENTES
  Audiencia similar (Lookalike 1%): basada en lista de clientes actuales
  Edad: 25-50 | Mujeres
  Ubicaciones: Argentina
  Presupuesto: $3.500 ARS/dia


--- CAMPANA 1C: IMPLANTES_CONVERSION_CALIENTE ---
Objetivo: Outcome Leads | Optimizacion: Conversations (WhatsApp + IG DM)
Presupuesto diario campana: $8.000 ARS
Genero: Mujeres

  [CONJUNTO C1] IMPL_CALIENTE_RETARGETING_ACTIVO
  Audiencia: vio video 75%+ O guardo algun anuncio O hizo click O envio mensaje (ultimos 30 dias)
  Excluyendo: clientes actuales
  Presupuesto: $5.000 ARS/dia
  ANUNCIO: oferta concreta, testimonio, CTA directo WhatsApp

  [CONJUNTO C2] IMPL_CALIENTE_LISTA_EXCLUIDOS
  Audiencia: quienes consultaron pero NO reservaron (lista manual o CRM)
  Presupuesto: $3.000 ARS/dia
  ANUNCIO: urgencia, respuesta a objeciones comunes ("precio", "recuperacion")


=============================================================
  CAPITULO 2: LIPOESCULTURA
=============================================================

--- CAMPANA 2A: LIPO_AWARENESS_FRIO ---
Objetivo: Outcome Awareness | Optimizacion: ThruPlay
Presupuesto diario campana: $15.000 ARS
Genero: Mujeres y Hombres (separados en conjuntos)

  [CONJUNTO D1] LIPO_FRIO_MUJERES_PREMIUM_25-45
  Edad: 25-45 | Mujeres
  Segmentacion:
    - Dietas y nutricion (interes activo en bajar de peso)
    - Fitness y gym premium
    - Moda y tendencias corporales
    - Antes y despues (beauty transformation)
    - Compradores online de alto valor
    - Tarjetas Amex / Visa Platinum
    - Viajes al exterior (poder adquisitivo)
    - Mujeres empresarias / profesionales independientes
  Ubicaciones: CABA + GBA Norte + Rosario + Cordoba
  Presupuesto: $6.000 ARS/dia

  [CONJUNTO D2] LIPO_FRIO_MUJERES_POSTPARTO_28-42
  Edad: 28-42 | Mujeres
  Segmentacion:
    - Madres con hijos pequenos (comportamiento)
    - Interesadas en recuperacion postparto
    - Fitness postparto / yoga mama
    - Bienestar y confianza corporal
    - Seguidoras de contenido de transformacion corporal
  Ubicaciones: CABA + GBA + principales ciudades
  Presupuesto: $4.000 ARS/dia

  [CONJUNTO D3] LIPO_FRIO_HOMBRES_PREMIUM_28-50
  Edad: 28-50 | Hombres
  Segmentacion:
    - Fitness y musculacion premium
    - Ropa masculina premium
    - Deportes de alto rendimiento
    - Emprendedores y ejecutivos
    - Viajes frecuentes / business class
    - Interesados en cirugia estetica masculina (ginecomastia, abdominoplastia)
  Ubicaciones: CABA + GBA + Rosario + Cordoba
  Presupuesto: $5.000 ARS/dia


--- CAMPANA 2B: LIPO_CONSIDERACION_TIBIO ---
Objetivo: Outcome Engagement | Optimizacion: Conversations
Presupuesto diario campana: $10.000 ARS

  [CONJUNTO E1] LIPO_TIBIO_VIO_VIDEO_50PCT
  Audiencia: vio 50%+ de videos de lipoescultura (ultimos 60 dias)
  Presupuesto: $4.000 ARS/dia

  [CONJUNTO E2] LIPO_TIBIO_INTERACCION_PERFIL
  Audiencia: interactuo con perfil IG/FB (ultimos 60 dias)
  Presupuesto: $3.500 ARS/dia

  [CONJUNTO E3] LIPO_TIBIO_SIMILAR_CLIENTES_LIPO
  Lookalike 1%: basada en clientes de lipoescultura
  Presupuesto: $2.500 ARS/dia


--- CAMPANA 2C: LIPO_CONVERSION_CALIENTE ---
Objetivo: Outcome Leads | Optimizacion: Conversations
Presupuesto diario campana: $8.000 ARS

  [CONJUNTO F1] LIPO_CALIENTE_RETARGETING_ACTIVO
  Audiencia: maximo engagement (75%+ video, guardados, clicks) ultimos 30 dias
  Presupuesto: $5.000 ARS/dia

  [CONJUNTO F2] LIPO_CALIENTE_OBJECIONES
  Audiencia: consultas previas sin reserva
  Presupuesto: $3.000 ARS/dia


=============================================================
  PRESUPUESTO TOTAL DIARIO
=============================================================

  Implantes Mamarios:
    Campana 1A Awareness:     $15.000 ARS/dia
    Campana 1B Consideracion: $12.000 ARS/dia
    Campana 1C Conversion:     $8.000 ARS/dia
    SUBTOTAL IMPLANTES:       $35.000 ARS/dia

  Lipoescultura:
    Campana 2A Awareness:     $15.000 ARS/dia
    Campana 2B Consideracion: $10.000 ARS/dia
    Campana 2C Conversion:     $8.000 ARS/dia
    SUBTOTAL LIPO:            $33.000 ARS/dia

  TOTAL DIARIO:               $68.000 ARS/dia (~$68 USD al cambio blue)
  TOTAL MENSUAL:           ~$2.040.000 ARS/mes

  NOTA: estos son presupuestos recomendados para maxima eficiencia.
  Se puede escalar desde $30.000 ARS/dia total e ir subiendo segun resultados.
  El ratio ideal: 40% Awareness / 35% Consideracion / 25% Conversion

=============================================================
  COPIES RECOMENDADOS POR ETAPA
=============================================================

--- IMPLANTES MAMARIOS ---

[AWARENESS - Gancho emocional]
"Tu cuerpo. Tus reglas.
El aumento mamario que siempre quisiste, ahora al alcance de tu mano.
Dr. Diego Rop - Cirujano especialista"

[CONSIDERACION - Prueba social + diferencial]
"Mas de [X] pacientes ya transformaron su figura con nosotros.
Tecnica premium. Recuperacion rapida. Resultados naturales.
Consulta gratuita y sin compromiso."

[CONVERSION - CTA directo]
"Hoy podes dar el primer paso.
Turnos de consulta disponibles esta semana.
Respondemos en menos de 2 horas.
>> Escribinos por WhatsApp"

--- LIPOESCULTURA ---

[AWARENESS - Aspiracional]
"Lipoescultura de alta definicion.
No es solo sacar grasa. Es esculpir tu figura.
Resultados permanentes. Cirugia ambulatoria."

[CONSIDERACION - Educativo + confianza]
"¿Sabes la diferencia entre liposuccion y lipoescultura?
La lipoescultura remodela y define. No solo extrae.
Te explicamos todo en una consulta sin costo."

[CONVERSION - Urgencia real]
"Esta semana tenemos turnos quirurgicos disponibles.
Si ya lo estabas pensando, este es el momento.
>> Escribinos y te cotizamos sin compromiso"

=============================================================
  CREATIVIDADES RECOMENDADAS
=============================================================

FORMATO GANADOR: Reel vertical 9:16, 15-30 segundos

PARA AWARENESS:
  - Antes/despues con transicion elegante (no grafico, estetico)
  - Testimonial real de paciente (con permiso)
  - "Un dia en la clinica" mostrando el proceso humanizado
  - El doctor explicando el procedimiento en 30 seg (autoridad)

PARA CONSIDERACION:
  - FAQ en formato rapido: "3 preguntas frecuentes sobre implantes"
  - Comparativa: mitos vs realidad
  - Testimonial mas largo (60 seg) con resultado final

PARA CONVERSION:
  - Oferta especifica o turno disponible
  - CTA muy claro: "Escribinos HOY" con numero visible
  - Urgencia real: "quedan X turnos esta semana"

NOTA: Evitar imagenes de operaciones o sangre (viola politicas de Meta)
Usar siempre cuerpos post-operados ya recuperados o animaciones/graficos

=============================================================
  NAMING CONVENTION DEFINITIVA
=============================================================

Campana:   [TRATAMIENTO]_[ETAPA]_[FECHA_INICIO]
           Ej: IMPL_AWARENESS_202606

Conjunto:  [TRATAMIENTO]_[TEMP]_[SEGMENTO]_[EDAD]
           Ej: IMPL_FRIO_PROFESIONALES_25-45

Anuncio:   [TRATAMIENTO]_[FORMATO]_[VARIANTE]_[FECHA]
           Ej: IMPL_REEL_TESTIMONIO_A_202606

=============================================================
  METRICAS A MONITOREAR (revisar 2x por semana)
=============================================================

Awareness:    CPM < $2.500 ARS | Alcance unico | ThruPlay rate > 20%
Consideracion: CTR > 1,5% | Costo por mensaje < $500 ARS
Conversion:   Costo por consulta < $2.000 ARS | Tasa respuesta > 60%

SEÑAL DE ALARMA: si un conjunto gasta 3 dias sin resultados -> pausar
SEÑAL DE ESCALAR: si CPA < 50% del objetivo -> duplicar presupuesto

=============================================================
  PROXIMOS PASOS (orden de implementacion)
=============================================================

SEMANA 1:
  [ ] Crear audiencias personalizadas en Meta:
      - Lista de clientes actuales (subir CSV)
      - Visitantes sitio web (si hay pixel)
      - Interacciones con perfil IG (90 dias)
      - Vistas de video 50%+ (60 dias)
  [ ] Crear lookalike 1% de lista de clientes

SEMANA 2:
  [ ] Lanzar Campanas Awareness (1A y 2A) primero
  [ ] Grabar/preparar 2-3 Reels nuevos por tratamiento
  [ ] Configurar naming convention en todas las campanas existentes

SEMANA 3:
  [ ] Lanzar Campanas de Consideracion (1B y 2B)
  [ ] Revisar metricas de awareness y ajustar

SEMANA 4:
  [ ] Lanzar Campanas de Conversion (1C y 2C)
  [ ] Primer analisis de embudo completo

"""

output_path = "marketing/analisis/estructura_campanas_premium_202606.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(estructura)

print(f"Estructura guardada en: {output_path}")
print(f"Total de caracteres: {len(estructura):,}")
