# Log de etiquetado retroactivo — ManyChat

Registro de cada contacto etiquetado manualmente (revisión de conversación real, no automatización).
Objetivo: etiquetar TODOS los contactos existentes (~10.000) por interés/procedimiento, en lotes continuos, para poder usarlos en campañas de remarketing de Meta/Instagram.

Formato por fila: `Nombre | chat_id | etiquetas aplicadas | nota`

## Pendientes de corrección conocidos (de sesiones anteriores)
- Constanza (chat_id 592712513) | fox eyes + blefaroplastia espurios, NO se pudieron quitar (ver bug abajo). Falta agregar "relleno de menton" (mencionado explícitamente, correcto según conversación). rinomodelacion sí es correcto, se mantiene.
- Yesica Ferreyra | armonizacion facial espuria detectada, pendiente de corregir

## 🔴 ERROR CONFIRMADO EN VIVO (01/08/2026)
- **𝓓𝓪𝓲🖤** (chat_id 811885872, Instagram) | Preguntó por "labios" → correspondía "relleno de labios". Un click mal targeteado en el dropdown aplicó por error **"blefaroplastia"** en su lugar. Ya se agregó "relleno de labios" (correcto). Falta SOLO quitar "blefaroplastia" (varios intentos de remoción fallaron — bug de UI, ver abajo). Queda con una etiqueta de más, pendiente de que Diego la quite manualmente.
- **Agostina Franco** (chat_id 1565074963, Instagram) | Preguntó por precio de "sirugia de mamas" → correspondía "implantes mamarios". Mismo patrón de misclick (segundo click del doble-intento cayó sobre un ítem ya visible de la lista) aplicó **"blefaroplastia"** por error. Ya se agregó "implantes mamarios" (correcto). Falta SOLO quitar "blefaroplastia", pendiente de Diego.

## ⚠️ Bug detectado (01/08/2026): no se puede QUITAR una etiqueta existente
El botón "x" de un chip de etiqueta ya aplicada no responde a clicks (probado con >10 coordenadas distintas, distintos tamaños de ventana, recarga de página completa, zoom de teclado, y clicks por referencia de accesibilidad). Agregar etiquetas nuevas (+ Añadir etiqueta) sigue funcionando. Conclusión: por ahora, cuando se detecte una etiqueta incorrecta, documentarla acá como pendiente en vez de intentar corregirla en el momento — no perder tiempo reintentando. Revisar en una sesión futura si el bug se resolvió (podría ser inestabilidad temporal de ManyChat, como la ya documentada con el dropdown de agregar etiquetas).

## Lote — continuación post-auditoría (01/08/2026)

