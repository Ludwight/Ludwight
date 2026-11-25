"""Genera presentacion.pptx (12 diapositivas, 2 con video) con las figuras de ../figures.
Uso: python build_slides.py   (requiere python-pptx, matplotlib e imageio-ffmpeg; correr antes el notebook)."""
import subprocess
from pathlib import Path
import imageio_ffmpeg
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


def video(s, path, x, y, w, t_poster):
    """Incrusta un MP4 (se reproduce en PowerPoint) con un cuadro del video como portada."""
    poster = EQ / (path.stem + "_portada.png")
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-ss", str(t_poster), "-i", str(path),
                    "-frames:v", "1", str(poster)], check=True)
    h = w * 9 / 16
    return s.shapes.add_movie(str(path), Inches(x), Inches(y), Inches(w), Inches(h),
                              poster_frame_image=str(poster), mime_type="video/mp4")


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
        ("Navier–Stokes 2D · método de proyección en 3 pasos · tinta virtual · análisis paramétrico", 22, False),
        ("", 12, False),
        ("Mecánica de Fluidos · Proyecto final · Prof. Anuar Sánchez", 20, False),
        ("Luis Antonio Pérez Hernández · Marco Antonio Navarrete Baños", 20, False)]):
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
            "Laminar: 100 ≤ Re ≤ 600",
            "Sin gravedad (no cambia la cinemática)",
            "Adimensional: U = H = 1 → ν = 1/Re",
            "Variar la viscosidad ≡ variar Re"], 8.4, 1.4, 4.7, 5)

# 4. CI/CF --------------------------------------------------------------------
s = slide("Condiciones iniciales y de frontera",
          "Integrante 2. Hay un canal de entrada de 2H antes del escalón, como en los estudios de referencia; el escalón "
          "es un bloque de celdas sólidas. p = 0 en la salida hace no singular la matriz de Poisson.")
