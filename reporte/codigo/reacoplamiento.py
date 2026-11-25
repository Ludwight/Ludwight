def reacoplamiento(m, u):
    """Donde el flujo se vuelve a pegar al piso: la u junto al piso pasa de negativa a positiva."""
    x = m["x_u"][m["I0"]:]                    # sólo después del escalón (x >= 0)
    u_piso = u[m["I0"]:, 1]                   # u en la fila de celdas pegada al piso
    i_min = np.argmin(u_piso)                 # centro del remolino (flujo de regreso más fuerte)
    for i in range(i_min, len(x) - 1):        # buscamos aguas abajo del centro del remolino
        if u_piso[i] < 0 <= u_piso[i + 1]:
            return x[i] - u_piso[i] * (x[i + 1] - x[i]) / (u_piso[i + 1] - u_piso[i])  # interpolación
    return np.nan
