"""Solver 2D incompresible para el escalón descendente (backward-facing step)."""
import time
import numpy as np
import scipy.sparse as sps
import scipy.sparse.linalg as spla


# ---------------------------------------------------------------------------
# 1. Malla y operador de Poisson
# ---------------------------------------------------------------------------
def make_grid(L=20.0, H=1.0, S=0.5, ny=20):
    """Malla escalonada (MAC) uniforme dx = dy sobre [0,L] x [0,H]."""
    dy = H / ny
    nx = int(round(L / dy))
    dx = L / nx
    xc = (np.arange(nx) + 0.5) * dx          # centros de celda (p)
    yc = (np.arange(ny) + 0.5) * dy
    xf = np.arange(nx + 1) * dx              # caras x (u)
    yf = np.arange(ny + 1) * dy              # caras y (v)
    return dict(L=L, H=H, S=S, nx=nx, ny=ny, dx=dx, dy=dy,
                xc=xc, yc=yc, xf=xf, yf=yf)


def poisson_matrix(g):
    """Laplaciano de 5 puntos centrado en celda.
    Neumann (dp/dn = 0) en entrada y paredes; Dirichlet p = 0 en la salida."""
    nx, ny, dx, dy = g["nx"], g["ny"], g["dx"], g["dy"]

    def lap1d(n, h, dirichlet_right):
        main = -2.0 * np.ones(n)
        main[0] = -1.0                                   # Neumann izquierda/abajo
        main[-1] = -3.0 if dirichlet_right else -1.0     # p_ghost = -p (p_cara = 0)
        off = np.ones(n - 1)
        return sps.diags([off, main, off], [-1, 0, 1]) / h**2

    Dxx = lap1d(nx, dx, dirichlet_right=True)
    Dyy = lap1d(ny, dy, dirichlet_right=False)
    A = sps.kron(Dxx, sps.identity(ny)) + sps.kron(sps.identity(nx), Dyy)
    return spla.splu(A.tocsc())              # factorización LU (una sola vez)


# ---------------------------------------------------------------------------
# 2. Condiciones de frontera
# ---------------------------------------------------------------------------
def inlet_profile(g, Ub=1.0):
    """Perfil parabólico de Poiseuille en S < y < H con velocidad media Ub; 0 en la cara del escalón."""
    S, H, y = g["S"], g["H"], g["yc"]
    h = H - S
    eta = (y - S) / h
    u = np.where(y > S, 6.0 * Ub * eta * (1.0 - eta), 0.0)
    return u


def apply_bc(u, v, uin):
    """u: (nx+1, ny+2) con celdas fantasma en y;  v: (nx+2, ny+1) con fantasmas en x."""
    # entrada (x = 0): perfil impuesto / pared del escalón
    u[0, 1:-1] = uin
    v[0, :] = -v[1, :]                 # v = 0 en x = 0
    # salida (x = L): gradiente nulo
    u[-1, 1:-1] = u[-2, 1:-1]
    v[-1, :] = v[-2, :]
    # paredes inferior y superior: no deslizamiento
    u[:, 0] = -u[:, 1]
    u[:, -1] = -u[:, -2]
    v[:, 0] = 0.0
    v[:, -1] = 0.0


