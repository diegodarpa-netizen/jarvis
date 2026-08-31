"""
Barrido de riesgo por operacion, de 1% a 5%, sobre el historial real de
Fabian (191 operaciones, interes compuesto), con $10.000 iniciales. A
pedido de Diego (30/08/2026) -- reproduce el mismo formato que
barrido_riesgo_1_a_10.py (27/08/2026), esta vez acotado a 1%-5%.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/barrido_riesgo_1_a_5.png'
CAPITAL_INICIAL = 10000.0
NIVELES = list(range(1, 6))  # 1% a 5%


def curva_compuesta(r_serie, riesgo_pct, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    valores = [capital]
    for r in r_serie:
        capital += capital * riesgo_pct * r
        valores.append(capital)
    return valores


def max_drawdown(valores):
    s = pd.Series(valores)
    pico = s.cummax()
    dd = (s - pico) / pico * 100
    return dd.min()


def peor_racha_perdedora_impacto(riesgo_pct):
    peor = 1.0
    for r in [-1, -1, -1]:
        peor *= (1 + riesgo_pct * r)
    return (peor - 1) * 100


if __name__ == '__main__':
    df = pd.read_csv(INPUT)
    df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
    df = df.sort_values('Fecha_dt')
    r_serie = df['Beneficio_R'].values
    ini_fecha = df['Fecha_dt'].min().strftime('%d/%m/%Y')
    fin_fecha = df['Fecha_dt'].max().strftime('%d/%m/%Y')

    resumen = []
    curvas = {}
    for pct in NIVELES:
        riesgo = pct / 100
        valores = curva_compuesta(r_serie, riesgo)
        final = valores[-1]
        ret_pct = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        impacto_racha = peor_racha_perdedora_impacto(riesgo)
        curvas[pct] = valores
        resumen.append({
            'riesgo_%': pct, 'capital_final': round(final, 2), 'retorno_%': round(ret_pct, 1),
            'drawdown_max_%': round(dd, 2), 'impacto_racha_3_perdidas_%': round(impacto_racha, 2),
        })

    tabla = pd.DataFrame(resumen)
    print("=" * 100)
    print(f"BARRIDO DE RIESGO 1%-5% -- USD 10.000 iniciales, {len(df)} operaciones reales de Fabian, interes compuesto")
    print(f"Periodo: {ini_fecha} a {fin_fecha}")
    print("=" * 100)
    print(tabla.to_string(index=False))
    tabla.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/barrido_riesgo_1_a_5_resumen.csv', index=False)

    fig = plt.figure(figsize=(20, 14), dpi=120)
    gs = fig.add_gridspec(2, 2, height_ratios=[2, 1], hspace=0.35, wspace=0.25)

    ax1 = fig.add_subplot(gs[0, :])
    cmap = plt.cm.RdYlGn_r
    for i, pct in enumerate(NIVELES):
        color = cmap(i / (len(NIVELES) - 1))
        ax1.plot(range(len(curvas[pct])), curvas[pct], label=f'{pct}% (${curvas[pct][-1]:,.0f})',
                  color=color, linewidth=2.0 if pct in (1, 2) else 1.3)
    ax1.axhline(CAPITAL_INICIAL, color='black', linestyle=':', linewidth=0.8)
    ax1.set_yscale('log')
    ax1.set_title(f'Barrido de riesgo 1%-5% por operación -- USD 10.000 iniciales, {len(df)} operaciones reales, {ini_fecha}-{fin_fecha} (escala log)',
                  fontsize=13, fontweight='bold')
    ax1.set_xlabel('N° de operación')
    ax1.set_ylabel('Capital (USD, escala log)')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(alpha=0.3, which='both')

    ax2 = fig.add_subplot(gs[1, 0])
    barras = ax2.bar(tabla['riesgo_%'].astype(str) + '%', tabla['retorno_%'], color=cmap(np.linspace(0, 1, len(NIVELES))))
    ax2.set_title('Retorno total por nivel de riesgo', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Retorno (%)')
    for bar, val in zip(barras, tabla['retorno_%']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(tabla['retorno_%'])*0.01, f'{val:,.0f}%', ha='center', fontsize=9)

    ax3 = fig.add_subplot(gs[1, 1])
    barras2 = ax3.bar(tabla['riesgo_%'].astype(str) + '%', tabla['drawdown_max_%'], color=cmap(np.linspace(0, 1, len(NIVELES))))
    ax3.set_title('Drawdown máximo por nivel de riesgo', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Drawdown máximo (%)')
    for bar, val in zip(barras2, tabla['drawdown_max_%']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 1.5, f'{val:.1f}%', ha='center', fontsize=9, color='white', fontweight='bold')

    plt.savefig(OUT, bbox_inches='tight')
    print(f"\nGrafico guardado en {OUT}")
