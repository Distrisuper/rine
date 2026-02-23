"""
Render de etiqueta: template_id + LabelRenderData → ZPL.
Placeholder: genera ZPL mínimo para pruebas hasta integrar template real.
"""
from app.interfaces.label_renderer import LabelRenderer
from app.models import LabelRenderData


class PlaceholderLabelRenderer(LabelRenderer):
    """Genera ZPL mínimo para pruebas; reemplazar por template real."""

    def render(self, template_id: str, data: LabelRenderData) -> bytes:
        # ZPL mínimo: etiqueta con texto (destinatario, dirección, etc.)
        lines = [
            "^XA",
            "^FO50,50^A0N,30,30^FD%s^FS" % (data.to or "N/A")[:40],
            "^FO50,90^A0N,25,25^FD%s^FS" % (data.address or "")[:40],
            "^FO50,130^A0N,25,25^FD%s^FS" % (data.city or "")[:40],
            "^FO50,170^A0N,25,25^FD%s^FS" % (data.packages or "")[:20],
            "^XZ",
        ]
        return "\n".join(lines).encode("utf-8")