# ---------------------------------------------------------------------------
# 3. Términos de momento (convección con esquema híbrido gamma + difusión central)
# ---------------------------------------------------------------------------
def momentum_rhs(u, v, nu, dx, dy, gamma):
    """Devuelve (Ru, Rv) = nu*lap(u) - conv(u) en caras interiores."""
    # ---- ecuación x, nodos u[1:-1, 1:-1] ----
    uc = u[1:-1, 1:-1]
    uE, uW = u[2:, 1:-1], u[:-2, 1:-1]
    uN, uS = u[1:-1, 2:], u[1:-1, :-2]
    lap_u = (uE - 2 * uc + uW) / dx**2 + (uN - 2 * uc + uS) / dy**2

    ue, uw = 0.5 * (uc + uE), 0.5 * (uW + uc)            # velocidades en caras
    du2dx = (ue**2 - uw**2 + gamma * (np.abs(ue) * (uc - uE) / 2
                                      - np.abs(uw) * (uW - uc) / 2)) / dx
    vn = 0.5 * (v[1:-2, 1:] + v[2:-1, 1:])               # v promedio arriba de u
    vs = 0.5 * (v[1:-2, :-1] + v[2:-1, :-1])             # v promedio abajo de u
    duvdy = (vn * 0.5 * (uc + uN) - vs * 0.5 * (uS + uc)
             + gamma * (np.abs(vn) * (uc - uN) / 2 - np.abs(vs) * (uS - uc) / 2)) / dy
    Ru = nu * lap_u - du2dx - duvdy

    # ---- ecuación y, nodos v[1:-1, 1:-1] ----
    vc = v[1:-1, 1:-1]
    vE, vW = v[2:, 1:-1], v[:-2, 1:-1]
    vN, vS = v[1:-1, 2:], v[1:-1, :-2]
    lap_v = (vE - 2 * vc + vW) / dx**2 + (vN - 2 * vc + vS) / dy**2

    vnn, vss = 0.5 * (vc + vN), 0.5 * (vS + vc)
    dv2dy = (vnn**2 - vss**2 + gamma * (np.abs(vnn) * (vc - vN) / 2
                                         - np.abs(vss) * (vS - vc) / 2)) / dy
    ue_ = 0.5 * (u[1:, 1:-2] + u[1:, 2:-1])              # u promedio a la derecha de v
    uw_ = 0.5 * (u[:-1, 1:-2] + u[:-1, 2:-1])            # u promedio a la izquierda de v
    duvdx = (ue_ * 0.5 * (vc + vE) - uw_ * 0.5 * (vW + vc)
             + gamma * (np.abs(ue_) * (vc - vE) / 2 - np.abs(uw_) * (vW - vc) / 2)) / dx
    Rv = nu * lap_v - duvdx - dv2dy
    return Ru, Rv


# ---------------------------------------------------------------------------
# 4. Paso fraccionado (proyección de Chorin) e integración en el tiempo
# ---------------------------------------------------------------------------
def stable_dt(g, Re, Umax=1.5, safety=0.5):
    """Límite explícito: CFL convectivo y número de Fourier difusivo."""
    dx, dy = g["dx"], g["dy"]
    dt_conv = min(dx, dy) / Umax
    dt_diff = 0.5 * Re / (1 / dx**2 + 1 / dy**2)
    return safety * min(dt_conv, dt_diff), dt_conv, dt_diff


def solve_bfs(Re=200, ny=20, L=20.0, S=0.5, dt=None, gamma=0.5, t_end=200.0,
              tol=1e-5, snap_every=None, verbose=True, max_div=1e3):
    """Integra Navier–Stokes 2D hasta estado estacionario (o t_end).

    Re  : número de Reynolds basado en la velocidad media de entrada Ub = 1 y en
          la altura del canal aguas abajo H = 1 (diámetro hidráulico de entrada).
    ny  : celdas en la altura H (malla uniforme dx = dy).
    dt  : paso de tiempo; None -> 50 % del límite de estabilidad.
    gamma : 0 = diferencias centrales, 1 = upwind puro (donor cell).
    """
    g = make_grid(L=L, H=1.0, S=S, ny=ny)
    nx, dx, dy = g["nx"], g["dx"], g["dy"]
    nu = 1.0 / Re
    if dt is None:
        dt = stable_dt(g, Re)[0]

    lu = poisson_matrix(g)
    uin = inlet_profile(g)

    u = np.zeros((nx + 1, ny + 2))
    v = np.zeros((nx + 2, ny + 1))
    u[:, 1:-1] = uin[None, :] * 0.0     # condición inicial: fluido en reposo
    apply_bc(u, v, uin)
    p = np.zeros((nx, ny))

    hist_t, hist_res, snaps = [], [], []
    n_steps = int(round(t_end / dt))
    status = "max_time"
    t0 = time.time()
    for n in range(1, n_steps + 1):
        Ru, Rv = momentum_rhs(u, v, nu, dx, dy, gamma)

        # (a) velocidad intermedia u*
        F = u[:, 1:-1].copy()
        G = v[1:-1, :].copy()
        F[1:-1, :] += dt * Ru
        G[:, 1:-1] += dt * Rv
        F[-1, :] = F[-2, :]               # estimación en la salida

        # (b) Poisson para la presión:  lap(p) = div(u*) / dt
        div = (F[1:, :] - F[:-1, :]) / dx + (G[:, 1:] - G[:, :-1]) / dy
        p = lu.solve((div / dt).ravel()).reshape(nx, ny)

        # (c) corrección: u^{n+1} = u* - dt grad(p)
        u_old = u[:, 1:-1].copy()
        u[1:-1, 1:-1] = F[1:-1, :] - dt * (p[1:, :] - p[:-1, :]) / dx
        u[-1, 1:-1] = F[-1, :] - dt * (-2.0 * p[-1, :]) / dx   # p = 0 en la salida
        v[1:-1, 1:-1] = G[:, 1:-1] - dt * (p[:, 1:] - p[:, :-1]) / dy
        # sólo fantasmas; u en la salida se conserva para garantizar masa
        u[0, 1:-1] = uin
        v[0, :] = -v[1, :]
        v[-1, :] = v[-2, :]
        u[:, 0] = -u[:, 1]
        u[:, -1] = -u[:, -2]

        res = np.max(np.abs(u[:, 1:-1] - u_old)) / dt
        if n % 10 == 0 or n == 1:
            hist_t.append(n * dt)
            hist_res.append(res)
        if snap_every and n % snap_every == 0:
            snaps.append((n * dt, u.copy(), v.copy()))
        if not np.isfinite(res) or res > max_div:
            status = "diverged"
            if verbose:
                print(f"  ¡Divergencia en t = {n*dt:.3f}! (residuo = {res:.2e})")
            break
        if res < tol and n * dt > 5.0:
            status = "converged"
            break

    t_cpu = time.time() - t0
    out = dict(g=g, Re=Re, nu=nu, dt=dt, gamma=gamma, u=u, v=v, p=p, t=n * dt,
               steps=n, status=status, cpu=t_cpu, uin=uin,
               hist_t=np.array(hist_t), hist_res=np.array(hist_res), snaps=snaps)
    if status != "diverged":
        out.update(reattachment(out))
    if verbose:
        msg = f"Re={Re:4d} ny={ny:3d} dt={dt:.4f} gamma={gamma:.2f} -> {status} " \
              f"t={n*dt:7.2f} ({n} pasos, {t_cpu:5.1f} s)"
        if status != "diverged":
            msg += f"  x_r/S = {out['xr']/S:5.2f}"
        print(msg)
    return out


