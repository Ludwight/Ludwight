"""Genera presentacion.pptx (10 diapositivas) con las figuras de ../figures.
Uso: python build_slides.py   (requiere python-pptx y matplotlib; correr antes el notebook)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

HERE = Path(__file__).resolve().parent
FIG = HERE.parent / "figures"
EQ = HERE / "eq"; EQ.mkdir(exist_ok=True)
NAVY = RGBColor(0x1F, 0x38, 0x64)
GREY = RGBColor(0x40, 0x40, 0x40)


def eq_png(name, latex_lines, fs=22):
    """Renderiza cada ecuación con mathtext de matplotlib (una imagen por línea)."""
    paths = []
    for k, line in enumerate(latex_lines):
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.text(0, 0, line, fontsize=fs)
        out = EQ / f"{name}_{k}.png"
        fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.06, transparent=True)
        plt.close(fig)
        paths.append(out)
    return paths


def eq_block(s, paths, x, y, h_line=0.75, gap=0.35):
    """Apila las ecuaciones verticalmente (alto fijo por línea)."""
    for pth in paths:
        pic(s, pth, x, y, h=h_line)
        y += h_line + gap


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def slide(title, notes=""):
    s = prs.slides.add_slide(BLANK)
    bar = s.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(0.95))
    bar.fill.solid(); bar.fill.fore_color.rgb = NAVY; bar.line.fill.background()
    tf = bar.text_frame; tf.text = title
    p = tf.paragraphs[0]; p.font.size = Pt(28); p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255); p.alignment = PP_ALIGN.LEFT
    tf.margin_left = Inches(0.4)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def bullets(s, items, x, y, w, h, size=20):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    for k, it in enumerate(items):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        sub = it.startswith("  ")
        p.text = ("– " if sub else "• ") + it.strip()
        p.font.size = Pt(size - 3 if sub else size); p.font.color.rgb = GREY
        p.level = 1 if sub else 0
        p.space_after = Pt(6)
    return tb


def pic(s, path, x, y, w=None, h=None):
    kw = {}
    if w: kw["width"] = Inches(w)
    if h: kw["height"] = Inches(h)
    return s.shapes.add_picture(str(path), Inches(x), Inches(y), **kw)


# 1. Portada -------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
tb = s.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(4))
tf = tb.text_frame; tf.word_wrap = True
for k, (txt, size, bold) in enumerate([
        ("Flujo laminar sobre un escalón descendente", 40, True),
        ("Navier–Stokes 2D · método de proyección en malla MAC · análisis paramétrico", 22, False),
        ("", 12, False),
        ("Mecánica de Fluidos · Proyecto final · Prof. Anuar Sánchez", 20, False),
        ("[Integrante 1] · [Integrante 2] · [Integrante 3] · [Integrante 4]", 20, False)]):
    p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
    p.text = txt; p.font.size = Pt(size); p.font.bold = bold; p.font.color.rgb = RGBColor(255, 255, 255)
pic(s, FIG / "campos_base.png", 7.2, 4.9, h=2.4).crop_bottom = 0.66
s.notes_slide.notes_text_frame.text = "Presentación del equipo (30 s). La sección técnica empieza en la diapositiva 2."

# 2. Fenómeno ------------------------------------------------------------------
s = slide("¿Qué pasa en un escalón descendente?",
          "Integrante 1. Explicar separación por gradiente de presión adverso, capa de corte, burbuja, "
          "reacoplamiento (tau_w = 0) y burbuja secundaria para Re > 400.")
bullets(s, ["La capa límite no puede seguir la esquina → se separa en la arista",
            "Capa de corte libre con vorticidad intensa",
            "Burbuja de recirculación (u < 0) bajo la capa de corte",
            "Reacoplamiento en x_r, donde τ_w = 0",
            "Re ≳ 400: burbuja secundaria en la pared superior",
            "Caso de prueba clásico de CFD (Armaly 1983, Gartling 1990)"], 0.5, 1.2, 5.6, 5.5)
pic(s, FIG / "campos_base.png", 6.2, 1.2, w=7.0)

# 3. Ecuaciones ---------------------------------------------------------------
s = slide("Modelo físico: ecuaciones y supuestos",
          "Integrante 1/2. Adimensionalización con U (velocidad media de entrada) y H. "
          "Re basado en el diámetro hidráulico de entrada 2h = H. Variar nu = variar Re.")
eq_block(s, eq_png("ns", [r"$\nabla\cdot\mathbf{u}=0$",
                     r"$\frac{\partial\mathbf{u}}{\partial t}+(\mathbf{u}\cdot\nabla)\mathbf{u}=-\nabla p+\frac{1}{Re}\nabla^2\mathbf{u}$",
                     r"$Re=\frac{U\,H}{\nu},\quad ER=\frac{H}{h}=2,\quad S=\frac{H}{2}$"], fs=26), 0.6, 1.5, h_line=0.75, gap=0.6)
bullets(s, ["2D, incompresible, newtoniano, isotérmico",
            "Laminar: 100 ≤ Re ≤ 800",
            "Sin gravedad (no cambia la cinemática)",
            "Adimensional: U = H = 1 → ν = 1/Re",
            "Variar la viscosidad ≡ variar Re"], 8.4, 1.4, 4.7, 5)

# 4. CI/CF --------------------------------------------------------------------
s = slide("Condiciones iniciales y de frontera",
          "Integrante 2. La entrada va en el plano del escalón, igual que el benchmark de Gartling. "
          "p = 0 en la salida hace no singular la matriz de Poisson.")
rows = [("Frontera", "Velocidad", "Presión"),
        ("Entrada x = 0, S < y < H", "Poiseuille u = 6Uη(1−η), v = 0", "∂p/∂n = 0"),
        ("Cara del escalón", "u = v = 0 (no deslizamiento)", "∂p/∂n = 0"),
        ("Paredes y = 0, H", "u = v = 0 (no deslizamiento)", "∂p/∂n = 0"),
        ("Salida x = L", "∂u/∂x = ∂v/∂x = 0", "p = 0"),
        ("CI (t = 0)", "fluido en reposo u = v = 0", "—")]
tbl = s.shapes.add_table(len(rows), 3, Inches(0.7), Inches(1.5), Inches(11.9), Inches(4.2)).table
for i, r in enumerate(rows):
    for j, c in enumerate(r):
        cell = tbl.cell(i, j); cell.text = c
        cell.text_frame.paragraphs[0].font.size = Pt(19)
        cell.text_frame.paragraphs[0].font.bold = (i == 0)
tbl.columns[0].width = Inches(3.6); tbl.columns[1].width = Inches(5.6); tbl.columns[2].width = Inches(2.7)

# 5. Método numérico ----------------------------------------------------------
s = slide("Método numérico: proyección de Chorin en malla MAC",
          "Integrante 2/3. MAC evita el tablero de ajedrez. La LU se factoriza una vez. "
          "Gamma controla la difusión numérica. Estabilidad: CFL y Fourier.")
eq_block(s, eq_png("proj", [r"$1)\ \mathbf{u}^*=\mathbf{u}^n+\Delta t\left[\frac{1}{Re}\nabla^2\mathbf{u}^n-\nabla\cdot(\mathbf{u}\mathbf{u})^n\right]$",
                       r"$2)\ \nabla^2 p^{n+1}=\frac{\nabla\cdot\mathbf{u}^*}{\Delta t}$",
                       r"$3)\ \mathbf{u}^{n+1}=\mathbf{u}^*-\Delta t\,\nabla p^{n+1}$",
                       r"$\Delta t\leq\min\left(\frac{\Delta x}{|u|_{max}},\ \frac{Re}{2}\left(\frac{1}{\Delta x^2}+\frac{1}{\Delta y^2}\right)^{-1}\right)$"],
            fs=24), 0.4, 1.4, h_line=0.7, gap=0.45)
bullets(s, ["Volúmenes finitos, malla escalonada (MAC)",
            "Difusión: centrada 2.º orden",
            "Convección: híbrido γ",
            "  γ = 0 centrado · γ = 1 upwind",
            "Poisson: LU dispersa (una vez)",
            "∇·u = 10⁻¹⁵ (masa exacta)",
            "Paro: max|Δu|/Δt < 10⁻⁵"], 8.7, 1.3, 4.5, 5.5, size=19)

# 6. Caso base ----------------------------------------------------------------
s = slide("Caso base Re = 200: x_r/S = 4.90",
          "Integrante 3. Leer vorticidad (capa de corte) y presión (recuperación aguas abajo = gradiente adverso). "
          "Aquí va la DEMO EN VIVO: cambiar RE_BASE en el bloque 0 y ejecutar.")
pic(s, FIG / "campos_base.png", 0.4, 1.1, h=4.6)
pic(s, FIG / "perfiles_base.png", 0.4, 5.75, h=1.65)
bullets(s, ["6000 celdas, 2916 pasos, ~4 s", "p sube tras el escalón: gradiente adverso",
            "u_max: 1.5 → 0.75 (masa)"], 9.6, 5.6, 3.6, 1.8, size=15)

# 7. Reynolds -----------------------------------------------------------------
s = slide("Efecto de la viscosidad (Re)",
          "Integrante 3/4. x_r crece casi lineal hasta Re 400; luego más lento porque la burbuja superior "
          "empuja el chorro hacia abajo.")
pic(s, FIG / "re_streamfunction.png", 0.3, 1.2, w=8.0)
pic(s, FIG / "re_tau_w.png", 8.5, 1.3, w=4.7)
bullets(s, ["Re 100 → 600: x_r/S 3.0 → 9.8", "Burbuja superior desde Re ≈ 400",
            "τ_w = 0 marca el reacoplamiento"], 8.5, 3.4, 4.7, 3, size=17)

# 8. Malla y dt ---------------------------------------------------------------
s = slide("Malla y paso de tiempo",
          "Integrante 4. Orden observado ~1 por la parte upwind. dt no cambia el resultado estacionario "
          "si es estable; dt = 1.35 dt_CFL diverge en 22 pasos.")
pic(s, FIG / "malla.png", 0.3, 1.15, w=7.2)
pic(s, FIG / "dt.png", 7.6, 1.15, w=5.5)
bullets(s, ["ny = 10/20/40 → x_r/S = 4.47/4.90/5.11", "Richardson: 5.32, p = 1.0, GCI = 5 %",
            "Δt ≤ 1.08 Δt_CFL: mismo x_r = 4.899", "Δt = 1.35 Δt_CFL: diverge"], 0.5, 4.2, 12, 3, size=19)

# 9. Esquema y validación ------------------------------------------------------
s = slide("Difusión numérica y validación",
          "Integrante 4. nu_num ~ gamma |u| dx / 2 = 0.025 > nu = 0.005. "
          "Buen acuerdo hasta Re 600; en Re 800 la malla gruesa acorta la burbuja (10.45 vs 12.2 Gartling).")
pic(s, FIG / "gamma.png", 0.3, 1.15, w=6.4)
pic(s, FIG / "validacion.png", 6.9, 1.15, w=6.2)
bullets(s, ["γ = 0 / 0.5 / 1 → x_r/S = 5.33 / 4.90 / 4.50",
            "Upwind: ν_num ≈ 5 ν → burbuja 16 % más corta",
            "Error vs literatura < 3.5 % (Re ≤ 600); −14 % vs Gartling en Re = 800"], 0.5, 4.9, 12.3, 2.5, size=19)

# 10. Conclusiones ------------------------------------------------------------
s = slide("Conclusiones",
          "Cierre (1 min) y preguntas. Tener el notebook abierto para la demo.")
bullets(s, ["Solver propio (MAC + proyección) que conserva la masa a precisión de máquina",
            "Reproduce separación, reacoplamiento y burbuja secundaria",
            "Menor viscosidad → burbuja más larga (x_r ∝ Re hasta ~400)",
            "Δt sólo afecta la estabilidad, no el estado estacionario",
            "La difusión numérica (upwind, malla gruesa) acorta la burbuja",
            "Siguiente paso: esquema de mayor orden (QUICK/TVD) + Adams–Bashforth"], 0.6, 1.3, 12, 5.5, size=22)

out = HERE / "presentacion.pptx"
prs.save(out)
print("escrito", out)
