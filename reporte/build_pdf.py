"""Compila reporte.tex -> reporte.pdf.

1. Extrae del notebook final (../escalon_descendente.ipynb) el código de las funciones citadas en el anexo y lo
   escribe en codigo/<funcion>.py, de modo que el reporte siempre muestra el código que realmente se ejecuta.
2. Corre pdflatex dos veces (referencias cruzadas e índice).
Uso: python reporte/build_pdf.py   (requiere TeX Live con babel-spanish, listings, booktabs, siunitx)."""
import ast
import json
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NOTEBOOK = AQUI.parent / "escalon_descendente.ipynb"
FUNCIONES = ["crear_malla", "perfil_entrada", "matriz_presion", "fronteras", "aceleracion_u", "simular",
             "reacoplamiento", "vorticidad"]

nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
fuente = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
definiciones = {n.name: ast.get_source_segment(fuente, n) for n in ast.parse(fuente).body
                if isinstance(n, ast.FunctionDef)}
salida = AQUI / "codigo"
salida.mkdir(exist_ok=True)
for nombre in FUNCIONES:
    (salida / f"{nombre}.py").write_text(definiciones[nombre] + "\n", encoding="utf-8")

for _ in range(2):
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "reporte.tex"],
                       cwd=AQUI, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:])
        raise SystemExit("pdflatex falló")
for ext in ("aux", "log", "out", "toc"):
    (AQUI / f"reporte.{ext}").unlink(missing_ok=True)
print("reporte.pdf listo")
