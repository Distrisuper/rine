from sqlmodel import SQLModel, Field, Index, Session, select
from datetime import datetime
from typing import Optional
import json

from domain.value_objects import LabelRenderData, RemitoRenderData
from domain.entities.channel import Channel
from domain.entities.template import Template
from domain.services.document_builder.document_builder_factory import DocumentBuilderFactory
from domain.value_objects.rendered_document import RenderedDocument


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
    number_of_copies: int = 1
    attempt_count: int = 0
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_started: Optional[datetime] = None
    date_processed: Optional[datetime] = None
    printer_name: Optional[str] = None
    error_message: Optional[str] = None
    processing_since: Optional[datetime] = None
    cups_job_id: Optional[int] = Field(default=None)

    def get_template(self, session: Session) -> Template | None:
        channel = self.get_channel(session)
        if not channel or not channel.template_id:
            return None
        return session.get(Template, channel.template_id)

    def get_channel(self, session: Session) -> Channel | None:
        return session.exec(
            select(Channel).where(Channel.channel_number == self.channel)
        ).first()

    def render(self, session: Session) -> RenderedDocument:
        channel = self.get_channel(session)
        if not channel:
            raise ValueError(f"Channel {self.channel} no existe")

        builder = DocumentBuilderFactory.get_for(channel, session)
        return builder.build(self, session)

    def get_render_data_label(self) -> LabelRenderData:
        data = json.loads(self.payload) if isinstance(self.payload, str) else (self.payload or {})
        return LabelRenderData(
            to=data.get("to", ""),
            address=data.get("address", ""),
            city=data.get("city", ""),
            packages=str(data.get("packages", "")),
            transport=data.get("transport", ""),
            observations=data.get("observations", "")
        )

    def get_render_data_remito(self) -> RemitoRenderData:
        data = json.loads(self.payload) if isinstance(self.payload, str) else (self.payload or {})
        return RemitoRenderData(
            client_code=self.client_code or data.get("client_code", ""),
            client_name=self.client_name or data.get("client_name", ""),
            order_number=data.get("order_number", 0),
            address=data.get("address", ""),
            city=data.get("city", ""),
            items=data.get("items", []),
            total=float(data.get("total", 0.0)),
            remito_id=data.get("remito_id", ""),
            fecha=data.get("fecha", ""),
            reparto=data.get("reparto"),
            sucursal=data.get("sucursal"),
            obs=data.get("comentarios") or data.get("obs"), # PR #35
            cant_unidades=data.get("cant_unidades"),
            valor_declarado=data.get("valor_declarado"),
            numero_cot=data.get("numero_cot"),
            numero_cai=data.get("numero_cai"),
            vencimiento=data.get("vencimiento"),
            disclaimer=data.get("disclaimer"),
        )
