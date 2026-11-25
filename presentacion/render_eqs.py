"""Compila cada ecuación de la presentación con LaTeX (pdflatex, fuentes Computer Modern) y la guarda como PNG
transparente en presentacion/eq/. Requiere TeX Live con standalone y amsmath (paquetes texlive-latex-extra).
Uso: python render_eqs.py"""
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

EQ = Path(__file__).resolve().parent / "eq"
EQ.mkdir(exist_ok=True)
COLOR_RGB = (11, 31, 58)                     # azul marino de la paleta, 0B1F3A

ECUACIONES = {
    # ---- ecuaciones de gobierno ----
    "continuidad": r"\nabla\cdot\mathbf{u}=0",
    "mom_x": r"\frac{\partial u}{\partial t}+\frac{\partial (u^2)}{\partial x}+\frac{\partial (uv)}{\partial y}"
             r"=-\frac{\partial p}{\partial x}+\frac{1}{Re}\left(\frac{\partial^2 u}{\partial x^2}+\frac{\partial^2 u}{\partial y^2}\right)",
    "mom_y": r"\frac{\partial v}{\partial t}+\frac{\partial (uv)}{\partial x}+\frac{\partial (v^2)}{\partial y}"
             r"=-\frac{\partial p}{\partial y}+\frac{1}{Re}\left(\frac{\partial^2 v}{\partial x^2}+\frac{\partial^2 v}{\partial y^2}\right)",
    "adim": r"Re=\frac{UH}{\nu}=\frac{1}{\nu}, \qquad x^*=\frac{x}{H},\quad u^*=\frac{u}{U},\quad p^*=\frac{p}{\rho U^2}",
    "geom": r"h=\frac{H}{2},\qquad S=\frac{H}{2},\qquad ER=\frac{H}{h}=2",
    # ---- condiciones iniciales y de frontera ----
    "ci": r"\mathbf{u}(x,y,0)=\mathbf{0}",
    "entrada": r"u(-2H,y)=6U\,\eta\,(1-\eta),\quad \eta=\frac{y-S}{h},\qquad v(-2H,y)=0",
    "noslip": r"\mathbf{u}=\mathbf{0}\quad\text{en } y=0,\; y=H,\; y=S\ (x<0),\; x=0\ (y<S)",
    "salida": r"\frac{\partial u}{\partial x}=\frac{\partial v}{\partial x}=0,\qquad p(L,y)=0",
    "neumann": r"\frac{\partial p}{\partial n}=0\quad\text{en paredes y entrada}",
    # ---- método de proyección ----
    "paso1": r"\mathbf{u}^*=\mathbf{u}^n+\Delta t\left[\tfrac{3}{2}\mathbf{A}^{n}-\tfrac{1}{2}\mathbf{A}^{n-1}\right]",
    "def_A": r"\mathbf{A}=\frac{1}{Re}\nabla^2\mathbf{u}-\nabla\cdot(\mathbf{u}\mathbf{u})",
    "paso2": r"\nabla^2 p^{n+1}=\frac{1}{\Delta t}\,\nabla\cdot\mathbf{u}^*",
    "paso3": r"\mathbf{u}^{n+1}=\mathbf{u}^*-\Delta t\,\nabla p^{n+1}",
    "deriv": r"\nabla\cdot\mathbf{u}^{n+1}=\nabla\cdot\mathbf{u}^*-\Delta t\,\nabla^2 p^{n+1}=0",
    # ---- discretización espacial ----
    "lap": r"\nabla^2 u\approx\frac{u_E+u_W+u_N+u_S-4u_P}{\Delta x^2}",
    "conv": r"\left.\frac{\partial (u^2)}{\partial x}\right|_{i}\approx\frac{\bar u_e^{\,2}-\bar u_w^{\,2}}{\Delta x},"
            r"\qquad \bar u_e=\tfrac{1}{2}(u_i+u_{i+1})",
    "grad": r"\left.\frac{\partial p}{\partial x}\right|_{\text{cara}}\approx\frac{p_{i}-p_{i-1}}{\Delta x}",
    "poisson": r"\frac{p_E+p_W+p_N+p_S-4p_P}{\Delta x^2}=b_P,\qquad b_P=\frac{1}{\Delta t}\,(\nabla\cdot\mathbf{u}^*)_P",
    "fantasma": r"p_{\text{sal}}=-p_P\;\Rightarrow\;\text{coef. de }p_P=-2",
    # ---- estabilidad y convergencia ----
    "cfl": r"\Delta t\leq\frac{\Delta x}{|u|_{\max}}",
    "difusion": r"\Delta t\leq\frac{Re}{2}\left(\frac{1}{\Delta x^2}+\frac{1}{\Delta y^2}\right)^{-1}",
    "criterio": r"\frac{\max|\mathbf{u}^{n+1}-\mathbf{u}^{n}|}{\Delta t}<10^{-4}",
    "orden": r"p=\log_2\frac{x_{10}-x_{20}}{x_{20}-x_{40}}\approx 2.3,\qquad x_\infty\approx x_{40}+\frac{x_{40}-x_{20}}{2^{p}-1}",
    "tauw": r"\tau_w=\mu\left.\frac{\partial u}{\partial y}\right|_{y=0}=0\quad\text{en el reacoplamiento}",
    "vort": r"\omega=\frac{\partial v}{\partial x}-\frac{\partial u}{\partial y}",
}

PREAMBULO = r"""\documentclass[varwidth=true,border=2pt]{standalone}
\usepackage{amsmath,amssymb,bm}
\usepackage[T1]{fontenc}
\usepackage{xcolor}
\begin{document}
\color[RGB]{11,31,58}
\[ %s \]
\end{document}
"""


def compilar(nombre, tex):
    with tempfile.TemporaryDirectory() as tmp:
        fuente = Path(tmp) / f"{nombre}.tex"
        fuente.write_text(PREAMBULO % tex, encoding="utf-8")
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", fuente.name],
                       cwd=tmp, check=True, capture_output=True)
        subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile", f"{nombre}.pdf", nombre],
                       cwd=tmp, check=True, capture_output=True)
        img = Image.open(Path(tmp) / f"{nombre}.png").convert("RGB")
        a = np.asarray(img).astype(np.float32)
        alfa = 255 - a.min(axis=2)                     # cuanto más oscuro el píxel, más opaco
        rgba = np.zeros((*alfa.shape, 4), dtype=np.uint8)
        rgba[..., :3] = COLOR_RGB
        rgba[..., 3] = np.clip(alfa, 0, 255).astype(np.uint8)
        out = Image.fromarray(rgba, "RGBA")
        out = out.crop(out.getbbox())
        out.save(EQ / f"{nombre}.png")


for nombre, tex in ECUACIONES.items():
    compilar(nombre, tex)
print("ecuaciones LaTeX:", len(ECUACIONES), "->", EQ)
