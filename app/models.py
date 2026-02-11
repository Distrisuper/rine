from pydantic import BaseModel
from typing import Optional

class QueueItem(BaseModel):
    """Ítem en la cola de impresión."""

    id: int
    client_id: str
    client_code: str
    client_name: str
    order_number: int
    type: str
    type_code: Optional[str] = None
    location: str
    channel: int
    invoice_type: Optional[str] = None
    invoice_number: Optional[str] = None
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
    extra_data: str


class PrintQueueResponse(BaseModel):
    """Respuesta del endpoint de cola de impresión."""

    ok: int
    data: list[QueueItem]
