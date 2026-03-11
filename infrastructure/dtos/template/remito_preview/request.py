from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class RemitoPreviewRequestDTO(BaseModel):
    channel: int
    client_code: str
    client_name: str
    payload: Dict[str, Any]
    number_of_copies: Optional[int] = Field(default=1, ge=1, le=100)
