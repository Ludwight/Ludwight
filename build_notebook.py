"""Genera BFS_escalon_descendente.ipynb a partir de src/bfs_solver.py y src/plots.py.

Así el notebook es autocontenido (no depende de rutas) y el código fuente vive en un solo lugar.
Uso:  python build_notebook.py
"""
import re
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).parent
solver = (ROOT / "src" / "bfs_solver.py").read_text(encoding="utf-8")
plots = (ROOT / "src" / "plots.py").read_text(encoding="utf-8")

# separa el solver en bloques "# 1. ...", "# 2. ..." para tener una celda por bloque
blocks = re.split(r"\n(?=# -{70,}\n# \d\.)", solver)
header, solver_blocks = blocks[0], blocks[1:]
plots_body = plots.split('from bfs_solver import cell_fields\n', 1)[1]

md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
cells = []

cells.append(md(r"""# Flujo laminar sobre un escalón descendente (*backward-facing step*)
**Mecánica de Fluidos · Proyecto final**

Simulación numérica 2D del flujo incompresible y laminar que se separa en la arista de un escalón,
forma una burbuja de recirculación y se vuelve a adherir aguas abajo. El código es propio:
volúmenes finitos en malla escalonada (MAC), método de proyección de Chorin y presión por factorización LU.

| Bloque | Contenido |
|---|---|
| 0 | Librerías y parámetros de usuario (editar aquí para la demo en vivo) |
| 1 | Física: ecuaciones de gobierno, CI/CF y supuestos |
| 2 | Método numérico (malla MAC, proyección, estabilidad) |
| 3 | Código del solver |
| 4 | Caso base Re = 200 |
| 5 | Animación del transitorio |
| 6 | Análisis paramétrico: Re (viscosidad), malla, Δt, esquema convectivo |
| 7 | Validación contra la literatura |
| 8 | Conclusiones |

**Ejecutar todo** (*Kernel → Restart & Run All*) corre el notebook completo en unos 5–8 min en una laptop.
Sólo requiere `numpy`, `scipy` y `matplotlib`.

Referencia de partida: el notebook *Combined backward facing step* de kangluosee/CFD-Python (SIMPLE colocalizado
con interpolación de Rhie–Chow). Aquí se reescribió desde cero con otro método (proyección en malla escalonada),
vectorizado con NumPy, y se añadió el análisis paramétrico y la validación."""))

cells.append(md("## 0. Librerías y parámetros de usuario"))
cells.append(code(r"""import time
import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as spla
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter
from IPython.display import HTML, display
from pathlib import Path

FIG = Path("figures"); FIG.mkdir(exist_ok=True)   # aquí se guardan las figuras del reporte
plt.rcParams.update({"figure.dpi": 100, "font.size": 10})"""))

cells.append(code(r"""# ===================== PARÁMETROS DE USUARIO (demo en vivo) =====================
RE_BASE  = 200     # número de Reynolds  Re = U H / nu   (equivale a variar la viscosidad)
NY_BASE  = 20      # celdas en la altura H del canal (malla uniforme dx = dy)
L_BASE   = 15.0    # longitud del dominio aguas abajo del escalón, en unidades de H
GAMMA    = 0.5     # esquema convectivo: 0 = centrado, 1 = upwind
DT_BASE  = None    # paso de tiempo; None = 50 % del límite de estabilidad
RUN_RE800 = True   # caso de validación Re = 800 (Gartling, 1990); tarda ~2-3 min
# ================================================================================="""))

