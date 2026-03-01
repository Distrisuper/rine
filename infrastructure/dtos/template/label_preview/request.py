from pydantic import BaseModel
from typing import Optional


class LabelPreviewRequestDTO(BaseModel):
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
