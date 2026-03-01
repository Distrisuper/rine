from pydantic import BaseModel
from typing import Optional, Any

class LabelRenderData(BaseModel):
    """Datos para renderizar una etiqueta/rótulo (ZPL)."""
    to: str = ""
    address: str = ""
    city: str = ""
    packages: str = ""
    transport: str = ""
    observations: str = ""

    @classmethod
    def from_queue_item(cls, item: Any, extra: Optional[Any] = None) -> "LabelRenderData":
        """Factory method para construir los datos de renderizado desde un QueueItem."""
        return cls(
            to=item.client_name or "",
            address=getattr(item, "address", "") or "",
            city=getattr(item, "city", "") or "",
            packages=str(getattr(item, "quantity", "")) if hasattr(item, "quantity") else "",
        )