cells.append(md(r"""## 1. Física del problema

### Geometría
Canal de altura $H$ aguas abajo; el canal de entrada tiene altura $h = H - S$ y el escalón altura $S = H/2$
(relación de expansión $ER = H/h = 2$). La entrada se coloca justo en el plano del escalón ($x=0$), como en el
*benchmark* de Gartling (1990). El dominio es $0 \le x \le L$, $0 \le y \le H$.

### Ecuaciones de gobierno (adimensionales)
Con $U$ = velocidad media de entrada, $H$ como longitud y $\rho U^2$ como presión:

$$\nabla\cdot\mathbf{u} = 0, \qquad
\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u} = -\nabla p + \frac{1}{Re}\nabla^2\mathbf{u},
\qquad Re = \frac{U H}{\nu}$$

$H = 2h$ es el diámetro hidráulico del canal de entrada, la definición que usan Armaly et al. (1983) y Gartling (1990).
**Variar la viscosidad $\nu$ equivale a variar $Re$.**

### Supuestos
Flujo 2D, incompresible ($\rho$ constante), newtoniano, isotérmico, laminar ($Re \le 800$), sin gravedad (no afecta la cinemática).

### Condiciones de frontera e inicial
| Frontera | Velocidad | Presión |
|---|---|---|
| Entrada $x=0,\ S<y<H$ | Poiseuille: $u = 6U\eta(1-\eta)$, $\eta = (y-S)/h$; $v=0$ | $\partial p/\partial n = 0$ |
| Cara del escalón $x=0,\ y<S$ | no deslizamiento $u=v=0$ | $\partial p/\partial n = 0$ |
| Paredes $y=0,\ y=H$ | no deslizamiento $u=v=0$ | $\partial p/\partial n = 0$ |
| Salida $x=L$ | $\partial u/\partial x = \partial v/\partial x = 0$ | $p = 0$ |

**CI:** fluido en reposo, $\mathbf{u}(x,y,0)=0$; se integra en el tiempo hasta el estado estacionario.

### El fenómeno
La capa límite no puede seguir la esquina convexa y se separa. Se forma una capa de corte libre que encierra
una **burbuja de recirculación** pegada a la pared inferior; la línea de corriente divisoria vuelve a la pared en
$x_r$ (**reacoplamiento**, donde $\tau_w = 0$). Al subir $Re$, $x_r$ crece casi linealmente, y para $Re \gtrsim 400$
el gradiente de presión adverso separa también la capa límite superior y aparece una **burbuja secundaria** en la pared de arriba."""))

cells.append(md(r"""## 2. Método numérico

**Malla escalonada (MAC):** $p$ en centros de celda, $u$ en caras verticales, $v$ en caras horizontales.
Así se evita el desacople presión–velocidad ("tablero de ajedrez") sin necesidad de Rhie–Chow.

**Proyección de Chorin (paso fraccionado)**, con $\mathbf{R} = \tfrac{1}{Re}\nabla^2\mathbf{u} - \nabla\cdot(\mathbf{u}\mathbf{u})$:
1. Predictor explícito: $\mathbf{u}^* = \mathbf{u}^n + \Delta t\,\mathbf{R}(\mathbf{u}^n)$
2. Poisson: $\nabla^2 p^{n+1} = \dfrac{\nabla\cdot\mathbf{u}^*}{\Delta t}$ (matriz de 5 puntos, factorizada **una vez** con LU dispersa)
3. Corrector: $\mathbf{u}^{n+1} = \mathbf{u}^* - \Delta t\,\nabla p^{n+1}$, que deja $\nabla\cdot\mathbf{u}^{n+1}=0$ a precisión de máquina.

**Discretización espacial:** difusión con diferencias centrales de 2.º orden; convección en forma conservativa
con el esquema híbrido de Hirt (Griebel et al., 1998):
$$\frac{\partial(u^2)}{\partial x}\Big|_i \approx \frac{u_e^2-u_w^2}{\Delta x} + \frac{\gamma}{\Delta x}\left[|u_e|\frac{u_i-u_{i+1}}{2} - |u_w|\frac{u_{i-1}-u_i}{2}\right],$$
con $\gamma=0$ (centrado, 2.º orden) y $\gamma=1$ (upwind, 1.er orden, más difusivo).

**Estabilidad (Euler explícito):**
$$\Delta t \le \min\left(\frac{\Delta x}{|u|_{max}},\ \frac{Re}{2}\Big(\frac{1}{\Delta x^2}+\frac{1}{\Delta y^2}\Big)^{-1}\right)$$
(CFL convectivo y número de Fourier difusivo). Por defecto se usa el 50 % de ese límite.

**Convergencia:** se detiene cuando $\max|\mathbf{u}^{n+1}-\mathbf{u}^n|/\Delta t < 10^{-5}$.

**Post-proceso:** $x_r$ es el cruce por cero (de $-$ a $+$) de $\tau_w \propto u$ en la primera celda junto a la pared."""))

