from pydantic import BaseModel
from typing import Any


class GetStatusResponseDTO(BaseModel):
    _cups_unavailable: bool
    message: str | None = None
    printers: dict[str, Any]
