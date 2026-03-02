import json
from pydantic import BaseModel, model_validator
from typing import Optional


class LabelPreviewRequestDTO(BaseModel):
    channel: int = 0
    location: str = ""
    extra_data: Optional[str] = None
    client_code: str = ""
    client_name: str = "Cliente prueba"
    order_number: int = 1
    invoice_total: Optional[float] = None
    redi_id: int = 0
    server: Optional[str] = None
    ds: Optional[str] = None
    
    # Parámetros para Query String
    to: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    packages: Optional[str] = None

    @model_validator(mode='after')
    def pack_extra_data(self) -> 'LabelPreviewRequestDTO':
        # Si extra_data está vacío pero tenemos los campos individuales, los empaquetamos como JSON
        if not self.extra_data and any([self.to, self.address, self.city, self.packages]):
            data = {
                "to": self.to or "",
                "address": self.address or "",
                "city": self.city or "",
                "packages": self.packages or ""
            }
            self.extra_data = json.dumps(data)
        return self