cells.append(md("## 3. Código del solver"))
titles = {
    "1": "### 3.1 Malla y operador de Poisson",
    "2": "### 3.2 Condiciones de frontera",
    "3": "### 3.3 Términos de momento (convección + difusión)",
    "4": "### 3.4 Paso fraccionado e integración en el tiempo",
    "5": "### 3.5 Post-proceso: reacoplamiento, vorticidad, función de corriente",
}
for blk in solver_blocks:
    n = re.search(r"# (\d)\.", blk).group(1)
    cells.append(md(titles[n]))
    cells.append(code(blk.strip("\n")))
cells.append(md("### 3.6 Funciones de graficado"))
cells.append(code("S_COLOR = \"0.35\"\n" + plots_body.split('S_COLOR = "0.35"\n', 1)[1].strip("\n")))

cells.append(md(r"""## 4. Caso base
Se resuelve con los parámetros del bloque 0 (por defecto Re = 200, 20 celdas por H). Se verifica que la divergencia
discreta sea ~0 y se grafican los campos."""))
cells.append(code(r"""base = solve_bfs(Re=RE_BASE, ny=NY_BASE, L=L_BASE, dt=DT_BASE, gamma=GAMMA, snap_every=15)
print(f"max |div u| = {divergence_norm(base):.1e}   (incompresibilidad a precisión de máquina)")
S = base["g"]["S"]
print(f"Reacoplamiento x_r = {base['xr']:.3f} H  ->  x_r/S = {base['xr']/S:.2f}")"""))
cells.append(code(r"""plot_fields(base, xmax=8, fname=FIG / "campos_base.png"); plt.show()
plot_profiles(base, fname=FIG / "perfiles_base.png"); plt.show()"""))
cells.append(md(r"""**Lectura física.** Aguas abajo de la esquina el perfil parabólico se "despega" de la pared: aparece una zona con
$u<0$ (recirculación, vorticidad negativa intensa en la capa de corte). En $x_r$ el flujo se vuelve a adherir y el
perfil evoluciona de nuevo hacia una parábola que ocupa todo el canal ($u_{max} = 1.5 \to 0.75$ por conservación de masa).
La presión **sube** a lo largo del canal en la zona de expansión (recuperación de presión, gradiente adverso)."""))

cells.append(md("## 5. Animación del transitorio (arranque desde el reposo)"))
cells.append(code(r"""def animate_run(res, xmax=8, every=1, fname=None):
    g = res["g"]; snaps = res["snaps"][::every]
    X, Y = np.meshgrid(g["xc"], g["yc"], indexing="ij")
    fig, ax = plt.subplots(figsize=(10, 2.3), constrained_layout=True)

    def frame(k):
        t, u, v = snaps[k]
        ax.clear()
        uc = 0.5 * (u[1:, 1:-1] + u[:-1, 1:-1]); vc = 0.5 * (v[1:-1, 1:] + v[1:-1, :-1])
        ax.contourf(X, Y, np.hypot(uc, vc), levels=np.linspace(0, 1.6, 33), cmap="viridis")
        ax.streamplot(g["xc"], g["yc"], uc.T, vc.T, color="w", density=1.2, linewidth=0.5, arrowsize=0.6)
        ax.add_patch(patches.Rectangle((-0.6, 0), 0.6, g["S"], fc="0.35", ec="k", hatch="///"))
        ax.set_xlim(-0.6, xmax); ax.set_ylim(0, 1); ax.set_aspect("equal")
        ax.set_title(f"Re = {res['Re']}   t U/H = {t:5.1f}")
        return []

    ani = FuncAnimation(fig, frame, frames=len(snaps), interval=120)
    if fname:
        ani.save(fname, writer=PillowWriter(fps=8))
    plt.close(fig)
    return ani

ani = animate_run(base, every=max(1, len(base["snaps"]) // 60), fname=FIG / "transitorio.gif")
display(HTML(ani.to_jshtml()))"""))

