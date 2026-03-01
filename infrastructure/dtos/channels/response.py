from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChannelResponseDTO(BaseModel):
    id: int
    channel_number: int
    description: Optional[str] = None
    template_id: Optional[int] = None
    template_name: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
