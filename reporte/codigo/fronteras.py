def fronteras(u, v, u_entrada, m):
    """Condiciones de frontera. u tiene forma (NX+1, NY+2) y v (NX+2, NY+1):
    incluyen una 'celda fantasma' fuera del dominio para poner las paredes."""
    I0, J0 = m["I0"], m["J0"]
    u[0, 1:-1] = u_entrada           # entrada: perfil parabólico
    v[0, :] = -v[1, :]               # entrada: v = 0 (fantasma espejo: el promedio en la frontera da cero)
    u[:I0 + 1, 1:J0 + 1] = 0.0       # escalón: u = 0 dentro del bloque y en su cara vertical
    v[1:I0 + 1, :J0 + 1] = 0.0       # escalón: v = 0 dentro del bloque y en su tapa
    u[:I0, J0] = -u[:I0, J0 + 1]     # tapa del escalón: no deslizamiento (fantasma espejo)
    v[I0, 1:J0] = -v[I0 + 1, 1:J0]   # cara vertical del escalón: no deslizamiento
    u[:, 0] = -u[:, 1]               # piso: u = 0
    u[:, -1] = -u[:, -2]             # techo: u = 0
    v[:, 0] = 0.0                    # piso: v = 0 (v está justo sobre la pared)
    v[:, -1] = 0.0                   # techo: v = 0
    v[-1, :] = v[-2, :]
