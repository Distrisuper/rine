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
