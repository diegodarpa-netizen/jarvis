# Código propio de Fabian — indicador XAU

Acá va el código del indicador que Fabian armó por su cuenta (Pine Script,
Python, lo que sea), para compararlo directamente contra el motor ya
calibrado en `../seguimiento_vela_por_vela/` y contra `../fabian_consolidado_limpio.csv`
(las 191 operaciones reales que ya validamos).

## Cómo trabajar acá

1. Pegá tu código tal cual lo tenés hoy (no hace falta que esté terminado).
2. Contame qué reglas del Plan Técnico/Operativo ya implementaste y cuáles
   no, así sé desde dónde arrancar la comparación.
3. Vamos a correrlo (vela por vela, mismo método que usamos con el motor
   Python) contra el mismo dataset histórico y ver dónde coincide/difiere
   con lo que Fabian tomó en la realidad y con el motor ya calibrado.

## Antes de tocar nada

Leer, en este orden:
1. `../../fabian_manual_strategy/REGISTRO_COMPLETO_CALIBRACION_28_30AGO2026.md`
   — toda la historia de la calibración hasta acá.
2. `../seguimiento_vela_por_vela/README.md` — bitácora día por día.
3. `../PLAN_HACIA_PRODUCCION.md` — en qué fase estamos.
4. `../base_conocimiento_NO_TOCAR/` — PDFs base (Plan Técnico, Plan
   Operativo) y las respuestas textuales de Fabian.

**No se pisa nada de lo que ya está calibrado en el resto de la carpeta**
— esta subcarpeta es un espacio nuevo para el código de Fabian, en
paralelo.
