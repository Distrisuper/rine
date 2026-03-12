"""
Generación de código de barras para remitos.
Code 39 (alfanumérico) a partir de redi_id / remito_id.
"""
import base64
from io import BytesIO

from domain.services.barcode_service_interface import BarcodeServiceInterface


_CODE39_CHARS = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ -.$/+%")


def _sanitize_code39(value: str) -> str:
    """Deja solo caracteres válidos para Code 39; si queda vacío devuelve '0'."""
    if not value or not value.strip():
        return "0"
    s = value.strip().upper()
    out = "".join(c for c in s if c in _CODE39_CHARS)
    return out if out else "0"


class BarcodeService(BarcodeServiceInterface):
    def to_svg_data_url(self, value: str, add_checksum: bool = False) -> str | None:
        """
        Genera un código de barras Code 39 a partir de value (ej. remito_id / redi_id)
        y lo devuelve como data URL SVG (para usar en <img src="...">).

        Si value está vacío o la generación falla, devuelve None.
        """
        try:
            from barcode import get_barcode_class
            from barcode.writer import SVGWriter
        except ImportError:
            return None

        raw = _sanitize_code39(value)
        if not raw:
            return None

        try:
            Code39 = get_barcode_class("code39")
            writer = SVGWriter()
            code = Code39(raw, writer=writer, add_checksum=add_checksum)
            buffer = BytesIO()
            code.write(buffer, options={
                "module_width": 0.5,
                "module_height": 18.0,
                "quiet_zone": 8.0,
            })
            buffer.seek(0)
            svg_bytes = buffer.getvalue()
            b64 = base64.b64encode(svg_bytes).decode("ascii")
            return f"data:image/svg+xml;base64,{b64}"
        except Exception:
            return None