| Nombre | chat_id | Etiquetas aplicadas | Nota |
|---|---|---|---|
| кισѕкιтσ512 vero | 1054070094 | rinomodelacion, botox | auditado, correcto, sin acción |
| Constanza | 592712513 | (ver pendientes arriba) | falta agregar relleno de menton, no se pudo por fallas de UI repetidas |
| 𝓓𝓪𝓲🖤 | 811885872 | relleno de labios agregado | blefaroplastia quedó de más, no se pudo quitar |
| Karen🐞 | 621927689 | implantes mamarios (ya la tenía, automatización) | verificado, correcto, sin acción |
| Anii Labozzetta | 224795061 | implantes mamarios (ya la tenía, automatización) | verificado, correcto, sin acción |
| Sofi | 998707183 | falta rinomodelacion (botox + rinolips ya los tenía) | 10+ intentos fallidos en dos rondas distintas — este contacto puntual parece atascado, saltado definitivamente por ahora |
| JohiValen💜 | 1072145109 | rinomodelacion (ya la tenía, automatización) | verificado, correcto, sin acción |
| javicami | 933613249 | rinomodelacion (ya la tenía, automatización) | verificado, correcto, sin acción |
| Victoria | 1652769945 | — | no especificó procedimiento aún, sin acción |
| Angeles ruiz | 854803534 | relleno de labios (ya la tenía, automatización) | verificado, correcto, sin acción |
| Fram | 1130759727 | rinomodelacion (ya la tenía, automatización) | verificado, correcto, sin acción |
| _bella.cherry._ | 59736321 | rinoplastia + lipoescultura agregados bien; blefaroplastia quedó de más (misclick) | pendiente quitar blefaroplastia |
| PRISS | 593681366 | — | sin contenido en la conversación, sin acción |
| ꧁𝕯𝖞𝖑𝖆𝖓𝖓ᵕ̈ᥫ᭡꧂ | 796970539 | — | sin contenido en la conversación, sin acción |
| . | 354504849 | rinomodelacion + relleno de labios (ya las tenía, automatización) | verificado, correcto, sin acción |
| Pablo Eitner | 962163389 | rinomodelacion (ya la tenía, automatización) | verificado, correcto, sin acción |
| Randy😎⚽ | 264416222 | rinomodelacion (ya la tenía, automatización) | verificado, correcto, sin acción |
| Alee | 2004649608 | rinomodelacion | agregado por automatización en tiempo real mientras yo lo revisaba, sin acción de mi parte |
| 🙃 | 1833561017 | rinomodelacion | agregado correctamente |
| 💜 | 722319385 | rinomodelacion (automatización) | verificado, correcto |
| agoos | 515623029 | rinomodelacion (automatización) | verificado, correcto |
| Moreee✨✨ | 342647225 | relleno de labios (automatización) | verificado, correcto |
| 𝙽𝚊𝚑𝚑𝚒𝚊𝚛𝚊 ♉︎ | 2029005388 | implantes mamarios | agregado correctamente |
| 😊😊😊 | 179243545 | rinomodelacion (automatización) | verificado, correcto |
| LA MORE | 1754792550 | — | sin procedimiento mencionado, sin acción |
| .. | 653876316 | rinomodelacion (automatización) | verificado, correcto |
| Emmanuel | 528049988 | rinomodelacion (automatización) | verificado, correcto |
| RICARDO S | 1665024438 | rinomodelacion (automatización) | verificado, correcto |
| Mica 🍁 | 1179384116 | rinomodelacion (automatización) | verificado, correcto |
| Gianni | 617930725 | rinomodelacion (automatización) | verificado, correcto |
| 𝐒𝐡𝐚𝐢 💗 | 113008305 | implantes mamarios + lipoescultura (automatización) | verificado, correcto |
| Lu Alegre🔥 | 2012175884 | rinomodelacion (automatización) | verificado, correcto |
| camila sala | 289367973 | rinomodelacion (automatización) | verificado, correcto — NO es la Camila staff, contacto real distinto |
| Maidana😎 H. L | 621493227 | rinomodelacion (automatización) | verificado, correcto |
| 𝓒𝓪𝓶𝓲𝓵𝓪 🐆 | 75411033 | rinomodelacion | agregado correctamente — NO es la Camila staff, usuario ccamiisala distinto |
| Max | 125323335 | rinoplastia | agregado correctamente (quería cirugía de nariz, no rinomodelación) |
| Max ⚡ | 1741144704 | — | pidió ginecomastia, no existe etiqueta para eso en la taxonomía de 16/19 — sin acción, flag para Diego (¿agregar etiqueta nueva "ginecomastia"?) |
| kia🪭 | 1530853915 | rinomodelacion (automatización) | verificado, correcto |
| Gabi 🍀 | 380799925 | rinomodelacion | agregado correctamente |
| Franco Coronel | 1268901703 | — | no especificó procedimiento, sin acción |
| Joaquin▶︎●──── | 1191917315 | — | no especificó procedimiento, sin acción |
| kia🪭 (IG) | 148213175 | — | misma persona que kia🪭 WhatsApp (1530853915), ya etiquetada ahí, sin acción |
| Oriana | 1895588638 | rinomodelacion (automatización) | verificado, correcto |
| Martin 💙💛💙 | 299153426 | — | parece coordinación administrativa de cirugía de un tercero, sin procedimiento propio claro, sin acción |
| Mer | 1780650362 | implantes mamarios (automatización) | verificado, correcto |
| Luis | 1261566130 | rinomodelacion (automatización) | verificado, correcto |
| . (candela godoy) | 1919242536 | relleno de labios (automatización) | verificado, correcto |
| Laura Marin | 1996006805 | — | NO es paciente, es quien cobra el alquiler del depto del doctor — sin acción, ruido no-paciente |
| 𝓜𝓲𝓬𝓪 𝓪𝔂𝓮𝓵𝓮𝓷 💋 | 179843290 | rinomodelacion | agregado correctamente |
| oriana (minúscula) | 241614447 | relleno de labios + rinomodelacion | agregadas correctamente (pidió labios y nariz) — encontrada vía filtro de Contactos "sin rinomodelacion/labios/implantes", nuevo método más eficiente que recorrer el Inbox |
| Gaby (1712973748) | 1712973748 | — | no especificó procedimiento, sin acción |
| 𝓶𝓲𝓲𝓵𝓪𝓰𝓻𝓸𝓸𝓼 | 376986136 | — | respondió a una historia, sin procedimiento claro visible, sin acción |
| Jime 🦋 | — | relleno de labios (ya la tenía) | verificado, correcto, sin acción |
| Yeiner Mejia | 138649579 | rinomodelacion | agregado correctamente |
| Angel 👽👽 | 1048464755 | contorno mandibular + rinomodelacion (automatización) | verificado, correcto |
| Emiliano Garrido, Ardy, Gladys, ariel, "mi nieto Derek yagode" | varios | ya tenían rinomodelacion (y Ardy también ojeras+labios) | verificados vía Contactos, correctos, sin acción — backlog de ~7hs de antigüedad, mayormente ya bien tageado por la automatización |
| lamper | 1110711525 | — | sin contenido en la conversación, sin acción |
| Esteban, Maxi, 😐(implantes), Nati, Fa, Lucas, "-.-l", Claudia Rodriguez | varios | ya tenían su etiqueta correcta | verificados vía Contactos (backlog 6-10hs), correctos, sin acción |
| Jose Ruben | 1180592697 | — | no especificó procedimiento, sin acción |
| Enzo Benitez | — | rinomodelacion (ya la tenía) | verificado, correcto |
| Lupe | 1914606316 | — | no especificó procedimiento ("esto"), sin acción |
| Zoe, Camila Cozzolino, ELUNEY Jazmin Abigail | varios | ya tenían sus etiquetas (Zoe: rinoplastia+labios) | verificados, correctos, sin acción |
| Nahiara Sanhueza 📸 | 617117009 | — | no especificó procedimiento, sin acción |
| Walter | 1340842550 | — | solo mandó emojis, sin poder identificar procedimiento, derivado a humano, sin acción |

