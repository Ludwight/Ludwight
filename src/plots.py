"""Gráficas del escalón descendente (todas reciben el diccionario devuelto por solve_bfs)."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from bfs_solver import cell_fields

S_COLOR = "0.35"


def _step(ax, res):
    """Dibuja el escalón (la entrada está en x = 0, el escalón ocupa 0 < y < S)."""
    S = res["g"]["S"]
    ax.add_patch(patches.Rectangle((-0.6, 0), 0.6, S, fc=S_COLOR, ec="k", hatch="///"))
    ax.set_xlim(-0.6, None)


def plot_fields(res, xmax=None, fname=None):
    """|V| con líneas de corriente, vorticidad y presión."""
    g = res["g"]
    f = cell_fields(res)
    xmax = xmax or g["L"]
    S = g["S"]
    X, Y = np.meshgrid(g["xc"], g["yc"], indexing="ij")
    Xf, Yf = np.meshgrid(g["xf"], g["yf"], indexing="ij")

    fig, axs = plt.subplots(3, 1, figsize=(12, 6.2), sharex=True, constrained_layout=True)
    cs = axs[0].contourf(X, Y, f["speed"], levels=40, cmap="viridis")
    axs[0].contour(Xf, Yf, f["psi"], levels=np.r_[np.linspace(-0.03, -0.001, 6), np.linspace(0.02, 0.98, 12)],
                   colors="w", linewidths=0.6)
    fig.colorbar(cs, ax=axs[0], label="|V| / U")
    axs[0].set_title(f"Re = {res['Re']}: magnitud de velocidad y líneas de corriente   "
                     f"(x_r/S = {res['xr']/S:.2f})")

    wmax = np.percentile(np.abs(f["w"]), 98)
    cs = axs[1].contourf(Xf, Yf, f["w"], levels=np.linspace(-wmax, wmax, 41), cmap="RdBu_r", extend="both")
    fig.colorbar(cs, ax=axs[1], label="ω H / U")
    axs[1].set_title("Vorticidad")

    cs = axs[2].contourf(X, Y, res["p"], levels=40, cmap="coolwarm")
    fig.colorbar(cs, ax=axs[2], label="p / ρU²")
    axs[2].set_title("Presión")

    for ax in axs:
        _step(ax, res)
        ax.axvline(res["xr"], color="r", ls="--", lw=1)
        ax.set_xlim(-0.6, xmax)
        ax.set_aspect("equal")
        ax.set_ylabel("y / H")
    axs[-1].set_xlabel("x / H")
    if fname:
        fig.savefig(fname, dpi=150)
    return fig


def plot_profiles(res, stations=(0.0, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0), fname=None):
    """Perfiles u(y) en varias estaciones x (escalados y desplazados)."""
    g = res["g"]
    u = res["u"][:, 1:-1]
    fig, ax = plt.subplots(figsize=(12, 2.8), constrained_layout=True)
    for xs in stations:
        i = int(round(xs / g["dx"]))
        ax.plot(xs + 0.8 * u[i], g["yc"], "b-")
        ax.axvline(xs, color="0.6", lw=0.6)
    _step(ax, res)
    ax.axvline(res["xr"], color="r", ls="--", lw=1, label="reacoplamiento")
    ax.set_xlim(-0.6, max(stations) + 1.5)
    ax.set_xlabel("x / H  (perfil: x + 0.8 u/U)")
    ax.set_ylabel("y / H")
    ax.set_title(f"Perfiles de velocidad u(y), Re = {res['Re']}")
    ax.legend(loc="upper right")
    if fname:
        fig.savefig(fname, dpi=150)
    return fig


def plot_wall_shear(results, fname=None):
    """u en la primera celda junto a la pared inferior (proporcional a τ_w)."""
    fig, ax = plt.subplots(figsize=(9, 3.2), constrained_layout=True)
    for r in results:
        g = r["g"]
        tau = r["nu"] * r["u"][:, 1] / (0.5 * g["dy"])
        ax.plot(g["xf"] / g["S"], tau, label=f"Re = {r['Re']}")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlim(0, 25)
    ax.set_xlabel("x / S")
    ax.set_ylabel("τ_w / ρU²  (pared inferior)")
    ax.set_title("Esfuerzo cortante en la pared inferior: τ_w = 0 marca el reacoplamiento")
    ax.legend()
    if fname:
        fig.savefig(fname, dpi=150)
    return fig


def plot_convergence(results, labels, fname=None):
    fig, ax = plt.subplots(figsize=(7, 3.5), constrained_layout=True)
    for r, lab in zip(results, labels):
        ax.semilogy(r["hist_t"], r["hist_res"], label=lab)
    ax.set_xlabel("t U / H")
    ax.set_ylabel("max |Δu| / Δt")
    ax.set_title("Historia de convergencia hacia el estado estacionario")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    if fname:
        fig.savefig(fname, dpi=150)
    return fig
