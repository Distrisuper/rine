from pydantic import BaseModel
from typing import List, Optional, Any

class RemitoRenderData(BaseModel):
    """Datos completos para renderizar un remito (PDF)."""
    client_name: str = ""
    client_code: str = ""
    order_number: int = 0
    address: str = ""
    city: str = ""
    items: List[dict] = []
    total: float = 0.0
    remito_id: str = ""
    fecha: str = ""
    reparto: str = ""
    sucursal: str = ""
    obs: str = ""
    comentarios: str = ""
    cant_unidades: str = ""
    valor_declarado: str = ""
    numero_cot: str = ""
    numero_cai: str = ""
    vencimiento: str = ""
    disclaimer: str = ""

    @classmethod
    def from_queue_item(cls, item: Any, extra: Optional[Any] = None) -> "RemitoRenderData":
        """
        Construye RemitoRenderData desde un QueueItem.
        Los campos del remito (items, fecha, reparto, etc.) se leen de `extra`
        (ExtraDataRemito), con fallback a los atributos del item.
        """
        e = extra  # alias corto

        return cls(
            client_code=item.client_code or "",
            client_name=item.client_name or "",
            order_number=getattr(item, "order_number", 0) or 0,
            address=(e and e.address) or getattr(item, "address", "") or "",
            city=(e and e.city) or getattr(item, "city", "") or "",
            items=(e.items if e and e.items is not None else []),
            total=(e.total if e and e.total is not None else None) or getattr(item, "invoice_total", 0.0) or 0.0,
            remito_id=(e and e.remito_id) or getattr(item, "remito_id", "") or "",
            fecha=(e and e.fecha) or "",
            reparto=(e and e.reparto) or "",
            sucursal=(e and e.sucursal) or "",
            obs=(e and e.obs) or "",
            comentarios=(e and e.comentarios) or "",
            cant_unidades=(e and e.cant_unidades) or "",
            valor_declarado=(e and e.valor_declarado) or "",
            numero_cot=(e and e.numero_cot) or "",
            numero_cai=(e and e.numero_cai) or "",
            vencimiento=(e and e.vencimiento) or "",
            disclaimer=(e and e.disclaimer) or "",
        )
