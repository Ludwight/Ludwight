"""Arma el video del proyecto (1920x1080, 30 fps) a partir del guion, la voz sintetizada y los clips."""
import json, subprocess, wave
from pathlib import Path
import numpy as np
from guion import SEGMENTOS
from voz import decir

AQUI = Path(__file__).parent
FIG = AQUI.parents[1] / "figures"
OUT = AQUI / "salida"; OUT.mkdir(exist_ok=True)
FF = ["ffmpeg", "-y", "-loglevel", "error"]
SR = 16000                      # frecuencia de la voz de mbrola
HUECO, ANTES, DESPUES = 0.35, 0.35, 0.45
eventos = dict(json.load(open(AQUI / "eventos.json"))["eventos"])
grabacion = json.load(open(AQUI / "eventos.json"))["video"]
MIN_DUR = {"codigo_e": 3.0, "codigo_f": 7.0, "titulo": 6.0}
ETIQUETA = "Demostración en vivo: el notebook corriendo en Jupyter"


def leer(wav):
    w = wave.open(str(wav))
    return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)


# ---------- 1) voz y tiempos ----------
plan, t = [], 0.0
for sid, visual, frases in SEGMENTOS:
    audios = []
    for k, f in enumerate(frases):
        wav = AQUI / "voz" / f"{sid}_{k}.wav"
        decir(f, str(wav))
        audios.append((f, leer(wav)))
    habla = sum(len(a) / SR for _, a in audios) + HUECO * max(len(audios) - 1, 0)
    dur = max(ANTES + habla + DESPUES, MIN_DUR.get(sid, 0))
    plan.append(dict(sid=sid, visual=visual, audios=audios, t0=t, dur=round(dur * 30) / 30))
    t += plan[-1]["dur"]
TOTAL = t
print(f"duración total: {TOTAL:.1f} s")

# ---------- 2) clip de video de cada segmento ----------
grupo = lambda sid: sid.split("_")[0]
for i, s in enumerate(plan):
    d, vis = s["dur"], s["visual"]
    fades = []
    if i == 0 or grupo(plan[i - 1]["sid"]) != grupo(s["sid"]):
        fades.append("fade=in:st=0:d=0.3")
    if i == len(plan) - 1 or grupo(plan[i + 1]["sid"]) != grupo(s["sid"]):
        fades.append(f"fade=out:st={d - 0.3:.3f}:d=0.3")
    tipo, _, resto = vis.partition(":")
    if tipo == "img":
        nombre = resto if not resto.startswith("slide") else f"slide-{resto[5:]}"
        entrada = ["-loop", "1", "-framerate", "30", "-t", f"{d:.3f}", "-i", str(AQUI / "img" / f"{nombre}.png")]
        filtro = ["scale=1920:1080"]
    else:
        if tipo == "rec":
            def tiempo(x):
                nombre, _, extra = x.partition("+")
                return eventos[nombre] + float(extra or 0)
            a, b = (tiempo(x) for x in resto.split(":"))
            fuente, ini = str(AQUI / "grabacion_30fps.mp4"), a
        else:
            fuente, ini = str(FIG / resto), 0.0
            b = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                      fuente], capture_output=True, text=True).stdout)
            a = 0.0
        vel = min(max((b - a) / d, 1.0), 4.0)
        entrada = ["-ss", f"{ini:.3f}", "-t", f"{b - a:.3f}", "-i", fuente]
        filtro = [f"setpts=PTS/{vel:.4f}", "fps=30", "scale=1920:1080", f"tpad=stop_mode=clone:stop_duration={d:.3f}",
                  f"trim=duration={d:.3f}"]
        if tipo == "rec":
            txt = (ETIQUETA + (f"   (×{vel:.0f})" if vel >= 1.5 else "")).replace(":", "\\:")
            filtro.append(f"drawtext=text='{txt}':fontfile=/usr/share/fonts/opentype/inter/Inter-SemiBold.otf:"
                          "fontsize=30:fontcolor=white:box=1:boxcolor=0x1F3864E6:boxborderw=14:x=w-tw-40:y=70")
        s["vel"] = vel
    vf = ",".join(filtro + fades + ["format=yuv420p"])
    subprocess.run(FF + entrada + ["-vf", vf, "-an", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                                   "-r", "30", "-t", f"{d:.3f}", str(OUT / f"{i:02d}_{s['sid']}.mp4")], check=True)
    print(f"{i:02d} {s['sid']:11s} {d:5.1f} s" + (f"  vel ×{s['vel']:.2f}" if "vel" in s else ""))

lista = OUT / "lista.txt"
lista.write_text("".join(f"file '{OUT / f'{i:02d}_{s['sid']}.mp4'}'\n" for i, s in enumerate(plan)))
subprocess.run(FF + ["-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(OUT / "solo_video.mp4")], check=True)

# ---------- 3) pista de voz y subtítulos ----------
pista = np.zeros(int((TOTAL + 1) * SR), dtype=np.float32)
srt, n = [], 1
fmt = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round(x % 1 * 1000)) % 1000:03d}"
for s in plan:
    t = s["t0"] + ANTES
    for frase, a in s["audios"]:
        i0 = int(t * SR); pista[i0:i0 + len(a)] += a
        srt.append(f"{n}\n{fmt(t)} --> {fmt(t + len(a) / SR + 0.15)}\n{frase}\n"); n += 1
        t += len(a) / SR + HUECO
pista = np.clip(pista / np.abs(pista).max() * 0.9 * 32767, -32767, 32767).astype(np.int16)
w = wave.open(str(OUT / "voz.wav"), "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(pista.tobytes()); w.close()
(OUT / "subtitulos.srt").write_text("\n".join(srt), encoding="utf-8")

# ---------- 4) versiones finales ----------
estilo = ("FontName=Inter,FontSize=10,PrimaryColour=&H00FFFFFF,BackColour=&H99000000,BorderStyle=3,"
          "Outline=1,Shadow=0,MarginV=14,MarginL=60,MarginR=60")
subprocess.run(FF + ["-i", str(OUT / "solo_video.mp4"), "-i", str(OUT / "voz.wav"),
                     "-vf", f"subtitles={OUT / 'subtitulos.srt'}:force_style='{estilo}'",
                     "-af", "loudnorm=I=-16:TP=-1.5,aresample=48000", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                     "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
                     str(OUT / "video_proyecto.mp4")], check=True)
subprocess.run(FF + ["-i", str(OUT / "solo_video.mp4"), "-c", "copy", "-movflags", "+faststart",
                     str(OUT / "video_proyecto_sin_voz.mp4")], check=True)
json.dump([{k: s[k] for k in ("sid", "t0", "dur")} | {"frases": [f for f, _ in s["audios"]]} for s in plan],
          open(OUT / "plan.json", "w"), ensure_ascii=False, indent=1)
print("listo:", OUT / "video_proyecto.mp4")
