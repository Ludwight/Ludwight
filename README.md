# Escalón descendente (backward-facing step): Proyecto final de Mecánica de Fluidos

Simulación 2D del flujo laminar incompresible sobre un escalón descendente (el canal se ensancha al doble, Re = 100–600).
Se resuelven las ecuaciones de Navier–Stokes con el método de proyección en 3 pasos (velocidad de prueba → presión → corrección),
convección por promedio (segundo orden) y Adams–Bashforth en el tiempo. El arranque del flujo se filma con tinta virtual.

| Entregable | Archivo |
|---|---|
| Código (Ejecutar todo: ~13 min con videos, ~5 min con `HACER_VIDEOS = False`) | `escalon_descendente.ipynb` |
| Reporte escrito (PDF) | `reporte/reporte.pdf` (fuente: `reporte/reporte.md`) |
| Diapositivas (12, dos con video) | `presentacion/presentacion.pptx` (notas del orador con el reparto sugerido) |
| Guía para estudiar el código línea por línea | `guia/guia_explicacion.pdf` |
| Videos de la simulación (1080p) | `figures/arranque_re200.mp4`, `figures/comparacion_re.mp4` |
| Video para YouTube (2:39, con voz y subtítulos; versión sin voz y guion con tiempos) | `video/video_proyecto.mp4`, `video/video_proyecto_sin_voz.mp4`, `video/guion_video.md` |
| Enlace YouTube | https://youtu.be/kBtmlx2zd3A |
| Figuras | `figures/` (las genera el notebook) |

## Ejecutar

```bash
pip install -r requirements.txt
jupyter notebook escalon_descendente.ipynb     # Kernel → Restart & Run All
```

Para la demo en vivo, cambiar `RE` (y si se quiere `NY`, `L`) en el bloque 0 del notebook, con `HACER_VIDEOS = False`.

## Resultados principales

| Re | 100 | 200 | 300 | 400 | 500 | 600 |
|---|---|---|---|---|---|---|
| x_r/S (este trabajo, 20 celdas/H) | 2.84 | 4.91 | 6.73 | 8.26 | 9.40 | 10.06 |
| x_r/S (literatura 2D) | 3.00 | 4.95 | 6.75 | 8.10 | 9.30 | 10.05 |

Error de malla con 20 celdas/H: < 1 % (NY = 10 / 20 / 40 → 4.75 / 4.91 / 4.95 a Re = 200).

Regenerar los documentos: `python reporte/build_pdf.py`, `python guia/build_pdf.py`, `python presentacion/build_slides.py`.
