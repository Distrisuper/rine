from pydantic import BaseModel, Field
from typing import Dict, Any


class CreatePrintJobRequestDTO(BaseModel):
    channel: int
    client_code: str
    client_name: str
    payload: Dict[str, Any]
    number_of_copies: int | None = Field(default=1, ge=1, le=100)
