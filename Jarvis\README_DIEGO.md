# Jarvis — Tu Asistente Financiero Personal

Bienvenido, Diego. Esta guía te lleva de cero a operativo en menos de 10 minutos.

---

## Lo que necesitás antes de empezar

1. **Claude Code Desktop** — [descargar acá](https://claude.ai/download)
   Necesitás una suscripción activa a Claude Pro o superior.

2. **Python 3.10 o superior** — [descargar acá](https://python.org/downloads)
   Durante la instalación, **tildá la opción "Add Python to PATH"** antes de continuar.

---

## Paso 1 — Instalación de dependencias (una sola vez)

Abrí PowerShell dentro de la carpeta `Asistente Financiero IA` y ejecutá:

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

El script instala todas las librerías necesarias y verifica la conexión con Yahoo Finance.
Si todo está bien, vas a ver el mensaje: `✓ Setup completado`.

---

## Paso 2 — Abrí Jarvis en Claude Code

1. Abrí **Claude Code Desktop**
2. Clic en **File → Open Folder**
3. Seleccioná la carpeta `Asistente Financiero IA`
4. Jarvis se activa automáticamente

**La primera vez que lo abrís, Jarvis te va a hacer las preguntas de configuración directamente en el chat.** No hay nada más que ejecutar — seguí las instrucciones que te aparecen en pantalla.

---

## Paso 3 — Onboarding inicial

Jarvis te va a pedir en el chat:
- Tu nombre y email (para enviarte reportes)
- Tu broker
- Tu perfil de riesgo y horizonte de inversión
- Tus posiciones actuales (empresa, cantidad, precio de compra)
- Empresas adicionales que querés monitorear

Al confirmar, Jarvis guarda todo automáticamente. Listo.

---

## Cómo usarlo día a día

Escribís lo que necesitás en lenguaje natural. Algunos ejemplos:

```
"Cómo está el mercado hoy?"
"Analizame NVIDIA para los próximos 6 meses"
"Mostrá mi portfolio actual"
"Buscame oportunidades en el sector tech"
"Qué noticias hay de Apple en los últimos 3 meses?"
"Generá el reporte de hoy y mandámelo por email"
"Comparame AAPL vs MSFT en el último año"
"Qué está pasando con las tasas de interés?"
"Conviene mantener mi posición en Tesla?"
```

---

## Tus archivos

| Archivo | Para qué sirve |
|---|---|
| `jarvis/portfolio/active_positions.json` | Tu cartera — Jarvis la actualiza cuando le pedís |
| `jarvis/portfolio/watchlist.json` | Empresas que Jarvis monitorea |
| `jarvis/data/profile.json` | Tu perfil (generado en el onboarding) |
| `jarvis/charts/` | Gráficos generados — abrirlos con cualquier browser |
| `jarvis/reports/` | Reportes HTML generados |

> Para modificar el portfolio no necesitás tocar ningún archivo — simplemente decile a Jarvis:
> *"Comprá 5 acciones de AMD a $180"* o *"Vendí mis TSLA, sacalas del portfolio"*

---

## Activar noticias históricas (opcional, recomendado)

Con la key de **Alpha Vantage** Jarvis puede analizar noticias de hasta 12 meses atrás para cualquier empresa.

1. Registrate gratis en: [alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)
2. Copiá tu API key
3. Decile a Jarvis: *"Configurá mi Alpha Vantage key: [tu key]"* y Jarvis la guarda en el archivo de configuración

---

## Soporte

Cualquier inconveniente, contactá a Nahuel.