rows = [("Frontera", "Velocidad", "Presión"),
        ("Entrada x = −2H, S < y < H", "Poiseuille u = 6Uη(1−η), v = 0", "∂p/∂n = 0"),
        ("Escalón (tapa y cara)", "u = v = 0 (no deslizamiento)", "∂p/∂n = 0"),
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
s = slide("Método numérico: 3 pasos por cada Δt",
          "Integrante 2/3. Paso 1: NS sin presión; Adams-Bashforth estima la aceleración a mitad del paso con la actual y la "
          "anterior (Euler explota con convección por promedio). Paso 2: la presión que hace cumplir continuidad (sale de "
          "aplicar divergencia al paso 3). Paso 3: corregir. CFL: el fluido no avanza más de una celda por paso.")
eq_block(s, eq_png("proj", [r"$1)\ \mathbf{u}^*=\mathbf{u}^n+\Delta t\left[\frac{3}{2}A^n-\frac{1}{2}A^{n-1}\right]$",
                       r"$\quad A=\frac{1}{Re}\nabla^2\mathbf{u}-\nabla\cdot(\mathbf{u}\mathbf{u})$",
                       r"$2)\ \nabla^2 p^{n+1}=\frac{\nabla\cdot\mathbf{u}^*}{\Delta t}$",
                       r"$3)\ \mathbf{u}^{n+1}=\mathbf{u}^*-\Delta t\,\nabla p^{n+1}$",
                       r"$\Delta t\leq\min\left(\frac{\Delta x}{|u|_{max}},\ \frac{Re}{2}\left(\frac{1}{\Delta x^2}+\frac{1}{\Delta y^2}\right)^{-1}\right)$"],
            fs=24), 0.4, 1.3, h_line=0.68, gap=0.33)
pic(s, FIG / "malla_escalonada.png", 8.6, 1.2, w=4.5)
bullets(s, ["Derivadas → diferencias; valor en la cara = promedio",
            "p en el centro, u y v en las caras",
            "Adams–Bashforth: estable sin difusión falsa",
            "Poisson: sistema lineal A·p = b (LU)",
            "∇·u = 10⁻¹⁴: la masa se conserva"], 8.5, 4.4, 4.7, 3.0, size=15)

# 6. Caso base ----------------------------------------------------------------
s = slide("Caso base Re = 200: x_r/S = 4.91",
          "Integrante 3. Leer vorticidad (capa de corte) y presión (recuperación aguas abajo = gradiente adverso). "
          "Aquí va la DEMO EN VIVO: cambiar RE_BASE en el bloque 0 y ejecutar.")
pic(s, FIG / "campos_base.png", 0.4, 1.1, h=4.6)
pic(s, FIG / "perfiles_base.png", 0.4, 5.75, h=1.65)
bullets(s, ["6400 celdas, 2608 pasos, ~3 s", "p sube tras el escalón: gradiente adverso",
            "u_max: 1.5 → 0.75 (masa)"], 9.6, 5.6, 3.6, 1.8, size=15)

# 7. Video del arranque -------------------------------------------------------
s = slide("Video: cómo se forma el remolino (Re = 200)",
          "Integrante 3. Señalar: (1) vórtice de arranque en forma de hongo, (2) separación pasajera en el techo, "
          "(3) x_r(t) crece y se aplana, (4) el tablero gris queda atrapado en la burbuja: eso es recirculación. "
          "El video se reproduce en PowerPoint (clic sobre él).")
video(s, FIG / "arranque_re200.mp4", 0.35, 1.05, 10.9, t_poster=3.0)
bullets(s, ["Tinta virtual: partículas que el flujo arrastra",
            "Vórtice de arranque",
            "Separación pasajera en el techo",
            "Fluido atrapado: recirculación"], 11.35, 1.3, 1.95, 5.5, size=14)

# 8. Reynolds -----------------------------------------------------------------
s = slide("Efecto de la viscosidad (Re)",
          "Integrante 3/4. x_r crece casi lineal hasta Re 400; luego más lento porque la burbuja superior "
          "empuja el chorro hacia abajo.")
pic(s, FIG / "re_remolinos.png", 0.3, 1.2, w=8.0)
pic(s, FIG / "re_cortante.png", 8.5, 1.3, w=4.7)
bullets(s, ["Re 100 → 600: x_r/S 2.8 → 10.1", "Burbuja superior desde Re ≈ 400",
            "τ_w = 0 marca el reacoplamiento"], 8.5, 3.4, 4.7, 3, size=17)

# 9. Video comparativo --------------------------------------------------------
s = slide("Video: tres viscosidades a la vez",
          "Integrante 4. Re = 100 se calma en t ≈ 20; Re = 600 forma varios vórtices que viajan y se juntan, y una burbuja en "
          "el techo que se queda. Menos viscosidad = transitorio más largo y remolino más largo.")
video(s, FIG / "comparacion_re.mp4", 0.35, 1.05, 10.9, t_poster=5.0)
bullets(s, ["Re = 100: se calma en t ≈ 20",
            "Re = 600: vórtices que viajan y se juntan",
            "Burbuja del techo sólo a Re alto"], 11.35, 1.3, 1.95, 5.5, size=14)

# 10. Malla y dt --------------------------------------------------------------
s = slide("Malla y paso de tiempo",
          "Integrante 4. Duplicar la malla reduce el cambio unas 5 veces (esquema de segundo orden): con NY = 20 el error es < 1 %. "
          "dt no cambia el resultado estacionario si es estable. Euler simple explota: por eso Adams-Bashforth.")
pic(s, FIG / "malla.png", 0.3, 1.15, w=7.2)
pic(s, FIG / "dt.png", 7.6, 1.15, w=5.5)
bullets(s, ["NY = 10 / 20 / 40 → x_r/S = 4.75 / 4.91 / 4.95: con 20 celdas el error es < 1 %",
            "Δt ≤ 0.8 Δt_CFL: mismo resultado x_r/S = 4.91, sólo cambia el número de pasos",
            "Δt = Δt_CFL explota en 36 pasos; Euler simple explota en 706 aunque Δt sea chico"], 0.5, 4.2, 12.3, 3, size=19)

# 11. Comparación con la literatura ------------------------------------------
s = slide("Comparación con la literatura",
          "Integrante 4. Diferencias de 2 % o menos de Re 200 a 600. El error de malla es < 1 %, así que la diferencia es del orden "
          "de la dispersión entre estudios publicados.")
pic(s, FIG / "validacion.png", 0.4, 1.2, w=7.6)
rows = [("Re", "Nuestro", "Literatura", "Dif."), ("100", "2.84", "3.00", "−5.4 %"), ("200", "4.91", "4.95", "−0.7 %"),
        ("300", "6.73", "6.75", "−0.3 %"), ("400", "8.26", "8.10", "+2.0 %"), ("500", "9.40", "9.30", "+1.1 %"),
        ("600", "10.06", "10.05", "+0.1 %")]
tbl = s.shapes.add_table(len(rows), 4, Inches(8.3), Inches(1.3), Inches(4.7), Inches(3.6)).table
for i, rw in enumerate(rows):
    for j, c in enumerate(rw):
        tbl.cell(i, j).text = c
        tbl.cell(i, j).text_frame.paragraphs[0].font.size = Pt(17)
        tbl.cell(i, j).text_frame.paragraphs[0].font.bold = (i == 0)
bullets(s, ["≤ 2 % para Re 200–600", "Remolino del techo desde Re ≈ 400, como en la literatura"], 8.3, 5.1, 4.8, 2, size=17)

# 12. Conclusiones ------------------------------------------------------------
s = slide("Conclusiones",
          "Cierre (1 min) y preguntas. Tener el notebook abierto para la demo.")
bullets(s, ["Navier–Stokes resuelto con el método de proyección; la masa se conserva",
            "Reproduce separación, reacoplamiento y burbuja secundaria",
            "Menor viscosidad → burbuja más larga (x_r ∝ Re hasta ~400) y arranque más agitado",
            "Segundo orden: con 20 celdas/H el error de malla es < 1 %; literatura ±2 %",
            "Δt sólo afecta la estabilidad; Euler explota, Adams–Bashforth no",
            "La tinta virtual muestra el vórtice de arranque y el fluido atrapado",
            "Siguiente paso: Re > 800 (inestabilidad, 3D) con malla más fina"], 0.6, 1.3, 12, 5.5, size=22)

out = HERE / "presentacion.pptx"
prs.save(out)
print("escrito", out)