| Mayten, Flor Ilardo(sin proc.), Sebas, Sol, morena(x2), Giselle, Nere, Sasha, Juan, Max | varios | ya tenían su etiqueta correcta (implantes mamarios, abdominoplastia, rinomodelacion, relleno de labios, etc.) | verificados vía Contactos hasta "hace 1 día", correctos, sin acción |
| Walter | 1340842550 | — | solo emojis, sin poder identificar procedimiento, derivado a humano |
| Dáni | 1116127008 | rinomodelacion | agregado correctamente — contacto de "Friday" (backlog real de +1 día), confirma que ahí SÍ hay huecos reales para encontrar |
| Josue | 1470002006 | — | no especificó procedimiento, sin acción |
| Pablohs, III | varios | ya tenían rinomodelacion | verificados, correctos, sin acción |
| Leonel Duarte | 19971867 | — | compartió un post, sin procedimiento específico, sin acción |
| Hugo Tintaya | 33012784 | rinomodelacion (ya la tenía) | verificado, correcto |
| Camila Josefina | 164947280 | — | solo "Si", sin contexto, sin acción |
| d | 988663907 | rinomodelacion | agregada por automatización en tiempo real, sin acción de mi parte |
| Aime, Pablohs, 🫩🫩🫩 | varios | rinomodelacion (automatización) | verificados, correctos, sin acción |
| Shryl, Ro | varios | relleno de labios (ya la tenían) | verificados, correctos, sin acción |
| maimarita | 454192363 | rinomodelacion + relleno de labios + armonizacion facial | ya las tenía, verificado correcto |
| Katy.katy 33 | 348888831 | relleno de labios | agregado correctamente — SEGUNDO hueco real encontrado en backlog de "Friday" (pidió "me interesa el relleno de labios" explícito, sin ninguna etiqueta) |
| Lai Caballero | 851950936 | rinomodelacion + relleno de labios | agregadas correctamente — TERCER hueco real, backlog de "Saturday" (pidió "riño y labios"), sin ninguna etiqueta |
| HECTOR AGUILAR, Ursula, Ursula Nazarena, Bren/Brenda Retegui, Yelimar, JOSHUA GAUTO | varios | ya tenían su etiqueta correcta | verificados, correctos, sin acción |
| Elpidio Garcete Vera | 522866510 | — | no especificó procedimiento, sin acción |
| Agustina Moisés | 270556506 | implantes mamarios | agregado correctamente — CUARTO hueco real ("Info sobre implantes de mamas" sin etiquetar) |
| 𝖒𝖆𝖎𝖑𝖊𝖓✨ | 2050925364 | rinomodelacion + relleno de labios | agregadas correctamente — QUINTO hueco real, backlog de "Saturday" (pidió "rinomodelación y labios" explícito), sin ninguna etiqueta |
| Agostina Franco | 1565074963 | implantes mamarios agregado; blefaroplastia quedó de más (misclick) | SEXTO hueco real, backlog de "Friday" (preguntó "sirugia de mamas"), sin ninguna etiqueta — pendiente quitar blefaroplastia |
| Evelyn Melina Ibañez | 1827294484 | rinomodelacion | agregado correctamente — SÉPTIMO hueco real, backlog de "Friday" (preguntó "cuanto esta para la rinomodelacion"), solo tenía "bienvenida_enviada" (no es de procedimiento) |
| Pato Pickenpack⚜️ | 992862417 | — | coordinación de turno con "Julia" ya derivada a humano, sin procedimiento explícito visible, sin acción |
| Marii🫧 | 1231869723 | rinomodelacion | agregado correctamente — OCTAVO hueco real, backlog de "Friday" (TikTok, preguntó "cuantos cobras para la rinomodelacion"), solo tenía "bienvenida_enviada" |
| Magali❤️ | 1188895315 | rinomodelacion | agregado correctamente — NOVENO hueco real, backlog de "Friday" (WhatsApp, conversación completa sobre precio de rinomodelación con el bot), cero etiquetas |
| Bich..🐍 | — | relleno de labios (ya la tenía, automatización) | verificado, correcto, sin acción |
| 🐍🐍🐍 (bichiinn) | 1824334628 | relleno de labios | agregado correctamente — DÉCIMO hueco real, backlog de "Friday" (IG, preguntó "cuanto sale relleno de labios"), solo tenía "bienvenida_enviada" — nota: username "bichiinn" muy similar a "Bich..🐍", posible mismo paciente en 2 registros distintos de ManyChat (IG vs otro canal), no se puede fusionar |
| karmaa_abuelela | 1946965248 | rinomodelacion | agregado correctamente — UNDÉCIMO hueco real, backlog de "Friday" (TikTok, en inglés, preguntó sobre migración de filler en la nariz), cero etiquetas |
| Abiggail ♡ | 872591020 | relleno de labios | agregado correctamente — DUODÉCIMO hueco real, backlog de "Friday" ("Me interesa el relleno de labios😍"), solo tenía "bienvenida_enviada" |
| Franco Ivan | 1109708300 | rinomodelacion | agregado correctamente — DÉCIMO TERCER hueco real, backlog de "Friday" (WhatsApp, preguntó por rinomodelación), cero etiquetas |
| Cholo | — | lipoescultura + abdominoplastia (ya las tenía, automatización) | verificado, correcto, sin acción |
| Moises😎 | 969518085 | — | mensajes de coqueteo con el bot, sin procedimiento real, sin acción |
| 🥰 Genesis 🥂🤑 | 1358558638 | rinomodelacion | agregado correctamente — DÉCIMO CUARTO hueco real, backlog de "Friday" (WhatsApp, conversación completa con precio y coordinación de turno), cero etiquetas |
| Yean | — | contorno mandibular (ya la tenía, automatización) | verificado, correcto, sin acción |
| karina | 1851863229 | rinomodelacion | agregado correctamente — DÉCIMO QUINTO hueco real, backlog de "Friday" (WhatsApp, preguntó ubicación y precio de rinomodelación), cero etiquetas |
| Dieguito | 1027092128 | — (debería ser rinomodelacion, DÉCIMO SEXTO hueco real identificado pero NO aplicado) | "+Añadir etiqueta" no abrió el dropdown en >8 intentos (distintos tamaños de ventana, reload, ref-click) — mismo tipo de bug UI que "Sofi" en sesión anterior. Conversación completa: preguntó por "remodelación de nariz" con precio incluido, cero etiquetas. Saltado, pendiente de reintentar en otra sesión o corregir a mano |
| kopi | 993214441 | — | sin contenido en la conversación, sin acción |
| Agustín Sosa | 928540224 | rinomodelacion | agregado correctamente — DÉCIMO SÉPTIMO hueco real, backlog de "Friday" (WhatsApp, conversación completa con precio y duración de rinomodelación), cero etiquetas |
| diego | 861147081 | rinomodelacion | agregado correctamente — DÉCIMO OCTAVO hueco real, backlog de "Friday" (WhatsApp, precio y duración de rinomodelación), cero etiquetas |
| Claudia la colito | — | rinomodelacion (ya la tenía, automatización) | verificado, correcto, sin acción — confirma que la plataforma volvió a responder tras el corte |
| Rafael | — | rinomodelacion (ya la tenía, automatización) | verificado, correcto, sin acción |
| Chole | 4593544 | lipoescultura + abdominoplastia (ya las tenía, automatización) | verificado, correcto, sin acción — NO es la misma persona que "Cholo" revisado antes (contacto distinto) |
| abi | 1370576693 | relleno de labios (ya la tenía, automatización) | verificado, correcto, sin acción |
| Abiggail ♡ (2do encuentro) | 872591020 | relleno de labios | ya revisada antes en esta sesión, sin acción nueva |
| Moises😎 (2do encuentro) | 969518085 | — | ya revisado antes en esta sesión, sin acción nueva |
| Kevin | 218605119 | rinomodelacion | agregado correctamente — DÉCIMO NOVENO hueco real, backlog de "Friday" (WhatsApp, pidió info de rinomodelación explícito con precio), cero etiquetas |
| bri (let) | 12783434243 | relleno de labios (ya la tenía, automatización) | verificado, correcto, sin acción |
| 𝕭 𝖗 𝖎 𝖘 𝖆 💅🏼 | 1383310769 | — | preguntó "cuanto sale el volumen" respondiendo a una historia sin contexto visible del procedimiento — ambiguo (¿labios? ¿otra cosa?), sin acción por falta de certeza |
| Ney | 1062241720 | rinomodelacion | agregado correctamente — VIGÉSIMO hueco real, backlog de "Friday" (WhatsApp, preguntó por rinomodelación y ubicación), cero etiquetas |
| Cata (Catalina Melchiori) | 1674947892 | rinomodelacion | agregado correctamente — VIGÉSIMO PRIMERO hueco real, backlog de "Friday" (WhatsApp, conversación completa con precio, derivada a humano), cero etiquetas |
| "VICO" | 699647099 | rinomodelacion | agregado correctamente — VIGÉSIMO SEGUNDO hueco real, backlog de "Friday" (WhatsApp, preguntó por rinomodelación y ubicación), cero etiquetas |
| Kat💕 | 1543621057 | rinomodelacion | agregado correctamente — VIGÉSIMO TERCER hueco real, backlog de "Friday" (WhatsApp, conversación completa con precio de rinomodelación), cero etiquetas |
| Tobias Galván | 820978865 | rinomodelacion | agregado correctamente — VIGÉSIMO CUARTO hueco real, backlog de "Friday" (WhatsApp, preguntó precio de rinomodelación), cero etiquetas |
| Medusa | — | relleno de labios (ya la tenía, automatización) | verificado, correcto, sin acción |
| 🔜 | 1025779033 | rinomodelacion | agregado correctamente — VIGÉSIMO QUINTO hueco real, backlog de "Friday" (WhatsApp, conversación completa con precio y duración de rinomodelación), cero etiquetas — con este contacto se completó TODO el bloque de "hace 2 días" |

