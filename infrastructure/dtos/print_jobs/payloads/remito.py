from pydantic import BaseModel, Field
from typing import List, Optional

class RemitoItemDTO(BaseModel):
    descripcion: str
    cantidad: int

class RemitoPayloadDTO(BaseModel):
    client_code: Optional[str] = None
    client_name: Optional[str] = None
    order_number: str | int = ""
    address: str = ""
    city: str = ""
    items: List[RemitoItemDTO] = Field(default_factory=list)
    total: float = 0.0
    remito_id: str = ""
    fecha: str = ""
    reparto: Optional[str] = None
    sucursal: Optional[str] = None
    obs: Optional[str] = None
    cant_unidades: Optional[str] = None
    valor_declarado: Optional[str] = None
    numero_cot: Optional[str] = None
    numero_cai: Optional[str] = None
    vencimiento: Optional[str] = None
    disclaimer: Optional[str] = None
