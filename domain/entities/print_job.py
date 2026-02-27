from sqlmodel import SQLModel, Field, Index, Session, select
from datetime import datetime
from typing import Optional
import json

from domain.entities.document_type import get_document_type
from domain.entities.printer_registry import PrinterRegistry, PrinterConfig
from domain.entities.render_data import LabelRenderData, RemitoRenderData
from domain.entities.channel import Channel
from domain.entities.template import Template
from infrastructure.db.database import engine


class PrintJob(SQLModel, table=True):
    __tablename__ = "print_jobs"
    __table_args__ = (
        Index("idx_print_jobs_status_created", "status", "date_created"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    client_code: str
    client_name: str
    channel: int
    payload: str  # JSON
    status: str = "pending"
    print_count: int = 0
    print_type: Optional[str] = None
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_started: Optional[datetime] = None
    date_processed: Optional[datetime] = None
    printer_name: Optional[str] = None
    error_message: Optional[str] = None
    processing_since: Optional[datetime] = None

    def get_document_type(self) -> dict:
        return get_document_type(self.channel)

    def get_printer(self) -> PrinterConfig:
        return PrinterRegistry.get_printer_for_channel(self.channel)

    def get_template(self) -> Template | None:
        with Session(engine) as session:
            channel = session.exec(
                select(Channel).where(Channel.channel_number == self.channel)
            ).first()
            if not channel or not channel.template_id:
                return None
            return session.get(Template, channel.template_id)

    def get_render_data(self) -> LabelRenderData | RemitoRenderData:
        data = json.loads(self.payload)
        doc_type = self.get_document_type()

        if self.channel == 3:
            return LabelRenderData(
                to=data.get("to", ""),
                address=data.get("address", ""),
                city=data.get("city", ""),
                packages=data.get("packages", ""),
            )
        elif self.channel in (4, 8):
            return RemitoRenderData(
                client_code=data.get("client_code", ""),
                client_name=data.get("client_name", ""),
                order_number=data.get("order_number", 0),
                address=data.get("address", ""),
                city=data.get("city", ""),
                items=data.get("items", []),
                total=data.get("total", 0.0),
                remito_id=data.get("remito_id", ""),
                fecha=data.get("fecha", ""),
                reparto=data.get("reparto"),
                sucursal=data.get("sucursal"),
                obs=data.get("obs"),
                cant_unidades=data.get("cant_unidades"),
                valor_declarado=data.get("valor_declarado"),
                numero_cot=data.get("numero_cot"),
                numero_cai=data.get("numero_cai"),
                vencimiento=data.get("vencimiento"),
                disclaimer=data.get("disclaimer"),
            )

        raise ValueError(f"Tipo de documento no soportado: {self.channel}")

    def render(self) -> bytes:
        template = self.get_template()
        if not template:
            raise ValueError(f"No hay template configurado para channel {self.channel}")

        if self.channel == 3:
            return self._render_label(self.get_render_data(), template.file_path)
        else:
            return self._render_remito(self.get_render_data(), template.file_path)

    def _render_label(self, data: LabelRenderData, file_path: str) -> bytes:
        from jinja2 import Template
        from pathlib import Path

        template_path = Path(f"/app/templates/{file_path}")
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
        return zpl.encode("utf-8")

    def _render_remito(self, data: RemitoRenderData, file_path: str) -> bytes:
        from pathlib import Path
        from jinja2 import Template
        from weasyprint import HTML
        from infrastructure.services.barcode_service import BarcodeService

        barcode_service = BarcodeService()

        template_path = Path(f"/app/templates/{file_path}")
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
