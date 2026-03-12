from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TemplateResponseDTO(BaseModel):
    id: int
    name: str
    file_path: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
