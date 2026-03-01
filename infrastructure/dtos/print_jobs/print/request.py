from pydantic import BaseModel
from typing import Literal


class PrintJobRequestDTO(BaseModel):
    printer_name: str
    content: bytes
    content_type: Literal["pdf", "zpl"]
    job_title: str
