"""
Chequeo diario de XAU/USD -- corre 2 hipotesis simples (MA-200, Opening Range
Breakout) sobre el dia de hoy, sin tocar ni ajustar reglas. Ver
bitacora_seguimiento_diario.md para el registro acumulado.
"""
import sys, os, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'data'))
from download_dukascopy_5y import fetch_hour_ticks, ticks_to_m1, NY_TZ, UTC
import yfinance as yf
import pandas as pd

def orb_hoy(fecha_ny: datetime.date, orb_min=30):
    """Opening range breakout de los primeros `orb_min` minutos de la sesion
    (03:00 NY, inicio de la ventana ya definida)."""
    start_ny = NY_TZ.localize(datetime.datetime.combine(fecha_ny, datetime.time(3, 0)))
    end_ny = NY_TZ.localize(datetime.datetime.combine(fecha_ny, datetime.time(17, 0)))
    hour = start_ny.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
    end_utc = end_ny.astimezone(UTC)
    all_ticks = []
    while hour <= end_utc:
        all_ticks.extend(fetch_hour_ticks(hour))
        hour += datetime.timedelta(hours=1)
    if not all_ticks:
        return None
    bars = ticks_to_m1(all_ticks)
    if not bars:
        return None
    orb_bars = bars[:orb_min]
    orb_high = max(b[2] for b in orb_bars)
    orb_low = min(b[3] for b in orb_bars)
    cierre_sesion = bars[-1][4]
    if cierre_sesion > orb_high:
        resultado = f"rompio ARRIBA del rango ({orb_high:.2f}) y cerro la sesion en {cierre_sesion:.2f}"
    elif cierre_sesion < orb_low:
        resultado = f"rompio ABAJO del rango ({orb_low:.2f}) y cerro la sesion en {cierre_sesion:.2f}"
    else:
        resultado = f"se quedo DENTRO del rango [{orb_low:.2f}, {orb_high:.2f}], cierre {cierre_sesion:.2f}"
    return {
        'orb_high': orb_high, 'orb_low': orb_low,
        'cierre_sesion': cierre_sesion, 'n_bars': len(bars),
        'resultado': resultado,
    }


def ma200_hoy():
    """Posicion del cierre de hoy respecto a la media movil de 200 dias."""
    df = yf.download('GC=F', period='400d', interval='1d', progress=False, auto_adjust=True)
    if df.empty:
        return None
    close = df['Close'].dropna()
    ma200 = close.rolling(200).mean()
    ultimo_close = float(close.iloc[-1].iloc[0]) if hasattr(close.iloc[-1], 'iloc') else float(close.iloc[-1])
    ultimo_ma = float(ma200.iloc[-1].iloc[0]) if hasattr(ma200.iloc[-1], 'iloc') else float(ma200.iloc[-1])
    fecha = close.index[-1].date()
    posicion = "POR ENCIMA (senal larga)" if ultimo_close > ultimo_ma else "POR DEBAJO (senal afuera/corto)"
    return {'fecha': fecha, 'close': ultimo_close, 'ma200': ultimo_ma, 'posicion': posicion}


if __name__ == '__main__':
    hoy_ny = datetime.datetime.now(NY_TZ).date()
    print(f"=== Chequeo diario XAU/USD -- {hoy_ny} ===\n")

    print("--- MA-200 ---")
    ma = ma200_hoy()
    if ma:
        print(f"Fecha dato diario: {ma['fecha']} | Cierre: {ma['close']:.2f} | MA200: {ma['ma200']:.2f}")
        print(f"Posicion: {ma['posicion']}")
    else:
        print("No se pudo obtener (yfinance sin datos)")

    print("\n--- Opening Range Breakout (primeros 30 min de sesion, 03:00 NY) ---")
    orb = orb_hoy(hoy_ny)
    if orb:
        print(f"Rango apertura: [{orb['orb_low']:.2f}, {orb['orb_high']:.2f}] | velas totales sesion: {orb['n_bars']}")
        print(f"Resultado: {orb['resultado']}")
    else:
        print("Sin datos todavia para hoy (puede que la sesion no haya arrancado o Dukascopy no publico aun)")
