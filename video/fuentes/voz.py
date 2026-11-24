import subprocess, wave
MAPA = {"R": "rr", "R2": "rr", "j": "i", "B": "b", "D": "d", "G": "g", "z": "s", "Z": "jj"}
OK = set("a e i o u w b d g p t k f T s x tS jj m n J l L r rr _".split())

def decir(texto, salida, velocidad=158, voz="es1"):
    pho = subprocess.run(["espeak-ng", "-v", "mb-" + voz, "-s", str(velocidad), "-q", "--pho", texto],
                         capture_output=True, text=True).stdout
    filas = []
    for linea in pho.splitlines():
        partes = linea.split()
        if not partes:
            continue
        ph = partes[0].rstrip("/")
        ph = MAPA.get(ph, ph)
        if ph not in OK:
            raise ValueError(f"fonema desconocido {ph!r} en: {texto}")
        dur = int(partes[1])
        if filas and filas[-1][0] == ph:                  # fusionar fonemas repetidos (no hay difono x-x)
            filas[-1][1] += dur
        else:
            filas.append([ph, dur, " ".join(partes[2:])])
    open(salida + ".pho", "w").write("\n".join(f"{p} {d} {r}".strip() for p, d, r in filas) + "\n")
    r = subprocess.run(["mbrola", "-e", f"/usr/share/mbrola/{voz}/{voz}", salida + ".pho", salida], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr + r.stdout)
    w = wave.open(salida)
    return w.getnframes() / w.getframerate()
