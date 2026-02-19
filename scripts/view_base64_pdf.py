"""Decodifica content_base64 del JSON de prueba y guarda/abre el PDF."""
import base64
import json
import sys
import subprocess
import platform
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Uso: python view_base64_pdf.py <ruta_json_o_base64>")
        print("  Si pasas un .json, lee content_base64 del JSON.")
        print("  Si pasas el string base64 directo, lo decodifica.")
        sys.exit(1)

    raw = sys.argv[1].strip()
    if raw.startswith("{"):
        data = json.loads(raw)
        b64 = data.get("content_base64", raw)
    else:
        b64 = raw

    pdf_bytes = base64.b64decode(b64)
    out_path = Path("remito_preview.pdf")
    out_path.write_bytes(pdf_bytes)
    print(f"Guardado: {out_path.absolute()}")

    if platform.system() == "Windows":
        subprocess.run(["start", "", str(out_path.absolute())], shell=True)
    elif platform.system() == "Darwin":
        subprocess.run(["open", str(out_path)])
    else:
        subprocess.run(["xdg-open", str(out_path)])

if __name__ == "__main__":
    main()
