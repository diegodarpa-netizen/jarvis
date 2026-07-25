# 📁 Screenshots XAU/USD — Base de Datos Visual

## PDFs BASE (nunca modificar, siempre consultar)
- `/Users/diegorodriguez/Downloads/scalping/Plan técnico XAU.pdf` — reglas técnicas completas
- `/Users/diegorodriguez/Downloads/scalping/Plan operativo XAU.pdf` — sesión, noticias, límites
- `/Users/diegorodriguez/Downloads/scalping/Aparienciadel indicador XAU.pdf` — visual

---

## 📂 Estructura de carpetas

### /semanas/
Capturas del chart completo al cierre de cada semana.
Nombre: `YYYY_W##_DDMMYYYY.png`
Ejemplo: `2026_W23_07062026.png`
→ Usadas para: evaluar trades generados vs estrategia, calcular WR y R semanal

### /señales/
Capturas de cada señal individual (entrada, SL, TP).
Nombre: `YYYYMMDD_HHMM_BUY|SELL_resultado.png`
Ejemplo: `20260607_0923_BUY_TP.png`
→ Usadas para: verificar que el patrón cumple las reglas del PDF

### /estructura_m3/
Capturas de la estructura M3 (highs/lows, ChOC, tendencia).
Nombre: `YYYYMMDD_estructura.png`
→ Usadas para: comparar detección automática vs ojo humano

### /errores/
Capturas donde el código generó una señal INCORRECTA según el PDF.
Nombre: `YYYYMMDD_error_descripcion.png`
Ejemplo: `20260607_error_env_sin_pullback.png`
→ Usadas para: identificar bugs y mejorar el código

---

## 🔄 Flujo de trabajo con Jarvis

1. Guardás el screenshot en la carpeta correcta
2. Me decís: "analiza screenshots/semanas/2026_W23.png"
3. Jarvis compara contra los PDFs base
4. Guarda análisis en `memory/trading_analysis.md`
5. Si detecta desvío → propone corrección en el código Pine
