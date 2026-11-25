def matriz_presion(m):
    """Arma y factoriza la matriz de la ecuación de Poisson  lap(p) = b.

    Para cada celda con fluido: sum_vecinos (p_vecino - p_celda) / dx^2 = b_celda.
    - Paredes, entrada y escalón: dp/dn = 0  -> ese vecino simplemente no se suma.
    - Salida: p = 0 en la cara, que está a dx/2 del centro -> aporta -2 p_celda / dx^2.
    """
    NX, NY, solido = m["NX"], m["NY"], m["solido"]
    A = sps.lil_matrix((NX * NY, NX * NY))   # una ecuación por celda; matriz fácil de llenar
    for i in range(NX):                      # columnas de celdas (dirección x)
        for j in range(NY):                  # filas de celdas (dirección y)
            k = i * NY + j                   # número de la celda (i, j) en la lista
            if solido[i, j]:                 # dentro del escalón no hay fluido: ecuación trivial p = 0
                A[k, k] = 1; continue
            for vi, vj in [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]:    # los 4 vecinos
                if vi == NX:                                                   # derecha de la última: la salida
                    A[k, k] -= 2
                elif vi >= 0 and 0 <= vj < NY and not solido[vi, vj]:         # vecino con fluido
                    A[k, vi * NY + vj] = 1; A[k, k] -= 1
    return spla.splu(A.tocsc() / m["dx"]**2)
