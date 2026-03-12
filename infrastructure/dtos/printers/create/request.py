from pydantic import BaseModel
from typing import Optional


class CreatePrinterRequestDTO(BaseModel):
    name: str
    channel_ids: list[int] = []
