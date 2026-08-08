"""
Render de remito desde template HTML (Jinja2) + CSS → PDF con WeasyPrint.
El formato se edita en infrastructure/templates/remitos/base_remito.html y remito.css.
"""
import base64
import logging
import os
from io import BytesIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

logging.getLogger("weasyprint").setLevel(logging.WARNING)
logging.getLogger("fontconfig").setLevel(logging.WARNING)

from domain.services.remito_renderer_interface import RemitoRenderer
from domain.value_objects import RemitoRenderData
from domain.services.barcode_service_interface import BarcodeServiceInterface

logger = logging.getLogger(__name__)


def _calcular_total_articulos(items: list[dict]) -> str:
    """Suma el campo 'cantidad' de los items del remito (acepta str o número)."""
    total = 0.0
    for row in items:
        try:
            total += float(row.get("cantidad", 0) or 0)
        except (TypeError, ValueError):
            continue
    return str(int(total)) if total.is_integer() else str(total)


def _logo_data_url(templates_dir: Path) -> str | None:
    """
    Si existe logo.png o logo.svg en la carpeta de templates, lo lee y devuelve
    un data URL (base64) para el <img>.
    """
    # Buscamos el logo en la subcarpeta remitos de la raíz de templates
    remitos_dir = templates_dir / "remitos"
    for name in ("logo.png", "logo.svg"):
        path = remitos_dir / name
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
        "total_articulos": _calcular_total_articulos(data.items),
        "remito_id": remito_id,
        "barcode_data_url": barcode_service.to_svg_data_url(remito_id),
        "fecha": data.fecha,
        "reparto": data.reparto,
        "sucursal": data.sucursal,
        "obs": data.obs,
        "comentarios": data.obs, # Mapeamos obs a comentarios para el template del PR
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
    Busca templates en infrastructure/templates/ usando rutas relativas (ej: 'remitos/base_remito.html').
    """

    def __init__(
        self,
        barcode_service: BarcodeServiceInterface,
        templates_dir: Path | None = None,
    ):
        self._barcode_service = barcode_service
        if templates_dir is None:
            # Al estar en infrastructure/services/, subimos dos niveles para llegar a infrastructure/
            templates_dir = Path(__file__).resolve().parent.parent / "templates"
        self._templates_dir = Path(templates_dir)
        self._env = Environment(
            loader=FileSystemLoader(str(self._templates_dir)),
            autoescape=select_autoescape(("html",)),
        )

    def _get_safe_template_path(self, template_path: str) -> str:
        """Verifica si el path existe, si no devuelve el default."""
        if (self._templates_dir / template_path).exists():
            return template_path
        return "remitos/base_remito.html"

    def render(self, template_id: str, data: RemitoRenderData) -> bytes:
        # template_id aquí actúa como el path relativo guardado en DB
        template_path = self._get_safe_template_path(template_id)
        template = self._env.get_template(template_path)
        
        context = _data_to_context(data, self._barcode_service)
        context["logo_data_url"] = _logo_data_url(self._templates_dir)
        html_string = template.render(**context)

        if os.getenv("DEBUG_REMITO_HTML", "").strip().lower() in ("1", "true", "yes"):
            print("--- START DEBUG HTML ---")
            print(html_string)
            print("--- END DEBUG HTML ---")

        # La base_url para assets (CSS, etc) debe ser relativa a la carpeta del template
        current_template_dir = (self._templates_dir / template_path).parent
        base_url = current_template_dir.as_uri() + "/"

        css_path = current_template_dir / "remito.css"
        logger.debug("remito_css_path=%s exists=%s", css_path, css_path.exists())

        # if css_path.exists():
        #     stylesheets.append(CSS(filename=str(css_path)))
        
        # # PR #35: Devolver los bytes directamente (sin buffer intermedio)
        # return HTML(string=html_string, base_url=base_url).write_pdf()

        pdf_doc = HTML(string=html_string, base_url=base_url)
        buffer = BytesIO()
        pdf_doc.write_pdf(buffer)
        return buffer.getvalue()