cells.append(md(r"""## 6. Análisis paramétrico
### 6.1 Efecto del número de Reynolds (viscosidad)
$Re = UH/\nu$: bajar la viscosidad equivale a subir $Re$. Se usa un dominio más largo ($L = 25H$) para que la burbuja
secundaria y el reacoplamiento no toquen la salida."""))
cells.append(code(r"""RE_LIST = [100, 200, 300, 400, 600]
runs_re = [solve_bfs(Re=Re, ny=20, L=25.0, gamma=GAMMA, t_end=500) for Re in RE_LIST]

print("\n  Re    nu       x_r/S   x_s/S   x_e/S  (burbuja secundaria, pared superior)")
for r in runs_re:
    print(f"{r['Re']:5d}  {r['nu']:.5f}  {r['xr']/S:6.2f}  {r['xs']/S:6.2f}  {r['xe']/S:6.2f}")"""))
cells.append(code(r"""fig = plt.figure(figsize=(12, 7.5), constrained_layout=True)
gs = fig.add_gridspec(len(runs_re), 1)
for k, r in enumerate(runs_re):
    ax = fig.add_subplot(gs[k]); g = r["g"]; f = cell_fields(r)
    Xf, Yf = np.meshgrid(g["xf"], g["yf"], indexing="ij")
    X, Y = np.meshgrid(g["xc"], g["yc"], indexing="ij")
    ax.contourf(X, Y, f["speed"], levels=40, cmap="viridis")
    ax.contourf(X, Y, f["uc"], levels=[-10, 0], colors="red", alpha=0.45)      # zonas con u < 0
    ax.contour(Xf, Yf, f["psi"], levels=np.linspace(0.05, 0.95, 10), colors="w", linewidths=0.5)
    ax.add_patch(patches.Rectangle((-0.6, 0), 0.6, S, fc="0.35", ec="k", hatch="///"))
    ax.set_xlim(-0.6, 12); ax.set_aspect("equal"); ax.set_yticks([0, 1])
    ax.set_ylabel(f"Re={r['Re']}")
ax.set_xlabel("x / H")
fig.suptitle("|V| y líneas de corriente; en rojo las zonas de flujo inverso (u < 0): burbuja principal y secundaria")
fig.savefig(FIG / "re_streamfunction.png", dpi=150); plt.show()

plot_wall_shear(runs_re, fname=FIG / "re_tau_w.png"); plt.show()"""))

cells.append(md(r"""### 6.2 Independencia de malla
Caso Re = 200 con 10, 20 y 40 celdas por $H$ (refinamiento $r = 2$). Con la extrapolación de Richardson se estima
el orden observado $p$ y el valor "exacto" de $x_r$, y con eso el índice de convergencia de malla (GCI, Roache)."""))
cells.append(code(r"""NY_LIST = [10, 20, 40]
runs_mesh = [solve_bfs(Re=200, ny=ny, L=15.0, gamma=GAMMA) for ny in NY_LIST]
xr = np.array([r["xr"] / S for r in runs_mesh])
p_obs = np.log(abs(xr[1] - xr[0]) / abs(xr[2] - xr[1])) / np.log(2)
xr_ext = xr[2] + (xr[2] - xr[1]) / (2**p_obs - 1)
gci = 1.25 * abs((xr[2] - xr[1]) / xr[2]) / (2**p_obs - 1) * 100
for ny, x, r in zip(NY_LIST, xr, runs_mesh):
    print(f"ny = {ny:3d}  celdas = {r['g']['nx']*ny:6d}  x_r/S = {x:.3f}  CPU = {r['cpu']:5.1f} s")
print(f"Orden observado p = {p_obs:.2f};  Richardson x_r/S = {xr_ext:.3f};  GCI(malla fina) = {gci:.2f} %")

fig, ax = plt.subplots(1, 2, figsize=(11, 3.4), constrained_layout=True)
h = 1 / np.array(NY_LIST)
ax[0].plot(h, xr, "o-", label="simulación"); ax[0].axhline(xr_ext, color="k", ls="--", label="Richardson (h→0)")
ax[0].set_xlabel("Δx / H"); ax[0].set_ylabel("x_r / S"); ax[0].set_title("Convergencia de x_r con la malla"); ax[0].legend()
for r, ny in zip(runs_mesh, NY_LIST):
    i = int(round(3.0 / r["g"]["dx"]))
    ax[1].plot(r["u"][i, 1:-1], r["g"]["yc"], label=f"ny = {ny}")
ax[1].set_xlabel("u / U"); ax[1].set_ylabel("y / H"); ax[1].set_title("Perfil u(y) en x = 3H"); ax[1].legend()
fig.savefig(FIG / "malla.png", dpi=150); plt.show()"""))

