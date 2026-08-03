# encoding: utf-8
"""
Analisis de segmentacion geografica e intereses
para clinica en Palermo, CABA - Cirugia Estetica
"""

report = """
=============================================================
  ANALISIS DE AUDIENCIAS GEOGRAFICAS
  Clinica en Palermo, CABA
  Procedimientos: Rino, Labios, Implantes, Lipo
=============================================================

PODER ADQUISITIVO POR ZONA - ARGENTINA
(relevante para cirugia estetica, valor ticket alto)

ZONA          | PODER ADQ. | DISTANCIA | RECOMENDACION
---------------------------------------------------------------------------
CABA completa |  Alto-Medio |    0 km   | SIEMPRE incluir
GBA Norte     |   Alto      |  20-50 km | PRIORIDAD #1
GBA Sur       |   Medio-Bajo|  15-40 km | Solo conjuntos amplios
GBA Oeste     |   Medio     |  20-45 km | Incluir con moderacion
La Plata      |   Medio     |   60 km   | SI (ya tienen pacientes)
Uruguay       |   Medio-Alto| 200+ km   | Campana separada (gran oportunidad)


GBA NORTE - LOS BARRIOS/MUNICIPIOS MAS VALIOSOS
------------------------------------------------
San Isidro       -> el mejor municipio del GBA para este servicio
Martinez         -> zona residencial premium
Olivos           -> alta concentracion de profesionales
Vicente Lopez    -> muy bueno
Acassuso         -> residencial premium
Beccar           -> clase alta
Nordelta/Tigre   -> countries, muy alto poder adquisitivo
Pilar            -> countries premium (Haras, Santa Barbara, etc.)
La Horqueta      -> excelente


CABA - BARRIOS CON MEJOR PERFIL PARA CIRUGIA ESTETICA
-------------------------------------------------------
Palermo          -> tu ubicacion, excelente
Recoleta         -> top 1, maximo poder adquisitivo
Belgrano         -> muy bueno
Nunez            -> bueno
Puerto Madero    -> excelente pero chico
Las Canitas      -> bueno
Villa Urquiza    -> bueno
Colegiales       -> bueno
Caballito        -> medio-alto, gran volumen


POR QUE URUGUAY ES UNA GRAN OPORTUNIDAD
-----------------------------------------
1. Tipo de cambio: los procedimientos en Argentina les salen 30-50% mas baratos
2. Ya tienen 2 clinicas top en Montevideo (Garber, Zibell) pero
   la demanda supera la oferta y los tiempos de espera son largos
3. El uruguayo viaja a BsAs con frecuencia (puente aereo barato)
4. CPM en Uruguay es MAS BAJO que en Argentina (menos competencia publicitaria)
5. Perfil: mujer 28-50, clase media-alta, con capacidad de viajar
6. Instagram es muy usado en Uruguay para este tipo de busquedas

COMPETENCIA EN ARGENTINA (lo que hacen la mayoria)
---------------------------------------------------
- Targetean "Argentina" o "Buenos Aires" de forma generica -> desaprovechan presupuesto
- No diferencian GBA Norte de GBA Sur -> malgastan en zonas de bajo retorno
- No targetean Uruguay -> estan dejando un mercado libre
- Usan el mismo anuncio para 18-20 anos que para 40-50 -> mensaje equivocado
- No excluyen zonas de muy bajo poder adquisitivo -> bajo CTR, sube el CPM

NUESTRA VENTAJA COMPETITIVA
-----------------------------
- Segmentar GBA NORTE especificamente (San Isidro, Olivos, Martinez)
- Campana separada para Uruguay
- Mensajes diferenciados por edad (18-28 vs 29-45 vs 45-55)
- Incluir La Plata con radio de ciudad (ya hay base de pacientes)

"""

output_path = "marketing/analisis/audiencias_geograficas_202606.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(report)
print("Analisis guardado.")
