# Plan de construcción — Algo Trading

Cómo se arma este proyecto de acá en adelante. Es la síntesis operativa de todo lo que hay en `knowledge/` — cuando Diego diga "arranquemos con el código", este es el orden a seguir.

## Qué debemos tener antes de escribir la primera estrategia

1. **Universo de activos definido** (ver abajo) — sin esto, el motor y los datos no tienen para qué correr.
2. **Motor único de backtesting**: NautilusTrader, self-hosted, 100% gratis (`knowledge/plataforma_backtesting.md`) — ya instalado y validado con `smoke_test.py`.
3. **Fuente de datos por activo**: `knowledge/fuentes_datos_historicos.md` (HistData para XAU, CCXT/CryptoDataDownload para BTC, Tiingo/yfinance para equities) — con NautilusTrader no vienen datos incluidos, hay que cargarlos nosotros vía su `ParquetDataCatalog`.
4. **Metodología de validación fija**: walk-forward real (`knowledge/metodologia_validacion.md`) — ninguna estrategia se declara "buena" con un solo backtest estático, siguiendo la lección ya aprendida con el 70%→38,5% WR de XAU.
5. **Estructura de riesgo separada de la señal de entrada**: el patrón que ya recomendaba `ANALISIS_ESTRATEGICO_IA_FINANCIERA.md` y que confirma Ivan Scherman en `knowledge/traders_referentes.md` — el módulo de riesgo debe poder vetar independientemente de qué tan buena se vea la señal técnica.
6. **Bitácora de activos** (`bitacora_activos.md`, en esta misma carpeta) — para que cada vez que Diego pida "revisemos activos" quede registrado y no se repita research ya hecho.

## Universo de activos — propuesta inicial

No hace falta arrancar de cero: ya hay tres frentes activos en Jarvis, esta es la propuesta de qué traer primero al proyecto unificado (a confirmar/ajustar con Diego):

| Activo | Estado actual en Jarvis | Prioridad propuesta |
|---|---|---|
| XAU/USD | Scalping intradía, Pine Script + backtest.py sin walk-forward | **1º** — es donde más urge aplicar la metodología nueva (ya tiene el problema documentado) |
| BTC/USD | Scalping, carpeta de backtest vacía | 2º — reutiliza la misma lógica de scalping que XAU una vez validado el proceso ahí |
| Equities swing (CRM, WFC, SLB, ORCL, FSLR, BSBR) | Backtest mecánico corrido una vez (flojo), scripts perdidos en scratchpad | 3º — retomar con el filtro técnico que había quedado pendiente, ahora sobre LEAN en vez de scripts sueltos |

Si Diego quiere sumar activos nuevos que hoy no están en Jarvis (otro par de forex, otra cripto, otro sector de equities), es el momento de decirlo para incluirlos en la bitácora desde el arranque.

## Estructura de carpetas propuesta (para cuando se empiece a escribir código)

```
jarvis/trading_algoritmico/
├── README.md                    (ya existe — índice del proyecto)
├── PLAN_CONSTRUCCION.md         (este archivo)
├── bitacora_activos.md          (ya existe — log de cada revisión)
├── knowledge/                   (ya existe — investigación base)
├── lean_project/                (a crear cuando se instale LEAN CLI)
│   ├── data/                    (caché local de datos LEAN)
│   └── strategies/
│       ├── xau_scalping/
│       ├── btc_scalping/
│       └── equities_swing/
└── walkforward_results/         (resultados versionados por fecha, no sobreescribir)
```

## Próximo paso concreto

**Hecho (11/08/2026):** LEAN CLI instalado — `lean 1.0.227`, en entorno virtual aislado `jarvis/trading_algoritmico/venv/` (no toca el Python del sistema). Se activa con:

```bash
source jarvis/trading_algoritmico/venv/bin/activate
lean --version
```

**Hecho (11/08/2026):** Docker Desktop instalado (v4.86.0), configurado y probado — `docker run hello-world` corrió sin errores, engine activo. Sigue siendo útil más adelante (adaptador de Interactive Brokers), aunque NautilusTrader no lo necesita para backtesting local.

**Cambio de plataforma (11/08/2026):** LEAN CLI quedó descartado — requiere plan pago de QuantConnect (Researcher, US$84/mes) para uso local/API, cosa que no estaba clara hasta intentar generar el token real. Se reemplaza por **NautilusTrader** (100% gratis, LGPL, activamente mantenido) — ver `knowledge/plataforma_backtesting.md`.

**Hecho (11/08/2026):**
1. ~~Instalar Docker Desktop~~ ✅
2. ~~Crear cuenta QuantConnect / `lean login`~~ — abandonado, ya no hace falta.
3. ~~Instalar Python 3.12~~ ✅ `Python 3.12.10`, verificado con MD5 oficial de python.org antes de instalar.
4. ~~Crear venv nuevo + instalar NautilusTrader~~ ✅ `jarvis/trading_algoritmico/venv/` recreado con Python 3.12 (el anterior tenía Python 3.9 + LEAN, descartado). **Ojo con la versión:** se instaló `nautilus_trader==1.230.0` a propósito, no la última (1.231.0) — esa última solo trae wheel precompilado para macOS 26+, y esta Mac corre macOS 15.3; instalarla a secas fuerza a pip a compilar desde cero (necesita Rust/cargo, no instalado) y falla. Si en el futuro se actualiza, revisar primero qué versión de macOS trae el wheel arm64 en PyPI antes de correr `pip install --upgrade`.

**Hecho (11/08/2026): prueba de humo end-to-end.** `smoke_test.py` — motor de backtest + venue simulado (SIM, cuenta margen USD) + instrumento EUR/USD + 300 barras sintéticas (datos generados en memoria, no reales) + estrategia de referencia EMACross (cruce de medias, sin ventaja real) + fills + reporte de cuenta/órdenes/posiciones. Corrió sin errores: 4 órdenes, 2 posiciones abiertas y cerradas. Confirma que todo el pipeline funciona en esta máquina (Python 3.12.10 + nautilus_trader 1.230.0 + macOS 15.3 arm64).

**Nota técnica para la próxima estrategia real:** el `BarType` tiene que usar precio `LAST`, no `BID` — con `BID` el motor rechaza todas las órdenes de mercado con "no market for ...". Costó un par de intentos encontrarlo, no está en la doc oficial de forma obvia.

**Próximo paso:** migrar la lógica de XAU (la más urgida de walk-forward) como primera estrategia real — cargando datos de HistData.com vía el `ParquetDataCatalog` de NautilusTrader, en vez de datos sintéticos. No se toca `jarvis/trading/xau_strategy` ni el Pine Script en vivo hasta que la versión nueva esté validada — se corre en paralelo. BTC y equities quedan para después, con el mismo patrón (traer datos gratis de `fuentes_datos_historicos.md` y cargarlos al catálogo).

Se activa con:
```bash
source jarvis/trading_algoritmico/venv/bin/activate
python -c "import nautilus_trader; print(nautilus_trader.__version__)"
```