## Lote — bloque "hace 3 días" en adelante (02/08/2026)

Nota técnica: durante la sesión, la lista de Contactos se reinició sola a la vista de "más reciente" (probablemente por el reload asociado al corte de plataforma documentado abajo), perdiendo la posición de scroll. Se volvió a paginar con "Cargar Más" desde el principio hasta reencontrar el punto donde se había quedado (bloques "hace 1 día" y "hace 2 días" — todos ya revisados, sin acción nueva) y de ahí se siguió a territorio nuevo.

| Nombre | chat_id | Etiquetas aplicadas | Nota |
|---|---|---|---|
| pablo | 1161035764 | rinomodelacion | agregado correctamente — VIGÉSIMO SEXTO hueco real, primer contacto del bloque "hace 3 días" (WhatsApp, conversación completa con ubicación y precio de rinomodelación), cero etiquetas |
| Angel | 5343... (implantes mamarios) | implantes mamarios (ya la tenía, automatización) | verificado, correcto, sin acción — segundo contacto del bloque "hace 3 días" |
| Sara | 12737... | relleno de labios (ya la tenía, automatización) | verificado, correcto, sin acción |
| Angie | 1164502972 | rinomodelacion | agregado correctamente — VIGÉSIMO SÉPTIMO hueco real (WhatsApp, "¿Puedo obtener más información sobre Rinomodelacion?"), cero etiquetas |
| Jime | 487951744 | lipoescultura (ya la tenía, automatización) | verificado, correcto, sin acción |
| Valentina ❤️ | 349466637 | rinomodelacion | agregado correctamente — VIGÉSIMO OCTAVO hueco real (WhatsApp, conversación completa sobre precio de rinomodelación, incluye pregunta de menor de edad con autorización), cero etiquetas |
| jazmin 🤍 | 1639051467 | rinomodelacion | agregado correctamente — VIGÉSIMO NOVENO hueco real (WhatsApp, "quería saber el precio de la Rinomodelacion"), cero etiquetas |
| 🥰 | 665697140 | rinomodelacion | agregado correctamente — TRIGÉSIMO hueco real (WhatsApp, comparó rinomodelación vs rinoplastia, eligió explícitamente "la sin cirugía" = rinomodelación, conversación completa con precio y duración), cero etiquetas |
| Martina | 713000044 | rinomodelacion | agregado correctamente — TRIGÉSIMO PRIMER hueco real (Instagram, "quería consultarte cuánto está la remodelación"), solo tenía "bienvenida_enviada" |
| Solcito❤️ | 180158239 | relleno de labios (ya la tenía, automatización) | verificado, correcto, sin acción |
| Micaela Ponce 15 | 1168537485 | — | TikTok, solo saludó y preguntó ubicación, sin procedimiento explícito, sin acción |
| Jennifer Daiana Rodriguez | 122141235 | rinomodelacion | agregado correctamente — TRIGÉSIMO SEGUNDO hueco real (Instagram, "Hola qué tal!! Precio de rinomodelacion?"), solo tenía "bienvenida_enviada" |
| Claris, | 1494540672 | abdominoplastia + implantes mamarios | agregadas correctamente — TRIGÉSIMO TERCER hueco real (WhatsApp, "Sobre reducción de abdomen y sobre implantes mamarios" explícito, derivada a humano), cero etiquetas — primer caso de esta sesión con DOS procedimientos distintos en una sola conversación |
| Agustina Belen | 788119538 | rinomodelacion | agregado correctamente — TRIGÉSIMO CUARTO hueco real (WhatsApp, "queria saber que precio esta la rinomodelacion"), cero etiquetas |
| Agus Belen | 471549460 | rinomodelacion | agregado correctamente — TRIGÉSIMO QUINTO hueco real (Instagram, "que precio sale la rinomodelacion porfavor"), solo tenía "bienvenida_enviada" — posible mismo paciente que "Agustina Belen" (registro distinto por canal, no se puede fusionar) |
| Moree💞 | 883232307 | Lipotransferencia | agregado correctamente — TRIGÉSIMO SEXTO hueco real (WhatsApp, preguntó "Ipotraferencia glutea" explícito y derivada a humano; tema panza quedó ambiguo entre lipoescultura/abdominoplastia sin definir, no se etiquetó eso), cero etiquetas — nota técnica: la etiqueta "Lipotransferencia" existe en ManyChat con mayúscula inicial (a diferencia del resto que son todas en minúscula), tenerlo en cuenta para futuras búsquedas |
| moree_bj8 | 378778889 | — | Instagram, solo dijo "Hola info", sin procedimiento explícito, sin acción |
| Xiomii Maina | 2053495621 | rinomodelacion | agregado correctamente — TRIGÉSIMO SÉPTIMO hueco real (WhatsApp, "quería consultar por el precio de una rino modelación", conversación completa con precio y duración), cero etiquetas |
| Amat Victoria Curam | 2107807259 | rinomodelacion | agregado correctamente — TRIGÉSIMO OCTAVO hueco real (WhatsApp, consulta por cicatriz en nariz, discutió rinomodelación como opción, coordinó evaluación), cero etiquetas |
| Valentina 💙 | 1579857144 | rinomodelacion | agregado correctamente — TRIGÉSIMO NOVENO hueco real (WhatsApp, "llegue aca por la rinomodelacion que le hicieron a ari zalazar", con precio, sin decidir aún), cero etiquetas |
| Valentina🤍 | 1943746733 | — | Instagram, compartió un reel ("Contenido no disponible" para lectura) y dijo "me encanto tu trabajo", sin nombrar procedimiento específico — ambiguo, sin acción |
| . | 784054721 | rinomodelacion | agregado correctamente — CUADRAGÉSIMO hueco real (WhatsApp, "Hola quiero hacerme una rinomodelacion" explícito, con precio), cero etiquetas |
| Tiaraa | 842483634 | rinomodelacion | agregado correctamente — CUADRAGÉSIMO PRIMER hueco real (WhatsApp, conversación completa sobre perfil/giba nasal, terminó en rinomodelación con precio), cero etiquetas |
| Tiara | 713212098 | rinomodelacion | agregado correctamente — CUADRAGÉSIMO SEGUNDO hueco real (Instagram, "me gustaría saber más info sobre el retoque en la nariz"), solo tenía "bienvenida_enviada" |
| Denise🦋 | 630631615 | rinomodelacion + relleno de labios | agregadas correctamente — CUADRAGÉSIMO TERCER hueco real (TikTok, "quería saber el precio de rinolips" — combo rino+labios según regla de la taxonomía), solo tenía "bienvenida_enviada" |

