# Jarvis — Manual de Operaciones
**Asistente Financiero Personal con Inteligencia Artificial**
*Desarrollado para Diego Rodriguez por Nahuel Divano*

---

## ¿Qué es Jarvis?

Jarvis es un asistente financiero personal impulsado por inteligencia artificial que vive dentro de Claude Code. Combina datos de mercado en tiempo real con IA avanzada para acompañarte en cada decisión de inversión.

No es un chatbot genérico: conoce tu portfolio, tu perfil de riesgo, los mercados que seguís y tu estilo de inversión. Todo lo que hace está contextualizado con tu información personal.

**Interactuás con Jarvis en lenguaje natural, como si hablaras con un asesor de confianza.** No hay comandos que memorizar.

---

## INSTALACIÓN Y CONFIGURACIÓN (una sola vez)

### Requisitos
- Claude Code Desktop instalado (claude.ai/download)
- Suscripción a Claude Pro o superior
- Python 3.10 o superior (si no lo tenés, `setup.ps1` lo detecta)
- Windows 10/11
- Conexión a internet

### Paso 1 — Instalar dependencias Python
Abrí PowerShell en la carpeta del proyecto y ejecutá:
```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```
Instala automáticamente todas las librerías necesarias y verifica la conexión con Yahoo Finance.

### Paso 2 — Abrir en Claude Code
1. Abrí Claude Code Desktop
2. `File → Open Folder` → seleccioná la carpeta `Asistente Financiero IA`
3. Jarvis se activa automáticamente

### Paso 3 — Onboarding inicial
La primera vez que abrís la carpeta, **Jarvis te guía por el proceso de configuración dentro del mismo chat**. Te va a preguntar:
- Tu email (para recibir reportes)
- Tu broker
- Tu perfil de riesgo y horizonte de inversión
- Tus posiciones actuales
- Empresas que querés monitorear

Al confirmar, Jarvis guarda todo automáticamente. **No hay formularios externos ni configuración manual.**

---

## CAPACIDADES DEL SISTEMA

### 1. Análisis de empresas
Jarvis analiza cualquier empresa cotizada en bolsa con un análisis completo que incluye:
- Precio actual y tendencia
- Análisis técnico (medias móviles MA20/50/200, RSI, soporte y resistencia)
- Valuación (PE, EV/EBITDA, upside al target de analistas, consenso)
- Salud financiera (deuda, márgenes, ROE, crecimiento de ingresos)
- Últimas noticias relevantes con impacto esperado
- Recomendación concreta con escenarios optimista / base / pesimista
- Gráfico interactivo (candlestick con MAs y volumen)

**Mercados cubiertos:** S&P 500, NASDAQ, NYSE, ETFs, ADRs, acciones latinoamericanas (BA, NYSE)

---

### 2. Briefing de mercado
Resumen ejecutivo del estado del mercado en el momento en que lo pedís:
- Sentimiento general (risk-on / risk-off / mixto)
- Índices principales: S&P 500, NASDAQ, Dow Jones, Russell 2000, VIX
- Los 11 sectores del S&P 500 con variación diaria
- Activos macro: oro, petróleo, dólar (DXY), bonos del Tesoro 10Y/2Y, Bitcoin
- Nivel de VIX e interpretación (calma / alerta / pánico)
- Yield curve: spread 10Y-2Y y señal de inversión

---

### 3. Seguimiento del portfolio
Vista completa de tu cartera con datos en tiempo real:
- P&L por posición (ganancia/pérdida en USD y %)
- Valor actual vs. capital invertido
- P&L total del portfolio
- Mejor y peor posición
- Distribución del portfolio (gráfico de torta)

---

### 4. Scanner de oportunidades
Jarvis escanea tus watchlists y las rankea por score (0-100) combinando:
- Señales técnicas: posición vs. MAs, RSI sobrecomprado/sobrevendido
- Señales fundamentales: PE forward, ROE, crecimiento de ingresos, márgenes, P/B
- Señales de analistas: consenso buy/hold/sell, upside al target price

Watchlists disponibles: `tech`, `finance`, `etfs`, `latam`, `custom` (tus empresas personalizadas)

---

### 5. Noticias e investigación
- Noticias de cualquier empresa o del mercado en general (Yahoo Finance)
- Deep research: investigación profunda con búsqueda web en tiempo real, sintetizando fuentes como Reuters, Bloomberg, WSJ, SEC EDGAR y Fed Reserve
- Contexto macro: inflación, tasas de interés, decisiones del Fed, datos económicos

---

### 6. Reportes profesionales
Reportes HTML con diseño dark-theme, gráficos interactivos embebidos y todo en español:

| Tipo de reporte | Contenido |
|---|---|
| **Portfolio** | Posiciones, P&L, gráfico de distribución y rendimiento |
| **Mercado** | Índices, sectores, macro, VIX, yield curve |
| **Empresa** | Análisis completo con gráfico candlestick |
| **Oportunidades** | Ranking de oportunidades por sector con scores |

Los reportes se guardan en `jarvis/reports/` y se pueden enviar por email con un solo pedido.

---

### 7. Envío de reportes por email
Jarvis envía cualquier reporte a tu email directamente desde el chat. Solo pedílo.

---

### 8. Gráficos interactivos
Gráficos HTML que se abren en el browser. Soportan zoom, pan y hover con datos completos.
- **Candlestick**: OHLCV con MAs superpuestas y volumen
- **Línea / Área**: para evolución de precio o portfolio
- **Barras / Torta**: para composición del portfolio y comparativas

---

## USO DIARIO — Comandos en lenguaje natural

Todo se hace escribiendo en el chat de Claude Code. Ejemplos reales de lo que podés decirle a Jarvis:

---

### Análisis de mercado

