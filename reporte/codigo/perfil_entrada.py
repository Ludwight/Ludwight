def perfil_entrada(y):
    """Perfil parabólico (flujo de Poiseuille) en el canal de entrada S < y < H."""
    eta = (y - S) / (H - S)                  # 0 en la tapa del escalón, 1 en el techo
    return np.where(y > S, 6 * U * eta * (1 - eta), 0.0)
