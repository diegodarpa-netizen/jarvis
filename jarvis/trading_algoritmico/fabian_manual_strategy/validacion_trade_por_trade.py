"""
Validacion trade por trade: para cada operacion de Fabian que cae dentro
de nuestra ventana de 6 meses M1, se reconstruye la vela real de entrada
y se le aplican las MISMAS formulas de deteccion de patron que EstrategiaXAU.pine
(envolvente clasica/martillo/doji, umbrales 85%/50%/15% del Plan Tecnico),
para ver si el codigo reconoceria la misma señal que tomo Fabian a mano.

A pedido de Diego (27/08/2026): "dia por dia, paso a paso... si no entiendo
por que tomo esa decision, ir al PDF" -- esto es exactamente esa auditoria,
hecha programaticamente sobre las 123 operaciones que se pueden verificar.
"""
import pandas as pd
import numpy as np
import pytz

INPUT_OHLC = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
INPUT_FABIAN = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
NY = pytz.timezone('America/New_York')
UTC = pytz.UTC

# Umbrales identicos a EstrategiaXAU.pine
ENV_CLASICA_MIN = 0.85
ENV_MARTILLO_MIN = 0.50
ENV_DOJI_MIN = 0.15


def cargar():
    ohlc = pd.read_csv(INPUT_OHLC, index_col=0)
    ohlc.index = pd.to_datetime(ohlc.index, utc=True)
    fab = pd.read_csv(INPUT_FABIAN)
    fab['Fecha_dt'] = pd.to_datetime(fab['Fecha_dt'])
    return ohlc, fab


def hora_ny_a_utc(fecha, hora_str):
    h, m = map(int, hora_str.split(':'))
    dt_ny = NY.localize(pd.Timestamp(fecha.year, fecha.month, fecha.day, h, m))
    return dt_ny.astimezone(UTC)


def tipo_envolvente(o, h, l, c, es_compra):
    total = h - l
    if total <= 0:
        return 0, "sin rango"
    body = abs(c - o)
    bp = body / total
    if es_compra:
        w_opuesta = (h - max(o, c)) / total
        w_favor = (min(o, c) - l) / total
        direccion_ok = c > o
    else:
        w_opuesta = (min(o, c) - l) / total
        w_favor = (h - max(o, c)) / total
        direccion_ok = c < o

    if not direccion_ok:
        return 0, "vela no es del color esperado"
    if bp >= ENV_CLASICA_MIN and w_opuesta < ENV_DOJI_MIN:
        return 1, "Envolvente clasica"
    elif ENV_MARTILLO_MIN <= bp < ENV_CLASICA_MIN and w_opuesta >= ENV_DOJI_MIN:
        return 2, "Envolvente martillo"
    elif ENV_DOJI_MIN <= w_opuesta <= ENV_CLASICA_MIN and ENV_DOJI_MIN <= w_favor <= ENV_CLASICA_MIN:
        return 3, "Envolvente doji"
    else:
        return 0, f"no cumple ningun umbral (cuerpo={bp*100:.0f}%, mecha_op={w_opuesta*100:.0f}%)"


if __name__ == '__main__':
    ohlc, fab = cargar()
    ini_ventana, fin_ventana = ohlc.index.min().tz_convert(None), ohlc.index.max().tz_convert(None)
    overlap = fab[(fab['Fecha_dt'] >= ini_ventana) & (fab['Fecha_dt'] <= fin_ventana)].copy()

    resultados = []
    for _, t in overlap.iterrows():
        try:
            t_utc = hora_ny_a_utc(t['Fecha_dt'], t['Hora apertura (NY)'])
        except Exception:
            continue
        idx = ohlc.index.get_indexer([t_utc], method='nearest')[0]
        vela = ohlc.iloc[idx]
        es_compra = t['Buy / Sell'] == 'Buy'
        tipo, motivo = tipo_envolvente(vela['open'], vela['high'], vela['low'], vela['close'], es_compra)

        patron_declarado = t['Patrón de entrada'] if pd.notna(t['Patrón de entrada']) else ('START' if t['modelo_limpio'] == 'MEC' else 'MER-sin-patron')
        coincide = (tipo > 0) if 'Envolvente' in str(patron_declarado) else None  # START/MER no se valida por esta via directa

        resultados.append({
            'fecha': t['Fecha_dt'].strftime('%d/%m/%Y'), 'hora': t['Hora apertura (NY)'],
            'modelo': t['modelo_limpio'], 'patron_declarado': patron_declarado,
            'direccion': t['Buy / Sell'], 'resultado_real': t['Resultado'], 'R': t['Beneficio_R'],
            'vela_open': round(vela['open'], 2), 'vela_high': round(vela['high'], 2),
            'vela_low': round(vela['low'], 2), 'vela_close': round(vela['close'], 2),
            'tipo_detectado_codigo': tipo, 'motivo_codigo': motivo,
            'coincide_con_codigo': coincide,
        })

    df_val = pd.DataFrame(resultados)
    print("=" * 100)
    print(f"VALIDACION TRADE POR TRADE -- {len(df_val)} operaciones de Fabian cruzadas contra la vela real M1")
    print("=" * 100)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 200)
    print(df_val[['fecha', 'hora', 'modelo', 'patron_declarado', 'direccion', 'resultado_real', 'R', 'tipo_detectado_codigo', 'coincide_con_codigo']].to_string(index=False))

    con_patron_envolvente = df_val[df_val['patron_declarado'].astype(str).str.contains('Envolvente', na=False)]
    print(f"\n\nDe las operaciones con patron 'Envolvente' declarado ({len(con_patron_envolvente)}):")
    print(f"  El codigo (formulas EstrategiaXAU.pine) reconoce el mismo patron en: {con_patron_envolvente['coincide_con_codigo'].sum()} de {len(con_patron_envolvente)} "
          f"({con_patron_envolvente['coincide_con_codigo'].sum()/len(con_patron_envolvente)*100:.1f}%)")

    no_coincide = con_patron_envolvente[con_patron_envolvente['coincide_con_codigo'] == False]
    print(f"\n--- Casos donde el codigo NO reconoce lo que Fabian marco como Envolvente (revisar contra el PDF) ---")
    print(no_coincide[['fecha', 'hora', 'direccion', 'motivo_codigo']].to_string(index=False))

    df_val.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/validacion_trade_por_trade.csv', index=False)
    print("\nGuardado en validacion_trade_por_trade.csv")
