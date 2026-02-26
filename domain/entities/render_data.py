from pydantic import BaseModel
from typing import Optional


class LabelRenderData(BaseModel):
    to: str
    address: str
    city: str
    packages: str = ""


class RemitoRenderData(BaseModel):
    client_code: str
    client_name: str
    order_number: int
    address: str
    city: str
    items: list[dict]
    total: float
    remito_id: str
    fecha: str
    reparto: Optional[str] = None
    sucursal: Optional[str] = None
    obs: Optional[str] = None
    cant_unidades: Optional[str] = None
    valor_declarado: Optional[str] = None
    numero_cot: Optional[str] = None
    numero_cai: Optional[str] = None
    vencimiento: Optional[str] = None
    disclaimer: Optional[str] = None