## Acciones masivas (02/08/2026) — NUEVO método descubierto
Se descubrió que ManyChat permite seleccionar TODOS los contactos que coinciden con un filtro (no solo los de la página visible) y aplicarles una etiqueta en bloque vía "Acciones Masivas" → "Añadir etiqueta". Se usó para migrar las etiquetas legacy a la taxonomía nueva:
- **"operación de mamas" (74 contactos)** → se agregó "implantes mamarios" a los 74 de una sola acción.
- **"rinolips" (66 contactos)** → se agregó "rinomodelacion" Y "relleno de labios" a los 66, en dos acciones.
- Total: **140 contactos correctamente etiquetados en 3 clicks**, sin revisión individual.
- Balance actualizado: **43 huecos individuales + 140 por acción masiva = 183 contactos corregidos en la sesión**.
- Se investigó si había más atajos masivos disponibles (filtro por anuncio de origen, por secuencia de automatización, por campo custom con contenido del primer mensaje): ninguno escala — no hay anuncios cargados, no hay secuencias segmentadas, y el único campo con contenido de mensaje ("RespuestaDefinitiva") solo tiene datos en 15 contactos de 10.195 (resto de una migración vieja), y esos 15 ya estaban mayormente etiquetados. Confirmado: no existe atajo masivo adicional — el resto (~9.000+) requiere revisión conversación por conversación.

