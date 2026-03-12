from pydantic import BaseModel
from typing import Optional, Any


class GetOneStatusByNameResponseDTO(BaseModel):
    ready: bool
    estado: str
    estado_codigo: int
    razon: Optional[str]
    detalles: list[Any]
    cups_state: int
    modelo: str
    ocupada: bool