cells.append(md(r"""### 6.3 Paso de tiempo y estabilidad
Re = 200, ny = 20. El límite convectivo es $\Delta t_{CFL} = \Delta x/u_{max} = 0.033$ y el difusivo
$\Delta t_{Fo} = 0.125$; manda el convectivo. Se prueban valores por debajo y por encima."""))
cells.append(code(r"""g20 = make_grid(L=15.0, ny=20)
dt_safe, dt_cfl, dt_fo = stable_dt(g20, 200)
print(f"dt_CFL = {dt_cfl:.4f}   dt_Fourier = {dt_fo:.4f}   dt por defecto = {dt_safe:.4f}")
DT_LIST = [0.005, 0.0167, 0.030, 0.036, 0.045]
runs_dt = [solve_bfs(Re=200, ny=20, L=15.0, dt=dt, gamma=GAMMA, t_end=150) for dt in DT_LIST]

fig, ax = plt.subplots(figsize=(8, 3.6), constrained_layout=True)
for r in runs_dt:
    ax.semilogy(r["hist_t"], r["hist_res"], label=f"Δt = {r['dt']:.4f} ({r['status']})")
ax.set_xlabel("t U/H"); ax.set_ylabel("max |Δu|/Δt"); ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=8)
ax.set_title("Efecto de Δt: mismo estado estacionario si es estable; divergencia si Δt > límite")
fig.savefig(FIG / "dt.png", dpi=150); plt.show()
for r in runs_dt:
    xr_txt = f"{r['xr']/S:.3f}" if r["status"] != "diverged" else "—"
    print(f"dt = {r['dt']:.4f}  ({r['dt']/dt_cfl:4.2f} dt_CFL)  {r['status']:9s}  pasos = {r['steps']:5d}  x_r/S = {xr_txt}")"""))
cells.append(md(r"""Mientras el esquema es estable, el estado estacionario **no depende** de $\Delta t$ (mismo $x_r$); un $\Delta t$ mayor
sólo llega antes. Por encima de ~1.1 $\Delta t_{CFL}$ los errores crecen exponencialmente y la solución diverge en pocas
iteraciones. El término $\gamma$-upwind añade algo de disipación, por eso el límite real queda un poco por encima del CFL teórico."""))