## Balance total de la sesión (01/08/2026 - 02/08/2026)
Revisé sistemáticamente ~150+ contactos desde el más reciente hasta bien entrado el bloque de "hace 3 días". Hallazgo refinado:
- **Últimas ~24hs: >90% ya bien etiquetado** por la automatización en vivo.
- **Pasadas las 24hs (contactos de "Friday"/"Saturday"/"hace 3 días" en adelante): ahí aparecen los huecos reales.** Total encontrados y corregidos esta sesión vía revisión manual: **41 huecos reales** (los 34 documentados antes + Agus Belen, Moree💞, Xiomii Maina, Amat Victoria Curam, Valentina ❤️💙, jazmin 🤍, ".", Tiaraa) + 1 identificado pero NO corregido por bug de UI (Dieguito) — todos con conversación real sobre un procedimiento y CERO etiquetas antes de mi revisión. **Además, 140 contactos más quedaron cubiertos por las 2 acciones masivas** (operación de mamas→implantes mamarios, rinolips→rinomodelacion+relleno de labios) — total combinado: **181 contactos corregidos esta sesión**.
- **2 misclicks confirmados** (mismo bug de siempre: el segundo click del patrón "doble intento" cae sobre un ítem ya visible de la lista en vez del buscador) — Agostina Franco quedó con "blefaroplastia" espuria de más, sumándose a Dai. Ambos pendientes de que Diego los quite manualmente (ver sección de bugs arriba).
- **El bloque "hace 3 días" confirma que el backlog viejo SIGUE teniendo huecos reales** al mismo ritmo que "Friday"/"Saturday" — no se agotó, sigue habiendo valor en continuar.
- **Bug nuevo detectado esta sesión**: la lista de Contactos puede resetearse sola a la vista de "más reciente" (perdiendo la posición de scroll) tras un reload o corte de plataforma, aunque el filtro de etiqueta se mantenga. No hay forma de "guardar" la posición — hay que volver a paginar desde el principio cada vez que esto pasa. El buscador por nombre a veces tarda 1-2 intentos extra en aplicar el filtro (mismo patrón que el buscador de etiquetas).
- **La única forma realista de llegar a los ~10.000 contactos totales sigue siendo la integración por API** (clave ya generada, pendiente de que Diego la copie a `.env`). El trabajo manual sirvió para: (1) corregir errores puntuales de la automatización, y (2) confirmar que el backlog real (>1 día de antigüedad) SÍ tiene valor y sigue apareciendo a medida que se avanza — no se agotó en esta sesión.

