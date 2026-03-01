from pydantic import BaseModel
from typing import Dict, Any


class CreatePrintJobRequestDTO(BaseModel):
    channel: int
    client_code: str
    client_name: str
    payload: Dict[str, Any]
