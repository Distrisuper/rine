import json
from pathlib import Path
from typing import Any
from sqlmodel import Session, select

from domain.services.document_builder.document_builder_interface import DocumentBuilder
from domain.services.barcode_service_interface import BarcodeServiceInterface
from domain.value_objects import LabelRenderData, RemitoRenderData
from domain.entities.channel import Channel


class TemplateDocumentBuilder(DocumentBuilder):
    """Builds document from Jinja template (ZPL or HTML)."""

    def __init__(self, barcode_service: "BarcodeServiceInterface | None" = None):
        self._barcode_service = barcode_service

    def build(self, job: Any, session: Session) -> bytes:
        template = self._get_template(job, session)
        if not template:
            raise ValueError(f"No hay template configurado para channel {job.channel}")

        file_path = template.file_path

        if file_path.endswith('.zpl'):
            return self._render_label(job.get_render_data_label(), file_path)
        elif file_path.endswith('.html'):
            return self._render_remito(job.get_render_data_remito(), file_path)

        raise ValueError(f"Template no soportado: {file_path}")

    def _get_template(self, job: Any, session: Session):
        channel = self._get_channel(job, session)
        if not channel or not channel.template_id:
            return None
        from domain.entities.template import Template
        return session.get(Template, channel.template_id)

    def _get_channel(self, job: Any, session: Session) -> Channel | None:
        return session.exec(
            select(Channel).where(Channel.channel_number == job.channel)
        ).first()

    def _render_label(self, data: LabelRenderData, file_path: str) -> bytes:
        from jinja2 import Template

        template_path = Path(f"/app/infrastructure/templates/{file_path}")
        if not template_path.exists():
            raise FileNotFoundError(f"Template ZPL no encontrado: {file_path}")

        with open(template_path) as f:
            template = Template(f.read())

        zpl = template.render(
            to=data.to,
            address=data.address,
            city=data.city,
            packages=data.packages,
        )
        return zpl.encode("latin-1", errors="replace")

    def _render_remito(self, data: RemitoRenderData, file_path: str) -> bytes:
        from jinja2 import Template
        from weasyprint import HTML

        if self._barcode_service is None:
            from infrastructure.services.barcode_service import BarcodeService
            self._barcode_service = BarcodeService()

        barcode_service = self._barcode_service

        template_path = Path(f"/app/infrastructure/templates/{file_path}")
        if not template_path.exists():
            return self._placeholder_pdf()

        with open(template_path) as f:
            template = Template(f.read())

        html = template.render(
            client_code=data.client_code,
            client_name=data.client_name,
            order_number=data.order_number,
            address=data.address,
            city=data.city,
            items=data.items,
            total=data.total,
            remito_id=data.remito_id,
            fecha=data.fecha,
            barcode_data_url=barcode_service.to_svg_data_url(data.remito_id) or "",
            reparto=data.reparto or "",
            sucursal=data.sucursal or "",
            obs=data.obs or "",
            cant_unidades=data.cant_unidades or "",
            valor_declarado=data.valor_declarado or "",
            numero_cot=data.numero_cot or "",
            numero_cai=data.numero_cai or "",
            vencimiento=data.vencimiento or "",
            disclaimer=data.disclaimer or "",
        )

        return HTML(string=html).write_pdf()

    def _placeholder_pdf(self) -> bytes:
        return b"%PDF-1.4 placeholder"
