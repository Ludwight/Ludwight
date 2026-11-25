def crear_malla(NY, L):
    """Celdas cuadradas de lado dx sobre [-LI, L] x [0, H]. El escalón es el bloque sólido x < 0, y < S."""
    dx = H / NY                              # lado de cada celda
    NX = round((LI + L) / dx)                # número de celdas a lo largo
    x_p = (np.arange(NX) + 0.5) * dx - LI    # x de los centros de celda (donde vive p)
    y_p = (np.arange(NY) + 0.5) * dx         # y de los centros de celda
    x_u = np.arange(NX + 1) * dx - LI        # x de las caras verticales (donde vive u)
    solido = (x_p[:, None] < 0) & (y_p[None, :] < S)     # True en las celdas del escalón
    return dict(NX=NX, NY=NY, dx=dx, L=L, x_p=x_p, y_p=y_p, x_u=x_u, solido=solido,
                I0=round(LI / dx),           # índice de la cara x = 0 (la cara del escalón)
                J0=round(S / dx))
