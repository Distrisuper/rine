from pydantic import BaseModel
from typing import Optional


class UpdatePrinterRequestDTO(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    channel_ids: Optional[list[int]] = None
