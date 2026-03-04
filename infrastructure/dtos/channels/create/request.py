from pydantic import BaseModel, field_validator
from typing import Optional


class CreateChannelRequestDTO(BaseModel):
    channel_number: int
    document_source: str
    description: Optional[str] = None
    template_id: Optional[int] = None

    @field_validator('document_source')
    @classmethod
    def validate_document_source(cls, v: str) -> str:
        allowed = ["INTERNAL", "S3_REMITOS_FRIC_ROT"]
        if v not in allowed:
            raise ValueError(f"document_source debe ser uno de: {allowed}")
        return v.upper()
