from pydantic import BaseModel
from typing import Optional


class DiscoverPrinterResponseDTO(BaseModel):
    name: str
    model: str
    type: str

