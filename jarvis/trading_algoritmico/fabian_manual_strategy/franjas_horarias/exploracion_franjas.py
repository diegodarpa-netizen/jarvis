"""
Primera exploracion de franjas horarias fuera de la ventana 09:01-10:59 NY
que usa Fabian -- a pedido de Diego (28/08/2026): "ver si en otras
sesiones, asia o demas, hay oportunidades con este tipo de estrategia".

Usa el motor YA CALIBRADO (M3 continuo, doji excluido, START fusionado,
quiebre medido con la mecha) sobre los 40 dias de dato 24hs ya descargados
(27/10/2025-19/12/2025, `data/XAUUSD_M1_24h_fabian.csv`) -- primera muestra,
no el historico completo (esa descarga sigue corriendo en background).

Paso 1: solo frecuencia de señales reconocidas por hora NY (sin backtest de
resultado todavia) -- para ver donde vale la pena mirar con mas detalle
antes de invertir en un backtest completo con SL/TP.
"""
import pandas as pd
import numpy as np
import pytz
import sys
sys.path.append('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy')
sys.path.append('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/seguimiento_vela_por_vela')
from validar_entrada_fabian import señales_del_dia

NY = pytz.timezone('America/New_York')
UTC = pytz.UTC
INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/data/XAUUSD_M1_24h_fabian.csv'


def tramos_continuos(df, max_hueco=pd.Timedelta(hours=2)):
    """Parte el dataframe en tramos donde no hay huecos > max_hueco (fin de
    semana, etc.) -- cada tramo se trata como una sesion continua propia
    para no mezclar estado (M3/tendencia) de un lado a otro de un hueco."""
    diffs = df.index.to_series().diff()
    cortes = diffs[diffs > max_hueco].index
    limites = [df.index[0]] + list(cortes) + [df.index[-1] + pd.Timedelta(minutes=1)]
    tramos = []
    for i in range(len(limites) - 1):
        ini, fin = limites[i], limites[i + 1]
        tramo = df[(df.index >= ini) & (df.index < fin)]
        if len(tramo) >= 30:
            tramos.append(tramo)
    return tramos


if __name__ == '__main__':
    df = pd.read_csv(INPUT, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    df = df[~df.index.duplicated(keep='last')]

    tramos = tramos_continuos(df)
    print(f"{len(tramos)} tramos continuos encontrados (cortados por huecos de fin de semana)")

    todas_señales = []
    for i, tramo in enumerate(tramos):
        s = señales_del_dia(tramo)
        if len(s):
            todas_señales.append(s)
        print(f"  tramo {i+1}: {tramo.index.min()} -> {tramo.index.max()} ({len(tramo)} velas, {len(s)} señales)")

    señales = pd.concat(todas_señales, ignore_index=True)
    señales['t_ny'] = señales['t'].apply(lambda x: x.tz_convert(NY))
    señales['hora_ny'] = señales['t_ny'].dt.hour

    print(f"\nTOTAL señales reconocidas en 40 dias de 24hs: {len(señales)}")
    print(f"Promedio por dia: {len(señales)/40:.1f}")

    print("\n--- Señales por hora NY (0-23) ---")
    por_hora = señales.groupby('hora_ny').size().reindex(range(24), fill_value=0)
    for h, n in por_hora.items():
        barra = '█' * int(n / por_hora.max() * 40) if por_hora.max() > 0 else ''
        marca = ' <-- ventana Fabian (09-10)' if h in (9, 10) else ''
        print(f"  {h:02d}:00-{h:02d}:59  {n:4d}  {barra}{marca}")

    print("\n--- Por franja de sesión (hora NY) ---")
    franjas = {
        'Asia (19:00-03:59)': list(range(19, 24)) + list(range(0, 4)),
        'Londres (04:00-07:59)': list(range(4, 8)),
        'NY apertura (08:00-11:59, incluye ventana Fabian)': list(range(8, 12)),
        'NY tarde (12:00-16:59)': list(range(12, 17)),
        'Cierre/noche (17:00-18:59)': list(range(17, 19)),
    }
    for nombre, horas in franjas.items():
        n = por_hora.loc[por_hora.index.isin(horas)].sum()
        print(f"  {nombre}: {n} señales ({n/40:.1f}/día)")

    señales.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/franjas_horarias/señales_24h_muestra.csv', index=False)
    print("\nGuardado: señales_24h_muestra.csv")
