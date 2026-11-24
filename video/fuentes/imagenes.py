import matplotlib; matplotlib.use("Agg")
import numpy as np, matplotlib.pyplot as plt
from PIL import Image
import json
from pathlib import Path
nb = json.load(open(Path(__file__).resolve().parents[2] / "escalon_descendente.ipynb", encoding="utf-8"))
src = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
exec(src[:src.index("from matplotlib.animation import")])       # sólo el solver y las gráficas
NOMBRES = ""   # p. ej. "Ana · Luis · ..." para que aparezcan en la portada

AZUL = "#1F3864"
# ---- portada y cierre sobre un cuadro de la simulación
def tarjeta(archivo, lineas, y0=0.80, banda=(0.04, 0.22)):
    fondo = np.asarray(Image.open("img/fondo.png").convert("RGB"))
    tira = fondo[110:287, 88:1871]                       # franja de tinta del video
    fig = plt.figure(figsize=(16, 9), dpi=120, facecolor=AZUL)
    ax = fig.add_axes([0.04, banda[0], 0.92, banda[1]]); ax.imshow(tira, aspect="auto"); ax.axis("off")
    y = y0
    for txt, tam, peso in lineas:
        fig.text(0.5, y, txt, ha="center", va="center", color="white", fontsize=tam, fontweight=peso)
        y -= 0.035 + tam / 700
    fig.savefig(archivo, facecolor=AZUL); plt.close(fig)

tarjeta("img/titulo.png", y0=0.78, banda=(0.17, 0.22), lineas=[("Flujo laminar sobre un", 46, "bold"), ("escalón descendente", 46, "bold"),
                           ("Simulación de Navier–Stokes 2D en Python", 26, "normal"),
                           ("Mecánica de Fluidos · Proyecto final · Prof. Anuar Sánchez", 20, "normal")]
        + ([(NOMBRES, 20, "normal")] if NOMBRES else []))
tarjeta("img/cierre.png", y0=0.86, banda=(0.13, 0.17), lineas=[("Conclusiones", 44, "bold"),
                           ("Navier–Stokes resuelto con el método de proyección; la masa se conserva", 22, "normal"),
                           ("Menos viscosidad → remolino más largo: x_r/S de 2.8 (Re 100) a 10.1 (Re 600)", 22, "normal"),
                           ("Malla: error < 1 %  ·  Δt estable no cambia el resultado", 22, "normal"),
                           ("Literatura: diferencia ≤ 2 % para Re 200–600", 22, "normal"),
                           ("¡Gracias!", 34, "bold")])

# ---- fenómeno: flujo estacionario anotado
r = simular(200, NY=40, L=15.0)
m = r["m"]; uc, vc = velocidad_en_centros(m, r["u"], r["v"])
fig = plt.figure(figsize=(16, 9), dpi=120, facecolor="white")
fig.text(0.04, 0.92, "¿Qué pasa en un escalón descendente?", fontsize=30, fontweight="bold", color=AZUL)
fig.text(0.04, 0.865, "Simulación a Re = 200: magnitud de velocidad y líneas de corriente", fontsize=17, color="0.3")
ax = fig.add_axes([0.04, 0.30, 0.92, 0.5])
ax.contourf(m["x_p"], m["y_p"], np.hypot(uc, vc).T, levels=40, cmap="viridis")
ax.contourf(m["x_p"], m["y_p"], uc.T, levels=[-10, 0], colors="red", alpha=0.25)
ax.streamplot(m["x_p"], m["y_p"], np.nan_to_num(uc.T), np.nan_to_num(vc.T), color="w", density=1.6, linewidth=0.7, arrowsize=0.8)
dibujar_escalon(ax); ax.set_xlim(-2, 6); ax.set_ylim(0, 1); ax.set_aspect("equal")
ax.set_xlabel("x / H", fontsize=14); ax.set_ylabel("y / H", fontsize=14); ax.tick_params(labelsize=12)
xr = r["xr"]
caja = dict(boxstyle="round,pad=0.35", fc="white", ec=AZUL, lw=1.5)
flecha = dict(arrowstyle="-|>", color=AZUL, lw=2.2, mutation_scale=22)
ax.annotate("Perfil parabólico\n(Poiseuille)", xy=(-1.5, 0.75), xytext=(-1.9, 1.32), fontsize=15, bbox=caja, arrowprops=flecha, annotation_clip=False)
ax.annotate("Separación en la esquina", xy=(0.02, 0.5), xytext=(0.3, 1.32), fontsize=15, bbox=caja, arrowprops=flecha, annotation_clip=False)
ax.annotate("Remolino (u < 0)", xy=(1.0, 0.22), xytext=(0.9, -0.62), fontsize=15, bbox=caja, arrowprops=flecha, annotation_clip=False)
ax.annotate(f"Reacoplamiento x_r = {xr:.2f} H\n(τ_pared = 0)", xy=(xr, 0.0), xytext=(2.8, -0.68), fontsize=15, bbox=caja, arrowprops=flecha, annotation_clip=False)
ax.annotate("Se frena → la presión sube\n(gradiente adverso)", xy=(3.2, 0.6), xytext=(3.6, 1.32), fontsize=15, bbox=caja, arrowprops=flecha, annotation_clip=False)
ax.plot([xr], [0.0], "v", color="r", ms=16, clip_on=False, zorder=10)
fig.savefig("img/fenomeno.png"); plt.close(fig)
print("listo", xr / S)
