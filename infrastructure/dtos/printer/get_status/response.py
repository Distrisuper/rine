from pydantic import BaseModel, ConfigDict, Field
from typing import Any


class GetStatusResponseDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cups_unavailable: bool = Field(alias="_cups_unavailable")
    message: str | None = None
    printers: dict[str, Any]