cells.append(md(r"""### 6.4 Esquema convectivo (difusión numérica)
Re = 200, ny = 20: comparación de $\gamma = 0$ (centrado), $0.5$ y $1$ (upwind). El esquema centrado con Euler explícito
tiene una restricción extra, $\Delta t \le 2\nu/|u|^2_{max}$ (Griebel et al.): a Re = 200 eso es $\Delta t \le 0.0044$,
así que para $\gamma = 0$ se usa $\Delta t = 0.004$ (con el $\Delta t$ por defecto diverge)."""))
cells.append(code(r"""runs_gamma = [solve_bfs(Re=200, ny=20, L=15.0, gamma=0.0, dt=0.004),
              solve_bfs(Re=200, ny=20, L=15.0, gamma=0.5),
              solve_bfs(Re=200, ny=20, L=15.0, gamma=1.0)]
for r in runs_gamma:
    print(f"gamma = {r['gamma']:.1f}  x_r/S = {r['xr']/S:.2f}")
fig, ax = plt.subplots(figsize=(9, 3.2), constrained_layout=True)
for r in runs_gamma:
    ax.plot(r["g"]["xf"] / S, r["nu"] * r["u"][:, 1] / (0.5 * r["g"]["dy"]), label=f"γ = {r['gamma']}")
ax.axhline(0, color="k", lw=0.8); ax.set_xlim(0, 25); ax.legend()
ax.set_xlabel("x / S"); ax.set_ylabel("τ_w / ρU²"); ax.set_title("Re = 200: efecto del esquema convectivo")
fig.savefig(FIG / "gamma.png", dpi=150); plt.show()"""))
cells.append(md(r"""El upwind puro ($\gamma=1$) introduce una viscosidad numérica $\nu_{num}\approx \gamma|u|\Delta x/2$. Con
$\Delta x = 0.05$ y $|u|\sim 1$ da $\nu_{num}\approx 0.025$, **cinco veces** la viscosidad física a Re = 200
($\nu = 0.005$): el flujo se comporta como si tuviera un $Re$ efectivo menor y la burbuja se acorta.
El centrado es el más preciso pero exige un $\Delta t$ ~4 veces menor (y a Re = 400 con el $\Delta t$ por defecto diverge en
menos de 100 pasos). El valor intermedio $\gamma=0.5$ es el compromiso que se usa en el resto del trabajo, y es la causa principal
de que el orden observado de convergencia en malla sea ~1."""))

cells.append(md(r"""## 7. Validación contra la literatura
Se compara $x_r/S$ con datos numéricos 2D de referencia (tabla de Re = 100–800 recopilada en arXiv:2507.16509) y con el
*benchmark* clásico de Gartling (1990) en Re = 800 ($x_r = 6.10H$ → $x_r/S = 12.2$; burbuja superior de $4.85H$ a $10.48H$).
Los experimentos de Armaly et al. (1983) coinciden con las simulaciones 2D sólo hasta Re ≈ 400; arriba el flujo real se vuelve 3D."""))
cells.append(code(r"""LIT_RE = np.array([100, 200, 300, 400, 500, 600, 700, 800])
LIT_XR = np.array([3.00, 4.95, 6.75, 8.10, 9.30, 10.05, 10.95, 11.55])   # x_r/S, arXiv:2507.16509 (Tabla 1)

runs_val = list(runs_re)
if RUN_RE800:
    r800 = solve_bfs(Re=800, ny=20, L=30.0, gamma=GAMMA, t_end=700, tol=1e-4)
    runs_val.append(r800)
    print(f"Re = 800: x_r/S = {r800['xr']/S:.2f} (Gartling 12.2);  burbuja superior "
          f"{r800['xs']:.2f}H – {r800['xe']:.2f}H (Gartling 4.85H – 10.48H)")

re_sim = np.array([r["Re"] for r in runs_val]); xr_sim = np.array([r["xr"] / S for r in runs_val])
fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)
ax.plot(LIT_RE, LIT_XR, "ks--", mfc="none", label="2D numérico (arXiv:2507.16509)")
ax.plot([800], [12.2], "r^", ms=9, mfc="none", label="Gartling (1990)")
ax.plot(re_sim, xr_sim, "bo-", label="este trabajo (ny = 20)")
ax.set_xlabel("Re = U H / ν"); ax.set_ylabel("x_r / S"); ax.grid(alpha=0.3); ax.legend()
ax.set_title("Longitud de reacoplamiento vs Reynolds")
fig.savefig(FIG / "validacion.png", dpi=150); plt.show()

for Re_, x in zip(re_sim, xr_sim):
    ref = np.interp(Re_, LIT_RE, LIT_XR)
    print(f"Re = {Re_:4d}   este trabajo = {x:6.2f}   referencia = {ref:6.2f}   error = {100*(x-ref)/ref:+5.1f} %")"""))
