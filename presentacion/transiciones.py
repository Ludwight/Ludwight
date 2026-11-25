"""Agrega transiciones de diapositiva (fundido lento) a un .pptx y elimina las entradas de carpeta del ZIP.
Uso: python transiciones.py presentacion.pptx   (modifica el archivo en su lugar)."""
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

TRANSICION = '<p:transition spd="slow"><p:fade/></p:transition>'


def marcar(xml: str) -> str:
    if "<p:transition" in xml:
        return xml
    return re.sub(r"(</p:clrMapOvr>)", r"\1" + TRANSICION, xml, count=1)


def main(origen: str) -> None:
    src = Path(origen)
    tmp = Path(tempfile.mkdtemp()) / src.name
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename.endswith("/"):
                continue
            datos = zin.read(item.filename)
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", item.filename):
                datos = marcar(datos.decode("utf-8")).encode("utf-8")
            zout.writestr(item, datos)
    shutil.move(tmp, src)
    print("transiciones aplicadas a", src)


if __name__ == "__main__":
    main(sys.argv[1])
