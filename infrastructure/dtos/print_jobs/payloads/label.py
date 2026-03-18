from pydantic import BaseModel, Field
from typing import Optional

class LabelPayloadDTO(BaseModel):
    to: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    packages: str | int
    transport: str
    observations: str = ""
