"""
"5 personas frias", cada una operando la MISMA estrategia real de Fabian
con un nivel de riesgo distinto (1%/1.5%/2%/2.5%/3%), las 5 arrancando
con USD 10.000 -- proyectadas a 1 año completo (365 dias), asumiendo que
el ritmo/edge observado en los 304 dias reales (27/10/2025-27/08/2026)
se sostiene. A pedido de Diego (27/08/2026).

Metodo: se anualiza el retorno COMPUESTO real observado (tecnica estandar
de finanzas para proyectar un periodo parcial a un año completo) --
NO se inventan operaciones nuevas, se extrapola la tasa de crecimiento
ya demostrada. Esto es una PROYECCION con el supuesto explicito de que
el ritmo se mantiene -- no una garantia.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/fabian_consolidado_limpio.csv'
OUT = '/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/graficos/panorama_1_anio.png'
CAPITAL_INICIAL = 10000.0
NIVELES = [1.0, 1.5, 2.0, 2.5, 3.0]
COLORES = ['#1a9850', '#66bd63', '#fee08b', '#fc8d59', '#d73027']

df = pd.read_csv(INPUT)
df['Fecha_dt'] = pd.to_datetime(df['Fecha_dt'])
df = df.sort_values('Fecha_dt').reset_index(drop=True)
r_serie = df['Beneficio_R'].values

dias_reales = (df['Fecha_dt'].max() - df['Fecha_dt'].min()).days  # 304
factor_anualizacion = 365 / dias_reales

resumen = []
fig, ax = plt.subplots(figsize=(15, 9), dpi=130)

for pct, color in zip(NIVELES, COLORES):
    riesgo = pct / 100
    capital = CAPITAL_INICIAL
    valores = [capital]
    for r in r_serie:
        capital += capital * riesgo * r
        valores.append(capital)
    retorno_real = valores[-1] / CAPITAL_INICIAL  # ej. 1.05 = +105%
    retorno_anualizado = retorno_real ** factor_anualizacion
    capital_1_anio = CAPITAL_INICIAL * retorno_anualizado

    # curva proyectada: escalar el eje X de "operaciones en 304 dias" a "operaciones en 365 dias" (mismo ritmo)
    x_real = np.linspace(0, dias_reales, len(valores))
    x_proyectado_max = 365
    ax.plot(x_real, valores, color=color, linewidth=2.2, label=f'{pct}% -> USD {capital_1_anio:,.0f} proyectado a 1 año (real a 304d: USD {valores[-1]:,.0f})')
    # tramo proyectado (punteado) desde el ultimo dato real hasta el dia 365
    x_proy = np.linspace(dias_reales, 365, 30)
    # interpolacion exponencial simple manteniendo la MISMA tasa diaria compuesta observada
    tasa_diaria = retorno_real ** (1/dias_reales)
    y_proy = valores[-1] * (tasa_diaria ** (x_proy - dias_reales))
    ax.plot(x_proy, y_proy, color=color, linewidth=2.2, linestyle='--', alpha=0.8)

    resumen.append({'riesgo_%': pct, 'capital_dia_304_real': round(valores[-1], 2),
                     'retorno_304d_%': round((retorno_real-1)*100, 1),
                     'capital_proyectado_365d': round(capital_1_anio, 2),
                     'retorno_anualizado_%': round((retorno_anualizado-1)*100, 1)})

ax.axvline(dias_reales, color='black', linestyle=':', linewidth=1.2, label=f'Hoy (día {dias_reales} real, resto proyectado)')
ax.axhline(CAPITAL_INICIAL, color='gray', linestyle=':', linewidth=0.8)
ax.set_title('5 escenarios de riesgo, mismo punto de partida (USD 10.000) -- proyectados a 1 año completo\n'
              'Línea sólida = datos reales (304 días) | Línea punteada = proyección al mismo ritmo (hasta 365 días)',
              fontsize=13, fontweight='bold')
ax.set_xlabel('Días de calendario desde el inicio (27/10/2025)')
ax.set_ylabel('Capital (USD)')
ax.legend(loc='upper left', fontsize=9.5)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT, bbox_inches='tight')

tabla = pd.DataFrame(resumen)
print("=" * 100)
print(f"PANORAMA A 1 AÑO -- proyectando el ritmo real observado en {dias_reales} días a 365 días completos")
print("=" * 100)
print(tabla.to_string(index=False))
tabla.to_csv('/Users/diegorodriguez/Desktop/Jarvis/jarvis/trading_algoritmico/fabian_manual_strategy/panorama_1_anio_resumen.csv', index=False)
print(f"\nGrafico guardado en {OUT}")
