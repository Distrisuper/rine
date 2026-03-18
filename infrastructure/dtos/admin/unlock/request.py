from pydantic import BaseModel, Field


class AdminUnlockRequestDTO(BaseModel):
    security_code: str = Field(min_length=1, max_length=128)
