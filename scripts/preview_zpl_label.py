"""
Simula en PC (sin impresora) cómo queda un rótulo ZPL, usando el conversor
público de Labelary (https://labelary.com) para convertir el ZPL renderizado
en una imagen PNG.

Uso:
    python scripts/preview_zpl_label.py zebra_label_landscape_90_v2.zpl --out preview.png

    # Con datos custom desde un archivo JSON (recomendado en PowerShell,
    # ya que pasar JSON inline con comillas anidadas rompe el parseo de argumentos):
    python scripts/preview_zpl_label.py zebra_label_landscape_90_v2.zpl --data-file data.json --out preview.png

    # Con datos custom inline (funciona bien en bash/cmd; en PowerShell puede fallar):
    python scripts/preview_zpl_label.py zebra_label_landscape_90_v2.zpl \
        --data '{"to": "Juan Perez", "address": "Calle Falsa 123", "city": "Mar del Plata", "packages": "2", "transport": "MOSTRADOR"}'
"""
import argparse
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.services.zpl_label_render_service import ZplLabelRenderer
from domain.value_objects import LabelRenderData

TEMPLATES_DIR = os.path.join("infrastructure", "templates", "labels")

DEFAULT_DATA = {
    "to": "Juan Perez",
    "address": "Calle Falsa 123",
    "city": "Mar del Plata",
    "packages": "2",
    "transport": "MOSTRADOR",
    "observations": "",
}

# Etiqueta física: 100mm x 150mm a 203dpi (8 dots/mm) -> 3.94in x 5.91in
LABELARY_URL = "http://api.labelary.com/v1/printers/8dpmm/labels/3.94x5.91/0/"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", help="Nombre del archivo .zpl (relativo a infrastructure/templates/labels)")
    parser.add_argument("--data", help="JSON con los datos a renderizar (sino usa datos de ejemplo)")
    parser.add_argument("--data-file", help="Archivo .json con los datos a renderizar (alternativa robusta a --data en PowerShell)")
    parser.add_argument("--out", default="label_preview.png", help="Archivo PNG de salida")
    args = parser.parse_args()

    data_dict = DEFAULT_DATA.copy()
    if args.data_file:
        with open(args.data_file, "r", encoding="utf-8") as f:
            data_dict.update(json.load(f))
    elif args.data:
        data_dict.update(json.loads(args.data))

    renderer = ZplLabelRenderer(TEMPLATES_DIR)
    zpl_bytes = renderer.render(args.template, LabelRenderData(**data_dict))

    req = urllib.request.Request(
        LABELARY_URL,
        data=zpl_bytes,
        headers={"Accept": "image/png", "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        png_bytes = resp.read()

    with open(args.out, "wb") as f:
        f.write(png_bytes)

    print(f"OK: preview guardada en {args.out}")
    if os.name == "nt":
        os.startfile(args.out)


if __name__ == "__main__":
    main()
