# Escalón descendente (backward-facing step): Proyecto final de Mecánica de Fluidos

Simulación 2D del flujo laminar incompresible sobre un escalón descendente (el canal se ensancha al doble, Re = 100–600).
Se resuelven las ecuaciones de Navier–Stokes con el método de proyección en 3 pasos (velocidad de prueba → presión → corrección).

| Entregable | Archivo |
|---|---|
| Código (Ejecutar todo, ~3.5 min) | `escalon_descendente.ipynb` |
| Reporte escrito (PDF) | `reporte/reporte.pdf` (fuente: `reporte/reporte.md`) |
| Diapositivas (10) | `presentacion/presentacion.pptx` (notas del orador con el reparto sugerido) |
| Guía para estudiar el código línea por línea | `guia/guia_explicacion.pdf` |
| Video | https://www.youtube.com/shorts/1UjPvbtYBLU |
| Figuras | `figures/` (las genera el notebook) |

## Ejecutar

```bash
pip install -r requirements.txt
jupyter notebook escalon_descendente.ipynb     # Kernel → Restart & Run All
```

Para la demo en vivo, cambiar `RE` (y si se quiere `NY`, `L`) en el bloque 0 del notebook.

## Resultados principales

| Re | 100 | 200 | 300 | 400 | 600 |
|---|---|---|---|---|---|
| x_r/S (este trabajo, 20 celdas/H) | 3.01 | 4.90 | 6.52 | 7.90 | 9.75 |
| x_r/S (literatura 2D) | 3.00 | 4.95 | 6.75 | 8.10 | 10.05 |

Regenerar los documentos: `python reporte/build_pdf.py`, `python guia/build_pdf.py`, `python presentacion/build_slides.py`.
