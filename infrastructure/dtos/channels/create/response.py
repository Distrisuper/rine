from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateChannelResponseDTO(BaseModel):
    id: int
    channel_number: int
    description: Optional[str]
    template_id: Optional[int]
    document_source: str
    is_active: bool
    created_at: datetime
