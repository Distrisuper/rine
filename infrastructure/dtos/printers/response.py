from pydantic import BaseModel
from typing import List, Optional

class PrinterChannelDTO(BaseModel):
    channel_id: int
    channel_number: int
    description: Optional[str] = None
    is_active: bool

class PrinterResponseDTO(BaseModel):
    id: int
    name: str
    is_active: bool
    channels: List[PrinterChannelDTO]
    channel_count: int

    class Config:
        from_attributes = True
