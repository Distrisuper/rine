"""
Render de remito desde template HTML (Jinja2) + CSS → PDF con WeasyPrint.
El formato se edita en app/templates/remitos/base_remito.html y remito.css.
"""
import base64
from io import BytesIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from domain.repositories.remito_renderer import RemitoRenderer
from domain.entities.models import RemitoRenderData
from domain.services.barcode_service_interface import BarcodeServiceInterface


def _logo_data_url(templates_dir: Path) -> str | None:
    """
    Si existe logo.png o logo.svg en la carpeta de templates, lo lee y devuelve
    un data URL (base64) para el <img>. Así WeasyPrint lo carga siempre (también en Docker).
    """
    for name in ("logo.png", "logo.svg"):
        path = templates_dir / name
        if not path.exists():
            continue
        try:
            raw = path.read_bytes()
            mime = "image/png" if name.endswith(".png") else "image/svg+xml"
            b64 = base64.b64encode(raw).decode("ascii")
            return f"data:{mime};base64,{b64}"
        except Exception:
            continue
    return None


def _data_to_context(data: RemitoRenderData, barcode_service: BarcodeServiceInterface) -> dict:
    """Convierte RemitoRenderData a dict para Jinja2."""
    remito_id = data.remito_id or ""
    return {
        "client_name": data.client_name,
        "client_code": data.client_code,
        "order_number": data.order_number,
        "address": data.address,
        "city": data.city,
        "items": data.items,
        "total": data.total,
        "remito_id": remito_id,
        "barcode_data_url": barcode_service.to_svg_data_url(remito_id),
        "fecha": data.fecha,
        "reparto": data.reparto,
        "sucursal": data.sucursal,
        "obs": data.obs,
        "cant_unidades": data.cant_unidades,
        "valor_declarado": data.valor_declarado,
        "numero_cot": data.numero_cot,
        "numero_cai": data.numero_cai,
        "vencimiento": data.vencimiento,
        "disclaimer": data.disclaimer,
    }


class HtmlRemitoRenderer(RemitoRenderer):
    """
    Genera PDF desde HTML + CSS.
    Busca templates en app/templates/remitos/; por defecto usa base_remito.html.
    Requiere weasyprint instalado; si no está, instanciar falla (usar PlaceholderRemitoRenderer).
    """

    def __init__(
        self,
        barcode_service: BarcodeServiceInterface,
        templates_dir: Path | None = None,
    ):
        self._barcode_service = barcode_service
        if templates_dir is None:
            templates_dir = Path(__file__).resolve().parent.parent / "templates" / "remitos"
        self._templates_dir = Path(templates_dir)
        self._env = Environment(
            loader=FileSystemLoader(str(self._templates_dir)),
            autoescape=select_autoescape(("html",)),
        )

    def _template_name(self, template_id: str) -> str:
        """Mapea template_id a nombre de archivo; por defecto base_remito.html."""
        candidate = f"{template_id}.html"
        if (self._templates_dir / candidate).exists():
            return candidate
        return "base_remito.html"

    def render(self, template_id: str, data: RemitoRenderData) -> bytes:
        template = self._env.get_template(self._template_name(template_id))
        context = _data_to_context(data, self._barcode_service)
        context["logo_data_url"] = _logo_data_url(self._templates_dir)
        html_string = template.render(**context)

        base_url = self._templates_dir.as_uri() + "/"
        pdf_doc = HTML(string=html_string, base_url=base_url)
        buffer = BytesIO()
        pdf_doc.write_pdf(buffer)
        return buffer.getvalue()
