"""
Ganancia (equity) y perdida (drawdown) lado a lado, para los 5 escenarios
1%-3%, sin filtrar por tolerancia -- a pedido explicito de Diego
(27/08/2026): mostrar los numeros crudos, pasivo a agresivo.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/ganancia_vs_perdida_1_3.png'
CAPITAL_INICIAL = 10000.0
NIVELES = [1.0, 1.5, 2.0, 2.5, 3.0]
COLORES = ['#1a9850', '#66bd63', '#fee08b', '#fc8d59', '#d73027']

df = pd.read_csv(INPUT)
df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
df = df.sort_values('Fecha_dt').reset_index(drop=True)
r_serie = df['Beneficio_R'].values

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(17, 12), dpi=130, sharex=True,
                                 gridspec_kw={'height_ratios': [2, 1.3]})

resumen = []
for pct, color in zip(NIVELES, COLORES):
    riesgo = pct / 100
    capital = CAPITAL_INICIAL
    valores = [capital]
    for r in r_serie:
        capital += capital * riesgo * r
        valores.append(capital)
    s = pd.Series(valores)
    pico = s.cummax()
    dd_pct = (s - pico) / pico * 100
    dd_usd = s - pico

    ax1.plot(range(len(s)), s.values, color=color, linewidth=1.8,
              label=f'{pct}% -> USD {valores[-1]:,.0f} (+{(valores[-1]/CAPITAL_INICIAL-1)*100:.0f}%)')
    ax2.fill_between(range(len(s)), dd_usd.values, 0, color=color, alpha=0.55,
                       label=f'{pct}% (peor %: {dd_pct.min():.1f}% | peor USD: -{abs(dd_usd.min()):,.0f})')

    resumen.append({'riesgo_%': pct, 'final_$': round(valores[-1],2),
                     'peor_caida_%_valor': round(dd_pct.min(),2), 'peor_caida_$_en_ese_punto': round(dd_usd[dd_pct.idxmin()],2),
                     'peor_caida_$_valor': round(dd_usd.min(),2), 'peor_caida_%_en_ese_punto': round(dd_pct[dd_usd.idxmin()],2)})

ax1.axhline(CAPITAL_INICIAL, color='black', linestyle=':', linewidth=0.9)
ax1.set_title('GANANCIA -- USD 10.000 iniciales, 191 operaciones reales de Fabian, interés compuesto', fontsize=13, fontweight='bold')
ax1.set_ylabel('Capital (USD)')
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(alpha=0.3)

ax2.axhline(0, color='black', linewidth=0.8)
ax2.set_title('PÉRDIDA -- caída en dólares reales desde el máximo previo (drawdown), mismo eje temporal', fontsize=13, fontweight='bold')
ax2.set_ylabel('Caída desde el pico (USD)')
ax2.set_xlabel('N° de operación')
ax2.legend(loc='lower left', fontsize=9)
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT, bbox_inches='tight')
print(f"Guardado en {OUT}")
print(pd.DataFrame(resumen).to_string(index=False))
