---
name: negocio-propuesta-comercial
description: Arma una propuesta comercial o presupuesto para un paciente/cliente del consultorio. Usar cuando Diego pida armar una propuesta, cotización o presupuesto para presentar a un paciente.
---

# Propuesta comercial

Equipo: Negocio/Ops. No hay script dedicado todavía — se arma con Claude directamente en el chat, siguiendo esta guía.

1. Pedir a Diego (si no lo dio ya): procedimiento(s), rango de precio, y cualquier condición particular (financiación, fecha).
2. Estructura de la propuesta: procedimiento, qué incluye, precio, condiciones de pago, próximos pasos — en español, tono profesional/cálido (no corporativo frío, es medicina estética).
3. Si Diego quiere el HTML formateado en vez de texto plano, reutilizar el estilo de `jarvis/scripts/report_builder.py` como referencia visual (no ejecutarlo tal cual, ese script es para reportes de portfolio — solo tomar el estilo).
4. Nunca inventar precios: si Diego no dio un número, preguntarle antes de poner una cifra en la propuesta.
