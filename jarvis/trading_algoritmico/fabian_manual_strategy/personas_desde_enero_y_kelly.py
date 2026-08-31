"""
1) 5 personas (distinta aversion al riesgo) arrancando el 1/1/2026 con
   USD 10.000, usando SOLO las operaciones reales de Fabian desde esa
   fecha (152 de 191).
2) Criterio de Kelly real calculado sobre los datos de Fabian, comparado
   contra la franja 1%-3% que veniamos usando.
A pedido de Diego (27/08/2026).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/personas_desde_enero_2026.png'
CAPITAL_INICIAL = 10000.0
NIVELES = [1.0, 1.5, 2.0, 2.5, 3.0]
COLORES = ['#1a9850', '#66bd63', '#fee08b', '#fc8d59', '#d73027']

df = pd.read_csv(INPUT)
df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
df = df.sort_values('Fecha_dt').reset_index(drop=True)
df_2026 = df[df['Fecha_dt'] >= '2026-01-01'].reset_index(drop=True)
r_serie = df_2026['Beneficio_R'].values

print("=" * 100)
print(f"5 PERSONAS DESDE EL 1/1/2026 -- {len(df_2026)} operaciones reales, USD 10.000 iniciales cada una")
print("=" * 100)

resumen = []
fig, ax = plt.subplots(figsize=(15, 8), dpi=130)
for pct, color in zip(NIVELES, COLORES):
    riesgo = pct / 100
    capital = CAPITAL_INICIAL
    valores = [capital]
    for r in r_serie:
        capital += capital * riesgo * r
        valores.append(capital)
    s = pd.Series(valores)
    dd = ((s - s.cummax()) / s.cummax() * 100).min()
    ax.plot(range(len(valores)), valores, color=color, linewidth=1.8,
             label=f'{pct}% -> USD {valores[-1]:,.0f} ({(valores[-1]/CAPITAL_INICIAL-1)*100:+.0f}%, DD max {dd:.1f}%)')
    resumen.append({'persona_riesgo_%': pct, 'capital_final': round(valores[-1],2),
                     'retorno_%': round((valores[-1]/CAPITAL_INICIAL-1)*100,1), 'drawdown_max_%': round(dd,2)})

ax.axhline(CAPITAL_INICIAL, color='gray', linestyle=':', linewidth=0.8)
ax.set_title(f'5 personas, mismo arranque USD 10.000, 1/1/2026 -> hoy ({len(df_2026)} operaciones reales de Fabian)',
              fontsize=13, fontweight='bold')
ax.set_xlabel('N° de operación')
ax.set_ylabel('Capital (USD)')
ax.legend(loc='upper left', fontsize=10)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUT, bbox_inches='tight')

tabla = pd.DataFrame(resumen)
print(tabla.to_string(index=False))
print(f"\nGrafico guardado en {OUT}")

print("\n" + "=" * 100)
print("CRITERIO DE KELLY -- el numero 'matematicamente optimo' segun la teoria clasica")
print("=" * 100)
ganadoras = df['Beneficio_R'][df['Beneficio_R'] > 0]
perdedoras = df['Beneficio_R'][df['Beneficio_R'] < 0]
p = len(ganadoras) / len(df)
avg_win = ganadoras.mean()
avg_loss = abs(perdedoras.mean())
b = avg_win / avg_loss
q = 1 - p
kelly = p - q / b
print(f"Win rate (p): {p*100:.2f}% | Ratio ganancia/perdida promedio (b): {b:.3f}")
print(f"Kelly completo: {kelly*100:.2f}%")
print(f"Half-Kelly (practica estandar profesional): {kelly*50:.2f}%")
print(f"Quarter-Kelly: {kelly*25:.2f}%")
print(f"1/8 Kelly: {kelly*12.5:.2f}%")
print(f"\nNuestra franja ya usada (1%-3%) equivale a Kelly/{kelly*100/1:.1f} hasta Kelly/{kelly*100/3:.1f} -- es decir,")
print(f"un 3% de riesgo real es apenas 1/{kelly*100/3:.0f} del Kelly completo -- ya tenemos margen de sobra.")
