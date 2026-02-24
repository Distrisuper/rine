"""Controlador para endpoints de prueba de templates (remito/etiqueta)."""
from fastapi import Response

from app.models import TemplateTestItem
from app.services.label_template_service import LabelTemplateService
from app.services.remito_template_service import RemitoTemplateService


class TemplateController:
    """Prueba de generación de remito (PDF) y etiqueta (ZPL) con datos mock."""

    @staticmethod
    def render_remito_test(service: RemitoTemplateService, body: TemplateTestItem) -> Response:
        """Genera PDF de remito para el body de prueba."""
        item = body.to_queue_item()
        pdf_bytes = service.render(item)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="remito.pdf"'},
        )

    @staticmethod
    def render_label_test(service: LabelTemplateService, body: TemplateTestItem) -> Response:
        """Genera ZPL de etiqueta para el body de prueba."""
        item = body.to_queue_item()
        zpl_bytes = service.render(item)
        return Response(content=zpl_bytes, media_type="application/vnd.zpl")
