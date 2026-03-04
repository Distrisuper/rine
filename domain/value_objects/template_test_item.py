from typing import Optional, Dict, Any
from pydantic import BaseModel
from domain.value_objects.queue_item import QueueItem

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
            number_of_copies=1,
            attempt_count=0,
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
