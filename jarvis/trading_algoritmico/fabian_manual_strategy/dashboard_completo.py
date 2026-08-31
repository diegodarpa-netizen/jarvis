"""
Dashboard visual completo del historial de Fabian -- tortas, barras,
equity curve, drawdown, R semanal. A pedido de Diego (27/08/2026): usa
el 100% de las 191 operaciones (esto no tiene hueco de datos, a diferencia
del cruce contra velas reales que si depende de que tengamos M1 de esas
fechas).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
OUTPUT_PNG = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/fabian_dashboard_completo.png'

COLOR_WIN = '#2ca02c'
COLOR_LOSS = '#d62728'
COLOR_BE = '#888888'
COLOR_MEC = '#1f77b4'
COLOR_MER = '#ff7f0e'


def cargar():
    df = pd.read_csv(INPUT)
    df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
    df = df.sort_values('Fecha_dt').reset_index(drop=True)
    return df


if __name__ == '__main__':
    df = cargar()

    fig = plt.figure(figsize=(22, 20), dpi=120)
    gs = fig.add_gridspec(4, 3, hspace=0.45, wspace=0.3)

    # --- 1. Torta: ganadoras/perdedoras/breakeven ---
    ax1 = fig.add_subplot(gs[0, 0])
    gan = (df['Beneficio_R'] > 0).sum()
    per = (df['Beneficio_R'] < 0).sum()
    be = (df['Beneficio_R'] == 0).sum()
    ax1.pie([gan, per, be], labels=[f'Ganadoras\n{gan} ({gan/len(df)*100:.1f}%)',
                                     f'Perdedoras\n{per} ({per/len(df)*100:.1f}%)',
                                     f'Breakeven\n{be} ({be/len(df)*100:.1f}%)'],
            colors=[COLOR_WIN, COLOR_LOSS, COLOR_BE], autopct='', startangle=90,
            textprops={'fontsize': 9})
    ax1.set_title(f'Resultado -- {len(df)} operaciones totales', fontsize=12, fontweight='bold')

    # --- 2. Torta: MEC vs MER ---
    ax2 = fig.add_subplot(gs[0, 1])
    mec_n = (df['modelo_limpio'] == 'MEC').sum()
    mer_n = (df['modelo_limpio'] == 'MER').sum()
    ax2.pie([mec_n, mer_n], labels=[f'MEC\n{mec_n} ops', f'MER\n{mer_n} ops'],
            colors=[COLOR_MEC, COLOR_MER], autopct='', startangle=90, textprops={'fontsize': 9})
    ax2.set_title('Modelo de entrada', fontsize=12, fontweight='bold')

    # --- 3. Torta: Envolvente vs START (dentro de MEC) ---
    ax3 = fig.add_subplot(gs[0, 2])
    env_n = (df['Patrón de entrada'] == 'Envolvente').sum()
    start_n = (df['Patrón de entrada'] == 'START').sum()
    ax3.pie([env_n, start_n], labels=[f'Envolvente\n{env_n} ops', f'START\n{start_n} ops'],
            colors=['#9467bd', '#8c564b'], autopct='', startangle=90, textprops={'fontsize': 9})
    ax3.set_title('Patrón de entrada (dentro de MEC)', fontsize=12, fontweight='bold')

    # --- 4. Torta: Buy vs Sell ---
    ax4 = fig.add_subplot(gs[1, 0])
    buy_n = (df['Buy / Sell'] == 'Buy').sum()
    sell_n = (df['Buy / Sell'] == 'Sell').sum()
    ax4.pie([buy_n, sell_n], labels=[f'Buy\n{buy_n} ops', f'Sell\n{sell_n} ops'],
            colors=['#17becf', '#e377c2'], autopct='', startangle=90, textprops={'fontsize': 9})
    ax4.set_title('Dirección', fontsize=12, fontweight='bold')

    # --- 5. Barras: Win rate por categoría ---
    ax5 = fig.add_subplot(gs[1, 1:])
    categorias = []
    win_rates = []
    ns = []
    for col, val in [('modelo_limpio', 'MEC'), ('modelo_limpio', 'MER'),
                      ('Patrón de entrada', 'Envolvente'), ('Patrón de entrada', 'START'),
                      ('Buy / Sell', 'Buy'), ('Buy / Sell', 'Sell')]:
        sub = df[df[col] == val]
        if len(sub) > 0:
            categorias.append(val)
            win_rates.append((sub['Beneficio_R'] > 0).mean() * 100)
            ns.append(len(sub))
    colores_barras = [COLOR_MEC, COLOR_MER, '#9467bd', '#8c564b', '#17becf', '#e377c2']
    bars = ax5.bar(categorias, win_rates, color=colores_barras)
    ax5.axhline(50, color='gray', linestyle='--', linewidth=1, label='50% (azar)')
    ax5.set_ylabel('Win rate (%)')
    ax5.set_title('Win rate por categoría', fontsize=12, fontweight='bold')
    ax5.legend(fontsize=8)
    for bar, n, wr in zip(bars, ns, win_rates):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{wr:.1f}%\n(n={n})',
                  ha='center', fontsize=8)
    ax5.set_ylim(0, 90)

    # --- 6. Barras: R total por día de semana ---
    ax6 = fig.add_subplot(gs[2, 0])
    orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    r_por_dia = df.groupby('Día')['Beneficio_R'].sum().reindex(orden_dias)
    ax6.bar(orden_dias, r_por_dia.values, color='#1f77b4')
    ax6.set_ylabel('R total acumulado')
    ax6.set_title('R total por día de la semana', fontsize=12, fontweight='bold')
    ax6.tick_params(axis='x', rotation=30)

    # --- 7. Barras: R semanal con línea de objetivo 2R ---
    ax7 = fig.add_subplot(gs[2, 1:])
    df['semana'] = df['Fecha_dt'].dt.to_period('W-SUN')
    r_semanal = df.groupby('semana')['Beneficio_R'].sum()
    colores_sem = [COLOR_WIN if r >= 2 else (COLOR_LOSS if r < 0 else '#f0ad4e') for r in r_semanal.values]
    ax7.bar(range(len(r_semanal)), r_semanal.values, color=colores_sem)
    ax7.axhline(2, color='black', linestyle='--', linewidth=1.2, label='Objetivo 2R/semana')
    ax7.axhline(0, color='gray', linewidth=0.5)
    cumplidas = (r_semanal >= 2).sum()
    ax7.set_title(f'R por semana ({cumplidas}/{len(r_semanal)} semanas cumplieron el objetivo, {cumplidas/len(r_semanal)*100:.0f}%)',
                  fontsize=12, fontweight='bold')
    ax7.set_ylabel('R de la semana')
    ax7.set_xlabel('N° de semana (27/10/2025 → hoy)')
    ax7.legend(fontsize=8)

    # --- 8. Equity curve $1000 ---
    ax8 = fig.add_subplot(gs[3, :2])
    capital = 1000.0
    riesgo_pct = 0.01
    valores = [1000.0]
    for r in df['Beneficio_R']:
        capital += capital * riesgo_pct * r
        valores.append(capital)
    pico = pd.Series(valores).cummax()
    dd = (pd.Series(valores) - pico) / pico * 100
    ax8.plot(range(len(valores)), valores, color=COLOR_WIN, linewidth=1.5)
    ax8.fill_between(range(len(valores)), 1000, valores, where=(pd.Series(valores) >= 1000), color=COLOR_WIN, alpha=0.1)
    ax8.axhline(1000, color='gray', linestyle=':', linewidth=1)
    ax8.set_title(f'USD 1.000 con reinversión (1% de riesgo, SUPUESTO no confirmado) -> USD {valores[-1]:,.0f} ({(valores[-1]/1000-1)*100:+.1f}%)',
                  fontsize=12, fontweight='bold')
    ax8.set_ylabel('Capital (USD)')
    ax8.set_xlabel('N° de operación')

    # --- 9. Drawdown ---
    ax9 = fig.add_subplot(gs[3, 2])
    ax9.fill_between(range(len(dd)), dd.values, 0, color=COLOR_LOSS, alpha=0.4)
    ax9.set_title(f'Drawdown (máx {dd.min():.2f}%)', fontsize=12, fontweight='bold')
    ax9.set_ylabel('Drawdown (%)')
    ax9.set_xlabel('N° de operación')

    fig.suptitle('Dashboard completo -- Estrategia de Fabian (XAU/USD), 191 operaciones, 27/10/2025 → hoy',
                 fontsize=16, fontweight='bold', y=0.995)
    plt.savefig(OUTPUT_PNG, bbox_inches='tight')
    print(f"Guardado en {OUTPUT_PNG}")
