# Escalón descendente (backward-facing step) — Proyecto final de Mecánica de Fluidos

Simulación 2D del flujo laminar incompresible sobre un escalón descendente (relación de expansión 2, Re = 100–800)
con un solver propio en Python: malla escalonada MAC, método de proyección de Chorin y Poisson por LU dispersa.

| Entregable | Archivo |
|---|---|
| Código (Ejecutar todo, ~5 min) | `BFS_escalon_descendente.ipynb` |
| Reporte escrito (PDF) | `reporte/reporte.pdf` (fuente: `reporte/reporte.md`) |
| Diapositivas (10) | `presentacion/presentacion.pptx` (notas del orador con el reparto sugerido) |
| Video | https://www.youtube.com/shorts/1UjPvbtYBLU |
| Figuras | `figures/` (las genera el notebook) |

## Ejecutar

```bash
pip install -r requirements.txt
jupyter notebook BFS_escalon_descendente.ipynb     # Kernel → Restart & Run All
```

Los parámetros de la demo en vivo (`RE_BASE`, `NY_BASE`, `GAMMA`, `DT_BASE`) están en el bloque 0 del notebook.

## Estructura

- `src/bfs_solver.py`: solver (malla, Poisson, CF, momento, proyección, post-proceso).
- `src/plots.py`: gráficas.
- `build_notebook.py`: arma el notebook autocontenido a partir de `src/` (`python build_notebook.py`).
- `reporte/build_pdf.py`: Markdown → PDF (pandoc + Chromium).
- `presentacion/build_slides.py`: genera el .pptx con las figuras.

## Resultados principales

| Re | 100 | 200 | 300 | 400 | 600 | 800 |
|---|---|---|---|---|---|---|
| x_r/S (este trabajo, 20 celdas/H) | 3.01 | 4.90 | 6.52 | 7.90 | 9.75 | 10.45 |
| x_r/S (literatura 2D) | 3.00 | 4.95 | 6.75 | 8.10 | 10.05 | 11.55 / 12.2 (Gartling) |