cells.append(code(r"""if RUN_RE800:
    plot_fields(r800, xmax=15, fname=FIG / "campos_re800.png"); plt.show()"""))
cells.append(md(r"""**Discusión de la validación.** Con 20 celdas por $H$ la tendencia $x_r(Re)$ coincide con la tabla de referencia
dentro de ~3 % hasta Re = 600 y se reproduce la burbuja secundaria superior (incipiente en Re = 400, clara en Re ≥ 600).
Hay que leer esa coincidencia con cuidado: el estudio de malla (6.2) indica que el valor convergido a Re = 200 es
$x_r/S\approx 5.3$, y el esquema centrado ($\gamma=0$, 6.4) da lo mismo (5.33). Es decir, a 20 celdas/$H$ la difusión numérica
acorta la burbuja ~8 %, y parte del buen acuerdo con la tabla es cancelación de errores (la tabla además puede usar un canal
de entrada aguas arriba, que cambia el perfil en la arista). En Re = 800, con la misma configuración que Gartling (entrada en
el plano del escalón), la malla gruesa da 10.45 frente a 12.2: el error crece con $Re$ porque la capa de corte es más delgada
y $\nu_{num}/\nu$ aumenta. Para cerrar esa diferencia hace falta refinar (ny ≥ 40) o un esquema de mayor orden."""))

cells.append(md(r"""## 8. Conclusiones
* El solver de proyección en malla MAC conserva la masa a precisión de máquina y reproduce la física del escalón:
  separación en la arista, burbuja principal, reacoplamiento y, desde Re ≈ 400, burbuja secundaria en la pared superior.
* $x_r/S$ crece casi linealmente con $Re$ (menor viscosidad → la capa de corte tarda más en difundir momento hacia la pared)
  y sigue la tendencia de la literatura 2D (±3 % hasta Re = 600 con 20 celdas/H); en Re = 800 la malla gruesa subestima
  $x_r$ (10.45 vs 12.2 de Gartling) por difusión numérica.
* El estudio de malla muestra convergencia monótona con orden observado ~1 (por la parte upwind del esquema); con
  20 celdas por $H$ el error de discretización en $x_r$ es de algunos por ciento y crece con $Re$, lo que explica que en
  Re = 800 la burbuja quede más corta que la de Gartling.
* $\Delta t$ no cambia el estado estacionario mientras se respete el criterio CFL; por encima de él la integración explícita diverge.
* El upwind ($\gamma=1$) añade difusión numérica que acorta la burbuja; esto ilustra por qué en CFD importa el orden del esquema.

**Referencias**
1. Armaly, B. F., Durst, F., Pereira, J. C. F., Schönung, B. (1983). *Experimental and theoretical investigation of backward-facing step flow*. J. Fluid Mech. 127, 473–496.
2. Gartling, D. K. (1990). *A test problem for outflow boundary conditions — flow over a backward-facing step*. Int. J. Numer. Methods Fluids 11, 953–967.
3. Chorin, A. J. (1968). *Numerical solution of the Navier–Stokes equations*. Math. Comp. 22, 745–762.
4. Griebel, M., Dornseifer, T., Neunhoeffer, T. (1998). *Numerical Simulation in Fluid Dynamics: A Practical Introduction*. SIAM.
5. Roache, P. J. (1994). *Perspective: a method for uniform reporting of grid refinement studies*. J. Fluids Eng. 116, 405–413.
6. arXiv:2507.16509 (2025). *A Finite Volume and Levenberg–Marquardt Optimization Framework for Benchmarking MHD Flows over Backward-Facing Steps* (Tabla 1, caso hidrodinámico).
7. kangluosee, *CFD-Python: Combined backward facing step* (GitHub), código de referencia."""))

nb = nbf.v4.new_notebook(cells=cells, metadata={
    "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
    "language_info": {"name": "python"}})
out = ROOT / "BFS_escalon_descendente.ipynb"
nbf.write(nb, out)
print("escrito", out)
