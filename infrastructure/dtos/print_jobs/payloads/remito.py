from pydantic import BaseModel, Field
from typing import List, Optional

class RemitoItemDTO(BaseModel):
    descripcion: str
    cantidad: str = Field(..., description="Cantidad como string. Ej: '2'")

class RemitoPayloadDTO(BaseModel):
    client_code: Optional[str] = None
    client_name: Optional[str] = None
    order_number: str = Field(default="", description="Numero de pedido como string")
    address: str = ""
    city: str = ""
    items: List[RemitoItemDTO] = Field(default_factory=list)
    total: str = Field(default="0.0", description="Total como string decimal. Ej: '185000.50'")
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
