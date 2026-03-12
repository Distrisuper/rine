from typing import Optional, Dict, Any
from pydantic import BaseModel

class TemplateTestItem(BaseModel):
    """
    Body mínimo para probar templates (remito/etiqueta).
    Estructura simplificada alineada con el nuevo diseño de payload.
    """
    channel: int
    client_code: str = ""
    client_name: str = "Cliente prueba"
    payload: Dict[str, Any] = {}