# ---------------------------------------------------------------------------
# 5. Post-proceso
# ---------------------------------------------------------------------------
def _crossings(x, f, direction):
    """Posiciones donde f cruza cero; direction=+1 (de - a +) o -1 (de + a -)."""
    idx = np.where((np.sign(f[:-1]) == -direction) & (np.sign(f[1:]) == direction))[0]
    return np.array([x[i] - f[i] * (x[i + 1] - x[i]) / (f[i + 1] - f[i]) for i in idx])


def reattachment(res):
    """Longitudes de recirculación a partir del signo del esfuerzo cortante en paredes.

    x_r : reacoplamiento de la burbuja principal (pared inferior, tau_w de - a +),
          tomado aguas abajo del mínimo de u (así se ignora el pequeño vórtice de esquina).
    x_s, x_e : separación y reacoplamiento de la burbuja secundaria (pared superior).
    """
    g, u = res["g"], res["u"]
    xf = g["xf"]
    u_bot = u[:, 1]             # primera fila sobre la pared inferior (tau_w ~ u / (dy/2))
    u_top = u[:, -2]            # primera fila bajo la pared superior
    i_min = int(np.argmin(u_bot))
    up = _crossings(xf, u_bot, +1)
    up = up[up > xf[i_min]]
    xr = up[0] if up.size else np.nan
    sep = _crossings(xf, u_top, -1)
    xs = sep[0] if sep.size else np.nan
    att = _crossings(xf, u_top, +1)
    att = att[att > xs] if sep.size else att[:0]
    xe = att[0] if att.size else np.nan
    return dict(xr=xr, xs=xs, xe=xe)


def cell_fields(res):
    """Interpola u, v a centros de celda; calcula |V|, vorticidad y función de corriente."""
    g, u, v = res["g"], res["u"], res["v"]
    dx, dy = g["dx"], g["dy"]
    uc = 0.5 * (u[1:, 1:-1] + u[:-1, 1:-1])
    vc = 0.5 * (v[1:-1, 1:] + v[1:-1, :-1])
    speed = np.hypot(uc, vc)
    # vorticidad en nodos (esquinas de celda): w = dv/dx - du/dy
    w = (v[1:, :] - v[:-1, :]) / dx - (u[:, 1:] - u[:, :-1]) / dy
    # función de corriente en esquinas: psi(x, y) = int_0^y u dy
    psi = np.zeros((g["nx"] + 1, g["ny"] + 1))
    psi[:, 1:] = np.cumsum(u[:, 1:-1], axis=1) * dy
    return dict(uc=uc, vc=vc, speed=speed, w=w, psi=psi)


def divergence_norm(res):
    g, u, v = res["g"], res["u"], res["v"]
    div = (u[1:, 1:-1] - u[:-1, 1:-1]) / g["dx"] + (v[1:-1, 1:] - v[1:-1, :-1]) / g["dy"]
    return np.max(np.abs(div))
