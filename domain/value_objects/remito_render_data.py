from pydantic import BaseModel
from typing import List, Optional, Any

class RemitoRenderData(BaseModel):
    """Datos completos para renderizar un remito (PDF)."""
    client_name: str = ""
    client_code: str = ""
    order_number: str = ""
    address: str = ""
    city: str = ""
    items: List[dict] = []
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

    @classmethod
    def from_queue_item(cls, item: Any, extra: Optional[Any] = None) -> "RemitoRenderData":
        """Factory method para construir los datos de renderizado desde un QueueItem."""
        return cls(
            client_code=item.client_code or "",
            client_name=item.client_name or "",
            order_number=str(getattr(item, "order_number", 0)),
            address=getattr(item, "address", "") or "",
            city=getattr(item, "city", "") or "",
            items=[],
            total=getattr(item, "invoice_total", 0.0) or 0.0,
            remito_id=getattr(item, "remito_id", "") or "",
            fecha="",
        )