**Próxima sesión — empezar directo ahí**: los bloques de "hace 1 día", "hace 2 días" están COMPLETAMENTE barridos. Dentro de "hace 3 días", el barrido llegó hasta "Agustina Belen" (chat_id 788119538) — el siguiente contacto sin revisar es "Agus Belen" (justo después, mismo bloque). Seguir desde ahí con "Cargar Más" hacia "hace 4 días" y más viejo. Pendiente puntual: reintentar el tag de Dieguito (chat_id 1027092128, debería llevar rinomodelacion) y quitar manualmente los 2 misclicks de "blefaroplastia" (Dai y Agostina Franco).

## ⚠️ Corte temporal por inestabilidad de la plataforma (02/08/2026) — RESUELTO
Después de agregar la etiqueta a "diego", ManyChat dejó de responder a ningún click en toda la página durante varios minutos (probado en Contactos y Bandeja de entrada, con reload de por medio). Se resolvió solo — tras un rato, volvió a responder con normalidad y se pudo seguir etiquetando (confirmado con Claudia la colito, Rafael, y varios contactos más después del corte). Si vuelve a pasar: esperar unos minutos y reintentar antes de asumir que hay que avisarle a Diego — no fue necesario esta vez.

## Hallazgo importante
Revisando sistemáticamente el backlog de las últimas ~10 horas vía Contactos, la enorme mayoría de los contactos YA están bien etiquetados por la automatización en vivo (el sistema n8n que etiqueta en tiempo real está funcionando bien para conversaciones nuevas). El valor real de seguir este trabajo retroactivo está en contactos MÁS VIEJOS (días/semanas, de antes de que existiera el auto-tagging), no en las últimas horas. Próxima sesión: saltar directo a backlog viejo con varios "Cargar Más" seguidos en vez de revisar hora por hora desde el presente.

## Método nuevo descubierto (más eficiente)
En vez de recorrer el Inbox (que resetea el scroll en cada navegación), usar Contactos → Filtro → Etiqueta "no es" [rinomodelacion / relleno de labios / implantes mamarios] → esto lista contactos que probablemente les falta etiqueta, ordenados por más reciente. Click en cada uno → "Iniciar Chat" → lleva a la vista de Inbox de ESE contacto puntual → mismo flujo de "+Añadir etiqueta" de siempre. Tiene paginación ("Cargar Más") para llegar más atrás en el tiempo. El filtro se resetea si se recarga la página de Contactos, hay que rearmarlo cada vez.
