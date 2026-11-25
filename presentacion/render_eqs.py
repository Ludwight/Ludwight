"""Renderiza las ecuaciones de la presentación a PNG (mathtext de matplotlib, fondo transparente).
Uso: python render_eqs.py   (escribe presentacion/eq/*.png; la carpeta está en .gitignore)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EQ = Path(__file__).resolve().parent / "eq"
EQ.mkdir(exist_ok=True)
COLOR = "#0B1F3A"

ECUACIONES = {
    "continuidad": r"$\nabla\cdot\mathbf{u}=0$",
    "momento": r"$\frac{\partial\mathbf{u}}{\partial t}+(\mathbf{u}\cdot\nabla)\mathbf{u}=-\nabla p+\frac{1}{Re}\nabla^2\mathbf{u}$",
    "adimensional": r"$Re=\frac{UH}{\nu},\quad ER=\frac{H}{h}=2,\quad S=\frac{H}{2}$",
    "poiseuille": r"$u=6U\eta(1-\eta),\quad \eta=\dfrac{y-S}{h}$",
    "paso1": r"$\mathbf{u}^*=\mathbf{u}^n+\Delta t\left[\frac{3}{2}A^n-\frac{1}{2}A^{n-1}\right]$",
    "def_A": r"$A=\frac{1}{Re}\nabla^2\mathbf{u}-\nabla\cdot(\mathbf{u}\mathbf{u})$",
    "paso2": r"$\nabla^2 p^{n+1}=\dfrac{\nabla\cdot\mathbf{u}^*}{\Delta t}$",
    "paso3": r"$\mathbf{u}^{n+1}=\mathbf{u}^*-\Delta t\,\nabla p^{n+1}$",
    "cfl": r"$\Delta t\leq\dfrac{\Delta x}{|u|_{max}}$",
}

for nombre, latex in ECUACIONES.items():
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, latex, fontsize=40, color=COLOR)
    fig.savefig(EQ / f"{nombre}.png", dpi=300, bbox_inches="tight", pad_inches=0.04, transparent=True)
    plt.close(fig)
print("ecuaciones:", len(ECUACIONES), "->", EQ)
