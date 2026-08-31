"""
20 escenarios de riesgo DINAMICO -- misma mezcla de niveles (1%/1.5%/2%/
2.5%/3%, 20% de las 191 operaciones cada uno), pero en ORDEN distinto en
cada escenario, para separar "cuanto arriesgas en promedio" de "CUANDO
arriesgas mas o menos". Se comparan contra un puñado de reglas con
logica real (no solo azar). A pedido de Diego (27/08/2026).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/20_escenarios_dinamicos.png'
CAPITAL_INICIAL = 10000.0
NIVELES = [0.01, 0.015, 0.02, 0.025, 0.03]
SEED = 42

df = pd.read_csv(INPUT)
df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
df = df.sort_values('Fecha_dt').reset_index(drop=True)
r_serie = df['Beneficio_R'].values
n = len(r_serie)


def correr(riesgos_por_trade):
    capital = CAPITAL_INICIAL
    valores = [capital]
    for r, riesgo in zip(r_serie, riesgos_por_trade):
        capital += capital * riesgo * r
        valores.append(capital)
    s = pd.Series(valores)
    dd = ((s - s.cummax()) / s.cummax() * 100).min()
    return valores, valores[-1], dd


# --- PARTE A: 20 escenarios con la MISMA mezcla (20% cada nivel), orden al azar ---
rng = np.random.default_rng(SEED)
base_mix = np.tile(NIVELES, n // len(NIVELES) + 1)[:n]  # misma cantidad de cada nivel

resultados_random = []
curvas_random = []
for i in range(20):
    mezcla = rng.permutation(base_mix)
    valores, final, dd = correr(mezcla)
    resultados_random.append({'escenario': i + 1, 'capital_final': round(final, 2),
                                'retorno_%': round((final/CAPITAL_INICIAL-1)*100, 1), 'drawdown_max_%': round(dd, 2)})
    curvas_random.append(valores)

tabla_random = pd.DataFrame(resultados_random)
print("=" * 100)
print("PARTE A -- 20 escenarios, MISMA mezcla (20% cada nivel: 1%/1.5%/2%/2.5%/3%), orden al azar")
print("=" * 100)
print(tabla_random.to_string(index=False))
print(f"\nCapital final -- min: ${tabla_random['capital_final'].min():,.0f} | max: ${tabla_random['capital_final'].max():,.0f} | "
      f"promedio: ${tabla_random['capital_final'].mean():,.0f} | desvio estandar: ${tabla_random['capital_final'].std():,.0f}")
print(f"Drawdown -- min: {tabla_random['drawdown_max_%'].min():.1f}% | max: {tabla_random['drawdown_max_%'].max():.1f}% | "
      f"promedio: {tabla_random['drawdown_max_%'].mean():.1f}%")
rango_pct = (tabla_random['capital_final'].max() - tabla_random['capital_final'].min()) / tabla_random['capital_final'].mean() * 100
print(f"Rango entre el mejor y el peor orden, como % del promedio: {rango_pct:.1f}%")

# --- PARTE B: escenarios con logica real ---
print("\n" + "=" * 100)
print("PARTE B -- escenarios con REGLA (no azar), mismo promedio aproximado de riesgo")
print("=" * 100)

# B1: sube tras 2+ ganadoras seguidas, baja tras 2+ perdedoras seguidas
riesgo_b1 = []
racha = 0
tipo_racha = 0
for r in r_serie:
    if racha >= 2 and tipo_racha == 1:
        riesgo_b1.append(0.03)
    elif racha >= 2 and tipo_racha == 0:
        riesgo_b1.append(0.01)
    else:
        riesgo_b1.append(0.02)
    if r > 0:
        racha = racha + 1 if tipo_racha == 1 else 1
        tipo_racha = 1
    elif r < 0:
        racha = racha + 1 if tipo_racha == 0 else 1
        tipo_racha = 0
    else:
        racha, tipo_racha = 0, -1
valores_b1, final_b1, dd_b1 = correr(riesgo_b1)

# B2: CONTRARIAN -- sube tras perder (ilustra que tan mala idea es, dado que no hay autocorrelacion)
riesgo_b2 = []
racha = 0
tipo_racha = 0
for r in r_serie:
    if racha >= 2 and tipo_racha == 0:
        riesgo_b2.append(0.03)
    elif racha >= 2 and tipo_racha == 1:
        riesgo_b2.append(0.01)
    else:
        riesgo_b2.append(0.02)
    if r > 0:
        racha = racha + 1 if tipo_racha == 1 else 1
        tipo_racha = 1
    elif r < 0:
        racha = racha + 1 if tipo_racha == 0 else 1
        tipo_racha = 0
    else:
        racha, tipo_racha = 0, -1
valores_b2, final_b2, dd_b2 = correr(riesgo_b2)

# B3: retrospectivo por mes (sabiendo el win rate real de cada mes -- referencia, no una regla predictiva real)
df['mes'] = df['Fecha_dt'].dt.to_period('M')
wr_por_mes = df.groupby('mes')['Beneficio_R'].apply(lambda x: (x > 0).mean())
riesgo_b3 = []
for _, row in df.iterrows():
    wr_mes = wr_por_mes[row['mes']]
    if wr_mes >= 0.70:
        riesgo_b3.append(0.03)
    elif wr_mes <= 0.55:
        riesgo_b3.append(0.01)
    else:
        riesgo_b3.append(0.02)
valores_b3, final_b3, dd_b3 = correr(riesgo_b3)

# B4: fijo 2% (referencia)
valores_fijo, final_fijo, dd_fijo = correr([0.02]*n)

tabla_b = pd.DataFrame([
    {'escenario': 'B1: sube tras 2+ ganadoras, baja tras 2+ perdedoras', 'capital_final': round(final_b1,2), 'retorno_%': round((final_b1/CAPITAL_INICIAL-1)*100,1), 'drawdown_max_%': round(dd_b1,2)},
    {'escenario': 'B2: CONTRARIAN -- sube tras perder (control)', 'capital_final': round(final_b2,2), 'retorno_%': round((final_b2/CAPITAL_INICIAL-1)*100,1), 'drawdown_max_%': round(dd_b2,2)},
    {'escenario': 'B3: retrospectivo, alto riesgo en meses fuertes (sabiendo el futuro)', 'capital_final': round(final_b3,2), 'retorno_%': round((final_b3/CAPITAL_INICIAL-1)*100,1), 'drawdown_max_%': round(dd_b3,2)},
    {'escenario': 'B4: fijo 2% (referencia)', 'capital_final': round(final_fijo,2), 'retorno_%': round((final_fijo/CAPITAL_INICIAL-1)*100,1), 'drawdown_max_%': round(dd_fijo,2)},
])
print(tabla_b.to_string(index=False))

tabla_random.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/20_escenarios_random_resumen.csv', index=False)
tabla_b.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/escenarios_con_regla_resumen.csv', index=False)

# --- Grafico ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8), dpi=130)
for curva in curvas_random:
    ax1.plot(range(len(curva)), curva, color='#1f77b4', alpha=0.25, linewidth=1)
ax1.plot(range(len(curvas_random[0])), np.mean(curvas_random, axis=0), color='#1f77b4', linewidth=2.5, label='Promedio de los 20')
ax1.axhline(CAPITAL_INICIAL, color='gray', linestyle=':', linewidth=0.8)
ax1.set_title('20 escenarios -- misma mezcla (20% cada nivel), orden al azar', fontsize=12, fontweight='bold')
ax1.set_xlabel('N° de operación')
ax1.set_ylabel('Capital (USD)')
ax1.legend()
ax1.grid(alpha=0.3)

colores_b = ['#2ca02c', '#d62728', '#9467bd', '#888888']
for valores, color, nombre in zip([valores_b1, valores_b2, valores_b3, valores_fijo], colores_b,
                                    ['B1: sube tras ganar', 'B2: sube tras perder (control)', 'B3: retrospectivo por mes', 'B4: fijo 2%']):
    ax2.plot(range(len(valores)), valores, color=color, linewidth=2, label=f'{nombre} (USD {valores[-1]:,.0f})')
ax2.axhline(CAPITAL_INICIAL, color='gray', linestyle=':', linewidth=0.8)
ax2.set_title('Escenarios con REGLA vs. fijo 2%', fontsize=12, fontweight='bold')
ax2.set_xlabel('N° de operación')
ax2.set_ylabel('Capital (USD)')
ax2.legend(fontsize=9)
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT, bbox_inches='tight')
print(f"\nGrafico guardado en {OUT}")
