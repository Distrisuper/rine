from typing import Optional
from pydantic import BaseModel

class QueueItem(BaseModel):
    """Ítem en la cola de impresión."""
    id: int
    client_id: str
    client_code: str
    client_name: str
    order_number: int
    type: str
    type_code: Optional[int | str] = None
    location: str
    channel: int
    invoice_type: Optional[str] = None
    invoice_number: Optional[int | str] = None
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
