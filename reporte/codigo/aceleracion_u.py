def aceleracion_u(u, v, nu, dx):
    """Ecuación de x sin la presión:  nu*lap(u) - d(uu)/dx - d(vu)/dy."""
    P = u[1:-1, 1:-1]                                     # u en el nodo
    E, W = u[2:, 1:-1], u[:-2, 1:-1]                      # vecinos este y oeste
    N, Sur = u[1:-1, 2:], u[1:-1, :-2]                    # vecinos norte y sur
    difusion = nu * (E + W + N + Sur - 4 * P) / dx**2     # laplaciano de 5 puntos

    u_e, u_w = (P + E) / 2, (W + P) / 2                   # u en las caras este y oeste (promedio)
    u_n, u_s = (P + N) / 2, (Sur + P) / 2                 # u en las caras norte y sur
    v_n = (v[1:-2, 1:] + v[2:-1, 1:]) / 2                 # v que cruza la cara norte
    v_s = (v[1:-2, :-1] + v[2:-1, :-1]) / 2               # v que cruza la cara sur
    conveccion = (u_e * u_e - u_w * u_w) / dx + (v_n * u_n - v_s * u_s) / dx   # lo que sale - lo que entra
    return difusion - conveccion
