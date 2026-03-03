from pydantic import BaseModel
from typing import Optional


class CreateChannelRequestDTO(BaseModel):
    channel_number: int
    description: Optional[str] = None
    template_id: Optional[int] = None
