"""
Dashboard del backtest 2022 (codigo) + comparacion directa contra Fabian
(real). A pedido de Diego (27/08/2026).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BT = pd.read_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/backtest_2022_resultados.csv')
FAB = pd.read_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv')
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/backtest_2022_vs_fabian.png'

BT['t_entrada'] = pd.to_datetime(BT['t_entrada'])
BT = BT.sort_values('t_entrada').reset_index(drop=True)

COLOR_WIN, COLOR_LOSS = '#2ca02c', '#d62728'

fig = plt.figure(figsize=(22, 16), dpi=120)
gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)

# 1. Torta resultado backtest 2022
ax1 = fig.add_subplot(gs[0, 0])
gan, per = (BT['R'] > 0).sum(), (BT['R'] < 0).sum()
ax1.pie([gan, per], labels=[f'Ganadoras\n{gan} ({gan/len(BT)*100:.1f}%)', f'Perdedoras\n{per} ({per/len(BT)*100:.1f}%)'],
        colors=[COLOR_WIN, COLOR_LOSS], startangle=90, textprops={'fontsize': 9})
ax1.set_title(f'Backtest 2022 (código) -- {len(BT)} operaciones', fontsize=11, fontweight='bold')

# 2. Torta por modelo (backtest)
ax2 = fig.add_subplot(gs[0, 1])
conteo_modelo = BT['modelo'].value_counts()
ax2.pie(conteo_modelo.values, labels=[f'{m}\n{n} ops' for m, n in conteo_modelo.items()],
        colors=['#1f77b4', '#9467bd', '#ff7f0e'], startangle=90, textprops={'fontsize': 9})
ax2.set_title('Backtest 2022 -- por modelo de entrada', fontsize=11, fontweight='bold')

# 3. Comparacion win rate: Fabian real vs Backtest codigo
ax3 = fig.add_subplot(gs[0, 2])
wr_fabian = (FAB['Beneficio_R'] > 0).mean() * 100
wr_bt = (BT['R'] > 0).mean() * 100
bars = ax3.bar(['Fabian\n(real, mano)', 'Backtest 2022\n(código)'], [wr_fabian, wr_bt],
                color=['#2ca02c', '#1f77b4'])
ax3.axhline(50, color='gray', linestyle='--', linewidth=1)
ax3.set_ylabel('Win rate (%)')
ax3.set_title('Win rate: humano vs código', fontsize=11, fontweight='bold')
for bar, wr in zip(bars, [wr_fabian, wr_bt]):
    ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, f'{wr:.1f}%', ha='center', fontsize=10, fontweight='bold')
ax3.set_ylim(0, 80)

# 4. Win rate por modelo, backtest
ax4 = fig.add_subplot(gs[1, 0])
wr_por_modelo = BT.groupby('modelo')['R'].apply(lambda x: (x>0).mean()*100)
ax4.bar(wr_por_modelo.index, wr_por_modelo.values, color=['#1f77b4', '#9467bd', '#ff7f0e'])
ax4.axhline(50, color='gray', linestyle='--', linewidth=1)
ax4.set_ylabel('Win rate (%)')
ax4.set_title('Backtest 2022 -- win rate por modelo', fontsize=11, fontweight='bold')
ax4.set_ylim(0, 80)

# 5. R mensual 2022 (linea)
ax5 = fig.add_subplot(gs[1, 1:])
BT['mes'] = BT['t_entrada'].dt.to_period('M')
r_mensual = BT.groupby('mes')['R'].sum()
colores_mes = [COLOR_WIN if r >= 0 else COLOR_LOSS for r in r_mensual.values]
ax5.bar(r_mensual.index.astype(str), r_mensual.values, color=colores_mes)
ax5.axhline(0, color='gray', linewidth=0.5)
ax5.set_title('Backtest 2022 -- R total por mes', fontsize=11, fontweight='bold')
ax5.set_ylabel('R del mes')
ax5.tick_params(axis='x', rotation=45)

# 6. Equity curve 2022 (compuesto, 1% riesgo, mismo supuesto que Fabian)
ax6 = fig.add_subplot(gs[2, :2])
capital = 1000.0
valores = [1000.0]
for r in BT['R']:
    capital += capital * 0.01 * r
    valores.append(capital)
ax6.plot(range(len(valores)), valores, color='#1f77b4', linewidth=1.3)
ax6.axhline(1000, color='gray', linestyle=':', linewidth=1)
ax6.fill_between(range(len(valores)), 1000, valores, alpha=0.1, color='#1f77b4')
ax6.set_title(f'Backtest 2022 -- USD 1.000 con reinversión (1% riesgo) -> USD {valores[-1]:,.0f} ({(valores[-1]/1000-1)*100:+.1f}%)',
              fontsize=11, fontweight='bold')
ax6.set_xlabel('N° de operación')
ax6.set_ylabel('Capital (USD)')

# 7. Comparacion directa de metricas clave (tabla visual como barras normalizadas)
ax7 = fig.add_subplot(gs[2, 2])
metricas = ['Win rate %', 'Prom. R x10', 'Ops/mes']
fab_vals = [wr_fabian, FAB['Beneficio_R'].mean()*10, len(FAB)/10]  # ~10 meses de Fabian
bt_vals = [wr_bt, BT['R'].mean()*10, len(BT)/12]
x = np.arange(len(metricas))
width = 0.35
ax7.bar(x - width/2, fab_vals, width, label='Fabian (real)', color=COLOR_WIN)
ax7.bar(x + width/2, bt_vals, width, label='Backtest 2022 (código)', color='#1f77b4')
ax7.set_xticks(x)
ax7.set_xticklabels(metricas, fontsize=8)
ax7.legend(fontsize=8)
ax7.set_title('Comparación directa', fontsize=11, fontweight='bold')

fig.suptitle('Backtest 2022 (código EstrategiaXAU) vs. Fabian (ejecución real a mano)', fontsize=15, fontweight='bold', y=0.995)
plt.savefig(OUT, bbox_inches='tight')
print(f"Guardado en {OUT}")
