"""
Escenario con $10.000 desde el inicio del historial de Fabian
(27/10/2025), interes compuesto, comparado contra varios otros
escenarios. A pedido de Diego (27/08/2026).

Escenarios:
1. 1% de riesgo compuesto (el supuesto base que venimos usando)
2. 0.5% de riesgo compuesto (conservador)
3. 2% de riesgo compuesto (agresivo)
4. 1% SIN componer (fijo $100 por R todo el periodo)
5. 1% compuesto pero SIN Hedge Position (dado el hallazgo de que los
   dias con hedge rinden peor en promedio)
6. Comprar y mantener oro en el mismo periodo exacto (benchmark real,
   GC=F via Yahoo Finance)
"""
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/escenario_10000usd.png'
CAPITAL_INICIAL = 10000.0


def cargar():
    df = pd.read_csv(INPUT)
    df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
    df = df.sort_values('Fecha_dt').reset_index(drop=True)
    return df


def curva_compuesta(r_serie, riesgo_pct, capital_inicial=CAPITAL_INICIAL):
    capital = capital_inicial
    valores = [capital]
    for r in r_serie:
        capital += capital * riesgo_pct * r
        valores.append(capital)
    return valores


def curva_fija(r_serie, riesgo_pct, capital_inicial=CAPITAL_INICIAL):
    r_fijo = capital_inicial * riesgo_pct
    capital = capital_inicial
    valores = [capital]
    for r in r_serie:
        capital += r_fijo * r
        valores.append(capital)
    return valores


def max_drawdown(valores):
    s = pd.Series(valores)
    pico = s.cummax()
    dd = (s - pico) / pico * 100
    return dd.min()


if __name__ == '__main__':
    df = cargar()
    r_todas = df['Beneficio_R'].values
    r_sin_hedge = df[~df['es_hedge']]['Beneficio_R'].values

    escenarios = {
        '1% compuesto (base)': curva_compuesta(r_todas, 0.01),
        '0.5% compuesto (conservador)': curva_compuesta(r_todas, 0.005),
        '2% compuesto (agresivo)': curva_compuesta(r_todas, 0.02),
        '1% SIN componer (fijo)': curva_fija(r_todas, 0.01),
        '1% compuesto, SIN Hedge Position': curva_compuesta(r_sin_hedge, 0.01),
    }

    # Buy & hold oro, mismo periodo exacto
    ini_fecha = df['Fecha_dt'].min().strftime('%Y-%m-%d')
    fin_fecha = df['Fecha_dt'].max().strftime('%Y-%m-%d')
    gold = yf.download('GC=F', start=ini_fecha, end=pd.Timestamp(fin_fecha) + pd.Timedelta(days=2), progress=False)
    gold.columns = gold.columns.get_level_values(0)
    precio_ini = gold['Close'].iloc[0]
    precio_fin = gold['Close'].iloc[-1]
    bh_valores = (CAPITAL_INICIAL * gold['Close'] / precio_ini).tolist()

    print("=" * 100)
    print(f"ESCENARIO $10.000 -- {ini_fecha} a {fin_fecha} ({len(df)} operaciones)")
    print("=" * 100)
    resumen = []
    for nombre, valores in escenarios.items():
        final = valores[-1]
        ret_pct = (final / CAPITAL_INICIAL - 1) * 100
        dd = max_drawdown(valores)
        print(f"{nombre:38s} -> ${final:>10,.2f}  ({ret_pct:+7.1f}%)  | Drawdown max: {dd:6.2f}%")
        resumen.append({'escenario': nombre, 'final_usd': round(final, 2), 'retorno_%': round(ret_pct, 1), 'drawdown_max_%': round(dd, 2)})

    bh_final = bh_valores[-1]
    bh_ret = (bh_final / CAPITAL_INICIAL - 1) * 100
    bh_dd = max_drawdown(bh_valores)
    print(f"{'Comprar y mantener ORO (benchmark)':38s} -> ${bh_final:>10,.2f}  ({bh_ret:+7.1f}%)  | Drawdown max: {bh_dd:6.2f}%")
    resumen.append({'escenario': 'Comprar y mantener ORO', 'final_usd': round(bh_final, 2), 'retorno_%': round(bh_ret, 1), 'drawdown_max_%': round(bh_dd, 2)})

    pd.DataFrame(resumen).to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/escenario_10000_resumen.csv', index=False)

    # --- Grafico ---
    fig, axes = plt.subplots(2, 1, figsize=(16, 11), dpi=130, gridspec_kw={'height_ratios': [2.2, 1]})
    ax1 = axes[0]
    colores = {'1% compuesto (base)': '#2ca02c', '0.5% compuesto (conservador)': '#1f77b4',
               '2% compuesto (agresivo)': '#d62728', '1% SIN componer (fijo)': '#888888',
               '1% compuesto, SIN Hedge Position': '#9467bd'}
    for nombre, valores in escenarios.items():
        ax1.plot(range(len(valores)), valores, label=f'{nombre} (${valores[-1]:,.0f})',
                  color=colores.get(nombre), linewidth=1.6 if '1% compuesto (base)' in nombre else 1.1)
    ax1.axhline(CAPITAL_INICIAL, color='black', linestyle=':', linewidth=0.8)
    ax1.set_title(f'Escenario USD 10.000 -- estrategia de Fabian, {len(df)} operaciones, {ini_fecha} a {fin_fecha}', fontsize=13, fontweight='bold')
    ax1.set_xlabel('N° de operación')
    ax1.set_ylabel('Capital (USD)')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(alpha=0.3)

    ax2 = axes[1]
    fechas_bh = gold.index
    x_bh = np.linspace(0, len(escenarios['1% compuesto (base)']) - 1, len(bh_valores))
    ax2.plot(x_bh, bh_valores, label=f'Comprar y mantener oro (${bh_final:,.0f})', color='#d4af37', linewidth=1.6)
    ax2.plot(range(len(escenarios['1% compuesto (base)'])), escenarios['1% compuesto (base)'],
              label=f'Estrategia Fabian, 1% compuesto (${escenarios["1% compuesto (base)"][-1]:,.0f})', color='#2ca02c', linewidth=1.6)
    ax2.axhline(CAPITAL_INICIAL, color='black', linestyle=':', linewidth=0.8)
    ax2.set_title('Estrategia vs. Comprar y Mantener oro (mismo período exacto)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Tiempo (escala aproximada, N° operación / días)')
    ax2.set_ylabel('Capital (USD)')
    ax2.legend(loc='upper left', fontsize=9)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUT, bbox_inches='tight')
    print(f"\nGrafico guardado en {OUT}")
