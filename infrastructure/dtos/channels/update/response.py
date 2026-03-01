from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UpdateChannelResponseDTO(BaseModel):
    id: int
    channel_number: int
    description: Optional[str]
    template_id: Optional[int]
    is_active: bool
    created_at: Optional[datetime]
