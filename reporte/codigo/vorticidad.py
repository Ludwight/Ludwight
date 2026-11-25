def vorticidad(m, u, v):
    """omega = dv/dx - du/dy en las esquinas de las celdas (ahí la malla escalonada la da directo)."""
    w = (v[1:, :] - v[:-1, :]) / m["dx"] - (u[:, 1:] - u[:, :-1]) / m["dx"]
    y_v = np.arange(m["NY"] + 1) * m["dx"]
    w[(m["x_u"][:, None] < 0) & (y_v[None, :] < S)] = np.nan   # dentro del escalón no hay fluido
    return w
