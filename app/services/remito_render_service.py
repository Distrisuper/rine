"""
Render de remito: template_id + RemitoRenderData → PDF.
Placeholder: genera un PDF con texto visible para pruebas; reemplazar por WeasyPrint/Jinja2.
"""
from app.interfaces.remito_renderer import RemitoRenderer
from app.models import RemitoRenderData


def _escape_pdf_string(s: str) -> str:
    """Escapa paréntesis y backslash para literal string en PDF."""
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


class PlaceholderRemitoRenderer(RemitoRenderer):
    """Genera un PDF con texto visible (remito de prueba) para que se vea algo al abrirlo."""

    def render(self, template_id: str, data: RemitoRenderData) -> bytes:
        # Texto visible en la página (escapado para PDF)
        titulo = _escape_pdf_string("Remito de prueba")
        cliente = _escape_pdf_string((data.client_name or "—")[:60])
        remito_id = _escape_pdf_string((data.remito_id or "—")[:40])
        ciudad = _escape_pdf_string((data.city or "—")[:40])
        # Contenido de la página: BT = begin text, /F1 24 Tf = font tamaño 24, Tj = show text, ET = end text
        stream_lines = [
            "BT",
            "/F1 24 Tf",
            "72 700 Td",
            f"({titulo}) Tj",
            "0 -30 Td",
            "/F1 14 Tf",
            f"(Cliente: {cliente}) Tj",
            "0 -20 Td",
            f"(Remito: {remito_id}) Tj",
            "0 -20 Td",
            f"(Ciudad: {ciudad}) Tj",
            "ET",
        ]
        stream_body = "\n".join(stream_lines)
        stream = f"stream\n{stream_body}\nendstream"

        obj1 = "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj"
        obj2 = "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj"
        obj3 = (
            "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            "/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
            "/Contents 4 0 R >> endobj"
        )
        obj4 = f"4 0 obj << /Length {len(stream_body) + 18} >> {stream} endobj"

        body = "\n".join(["%PDF-1.4", obj1, obj2, obj3, obj4])
        body_utf8 = body.encode("utf-8")
        o1, o2, o3, o4 = (
            body.find("1 0 obj"),
            body.find("2 0 obj"),
            body.find("3 0 obj"),
            body.find("4 0 obj"),
        )
        xref_block = (
            "xref\n0 5\n"
            "0000000000 65535 f \n"
            f"{o1:010d} 00000 n \n"
            f"{o2:010d} 00000 n \n"
            f"{o3:010d} 00000 n \n"
            f"{o4:010d} 00000 n \n"
        )
        full = body + "\n" + xref_block + "trailer << /Size 5 /Root 1 0 R >>\n"
        full_utf8 = full.encode("utf-8")
        startxref = full.find("xref")  # offset en bytes (ASCII)
        full_utf8 += f"startxref\n{startxref}\n%%EOF\n".encode("utf-8")
        return full_utf8
