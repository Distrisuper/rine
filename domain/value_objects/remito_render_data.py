from pydantic import BaseModel
from typing import Optional, List, Any, Dict

class RemitoRenderData(BaseModel):
    """Datos para renderizar un remito (PDF)."""
    client_code: str = ""
    client_name: str = ""
    order_number: int = 0
    address: str = ""
    city: str = ""
    items: List[Dict[str, Any]] = []
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
