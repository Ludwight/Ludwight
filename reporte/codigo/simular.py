def simular(Re, NY=20, L=15.0, dt=None, t_max=400.0, tol=1e-4, fotos_cada=0, ab2=True):
    """Resuelve Navier-Stokes desde el reposo hasta que el flujo deja de cambiar."""
    nu = 1.0 / Re                            # viscosidad adimensional
    m = crear_malla(NY, L)
    NX, dx = m["NX"], m["dx"]
    if dt is None:
        dt = CFL * dx / 1.5                  # límite CFL: dt = dx / u_max, con u_max = 1.5 U

    resolver_p = matriz_presion(m)           # matriz de presión, factorizada una sola vez
    u_entrada = perfil_entrada(m["y_p"])
    u = np.zeros((NX + 1, NY + 2))           # condición inicial: fluido en reposo
    v = np.zeros((NX + 2, NY + 1))
    fronteras(u, v, u_entrada, m)

    t, n, estado = 0.0, 0, "tiempo máximo"
    hist_t, hist_cambio, fotos = [], [], []
    Au_ant = Av_ant = None                   # aceleraciones del paso anterior (para Adams-Bashforth)
    while t < t_max:
        u_viejo = u.copy()

        # PASO 1: velocidad de prueba con convección y difusión, SIN presión.
        # Adams-Bashforth: la aceleración a la mitad del paso se estima como 1.5*(la de ahora) - 0.5*(la anterior)
        Au, Av = aceleracion_u(u, v, nu, dx), aceleracion_v(u, v, nu, dx)
        if Au_ant is None or not ab2:
            Au_ant, Av_ant = Au, Av          # primer paso (o ab2=False): Euler simple
        u_est, v_est = u.copy(), v.copy()
        u_est[1:-1, 1:-1] += dt * (1.5 * Au - 0.5 * Au_ant)
        v_est[1:-1, 1:-1] += dt * (1.5 * Av - 0.5 * Av_ant)
        Au_ant, Av_ant = Au, Av
        u_est[-1, 1:-1] = u_est[-2, 1:-1]    # salida: du/dx = 0
        fronteras(u_est, v_est, u_entrada, m)

        # PASO 2: presión que hace falta para que no se cree ni se pierda masa:  lap(p) = div(u_est)/dt
        div = (u_est[1:, 1:-1] - u_est[:-1, 1:-1] + v_est[1:-1, 1:] - v_est[1:-1, :-1]) / dx
        div[m["solido"]] = 0.0
        p = resolver_p.solve((div / dt).ravel()).reshape(NX, NY)

        # PASO 3: corregir la velocidad con el gradiente de presión:  u = u_est - dt * grad(p)
        u, v = u_est, v_est
        u[1:-1, 1:-1] -= dt * (p[1:, :] - p[:-1, :]) / dx
        u[-1, 1:-1] -= dt * (0.0 - p[-1, :]) / (dx / 2)       # salida: p = 0 en la cara
        v[1:-1, 1:-1] -= dt * (p[:, 1:] - p[:, :-1]) / dx
        fronteras(u, v, u_entrada, m)

        t += dt; n += 1
        cambio = np.max(np.abs(u - u_viejo)) / dt              # qué tan rápido cambia todavía el flujo
        if n % 10 == 0:
            hist_t.append(t); hist_cambio.append(cambio)
        if fotos_cada and n % fotos_cada == 0:
            fotos.append((t, u.astype(np.float32), v.astype(np.float32)))
        if not np.isfinite(cambio) or cambio > 1e3:            # la solución explotó
            estado = "diverge"; break
        if cambio < tol and t > 5:                             # ya no cambia: estado estacionario
            estado = "converge"; break

    r = dict(m=m, Re=Re, nu=nu, dt=dt, u=u, v=v, p=p, t=t, pasos=n, estado=estado,
             hist_t=hist_t, hist_cambio=hist_cambio, fotos=fotos)
    txt = f"Re = {Re:4d} | NY = {NY:3d} | dt = {dt:.4f} | {estado:9s} en t = {t:6.1f} ({n} pasos)"
    if estado != "diverge":
        r["xr"] = reacoplamiento(m, u)
        r["burbuja_sup"] = burbuja_superior(m, u)
        txt += f" | x_r/S = {r['xr']/S:.2f}"
    print(txt)
    return r