```
"¿Cómo está el mercado hoy?"
"Dame el briefing del mercado"
"¿Qué pasó en los mercados esta semana?"
"Briefing completo con las acciones que más subieron y bajaron"
```

---

### Análisis de empresas

```
"Analizame NVIDIA"
"Hacé un análisis de Apple"
"¿Qué onda Tesla? ¿Conviene entrar?"
"Analizame Microsoft para los próximos 6 meses"
"Comparame AAPL vs MSFT"
"¿Cuál es mejor, AMD o NVIDIA?"
"¿Cuánto vale Google ahora?"
"¿Qué dice el consenso de analistas sobre Meta?"
"Mostrá el gráfico de Tesla a 6 meses"
```

---

### Portfolio

```
"Mostrá mi portfolio"
"¿Cómo estoy con mis inversiones?"
"¿Cuánto gané/perdí en total?"
"¿Cómo está mi posición en NVIDIA?"
"¿Conviene mantener Apple?"
"Comprá 5 acciones de AMD a $180"
"Agregá al portfolio: 10 Microsoft a $420"
"Vendí mis Tesla, sacalas del portfolio"
```

---

### Oportunidades e ideas

```
"Buscame oportunidades en tech"
"¿Qué acciones están baratas ahora?"
"Dame las mejores ideas del sector finanzas"
"Escaneá mi watchlist"
"Ideas de inversión en Latinoamérica"
"¿Qué ETFs convienen ahora?"
"Escaneá estas acciones: MercadoLibre, Nubank, Globant"
```

---

### Noticias e investigación

```
"¿Qué noticias hay de NVIDIA?"
"¿Qué está pasando con Tesla?"
"Últimas novedades de Apple"
"Principales noticias financieras de hoy"
"Investigá en profundidad a NVIDIA"
"¿Qué impacto tienen los aranceles de Trump en mi portfolio?"
"Investigá la situación de las tasas de interés en EEUU"
"¿Qué dice el mercado sobre la inflación?"
```

---

### Reportes y email

```
"Generá el reporte de hoy"
"Dame el reporte de mi portfolio"
"Reporte del mercado de esta semana"
"Análisis de NVIDIA en reporte"
"Generá el reporte y mandámelo por mail"
"Enviame el briefing de hoy por email"
"Mandá el reporte de oportunidades en tech"
```

---

### Gestión de watchlist

```
"Agregá MercadoLibre a mi watchlist"
"Sacá ARKK de la lista de ETFs"
"Agregá una watchlist de cripto con Bitcoin y Ethereum"
"¿Qué tengo en mi watchlist?"
```

---

## GESTIÓN DEL PORTFOLIO

### Agregar una posición
```
"Comprá 10 acciones de NVIDIA a $850"
"Agregá: 5 SPY a $530"
```
Jarvis actualiza `jarvis/portfolio/active_positions.json` directamente.

### Cerrar una posición
```
"Vendí todo Apple, sacalo del portfolio"
"Cerrá mi posición en Tesla"
```

### Actualizar precio promedio
```
"Promedié NVIDIA comprando 5 más a $780, actualizá"
```

---

## ESTRUCTURA DE ARCHIVOS

```
Asistente Financiero IA/
├── CLAUDE.md                        ← prompt principal de Jarvis (no modificar)
├── .env                             ← claves y credenciales (no compartir)
├── requirements.txt                 ← dependencias Python
├── setup.ps1                        ← instalación automática
└── jarvis/
    ├── data/
    │   └── profile.json             ← perfil e información del usuario
    ├── portfolio/
    │   ├── active_positions.json    ← posiciones actuales del portfolio
    │   └── watchlist.json           ← listas de seguimiento por sector
    ├── scripts/                     ← motor del sistema (no modificar)
    ├── reports/                     ← reportes HTML generados
    └── charts/                      ← gráficos HTML interactivos
```

---

## PERÍODOS DISPONIBLES PARA GRÁFICOS Y ANÁLISIS

| Código | Período |
|---|---|
| 1d | 1 día |
| 5d | 5 días |
| 1mo | 1 mes |
| 3mo | 3 meses |
| 6mo | 6 meses (por defecto) |
| 1y | 1 año |
| 2y | 2 años |
| 5y | 5 años |
| ytd | Año a la fecha |
| max | Máximo histórico disponible |

---

## TROUBLESHOOTING

### "No se encontraron datos para [empresa]"
- Verificar que el ticker sea correcto (usar ticker de Yahoo Finance)
- Acciones argentinas en BYMA: `GGAL.BA`, `YPF.BA`
- ADRs argentinos en NYSE: `GGAL`, `YPF`, `PAM`, `MELI`
- Cripto: `BTC-USD`, `ETH-USD`

### "Error de conexión"
- Verificar conexión a internet
- Yahoo Finance tiene rate limiting ocasional — esperar 30 segundos y reintentar

### "El email no llega"
- Revisar carpeta de spam
- Ejecutar `setup.ps1` de nuevo para reconfigurar

### "ModuleNotFoundError"
- Ejecutar: `pip install -r requirements.txt`
- O ejecutar `setup.ps1` de nuevo

### "Los gráficos no se abren"
- Los HTML están en `jarvis/charts/`
- Arrastrar el archivo al browser manualmente

---

## FUENTES DE DATOS

| Fuente | Datos que provee | Costo |
|---|---|---|
| Yahoo Finance | Precios, histórico, fundamentals, noticias, earnings, analistas | Gratuito |
| NewsAPI | Noticias adicionales de medios financieros | Gratuito (plan básico) |
| Web en tiempo real | Deep research, contexto macro, noticias de última hora | Incluido en Claude |

---

*Jarvis MVP — Mayo 2026*
*Desarrollado por Nahuel Divano*
