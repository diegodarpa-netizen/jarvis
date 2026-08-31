"""
Trata cada franja (tramo de días consecutivos surfeando el mismo lado de la
EMA9, cortado por el amarillo) como UNA decisión — no día a día. A pedido
de Diego (14/08/2026): sumar verdes y rojos como si fuera una toma de
decisión, amarillo afuera (no se opera ahí), y medir el % de acierto.

Acierto: en una franja verde, si el precio cerró más alto al final de la
franja que al principio. En una franja roja, si cerró más bajo (estamos
vendidos, ganamos si baja).

Uso:
    python3 analisis_franjas_verde_rojo.py --desde 2025-12-17 --hasta 2026-03-05
    python3 analisis_franjas_verde_rojo.py --desde 2026-01-01
    python3 analisis_franjas_verde_rojo.py --desde 2021-01-01   # varios años
    python3 analisis_franjas_verde_rojo.py --desde 2026-01-01 --umbral-atr 0.5
        # ^ filtro nuevo (14/08/2026, a pedido de Diego): dentro de cada
        # franja, no entrar apenas cambia de color -- esperar a que la
        # distancia a la EMA9 (en unidades de ATR14) supere el umbral. Si la
        # franja nunca llega a esa distancia, se descarta (no hubo "decisión"
        # real, quedó pegada a la EMA todo el tiempo). Con --umbral-atr 0
        # (default) el comportamiento es idéntico al de antes -- entra el
        # primer día del color, sin exigir distancia mínima.
"""
import argparse

import pandas as pd

from medir_distancia_ema9 import calcular_distancia, DATA_PATH


def identificar_franjas(ventana: pd.DataFrame, umbral_atr: float = 0.0) -> pd.DataFrame:
    franjas = []
    color_actual = None
    inicio_idx = None

    for i in range(len(ventana)):
        estado = ventana["estado"].iloc[i]
        color = "verde" if estado == "surfea_arriba" else ("rojo" if estado == "surfea_abajo" else "amarillo")
        if color != color_actual:
            if color_actual in ("verde", "rojo"):
                franjas.append((color_actual, inicio_idx, i - 1))
            if color in ("verde", "rojo"):
                inicio_idx = i
            color_actual = color

    if color_actual in ("verde", "rojo"):
        franjas.append((color_actual, inicio_idx, len(ventana) - 1))

    filas = []
    for color, ini, fin in franjas:
        # Filtro de distancia (umbral_atr > 0): no entrar apenas arranca el
        # color -- buscar dentro de la franja el primer día donde la
        # distancia a la EMA9 (en ATR) ya superó el umbral, y entrar ahí. Si
        # la franja entera nunca llega a esa distancia, se descarta (no fue
        # una "franja" con convicción, quedó pegada a la EMA).
        ini_real = None
        for i in range(ini, fin + 1):
            if abs(ventana["dist_atr"].iloc[i]) >= umbral_atr:
                ini_real = i
                break
        if ini_real is None:
            continue
        arranco_color = ventana.index[ini].date()
        ini = ini_real

        # Entrada = cierre del día en que se confirma la distancia (o el
        # primer día del color, si no hay filtro) -- se sabe en ese mismo
        # cierre, sin mirar al futuro.
        #
        # Salida = cierre del día SIGUIENTE al último día del color (fin+1),
        # no el cierre del propio último día -- porque recién en ese día
        # siguiente uno "se entera" de que la franja terminó (el último día
        # todavía cerró siendo del mismo color, no había forma de saber en
        # tiempo real que sería el último). Si la franja llega hasta el
        # final de los datos, no hay día siguiente -- se usa el cierre del
        # último día disponible (posición que queda abierta).
        precio_entrada = ventana["close"].iloc[ini]
        if fin + 1 < len(ventana):
            precio_salida = ventana["close"].iloc[fin + 1]
            abierta = False
        else:
            precio_salida = ventana["close"].iloc[fin]
            abierta = True
        dias_expuesto = (fin + 1 - ini + 1) if not abierta else (fin - ini + 1)
        ret_pct = (precio_salida / precio_entrada - 1) * 100
        if color == "rojo":
            ret_pct = -ret_pct
        if ret_pct > 0:
            resultado = "SI"
        elif ret_pct < 0:
            resultado = "NO"
        else:
            resultado = "NEUTRO"
        idx_salida = fin + 1 if not abierta else fin
        filas.append({
            "color": color,
            "arranco_color": arranco_color,
            "entra": ventana.index[ini].date(), "sale": ventana.index[idx_salida].date(),
            "dias": dias_expuesto,
            "precio_entrada": round(precio_entrada, 2), "precio_salida": round(precio_salida, 2),
            "retorno_%": round(ret_pct, 2),
            "acierto": resultado,
            "abierta": abierta,
        })
    return pd.DataFrame(filas)


def reportar(tabla: pd.DataFrame, etiqueta: str):
    print("=" * 70)
    print(etiqueta)
    print("=" * 70)
    if tabla.empty:
        print("Sin franjas en esta ventana.")
        return
    pd.set_option("display.width", 140)
    print(tabla.to_string(index=False))
    total = len(tabla)
    aciertos = (tabla["acierto"] == "SI").sum()
    fallos = (tabla["acierto"] == "NO").sum()
    neutros = (tabla["acierto"] == "NEUTRO").sum()
    verdes = (tabla["color"] == "verde").sum()
    rojas = (tabla["color"] == "rojo").sum()
    print(f"\nTotal de franjas (decisiones): {total} | Verdes: {verdes} | Rojas: {rojas}")
    print(f"Aciertos: {aciertos} | Fallos: {fallos} | Neutros (1 día, sin exposición real): {neutros}")
    print(f"% de acierto (sobre las que tuvieron resultado, sin contar neutros): {aciertos/(aciertos+fallos)*100:.1f}%")
    print(f"Retorno acumulado (suma simple de %): {tabla['retorno_%'].sum():.2f}%")
    print(f"Franja más larga: {tabla['dias'].max()} días | Franja típica (mediana): {tabla['dias'].median():.0f} días")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--desde", required=True)
    parser.add_argument("--hasta", default=None)
    parser.add_argument("--umbral-atr", type=float, default=0.0,
                         help="Distancia mínima a la EMA9 (en ATR14) para recién ahí entrar dentro de la franja. 0 = sin filtro (default).")
    args = parser.parse_args()

    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    df.columns = [c.lower() for c in df.columns]
    df = df.sort_index()
    r = calcular_distancia(df)

    hasta = args.hasta or str(r.index[-1].date())
    ventana = r[(r.index >= args.desde) & (r.index <= hasta)].copy()
    tabla = identificar_franjas(ventana, umbral_atr=args.umbral_atr)
    etiqueta = f"Franjas verde/rojo — {args.desde} a {hasta}"
    if args.umbral_atr > 0:
        etiqueta += f" (umbral: {args.umbral_atr} ATR)"
    reportar(tabla, etiqueta)


if __name__ == "__main__":
    main()
