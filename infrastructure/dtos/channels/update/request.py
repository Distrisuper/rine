from pydantic import BaseModel, field_validator
from typing import Optional


class UpdateChannelRequestDTO(BaseModel):
    description: Optional[str] = None
    is_active: Optional[bool] = None
    template_id: Optional[int] = None
    document_source: Optional[str] = None

    @field_validator('document_source')
    @classmethod
    def validate_document_source(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = ["INTERNAL", "S3_REMITOS_FRIC_ROT"]
        if v not in allowed:
            raise ValueError(f"document_source debe ser uno de: {allowed}")
        return v.upper()
