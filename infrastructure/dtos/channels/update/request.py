from pydantic import BaseModel
from typing import Optional


class UpdateChannelRequestDTO(BaseModel):
    description: Optional[str] = None
    is_active: Optional[bool] = None
    template_id: Optional[int] = None
