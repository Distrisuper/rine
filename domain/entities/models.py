from __future__ import annotations

import json
from typing import Literal, Optional

from pydantic import BaseModel, ValidationError


class QueueItem(BaseModel):
    """Ítem en la cola de impresión."""

    id: int
    client_id: str
    client_code: str
    client_name: str
    order_number: int
    type: str
    type_code: int | str | None = None
    location: str
    channel: int
    invoice_type: Optional[str] = None
    invoice_number: int | str | None = None
    invoice_comment: str
    invoice_total: Optional[float] = None
    result: int
    result_detail: str
    retry: int
    priority: int
    printed: int
    print_count: int
    host: int
    redi_code: str
    redi_id: int
    date_created: str
    date_started: Optional[str] = None
    date_processed: Optional[str] = None
    extra_data: Optional[str] = None
    server: Optional[str] = None
    ds: Optional[str] = None


class ExtraDataRemito(BaseModel):
    """
    Datos extra del ítem de cola (remito/etiqueta).
    Equivalente a dataRemito del legacy C#; se parsea desde QueueItem.extra_data.
    """

    remito: Optional[str] = None
    ftp_filename: Optional[str] = None
    label_to: Optional[str] = None
    label_address: Optional[str] = None
    label_city: Optional[str] = None
    label_packages: Optional[str] = None
    label_transport: Optional[str] = None
    idRemito: Optional[str] = None
    redi_id: Optional[str] = None

    @classmethod
    def from_json(cls, raw: str | None) -> ExtraDataRemito | None:
        """Parsea el JSON de extra_data; devuelve None si está vacío o es inválido."""
        if not raw or not raw.strip():
            return None
        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                return None
            return cls.model_validate(data)
        except (json.JSONDecodeError, ValidationError):
            return None


class ResolvedTemplate(BaseModel):
    """Resultado del resolver: template a usar y tipo de salida."""

    template_id: str
    output_type: Literal["pdf", "zpl"]


class RemitoRenderData(BaseModel):
    """Datos completos para renderizar un remito (PDF). Diseño tipo Distrisuper."""

    client_name: str = ""
    client_code: str = ""
    order_number: str = ""
    address: str = ""
    city: str = ""
    items: list[dict] = []
    total: float = 0.0
    remito_id: str = ""
    fecha: str = ""
    reparto: str = ""
    sucursal: str = ""
    obs: str = ""
    cant_unidades: str = ""
    valor_declarado: str = ""
    numero_cot: str = ""
    numero_cai: str = ""
    vencimiento: str = ""
    disclaimer: str = ""


class LabelRenderData(BaseModel):
    """Datos para renderizar una etiqueta/rótulo (ZPL)."""

    to: str = ""
    address: str = ""
    city: str = ""
    packages: str = ""
    transport: str = ""
    observations: str = ""


class TemplateTestItem(BaseModel):
    """
    Body mínimo para probar templates (remito/etiqueta).
    Los campos no enviados se rellenan con valores por defecto.
    """

    channel: int
    location: str = ""
    extra_data: Optional[str] = None
    client_code: str = ""
    client_name: str = "Cliente prueba"
    order_number: int = 1
    invoice_total: Optional[float] = None
    redi_id: int = 0
    server: Optional[str] = None
    ds: Optional[str] = None

    def to_queue_item(self) -> QueueItem:
        """Construye un QueueItem para el servicio de templates."""
        return QueueItem(
            id=0,
            client_id="test",
            client_code=self.client_code,
            client_name=self.client_name,
            order_number=self.order_number,
            type="remito" if self.channel in (4, 8) else "etiqueta",
            type_code=None,
            location=self.location,
            channel=self.channel,
            invoice_type=None,
            invoice_number=None,
            invoice_comment="",
            invoice_total=self.invoice_total,
            result=0,
            result_detail="",
            retry=0,
            priority=0,
            printed=0,
            print_count=1,
            host=0,
            redi_code="",
            redi_id=self.redi_id,
            date_created="",
            date_started=None,
            date_processed=None,
            extra_data=self.extra_data,
            server=self.server,
            ds=self.ds,
        )
