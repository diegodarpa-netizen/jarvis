"""
Vista previa (mockup en Python, sobre velas reales) del estilo visual
aprobado en "Apariencia del indicador XAU.pdf": lineas punteadas en los
niveles M3 + cartel tipo nube (fondo gris, texto blanco mayuscula
negrita) arriba de la vela para SELL, abajo para BUY. Sirve para
previsualizar antes de pegar en TradingView. A pedido de Diego
(27/08/2026).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading/xau_strategy/data/XAUUSD_M1.csv'
FABIAN = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/preview_apariencia_indicador.png'


def cargar():
    ohlc = pd.read_csv(INPUT, index_col=0)
    ohlc.index = pd.to_datetime(ohlc.index, utc=True)
    fab = pd.read_csv(FABIAN)
    fab['Fecha_dt'] = pd.to_datetime(fab['Fecha_dt'])
    return ohlc.sort_index(), fab


def dibujar_velas(ax, g):
    for i in range(len(g)):
        o, h, l, c = g['open'].iloc[i], g['high'].iloc[i], g['low'].iloc[i], g['close'].iloc[i]
        color = 'black' if c >= o else 'white'
        edge = 'black'
        ax.plot([i, i], [l, h], color='black', linewidth=0.8, zorder=2)
        alto = abs(c - o) if abs(c - o) > 1e-9 else 0.01
        base = min(o, c)
        rect = patches.Rectangle((i - 0.3, base), 0.6, alto, facecolor=color, edgecolor=edge, linewidth=0.6, zorder=3)
        ax.add_patch(rect)


def nube_label(ax, x, y, texto, arriba):
    """Cartel tipo nube -- fondo gris claro, texto blanco mayuscula negrita,
    apuntando hacia la vela (abajo si esta arriba de la vela = SELL,
    arriba si esta abajo = BUY)."""
    offset = 1 if arriba else -1
    y_caja = y + offset * 1.2
    box = FancyBboxPatch((x - 0.9, y_caja - 0.35 * offset if not arriba else y_caja),
                          1.8, 0.7, boxstyle="round,pad=0.15,rounding_size=0.3",
                          facecolor='#8c8c8c', edgecolor='#6b6b6b', zorder=6)
    ax.add_patch(box)
    ax.text(x, y_caja + 0.35, texto, ha='center', va='center', color='white',
             fontsize=9, fontweight='bold', zorder=7)
    ax.plot([x, x], [y, y_caja if arriba else y_caja + 0.7], color='#6b6b6b', linewidth=1.2, zorder=5)


if __name__ == '__main__':
    ohlc, fab = cargar()
    # tomar un dia real de Fabian con MEC->Envolvente para el ejemplo
    ejemplo = fab[(fab['Patrón de entrada'] == 'Envolvente') & (fab['Resultado'] == 'Take Profit')].iloc[10]
    fecha = ejemplo['Fecha_dt']
    dia_ohlc = ohlc[ohlc.index.date == fecha.date()]

    if len(dia_ohlc) < 20:
        # fallback: usar el primer dia disponible con suficientes velas
        for _, ev in fab.iterrows():
            d = ohlc[ohlc.index.date == ev['Fecha_dt'].date()]
            if len(d) >= 20:
                dia_ohlc, fecha, ejemplo = d, ev['Fecha_dt'], ev
                break

    dia_ohlc = dia_ohlc.reset_index()
    dia_ohlc.columns = ['time', 'open', 'high', 'low', 'close', 'n_ticks']

    # recortar a una ventana angosta alrededor de la mitad de la sesion,
    # igual que los ejemplos del PDF (~60-70 min de contexto, no el dia entero)
    centro = len(dia_ohlc) // 2
    dia_ohlc = dia_ohlc.iloc[max(0, centro-35):centro+35].reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(14, 8), dpi=130, facecolor='#131722')
    ax.set_facecolor('#131722')
    dibujar_velas(ax, dia_ohlc)

    # niveles M3 de ejemplo (2-3 dashed lines representativas, estilo del PDF)
    n = len(dia_ohlc)
    idx_entrada = min(n // 2, n - 5)
    nivel1 = dia_ohlc['low'].iloc[max(0, idx_entrada-15):idx_entrada].min()
    nivel2 = dia_ohlc['high'].iloc[max(0, idx_entrada-8):idx_entrada].max()
    ax.plot([max(0, idx_entrada-15), idx_entrada+5], [nivel1, nivel1], color='#787b86', linestyle='--', linewidth=1, alpha=0.8)
    ax.plot([max(0, idx_entrada-8), idx_entrada+10], [nivel2, nivel2], color='#787b86', linestyle='--', linewidth=1, alpha=0.8)

    precio_entrada = dia_ohlc['low'].iloc[idx_entrada]
    es_buy = ejemplo['Buy / Sell'] == 'Buy'
    nube_label(ax, idx_entrada, precio_entrada if es_buy else dia_ohlc['high'].iloc[idx_entrada],
               'BUY' if es_buy else 'SELL', arriba=not es_buy)

    ax.tick_params(colors='#787b86')
    for spine in ax.spines.values():
        spine.set_color('#2a2e39')
    ax.set_title(f"Vista previa estilo aprobado -- {fecha.strftime('%d/%m/%Y')} -- {ejemplo['modelo_limpio']} -> {ejemplo['Patrón de entrada']} ({'BUY' if es_buy else 'SELL'})",
                 color='white', fontsize=12, fontweight='bold')
    ax.set_ylabel('Precio (USD)', color='white')

    plt.tight_layout()
    plt.savefig(OUT, bbox_inches='tight', facecolor='#131722')
    print(f"Guardado en {OUT}")
    print(f"Ejemplo usado: {fecha.strftime('%d/%m/%Y')}, {ejemplo['Buy / Sell']}, {ejemplo['Resultado']}, {ejemplo['Beneficio_R']}R")
