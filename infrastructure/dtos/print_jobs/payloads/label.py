from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional

class LabelPayloadDTO(BaseModel):
    to: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    packages: str | int
    transport: str
    observations: str = ""

    @model_validator(mode="before")
    @classmethod
    def _alias_observations(cls, data: Any) -> Any:
        if isinstance(data, dict) and not data.get("observations"):
            data["observations"] = data.get("comentarios") or data.get("obs") or ""
        return data
